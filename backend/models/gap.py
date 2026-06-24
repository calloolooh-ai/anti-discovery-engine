from __future__ import annotations
from pydantic import BaseModel


class Gap(BaseModel):
    gap_id: str
    type: str  # "structural"|"cross_domain"
    node_a: str
    node_b: str
    bridging_concepts: list[str]
    field_a: str
    field_b: str
    leverage_score: float  # 0-100
    score_components: dict
    question: dict | None = None


class ResearchQuestion(BaseModel):
    model_config = {"protected_namespaces": ()}

    gap_id: str
    question: str
    why_matters: str
    historical_analogy: str
    model_used: str
    generated_at: str


class HistoricalValidationResult(BaseModel):
    job_id: str
    target_gap: str
    engine_detected: bool
    detected_gap: Gap | None = None
    known_gap_description: str
    actual_discovery_year: int
    key_papers: list[str]
    completed_at: str
