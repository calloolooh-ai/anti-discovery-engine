# Anti-Discovery Engine — Project Details

## What It Is
A tool that maps the topology of human scientific knowledge and finds the highest-leverage gaps — questions nobody is asking that would unlock multiple fields simultaneously. Not a search engine for what we know. A compass for what we don't.

## Hackathon
- **Name:** Moonshot Hackathon: Zero to One Ideas
- **Organizer:** Aethra (Devpost)
- **Date:** June 30, 2026
- **Submission deadline:** June 30, 2026 at 5:00pm IST

## Stack
- **Frontend:** React + TypeScript (Vite)
- **Backend:** Python (FastAPI)
- **Graph:** NetworkX
- **Data:** Semantic Scholar API (public, no auth required)
- **LLM:** Groq API (fast inference — llama-3.3-70b or mixtral for gap question generation)
- **Visualization:** D3.js or react-force-graph

## Deployment
- **Version control:** GitHub
- **Hosting:** Vercel (frontend) + likely Vercel serverless or Railway for backend
- **Dev environment:** localhost

## Folder Structure (planned)
```
anti-discovery-engine/
├── frontend/          # React app
├── backend/           # FastAPI server
├── data/              # cached paper data / graph exports
├── docs/              # moonshot paper drafts
├── PROJECT.md         # this file
├── HACKATHON.md       # hackathon requirements
├── IDEAS.md           # original project ideas
├── ADE_FEATURES.md    # feature list by priority
├── COMPARISON.md      # ADE vs FCP comparison
├── mvp_anti_discovery.md
└── mvp_first_contact.md
```

## Core Features (MVP — must ship)
1. Paper ingestion from Semantic Scholar API
2. Knowledge graph construction (NetworkX)
3. Interactive graph visualization
4. Structural gap detection (Type A + B)
5. LLM-powered gap question generation
6. Leverage scoring / ranking
7. Historical validation mode (killer demo moment)

## Key Demo Moment
Show the engine running on a paper corpus from ~2005 and surfacing the gap between **network topology and epidemiology** — a gap that was closed when network science transformed disease modeling. Proof the engine works in hindsight = proof it works for the future.
