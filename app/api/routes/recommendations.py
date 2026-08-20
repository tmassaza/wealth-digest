from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/users/{user_id}")
def user_recommendations(
    user_id: int,
    top_n: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Restituisce le top news consigliate per un utente."""

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    items = RecommendationService(db).top_news_for_user(user_id=user_id, top_n=top_n)
    return {
        "user_id": user_id,
        "top_n": top_n,
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "content_text": item.content_text,
                "score": 0.0,
            }
            for item in items
        ],
    }
