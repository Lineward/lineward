# Release notes

What changed for you in each release of Lineward for dbt™: the `lineward` binary, the VS Code extension, and this
repository's plugin, skills and setup pages. The newest release comes first, and each section is the text of that
release's page under [Releases](https://github.com/Lineward/lineward/releases). A section names any change to the
lineage export's format or facet versions, the issues it closes as `Lineward/lineward#<number>`, and the author of
each pull request ported to it, by their GitHub name ([`CONTRIBUTING.md`](CONTRIBUTING.md)).

## 0.1.1

The extension's page on the stores and its licence file. Nothing changes in what Lineward does.

- **The extension's page:** rewritten to follow [lineward.dev](https://lineward.dev): the free features first, what
  needs a Pro key named where it is, and links to support, the terms of service and the privacy policy.
- **The licence file:** the extension ships the French contract alone, the version that binds, with a link to its
  English translation on lineward.dev. The terms themselves are those of 0.1.0.
- **The binary, the plugin and the skills:** those of 0.1.0, under the new version.
- **Lineage export:** no change to the format or to the facet versions.

## 0.1.0

The first release of Lineward for dbt™: the offline, no-registration dbt™ analysis engine that brings dbt™ OSS the
tooling it lacks, free from vendor lock-in.

- **What it holds:** the VS Code extension; the `lineward` binary, with its language server, its MCP server and its
  command line; and the plugin for Claude Code and Codex CLI, with its skills and setup pages.
- **Without a licence key:** the skills keep working in a session with a person in it, on the language server's
  diagnostics and the agent's own reading of the files, and say which of Lineward's checks they did not run. A session
  with no person in it, a pipeline or a background agent, needs a key.
- **Platforms:** Linux x64 (glibc 2.31 and later), Windows x64, macOS x64 and macOS arm64 (Apple silicon).
- **Lineage export:** the OpenLineage format and facets that
  [`docs/openlineage.md`](https://github.com/Lineward/lineward/blob/v0.1.0/docs/openlineage.md) documents.
