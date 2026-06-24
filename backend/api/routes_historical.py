"""
Historical validation API routes.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from models.gap import HistoricalValidationResult
from state import jobs

router = APIRouter(prefix="/historical", tags=["historical"])


@router.post("/run")
async def run_historical(background_tasks: BackgroundTasks) -> dict:
    from core.historical_mode import run_historical_validation

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "stage": "fetching",
        "progress": 0,
        "eta_seconds": None,
        "error": None,
        "mode": "historical",
    }
    background_tasks.add_task(run_historical_validation, job_id, jobs)
    return {"job_id": job_id}


@router.get("/result/{job_id}", response_model=HistoricalValidationResult)
async def get_historical_result(job_id: str) -> HistoricalValidationResult:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("stage") == "error":
        raise HTTPException(status_code=500, detail=f"Job failed: {job.get('error')}")
    if job.get("stage") != "complete":
        raise HTTPException(
            status_code=202,
            detail=f"Still running. Stage: {job.get('stage')}",
        )
    result = job.get("result")
    if not result:
        raise HTTPException(status_code=500, detail="Result missing")
    return result
