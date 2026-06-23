"""Thin Webflow Data API v2 client.

Fetches CMS collection items. In --mock mode it returns bundled sample items so
the rest of the pipeline can be exercised with no token and no network.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List

API_ROOT = "https://api.webflow.com/v2"

MOCK_ITEMS: List[Dict[str, Any]] = [
    {
        "id": "item-hero",
        "fieldData": {
            "name": "Landing Hero",
            "slug": "landing-hero",
            "headline": "Plan for your baby's future",
            "cta-label": "Get started",
            "is-published": True,
        },
    },
    {
        "id": "item-faq",
        "fieldData": {
            "name": "FAQ Block",
            "slug": "faq-block",
            "headline": "Questions, answered",
            "cta-label": "Read FAQ",
            "is-published": True,
        },
    },
]


class WebflowClient:
    def __init__(self, token: str | None = None, mock: bool = False):
        self.mock = mock
        self.token = token or os.environ.get("WEBFLOW_TOKEN", "")
        if not self.mock and not self.token:
            raise ValueError("WEBFLOW_TOKEN is required when not running with --mock")

    def list_items(self, collection_id: str) -> List[Dict[str, Any]]:
        """Return all CMS items for a collection (handles pagination)."""
        if self.mock:
            return MOCK_ITEMS

        import requests  # imported lazily so --mock needs no dependency

        items: List[Dict[str, Any]] = []
        offset = 0
        while True:
            resp = requests.get(
                f"{API_ROOT}/collections/{collection_id}/items",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "accept": "application/json",
                },
                params={"limit": 100, "offset": offset},
                timeout=30,
            )
            resp.raise_for_status()
            payload = resp.json()
            batch = payload.get("items", [])
            items.extend(batch)
            total = payload.get("pagination", {}).get("total", len(items))
            offset += len(batch)
            if not batch or offset >= total:
                break
        return items
