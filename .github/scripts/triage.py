#!/usr/bin/env python3
"""The triage of this repository's issues, run by .github/workflows/triage.yml.

    triage.py event <event.json>   label the issue of an `issues` event from its form's answers, or ask for the form
    triage.py close                close each open issue labelled incomplete with no activity for the days configured

What it reads of each form is .github/triage.json; the labels are .github/labels.json. An issue's title and body are
anyone's text: the event's file gives the issue's number, the API the issue as it stands; nothing of the text reaches
the command line, and nothing of it is written back.
Standard library only, and `gh` with the job's token (GH_TOKEN, GH_REPO), both on GitHub's runners.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

GITHUB = Path(__file__).resolve().parent.parent
# An issue opened by the repository's own people is never triaged. Their permission on the repository says who they
# are (`maintain` reads `write` there); the association, which may read NONE for a private member of the organisation,
# decides only when the permission cannot be read.
WRITERS = frozenset({"admin", "maintain", "write"})
MAINTAINERS = frozenset({"OWNER", "MEMBER", "COLLABORATOR"})
# A GitHub login, or an app's: what may go into the permission call's path.
LOGIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}(?:\[bot\])?")
# The events whose run adds the answers' labels whatever the issue's state; an edit adds them only when it completes it.
OPENING = frozenset({"opened", "reopened"})
# What GitHub writes for an optional field left empty.
NO_RESPONSE = "_No response_"
HEADING = re.compile(r"^### (.+?)\s*$")
CODE = re.compile(r"\bLW\d{3}\b")


def load(name: str, root: Path = GITHUB) -> dict | list:
    return json.loads((root / name).read_text(encoding="utf-8"))


def answers(body: str | None, fields: list[dict]) -> dict[str, str]:
    """The text under each `### <label>` heading of a form's `fields`, stripped. A section starts only at the heading
    of a later field, in the form's order: a heading, a fence or a task list in an answer stays that answer's text."""
    labels = [entry["label"] for entry in fields]
    sections: dict[str, list[str]] = {}
    at = -1  # the field whose answer is being read
    for line in (body or "").splitlines():
        heading = HEADING.match(line)
        if heading and heading.group(1) in labels[at + 1 :]:
            at = labels.index(heading.group(1), at + 1)
            sections[labels[at]] = []
        elif at >= 0:
            sections[labels[at]].append(line)
    return {label: "\n".join(lines).strip() for label, lines in sections.items()}


def answered(value: str, boxes: bool) -> bool:
    """A field is answered when it holds text and, for a field of boxes, every box is ticked."""
    return bool(value) and value != NO_RESPONSE and not (boxes and "- [ ]" in value)


def ticked(value: str) -> bool:
    return any(line.strip().lower().startswith("- [x]") for line in value.splitlines())


def form_of(labels: set[str], body: str | None, config: dict) -> dict | None:
    """The form an issue came through: the one whose label it carries, or else the one form whose required fields all
    have their heading in its body, in the form's order. An issue opened through the API, or before the labels existed,
    carries no form's label; one whose body matches both forms, or neither, has no form."""
    labelled = next((form for form in config["forms"] if form["label"] in labels), None)
    if labelled:
        return labelled
    matches = [form for form in config["forms"] if set(form["required"]) <= answers(body, form["fields"]).keys()]
    return matches[0] if len(matches) == 1 else None


def label_names(issue: dict) -> set[str]:
    return {label["name"] for label in issue.get("labels", [])}


def held(labels: set[str], config: dict) -> bool:
    """Whether a maintainer took the issue over: a label of the incomplete label's family (`status/`) but that one."""
    family = config["incomplete"].split("/")[0] + "/"
    return any(label.startswith(family) and label != config["incomplete"] for label in labels)


def missing(form: dict | None, sections: dict[str, str]) -> list[str]:
    """The required fields of `form` left unanswered; the whole form when the issue came through none."""
    if form is None:
        return ["the answers of one of the forms"]
    boxes = {entry["label"] for entry in form["fields"] if entry["type"] == "checkboxes"}
    return [name for name in form["required"] if not answered(sections.get(name, ""), name in boxes)]


