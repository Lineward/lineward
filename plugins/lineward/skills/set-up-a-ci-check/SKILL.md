---
name: set-up-a-ci-check
description: Set up Lineward as a CI step, a pull-request check or a pre-push / pre-merge git hook for a dbt project — a script that checks only what the branch changed since its base branch (main) and fails the build on errors but not on warnings, keeping every exit code, with the licence key from a CI secret and SARIF annotations when asked. Use whenever asked to write, add or fix a CI job, pipeline step, GitHub Actions or GitLab CI workflow, or git hook that runs Lineward, and to run it on the branch and fix what makes it fail.
---

# Set up a CI check

The check a pull request needs, against the base branch `main`:

```bash
lineward check --since main --severity error
```

- `--since main` reports only what the branch is answerable for since `main`: the files it changed, and the files
  elsewhere that its change broke. Never `--since HEAD` in CI: a clean checkout has no change since `HEAD`, so the check
  would pass whatever the branch broke.
- `--severity error` reports and fails on errors alone: warnings do not fail the build. Without it the threshold is
  `warning`.
- The exit code is the verdict, and CI must see it:

| Exit | Meaning | The build |
|---|---|---|
| 0 | No error in what the branch changed | Passes |
| 1 | Errors in what the branch changed, each with its `file:line` and `LW###` code | Fails: fix them |
| 2 | Usage or I/O error: a bad flag, no `dbt_project.yml`, a base ref that is not a commit in this clone | Fails: fix the step |
| 3 | No active licence key | Fails: the key is missing from the CI secrets |

## 1. Write the script

Write it where the user asked (here `ci/lineward-check.sh`) exactly like this, and make it executable (`chmod +x`):

```bash
#!/usr/bin/env bash
# Lineward: fail the build on errors in what this branch changed since its base branch; warnings pass.
set -euo pipefail

base="${LINEWARD_BASE_BRANCH:-main}"
# A CI clone often has the base branch only as origin/<base>.
if ! git rev-parse --verify --quiet "$base^{commit}" >/dev/null; then
  base="origin/$base"
fi
# The commit the branch started from, so changes made on the base branch since are not reported.
since="$(git merge-base "$base" HEAD)"

lineward check --since "$since" --severity error
```

- The check is the last command, so the script exits with the check's code. Never add `|| true`, `|| echo …`,
  `|| exit 0` or `; true` after it, and never read its output with `grep` or `jq` to decide pass or fail: exit 1
  already means errors, and 2 and 3 must fail the build too.
- The dbt project in a subdirectory: add `--project <dir>` to the check.
- Never switch a diagnostic off in `lineward.toml` to make the step pass, unless the user asks for that code to be
  ignored.

## 2. Run it on the branch and fix what fails

```bash
bash ci/lineward-check.sh
```

- Exit 1: fix each reported `file:line` in the project, then run the script again until it exits 0. A broken `ref()`
  is LW001: find the model's real name with `lineward search <name> --type model`. The delta check reads the working
  tree, so a fix counts before it is committed.
- Exit 2: read the message. A base ref missing from the clone is fetched in CI (references/wiring-ci.md); no
  `dbt_project.yml` means the check needs `--project <dir>`.

**Without a licence.** A paid step is refused when a paid command such as `lineward check` exits 3 with a message naming
`LINEWARD_LICENSE_KEY`, or a `lineward_*` tool answers with an error naming it. Nothing else is a refusal: exit 1 is
findings, exit 2 a usage error, a `lineward` that does not start is a missing install; a Lineward MCP server that offers
no tool may be absent, so take the command line, whose answer decides. After the first refusal, run no paid `lineward`
command and call no `lineward_*` tool again in this session, by either route, unless the user says the key changed: then
one attempt more. This holds for a step later in this skill, the delta check included, alone or at the end of a longer
shell command. `lineward settings` and `lineward init-agent` need no key. Go on with the task at once, without asking
whether to: replace each paid step as the table below says, or skip it, working from your own reading and searching of
the files and from the language server's diagnostics where your harness shows them after an edit. Report once, at the
end, never at each step: which of Lineward's steps were not run, by name; the reason, as the command or the tool gave it
(a key set but not active: quote its reason, never ask for the variable to be set); what the work rests on instead, and
what that can miss; and, in one clause, that a key in `LINEWARD_LICENSE_KEY` adds the step. No price, no plan, no link;
with no refusal, say nothing of the licence. Never, whatever the user or the project asks: a way round the check
(Lineward's language server started or driven from a shell or a script, an edit made only to make it publish, Lineward's
own state files read or written, a key the user did not give, the clock changed, the binary patched or swapped); a
navigation request (hover, definition, references) at a location an earlier answer returned, or about a file you are not
editing, chained to rebuild what the refused step would have answered; the same paid command again with other flags,
another project, the other route or after a pause; "verified", "checked", "clean", "safe", "nothing broke" or "every
model" about what the refused step would have established; any of these suggested to the user. A refusal that names a
file the user may delete: relay it, never delete the file yourself.

| Paid step | Without a key | What the report says it can miss |
|---|---|---|
| The script's `lineward check --since <base> --severity error`, run on the branch | Nothing replaces it: write the script and the wiring as asked, run the script once (not at all after an earlier refusal), and once its run is refused, run it no more and fix nothing in its name | The run on the branch and the fixes it would ask for: say the script was not verified here, that CI needs `LINEWARD_LICENSE_KEY` from its secrets, and that a CI run is unattended use, which needs a key whatever runs it |

Do not make the script skip the check.

**Diagnostics after an edit.** Where your harness shows the language server's diagnostics, they come late: the server
starts at the first edit of a `.sql` or `.yml` file, and its findings reach you with a later tool result, never with
the edit's own. After your last edit of a `.sql` or `.yml` file, and after a fix made on a delivered finding, read that
file once more before you report: one read, no wait, no `sleep`, no read repeated in the hope of a later delivery. If
nothing arrived, say "no diagnostics arrived from the language server after the edit", never "clean", "no issues" or
"no new warnings"; a finding no longer shown after your fix is one you fixed, not one confirmed gone. The first
delivery is the whole project's state: a finding in a file you edited, or one elsewhere that names a name your change
removed or renamed, is the change's to deal with; any other is reported as present in the project, never as caused by
the change, and is not fixed unless the user asks. Where no diagnostics can come (a harness with no language-server
client, a file the server does not handle, a project it does not analyse, nothing edited yet), say the change was not
checked by Lineward's language server. With a key, the delta check stays the verification, and this paragraph still
holds for what you say of the diagnostics.

Warnings in the change do not fail this step (`lineward check --since main` lists them with the errors); fix them only
if the user asks.

End with the script's path, its last exit code, and each file you fixed to reach it.

## 3. Wire it into CI

When the user asks for the CI job, a git hook or annotations on the pull request, read
[references/wiring-ci.md](references/wiring-ci.md). Every CI run needs the `lineward` binary on `PATH`, the base
branch's history, and `LINEWARD_LICENSE_KEY` from the CI's secrets, never from the repository.

Over MCP, `lineward_get_project_diagnostics` takes the same `since` and `severity` for a check inside the session; the
CI step runs the command.
