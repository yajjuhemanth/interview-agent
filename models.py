from __future__ import annotations

"""SQLAlchemy ORM models for the application."""

from datetime import datetime
from typing import List

from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    # Store questions as JSON string; API will parse/format as list[str]
    questions: Mapped[str] = mapped_column(Text, nullable=False)
    # Optional: store Q&A pairs as JSON string: [{"question": str, "answer": str}, ...]
    qa: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def to_dict(self) -> dict:
        """Return a minimal dictionary representation (without deserializing JSON fields)."""
        return {
            "id": self.id,
            "job_title": self.job_title,
            "job_description": self.job_description,
            "questions": self.questions,  # caller may json.loads
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
