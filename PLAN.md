# Anti-Discovery Engine — Full Implementation Plan

## Overview and Time Budget

The hackathon is a single day (June 30, 2026). Critical path: data pipeline working → graph visualizable → gaps detectable → LLM generating questions → historical mode. Assume 8 hours real build time. Agent A (backend) and Agent B (frontend) run in parallel from minute one sharing a frozen API contract.

> **LLM:** Using Groq API (key in `.env` as `GROQ_API_KEY`). Use `llama-3.3-70b-versatile` model. Install `groq` Python package.

---

## 1. Full Folder / File Structure

```
anti-discovery-engine/
├── backend/
│   ├── main.py                     # FastAPI app, route registration, CORS
│   ├── requirements.txt
│   ├── config.py                   # constants: rate limits, model names, field seeds
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes_graph.py         # /graph/build, /graph/status, /graph/export
│   │   ├── routes_gaps.py          # /gaps/detect, /gaps/score, /gaps/questions
│   │   └── routes_historical.py    # /historical/run, /historical/status
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ingestion.py            # Semantic Scholar API client + rate limiter
│   │   ├── graph_builder.py        # NetworkX graph construction from papers
│   │   ├── gap_detector.py         # Type A structural gaps + Type B cross-domain
│   │   ├── leverage_scorer.py      # gap ranking algorithm
│   │   ├── question_generator.py   # Groq API calls for question generation
│   │   └── historical_mode.py      # pre-2005 corpus filter + gap replay
│   ├── models/
│   │   ├── __init__.py
│   │   ├── paper.py                # Pydantic Paper, Author, Concept models
│   │   ├── graph.py                # Pydantic GraphNode, GraphEdge, GraphExport
│   │   └── gap.py                  # Pydantic Gap, LeverageScore, ResearchQuestion
│   └── data/
│       ├── cache/                  # JSON cache of Semantic Scholar responses
│       ├── graphs/                 # Serialized NetworkX graphs
│       └── seeds/
│           ├── modern_fields.json
│           └── historical_2005.json
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       │   ├── client.ts
│       │   ├── graph.ts
│       │   ├── gaps.ts
│       │   └── historical.ts
│       ├── types/
│       │   └── index.ts            # shared TypeScript types — frozen at T+30min
│       ├── components/
│       │   ├── GraphCanvas.tsx     # react-force-graph-2d wrapper
│       │   ├── GapPanel.tsx        # right sidebar: gap list + detail
│       │   ├── QuestionCard.tsx    # single gap: question + leverage + analogy
│       │   ├── FieldSelector.tsx   # left sidebar: domain checkboxes + build button
│       │   ├── ModeToggle.tsx      # "Live" vs "Historical (2005)" toggle
│       │   ├── StatusBar.tsx       # build progress indicator
│       │   ├── TopGapsLeaderboard.tsx
│       │   └── LoadingOverlay.tsx
│       ├── hooks/
│       │   ├── useGraphData.ts     # poll /graph/build → status → export
│       │   ├── useGaps.ts
│       │   └── useHistorical.ts
│       └── styles/
│           ├── globals.css
│           └── theme.ts
├── data/
│   ├── example_graph.json          # pre-built graph fallback for demo
│   └── historical_gaps.json        # known historical gaps for validation
├── docs/
│   └── moonshot_paper.md
├── .env                            # GROQ_API_KEY (git-ignored)
├── .gitignore
├── PROJECT.md
├── HACKATHON.md
└── README.md
```

---

## 2. API Contract (Frozen)

```typescript
type FieldOfStudy =
  | "Computer Science" | "Mathematics" | "Physics"
  | "Biology" | "Medicine" | "Economics" | "Chemistry" | "Engineering";

interface BuildRequest {
  fields: FieldOfStudy[];
  max_papers_per_field: number;   // default 150
  year_filter?: number;           // null = all; 2005 = historical
}

interface JobStatus {
  job_id: string;
  stage: "fetching" | "building" | "detecting_gaps" | "scoring" | "complete" | "error";
  progress: number;               // 0–100
  eta_seconds: number | null;
  error?: string;
}

interface GraphNode {
  id: string;
  label: string;
  field: string[];
  paper_count: number;
  community_id: number;
  x?: number;
  y?: number;
}

interface GraphEdge {
  source: string;
  target: string;
  weight: number;
  is_gap: boolean;
  gap_id?: string;
  gap_type?: "structural" | "cross_domain";
}

interface GraphExport {
  job_id: string;
  node_count: number;
  edge_count: number;
  gap_count: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
  communities: Record<number, string>;
  built_at: string;
}

interface Gap {
  gap_id: string;
  type: "structural" | "cross_domain";
  node_a: string;
  node_b: string;
  bridging_concepts: string[];
  field_a: string;
  field_b: string;
  leverage_score: number;         // 0–100
  score_components: {
    betweenness_delta: number;
    community_reach: number;
    paper_velocity: number;
    cross_domain_bonus: number;
  };
  question?: ResearchQuestion;
}

interface ResearchQuestion {
  gap_id: string;
  question: string;
  why_matters: string;
  historical_analogy: string;
  model_used: string;
  generated_at: string;
}

interface QuestionRequest {
  gap_ids: string[];
  use_high_quality: boolean;
}

interface HistoricalValidationResult {
  job_id: string;
  target_gap: {
    name: string;
    description: string;
    actual_discovery_year: number;
    key_papers: string[];
  };
  engine_detected: boolean;
  engine_gap: Gap | null;
  engine_question: ResearchQuestion | null;
  graph_export: GraphExport;
  validation_text: string;
}
```

