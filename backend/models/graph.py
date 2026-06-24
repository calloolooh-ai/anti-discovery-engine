from __future__ import annotations
from pydantic import BaseModel


class BuildRequest(BaseModel):
    fields: list[str]
    max_papers_per_field: int = 150
    year_filter: int | None = None


class JobStatus(BaseModel):
    job_id: str
    stage: str  # "fetching"|"building"|"detecting_gaps"|"scoring"|"complete"|"error"
    progress: int  # 0-100
    eta_seconds: int | None = None
    error: str | None = None
    failed_fields: list[str] = []  # fields that returned no papers (e.g. rate-limited)


class GraphNode(BaseModel):
    id: str
    label: str
    field: list[str]
    paper_count: int
    community_id: int
    x: float | None = None
    y: float | None = None


class GraphEdge(BaseModel):
    source: str
    target: str
    weight: float
    is_gap: bool
    gap_id: str | None = None
    gap_type: str | None = None  # "structural"|"cross_domain"


class GraphExport(BaseModel):
    job_id: str
    node_count: int
    edge_count: int
    gap_count: int
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    communities: dict[int, str]
    built_at: str
    failed_fields: list[str] = []  # fields that returned no papers (e.g. rate-limited)
