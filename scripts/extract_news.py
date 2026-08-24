from __future__ import annotations

from datetime import datetime, timezone
import sys
import time
from pathlib import Path
from typing import Any

import requests
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings
from app.db.base import Base
from app.db.models import News
from app.services.embedding_service import EmbeddingService

NEWSDATA_URL = "https://newsdata.io/api/1/news"
REQUEST_TIMEOUT_SECONDS = 30


def _parse_publication_date(value: object) -> datetime:
    """Converte la data di NewsData.io in un datetime con timezone."""

    if not isinstance(value, str) or not value.strip():
        return datetime.now(timezone.utc)

    normalized_value = value.strip().replace("Z", "+00:00")
    try:
        parsed_date = datetime.fromisoformat(normalized_value)
    except ValueError:
        return datetime.now(timezone.utc)

    if parsed_date.tzinfo is None:
        parsed_date = parsed_date.replace(tzinfo=timezone.utc)
    return parsed_date


def _normalize_article(article: dict[str, Any]) -> dict[str, Any] | None:
    """Mappa un risultato NewsData.io sui campi del modello News."""

    title = article.get("title")
    link = article.get("link")
    if not isinstance(title, str) or not title.strip():
        return None
    if not isinstance(link, str) or not link.strip():
        return None

    description = article.get("description")
    content = article.get("content")
    summary = description.strip() if isinstance(description, str) and description.strip() else title.strip()
    content_text = content.strip() if isinstance(content, str) and content.strip() else summary

    source = article.get("source_id")
    language = article.get("language")

    return {
        "title": title.strip(),
        "content_text": content_text,
        "summary": summary,
        "date": _parse_publication_date(article.get("pubDate")),
        "source": source.strip() if isinstance(source, str) and source.strip() else "unknown",
        "link": link.strip(),
        "language": language.strip() if isinstance(language, str) and language.strip() else "unknown",
    }


def _download_news(
    api_key: str,
    category: str,
    language: str,
    domain: str,
    session: Session,
    embedding_service: EmbeddingService,
) -> int:
    """Scarica tutte le pagine e aggiunge le notizie alla sessione DB."""

    saved_count = 0
    seen_links: set[str] = set()
    seen_page_tokens: set[str] = set()
    next_page_token: str | None = None
    current_page = 0
    params = {
        "apikey": api_key,
        "category": category,
        "language": language,
        "domain": domain,
    }

    while True:
        current_page += 1
        print(f"Scaricamento pagina {current_page}...")

        if next_page_token:
            params["page"] = next_page_token
        else:
            params.pop("page", None)

        response = requests.get(
            NEWSDATA_URL,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Risposta NewsData.io non valida: atteso un oggetto JSON.")

        results = data.get("results", [])
        if not isinstance(results, list):
            raise ValueError("Risposta NewsData.io non valida: 'results' non e una lista.")

        for article in results:
            if not isinstance(article, dict):
                continue
            news_item = _normalize_article(article)
            if news_item is None or news_item["link"] in seen_links:
                continue
            seen_links.add(news_item["link"])
            session.add(
                News(
                    title=news_item["title"],
                    content_text=news_item["content_text"],
                    embedding=embedding_service.embed_text(news_item["content_text"]),
                )
            )
            saved_count += 1

        raw_next_page = data.get("nextPage")
        next_page_token = raw_next_page if isinstance(raw_next_page, str) and raw_next_page else None
        if next_page_token is None:
            print("Non ci sono piu notizie disponibili.")
            break
        if next_page_token in seen_page_tokens:
            raise RuntimeError("NewsData.io ha restituito un token di pagina gia elaborato.")

        seen_page_tokens.add(next_page_token)
        time.sleep(1)

    return saved_count


def extract_news(
    category: str = "business",
    language: str = "it",
    domain: str = "ilsole24ore",
) -> int:
    """Estrae notizie finanziarie da NewsData.io e aggiorna la tabella news."""

    settings = get_settings()
    if not settings.newsdata_api_key:
        raise RuntimeError("Imposta NEWSDATA_API_KEY nel file .env prima di eseguire lo script.")

    embedding_service = EmbeddingService(model_name=settings.model_name)
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        session.execute(delete(News))
        saved_count = _download_news(
            api_key=settings.newsdata_api_key,
            category=category,
            language=language,
            domain=domain,
            session=session,
            embedding_service=embedding_service,
        )
        if saved_count == 0:
            session.rollback()
            print("Nessuna notizia trovata: i dati presenti nel database non sono stati modificati.")
            return 0
        session.commit()

    print(f"Totale notizie salvate: {saved_count}")
    return saved_count


if __name__ == "__main__":
    extract_news()
