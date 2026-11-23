# Running in a container

Lineward publishes no image: you build one on the base image your organisation approves, from the release binary.
[`container.Dockerfile`](container.Dockerfile) is the recipe. Nothing is downloaded at runtime and no network is
needed.

## What the binary needs

| | |
|---|---|
| Platform | Linux x86_64, glibc 2.31 or newer (Debian 11+, Ubuntu 20.04+, RHEL 9+), `libgcc_s` |
| git | Only for `check --since`; install it in your base if you use it |
| User | Any non-root user; the project can be mounted read-only |
| Network | None. The MCP server listens on loopback only and never dials out |
| Licence | `LINEWARD_LICENSE_KEY` environment variable ([install.md § Licence key](install.md#licence-key)) — required by `check` and the other paid commands, which exit 3 without it, and by the MCP server: over HTTP it exits 3, over stdio it starts and refuses every tool and resource method, the listings included, naming the variable. An agent run in a container with no person in the session is unattended use, the language server included, and needs the key |

## Build

Download `lineward-linux-x64.tar.gz`, `THIRD_PARTY_NOTICES.md` and `SHA256SUMS` from one release, and
`container.Dockerfile` from this repository at that release's tag, into one directory; then:

```bash
sha256sum --ignore-missing -c SHA256SUMS
tar -xzf lineward-linux-x64.tar.gz
docker build -f container.Dockerfile --build-arg BASE=registry.internal/base/debian:12-slim -t lineward:0.1.1 .
```

`sha256sum` proves the files match the checksums; [`verify.md`](verify.md) also proves the release key signed them and
which workflow built them, with no network. Without `--build-arg BASE`, the recipe uses
`gcr.io/distroless/cc-debian12:nonroot`, which has no git.

## Run

The entrypoint is `lineward` and the project is mounted at `/project` (read-only is fine). The MCP server listens on
loopback only: it refuses `--bind 0.0.0.0` or any other address beyond loopback and exits 2, so a port published with
`-p` reaches nothing. Three routes remain.

### `lineward check` in CI

The image's default command reports the project's diagnostics once and exits: 0 when nothing is at or above the
threshold, 1 when something is.

```bash
docker run --rm -v "$PWD:/project:ro" -e LINEWARD_LICENSE_KEY lineward:0.1.1
docker run --rm -v "$PWD:/project:ro" -e LINEWARD_LICENSE_KEY \
  lineward:0.1.1 check --project /project --since origin/main --format sarif
```

(`--since` needs git in the image and the mounted directory to be a git checkout. git refuses a checkout another user
owns ("detected dubious ownership"), and the image runs as 65532: run the container as the checkout's owner,
`--user "$(id -u):$(id -g)"`, or, in your own base, trust the mount with
`git config --system --add safe.directory /project`.)

### MCP over stdio, the agent in the same container

Build the agent's own image with the recipe, its image as `--build-arg BASE=`, or copy `lineward` into it, and let the
agent start the server as its MCP server, as the plugins of this pack do:

```bash
lineward mcp --stdio --project /project
```

Nothing listens: the agent and the server talk over a pipe.

### MCP over HTTP, with host networking (Linux)

`--network host` shares the host's network, so the server's loopback is the host's: an agent on the same machine
reaches it, and no other machine does.

```bash
docker run --rm --network host -v "$PWD/analytics:/project:ro" -e LINEWARD_LICENSE_KEY \
  lineward:0.1.1 mcp --http 8080 --health-port 8081 --project /project
```

| | |
|---|---|
| MCP endpoint | `POST http://127.0.0.1:8080/mcp` |
| Health | `GET http://127.0.0.1:8081/health` → `200 {"status":"ok"}` |

Docker Desktop on macOS and Windows has host networking only in recent versions, where it is a setting to turn on;
without it, use stdio.