def labels_for(sections: dict[str, str], config: dict, known: set[str]) -> set[str]:
    """The labels the answers name: a dropdown's choice, each live code of the code field, a ticked paid plan."""
    found = set()
    for name, choices in config["answers"].items():
        choice = choices.get(sections.get(name, "").strip())
        if choice:
            found.add(choice)
    found |= set(CODE.findall(sections.get(config["codes"], "").upper()))
    if ticked(sections.get(config["paid"]["field"], "")):
        found.add(config["paid"]["label"])
    return found & known


def reply(fields: list[str], form: dict | None, config: dict) -> str:
    """The one reply to an incomplete issue. With no form, nothing an edit does is promised: a new issue is asked for."""
    days = config["close_after_days"]
    public = (
        "The issue is public: never add a licence key, a payment detail, personal data or your own SQL; a synthetic "
        "example is enough."
    )
    if form is None:
        return (
            "Thank you for writing. Every issue of this repository comes through one of its forms, so that it holds "
            "what a fix needs, and this one lacks the answers of one of the forms. Please open a new issue with a "
            f"form, and link this one in it: {config['chooser']}\n\n"
            f"{public} This issue is closed in {days} days."
        )
    return (
        "Thank you for writing. Every issue of this repository comes through one of its forms, so that it holds what "
        f"a fix needs, and this one lacks: {', '.join(fields)}. Please edit the issue to complete it, or open a new "
        f"one with a form: {config['chooser']}\n\n"
        f"{public} Without an answer in {days} days the issue is closed; completing the form by an edit reopens it."
    )


@dataclass
class Decision:
    add: list[str] = field(default_factory=list)
    remove: list[str] = field(default_factory=list)
    comment: str | None = None
    reopen: bool = False


def decide(
    issue: dict, config: dict, known: set[str], action: str = "opened", maintainer: bool | None = None
) -> Decision:
    """What the triage does to `issue`, as the API gives it, on an `issues` event of `action`; `maintainer` is the
    verdict of `author_is_maintainer`, the association alone when it is not given."""
    if maintainer is None:
        maintainer = issue.get("author_association") in MAINTAINERS
    current = label_names(issue)
    incomplete = config["incomplete"]
    closed = issue.get("state") == "closed"
    # A closed issue is the triage's only when the daily run closed it as incomplete.
    if maintainer or held(current, config) or (closed and incomplete not in current):
        return Decision()
    form = form_of(current, issue.get("body"), config)
    sections = answers(issue.get("body"), form["fields"]) if form else {}
    lacking = missing(form, sections)
    completing = not lacking and incomplete in current
    if closed and not completing:
        return Decision()  # still incomplete: it stays closed, and it had its reply
    # The answers' labels on opening and on the completing edit alone: a maintainer's correction outlives other edits.
    if action in OPENING or completing:
        found = labels_for(sections, config, known) | ({form["label"]} & known if form else set())
    else:
        found = set()
    add = found - current
    decision = Decision(add=sorted(add))
    if lacking and incomplete not in current:
        decision.add = sorted(add | {incomplete})
        decision.comment = reply(lacking, form, config)
    elif completing:
        decision.remove = [incomplete]
        decision.reopen = closed
    return decision


def stale(issues: list[dict], now: datetime, days: int) -> list[int]:
    """The numbers of the issues not updated for `days` days."""
    limit = now - timedelta(days=days)
    return [
        issue["number"]
        for issue in issues
        if datetime.fromisoformat(issue["updatedAt"].replace("Z", "+00:00")) <= limit
    ]


def gh(*args: str, stdin: str | None = None) -> str:
    return subprocess.run(["gh", *args], input=stdin, text=True, capture_output=True, check=True).stdout


