"""
Generate research questions for gaps using the Groq API.
"""
from __future__ import annotations

import asyncio
import os
import re
from datetime import datetime, timezone

from groq import Groq

from config import GROQ_MODEL
from models.gap import Gap, ResearchQuestion

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


_PROMPT_TEMPLATE = """\
You are a research question generator for the Anti-Discovery Engine.

CONTEXT: Structural gap detected in the human knowledge graph:
- Concept A: {node_a} (field: {field_a}, {count_a} papers)
- Concept B: {node_b} (field: {field_b}, {count_b} papers)
- Gap type: {gap_type}
- Leverage score: {score}/100
- Bridging concepts: {bridging_concepts}

Generate ONE specific research question that would close this gap.
Respond in this exact format:
QUESTION: <the specific research question>
WHY_MATTERS: <2 sentences on what answering this unlocks>
HISTORICAL_ANALOGY: <one historical example of a similar gap being closed>\
"""


def _parse_response(text: str) -> tuple[str, str, str]:
    """Parse the structured response from the model."""
    question = ""
    why_matters = ""
    historical_analogy = ""

    for line in text.splitlines():
        if line.startswith("QUESTION:"):
            question = line[len("QUESTION:"):].strip()
        elif line.startswith("WHY_MATTERS:"):
            why_matters = line[len("WHY_MATTERS:"):].strip()
        elif line.startswith("HISTORICAL_ANALOGY:"):
            historical_analogy = line[len("HISTORICAL_ANALOGY:"):].strip()

    # Fallback if parsing failed
    if not question:
        question = text[:300]
    if not why_matters:
        why_matters = "This gap bridges important conceptual domains."
    if not historical_analogy:
        historical_analogy = "Similar to the unification of electromagnetism by Maxwell."

    return question, why_matters, historical_analogy


def _call_groq_sync(prompt: str) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=400,
    )
    return response.choices[0].message.content or ""


async def _generate_one(
    gap: Gap,
    graph_lookup: dict[str, object],
) -> ResearchQuestion:
    """Generate a research question for one gap."""
    G = graph_lookup.get(gap.gap_id)

    count_a = 1
    count_b = 1
    if G is not None:
        import networkx as nx
        _G: nx.Graph = G  # type: ignore
        if _G.has_node(gap.node_a):
            count_a = _G.nodes[gap.node_a].get("paper_count", 1)
        if _G.has_node(gap.node_b):
            count_b = _G.nodes[gap.node_b].get("paper_count", 1)

    prompt = _PROMPT_TEMPLATE.format(
        node_a=gap.node_a,
        field_a=gap.field_a,
        count_a=count_a,
        node_b=gap.node_b,
        field_b=gap.field_b,
        count_b=count_b,
        gap_type=gap.type,
        score=round(gap.leverage_score, 1),
        bridging_concepts=", ".join(gap.bridging_concepts) or "none identified",
    )

    # Run synchronous Groq call in a thread pool to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(None, _call_groq_sync, prompt)

    question, why_matters, historical_analogy = _parse_response(raw)

    return ResearchQuestion(
        gap_id=gap.gap_id,
        question=question,
        why_matters=why_matters,
        historical_analogy=historical_analogy,
        model_used=GROQ_MODEL,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


async def generate_questions(
    gaps: list[Gap],
    graph_lookup: dict[str, object],
) -> list[ResearchQuestion]:
    """Generate research questions for multiple gaps concurrently."""
    tasks = [_generate_one(gap, graph_lookup) for gap in gaps]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    questions: list[ResearchQuestion] = []
    for gap, result in zip(gaps, results):
        if isinstance(result, Exception):
            # Return a placeholder on error so one failure doesn't kill the batch
            questions.append(
                ResearchQuestion(
                    gap_id=gap.gap_id,
                    question=f"What connects {gap.node_a} and {gap.node_b}?",
                    why_matters="Error generating question: " + str(result),
                    historical_analogy="N/A",
                    model_used=GROQ_MODEL,
                    generated_at=datetime.now(timezone.utc).isoformat(),
                )
            )
        else:
            questions.append(result)  # type: ignore[arg-type]

    return questions
