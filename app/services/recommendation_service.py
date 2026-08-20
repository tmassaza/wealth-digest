from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import News, User


@dataclass(slots=True)
class ScoredNews:
    news: News
    score: float


class RecommendationService:
    """Servizio che ordina le notizie in base alla similarità vettoriale."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def top_news_for_user(self, user_id: int, top_n: int = 5) -> list[ScoredNews]:
        """Restituisce le notizie più vicine al profilo dell'utente con score di similarità."""

        user = self.db.get(User, user_id)
        if user is None or user.embedding is None:
            return []

        cosine_distance = News.embedding.cosine_distance(user.embedding)
        cosine_similarity = (1 - cosine_distance).label("score")

        stmt = (
            select(News, cosine_similarity)
            .where(News.embedding.is_not(None))
            .order_by(cosine_distance)
            .limit(top_n)
        )
        rows = self.db.execute(stmt).all()
        return [ScoredNews(news=row[0], score=float(row[1])) for row in rows]