### Endpoints

| Method | Path | Request | Response |
|--------|------|---------|----------|
| GET | `/health` | — | `{status: "ok"}` |
| POST | `/graph/build` | `BuildRequest` | `{job_id: string}` |
| GET | `/graph/status/{job_id}` | — | `JobStatus` |
| GET | `/graph/export/{job_id}` | — | `GraphExport` |
| GET | `/gaps/detect/{job_id}` | — | `Gap[]` |
| GET | `/gaps/score/{job_id}` | — | `Gap[]` sorted by leverage desc |
| POST | `/gaps/questions` | `QuestionRequest` | `ResearchQuestion[]` |
| POST | `/historical/run` | `{}` | `{job_id: string}` |
| GET | `/historical/result/{job_id}` | — | `HistoricalValidationResult` |

CORS: allow `http://localhost:5173` in dev.

---

## 3. Parallel Workstreams

### Agent A — Backend
1. `backend/main.py` — FastAPI + CORS
2. `backend/config.py` — constants
3. `backend/models/` — all Pydantic models
4. `backend/core/ingestion.py` — Semantic Scholar client + cache
5. `backend/core/graph_builder.py` — NetworkX graph
6. `backend/api/routes_graph.py` — build/status/export
7. `backend/core/gap_detector.py` — Type A then B
8. `backend/core/leverage_scorer.py`
9. `backend/api/routes_gaps.py`
10. `backend/core/question_generator.py` (Groq)
11. `backend/core/historical_mode.py` + routes

### Agent B — Frontend
1. `frontend/src/types/index.ts` — TS types
2. `frontend/src/api/mockData.ts` — mock GraphExport
3. `frontend/src/api/client.ts` — fetch wrapper
4. `frontend/src/components/GraphCanvas.tsx` — react-force-graph-2d + mock
5. `frontend/src/hooks/useGraphData.ts`
6. `frontend/src/components/FieldSelector.tsx` + `ModeToggle.tsx`
7. `frontend/src/components/GapPanel.tsx` + `QuestionCard.tsx`
8. `frontend/src/components/TopGapsLeaderboard.tsx`
9. `frontend/src/components/StatusBar.tsx` + `LoadingOverlay.tsx`
10. Wire real API (after backend /graph/export is live)
11. Historical mode UI

---

## 4. Critical Path Timeline

```
T+0:00  Both agents start — models + types (contract frozen at T+30min)
T+0:30  Agent B: GraphCanvas renders mock graph
        Agent A: Semantic Scholar ingestion working
T+1:30  Agent B: full visual shell done
        Agent A: /graph/export endpoint live
T+2:00  INTEGRATION 1 — Agent B switches from mock to real graph
T+2:30  Agent A: /gaps/score live
        INTEGRATION 2 — GapPanel shows real gaps
T+3:00  Agent A: /gaps/questions (Groq) live
        INTEGRATION 3 — questions flow end-to-end
T+4:15  Agent A: /historical/* live
        INTEGRATION 4 — full historical demo works
T+5:15  Bug fixing, polish, demo rehearsal
T+6:30  Deploy: Vercel (frontend) + Railway (backend)
```

---

## 5. Gotchas

- **Semantic Scholar rate limit:** 100 req/5min on public API. Use token-bucket rate limiter, cache all responses to `backend/data/cache/`.
- **Graph size:** Prune nodes appearing in <2 papers. Target 500–2000 nodes for D3 performance.
- **react-force-graph-2d:** Use canvas renderer (default). Set `warmupTicks=100`. Disable physics after stabilization.
- **Job state:** In-memory dict only — no Redis/Celery. Fine for hackathon.
- **Historical fallback:** Hard-code the network science × epidemiology gap in `data/historical_gaps.json` as a safety net if the corpus doesn't surface it organically.
- **Demo fallback:** Commit `data/example_graph.json` as pre-built graph. Add hidden "load example" button in UI.
- **Groq model:** Use `llama-3.3-70b-versatile`. Install `groq` package. Key from env var `GROQ_API_KEY`.
