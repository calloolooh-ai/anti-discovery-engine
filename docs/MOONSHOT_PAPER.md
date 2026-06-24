# The Anti-Discovery Engine
### A compass for the questions science has not yet thought to ask

**Moonshot Hackathon — Zero to One Ideas**
A telescope pointed not at what we know, but at the shape of what we don't.

---

## 1. The Problem: Science optimizes answers, not questions

Every institution humanity has built for knowledge — universities, journals,
funding agencies, citation indices — is an apparatus for *answering* questions.
None of them is an apparatus for *choosing which questions to ask*. That choice
is left to individual intuition, disciplinary fashion, and the gravitational pull
of whatever is already well-funded.

This produces a systematic failure mode that is invisible because it has no
metric: **the highest-leverage questions are the ones nobody is positioned to
ask.** A question that sits between two fields belongs to neither department,
appears in neither literature, and is legible to neither set of reviewers. It is
not rejected — it is never proposed. The scientific record is therefore not a map
of what is true; it is a map of what was *askable* given the social structure of
science at the time.

The consequences are measurable in hindsight. The mathematics of scale-free
networks (Barabási–Albert, 1999) and the dynamics of epidemics (decades of
compartmental SIR modelling) coexisted for years before anyone connected them.
When Pastor-Satorras and Vespignani finally did in 2001, they overturned the
foundational assumption of epidemiology — that every disease has a finite
epidemic threshold. The connection required no new data and no new instrument.
It required only that someone *ask*. The gap was real, structural, and
detectable for years before it was closed.

If that gap was detectable in advance, others are too. **The cost of the
questions we fail to ask is the central, unmeasured tax on scientific progress.**

---

## 2. Gaps in Existing Solutions

The tools we already have all look in the wrong direction:

- **Search engines (Google Scholar, Semantic Scholar)** retrieve what exists.
  They are exquisitely optimized for finding answers and structurally incapable
  of surfacing absences. You cannot search for a paper that was never written.
- **Recommendation systems** amplify the existing citation gradient. They push
  you *toward* dense regions of the literature — the opposite of where the
  unexplored gaps are.
