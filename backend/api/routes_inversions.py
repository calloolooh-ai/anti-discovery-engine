"""
Type-C inversion ("Antimatter Query") and Cascade Map API routes.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from state import jobs

router = APIRouter(tags=["inversions"])


def _require_job(job_id: str) -> dict:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found. Build a graph first (inversions need the live corpus).",
        )
    if job.get("stage") == "error":
        raise HTTPException(status_code=500, detail=f"Job failed: {job.get('error')}")
    return job


@router.get("/inversions/{job_id}")
async def get_inversions(job_id: str) -> dict:
    """Detect Type-C inversion gaps for a completed build job."""
    job = _require_job(job_id)

    # Cache on the job so repeated views are instant.
    if "inversions" in job:
        return {"job_id": job_id, "inversions": job["inversions"]}

    papers = job.get("papers")
    if not papers:
        raise HTTPException(
            status_code=202,
            detail=f"Corpus not ready. Stage: {job.get('stage')}",
        )

    from core.inversion_detector import detect_inversions

    G = job.get("graph")
    valid = set(G.nodes()) if G is not None else None
    inversions = detect_inversions(papers, valid)
    job["inversions"] = inversions
    return {"job_id": job_id, "inversions": inversions}


@router.get("/cascade/{job_id}/{gap_id}")
async def get_cascade(job_id: str, gap_id: str) -> dict:
    """Compute the downstream ripple of closing one gap."""
    job = _require_job(job_id)

    G = job.get("graph")
    gaps = job.get("gaps")
    if G is None or not gaps:
        raise HTTPException(
            status_code=202,
            detail=f"Graph not ready. Stage: {job.get('stage')}",
        )

    from core.cascade import compute_cascade

    return compute_cascade(G, gaps, gap_id)
