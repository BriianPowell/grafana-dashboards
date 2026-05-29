#!/usr/bin/env python3
"""Strip export-only fields from large system/metrics dashboards (root metadata only)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYSTEM_DIR = ROOT / "dashboards" / "system"


def clean_root(d: dict) -> None:
    for key in ("id", "liveNow", "weekStart", "uid"):
        d.pop(key, None)
    if d.get("links") == []:
        d.pop("links", None)
    if d.get("timepicker") == {}:
        d.pop("timepicker", None)
    if d.get("fiscalYearStartMonth") == 0:
        d.pop("fiscalYearStartMonth", None)
    if d.get("timezone") in ("", "browser"):
        d.pop("timezone", None)


def main() -> None:
    for path in sorted(SYSTEM_DIR.rglob("*.json")):
        data = json.loads(path.read_text())
        clean_root(data)
        path.write_text(json.dumps(data, indent=2) + "\n")
        print(f"cleaned {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
