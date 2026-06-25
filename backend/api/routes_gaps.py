"""
Gap-related API routes.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import DATA_DIR
from models.gap import Gap, ResearchQuestion
from state import jobs

router = APIRouter(prefix="/gaps", tags=["gaps"])

# Demo gaps are regenerated alongside example_graph.json by
# scripts/generate_demo_graph.py and loaded from disk when present, so the
# leaderboard always resolves to nodes that actually exist in the demo graph.
_EXAMPLE_GAPS_PATH = DATA_DIR / "example_gaps.json"

# Hand-authored fallback used only if example_gaps.json is missing.
_FALLBACK_DEMO_GAPS: list[Gap] = [
    Gap(
        gap_id="gap_demo_001",
        type="cross_domain",
        node_a="scale-free networks",
        node_b="disease transmission",
        bridging_concepts=["networks", "spread", "dynamics"],
        field_a="Computer Science / Physics",
        field_b="Medicine / Epidemiology",
        leverage_score=94.0,
        score_components={
            "betweenness_centrality": 0.87,
            "community_reach": 0.92,
            "paper_velocity": 0.78,
            "cross_domain_bonus": 1.0,
        },
        question={
            "gap_id": "gap_demo_001",
            "question": "Do the degree distributions of social contact networks follow power-law properties analogous to scale-free networks, and if so, how does hub-node superspreading alter the epidemic threshold predicted by classical SIR models?",
            "why_matters": "Answering this would unify network topology mathematics with epidemiological modelling, enabling far more accurate outbreak predictions than compartmental models allow. It would explain why diseases spread faster than classical models predict and identify the 20% of nodes responsible for 80% of transmission.",
            "historical_analogy": "Analogous to Maxwell unifying electricity and magnetism in 1865 — two well-studied phenomena whose mathematical equivalence was invisible until the right framework was applied.",
            "model_used": "llama-3.3-70b-versatile",
            "generated_at": "2026-06-24T00:00:00+00:00",
        },
    ),
    Gap(
        gap_id="gap_demo_002",
        type="structural",
        node_a="network topology",
        node_b="infectious disease",
        bridging_concepts=["spread", "nodes", "transmission"],
        field_a="Computer Science",
        field_b="Medicine",
        leverage_score=81.0,
        score_components={
            "betweenness_centrality": 0.74,
            "community_reach": 0.80,
            "paper_velocity": 0.65,
            "cross_domain_bonus": 1.0,
        },
        question=None,
    ),
]


def _load_demo_gaps() -> list[Gap]:
    """Load regenerated demo gaps from disk, falling back to the hand-authored set."""
    if _EXAMPLE_GAPS_PATH.exists():
        try:
            raw = json.loads(_EXAMPLE_GAPS_PATH.read_text())
            return [Gap(**g) for g in raw]
        except Exception:
            pass
    return _FALLBACK_DEMO_GAPS


class QuestionsRequest(BaseModel):
    gap_ids: list[str]
    use_high_quality: bool = False


def _require_complete_job(job_id: str) -> dict:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["stage"] == "error":
        raise HTTPException(status_code=500, detail=f"Job failed: {job.get('error')}")
    if job["stage"] not in ("complete", "scoring", "detecting_gaps"):
        raise HTTPException(
            status_code=202,
            detail=f"Job not ready. Current stage: {job['stage']}",
        )
    return job


@router.get("/demo", response_model=list[Gap])
async def demo_gaps() -> list[Gap]:
    return _load_demo_gaps()


@router.get("/detect/{job_id}", response_model=list[Gap])
async def detect(job_id: str) -> list[Gap]:
    job = _require_complete_job(job_id)
    gaps = job.get("raw_gaps") or job.get("gaps") or []
    return gaps


@router.get("/score/{job_id}", response_model=list[Gap])
async def score(job_id: str) -> list[Gap]:
    job = _require_complete_job(job_id)
    gaps = job.get("gaps") or []
    return sorted(gaps, key=lambda g: g.leverage_score, reverse=True)


@router.post("/questions", response_model=list[ResearchQuestion])
async def generate_questions_endpoint(body: QuestionsRequest) -> list[ResearchQuestion]:
    from core.question_generator import generate_questions

    # Collect all gaps: demo gaps + all job gaps
    gap_lookup: dict[str, Gap] = {g.gap_id: g for g in _load_demo_gaps()}
    for job in jobs.values():
        for gap in job.get("gaps") or []:
            gap_lookup[gap.gap_id] = gap

    requested_gaps = [gap_lookup[gid] for gid in body.gap_ids if gid in gap_lookup]
    if not requested_gaps:
        raise HTTPException(status_code=404, detail="No matching gaps found")

    # For paper_count context, pull from the job's graph
    graph_lookup: dict[str, object] = {}
    for job in jobs.values():
        G = job.get("graph")
        if G:
            for gap in job.get("gaps") or []:
                graph_lookup[gap.gap_id] = G

    questions = await generate_questions(requested_gaps, graph_lookup)
    return questions
