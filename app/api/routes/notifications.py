from __future__ import annotations

from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import User
from app.db.models import Notification, NotificationNews
from app.db.session import get_db
from app.services.extract_news_service import ExtractNewsService
from app.services.generate_notification_service import (
    GenerateNotificationService,
    GeneratedNotification,
    InvalidGeneratedNewsError,
    LLMModel,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/notifications", tags=["notifications"])

class NotificationSkippedResponse(BaseModel):
    message: str

@router.get("/users/{user_id}")
def generate_user_notification(
    user_id: int,
    llm_model: LLMModel = Query(default=LLMModel.OPENAI, description="Parametro utilizzato in fase di testing per fare confronto openai e gemini. Rimuovere in futuro"),
    db: Session = Depends(get_db),
) -> GeneratedNotification | NotificationSkippedResponse:

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    last_notification = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .first()
    )

    if last_notification is not None:
        now = datetime.now(timezone.utc)
        next_notification_at = (
            last_notification.created_at
            + timedelta(days=user.notification_interval_days)
        )

        if now < next_notification_at:
            return NotificationSkippedResponse(
                message=(
                    "Notifica non creata: la frequenza configurata "
                    "non consente ancora una nuova notifica."
                    )   
            )

    items = RecommendationService(db).top_news_for_user(user_id=user_id, top_n=10)

    try:
        notification = GenerateNotificationService().generate_notification(user.profile_text, items, llm_model)
    except InvalidGeneratedNewsError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if notification is not None and notification.generated_news:
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
