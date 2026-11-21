# Codex CLI

Tested with Codex CLI 0.166.0 and 0.155.1. `lineward` must be on `PATH` first ([install.md](install.md)).

```bash
codex plugin marketplace add Lineward/lineward
codex plugin add lineward@lineward
```

A clone of this repository works as the marketplace too: `codex plugin marketplace add ./lineward`. Then
`codex plugin list` shows `lineward@lineward` installed and enabled at the pack's version, and `codex mcp list` the
`lineward` server with `LINEWARD_LICENSE_KEY` in its environment. Start a new Codex session after installing.

Codex reads the pack's Codex manifests, `.agents/plugins/marketplace.json` and
`plugins/lineward/.codex-plugin/plugin.json`, which load the plugin directory Claude Code loads, and uses two of its
three parts:

1. **MCP server** (`.mcp.json`) — `lineward mcp --stdio`, started in the directory Codex runs in, so start Codex at the
   root of the dbt™ project you work on (with several beneath the directory, the server serves the closest alone and
   names the others): Codex expands no `${…}` variable in a server's command line, so the plugin names no project
   path. Paid: export `LINEWARD_LICENSE_KEY` in the shell before starting Codex, or the server offers no tool: it
   answers every tool method, the tool list included, with an error naming that variable, and its instructions name
   it. Codex hands a stdio server only the variables its `env_vars` names; the plugin's names this one. How the server
   reads the key: [install.md § Licence key](install.md#licence-key).
2. **Skills** — listed as `lineward:edit-a-model`, `lineward:rename-a-column`, `lineward:fix-project-health`,
   `lineward:answer-lineage-questions`, `lineward:set-up-a-ci-check` and `lineward:tune-settings`. In Codex a skill is
   best invoked by name: `$lineward:answer-lineage-questions` in the prompt, for example.
3. **Language server** (`.lsp.json`) — not used: Codex has no language-server client, and the Codex manifest names
   none (§ Diagnostics).

## Without the plugin

In `~/.codex/config.toml`, or `.codex/config.toml` in a project Codex trusts:

```toml
[mcp_servers.lineward]
command = "lineward"
args = ["mcp", "--stdio"]
env_vars = ["LINEWARD_LICENSE_KEY"]
```

Without `env_vars`, the server starts with no key even when the shell exports one. The project is again the directory
Codex runs in. The skills are then not installed: [`../plugins/lineward/skills/`](../plugins/lineward/skills/) holds
them in the `SKILL.md` format.

A server already listening over HTTP — `lineward mcp --http 3100` in a shell that exports the key — is added with
`codex mcp add lineward --url http://127.0.0.1:3100/mcp`.

Codex speaks MCP's `initialize` handshake by default, which the server answers; revision `2026-07-28` works too, behind
Codex's own under-development flags (`features.mcp_connection_sharing` on stdio, `features.mcp_2026_07_28` over
HTTP). Nothing needs to be set. Tools and resources both work: Codex reads the server's resources through its built-in
resource tools.

## Diagnostics

Codex injects no diagnostics after an edit. The agent finds them by running `lineward check --since HEAD`, which
reports what its change broke, or by calling `lineward_get_project_diagnostics`. Both need the key; the commands Codex
runs in its shell inherit it from the shell that started Codex. Without a key, Codex gets no diagnostics from Lineward
at all, so the skills edit and answer from the files and say that no Lineward check was made.

Codex reads the project's `AGENTS.md`. Write the workflow there, so the agent runs the check after each edit:

```bash
lineward init-agent            # a "Using Lineward" section in the project's AGENTS.md
```

## Check it works

In a Codex session started at the project's root:

1. `/mcp` lists `lineward` among the active servers.
2. `$lineward:answer-lineage-questions which models use the column amount of orders?` loads the skill, and the answer
   comes from a Lineward tool or command, not from reading files.
3. Ask for an edit that breaks a model: with the section above in `AGENTS.md`, the agent runs
   `lineward check --since HEAD` after the edit and reports the finding.
