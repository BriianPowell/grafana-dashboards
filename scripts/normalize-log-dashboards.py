#!/usr/bin/env python3
"""Normalize provisioned Loki log dashboards: trim export bloat, improve log panel UX."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "dashboards" / "logs"
LOKI_DS = {"type": "loki", "uid": "P8E80F9AEF21F6940"}

# Grafana Helm dashboard key -> (title, [(panel_title, job), ...])
SPECIAL = {
    "media/overseerr.json": (
        "Seerr",
        ["seerr"],
        [("Application", "loki.source.kubernetes.seerr")],
    ),
    "media/sonarr.json": (
        "Sonarr",
        ["sonarr", "media"],
        [
            ("TV", "loki.source.kubernetes.sonarr_tv"),
            ("Anime", "loki.source.kubernetes.sonarr_anime"),
        ],
    ),
    "media/bazarr.json": (
        "Bazarr",
        ["bazarr", "media"],
        [
            ("TV", "loki.source.kubernetes.bazarr"),
            ("Anime", "loki.source.kubernetes.bazarr_anime"),
        ],
    ),
}


def log_panel_options() -> dict:
    return {
        "dedupStrategy": "none",
        "enableLogDetails": True,
        "prettifyLogMessage": True,
        "showCommonLabels": False,
        "showLabels": True,
        "showTime": True,
        "sortOrder": "Descending",
        "wrapLogMessage": True,
    }


def make_log_panel(title: str, description: str, job: str, y: int, h: int) -> dict:
    return {
        "datasource": LOKI_DS.copy(),
        "description": description,
        "gridPos": {"h": h, "w": 24, "x": 0, "y": y},
        "options": log_panel_options(),
        "targets": [
            {
                "datasource": LOKI_DS.copy(),
                "editorMode": "code",
                "expr": f'{{job="{job}"}}',
                "queryType": "range",
                "refId": "A",
            }
        ],
        "title": title,
        "type": "logs",
    }


def clean_metadata(d: dict) -> None:
    for key in ("id", "liveNow", "weekStart", "fiscalYearStartMonth", "timezone", "uid"):
        d.pop(key, None)
    if d.get("links") == []:
        d.pop("links", None)
    if d.get("timepicker") == {}:
        d.pop("timepicker", None)
    if d.get("templating") == {"list": []}:
        d.pop("templating", None)
    d["schemaVersion"] = 39
    d["graphTooltip"] = 0
    d["refresh"] = "10s"
    d["editable"] = True


def clean_log_panel(panel: dict, y: int, h: int) -> None:
    panel.pop("id", None)
    panel.pop("pluginVersion", None)
    panel["datasource"] = LOKI_DS.copy()
    panel["gridPos"] = {"h": h, "w": 24, "x": 0, "y": y}
    panel["options"] = log_panel_options()
    for t in panel.get("targets", []):
        t.pop("key", None)
        t["datasource"] = LOKI_DS.copy()
        t["editorMode"] = "code"
        t["queryType"] = "range"
        if "expr" in t:
            expr = t["expr"].strip()
            expr = re.sub(r'\s*\|=\s*``\s*', "", expr)
            t["expr"] = expr


def rebuild_special(rel: str, spec: tuple) -> dict:
    title, tags_extra, panels_spec = spec
    tags = ["logs"] + list(tags_extra)
    n = len(panels_spec)
    base, extra = divmod(24, n)
    heights = [base + (1 if i < extra else 0) for i in range(n)]
    y = 0
    panels = []
    for i, (ptitle, job) in enumerate(panels_spec):
        panels.append(
            make_log_panel(
                ptitle,
                f"Loki stream `{job}`",
                job,
                y=y,
                h=heights[i],
            )
        )
        y += heights[i]
    return {
        "title": title,
        "tags": tags,
        "time": {"from": "now-6h", "to": "now"},
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": {"type": "grafana", "uid": "-- Grafana --"},
                    "enable": True,
                    "hide": True,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "type": "dashboard",
                }
            ]
        },
        "panels": panels,
    }


def normalize_file(path: Path) -> bool:
    rel = str(path.relative_to(LOGS_DIR))
    if rel in SPECIAL:
        data = rebuild_special(rel, SPECIAL[rel])
        clean_metadata(data)
    else:
        data = json.loads(path.read_text())
        clean_metadata(data)
        log_panels = [p for p in data.get("panels", []) if p.get("type") == "logs"]
        if not log_panels:
            return False
        n = len(log_panels)
        base, extra = divmod(24, n)
        heights = [base + (1 if i < extra else 0) for i in range(n)]
        y = 0
        log_i = 0
        for panel in data["panels"]:
            if panel.get("type") == "logs":
                clean_log_panel(panel, y, heights[log_i])
                y += heights[log_i]
                log_i += 1

    path.write_text(json.dumps(data, indent=2) + "\n")
    return True


def main() -> None:
    pihole = LOGS_DIR / "apps" / "pihole.json"
    if pihole.exists():
        pihole.unlink()
        print(f"removed {pihole.relative_to(ROOT)}")

    count = 0
    for path in sorted(LOGS_DIR.rglob("*.json")):
        if normalize_file(path):
            count += 1
            print(f"normalized {path.relative_to(ROOT)}")
    print(f"done: {count} dashboards")


if __name__ == "__main__":
    main()
