"""
Graph persistence backed by MongoDB Atlas, with an in-memory fallback.

If MONGODB_URI is set, saved graphs are written to an Atlas collection so they
survive restarts and can be shared via a stable id. If it is unset (or the
driver/connection is unavailable), we transparently fall back to an in-process
dict so the rest of the app keeps working with zero configuration.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from config import MONGODB_DB, MONGODB_URI


class _MemoryStore:
    """Process-local fallback store. Lost on restart — good enough for dev/demo."""

    backend = "memory"

    def __init__(self) -> None:
        self._docs: dict[str, dict[str, Any]] = {}

    def save(self, doc: dict[str, Any]) -> str:
        share_id = uuid.uuid4().hex[:12]
        doc = {**doc, "share_id": share_id, "saved_at": _now()}
        self._docs[share_id] = doc
        return share_id

    def load(self, share_id: str) -> dict[str, Any] | None:
        return self._docs.get(share_id)

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        docs = sorted(
            self._docs.values(), key=lambda d: d.get("saved_at", ""), reverse=True
        )
        return [_summary(d) for d in docs[:limit]]


class _MongoStore:
    """MongoDB Atlas-backed store."""

    backend = "mongodb"

    def __init__(self, client: Any) -> None:
        self._col = client[MONGODB_DB]["saved_graphs"]

    def save(self, doc: dict[str, Any]) -> str:
        share_id = uuid.uuid4().hex[:12]
        self._col.insert_one({**doc, "share_id": share_id, "saved_at": _now()})
        return share_id

    def load(self, share_id: str) -> dict[str, Any] | None:
        doc = self._col.find_one({"share_id": share_id}, {"_id": 0})
        return doc

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        cursor = (
            self._col.find({}, {"_id": 0})
            .sort("saved_at", -1)
            .limit(limit)
        )
        return [_summary(d) for d in cursor]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _summary(doc: dict[str, Any]) -> dict[str, Any]:
    """Lightweight listing entry (no heavy nodes/edges payload)."""
    graph = doc.get("graph") or {}
    return {
        "share_id": doc.get("share_id"),
        "label": doc.get("label", "Untitled graph"),
        "saved_at": doc.get("saved_at"),
        "node_count": graph.get("node_count", 0),
        "edge_count": graph.get("edge_count", 0),
        "gap_count": graph.get("gap_count", 0),
    }


def _build_store() -> Any:
    if MONGODB_URI:
        try:
            from pymongo import MongoClient

            client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=4000)
            # Fail fast if the cluster is unreachable so we can fall back cleanly.
            client.admin.command("ping")
            print("[persistence] Connected to MongoDB Atlas.")
            return _MongoStore(client)
        except Exception as exc:  # noqa: BLE001 — any failure → safe fallback
            print(f"[persistence] MongoDB unavailable ({exc}); using in-memory store.")
    else:
        print("[persistence] MONGODB_URI not set; using in-memory store.")
    return _MemoryStore()


_store: Any | None = None


def get_store() -> Any:
    global _store
    if _store is None:
        _store = _build_store()
    return _store
