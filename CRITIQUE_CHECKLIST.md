# Anti-Discovery Engine — Priority Checklist

Derived from the full critique against the Moonshot Hackathon rubric
(Originality 35% · Technical Depth 25% · Vision 20% · Feasibility 10% · Demo 10%).
Deadline: **June 30, 2026, 5:00pm IST**. Ordered top-to-bottom by judging ROI.

> **STATUS: ✅ ALL ITEMS COMPLETE** — built by 4 parallel agents, merged to `main`, and
> verified live end-to-end. Test evidence (integrated server):
> demo graph 362 nodes · betweenness 78 distinct values, 0 components out of [0,1] ·
> evidence on 100/100 gaps · inversions + cascade (44 unlocked) working ·
> historical: engine_detected=True, "complex network ↔ epidemiology" leverage 96, 576-node 2005 graph ·
> persistence save/load roundtrip (memory fallback) · `npm run build` clean.
> Only caveat: full MongoDB Atlas test needs your real `MONGODB_URI` (fallback path verified).

---

## 🔴 P0 — Critical (broken / credibility-killing)

- [x] **1. Fix historical validation end-to-end** *(your single highest-weight asset; currently dead)*
  - [x] `core/historical_mode.py`: unpack the tuple — `papers, failed = await fetch_papers_for_fields(...)` (it now returns `(papers, failed_fields)` and crashes `build_graph`)
  - [x] Align the contract: backend `HistoricalValidationResult` (`models/gap.py`) must match the frontend type (`target_gap: {name,…}`, `engine_gap`, `engine_question`, `graph_export`, `validation_text`)
  - [x] Make the run actually populate `graph_export` so the split-screen renders
  - [x] Verify the real (non-mock) path works; flip `USE_MOCK` off in `useHistorical.ts`

- [x] **2. Remove fabricated numbers from the UI**
  - [x] `QuestionCard.tsx`: kill the "{community_reach × 10} related research areas" line (arbitrary multiplier shown as a finding)
  - [x] Fix score-component bars: `community_reach` is a raw int rendered as `width: 300%` / `3.00` while others are 0–1 — normalize or display separately

- [x] **3. Make the leverage score real (or honest)**
  - [x] Replace the degree-sum `betweenness_proxy` in `leverage_scorer.py` with real `nx.betweenness_centrality` deltas (graph is ~100 nodes — affordable)
  - [x] Ensure the displayed metric matches its stated definition

---

## 🟢 P1 — Highest-ROI new features

- [x] **4. Foreground historical validation in the demo** — make it the *opening*, not a toggle ("here's 2005; engine flags network-topology × epidemiology; closed by Pastor-Satorras & Vespignani")
- [x] **5. Type C — Inversion / "Antimatter Query"** *(best originality-per-hour, 35% weight)* — "We know X→Y; has Y→X ever been tested? 0 papers in 40 years." Build on existing graph; it's in the original feature list (#9) but never built
- [x] **6. Real evidence behind gaps** — OpenAlex returns paper IDs/titles/years/citations that are currently discarded. On gap click, show "N papers touch A, M touch B, 0 touch both." Makes Technical Depth (25%) defensible
- [x] **7. Cascade Map** — betweenness + reachability ripple animation; substantiates the "unlocks downstream discoveries" claim

---

## 🟡 P2 — Cut / shrink (stop spending time here)

- [x] **8. Cut ChatBot from the demo path** (`ChatBot.tsx` + `core/chat.py`) — zero originality, can fail live, dilutes thesis
- [x] **9. Cut/replace the "Discovery Story" templated paragraph** — boilerplate; replace with real paper evidence or remove
- [x] **10. Shrink Onboarding** to one screen — 0% judging weight
- [x] (Don't polish: regenerate button, papers-per-field slider — irrelevant)

---

## 🔵 P3 — Strategic overhauls & paper

- [x] **11. Depth over breadth** — pick 2–3 domains, build genuinely large graphs (or ship a big *precomputed* demo graph so live API limits don't bite on stage); nail 2–3 validated historical examples (deep learning 2012, CRISPR, network epidemiology)
- [x] **12. Reframe around proof** — "an engine that would have seen these discoveries coming" (stronger Vision story than a live graph of arbitrary fields)
- [x] **13. Write the Moonshot Paper** — ≥35% of the grade lives here; no draft exists yet. Problem → gaps → first-principles insight → scientific foundations → implications → envisioned future
- [x] **14. MongoDB Atlas persistence** — persist graphs/gaps → shareable permalinks + "live monitoring" angle; claims 2× $150 sponsor awards + finalist favorability

---

## Suggested 6-day execution order
1. Fix historical validation (P0-1) — half day, unblocks best asset
2. Type C inversion query (P1-5) — biggest originality ROI
3. Real papers in gap detail (P1-6) — makes depth defensible
4. Real betweenness scoring + kill fabricated numbers (P0-2, P0-3)
5. Cut ChatBot from demo path (P2-8)
6. Draft Moonshot Paper in parallel (P3-13)
7. MongoDB persistence if time (P3-14)
