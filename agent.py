from __future__ import annotations

"""Agent module: encapsulates AI generation and persistence orchestration.

QuestionAgent responsibilities:
- Ask Gemini to generate Q&A grouped by difficulty levels: basic, intermediate, expert
- Validate/clean the JSON response
- Persist via provided save callback
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

    def generate_qa(self, job_title: str, job_description: str) -> Tuple[Dict[str, List[Dict[str, str]]], str]:
        """Generate Q&A pairs in three levels using Gemini.

        Returns a tuple (qa_by_level, source) where qa_by_level is a dict with keys:
        {"basic": [...], "intermediate": [...], "expert": [...]} and each value is a
        list of {question, answer} objects.
        Raises AIUnavailableError if the model is not available or response invalid.
        """
        if not settings.gemini_api_key:
            raise AIUnavailableError("Gemini API key not configured")

        try:
            client = genai.Client(api_key=settings.gemini_api_key)
            model = settings.gemini_model
            prompt = (
                "You are an expert interviewer and technical writer.\n"
                "Task: Generate interview Q&A pairs tailored to the role below, grouped by difficulty level.\n"
                "Levels: 'basic' (fundamentals), 'intermediate' (solid practical skills), 'expert' (deep, systems-level, or advanced).\n"
                "Answers must be concise (2-4 sentences), precise, practical, and role-specific; no fluff, no markdown.\n"
                "Output: ONLY valid JSON (no prose, no code fences).\n"
                "Schema: {\n  \"basic\": [{\"question\": str, \"answer\": str}, ... 5-8],\n  \"intermediate\": [{...} 6-10],\n  \"expert\": [{...} 6-10]\n}\n\n"
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
                # If model ignored schema and returned an array, capture it; otherwise try object
                match_obj = _re.search(r"\{[\s\S]*\}", cleaned)
                match_arr = _re.search(r"\[[\s\S]*\]", cleaned)
                if match_obj:
                    qa = _json.loads(match_obj.group(0))
                elif match_arr:
                    qa = {"basic": _json.loads(match_arr.group(0))}
                else:
                    raise

            # Normalize to dict of levels
            levels = {"basic": [], "intermediate": [], "expert": []}
            if isinstance(qa, dict):
                for k in list(levels.keys()):
                    v = qa.get(k)
                    if isinstance(v, list):
                        levels[k] = [x for x in v if isinstance(x, dict) and "question" in x and "answer" in x]
            elif isinstance(qa, list):
                levels["basic"] = [x for x in qa if isinstance(x, dict) and "question" in x and "answer" in x]
            else:
                raise ValueError("invalid JSON shape from Gemini")

            # Ensure at least one level is non-empty
            if not any(levels.values()):
                raise ValueError("no valid {question,answer} objects from Gemini")
            return levels, "gemini"
        except AIUnavailableError:
            raise
        except Exception as e:
            raise AIUnavailableError(f"Gemini generation failed: {e}")

    def run(self, job_title: str, job_description: str) -> dict:
        job_title = (job_title or "").strip()
        job_description = (job_description or "").strip()
        if not job_title or not job_description:
            raise ValueError("job_title and job_description are required")

        qa_by_level, source = self.generate_qa(job_title, job_description)
        # Flatten questions across all levels for simple storage and compatibility
        flat_qs: List[str] = []
        for arr in qa_by_level.values():
            for x in arr:
                q = (x.get("question") or "").strip()
                if q:
                    flat_qs.append(q)
        record = self._save(job_title, job_description, flat_qs, qa_by_level)
        return {
            "id": record["id"],
            "job_title": job_title,
            "job_description": job_description,
            "questions": flat_qs,
            "qa": record.get("qa") or qa_by_level,
            "created_at": record.get("created_at"),
            "source": source,
        }
