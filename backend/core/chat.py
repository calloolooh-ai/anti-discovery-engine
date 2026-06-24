"""
Graph-aware chatbot using Groq.
"""
from __future__ import annotations

import asyncio
import os

from groq import Groq

from config import GROQ_MODEL

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


_SYSTEM_PROMPT = """\
You are the Anti-Discovery Engine assistant. You help users understand a knowledge graph of scientific concepts and the research gaps it has detected.

A "gap" in this context is a pair of scientific concepts that are structurally related but have NEVER been studied together — representing an unexplored research opportunity.

You have access to the current graph context below. Use it to give specific, insightful answers.
Answer concisely (2-4 sentences unless detail is needed). Be enthusiastic about the science.

{graph_context}
"""


def _build_graph_context(graph_data: dict | None, gaps: list[dict]) -> str:
    if not graph_data and not gaps:
        return "No graph loaded yet. Ask the user to build a graph first."

    lines = []

    if graph_data:
        lines.append(f"GRAPH: {graph_data.get('node_count', 0)} concepts, "
                     f"{graph_data.get('edge_count', 0)} connections, "
                     f"{graph_data.get('gap_count', 0)} unexplored gaps detected.")
        communities = graph_data.get("communities", {})
        if communities:
            fields = list(communities.values())
            lines.append(f"Fields covered: {', '.join(fields)}")

    if gaps:
        lines.append(f"\nTOP GAPS (ranked by impact potential):")
        for i, g in enumerate(gaps[:5], 1):
            q = g.get("question") or {}
            question_text = q.get("question", "Not yet generated") if isinstance(q, dict) else "Not yet generated"
            lines.append(
                f"{i}. [{g.get('type','').replace('_',' ').title()}] "
                f"{g.get('node_a','')} ↔ {g.get('node_b','')} "
                f"(leverage: {g.get('leverage_score', 0):.0f}/100)\n"
                f"   Question: {question_text[:120]}{'...' if len(question_text) > 120 else ''}"
            )

    return "\n".join(lines)


def _call_groq_sync(messages: list[dict], system: str) -> str:
    client = _get_client()
    all_messages = [{"role": "system", "content": system}] + messages
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=all_messages,
        temperature=0.7,
        max_tokens=400,
    )
    return response.choices[0].message.content or ""


async def chat(
    messages: list[dict],
    graph_data: dict | None,
    gaps: list[dict],
) -> str:
    graph_context = _build_graph_context(graph_data, gaps)
    system = _SYSTEM_PROMPT.format(graph_context=graph_context)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _call_groq_sync, messages, system)
