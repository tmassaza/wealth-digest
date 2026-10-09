from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import User
from app.db.models import Notification
from app.db.session import get_db
from app.helpers.notifications_helper import NotificationHelper
from app.services.generate_notification_service import (
    GeneratedNotification,
    UserGeneratedNotification
)

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/users/{user_id}/list")
def get_user_notifications(
    user_id: int,
    db: Session = Depends(get_db),
) -> list[dict[str, object]]:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    notifications = db.query(Notification).filter(Notification.user_id == user.id).all()
    result = list()
    for notification in notifications:
        result.append({
            "date": notification.created_at.strftime("%d-%m-%Y"),
            "notification_news": NotificationHelper().setup_notification_news_response(notification)
        })

    return result

@router.get("/users/{user_id}/list/count")
def get_user_notifications_count(
    user_id: int,
    db: Session = Depends(get_db),
) -> int:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    notifications_count = db.query(Notification).filter(Notification.user_id == user.id).count()
    return notifications_count

@router.get("/users/{user_id}/last")
def get_user_last_notification(
    user_id: int,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    notification = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).first()
    if notification:
        return NotificationHelper().setup_notification_news_response(notification)
    return {}

@router.get("/users/{user_id}")
def generate_user_notification(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserGeneratedNotification:

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    notification = NotificationHelper().generate_notification(user, True, db)
    if notification is None:
        raise HTTPException(status_code=500, detail="Errore imprevisto")

    return notification

@router.get("/users")
def generate_users_notification(
    db: Session = Depends(get_db),
) -> list[GeneratedNotification]:

    users = db.query(User).all()
    result = list()
    for user in users:
        user_notification = NotificationHelper().generate_notification(user, False, db)

        if user_notification is None:
            continue
        if type(user_notification) is not UserGeneratedNotification:
            raise HTTPException(status_code=500, detail="Errore imprevisto")

        res = GeneratedNotification(
            user_id=user.id,
            notification=user_notification,
        )
        result.append(res)

    return result