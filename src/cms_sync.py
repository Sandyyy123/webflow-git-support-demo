"""Normalize Webflow CMS items into deterministic, diff-friendly JSON snapshots."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

SNAPSHOT_DIR = os.path.join("data", "cms")


def normalize(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Reduce raw API items to the fields we track, sorted by id for stable diffs."""
    rows: List[Dict[str, Any]] = []
    for it in items:
        fd = it.get("fieldData", {})
        rows.append(
            {
                "id": it.get("id"),
                "name": fd.get("name"),
                "slug": fd.get("slug"),
                "fields": {k: v for k, v in sorted(fd.items()) if k not in ("name", "slug")},
            }
        )
    rows.sort(key=lambda r: r["id"] or "")
    return rows


def snapshot_path(collection: str) -> str:
    return os.path.join(SNAPSHOT_DIR, f"{collection}.json")


def write_snapshot(collection: str, items: List[Dict[str, Any]]) -> str:
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    path = snapshot_path(collection)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(normalize(items), fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    return path


def read_snapshot(collection: str) -> List[Dict[str, Any]]:
    path = snapshot_path(collection)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)
