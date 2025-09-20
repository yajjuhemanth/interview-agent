"""Application configuration loading.

Loads environment variables from `.env` when present and exposes a typed
`Settings` object used across the app (Flask port/env, DB URL, Gemini model/key).
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load variables from .env if present
load_dotenv()


def _default_database_url() -> str:
    # Fallback to SQLite file in project root
    return "sqlite:///interview_agent.db"


@dataclass(frozen=True)
class Settings:
    # Flask
    port: int = int(os.getenv("PORT", "5000"))
    env: str = os.getenv("FLASK_ENV", "development")

    # Database
    database_url: str = os.getenv("DATABASE_URL") or _default_database_url()

    # Gemini
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY") or None
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")


settings = Settings()
