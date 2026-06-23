"""Diff a fresh CMS snapshot against the committed one and gate deploys on Git state."""
from __future__ import annotations

import subprocess
from typing import Any, Dict, List, Tuple


def _index(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {r["id"]: r for r in rows if r.get("id")}


def diff_snapshots(
    old: List[Dict[str, Any]], new: List[Dict[str, Any]]
) -> Tuple[List[str], List[str], List[str]]:
    """Return (added_ids, changed_ids, removed_ids) between two normalized snapshots."""
    old_idx, new_idx = _index(old), _index(new)
    added = [i for i in new_idx if i not in old_idx]
    removed = [i for i in old_idx if i not in new_idx]
    changed = [i for i in new_idx if i in old_idx and new_idx[i] != old_idx[i]]
    return sorted(added), sorted(changed), sorted(removed)


def working_tree_dirty(paths: List[str]) -> bool:
    """True if any of the given paths has uncommitted changes per `git status`."""
    out = subprocess.run(
        ["git", "status", "--porcelain", "--", *paths],
        capture_output=True,
        text=True,
    )
    return bool(out.stdout.strip())


def gate(snapshot_path: str) -> Tuple[bool, str]:
    """A deploy is allowed only when the snapshot is committed (clean working tree)."""
    if working_tree_dirty([snapshot_path]):
        return False, f"BLOCKED: {snapshot_path} has uncommitted CMS changes. Review and commit first."
    return True, "OK: CMS snapshot is committed. Safe to publish."
