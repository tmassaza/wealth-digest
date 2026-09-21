from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.services.embedding_service import EmbeddingService

router = APIRouter(prefix="/users", tags=["users"])


class UserUpdate(BaseModel):
    name: str | None = None
    profile_text: str | None = None


@router.post("")
def create_user(name: str, profile_text: str, db: Session = Depends(get_db)) -> dict[str, object]:
    """Crea un utente e salva un embedding del suo profilo testuale."""

    embedding = EmbeddingService().embed_text(profile_text)
    user = User(name=name, profile_text=profile_text, embedding=embedding)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "name": user.name, "profile_text": user.profile_text}


@router.put("/{user_id}")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)) -> dict[str, object]:
    """Aggiorna un utente e rigenera l'embedding se cambia il profilo."""

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.name is not None:
        user.name = payload.name
    if payload.profile_text is not None:
        user.profile_text = payload.profile_text
        user.embedding = EmbeddingService().embed_text(user.profile_text)

    db.commit()
    db.refresh(user)
    return {"id": user.id, "name": user.name, "profile_text": user.profile_text}


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    """Recupera un utente per id."""

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name, "profile_text": user.profile_text}
