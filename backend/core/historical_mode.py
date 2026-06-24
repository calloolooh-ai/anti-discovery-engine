"""
Historical validation mode.

Run the full pipeline with year_filter=2005 targeting the
network topology × epidemiology gap.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from config import HISTORICAL_GAPS_PATH
from models.gap import Gap, HistoricalValidationResult
from core.ingestion import fetch_papers_for_fields
from core.graph_builder import build_graph
from core.gap_detector import detect_gaps
from core.leverage_scorer import score_gaps

_TARGET_KEYWORDS = {
    "network", "topology", "scale-free", "epidemi", "disease", "spread",
    "infection", "contagion", "small-world", "graph theory",
}


def _gap_matches_target(gap: Gap) -> bool:
    """Check if this gap corresponds to the network × epidemiology gap."""
    combined = (
        gap.node_a + " " + gap.node_b + " " + gap.field_a + " " + gap.field_b
        + " " + " ".join(gap.bridging_concepts)
    ).lower()

    network_hit = any(k in combined for k in ("network", "topology", "graph", "scale"))
    epi_hit = any(k in combined for k in ("epidemi", "disease", "spread", "infection", "contagion"))
    return network_hit and epi_hit


async def run_historical_validation(job_id: str, state: dict) -> None:
    """
    Full async pipeline for historical mode. Mutates state[job_id].
    """
    def _set(stage: str, progress: int) -> None:
        state[job_id].update({"stage": stage, "progress": progress})

    _set("fetching", 5)

    fields = ["network science", "epidemiology", "graph theory", "infectious disease"]

    try:
        papers = await fetch_papers_for_fields(
            fields, max_papers_per_field=100, year_filter=2005
        )
        _set("building", 40)

        G = build_graph(papers)
        _set("detecting_gaps", 65)

        raw_gaps = detect_gaps(G)
        _set("scoring", 80)

        scored = score_gaps(G, raw_gaps)
        _set("complete", 100)

        # Load known gap data
        known: dict = {}
        if HISTORICAL_GAPS_PATH.exists():
            known = json.loads(HISTORICAL_GAPS_PATH.read_text())

        detected_gap: Gap | None = None
        for gap in scored:
            if _gap_matches_target(gap):
                detected_gap = gap
                break

        result = HistoricalValidationResult(
            job_id=job_id,
            target_gap=known.get("target_gap_name", "Network Science × Epidemiology"),
            engine_detected=detected_gap is not None,
            detected_gap=detected_gap,
            known_gap_description=known.get("description", ""),
            actual_discovery_year=known.get("actual_discovery_year", 2001),
            key_papers=known.get("key_papers", []),
            completed_at=datetime.now(timezone.utc).isoformat(),
        )

        state[job_id]["result"] = result

    except Exception as exc:
        import traceback
        state[job_id].update(
            {
                "stage": "error",
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
        )
