# Security

Report a vulnerability privately, never in a public issue or discussion: on this repository's **Security** tab,
choose **Report a vulnerability**, or open
<https://github.com/Lineward/lineward/security/advisories/new>. GitHub's private vulnerability
reporting shows the report to the maintainer alone. Without a GitHub account, write to <security@lineward.dev>
instead, which reaches Lineward's security contact alone.

It covers Lineward as a whole: the `lineward` binary, its language server, MCP server and command line, the
editor extension, the plugin and skills of this repository, the files of this repository, and the signatures and
checksums of its releases.

A report gives:

- the version, the output of `lineward --version`, and the extension's version when the editor is involved;
- the surface: the extension, the command line, the language server or the MCP server, the plugin, a container;
- the steps that show the problem, on a project you may share;
- the impact: what an attacker gains, and under which conditions.

Leave out any licence key, credential or personal data, in a mail as in an advisory: the report does not need them.

Reports are handled on a best-effort basis, like all support: there is no SLA
(<https://lineward.dev/security>).

How to check that a release is genuine, offline: [`docs/verify.md`](docs/verify.md).
