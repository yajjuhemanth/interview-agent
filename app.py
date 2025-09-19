import os
from flask import Flask, request, jsonify


def create_app() -> Flask:
    """Create and configure the Flask application.

    Routes:
        POST /generate: Accepts JSON with keys `job_title` and `job_description`.
                        Returns a JSON payload with placeholder interview questions.
    """
    app = Flask(__name__)

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

        # Placeholder questions (stub) — will be replaced by GPT integration later
        questions = [
            f"Can you summarize your experience relevant to the {job_title} role?",
            "Walk me through a challenging project you owned end-to-end and your impact.",
            f"Which tools, frameworks, or technologies are most important for a {job_title}, and how have you used them?",
            "How do you approach debugging complex issues and preventing regressions?",
            "What would your 30/60/90-day plan look like for this position?",
        ]

        return jsonify({
            "job_title": job_title,
            "job_description": job_description,
            "questions": questions,
            "source": "stub",
        })

    return app


if __name__ == "__main__":
    # Enable simple execution: `python app.py`
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
