"""
Cascade Map — downstream ripple of closing a gap.

When a gap edge (a, b) is hypothetically closed (the discovery is made), the
new connection reshapes the graph's topology. Two effects ripple outward:

  1. Distance collapse — other open gaps whose endpoints get *closer* (or become
     reachable at all) once the edge exists.
  2. Centrality lift  — concepts whose betweenness centrality rises because new
     shortest paths now route through them. Gaps touching those concepts become
     more bridgeable. This is the visible "domino chain".

All computed on the in-memory NetworkX graph for a build job.
"""
from __future__ import annotations

import networkx as nx

_EPS = 1e-6
_MAX_AFFECTED = 40


def _dist(G: nx.Graph, a: str, b: str) -> float:
    if a not in G or b not in G:
        return float("inf")
    try:
        return nx.shortest_path_length(G, a, b)
    except nx.NetworkXNoPath:
        return float("inf")


def compute_cascade(G: nx.Graph, gaps: list, gap_id: str) -> dict:
    """
    Compute the cascade for `gap_id`.

    `gaps` is a list of Gap objects (must expose .gap_id, .node_a, .node_b).
    Returns a JSON-serialisable dict.
    """
    target = next((g for g in gaps if g.gap_id == gap_id), None)
    if target is None or target.node_a not in G or target.node_b not in G:
        return {
            "gap_id": gap_id,
            "found": False,
            "new_edge": None,
            "unlocked_gaps": [],
            "unlocked_count": 0,
            "affected_nodes": [],
        }

    a, b = target.node_a, target.node_b

    # Graph with the discovery made.
    G2 = G.copy()
    G2.add_edge(a, b, weight=1.0)

    # --- Centrality lift from adding the edge ---
    # 172-node graphs compute exact betweenness in well under a second; sample
    # k for larger graphs to stay responsive.
    n = G.number_of_nodes()
    k = None if n <= 400 else 200
    bc1 = nx.betweenness_centrality(G, k=k, weight=None, seed=42)
    bc2 = nx.betweenness_centrality(G2, k=k, weight=None, seed=42)
    delta = {node: bc2.get(node, 0.0) - bc1.get(node, 0.0) for node in G2.nodes()}

    affected_scored = sorted(
        ((node, d) for node, d in delta.items() if d > _EPS),
        key=lambda kv: kv[1],
        reverse=True,
    )
    affected_nodes = [a, b] + [node for node, _ in affected_scored[:_MAX_AFFECTED]]
    # dedupe preserving order
    seen: set[str] = set()
    affected_nodes = [x for x in affected_nodes if not (x in seen or seen.add(x))]

    # --- Downstream gaps that become more closable ---
    unlocked: list[dict] = []
    for g in gaps:
        if g.gap_id == gap_id:
            continue
        x, y = g.node_a, g.node_b
        before = _dist(G, x, y)
        after = _dist(G2, x, y)
        dist_drop = (before - after) if before != float("inf") else (
            10_000 if after != float("inf") else 0
        )
        lift = max(delta.get(x, 0.0), 0.0) + max(delta.get(y, 0.0), 0.0)

        if dist_drop > 0 or lift > _EPS:
            unlocked.append(
                {
                    "gap_id": g.gap_id,
                    "node_a": x,
                    "node_b": y,
                    "distance_before": None if before == float("inf") else int(before),
                    "distance_after": None if after == float("inf") else int(after),
                    "centrality_lift": round(lift, 6),
                    "_rank": (1 if dist_drop > 0 else 0, dist_drop, lift),
                }
            )

    unlocked.sort(key=lambda u: u["_rank"], reverse=True)
    for u in unlocked:
        u.pop("_rank", None)

    return {
        "gap_id": gap_id,
        "found": True,
        "new_edge": [a, b],
        "unlocked_gaps": unlocked,
        "unlocked_count": len(unlocked),
        "affected_nodes": affected_nodes,
    }
