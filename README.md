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
