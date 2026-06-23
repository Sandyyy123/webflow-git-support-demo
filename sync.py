#!/usr/bin/env python3
"""CLI entry point for the Webflow + Git support helper.

Commands:
    snapshot   Pull the CMS collection into a versioned JSON snapshot.
    diff       Show added / changed / removed items vs the committed snapshot.
    gate       Exit 1 if the snapshot has uncommitted changes (pre-publish check).
"""
from __future__ import annotations

import argparse
import os
import sys

from src import cms_sync
from src.git_gate import diff_snapshots, gate
from src.webflow_client import WebflowClient


def _collection() -> str:
    return os.environ.get("WEBFLOW_COLLECTION_ID", "landing")


def cmd_snapshot(args: argparse.Namespace) -> int:
    client = WebflowClient(mock=args.mock)
    items = client.list_items(_collection())
    coll = _collection()
    path = cms_sync.write_snapshot(coll, items)
    print(f"Wrote {len(items)} item(s) to {path}")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    coll = _collection()
    old = cms_sync.read_snapshot(coll)
    client = WebflowClient(mock=args.mock)
    new = cms_sync.normalize(client.list_items(coll))
    added, changed, removed = diff_snapshots(old, new)
    print(f"added:   {added or 'none'}")
    print(f"changed: {changed or 'none'}")
    print(f"removed: {removed or 'none'}")
    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    coll = _collection()
    ok, msg = gate(cms_sync.snapshot_path(coll))
    print(msg)
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Webflow + Git support helper")
    parser.add_argument("--mock", action="store_true", help="use bundled sample data, no token")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fn in (("snapshot", cmd_snapshot), ("diff", cmd_diff), ("gate", cmd_gate)):
        sp = sub.add_parser(name)
        sp.add_argument("--mock", action="store_true", help="use bundled sample data, no token")
        sp.set_defaults(func=fn)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
