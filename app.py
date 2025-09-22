"""Flask application entry point and minimal HTTP API.

Exposed routes:
- POST /agent : Generate interview Q&A via Gemini and persist.
- GET  /get   : List saved records (optionally filter by job_title).

Notes:
- A React (Vite) frontend lives under `frontend/` and calls the API above.
- Legacy dev-only routes (/ and /react templates, /generate stub) were removed
    to keep the app minimal and focused on the production flow.
"""

import json
from flask import Flask, request, jsonify
from typing import List

from config import settings
from database import init_db, get_session
from models import InterviewQuestion
from agent import QuestionAgent, AIUnavailableError


def create_app() -> Flask:
    """Create and configure the Flask application.

    Routes:
        POST /generate: Accepts JSON with keys `job_title` and `job_description`.
                        Returns a JSON payload with placeholder interview questions.
    """
    app = Flask(__name__)

    # Minimal API: only /agent and /get are exposed for the frontend

    # Helper for agent to persist and return compact result
    def _save_record(job_title: str, job_description: str, questions: List[str], qa: dict | List[dict] | None = None) -> dict:
        """Persist a record and return minimal info for response assembly.

        questions is a list of strings. qa can be either a list of {q,a} pairs or
        a dict keyed by levels {basic, intermediate, expert}. They are serialized as JSON
        for storage and de-serialized on reads.
        """
        questions_json = json.dumps(questions, ensure_ascii=False)
        qa_json = json.dumps(qa, ensure_ascii=False) if qa is not None else None
        with get_session() as session:
            rec = InterviewQuestion(
                job_title=job_title,
                job_description=job_description,
                questions=questions_json,
                qa=qa_json,
            )
            session.add(rec)
            session.flush()
            return {
                "id": rec.id,
                "created_at": rec.created_at.isoformat() if getattr(rec, "created_at", None) else None,
                "qa": qa,
            }

    @app.route("/agent", methods=["POST"])
    def agent_run():
        data = request.get_json(silent=True) or {}
        job_title = (data.get("job_title") or "").strip()
        job_description = (data.get("job_description") or "").strip()
        if not job_title or not job_description:
            return jsonify({"error": "'job_title' and 'job_description' are required."}), 400

        agent = QuestionAgent(save_callback=_save_record)
        try:
            result = agent.run(job_title, job_description)
            return jsonify(result), 201
        except AIUnavailableError as e:
            return jsonify({"error": str(e)}), 503
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Note: manual /save endpoint was removed as the frontend persists via /agent

    @app.route("/get", methods=["GET"])
    def get_saved():
        # Optional filters: job_title
        job_title = request.args.get("job_title")
        limit = min(int(request.args.get("limit", 50)), 200)

        with get_session() as session:
            query = session.query(InterviewQuestion)
            if job_title:
                query = query.filter(InterviewQuestion.job_title == job_title)
            rows = query.order_by(InterviewQuestion.id.desc()).limit(limit).all()

            items = []
            for r in rows:
                try:
                    q_list = json.loads(r.questions)
                except Exception:
                    q_list = []
                qa_list = None
                if r.qa:
                    try:
                        qa_list = json.loads(r.qa)
                    except Exception:
                        qa_list = None
                items.append({
                    "id": r.id,
                    "job_title": r.job_title,
                    "job_description": r.job_description,
                    "questions": q_list,
                    "qa": qa_list,
                    "created_at": r.created_at.isoformat() if getattr(r, "created_at", None) else None,
                })

            return jsonify(items)

    return app


if __name__ == "__main__":
    # Initialize DB and run app with configured port
    init_db()
    app = create_app()
    app.run(host="0.0.0.0", port=settings.port, debug=(settings.env == "development"))
