# Anti-Discovery Engine

Hackathon project (Moonshot Hackathon — deadline June 30, 2026, 5:00pm IST).
See `HACKATHON.md` for the rubric and `docs/MOONSHOT_PAPER.md` for the writeup.

## Git / commit policy — IMPORTANT

All commits in this repo must be attributed **only to the user**, so the GitHub
contributor graph shows the user alone (no AI co-author).

- **Do NOT add a `Co-Authored-By: Claude` trailer** to commits.
- **Do NOT add the "Generated with Claude Code" line** to commits or PR bodies.
- Author and committer must be the user's GitHub identity:
  - name: `calloolooh-ai`
  - email: `237413272+calloolooh-ai@users.noreply.github.com`
- These are already set as the repo-local `git config user.name` / `user.email`.

## Run locally

- Backend: `cd backend && python3.13 -m uvicorn main:app --port 8000`
  (use `python3.13` — system `python3` is 3.14 and can't build pydantic-core)
- Frontend: `cd frontend && npm run dev` (Vite on :5173)
