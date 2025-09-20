from __future__ import annotations

"""Agent module: encapsulates AI generation and persistence orchestration.

QuestionAgent is responsible for:
- Asking Gemini to generate Q&A pairs tailored to a job title/description
- Validating/cleaning the JSON response
- Calling a save callback to persist results
"""

import json
from typing import List, Tuple, Dict

from config import settings
from google import genai
from google.genai import types as genai_types


class AIUnavailableError(Exception):
    pass


class QuestionAgent:
    """Encapsulates the flow: generate questions -> validate -> save (via callback)."""

    def __init__(self, save_callback):
        self._save = save_callback

    def _generate_stub(self, job_title: str, job_description: str) -> List[str]:
        return [
            f"What most excites you about the {job_title} role?",
            "Tell us about a time you solved a complex problem end-to-end.",
            f"Which tools or frameworks are essential for a {job_title} and why?",
            "How do you ensure code quality and reliability under deadlines?",
            "Describe your 30/60/90-day plan for this role.",
        ]

    def generate_qa(self, job_title: str, job_description: str) -> Tuple[List[Dict[str, str]], str]:
        """Generate Q&A pairs using Gemini. Raises AIUnavailableError if unavailable."""
        if not settings.gemini_api_key:
            raise AIUnavailableError("Gemini API key not configured")

        try:
            client = genai.Client(api_key=settings.gemini_api_key)
            model = settings.gemini_model
            prompt = (
                "You generate concise, practical interview questions with strong, succinct answers.\n"
                "Generate 8-12 Q&A pairs tailored to the role.\n"
                "Return ONLY valid JSON with no code fences, no extra text.\n"
                "Schema: an array of objects with keys 'question' and 'answer'.\n"
                "Example: [{\"question\": \"...\", \"answer\": \"...\"}]\n\n"
                f"Job Title: {job_title}\n"
                f"Job Description: {job_description}\n"
            )
            contents = [
                genai_types.Content(role="user", parts=[genai_types.Part.from_text(text=prompt)])
            ]
            cfg = genai_types.GenerateContentConfig(
                response_modalities=["TEXT"],
                # Ask explicitly for JSON output if supported by the SDK version
                response_mime_type="application/json",
            )
            resp = client.models.generate_content(model=model, contents=contents, config=cfg)

            # Aggregate textual output robustly
            text_chunks: List[str] = []
            if getattr(resp, "text", None):
                text_chunks.append(resp.text)
            elif getattr(resp, "candidates", None):
                for cand in resp.candidates:
                    if getattr(cand, "content", None) and getattr(cand.content, "parts", None):
                        for part in cand.content.parts:
                            t = getattr(part, "text", None)
                            if t:
                                text_chunks.append(t)
            content = "\n".join([t for t in text_chunks if t]).strip()

            # Clean possible fences or prose
            cleaned = content.strip()
            if cleaned.startswith("```"):
                # strip first fenced block
                try:
                    start = cleaned.find("\n") + 1
                    end = cleaned.rfind("```")
                    if end > start > 0:
                        cleaned = cleaned[start:end].strip()
                except Exception:
                    pass

            import json as _json, re as _re
            try:
                qa = _json.loads(cleaned)
            except Exception:
                # Try to extract first JSON array substring
                match = _re.search(r"\[[\s\S]*\]", cleaned)
                if not match:
                    raise
                qa = _json.loads(match.group(0))
            if not isinstance(qa, list) or not qa:
                raise ValueError("empty or invalid JSON from Gemini")
            qa_ok = [x for x in qa if isinstance(x, dict) and "question" in x and "answer" in x]
            if not qa_ok:
                raise ValueError("no valid {question,answer} objects from Gemini")
            return qa_ok, "gemini"
        except AIUnavailableError:
            raise
        except Exception as e:
            raise AIUnavailableError(f"Gemini generation failed: {e}")

    def run(self, job_title: str, job_description: str, with_answers: bool = True) -> dict:
        job_title = (job_title or "").strip()
        job_description = (job_description or "").strip()
        if not job_title or not job_description:
            raise ValueError("job_title and job_description are required")

        if with_answers:
            qa, source = self.generate_qa(job_title, job_description)
            qs = [x.get("question", "").strip() for x in qa if isinstance(x, dict)]
            record = self._save(job_title, job_description, qs, qa)
        else:
            qs = self._generate_stub(job_title, job_description)
            source = "stub"
            record = self._save(job_title, job_description, qs, None)
        return {
            "id": record["id"],
            "job_title": job_title,
            "job_description": job_description,
            "questions": qs,
            "qa": record.get("qa") or (qa if with_answers else None),
            "created_at": record.get("created_at"),
            "source": source,
        }
