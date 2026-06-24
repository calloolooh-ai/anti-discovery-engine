# MVP: The Anti-Discovery Engine

## Core Idea
Science advances by asking questions. But which questions? Researchers pick questions based on what's already being studied — an enormous selection bias. The Anti-Discovery Engine maps the topology of human knowledge and identifies the **highest-leverage gaps**: questions that, if answered, would unlock multiple fields simultaneously. Not a search engine for what we know — a compass for what we don't.

---

## The Zero-to-One Claim
Every research tool ever built helps you go deeper into what's already being studied. Google Scholar, Semantic Scholar, Elicit — all of them help you find more of what already exists.

No tool has ever been built to systematically find **what isn't being asked.**

The Anti-Discovery Engine inverts the entire paradigm: instead of navigating the map, it finds the blank spaces.

---

## Architecture

### Layer 1 — Knowledge Graph Construction
- Ingest a large corpus of scientific papers (arxiv, PubMed, semantic scholar API)
- Extract: concepts, methods, relationships, citations, fields
- Build a weighted graph where nodes = concepts, edges = co-occurrence / citation / causal relationship
- Identify **field clusters** (dense regions) and **field boundaries** (sparse bridges)

### Layer 2 — Gap Detection
Three types of gaps:

**Type A — Structural Gaps:** Concepts that should be connected based on graph topology but aren't. If concept X is connected to Y and Y is connected to Z, but X and Z have no relationship, that's a candidate gap.

**Type B — Cross-Domain Voids:** Fields that share deep mathematical/structural similarity but have never borrowed methods from each other. (Example: epidemiology and information theory were structurally similar for decades before anyone used network science for disease spread.)

**Type C — Missing Inversions:** For every studied phenomenon, there's often an unstudied inverse. We study how diseases spread but not why they stop. We study memory formation but not strategic forgetting. We study economic growth but not the conditions that make it fragile.

### Layer 3 — Leverage Scoring
Score each gap by:
- **Unlock potential:** how many other open problems does answering this question unblock?
- **Cross-field impact:** how many fields would be affected?
- **Historical analogy:** has a similar type of gap been resolved before with outsized impact?
- **Tractability:** does existing methodology, if applied, likely yield progress?

### Layer 4 — Question Generation
Use LLM to generate the actual research question at each high-scoring gap — in human-readable form, with the specific framing that makes it maximally tractable.

---

## Prototype / Demo

**What we build in one day:**

1. **Knowledge Graph** — Build a graph from a subset of arxiv papers (e.g., 10,000 papers across 5 fields). Visualize it: dense clusters are established fields, sparse regions are frontiers.

2. **Gap Detector** — Run structural gap detection (Type A + Type B) on the graph. Surface the top 20 candidate gaps.

3. **Question Generator** — For each gap, use an LLM to generate the specific research question that bridges it, with a one-paragraph explanation of why it's high-leverage.

4. **Demo Validation** — Show 2-3 historical examples: gaps that existed in the knowledge graph *before* a major discovery, proving the system would have found them in advance. (e.g., the gap between network topology and disease epidemiology before the 2000s.)

**Tech stack:** Python, networkx for graph, Semantic Scholar API for paper data, OpenAI/Claude API for question generation, d3.js or gephi for visualization.

---

## Moonshot Paper Outline

1. **The Problem Humanity Has Misunderstood**
   We treat scientific progress as a function of effort and funding. But the bottleneck is question selection. The questions we don't ask are more important than the questions we pursue — and we have no systematic way to find them.

2. **Why Existing Solutions Are Insufficient**
   - Literature review: finds what exists, not what's missing
   - Expert intuition: biased toward fields the expert already knows
   - Interdisciplinary initiatives: broad, unfocused, not systematic
   - AI research assistants: navigate the known map, don't generate the unknown

3. **The First-Principles Insight**
   Knowledge is a graph. Gaps in the graph are discoverable. High-leverage gaps — where a single answer unlocks many others — are computable. We can build a GPS for unexplored intellectual territory.

4. **Scientific Foundations**
   - Network science (graph theory, betweenness centrality, structural holes)
   - Scientometrics and bibliometrics
   - Philosophy of science (Kuhn's paradigm shifts, Lakatos research programs)
   - Information theory (where is the knowledge density lowest relative to potential?)

5. **Long-Term Implications**
   - Compress civilizational discovery timelines by targeting research effort at highest-leverage gaps
   - Democratize frontier research: a student anywhere can find genuinely important open questions, not just questions their institution happens to study
   - Identify questions that are structurally urgent before a crisis forces them (e.g., could have found the gap in pandemic preparedness + network science before 2020)

6. **The Future This Creates**
   Science directed not by funding cycles and institutional inertia, but by the actual structure of what we don't know.

---

## Judging Self-Assessment

| Criterion | Score (1-10) | Notes |
|-----------|-------------|-------|
| Originality & Zero-to-One | 8 | New paradigm for research tools; not a better search engine |
| Technical & Scientific Depth | 9 | Graph theory, scientometrics, information theory, strong technical core |
| Long-Term Vision & Impact | 9 | Compresses all of scientific progress |
| Feasibility & Execution Path | 9 | Fully buildable with existing APIs; demo is viscerally impressive |
| Prototype & Demonstration | 9 | Visual knowledge graph + historical validation is powerful and tangible |
