from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import User
from app.db.models import Notification, NotificationNews
from app.db.session import get_db
from app.services.generate_notification_service import GenerateNotificationService, GeneratedNotification
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/users/{user_id}")
def generate_user_notification(
    user_id: int,
    top_n: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
) -> GeneratedNotification | None:

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    items = RecommendationService(db).top_news_for_user(user_id=user_id, top_n=top_n)

    try:
        notification = GenerateNotificationService().generate_notification(user.profile_text, items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if notification is not None:
        created_at = datetime.now(timezone.utc)
        db_notification = Notification(
            user_id=user.id,
            created_at=created_at,
            notification_news=[
                NotificationNews(
                    news_id=int(generated_news.id),
                    summary=generated_news.summary,
                    relevance=generated_news.relevance,
                    created_at=created_at,
                )
                for generated_news in notification.generated_news
            ]
        )
        db.add(db_notification)
        db.commit()

    return notification
