# Wiring the check into CI

The runner needs the Lineward binary on its `PATH`, the base branch's history, and the licence key: CI is unattended
use, so every run needs `LINEWARD_LICENSE_KEY`, from the CI's secrets and never from the repository. GitHub Actions:

```yaml
name: Lineward
on: pull_request
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # the base branch and the commit the pull request started from
      - name: Install Lineward
        run: |
          # The latest release; pin a version (releases/download/v<version>) for reproducible builds.
          base=https://github.com/Lineward/lineward/releases/latest/download
          curl -fsSLO "$base/lineward-linux-x64.tar.gz"
          curl -fsSLO "$base/SHA256SUMS"
          sha256sum --check --ignore-missing SHA256SUMS
          tar -xzf lineward-linux-x64.tar.gz
          sudo install -m 0755 lineward /usr/local/bin/lineward
      # Only when the project declares packages (packages.yml or dependencies.yml): install them first,
      # with the dbt your project uses, or restore a cached dbt_packages/.
      - run: bash ci/lineward-check.sh
        env:
          LINEWARD_LICENSE_KEY: ${{ secrets.LINEWARD_LICENSE_KEY }}
          LINEWARD_BASE_BRANCH: ${{ github.base_ref }}
```

Another CI: fetch the base branch with its history before the script (`git fetch origin main`), and set
`LINEWARD_BASE_BRANCH` to the pull request's target branch when it is not `main`. A git hook (`pre-push`, or the
repository's hook manager) runs the same `bash ci/lineward-check.sh`, and needs the key in the shell too.

A project that declares packages needs them installed before the check (`dbt deps`, or a cached `dbt_packages/`):
without them every changed model that refs a package's model reports LW001, an error, and on dbt 2.x one that calls
a package's macro reports LW027, an error too.

## Annotations on the pull request

Only when the user wants the findings on the pull request's diff: GitHub code scanning reads SARIF. Keep the one check
and send its report to a file; the script's last line becomes:

```bash
lineward check --since "$since" --severity error --format sarif > lineward.sarif
```

The redirect keeps the exit code. Upload the file in a later step that runs even when this one failed
(`github/codeql-action/upload-sarif` with `if: always()`).
