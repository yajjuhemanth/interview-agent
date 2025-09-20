"""Flask application entry point and HTTP routes.

Routes:
- GET  /         : minimal HTML form
- GET  /react    : simple React (CDN) UI for testing the agent
- POST /generate : dev-only stubbed questions (no AI call)
- POST /save     : persist questions and optional Q&A
- GET  /get      : list saved records
- POST /agent    : generate Q&A via Gemini and save in one shot
"""

import os
import json
from flask import Flask, request, jsonify, render_template
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

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/react")
    def react_ui():
        return render_template("react.html")

    @app.route("/generate", methods=["POST"])
    def generate():
        # Parse and validate incoming JSON
        data = request.get_json(silent=True) or {}
        job_title = (data.get("job_title") or "").strip()
        job_description = (data.get("job_description") or "").strip()

        if not job_title or not job_description:
            return (
                jsonify({
                    "error": "Both 'job_title' and 'job_description' are required.",
                    "hint": {
                        "expected": {
                            "job_title": "string",
                            "job_description": "string"
                        }
                    }
                }),
                400,
            )

        # Development-friendly stub: keep /generate simple and deterministic
        questions: List[str] = [
            f"Can you summarize your experience relevant to the {job_title} role?",
            "Walk me through a challenging project you owned end-to-end and your impact.",
            f"Which tools, frameworks, or technologies are most important for a {job_title}, and how have you used them?",
            "How do you approach debugging complex issues and preventing regressions?",
            "What would your 30/60/90-day plan look like for this position?",
        ]
        source = "stub"

        return jsonify({
            "job_title": job_title,
            "job_description": job_description,
            "questions": questions,
            "source": source,
        })

    # Helper for agent to persist and return compact result
    def _save_record(job_title: str, job_description: str, questions: List[str], qa: List[dict] | None = None) -> dict:
        """Persist a record and return minimal info for response assembly.

        questions and qa are Python structures; they are serialized as JSON strings
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
            result = agent.run(job_title, job_description, with_answers=True)
            return jsonify(result), 201
        except AIUnavailableError as e:
            return jsonify({"error": str(e)}), 503
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/save", methods=["POST"])
    def save():
        data = request.get_json(silent=True) or {}
        job_title = (data.get("job_title") or "").strip()
        job_description = (data.get("job_description") or "").strip()
        questions = data.get("questions")
        qa = data.get("qa")  # optional list of {question, answer}

        if not job_title or not job_description:
            return jsonify({"error": "'job_title' and 'job_description' are required."}), 400

        if not isinstance(questions, list) or not all(isinstance(q, str) for q in questions):
            return jsonify({
                "error": "'questions' must be a list of strings.",
                "hint": {"questions": ["Q1", "Q2", "..."]}
            }), 400

        # Serialize questions as JSON string for storage
        questions_json = json.dumps(questions, ensure_ascii=False)
        qa_json = None
        if qa is not None:
            if not isinstance(qa, list) or not all(isinstance(x, dict) and "question" in x and "answer" in x for x in qa):
                return jsonify({
                    "error": "'qa' must be a list of objects with 'question' and 'answer' keys.",
                    "hint": {"qa": [{"question": "...", "answer": "..."}]}
                }), 400
            qa_json = json.dumps(qa, ensure_ascii=False)

        with get_session() as session:
            record = InterviewQuestion(
                job_title=job_title,
                job_description=job_description,
                questions=questions_json,
                qa=qa_json,
            )
            session.add(record)
            session.flush()  # get autogenerated id

            return jsonify({
                "message": "Saved",
                "id": record.id,
            }), 201

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
