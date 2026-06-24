"""
Regenerate the precomputed demo graph + demo gaps from live OpenAlex data.

Writes:
  data/example_graph.json   — GraphExport with top demo gaps marked as amber edges
  data/example_gaps.json    — the demo gap list served by /gaps/demo

Run:  cd backend && python3.13 scripts/generate_demo_graph.py
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_backend))

from config import EXAMPLE_GRAPH_PATH, DATA_DIR  # noqa: E402
from core.ingestion import fetch_papers_for_fields  # noqa: E402
from core.graph_builder import build_graph, graph_to_export_data  # noqa: E402
from core.gap_detector import detect_gaps  # noqa: E402
from core.leverage_scorer import score_gaps  # noqa: E402

# A cross-domain spread that produces interesting, legible gaps — and keeps the
# network-science x epidemiology storyline alive for the historical demo.
FIELDS = [
    "network science",
    "epidemiology",
    "machine learning",
    "genetics",
    "neuroscience",
    "materials science",
]
PAPERS_PER_FIELD = 45
N_DEMO_GAPS = 12

EXAMPLE_GAPS_PATH = DATA_DIR / "example_gaps.json"

# A hand-authored headline question, injected onto the top gap so the demo opens
# with a polished, concrete example.
HEADLINE_QUESTION = {
    "question": "Do the contact networks that carry real epidemics share the "
    "scale-free degree distributions studied in network science, and if so, how "
    "does hub-node superspreading move the epidemic threshold away from the value "
    "classical compartmental models predict?",
    "why_matters": "Answering this unifies network-topology mathematics with "
    "epidemiological modelling, yielding outbreak predictions that compartmental "
    "models cannot. It pinpoints the minority of nodes responsible for the "
    "majority of transmission.",
    "historical_analogy": "Like Maxwell unifying electricity and magnetism — two "
    "well-studied phenomena whose equivalence was invisible until the right "
    "framework connected them.",
    "model_used": "precomputed-demo",
    "generated_at": "2026-06-24T00:00:00+00:00",
}


async def main() -> None:
    print(f"Fetching {len(FIELDS)} fields x {PAPERS_PER_FIELD} papers from OpenAlex...")
    papers, failed = await fetch_papers_for_fields(FIELDS, PAPERS_PER_FIELD, None)
    print(f"  papers={len(papers)} failed_fields={failed}")

    G = build_graph(papers)
    print(f"  graph: nodes={G.number_of_nodes()} edges={G.number_of_edges()}")

    gaps = score_gaps(G, detect_gaps(G))
    demo_gaps = gaps[:N_DEMO_GAPS]
    print(f"  gaps: total={len(gaps)} demo={len(demo_gaps)}")

    # Inject the headline question onto the top gap.
    if demo_gaps:
        top = demo_gaps[0]
        q = dict(HEADLINE_QUESTION)
        q["gap_id"] = top.gap_id
        top.question = q

    export = graph_to_export_data(G, "demo", demo_gaps, failed)

    EXAMPLE_GRAPH_PATH.write_text(json.dumps(export, indent=2))
    EXAMPLE_GAPS_PATH.write_text(
        json.dumps([g.model_dump() for g in demo_gaps], indent=2)
    )
    print(f"Wrote {EXAMPLE_GRAPH_PATH} ({export['node_count']} nodes, "
          f"{export['edge_count']} edges, {export['gap_count']} gaps)")
    print(f"Wrote {EXAMPLE_GAPS_PATH} ({len(demo_gaps)} gaps)")


if __name__ == "__main__":
    asyncio.run(main())
