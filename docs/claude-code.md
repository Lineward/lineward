# Claude Code

```text
/plugin marketplace add Lineward/lineward
/plugin install lineward@lineward
```

The plugin brings three things; `lineward` must be on `PATH` first ([install.md](install.md)).

1. **Language server** (`.lsp.json`) — `lineward lsp` for `.sql`, `.yml` and `.yaml`. Claude Code starts it at the
   first edit of one of those files and adds its diagnostics to the agent's context with a later tool result, not with
   the edit's own, so the skills read the edited file once more before they report. Free for one dbt™ project in a
   session with a person in it: with several `dbt_project.yml` beneath the folder Claude Code starts in, only the
   closest is analysed without a key; `LINEWARD_LICENSE_KEY` exported adds the others and column-level lineage.
   `claude -p` in a pipeline, like any session with no person in it, is unattended use and needs a key.
2. **MCP server** (`.mcp.json`) — `lineward mcp --stdio`, started in the directory Claude Code runs in. It serves one
   dbt™ project, the closest at or beneath that directory, and names the others in its instructions and in every
   `Model not found` answer: start Claude Code at the root of the project you work on. Paid: export
   `LINEWARD_LICENSE_KEY` in the shell that starts Claude Code, or the server offers no tool: it answers every tool
   method, the tool list included, with an error naming that variable, and its instructions name it. How each server
   reads the key: [install.md § Licence key](install.md#licence-key).
3. **Skills** — `edit-a-model`, `rename-a-column`, `fix-project-health`, `answer-lineage-questions`,
   `set-up-a-ci-check`, `tune-settings`.

## Optional: a check after every edit

Hooks are configured in `.claude/settings.json` of the project (or `~/.claude/settings.json`). A `PostToolUse` hook on
the edit tools runs the delta check. Claude Code shows the agent a `PostToolUse` hook's stderr only when the hook exits
2, so the command sends the report to stderr and turns a failing check into exit 2:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [{ "type": "command", "command": "lineward check --since HEAD --severity error 1>&2 || exit 2" }]
      }
    ]
  }
}
```

A clean check exits 0 and shows nothing. Errors in the change (exit 1), a usage error such as a project with no commit
yet (exit 2) and a missing key (exit 3) all reach the agent, with the findings or the message. The hook needs a key (it
is unattended use); with the language-server integration alone, the diagnostics of the files the agent edits reach it
with a later tool result, the one the skills make by reading the edited file once more.
