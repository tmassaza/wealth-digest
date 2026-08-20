from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import News, User


class RecommendationService:
    """Servizio che ordina le notizie in base alla similarità vettoriale."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def top_news_for_user(self, user_id: int, top_n: int = 5) -> list[News]:
        """Restituisce le notizie più vicine al profilo dell'utente."""

        user = self.db.get(User, user_id)
        if user is None or user.embedding is None:
            return []

        stmt = (
            select(News)
            .where(News.embedding.is_not(None))
            .order_by(News.embedding.cosine_distance(user.embedding))
            .limit(top_n)
        )
        return list(self.db.execute(stmt).scalars().all())
