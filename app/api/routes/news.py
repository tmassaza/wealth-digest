from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import News
from app.db.session import get_db
from app.services.embedding_service import EmbeddingService

router = APIRouter(prefix="/news", tags=["news"])


@router.post("")
def create_news(title: str, content_text: str, db: Session = Depends(get_db)) -> dict[str, object]:
    """Crea una notizia e salva l'embedding del testo."""

    embedding = EmbeddingService().embed_text(content_text)
    news = News(title=title, content_text=content_text, embedding=embedding)
    db.add(news)
    db.commit()
    db.refresh(news)
    return {"id": news.id, "title": news.title, "content_text": news.content_text}


@router.get("/{news_id}")
def get_news(news_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    """Recupera una notizia per id."""

    news = db.get(News, news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return {"id": news.id, "title": news.title, "content_text": news.content_text}
