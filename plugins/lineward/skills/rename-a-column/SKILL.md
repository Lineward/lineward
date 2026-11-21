---
name: rename-a-column
description: Rename or remove a column in a dbt model without breaking anything — measure the blast radius with Lineward, find every file that names the column (downstream models, schema YAML, unit-test fixtures and expect CSVs, seeds, docs blocks), change them all in one change, then prove nothing is left with a delta check and a search for the old name. Use for any column rename, column removal, or change of a column's meaning in a dbt project analysed by Lineward. To only ask what a rename or drop would break, without changing files, use answer-lineage-questions.
---

# Rename or remove a column

A column is named in more places than the models that select it: the YAML that documents it, the
CSV fixtures and unit tests that list it, sometimes a seed or a docs block. The blast radius finds
the models; a search for the name finds the rest. The rename is done when Lineward reports nothing
new and the old name is left only where it is meant to stay.

Over MCP the Lineward commands below are `lineward_analyze_blast_radius`, `lineward_search_catalog` and
`lineward_get_project_diagnostics`.

## 1. Measure the models

```bash
lineward blast-radius <model> <column>
```

The blast radius lists each downstream model that reads the column, with its file: those are the SQL to change. One
marked `downstream, does not read <column>` needs no change; one marked `downstream (no column-level info)`, and a
column named only inside a Jinja expression, are settled by the search of step 2. No downstream dependents: the SQL
change is local, but its YAML and fixtures still follow. An error naming the model or the column means the name is
wrong, not that nothing reads it: correct it from the error's list of columns or with `lineward search`.

## 2. List every file that names the column

The blast radius lists downstream models, snapshots and exposures (an exposure by its YAML file), never the YAML
entries, CSV fixtures or Markdown that name the column. From the project's root, search it for the column
as a whole word: `git grep` reads the tracked and new files and skips what `.gitignore` leaves out (`target/`,
`dbt_packages/`, `logs/`); it exits 1, printing nothing, when no file names the column. Outside a git repository,
use `grep -rnwI --exclude-dir=target --exclude-dir=dbt_packages --exclude-dir=logs --exclude-dir=.git <column> .`
instead. Then list the columns the YAML documents:

```bash
git grep -nwI --untracked <column>
lineward search <column> --type column
```

Sort every hit into one of these rows before editing anything:

| Where | What changes |
|---|---|
| The model that defines the column | Its SELECT: `<column> AS <new>` when it reads the column from a source or an upstream model, the new name where it computes it |
| Each downstream model that reads it | Every reference: select list, joins, filters, `group by`, window clauses. A model that passes the column through renames its own output too, unless the user wants that model's columns kept (then `<new> AS <column>`) |
| Schema and properties YAML | The `- name:` entry of the column under every model whose output changed, and the tests that name it (`relationships` `field:`) |
| Unit-test fixtures | The header of `tests/samples/<model>.csv` and `tests/expects/<model>.csv`, and the row keys of a `unit_tests:` block's `given` and `expect`, for every model whose columns changed |
| Seeds | Only when the column comes from the seed: its CSV header and its entry in the seeds' YAML. A seed with a column of the same name is another table |
| Docs blocks | A `{% docs %}` block may keep its name; renaming it renames every `doc()` call to it |
| Sources | Nothing: a `sources:` entry describes the raw table, whose column keeps its name |

Then change every row in the same change. Leave no alias of the old name "for compatibility" unless
the user asked for one. To remove a column instead, the same rows apply: drop it from each, and in a
CSV drop its cell from every row, not only the header; ask the user before removing a column a
downstream model needs.

## 3. Prove nothing is left

Run the delta check at its default severity, which includes warnings:

```bash
lineward check --since HEAD
```

Over MCP, call `lineward_get_project_diagnostics` with `since: "HEAD"` and `severity: "warning"`: without `severity`
the tool also lists infos and hints, which the command leaves out.

It reports what the change is answerable for, in the files you changed and in the ones you did not.
Each of these codes names a site step 2 missed:

| Code | Site missed |
|---|---|
| LW014 | A YAML entry still documents the old name |
| LW015, LW024 | A model outputs the new name and its YAML does not document it |
| LW020, LW021 | A sample or expect CSV still has the old name in its header |
| LW010 | A model still reads the old name through an alias (`p.payment_method`) |

Fix each `file:line` and run it again until it exits 0; an exit 1 at warning level is not done. An exit 2: read the
message. Outside a git repository, or before its first commit, `--since HEAD` cannot run: run `lineward check`
instead and report only the findings in the files you changed. Then search once more:

```bash
git grep -nwI --untracked <column>
```

Exit 1 with no output: no hit is left. Every hit left must be one step 2 kept: the source's column, the
`<column> AS <new>` alias, a seed of another table. The search is the proof for a model that names the old column
unqualified while it joins, which the check cannot place.

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
| `lineward blast-radius` / `lineward_analyze_blast_radius` | Step 2's `git grep` of the column, then the models that `ref()` the model, and the models that `ref()` those, read for the column in the files. Navigation at most for the hop being edited: find references of the column in the model you rename, never again at a model that answer named | A model that reads the column under another name, inside an expression or through a model in between |
| `lineward search --type column` / `lineward_search_catalog` | `git grep` of the column in the YAML files | As above |
| `lineward check --since HEAD` / `lineward_get_project_diagnostics` | The diagnostics after the edit (below), then step 3's `git grep`, which needs no key and stays | What the change broke in files it did not edit, and any proof that nothing new is reported |

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

End with every file you changed, and each hit of the old name you kept, with why.
