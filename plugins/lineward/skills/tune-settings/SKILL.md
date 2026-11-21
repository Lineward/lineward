---
name: tune-settings
description: Explains and tunes Lineward's settings for a dbt project — each setting's effective value and source (lineward.toml, .vscode/settings.json, default), why a code is reported at its level on enabled or disabled models, settings with no effect or that disagree between CI and the editor; proposes the edit and applies it only when the user says so. Use to tune, review or explain Lineward's configuration, onDisabledNodes, the severity map, or to quiet a noisy diagnostic.
---

# Tune Lineward's settings

Read the settings as Lineward applies them before proposing anything: the precedence of the
layers, the disabled-node profile and the two severity maps decide each code's level, and a value
that looks set may have no effect.

```bash
lineward settings
```

(Over MCP: `lineward_get_settings`, which needs the key the command does not. `lineward settings --format json` gives
the same report to a script.) It changes nothing. It prints four sections:

| Section | What it says |
|---|---|
| Values | Every setting's effective value, and whether `lineward.toml`, the editor's settings or the default set it |
| Codes | Each LW code's level on an enabled model and on a disabled one, and what set each: a map entry, the `onDisabledNodes` profile, or the project's dbt line (`dbt_line`, named above the tables: `- dbt line: 2.x, from require-dbt-version`), which makes LW027 an Error on 2.x and a Warning otherwise |
| Findings | Settings that do not apply as written, have no effect or disagree, each with its correction |
| Suggestions | A few changes counted from the project's own findings, each with its count |

## Explain, then propose

1. Explain each finding in a sentence the user can act on, and what its correction changes.
2. For each suggestion, say what it would hide or keep, with its count, and that it is a choice:
   a team may want the findings it would hide.
3. Propose the edit as a diff of the file: `lineward.toml` for what the whole team and CI share,
   `.vscode/settings.json` only for one person's editor.
4. **Apply nothing until the user says so.** A settings change switches findings off for everyone
   who reads the file. When they agree, make that one edit, then run `lineward settings` again to
   show the finding gone, and `lineward check --severity info` for what the project now reports.

## What the findings mean

| Finding | Meaning | Usual correction |
|---|---|---|
| `settings_file` | `lineward.toml` holds a key it ignores, or a value out of range | Correct or remove the key, as the message says |
| `editor_entry` | The editor's settings hold an entry the server drops | Correct or remove the entry |
| `disabled_map_no_effect` | An entry of `[diagnostics.disabledNodes.severity]` changes nothing: the severity map sets that code `off` (off is final), the code never reaches a disabled model, or the profile already gives that level | Remove the entry; to see a code on disabled models, give it a level in `[diagnostics.severity]` instead of `off` |
| `disabled_map_raises` | A disabled model reports a code more severely than an enabled one | Lower it, unless that is the intent |
| `column_docs_unmatched` | A `columnDocs` pattern matches no model file or no output column | Correct the pattern or remove it |
| `settings_drift` | `lineward.toml` and `.vscode/settings.json` set one key to two values (LW031) | Align them: `lineward.toml`'s value applies on every surface |

## Rules

- Never switch a diagnostic off, or lower its level, to make a count drop unless the user asks for
  it; say what the change would hide.
- Keep `lineward.toml` the file that decides: an editor setting that disagrees with it is drift.
- A level set by the dbt line follows the dbt the project pins: propose a severity-map entry only if the team wants
  another level, and never change `require-dbt-version` to move it.

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
| `lineward_get_settings` | `lineward settings`, which needs no key and answers the same: no step is lost, and the report says nothing of the licence for it | Nothing |
| `lineward check --severity info` after an applied change | Skipped | What the project reports once the change applies |

`lineward settings` needs no key: report from it alone.
