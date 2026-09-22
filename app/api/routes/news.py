from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models import News
from app.db.session import get_db
from app.services.embedding_service import EmbeddingService, build_news_embedding_text
from app.services.extract_news_service import ExtractNewsService

router = APIRouter(prefix="/news", tags=["news"])


class NewsUpdate(BaseModel):
    title: str | None = None
    content_text: str | None = None
    summary: str | None = None


@router.post("")
def create_news(
    title: str,
    content_text: str,
    summary: str | None = None,
    link: str | None = None,
    source: str = "api",
    language: str = "it",
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Crea una notizia e calcola l'embedding da titolo e summary."""

    embedding_text = build_news_embedding_text(title, summary)
    news = News(
        title=title,
        content_text=content_text,
        summary=summary,
        embedding=EmbeddingService().embed_text(embedding_text),
        date=datetime.now(timezone.utc),
        link=link or f"urn:wealth-digest:news:{uuid4()}",
        source=source,
        language=language,
    )
    db.add(news)
    db.commit()
    db.refresh(news)
    return {
        "id": news.id,
        "title": news.title,
        "summary": news.summary,
        "content_text": news.content_text,
    }


@router.post("/extract")
def extract_news_endpoint(
    category: str = Query(default="business"),
    language: str = Query(default="it"),
    domain: str | None = Query(default=None),
) -> dict[str, object]:
    """Importa news dalle fonti configurate o dai domini richiesti."""

    return {
        "inserted_count": ExtractNewsService().extract_news(
            category=category,
            language=language,
            domain=domain,
        )
    }


@router.put("/{news_id}")
def update_news(news_id: int, payload: NewsUpdate, db: Session = Depends(get_db)) -> dict[str, object]:
    """Aggiorna una news e rigenera il vettore se cambia titolo o summary."""

    news = db.get(News, news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")

    embedding_changed = False
    if "title" in payload.model_fields_set:
        news.title = payload.title or ""
        embedding_changed = True
    if "summary" in payload.model_fields_set:
        news.summary = payload.summary
        embedding_changed = True
    if "content_text" in payload.model_fields_set:
        news.content_text = payload.content_text

    if embedding_changed:
        embedding_text = build_news_embedding_text(news.title, news.summary)
        news.embedding = EmbeddingService().embed_text(embedding_text)

    db.commit()
    db.refresh(news)
    return {
        "id": news.id,
        "title": news.title,
        "summary": news.summary,
        "content_text": news.content_text,
    }


@router.get("/{news_id}")
def get_news(news_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    """Recupera una notizia per id."""

    news = db.get(News, news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return {
        "id": news.id,
        "title": news.title,
        "summary": news.summary,
        "content_text": news.content_text,
    }
