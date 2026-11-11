#!/usr/bin/env python3
"""Check dashboard JSON against the repo conventions (see AGENTS.md). Never rewrites files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

LOKI_UID = "P8E80F9AEF21F6940"
PROMETHEUS_UID = "PBFA97CFB590B2093"
EXPORT_KEYS = ("id", "uid")
LEGACY_SELECTOR = re.compile(r'job=\\?"loki\.source')
VARIABLE_REF = re.compile(r"^\$\{?(\w+)\}?$")


def datasources(node):
    if isinstance(node, dict):
        ds = node.get("datasource")
        if isinstance(ds, dict):
            yield ds
        for value in node.values():
            yield from datasources(value)
    elif isinstance(node, list):
        for item in node:
            yield from datasources(item)


def check(path: Path) -> list[str]:
    text = path.read_text()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]

    problems = []
    if text != json.dumps(data, indent=2) + "\n":
        problems.append("not formatted as json.dumps(indent=2) with a trailing newline")
    for key in EXPORT_KEYS:
        if key in data:
            problems.append(f'top-level "{key}" (export metadata; Grafana assigns it)')
    if LEGACY_SELECTOR.search(text):
        problems.append('legacy job="loki.source..." selector; use namespace/pod labels')
    bad_loki = {ds.get("uid") for ds in datasources(data) if ds.get("type") == "loki"} - {LOKI_UID}
    for uid in sorted(map(str, bad_loki)):
        problems.append(f"Loki datasource uid {uid!r}; expected {LOKI_UID!r}")

    ds_vars = {
        v.get("name")
        for v in data.get("templating", {}).get("list", [])
        if v.get("type") == "datasource" and v.get("query") == "prometheus"
    }
    for uid in sorted({str(ds.get("uid")) for ds in datasources(data) if ds.get("type") == "prometheus"}):
        ref = VARIABLE_REF.match(uid)
        if uid != PROMETHEUS_UID and not (ref and ref.group(1) in ds_vars):
            problems.append(
                f"Prometheus datasource uid {uid!r}; expected {PROMETHEUS_UID!r} "
                "or a Prometheus datasource variable defined in this dashboard"
            )
    return problems


def main(argv: list[str]) -> int:
    failed = False
    for name in argv:
        for problem in check(Path(name)):
            print(f"{name}: {problem}")
            failed = True
    if failed:
        print("To format a file: python3 -c 'import json,sys; p=sys.argv[1]; "
              "d=json.load(open(p)); open(p,\"w\").write(json.dumps(d, indent=2)+\"\\n\")' FILE")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
