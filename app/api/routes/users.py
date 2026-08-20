from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.services.embedding_service import EmbeddingService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("")
def create_user(name: str, profile_text: str, db: Session = Depends(get_db)) -> dict[str, object]:
    """Crea un utente e salva un embedding del suo profilo testuale."""

    embedding = EmbeddingService().embed_text(profile_text)
    user = User(name=name, profile_text=profile_text, embedding=embedding)
    db.add(user)
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
