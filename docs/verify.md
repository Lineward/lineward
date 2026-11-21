# Verify a release

Each release can be checked on a machine with no network: that the release key signed it, that no file changed since,
what each file contains, and which workflow built it. You need [cosign](https://github.com/sigstore/cosign) 3 or later,
a single binary you can carry to an offline machine with the release's files.

## What a release attaches

| File | What it is |
|---|---|
| `SHA256SUMS` | The SHA-256 of every other asset, SBOMs included |
| `SHA256SUMS.sigstore.json` | Its signature by the release key |
| `*.cdx.json` | The SBOMs, in CycloneDX 1.5 (below) |
| `<SBOM>.sigstore.json` | Each SBOM's signature by the release key |
| `<asset>.provenance.sigstore.json` | Each asset's build provenance (SLSA 1.0), signed by the release key |
| `trusted_root.json` | Sigstore's trust root as it stood when the release was signed; every bundle verifies against it |

The release key's public half is `keys/lineward-release.pub` in this repository, and the same key is published on the
Lineward website: compare the two before you trust either. It is not the key that signs licences.

## 1. The release key signed the checksums

```bash
cosign verify-blob --key lineward-release.pub --trusted-root trusted_root.json \
  --bundle SHA256SUMS.sigstore.json SHA256SUMS
sha256sum --check --ignore-missing SHA256SUMS
```

The first command fails unless the release key signed this exact `SHA256SUMS`; the second, unless each file you
downloaded is the one it lists.

## 2. What each file contains

| SBOM | Lists |
|---|---|
| `lineward-linux-x64.cdx.json`, `lineward-win32-x64.cdx.json`, `lineward-darwin-x64.cdx.json`, `lineward-darwin-arm64.cdx.json` | The crates linked into that platform's binary: its archive, and the .vsix of that platform |
| `lineward-vsix-npm.cdx.json` | The npm packages every .vsix bundles beside the binary |
| `lineward-vendored.cdx.json` | The third-party source text compiled into every binary |

Each SBOM is signed on its own, so it can be checked where it is ingested:

```bash
cosign verify-blob --key lineward-release.pub --trusted-root trusted_root.json \
  --bundle lineward-linux-x64.cdx.json.sigstore.json lineward-linux-x64.cdx.json
```

The binary also carries its own crate list, built in with `cargo auditable`: `cargo audit bin`, syft, trivy and grype
read it from the binary itself.

## 3. Which build made a file

```bash
cosign verify-blob-attestation --key lineward-release.pub --type slsaprovenance1 --trusted-root trusted_root.json \
  --bundle lineward-linux-x64.tar.gz.provenance.sigstore.json lineward-linux-x64.tar.gz
```

The command fails unless the release key signed a SLSA 1.0 provenance for this exact file. The release key is used only
by Lineward's release workflow, run from its source repository's `master` branch, and the signed provenance names that
workflow as its builder. Its source repository is private, so the address below opens nothing; it is what the
provenance records:

```bash
jq -r .dsseEnvelope.payload lineward-linux-x64.tar.gz.provenance.sigstore.json | base64 -d \
  | jq -e '.predicate.runDetails.builder.id == "https://github.com/Lineward/LSP-MCP/.github/workflows/release.yml@refs/heads/master"'
```

The command prints `true` and exits 0 when the provenance the release key signed names that workflow on `master`, and
exits 1 otherwise. The provenance also names the commit that was built and the run that built it:
`jq -r .dsseEnvelope.payload lineward-linux-x64.tar.gz.provenance.sigstore.json | base64 -d | jq .predicate`.

## The trust root

Offline, `trusted_root.json` is what you trust for steps 1 to 3, beside the release key: the keys of Sigstore's
transparency log, which recorded each signature, at release time. With a network, the same commands without
`--trusted-root` check the bundles against Sigstore's current root, which cosign fetches itself.

If the release key ever changes, the new key is announced in that release's notes and on the website, and the old one
stays in `keys/` for the releases it signed.
