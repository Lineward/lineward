# Install the `lineward` binary

Every integration launches `lineward` from `PATH`. Nothing installs it for you: the binary never
downloads anything, and neither do the plugins.

## From a release

Each release of this repository attaches one archive per platform and a `SHA256SUMS` file, signed with the release
key; [`verify.md`](verify.md) checks the signature, the SBOMs and which workflow built each archive, offline:

| Platform | Asset |
|---|---|
| Linux x64 (glibc 2.31+, Ubuntu 20.04 and later) | `lineward-linux-x64.tar.gz` |
| Windows x64 | `lineward-win32-x64.zip` |
| macOS x64 | `lineward-darwin-x64.tar.gz` |
| macOS arm64 (Apple silicon) | `lineward-darwin-arm64.tar.gz` |

```bash
VERSION=0.1.1
curl -LO https://github.com/Lineward/lineward/releases/download/v$VERSION/lineward-linux-x64.tar.gz
curl -LO https://github.com/Lineward/lineward/releases/download/v$VERSION/SHA256SUMS
sha256sum --check --ignore-missing SHA256SUMS
tar -xzf lineward-linux-x64.tar.gz
install -m 0755 lineward ~/.local/bin/lineward      # any directory on PATH
lineward --version
```

On Windows, extract `lineward.exe` to a directory on `PATH`.

## From the VS Code extension

The extension bundles the same binary at `<extension dir>/bin/lineward-<platform>-<arch>`; it can
be copied to `PATH` and renamed `lineward`.

## Licence key

Every `lineward` process — the language server, the MCP server and each command — reads the key
from the `LINEWARD_LICENSE_KEY` environment variable of the process that starts it, once, at
start-up. Set it in your shell profile, in the harness's MCP `env` block, or in CI secrets.
Never commit it. A server already running keeps the key it started with: after changing the key, restart the agent
that started the server. The VS Code extension is the exception: it passes the key entered with
`Lineward: Enter License Key`, and none when none was entered, whatever the shell exports.

## Check

```bash
lineward --help
lineward check --project path/to/dbt/project     # exit 3 without a key: expected
lineward init-agent --project path/to/dbt/project
```
