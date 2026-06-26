"""
Graph-related API routes.
"""
from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from config import EXAMPLE_GRAPH_PATH
from models.graph import BuildRequest, GraphExport, JobStatus
from state import jobs

router = APIRouter(prefix="/graph", tags=["graph"])


# ---------------------------------------------------------------------------
# Background pipeline
# ---------------------------------------------------------------------------

async def _run_build_pipeline(job_id: str, request: BuildRequest) -> None:
    from core.ingestion import fetch_papers_for_fields
    from core.graph_builder import build_graph, graph_to_export_data
    from core.gap_detector import detect_gaps
    from core.leverage_scorer import score_gaps

    def _set(stage: str, progress: int, eta: int | None = None) -> None:
        jobs[job_id].update({"stage": stage, "progress": progress, "eta_seconds": eta})

    try:
        _set("fetching", 5, 120)

        total_expected = len(request.fields) * request.max_papers_per_field

        def _progress_cb(fetched: int, total: int) -> None:
            pct = min(35, int(fetched / max(total, 1) * 35) + 5)
            eta = max(0, int((total - fetched) / max(fetched, 1) * S2_DELAY_EST))
            jobs[job_id].update({"stage": "fetching", "progress": pct, "eta_seconds": eta})

        S2_DELAY_EST = 1.1
        papers, failed_fields = await fetch_papers_for_fields(
            request.fields,
            request.max_papers_per_field,
            request.year_filter,
            _progress_cb,
        )
        jobs[job_id]["papers"] = papers
        jobs[job_id]["failed_fields"] = failed_fields

        _set("building", 40, 30)

        def _build_cb(step: int) -> None:
            jobs[job_id]["progress"] = 40 + step * 4  # 5 steps → +20

        G = build_graph(papers, _build_cb)
        jobs[job_id]["graph"] = G

        _set("detecting_gaps", 65, 15)
        raw_gaps = detect_gaps(G)
        jobs[job_id]["raw_gaps"] = raw_gaps

        _set("scoring", 80, 8)
        scored_gaps = score_gaps(G, raw_gaps)
        jobs[job_id]["gaps"] = scored_gaps

        _set("complete", 100, 0)

        # Build export once, cache it
        export_data = graph_to_export_data(G, job_id, scored_gaps, failed_fields)
        jobs[job_id]["export"] = export_data

    except Exception as exc:
        import traceback
        jobs[job_id].update(
            {
                "stage": "error",
                "progress": jobs[job_id].get("progress", 0),
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/build")
async def build_graph_endpoint(
    request: BuildRequest, background_tasks: BackgroundTasks
) -> dict:
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "stage": "fetching",
        "progress": 0,
        "eta_seconds": None,
        "error": None,
        "request": request,
    }
    background_tasks.add_task(_run_build_pipeline, job_id, request)
    return {"job_id": job_id}


@router.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str) -> JobStatus:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(
        job_id=job_id,
        stage=job["stage"],
        progress=job["progress"],
        eta_seconds=job.get("eta_seconds"),
        error=job.get("error"),
        failed_fields=job.get("failed_fields", []),
    )


@router.get("/export/demo")
async def export_demo() -> dict:
    """Return the pre-built demo graph without needing a build job."""
    if not EXAMPLE_GRAPH_PATH.exists():
        raise HTTPException(status_code=404, detail="Demo graph not found")
    return json.loads(EXAMPLE_GRAPH_PATH.read_text())


@router.post("/build/sync")
async def build_graph_sync(request: BuildRequest) -> dict:
    """Run the full pipeline synchronously and return graph + gaps in one response."""
    from core.ingestion import fetch_papers_for_fields
    from core.graph_builder import build_graph, graph_to_export_data
    from core.gap_detector import detect_gaps
    from core.leverage_scorer import score_gaps

    job_id = str(uuid.uuid4())
    papers, failed_fields = await fetch_papers_for_fields(
        request.fields,
        request.max_papers_per_field,
        request.year_filter,
    )
    G = build_graph(papers)
    raw_gaps = detect_gaps(G)
    scored_gaps = score_gaps(G, raw_gaps)
    export_data = graph_to_export_data(G, job_id, scored_gaps, failed_fields)

    return {
        "job_id": job_id,
        "graph": export_data,
        "gaps": [g.model_dump() for g in scored_gaps],
    }


@router.get("/export/{job_id}", response_model=GraphExport)
async def export_graph(job_id: str) -> GraphExport:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["stage"] != "complete":
        raise HTTPException(
            status_code=202,
            detail=f"Job not complete yet. Stage: {job['stage']}",
        )
    export = job.get("export")
    if not export:
        raise HTTPException(status_code=500, detail="Export data missing")
    return GraphExport(**export)
