from __future__ import annotations

from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """Profilo utente usato per il matching con le notizie."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class News(Base):
    """Notizia con testo ed embedding associato."""

    __tablename__ = "news"

    id: Mapped[int] = mapped_column(index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, primary_key=True)
    content_text: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    link: Mapped[str] = mapped_column(String(500), nullable=False, primary_key=True)
    source: Mapped[str] = mapped_column(String(500), nullable=False)
    language: Mapped[str] = mapped_column(String(500), nullable=False)
