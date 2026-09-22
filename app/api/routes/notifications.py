from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import User
from app.db.models import Notification, NotificationNews
from app.db.session import get_db
from app.services.generate_notification_service import GenerateNotificationService, GeneratedNotification, LLMModel
from app.services.recommendation_service import RecommendationService
from app.services.extract_news_service import ExtractNewsService

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/users/{user_id}")
def generate_user_notification(
    user_id: int,
    extract_news: bool = Query(default=True, description="Parametro utilizzato in fase di testing; impostare a False per evitare di recuperare e salvare a db news duplicate."
                                                         "Rimuovere in futuro"),
    llm_model: LLMModel = Query(default=LLMModel.OPENAI, description="Parametro utilizzato in fase di testing per fare confronto openai e gemini. Rimuovere in futuro"),
    db: Session = Depends(get_db),
) -> GeneratedNotification | None:

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if extract_news:
        try:
            ExtractNewsService().extract_news(category='business', language='it', domain='ilsole24ore,milanofinanza,quifinanza,cnbc,yahoo')
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    items = RecommendationService(db).top_news_for_user(user_id=user_id, top_n=10)

    try:
        notification = GenerateNotificationService().generate_notification(user.profile_text, items, llm_model)
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
