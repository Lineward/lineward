# Lineward for dbt™

The offline, no-registration dbt™ analysis engine that brings dbt™ OSS the tooling it lacks, free from vendor lock-in.

This repository holds Lineward's releases, its plugin for coding agents, the setup pages and the tracker: it holds no
source code. It is generated from the product's private source tree on every release, and its version is the
binary's version.

## Install

- **The VS Code extension**, from the VS Code Marketplace:
  <https://marketplace.visualstudio.com/items?itemName=lineward.lineward-for-dbt>.
- **The `lineward` binary**, from this repository's [Releases](https://github.com/Lineward/lineward/releases): the
  archive of your platform, checked against `SHA256SUMS` (`sha256sum --check --ignore-missing SHA256SUMS`), then its
  signature, offline, as [`docs/verify.md`](docs/verify.md) shows. [`docs/install.md`](docs/install.md) has the
  commands.
- **The plugin**, which needs the binary on your `PATH`. In Claude Code:

  ```text
  /plugin marketplace add Lineward/lineward
  /plugin install lineward@lineward
  ```

  In Codex CLI, from a shell:

  ```bash
  codex plugin marketplace add Lineward/lineward
  codex plugin add lineward@lineward
  ```

Lineward is tested with Claude Code and Codex CLI. Both servers follow open standards over stdio: the language server
speaks LSP, and the MCP server implements the Model Context Protocol. Other agents that support them are expected to
work, but they are neither tested nor supported.

Codex CLI has no language-server client, so it gets no diagnostics after each edit: it finds them by running
`lineward check` and through the MCP diagnostics tool, both of which need a key.

| I use | Read |
|---|---|
| Every setup | [`docs/install.md`](docs/install.md) — get the `lineward` binary on your `PATH` first |
| Claude Code | [`docs/claude-code.md`](docs/claude-code.md) — one command installs the plugin |
| Codex CLI | [`docs/codex.md`](docs/codex.md) — two commands install the same plugin |
| CI, cloud agents, containers | [`docs/container.md`](docs/container.md) |
| A lineage catalog (OpenLineage) | [`docs/openlineage.md`](docs/openlineage.md) — export the model and column lineage as a file to load |
| Verify a release offline | [`docs/verify.md`](docs/verify.md) — the release key, the SBOMs, the build provenance |

The plugin's six skills, in the open `SKILL.md` format, live in [`plugins/lineward/skills/`](plugins/lineward/skills/);
another agent that reads that format loads them from there. With no plugin at all, `lineward init-agent` writes a
"Using Lineward" section into the project's `AGENTS.md`.

The language server and every diagnostic it reports are free in attended use. A key in `LINEWARD_LICENSE_KEY` unlocks
the MCP tools and the CLI commands but `init-agent` and `settings`, and any unattended use: CI, hooks, background
agents. Without a key, the skills keep working in a session with a person in it, on the language server's diagnostics
and the agent's own reading of the files, and say which of Lineward's checks they could not run. A session with no
person in it, a pipeline or a background agent included, is unattended use and needs a key, the language server's
diagnostics included. Plans: <https://lineward.dev/pricing>.

## Documentation

The website holds the documentation; this repository links it.

- [Overview](https://lineward.dev/docs)
- [Install](https://lineward.dev/install)
- [Agents](https://lineward.dev/agents)
- [Container and CI](https://lineward.dev/container)
- [Settings](https://lineward.dev/settings)
- [Command line](https://lineward.dev/cli)
- [Diagnostics](https://lineward.dev/diagnostics)
- [Security and privacy](https://lineward.dev/security)

## Report a problem

Issues are public: never post a licence key, a payment detail, personal data or your own SQL in one
([`CONTRIBUTING.md`](CONTRIBUTING.md), [`SUPPORT.md`](SUPPORT.md)), and everyone taking part follows the
[code of conduct](CODE_OF_CONDUCT.md).

- A bug: the form
  [Bug report](https://github.com/Lineward/lineward/issues/new?template=bug-report.yml).
- A wrong or missing diagnostic: the form
  [Diagnostic: false positive or missed problem](https://github.com/Lineward/lineward/issues/new?template=diagnostic.yml).
- A question or an idea: Discussions, [Q&A](https://github.com/Lineward/lineward/discussions/categories/q-a) or
  [Ideas](https://github.com/Lineward/lineward/discussions/categories/ideas).
- A vulnerability: [private vulnerability reporting](https://github.com/Lineward/lineward/security/advisories/new),
  never a public issue ([`SECURITY.md`](SECURITY.md)).

## Licence

This repository's own files, the plugin and its skills, the setup pages and the container recipe, are under the Apache
License 2.0 ([`LICENSE`](LICENSE), [`NOTICE`](NOTICE)). The Lineward software they set up, the `lineward` binary and
the VS Code extension, is closed source, under its End User License Agreement on the website.

---

[EULA](https://lineward.dev/legal/eula) · [Terms of Service](https://lineward.dev/legal/terms) ·
[Privacy Policy](https://lineward.dev/legal/privacy)

A French product — published by Lineward, France.

Lineward is an independent product. It is not affiliated with, endorsed by, or officially connected to dbt Labs, Inc.
dbt™ is a trademark of dbt Labs, Inc.
