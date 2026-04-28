# Planora: Autonomous Travel Planning Agent

<img width="1507" height="743" alt="Screenshot 2026-04-28 at 10 29 05 AM" src="https://github.com/user-attachments/assets/a059beec-551e-45d3-aec6-fce77832acd9" />

<img width="1508" height="824" alt="Screenshot 2026-04-28 at 10 29 17 AM" src="https://github.com/user-attachments/assets/f03d0f46-5fda-4390-a7ac-3a0f6de6fb17" />

<img width="1507" height="825" alt="Screenshot 2026-04-28 at 10 29 29 AM" src="https://github.com/user-attachments/assets/017ee496-9850-4f92-beff-953e72a1c794" />




Planora is a LangGraph-based autonomous travel planning system with:

- planner + specialized tool-calling agents,
- judge-driven refinement loops,
- feedback and memory persistence (SQLite),
- FastAPI backend with synchronous + SSE streaming planning APIs,
- Next.js + Framer Motion frontend for chat-style travel planning UI.

## Backend Quickstart

1. Create and activate virtual environment.
2. Install Python dependencies:
   - `pip install -e .[dev]`
3. Configure environment:
   - `cp .env.example .env`
   - set `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL`
4. Run tests:
   - `pytest`
5. (Optional) Run the graph once from the CLI and print JSON:
   - `python -m agent.run_graph --query "Plan a 4-day trip to Goa under ₹25,000"`
6. Run backend:
   - `uvicorn backend.main:app --reload`

### Backend API

- `POST /plan` - non-streaming planning run
- `POST /plan/stream` - SSE planning stream
- `POST /plan/retry` - explicit retry with strategy
- `POST /feedback` - thumbs feedback + optional comment
- `GET /feedback/{run_id}` - run with feedback history
- `GET /memory/{user_id}` - persisted preference profile

## Frontend Quickstart (Next.js)

1. Install Node dependencies:
   - `cd web && npm install`
2. Configure frontend env:
   - `cp .env.local.example .env.local`
   - ensure `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`
3. Run frontend:
   - `npm run dev`
4. Open:
   - `http://localhost:3000`

## Full Local Dev

Run backend and frontend in separate terminals:

- Terminal 1: `uvicorn backend.main:app --reload`
- Terminal 2: `cd web && npm run dev`

## Project Structure

- `agent/` - tests and `run_graph` CLI
- `agents/` - shared agent runtime helpers
- `graph/` - LangGraph orchestration
- `nodes/` - planner, specialist agents, judge, feedback nodes
- `tools/` - reusable tool layer
- `judge/` - evaluator implementation
- `memory/` - user preference memory store
- `feedback/` - planning run + feedback persistence
- `backend/` - FastAPI API layer
- `config/` - settings, LLM, database helpers
- `web/` - Next.js frontend with Framer Motion + Tailwind
