"""
Score gaps by leverage: how much does bridging this gap unlock?

Components
----------
betweenness_delta   : estimated betweenness increase if gap edge added (proxy)
community_reach     : distinct communities bridged (directly + via bridge nodes)
paper_velocity      : (log) citation count of anchor nodes
cross_domain_bonus  : +1 if spans different fieldsOfStudy
"""
from __future__ import annotations

import math
from collections import defaultdict

import networkx as nx

from models.gap import Gap

# Weights for the final score (must sum to 1 after cross_domain_bonus separate)
_W_BETWEENNESS = 0.35
_W_COMMUNITY = 0.30
_W_VELOCITY = 0.25
_W_CROSS = 0.10


def _log_citation(G: nx.Graph, node: str) -> float:
    pc = G.nodes[node].get("paper_count", 1)
    return math.log1p(pc)


def _community_id(G: nx.Graph, node: str) -> int:
    return G.nodes[node].get("community_id", -1)


def _betweenness_proxy(G: nx.Graph, node_a: str, node_b: str, bridging: list[str]) -> float:
    """
    Proxy for how much betweenness the new edge would add.
    Uses the sum of degrees of anchor nodes and bridges, normalised by graph size.
    """
    n = max(G.number_of_nodes(), 1)
    deg_a = G.degree(node_a) if G.has_node(node_a) else 0
    deg_b = G.degree(node_b) if G.has_node(node_b) else 0
    bridge_deg = sum(G.degree(b) for b in bridging if G.has_node(b))
    raw = (deg_a + deg_b + bridge_deg) / n
    return min(raw, 1.0)


def _community_reach(G: nx.Graph, node_a: str, node_b: str, bridging: list[str]) -> int:
    """Count distinct communities touched by node_a, node_b, and bridge nodes."""
    comms: set[int] = set()
    for node in [node_a, node_b] + bridging:
        if G.has_node(node):
            comms.add(_community_id(G, node))
    return len(comms)


def score_gaps(G: nx.Graph, gaps: list[Gap]) -> list[Gap]:
    """
    Compute leverage_score (0-100) for each gap in-place.
    Returns the same list, mutated.
    """
    if not gaps:
        return gaps

    # Pre-compute global maxima for normalisation
    max_velocity = max(
        (math.log1p(G.nodes[n].get("paper_count", 1)) for n in G.nodes()),
        default=1.0,
    )
    max_betweenness = 1.0  # already capped at 1
    max_community = max(
        (
            _community_reach(G, gap.node_a, gap.node_b, gap.bridging_concepts)
            for gap in gaps
        ),
        default=1,
    )

    scored: list[Gap] = []

    for gap in gaps:
        bet = _betweenness_proxy(G, gap.node_a, gap.node_b, gap.bridging_concepts)
        comm = _community_reach(G, gap.node_a, gap.node_b, gap.bridging_concepts)

        vel_a = _log_citation(G, gap.node_a) if G.has_node(gap.node_a) else 0.0
        vel_b = _log_citation(G, gap.node_b) if G.has_node(gap.node_b) else 0.0
        velocity = (vel_a + vel_b) / 2.0

        cross = 1.0 if gap.field_a != gap.field_b else 0.0

        # Normalise each component to [0, 1]
        norm_bet = bet / max_betweenness
        norm_comm = comm / max(max_community, 1)
        norm_vel = velocity / max(max_velocity, 1)

        raw = (
            _W_BETWEENNESS * norm_bet
            + _W_COMMUNITY * norm_comm
            + _W_VELOCITY * norm_vel
            + _W_CROSS * cross
        )

        leverage = round(min(raw * 100, 100.0), 2)

        gap.leverage_score = leverage
        gap.score_components = {
            **gap.score_components,
            "betweenness_delta": round(norm_bet, 4),
            "community_reach": comm,
            "paper_velocity": round(norm_vel, 4),
            "cross_domain_bonus": cross,
        }
        scored.append(gap)

    # Sort descending by score
    scored.sort(key=lambda g: g.leverage_score, reverse=True)
    return scored
