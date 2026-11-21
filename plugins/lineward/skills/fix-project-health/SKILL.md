---
name: fix-project-health
description: Work through a dbt project's Lineward diagnostics code by code — broken refs, undocumented models, column drift, missing tests, hard-coded table references — with the right fix for each LW### code and a verified clean result. Use when asked to clean up, fix warnings, improve documentation coverage, or make `lineward check` pass on a dbt project.
---

# Fix a project's diagnostics

Get the whole picture once, then work by code, not by file: one code has one kind of fix, and
fixing it everywhere in one pass is faster and more consistent than fixing files one by one.

```bash
lineward check --severity info --format markdown
```

(Over MCP: `lineward_get_project_diagnostics` with `severity: "info"`.) The first line counts findings per severity;
the table lists every finding as `file:line | code | severity | message`. Errors first.

## By code

| Code | Meaning | Fix |
|---|---|---|
| LW001 / LW002 | `ref()` or `source()` names something that does not exist | Find the intended object with `lineward search <name>`; correct the name, or declare the source in `_sources.yml` |
| LW005 / LW030 | Circular dependency / model refs itself | Break the cycle; a model refers to its own table with `{{ this }}` |
| LW007 | SQL syntax error | Fix the SQL; check a rewrite with `lineward validate <file>` before saving |
| LW008 | Column missing from `GROUP BY` | Add it to `GROUP BY` or aggregate it |
| LW009 | Wrong argument count for a Snowflake function | Fix the call |
| LW010 | A column the referenced model does not output (`Column 'X' not found in model 'Y'`) | Read `Y`'s columns in the upstream schemas of `lineward context <the model reported>` and use the name `Y` outputs; add the column upstream only if the user asks |
| LW011 | Model has no downstream consumers | Ask before deleting: it may be a mart consumed outside dbt |
| LW012 | Model has no description | Write one in `schema.yml`; `lineward scaffold <model>` gives the entry |
| LW013 | Model has no tests | Add `unique` / `not_null` on the key column in `schema.yml` |
| LW014 | Column documented but not in the SQL | Remove the stale entry, or the column was renamed — see the rename-a-column skill |
| LW015 / LW024 | Column in the SQL but undocumented | Add it to `schema.yml`; `lineward scaffold <model>` lists every column with its type |
| LW020 / LW021 | A CSV fixture's header and the model's YAML disagree: a column in the fixture the YAML does not declare, or the reverse | Make the header of `tests/samples/<model>.csv` or `tests/expects/<model>.csv` match the model's documented columns, once LW014, LW015 and LW024 have made those its output, adding or dropping that column's cell in every row |
| LW028 | Hard-coded `schema.table` reference | Replace with `{{ ref() }}` or `{{ source() }}` |
| LW031 | `lineward.toml` and `.vscode/settings.json` disagree on a setting | Edit neither file in this pass: name the key and its two values, say that `lineward.toml`'s applies, and propose the alignment as the tune-settings skill does, applying it only when the user says so |

For any other code, the message says what is wrong; `file:line` says where.

## Rules

- Never switch a diagnostic off in `lineward.toml` to make the count drop, unless the user asks
  for that code to be ignored.
- Never edit `lineward.toml` or `.vscode/settings.json` without the user's word: propose the change instead.
- Change what the message names and nothing else in the same pass; keep unrelated refactors out.
- After each pass, run `lineward check --since HEAD --severity info` to see what the pass itself
  introduced, then the full `lineward check` to confirm the count went down. An exit 2 of the first: read the message.
  Outside a git repository, or before its first commit, `--since HEAD` cannot run: run the full check alone.

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
| `lineward check --severity info` / `lineward_get_project_diagnostics` | The findings the user names from their editor, whose diagnostics need no key; once an edit has started the language server, the diagnostics it delivers (below). With neither, ask the user which findings or files to work on: the one question this allows | The project's complete list, and the counts before and after, which the report never gives as Lineward's |
| `lineward search`, `lineward validate`, `lineward context`, `lineward scaffold` / their tools | As the edit-a-model skill says: `git grep` and a glob, the SQL and YAML read in the files, the YAML entry written by hand; `validate` skipped | As that skill says |

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

End with the count per code before and after, and every finding you left, with why.
