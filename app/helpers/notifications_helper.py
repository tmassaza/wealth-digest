from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.models import Notification, NotificationNews, User
from app.db.session import get_db
from app.services.generate_notification_service import GenerateNotificationService, InvalidGeneratedNewsError, \
    UserGeneratedNotification
from app.services.recommendation_service import RecommendationService


class NotificationHelper:
    def setup_notification_news_response(self, notification: Notification) -> dict[str, object]:
        list_notification_news = list()
        for notification_news in notification.notification_news:
            news = notification_news.news
            list_notification_news.append({
                "title": news.title,
                "date": news.date.strftime("%d-%m-%Y"),
                "summary": news.summary,
                "relevance": notification_news.relevance_user,
                "source": news.source,
                "link": news.link
            })
        return {"date": notification.created_at.strftime("%d-%m-%Y"),
                "notification_news": list_notification_news}

    def generate_notification(
            self,
            user: User,
            is_generate_user_notification_endpoint: bool,
            db: Session = Depends(get_db),
    ) -> UserGeneratedNotification | None:
        user_id = user.id

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
                if is_generate_user_notification_endpoint:
                    raise HTTPException(status_code=500, detail="Notifica non creata: la frequenza configurata "
                                                                "non consente ancora una nuova notifica.")
                else:
                    return None

        items = RecommendationService(db).top_news_for_user(user_id=user_id, top_n=10)

        try:
            notification = GenerateNotificationService().generate_notification(user.profile_text, items)
        except InvalidGeneratedNewsError as error:
            raise HTTPException(status_code=502, detail=str(error)) from error
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        if notification is None:
            raise HTTPException(status_code=500,
                                detail=f"Errore imprevisto durante la generazione della notifica per utente {user_id}")

        if notification.generated_news:
            created_at = datetime.now(timezone.utc)
            db_notification = Notification(
                user_id=user.id,
                created_at=created_at,
                notification_news=[
                    NotificationNews(
                        news_id=int(generated_news.id),
                        summary=generated_news.summary,
                        relevance=generated_news.relevance,
                        relevance_user=generated_news.relevance_user,
                        created_at=created_at,
                    )
                    for generated_news in notification.generated_news
                ]
            )
            db.add(db_notification)
            db.commit()

        return notification