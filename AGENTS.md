# grafana-dashboards

Grafana dashboard JSON for the k3s-collective homelab cluster: Loki log dashboards per app and
Prometheus system dashboards (Flux, k3s, ntfy). Grafana loads them from raw GitHub URLs on `main`
listed in `k3s-collective/apps/monitoring/grafana/helm-release.yaml`, so a push to `main` is a
deploy once merged; the only automated gate is the pre-commit workflow.

## Verify before you finish

Run these and fix failures before reporting a task done. Report which ones you ran.

```bash
pre-commit run --all-files   # merge markers, private keys, JSON validity, file size, ripsecrets
grep -rlE 'job=\\?"loki\.source' dashboards   # legacy selectors; must print nothing
```

- No tests. `.github/workflows/pre-commit.yml` runs the same pre-commit hooks on pull requests
  and pushes to `main`; there is nothing else in CI.
- Keep dashboards formatted as Python's `json.dumps(indent=2)` plus a trailing newline; all
  dashboards currently match, and the normaliser scripts write that format.
- After running a normaliser, run `git diff --stat` and confirm only the dashboards you meant
  to change moved.
- If you add, rename or move a provisioned dashboard, check that the URL list in the
  k3s-collective HelmRelease still matches the files (a sibling checkout:
  `grep -c 'grafana-dashboards/main' ../k3s-collective/apps/monitoring/grafana/helm-release.yaml`
  counts the entries).

## Commands

```bash
python3 scripts/normalize-log-dashboards.py     # rewrites dashboards/logs/**: layout, metadata, Loki datasource
python3 scripts/normalize-system-dashboards.py  # strips export metadata from dashboards/system/**
```

- The pre-commit hook is installed by the nix-config `tools` devShell (`.envrc`).
- `package.json` (husky, lint-staged, eslint, prettier) is unused: no Node in the devShell, husky
  not wired up (`core.hooksPath` unset), and `lint:fix` has a misplaced quote. Do not run
  `prettier:write`; it would reformat every file away from the `json.dumps` style.

## Layout

- `dashboards/logs/<group>/`: Loki log dashboards. Only some are provisioned; the README lists
  which (`games/`, `monitoring/` and a few infra ones are not).
- `dashboards/system/`: Prometheus dashboards, mostly upstream exports.
- `scripts/`: normalisers that rewrite dashboards in place. Read them before running.

## Conventions

- LogQL selectors use the Kubernetes labels Alloy sets (`namespace`, `pod`, `container`), e.g.
  `{namespace="media", pod=~"radarr.*"}`. `job="loki.source.kubernetes.*"` selectors no longer match.
- `normalize-log-dashboards.py` still writes legacy `job=` selectors for overseerr, sonarr and
  bazarr (its `SPECIAL` table). Running it as is breaks those three dashboards; fix the table first.
- Datasource uids: Loki is `P8E80F9AEF21F6940` (pinned in the HelmRelease). Prometheus panels use
  `PBFA97CFB590B2093`, which the HelmRelease does not pin (unverified against the live Grafana).
- Dashboards have no `uid` on purpose (the scripts strip it); Grafana assigns one.
- Never commit `node_modules/`, `.envrc` or `.direnv/` (a pre-commit hook blocks them).
- Never read, print or commit secrets (`.env`, keys, tokens).
- Do not commit or push unless asked.