- **Literature-based discovery (Swanson's ABC model, 1986)** is the closest
  prior art: it finds implicit A–C links via shared intermediate B terms. But it
  operates on term co-occurrence in titles, produces enormous unranked candidate
  lists, and has no notion of *leverage* — which of the millions of latent links
  actually matters.
- **Large language models** interpolate fluently within their training
  distribution. They are, by construction, a compression of what has already been
  said. Asking an LLM for an unexplored question yields plausible-sounding
  recombination, not a structurally grounded absence.

The common failure: every one of these tools models **presence**. None models
**structured absence** — and absence, ranked by leverage, is the entire game.

---

## 3. First-Principles Insight

Three observations, each almost trivial alone, compound into the engine:

**(i) Knowledge has a topology.** Scientific concepts and their relationships
form a graph. This is not a metaphor — it is directly observable. Concepts that
are studied together co-occur in papers; the strength of co-occurrence is an edge
weight. The graph has communities (fields), hubs (foundational concepts), and —
crucially — *holes*.

**(ii) A gap is a graph-theoretic object, not a vibe.** An unexplored question is
a structural signature you can compute:
  - **Structural gap (Type A):** two concepts each strongly connected to a shared
    neighbor, but never directly connected to each other. The graph "expects" an
    edge that the literature has never drawn.
  - **Cross-domain gap (Type B):** two communities from different fields with high
    concept-vector similarity but zero connecting edges — methodological
    cousins that have never met.
  - **Inversion gap (Type C):** a studied directional claim *X → Y* whose logical
    inverse *Y → X* has never been tested. The asymmetry of attention is itself a
    detectable absence.

**(iii) Not all gaps are equal — leverage is computable.** The value of closing a
gap is how much of the rest of the graph it unlocks. This is *betweenness
centrality*: a candidate edge that would lie on a large fraction of shortest paths
between otherwise-distant regions is a high-leverage bridge. We compute the
betweenness contribution of the anchor nodes, the number of distinct communities
the gap would connect, and the citation mass behind each endpoint, and combine
them into a single leverage score.

The synthesis: **if knowledge is a graph, and gaps are structural features of
that graph, and leverage is a centrality measure on that graph, then the
selection of high-value research questions — historically an act of irreducible
genius — becomes a computation.**

---

## 4. Scientific Foundations

The engine stands on established, load-bearing results:

- **Network science** — Barabási–Albert preferential attachment; Watts–Strogatz
  small-world topology; Girvan–Newman / greedy-modularity community detection.
  These give us a principled decomposition of the knowledge graph into fields and
  a basis for detecting where fields *should* connect but don't.
- **Graph theory** — betweenness centrality (Freeman, 1977) as the formal measure
  of a node or edge's brokerage power. A high-leverage gap is, precisely, a
  high-potential-betweenness missing edge.
- **Scientometrics** — citation distributions are heavy-tailed; concept
  co-occurrence is a validated proxy for intellectual relatedness. We build on
  OpenAlex, an open index of ~250M works, so the graph reflects the real
  literature rather than a toy corpus.
- **Literature-based discovery** — Swanson's Raynaud's–fish-oil result (1986)
  is the existence proof that latent, computable connections in the literature
  correspond to real, confirmable discoveries.

### How the engine works (implemented pipeline)

```
OpenAlex query (per field)
        │  concepts, fields, citations, abstracts
        ▼
Concept co-occurrence graph  (NetworkX, weighted, community-labelled)
        │
        ├─► Type A  structural-gap detector   (distance-2, no direct edge)
        ├─► Type B  cross-domain detector      (similar communities, zero edges)
        └─► Type C  inversion detector         (X→Y present, Y→X absent)
        │
        ▼
Leverage scorer  (betweenness contribution + community reach + citation mass)
        │
        ▼
Ranked gaps ─► LLM question generator ─► concrete research question + rationale
        │
        ▼
Historical validation:  run on a pre-discovery corpus, confirm the engine
                        flags a gap that was later closed by a real breakthrough.
```

The **historical validation mode** is the engine's own falsification test. We
restrict the corpus to papers published before a known discovery, run the full
pipeline, and check whether the engine surfaces the gap that the discovery later
closed. Proof in hindsight is proof of the mechanism: if the engine can rediscover
the network-topology × epidemiology gap from 2005 literature, it is finding real
structure, not telling a story after the fact.

---

## 5. Implications

If question-selection is computable, the consequences cascade:

- **Research becomes steerable at the portfolio level.** A funding agency could
  see, before writing a single call for proposals, which high-leverage gaps no
  institution is positioned to close — and fund precisely those.
- **Interdisciplinarity stops being an accident.** The gaps that fall between
  departments are exactly the ones the engine ranks highest, because they have the
  greatest betweenness. The structure that hides them from humans is the structure
  that makes them visible to the engine.
- **Discovery gets a leading indicator.** Today we measure science by lagging
  metrics — citations, h-indices, papers published. A live gap monitor turns the
  literature into a seismograph: you can watch a gap narrow from "0 papers" to "2
  papers" and see a field being born in real time.
- **The cost of the unasked question becomes legible.** For the first time there
  is a metric for the questions we are failing to ask — and what you can measure,
  you can begin to fix.

---

## 6. The Envisioned Future

The single-day prototype maps a few fields and rediscovers gaps we can verify in
hindsight. That is the seed, not the tree.

**Near term** — a complete map of one discipline's frontier, with every
high-leverage gap ranked, a generated research question attached to each, and a
public "live monitoring" page that updates as new preprints arrive.

**Medium term** — the cross-domain map of *all* of science, refreshed daily.
Every researcher sees not only their own field's frontier but the bridges from
their expertise to the questions in adjacent fields that only they are positioned
to answer. The engine becomes the default first stop before writing any grant.

**Long term** — an *anti-discovery layer* over civilizational knowledge: a
standing inventory of the most valuable questions humanity has not yet asked,
continuously re-ranked as the graph evolves, with discoveries falling out of it
the way search results fall out of an index today.

We have spent four hundred years building ever-better machines for answering
questions. We have never built a machine for choosing them. The Anti-Discovery
Engine is the first attempt — a compass that points not at the territory we have
mapped, but at the most valuable unmapped direction, and says: *go here. Nobody
has, and they should.*

---

*Prototype: React + FastAPI + NetworkX over the OpenAlex corpus, with LLM-generated
research questions and a historical-validation harness. Source and demo accompany
this paper.*
