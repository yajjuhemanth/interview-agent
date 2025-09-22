# Interview Agent (minimal)

Minimal, production-focused app to generate interview Q&A for a role.

Components:
- Backend: Flask + SQLAlchemy (MySQL via PyMySQL or SQLite fallback) + Gemini (google-genai)
- Frontend: Vite + React (TypeScript)

## API (minimal)
- POST `/agent` — Generate Q&A via Gemini and save in DB. Body: `{ job_title, job_description }`
- GET  `/get` — List saved records (optional `?job_title=...&limit=50`)

Legacy dev routes and artifacts (/generate, /save, Jinja templates, Postman/OpenAPI, smoke tests) were removed to keep the app lean.

## Setup
1) Python deps
- Create a virtual env and install:
	- requirements.txt
2) Environment
- .env supports: `DATABASE_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `PORT`
- Examples:
	- MySQL: `mysql+pymysql://user:password@localhost:3306/interview_agent`
	- SQLite: `sqlite:///interview_agent.db` (default)

## Run (development)
Backend:
- Start Flask: run `python app.py` (uses PORT, default 5000)

Frontend:
- In `frontend/`: install once with `npm install`
- Start dev server: `npm run dev` (proxies API to http://localhost:5000)

Open the Vite URL printed in the terminal (default http://localhost:5173) and use the UI.

## Notes
- If `GEMINI_API_KEY` is not set or Gemini fails, backend returns 503 for `/agent`.
- DB schema is created automatically; a safe migration ensures an optional `qa` column exists.

## Folder overview
- app.py, agent.py, config.py, database.py, models.py — core backend
- frontend/ — Vite + React UI (only uses `/agent` and `/get`)
- requirements.txt — Python dependencies
