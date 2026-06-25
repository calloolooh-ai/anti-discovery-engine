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

# A cross-domain spread chosen to surface *believable* gaps between distant
# disciplines — avoiding intra-CS pairs that read as mundane co-occurrence
# misses. Network science × epidemiology is kept alive for the historical demo.
# Physics/materials and climate ensure distinctly non-biology communities form.
FIELDS = [
    "network science",
    "epidemiology",
    "materials science",
    "climate change",
    "quantum computing",
    "evolutionary biology",
]
PAPERS_PER_FIELD = 60
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

    # --- Demo gap curation ---
    # Generic methodology concepts appear in many fields and produce trivially
    # intra-domain gaps (gene→data science labeled "Biology×Biology").
    # Filter them out of demo-facing gap nodes so the leaderboard shows
    # genuine disciplinary boundaries.
    _GENERIC_TERMS = {
        # methodology / tooling — appear in many fields, produce trivial gaps
        "data science", "machine learning", "deep learning", "algorithm",
        "software", "computer program", "programming language", "data mining",
        "statistics", "statistical model", "artificial intelligence",
        "database", "computation", "computational model", "simulation",
        "data analysis", "data management", "information retrieval",
        "natural language processing", "pattern recognition",
        # specific databases / interfaces that aren't scientific concepts
        "medline", "pubmed", "world wide web", "internet", "web service",
        "search engine", "r package", "python (programming language)",
        "scalability", "open access",
        # overly generic concepts
        "incidence (geometry)", "sample size", "survey methodology",
        "meta-analysis", "systematic review", "questionnaire",
        "management science", "decision sciences",
        # abstract philosophical / linguistic terms that sneak into corpora
        "statement (logic)", "clarity", "terminology", "proposition",
        "concept", "framework", "discourse", "paradigm", "ontology",
        "epistemology", "interoperability", "subtext", "convergence (economics)",
        "simple (philosophy)", "expansive", "convergence",
    }

    # Canonical domain groupings — used for cross-domain detection so that
    # "Biology" and "Biochemistry, Genetics and Molecular Biology" are treated
    # as the SAME domain and don't produce fake cross-domain gaps.
    _DOMAIN_GROUPS: dict[str, str] = {
        "Biology": "Biology",
        "Biochemistry, Genetics and Molecular Biology": "Biology",
        "Biochemistry": "Biology",
        "Genetics": "Biology",
        "Immunology and Microbiology": "Biology",
        "Evolutionary Biology": "Biology",
        "Neuroscience": "Biology",
        "Medicine": "Medicine",
        "Health Professions": "Medicine",
        "Nursing": "Medicine",
        "Pharmacology, Toxicology and Pharmaceutics": "Medicine",
        "Computer science": "Computer Science",
        "Computer Science": "Computer Science",
        "Engineering": "Computer Science",
        "Decision Sciences": "Computer Science",
        "Mathematics": "Mathematics",
        "Statistics": "Mathematics",
        "Physics": "Physics",
        "Physics and Astronomy": "Physics",
        "Quantum Computing": "Physics",
        "Chemistry": "Chemistry",
        "Materials Science": "Materials Science",
        "Environmental Science": "Environmental Science",
        "Earth and Planetary Sciences": "Environmental Science",
        "Geography": "Environmental Science",
        "Atmospheric Science": "Environmental Science",
        "Ecology": "Environmental Science",
    }

    def _canonical_domain(field: str) -> str:
        return _DOMAIN_GROUPS.get(field, field)

    def _is_generic(node: str) -> bool:
        return node.lower() in _GENERIC_TERMS

    def _gap_sort_key(g):
        # Primary sort: truly cross-domain first (using canonical groupings)
        ca = _canonical_domain(g.field_a)
        cb = _canonical_domain(g.field_b)
        is_cross = 0 if ca != cb else 1
        return (is_cross, -g.leverage_score)

    curated = [
        g for g in gaps
        if not _is_generic(g.node_a) and not _is_generic(g.node_b)
    ]
    curated.sort(key=_gap_sort_key)
    demo_gaps = curated[:N_DEMO_GAPS]

    # Fallback to unfiltered if curation left too few
    if len(demo_gaps) < 4:
        gaps.sort(key=_gap_sort_key)
        demo_gaps = gaps[:N_DEMO_GAPS]

    print(f"  gaps: total={len(gaps)} curated={len(curated)} demo={len(demo_gaps)}")

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
