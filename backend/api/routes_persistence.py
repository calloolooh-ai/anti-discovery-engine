"""
Persistence routes — save / load / list knowledge graphs.

Backed by MongoDB Atlas when MONGODB_URI is configured, otherwise an in-memory
fallback (see core/persistence.py). Enables shareable graph permalinks.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.persistence import get_store
from state import jobs

router = APIRouter(prefix="/persistence", tags=["persistence"])


class SaveRequest(BaseModel):
    label: str = "Untitled graph"
    # Either persist a completed job by id, or pass an explicit graph/gaps payload.
    job_id: str | None = None
    graph: dict | None = None
    gaps: list[dict] | None = None


@router.get("/status")
async def status() -> dict:
    """Report which persistence backend is active."""
    return {"backend": get_store().backend}


@router.post("/save")
async def save(req: SaveRequest) -> dict:
    graph = req.graph
    gaps = req.gaps

    if graph is None and req.job_id:
        job = jobs.get(req.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        graph = job.get("export")
        scored = job.get("gaps") or []
        gaps = [g.model_dump() if hasattr(g, "model_dump") else g for g in scored]

    if not graph:
        raise HTTPException(
            status_code=400,
            detail="Provide a completed job_id or an explicit graph payload.",
        )

    share_id = get_store().save({"label": req.label, "graph": graph, "gaps": gaps or []})
    return {"share_id": share_id, "backend": get_store().backend}


@router.get("/recent")
async def recent(limit: int = 20) -> list[dict]:
    return get_store().list_recent(limit)


@router.get("/{share_id}")
async def load(share_id: str) -> dict:
    doc = get_store().load(share_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Saved graph not found")
    return doc
