# grafana-dashboards

Grafana dashboards for the k3s homelab ([k3s-collective](https://github.com/BriianPowell/k3s-collective)).

## Log dashboards (`dashboards/logs/`)

Panels query Loki with **Kubernetes labels**, aligned with Alloy in `apps/monitoring/alloy/config.yaml`:

```logql
{namespace="media", pod=~"deluge.*"}
```

Legacy selectors used `job="loki.source.kubernetes.<component>"`; those no longer match after the Alloy allowlist refactor.

Each log dashboard has the same layout: a log-volume chart by `detected_level`, an errors-and-warnings panel, then one logs panel per component. The `search` box (case-insensitive regex) and `level` filter apply to every panel, and dashboards refresh every 30s.

### Provisioned in Grafana

Wired from `apps/monitoring/grafana/helm-release.yaml` sidecar URLs:

- **App Logs** — adguard, atuin, home-assistant, keycloak, nextcloud, ntfy, wiki-js
- **Infra Logs** — cert-manager, cloudnative-pg, crowdsec, flux-system, kube-system, traefik
- **Media Logs** — *arr, deluge, plex, etc.

**Not provisioned** (no Alloy log shipping): `dashboards/logs/games/`, `dashboards/logs/monitoring/`, error-pages, nvidia, reflector, reloader. JSON files remain for reference or if collection is re-enabled.

## System dashboards (`dashboards/system/`)

Prometheus-backed, all provisioned in the **System** folder. Most are upstream exports, trimmed and pointed at the pinned datasource:

| Dashboard | Source |
| --- | --- |
| `adguard/` | [henrywhitaker3/adguard-exporter](https://github.com/henrywhitaker3/adguard-exporter) |
| `cloudnative-pg/` | [Grafana 20417](https://grafana.com/grafana/dashboards/20417) |
| `crowdsec/` | [crowdsecurity/grafana-dashboards](https://github.com/crowdsecurity/grafana-dashboards) (v5 overview) |
| `exportarr/` | [onedr0p/exportarr](https://github.com/onedr0p/exportarr) `dashboard2.json`, SABnzbd row removed |
| `flux/` | Flux cluster and control-plane stats (datasource variable `${DS_PROMETHEUS}`) |
| `k3s/` | Container panels rewritten for containerd cAdvisor labels |
| `node-exporter/` | [Grafana 1860](https://grafana.com/grafana/dashboards/1860) (Node Exporter Full) |
| `ntfy/` | ntfy server metrics |
| `smartctl/` | [Grafana 22604](https://grafana.com/grafana/dashboards/22604) |
| `traefik/` | [Grafana 17347](https://grafana.com/grafana/dashboards/17347) |

Prometheus scrapes most targets every 60s, but exporters that poll an app API on each scrape (exportarr, Plex, Home Assistant, …) run at 4m. A rate window needs two samples, so use `$__rate_interval` rather than fixed `[1m]`/`[5m]` windows, and set a panel min interval of `4m` on dashboards for 4m targets (as `exportarr/` does).

## Workflow

Grafana downloads each provisioned dashboard from its raw GitHub URL on `main`, so merging to `main` deploys it. To add or change a dashboard:

1. Edit or export it from Grafana, remove the top-level `id` and `uid`, and point Loki panels at the pinned datasource uid `P8E80F9AEF21F6940`.
2. Run `pre-commit run --all-files`. `scripts/check-dashboards.py` checks the format (`json.dumps(indent=2)`), uids, Loki selectors and datasource; it reports problems and never rewrites files.
3. For a new or renamed dashboard, add or update its URL in `apps/monitoring/grafana/helm-release.yaml` in [k3s-collective](https://github.com/BriianPowell/k3s-collective).
4. Open a pull request; the `pre-commit` check must pass before merging.
