# grafana-dashboards

Grafana dashboards for the k3s homelab ([k3s-collective](https://github.com/BriianPowell/k3s-collective)).

## Log dashboards (`dashboards/logs/`)

Panels query Loki with **Kubernetes labels**, aligned with Alloy in `apps/monitoring/alloy/config.yaml`:

```logql
{namespace="media", pod=~"deluge.*"}
```

Legacy selectors used `job="loki.source.kubernetes.<component>"`; those no longer match after the Alloy allowlist refactor.

### Provisioned in Grafana

Wired from `apps/monitoring/grafana/helm-release.yaml` sidecar URLs:

- **App Logs** — adguard, atuin, home-assistant, keycloak, nextcloud, ntfy, wiki-js
- **Infra Logs** — cert-manager, cloudnative-pg, crowdsec, flux-system, kube-system, traefik
- **Media Logs** — *arr, deluge, plex, etc.

**Not provisioned** (no Alloy log shipping): `dashboards/logs/games/`, `dashboards/logs/monitoring/`, error-pages, nvidia, reflector, reloader. JSON files remain for reference or if collection is re-enabled.

## System dashboards (`dashboards/system/`)

Prometheus-backed (Flux, k3s, ntfy, …).

## Workflow

Grafana downloads each provisioned dashboard from its raw GitHub URL on `main`, so merging to `main` deploys it. To add or change a dashboard:

1. Edit or export it from Grafana, remove the top-level `id` and `uid`, and point Loki panels at the pinned datasource uid `P8E80F9AEF21F6940`.
2. Run `pre-commit run --all-files`. `scripts/check-dashboards.py` checks the format (`json.dumps(indent=2)`), uids, Loki selectors and datasource; it reports problems and never rewrites files.
3. For a new or renamed dashboard, add or update its URL in `apps/monitoring/grafana/helm-release.yaml` in [k3s-collective](https://github.com/BriianPowell/k3s-collective).
4. Open a pull request; the `pre-commit` check must pass before merging.
