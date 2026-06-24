# Anti-Discovery Engine — Priority Checklist

Derived from the full critique against the Moonshot Hackathon rubric
(Originality 35% · Technical Depth 25% · Vision 20% · Feasibility 10% · Demo 10%).
Deadline: **June 30, 2026, 5:00pm IST**. Ordered top-to-bottom by judging ROI.

---

## 🔴 P0 — Critical (broken / credibility-killing)

- [ ] **1. Fix historical validation end-to-end** *(your single highest-weight asset; currently dead)*
  - [ ] `core/historical_mode.py`: unpack the tuple — `papers, failed = await fetch_papers_for_fields(...)` (it now returns `(papers, failed_fields)` and crashes `build_graph`)
  - [ ] Align the contract: backend `HistoricalValidationResult` (`models/gap.py`) must match the frontend type (`target_gap: {name,…}`, `engine_gap`, `engine_question`, `graph_export`, `validation_text`)
  - [ ] Make the run actually populate `graph_export` so the split-screen renders
  - [ ] Verify the real (non-mock) path works; flip `USE_MOCK` off in `useHistorical.ts`

- [ ] **2. Remove fabricated numbers from the UI**
  - [ ] `QuestionCard.tsx`: kill the "{community_reach × 10} related research areas" line (arbitrary multiplier shown as a finding)
  - [ ] Fix score-component bars: `community_reach` is a raw int rendered as `width: 300%` / `3.00` while others are 0–1 — normalize or display separately

- [ ] **3. Make the leverage score real (or honest)**
  - [ ] Replace the degree-sum `betweenness_proxy` in `leverage_scorer.py` with real `nx.betweenness_centrality` deltas (graph is ~100 nodes — affordable)
  - [ ] Ensure the displayed metric matches its stated definition

---

## 🟢 P1 — Highest-ROI new features

- [ ] **4. Foreground historical validation in the demo** — make it the *opening*, not a toggle ("here's 2005; engine flags network-topology × epidemiology; closed by Pastor-Satorras & Vespignani")
- [ ] **5. Type C — Inversion / "Antimatter Query"** *(best originality-per-hour, 35% weight)* — "We know X→Y; has Y→X ever been tested? 0 papers in 40 years." Build on existing graph; it's in the original feature list (#9) but never built
- [ ] **6. Real evidence behind gaps** — OpenAlex returns paper IDs/titles/years/citations that are currently discarded. On gap click, show "N papers touch A, M touch B, 0 touch both." Makes Technical Depth (25%) defensible
- [ ] **7. Cascade Map** — betweenness + reachability ripple animation; substantiates the "unlocks downstream discoveries" claim

---

## 🟡 P2 — Cut / shrink (stop spending time here)

- [ ] **8. Cut ChatBot from the demo path** (`ChatBot.tsx` + `core/chat.py`) — zero originality, can fail live, dilutes thesis
- [ ] **9. Cut/replace the "Discovery Story" templated paragraph** — boilerplate; replace with real paper evidence or remove
- [ ] **10. Shrink Onboarding** to one screen — 0% judging weight
- [ ] (Don't polish: regenerate button, papers-per-field slider — irrelevant)

---

## 🔵 P3 — Strategic overhauls & paper

- [ ] **11. Depth over breadth** — pick 2–3 domains, build genuinely large graphs (or ship a big *precomputed* demo graph so live API limits don't bite on stage); nail 2–3 validated historical examples (deep learning 2012, CRISPR, network epidemiology)
- [ ] **12. Reframe around proof** — "an engine that would have seen these discoveries coming" (stronger Vision story than a live graph of arbitrary fields)
- [ ] **13. Write the Moonshot Paper** — ≥35% of the grade lives here; no draft exists yet. Problem → gaps → first-principles insight → scientific foundations → implications → envisioned future
- [ ] **14. MongoDB Atlas persistence** — persist graphs/gaps → shareable permalinks + "live monitoring" angle; claims 2× $150 sponsor awards + finalist favorability

---

## Suggested 6-day execution order
1. Fix historical validation (P0-1) — half day, unblocks best asset
2. Type C inversion query (P1-5) — biggest originality ROI
3. Real papers in gap detail (P1-6) — makes depth defensible
4. Real betweenness scoring + kill fabricated numbers (P0-2, P0-3)
5. Cut ChatBot from demo path (P2-8)
6. Draft Moonshot Paper in parallel (P3-13)
7. MongoDB persistence if time (P3-14)