def current(number: str, run=gh) -> dict:
    """The issue as it stands when the run starts, in the shape an `issues` event carries it. The event's copy is
    older: runs of one issue queue, and an edit made before an earlier run labelled the issue does not show its label."""
    return json.loads(run("api", f"repos/{{owner}}/{{repo}}/issues/{number}"))


def author_is_maintainer(issue: dict, run=gh) -> tuple[bool, str]:
    """Whether the issue's author is a maintainer, and the test that decided, for the run's log: their permission on
    the repository, one call (it needs the metadata scope, which the job's token always reads), or else, when the call
    fails, `author_association`."""
    login = (issue.get("user") or {}).get("login") or ""
    association = issue.get("author_association") or "NONE"
    if not LOGIN.fullmatch(login):
        why = "no login to ask about"
    else:
        try:
            answer = json.loads(run("api", f"repos/{{owner}}/{{repo}}/collaborators/{login}/permission"))
            permission = answer["permission"]
        except subprocess.CalledProcessError as refused:
            why = (refused.stderr or f"exit {refused.returncode}").strip().splitlines()[0][:200]
        except (ValueError, KeyError, TypeError) as unread:
            why = f"no permission in the answer: {type(unread).__name__}"
        else:
            return permission in WRITERS, f"{login}'s permission is {permission}"
    return association in MAINTAINERS, f"the permission could not be read ({why}); author_association {association}"


def maintainer_logged(number: str, issue: dict, run=gh) -> bool:
    maintainer, how = author_is_maintainer(issue, run)
    print(f"triage: issue {number}: {'a maintainer' if maintainer else 'not a maintainer'}, {how}")
    return maintainer


def on_event(path: Path, run=gh, root: Path = GITHUB) -> int:
    event = json.loads(path.read_text(encoding="utf-8"))
    number = str(event["issue"]["number"])
    issue = current(number, run)
    config = load("triage.json", root)
    known = {label["name"] for label in load("labels.json", root)}
    maintainer = maintainer_logged(number, issue, run)
    decision = decide(issue, config, known, event.get("action", "edited"), maintainer)
    # The reply first: `gh issue edit` fails on a label the repository lacks, and the reporter still gets it.
    if decision.comment:
        run("issue", "comment", number, "--body-file", "-", stdin=decision.comment)
    if decision.reopen:
        run("issue", "reopen", number)
    if decision.add:
        run("issue", "edit", number, "--add-label", ",".join(decision.add))
    if decision.remove:
        run("issue", "edit", number, "--remove-label", ",".join(decision.remove))
    return 0


def on_schedule(run=gh, root: Path = GITHUB, now: datetime | None = None) -> int:
    config = load("triage.json", root)
    listed = run(
        "issue",
        "list",
        "--state",
        "open",
        "--label",
        config["incomplete"],
        "--json",
        "number,updatedAt",
        "--limit",
        "500",
    )
    days = config["close_after_days"]
    for number in stale(json.loads(listed), now or datetime.now(UTC), days):
        issue = current(str(number), run)
        labels = label_names(issue)
        if held(labels, config):
            print(f"triage: issue {number} left open: a maintainer gave it a status")
            continue
        if maintainer_logged(str(number), issue, run):
            print(f"triage: issue {number} left open: a maintainer's issue")
            continue
        note = close_note(form_of(labels, issue.get("body"), config), config)
        run("issue", "close", str(number), "--reason", "not planned", "--comment", note)
    return 0


def close_note(form: dict | None, config: dict) -> str:
    """The note of the daily close: an issue with a form is reopened by the edit that completes it (`decide`); one
    with none is asked for a new issue, as its reply was."""
    days = config["close_after_days"]
    if form is None:
        return (
            f"Closed after {days} days: this issue came through none of the forms. Please open a new issue with a "
            f"form, and link this one in it: {config['chooser']}"
        )
    return f"Closed: the form was not completed within {days} days. Completing the form by an edit reopens the issue."


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) == 2 and args[0] == "event":
        return on_event(Path(args[1]))
    if args == ["close"]:
        return on_schedule()
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
