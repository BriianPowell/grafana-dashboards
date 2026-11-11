# grafana-dashboards

Grafana dashboard JSON for the k3s-collective homelab cluster: Loki log dashboards per app and
Prometheus system dashboards (Flux, k3s, ntfy). Grafana loads them from raw GitHub URLs on `main`
listed in `k3s-collective/apps/monitoring/grafana/helm-release.yaml`, so a push to `main` is a
deploy once merged; the only automated gate is the pre-commit workflow.

## Verify before you finish

Run these and fix failures before reporting a task done. Report which ones you ran.

```bash
pre-commit run --all-files   # merge markers, private keys, JSON validity, file size, ripsecrets, dashboard conventions
```

- No tests. `.github/workflows/pre-commit.yml` runs the same pre-commit hooks on pull requests
  and pushes to `main`; there is nothing else in CI.
- `scripts/check-dashboards.py` (the `check-dashboards` hook) fails on: formatting other than
  Python's `json.dumps(indent=2)` plus a trailing newline, a top-level `id` or `uid`, legacy
  `job="loki.source..."` selectors, and any Loki datasource uid other than the pinned one. It
  reports and never rewrites; fix the file by hand (it prints a one-liner to reformat).
- If you add, rename or move a provisioned dashboard, check that the URL list in the
  k3s-collective HelmRelease still matches the files (a sibling checkout:
  `grep -c 'grafana-dashboards/main' ../k3s-collective/apps/monitoring/grafana/helm-release.yaml`
  counts the entries).

## Commands

- The pre-commit hook is installed by the nix-config `tools` devShell (`.envrc`).
- `package.json` (husky, lint-staged, eslint, prettier) is unused: no Node in the devShell, husky
  not wired up (`core.hooksPath` unset), and `lint:fix` has a misplaced quote. Do not run
  `prettier:write`; it would reformat every file away from the `json.dumps` style.

## Layout

- `dashboards/logs/<group>/`: Loki log dashboards. Only some are provisioned; the README lists
  which (`games/`, `monitoring/` and a few infra ones are not).
- `dashboards/system/`: Prometheus dashboards, mostly upstream exports.
- `scripts/check-dashboards.py`: the convention checker run by pre-commit.

## Conventions

- LogQL selectors use the Kubernetes labels Alloy sets (`namespace`, `pod`, `container`), e.g.
  `{namespace="media", pod=~"radarr.*"}`. `job="loki.source.kubernetes.*"` selectors no longer match.
- A dashboard exported from the Grafana UI needs its top-level `id` and `uid` removed and its
  Loki datasources pointed at the pinned uid before it passes the hook.
- Datasource uids: Loki is `P8E80F9AEF21F6940` (pinned in the HelmRelease). Prometheus panels use
  `PBFA97CFB590B2093`, which the HelmRelease does not pin (unverified against the live Grafana).
- Dashboards have no `uid` on purpose (the hook enforces it); Grafana assigns one.
- Never commit `node_modules/`, `.envrc` or `.direnv/` (a pre-commit hook blocks them).
- Never read, print or commit secrets (`.env`, keys, tokens).
- Do not commit or push unless asked.
