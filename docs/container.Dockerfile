# The lineward command line and MCP server on a base image you choose (container.md).
#
# Build it in a directory holding the release's Linux binary and its notices, checked against SHA256SUMS:
#   lineward                  from lineward-linux-x64.tar.gz
#   THIRD_PARTY_NOTICES.md    the release asset of that name
#
#   docker build -f container.Dockerfile --build-arg BASE=<your base image> -t lineward .
#
# The base needs Linux x86_64 with glibc 2.31 or newer and libgcc_s; git only for `check --since`. An agent that runs in
# the same container can take this base too, and start `lineward mcp --stdio` itself.
ARG BASE=gcr.io/distroless/cc-debian12:nonroot
FROM ${BASE}
COPY lineward /usr/local/bin/lineward
COPY THIRD_PARTY_NOTICES.md /usr/share/doc/lineward/THIRD_PARTY_NOTICES.md
WORKDIR /project
# Any non-root user; 65532 is distroless's nonroot.
USER 65532:65532
ENTRYPOINT ["/usr/local/bin/lineward"]
# The project's diagnostics, once. The MCP server listens on loopback only, so over HTTP it needs host networking
# (container.md).
CMD ["check", "--project", "/project"]
