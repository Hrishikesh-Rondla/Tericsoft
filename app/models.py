"""
SQLAlchemy 2.x model for the leads table.
Engine and session factory are defined here so every other module
imports from one place – no circular imports, no magic.
"""

import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

DATABASE_URL = "sqlite:///./leads.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite + threads
)


class Base(DeclarativeBase):
    pass


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_name: Mapped[str] = mapped_column(String(100))
    contact_email: Mapped[str] = mapped_column(String(254))
    requirement_text: Mapped[str] = mapped_column(Text)
    retrieved_context: Mapped[str] = mapped_column(Text)   # JSON string
    ai_analysis: Mapped[str] = mapped_column(Text)         # JSON string
    lead_score: Mapped[int] = mapped_column(Integer)
    priority: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="new")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


def create_tables() -> None:
    """Create all tables if they don't already exist. Called once on startup."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """
    Return a plain Session object.
    Callers are responsible for closing it (use 'with' or try/finally).
    We avoid a generator-based dependency here to keep the flow obvious.
    """
    return Session(engine)
