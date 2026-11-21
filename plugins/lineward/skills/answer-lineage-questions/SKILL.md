---
name: answer-lineage-questions
description: Answers questions about a dbt project's models and columns from Lineward's parsed graph instead of grep or file reads — which models use or hold some data, named or only described (an e-mail address, the personal data a privacy or GDPR review must list); where a column comes from; what dropping or renaming a column or model would break; what depends on a model. Use it before any grep or file read. Not for making the change itself (rename-a-column, edit-a-model).
---

# Answer a question about the project

A question that names data by what it holds rather than by its column — "the customer's e-mail
address", "the shipping country" — is a column question like any other: its first command is
`lineward search <word> --type column`, with one short word of the name such a column would have
(`email`, `country`), never a grep.

Lineward has parsed every model, YAML file and source of the project into a column-level graph. One
command answers a question from the whole of it, including the models a file search misses: a column
renamed on the way (`amount`→`payment_amount`), read inside an expression, or reached through a
model in between. On a project of hundreds of models, reading files is slow and still misses them.
Ask the graph first; open a file only to explain what the graph already named.

Over MCP the commands below are `lineward_search_catalog`, `lineward_trace_lineage`,
`lineward_analyze_blast_radius` and `lineward_get_node_context`.

1. Pick the command from the table below.
2. Run it before any `grep`, glob or file read, even to find a column's exact name: the search does that.
3. A list that ends on `> ⚠️ Showing <from>–<to> of <n>` has rows left out: run it again with `--offset <to>`
   (`offset` over MCP) until no such line is left, before naming "every" model. A line `> ⚠️ Cut at depth <n>` means
   the walk stopped: run it again with a larger `--depth` (`depth`), up to 50.
4. Answer from its output, and end your reply with the answer itself, each model by name.

## Pick the command by the question

| Question | Command |
|---|---|
| Where is a model, seed, snapshot, exposure, source, macro or documented column? | `lineward search <name>`, narrowed with `--type` |
| Which models use the column `<column>`? | `lineward search <column> --type column` lists the models and the source tables that document it; `lineward blast-radius <model> <column>`, from the model it starts in, adds every model downstream that reads it, documented or not |
| Which models use `<something>`, named by what it holds ("the customer's e-mail address", "the shipping country")? | `lineward search <word> --type column`, with one short word of the name such a column would have: `email`, `country` |
| Where does `<model>.<column>` come from? | `lineward lineage <model> <column>`: upstream, back to the source table |
| What breaks if `<column>` of `<model>` is dropped or renamed? | `lineward blast-radius <model> <column>`: every downstream model, and what the column becomes in each one that reads it |
| What breaks if the loader drops `<column>` of a source table? | `lineward blast-radius <source>.<table> <column>` (or `source:<source>.<table>`): every model that reads the table, and what the column becomes downstream |
| How does `<model>.<column>` flow downstream, hop by hop? | `lineward lineage <model> <column> --direction downstream` |
| What depends on `<model>`? | `lineward blast-radius <model>` |
| What does `<model>` select, and from which columns? | `lineward context <model>` |

## Read the answer

- `downstream, does not read <column>`: the model depends on yours and never reads the column; leave it out of a list
  of models that use it.
- `downstream (no column-level info)`: the analysis could not follow that model's SQL; open that model's SQL, and only
  that one, to settle it.
- `lineward search` matches one word of a name, never a description. `No results`: search another word, not the files.
- An error naming what you passed is not an answer about the project: `Model not found: <name>`, or a column the node
  does not have (the error lists its columns), means the name is wrong. Take the right one from that list or from
  `lineward search`, and run it again; never report it as "nothing depends on it". Where several dbt projects sit
  beneath the folder, one alone is served and the others are named: after `Model not found` over MCP (`This server
  serves the dbt project at <root> alone; also found: …`), on the command's stderr on the command line. The node may
  be another project's: run the command with `--project <that path>`, or tell the user that the MCP server must be
  started with `--project <that path>` to answer for it.

The arrow notation, exposures, installed packages and what the search lists:
[references/reading-the-answers.md](references/reading-the-answers.md), when an answer's form is unclear.

Answer with what the commands returned: the models, their columns, the source. Read a model's SQL
only to settle a model the graph could not follow, or to say how a model uses the column (inside a
`SUM`, as a join key), after the graph named it.

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
| `lineward search`, `lineward lineage`, `lineward blast-radius`, `lineward context` / their tools | `git grep`, then the SQL along the `ref()` chain, read in the files. No navigation request: a question edits nothing. The answer names each model found and how it was found | The graph's answer: a column renamed on the way, read inside an expression or reached through a model in between. Never "every model" |
