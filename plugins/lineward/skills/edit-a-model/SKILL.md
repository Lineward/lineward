---
name: edit-a-model
description: Edit or create a dbt model safely with Lineward — read the model's context (SQL, compiled SQL, upstream columns) before writing SQL, then check what the edit broke. Use whenever changing a model's SQL, adding a column, adding a ref() or source(), or creating a new model in a dbt project analysed by Lineward. Not for renaming or removing a column (rename-a-column) or clearing the project's findings (fix-project-health).
---

# Edit a dbt model

Lineward analyses the project's `.sql` and `.yml` files offline. Every finding has an `LW###`
code and a `file:line` location. Use the commands below from a shell; the same tools exist over
MCP as `lineward_get_node_context` and `lineward_get_project_diagnostics` when this session has
the Lineward MCP server — use one or the other, never both for the same question.

## Before writing SQL

1. Get the model's context in one call:

   ```bash
   lineward context <model>
   ```

   It returns the raw SQL, the compiled SQL and a table of every upstream model's columns with
   their types. Read column names from that table; never guess one. An error naming the model means the name is
   wrong, not that the model is missing: correct it with `lineward search <name> --type model`.

2. For a new model, get the context of each model it will `ref()` instead.

3. If the SQL uses a macro you do not know, find it: `lineward search <macro_name> --type macro`.

## While writing

- Reference other models with `{{ ref('name') }}` and raw tables with `{{ source('src', 'table') }}`,
  never with a hard-coded `schema.table` (LW028).
- A model must not `ref()` itself; use `{{ this }}` (LW030).
- Test a snippet before saving it, without writing a file:

  ```bash
  echo "select ... from {{ ref('stg_orders') }}" | lineward validate -
  ```

- If the model is new or gained columns, document them in the YAML file that describes the model, whatever its name
  (`git grep -n "name: <model>$" -- '*.yml' '*.yaml'` finds it); `lineward scaffold <model>` prints a complete entry
  inferred from the SQL. If `tests/expects/<model>.csv` (or `tests/samples/<model>.csv`) exists, add the new column
  to its header and a value to every row: the check reports LW021 until you do.

## After the edit

Run the delta check; it reports only what this change is answerable for, including models you
did not open:

```bash
lineward check --since HEAD
```

- Exit code 0: nothing at or above `warning`. Done.
- Exit code 1: fix every reported `file:line`, then run it again. Do not switch a diagnostic off
  in `lineward.toml` to make it pass unless the user asked for that.
- Exit code 2: read the message. Outside a git repository, or before its first commit, `--since HEAD` cannot run: run
  `lineward check` instead and report only the findings in the files you changed.

Over MCP, call `lineward_get_project_diagnostics` with `since: "HEAD"` and `severity: "warning"`: without `severity`
the tool also lists infos and hints, which the command leaves out.

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
| `lineward context` / `lineward_get_node_context` | Read the model's SQL, then the SQL and YAML of each model and source it reads; take column names from what those select or document, never a guess | The compiled SQL, the upstream columns' types |
| `lineward search` / `lineward_search_catalog` | `git grep` and a glob | A name only the parsed graph resolves |
| `lineward validate -` / `lineward_compile_and_validate` | Skipped: the diagnostics after the edit stand in, where your harness shows them | The render and the check of the SQL before it is written |
| `lineward scaffold` / `lineward_scaffold_yaml` | The YAML entry written by hand from the SQL | The inferred column types |
| `lineward check --since HEAD` / `lineward_get_project_diagnostics` | The diagnostics after the edit (below) | What the change broke in files it did not edit, and any proof that nothing new is reported |

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

End with the files you changed and the last check's result.
