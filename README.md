# Interview Question Generator (Agent-based App)

A simple Flask API that generates interview questions for a given job title and description, with optional GPT integration and MySQL persistence.

## Features
- POST `/generate` — Generate interview questions (GPT-ready; stubbed by default)
- POST `/save` — Save generated questions
- GET  `/get` — Fetch saved questions

## Tech
- Python 3.10+
- Flask
- SQLAlchemy (MySQL via PyMySQL; SQLite fallback)
- Gemini API

## Setup
1. Clone and open the folder in VS Code.
2. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Configure environment variables:

```powershell
Copy-Item .env.example .env
# Edit .env and set DATABASE_URL and GEMINI_API_KEY
```

- MySQL example: `mysql+pymysql://user:password@localhost:3306/interview_agent`
- SQLite fallback: `sqlite:///interview_agent.db`

## Run
```powershell
python app.py
```
Server runs on `http://localhost:5000` (PORT env can override).

## Quick test
```powershell
$body = @{ job_title = "Software Engineer"; job_description = "Builds APIs" } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/generate" -Method Post -Body $body -ContentType "application/json"
```

## Notes
- `/generate` returns stubbed questions (for development).
- `/agent` uses Gemini to generate Q&A pairs (requires `GEMINI_API_KEY`).
- Use Postman if you prefer a UI for testing.

## API docs
- OpenAPI: `docs/openapi.yaml`
- Import the Postman collection: `postman/InterviewAgent.postman_collection.json`

## Smoke test (optional)
Start the server, then run:

```powershell
python scripts/smoke_test.py
```

It will call `/generate`, `/save`, `/get` and exit with success if all good.

## Troubleshooting
- MySQL auth errors: ensure your DATABASE_URL is correct and URL-encodes special characters (e.g., `@` => `%40`).
- MySQL user permissions: grant `ALL PRIVILEGES` on `interview_db.*` to your app user.
- SSL/auth plugins: local dev may require `cryptography` or using `mysql_native_password` for your user.

## React test UI (optional)
You can also try a minimal React page (no build needed):

1. Start the server: `python app.py`
2. Open your browser to `http://localhost:5000/react`
3. Enter a job title/description and submit
	- If `GEMINI_API_KEY` is configured, Q&A will be generated and saved
	- If not, you’ll see a handled error (503) and no answers
