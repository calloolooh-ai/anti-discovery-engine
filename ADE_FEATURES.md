# Anti-Discovery Engine — Feature List (Build Order)

## Core (must have — demo lives or dies on these)

1. **Paper ingestion pipeline** — fetch papers from Semantic Scholar API by field/topic, extract concepts and relationships
2. **Knowledge graph builder** — construct weighted graph (nodes = concepts, edges = co-occurrence/citation strength)
3. **Graph visualizer** — interactive visual of the knowledge graph, color-coded by field/density
4. **Structural gap detector (Type A)** — find concept pairs that should be connected but aren't (graph topology analysis)
5. **Cross-domain gap detector (Type B)** — find fields with structural similarity but no methodological cross-pollination
6. **Gap question generator** — LLM call that takes a detected gap and outputs a specific, human-readable research question + why it matters
7. **Leverage scorer** — rank gaps by unlock potential (how many other problems does answering this unblock?)

## High Value (strong to have — elevates the demo)

8. **Historical validation mode** — run the engine on a corpus *before* a known major discovery and show the gap was detectable in advance
9. **Missing inversion detector (Type C)** — for studied phenomena, surface their unstudied inverses
10. **Field selector UI** — let user pick which scientific domains to include and watch the graph update live
11. **Gap detail panel** — click a gap in the visualizer, see the generated question, related papers, and leverage score
12. **Top 10 gaps leaderboard** — ranked list of highest-leverage unexplored questions surfaced by the engine

## Paper / Presentation Support (needed for judging, not the demo)

13. **Case study export** — generate a PDF/markdown report of the top gaps with citations and explanations (for the moonshot paper)
14. **Before/after comparison view** — show knowledge graph at time T vs T+5 years to illustrate how gaps close after discovery

## Stretch (only if time allows)

15. **Real-time query mode** — user types any topic, engine finds the nearest high-leverage gap in that area
16. **Collaboration network overlay** — show which research groups are positioned to close each gap
17. **Funding gap analysis** — cross-reference gaps with NSF/NIH grant data to show which gaps are also underfunded
18. **Email/alert system** — subscribe to a gap, get notified when a new paper edges toward closing it
