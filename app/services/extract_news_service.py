from __future__ import annotations

import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import News
from app.services.embedding_service import EmbeddingService, build_news_embedding_text


class ExtractNewsService:
    def extract_news(
        self,
        category: str = "business",
        language: str = "it",
        domain: str | None = None,
    ) -> int:
        settings = get_settings()

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/91.0 Safari/537.36"
            )
        }

        params = {
            "apikey": settings.newsdata_api_key,
            "category": category,
            "language": language,
            "domain": domain or settings.news_domains,
        }

        engine = create_engine(settings.database_url, pool_pre_ping=True)
        embedding_service = EmbeddingService(model_name=settings.model_name)

        next_page_token: str | None = None
        pagina_corrente = 0
        inserted_count = 0

        with Session(engine) as session:
            existing_links = set(session.scalars(select(News.link)).all())

            while True:
                pagina_corrente += 1
                print(f"Scaricamento pagina {pagina_corrente}...")

                if next_page_token:
                    params["page"] = next_page_token
                else:
                    params.pop("page", None)

                response = requests.get(
                    settings.newsdata_base_url,
                    params=params,
                    timeout=30,
                )
                response.raise_for_status()
                dati = response.json()

                for articolo in dati.get("results") or []:
                    title = articolo.get("title")
                    link = articolo.get("link")

                    if not title or not link or link in existing_links:
                        continue

                    summary = articolo.get("description")
                    content_text = (
                        self.extract_article_text(link, headers)
                        or summary
                        or title
                    )

                    news = News(
                        title=title,
                        content_text=content_text,
                        summary=summary,
                        embedding=embedding_service.embed_text(
                            build_news_embedding_text(title, summary)
                        ),
                        date=self.parse_publication_date(articolo.get("pubDate")),
                        link=link,
                        source=articolo.get("source_id") or "unknown",
                        language=articolo.get("language") or "unknown",
                    )

                    session.add(news)
                    existing_links.add(link)
                    inserted_count += 1

                next_page_token = dati.get("nextPage")

                if not next_page_token:
                    break

                time.sleep(1)

            session.commit()

        print(f"Notizie inserite: {inserted_count}")
        return inserted_count

    def parse_publication_date(self, value: str | None) -> datetime:
        if not value:
            return datetime.now(timezone.utc)

        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            return datetime.now(timezone.utc)

    def extract_article_text(self, url: str, headers: dict[str, str]) -> str | None:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            selectors = [
                "article",
                ".article-body",
                ".story-body",
                ".post-content",
                ".entry-content",
                'div[itemprop="articleBody"]',
            ]

            article_text: list[str] = []

            for selector in selectors:
                container = soup.select_one(selector)
                if container is None:
                    continue

                article_text = [
                    paragraph.get_text(" ", strip=True)
                    for paragraph in container.select("p")
                    if paragraph.get_text(" ", strip=True)
                ]

                if article_text:
                    break

            if not article_text:
                article_text = [
                    paragraph.get_text(" ", strip=True)
                    for paragraph in soup.select("p")
                    if paragraph.get_text(" ", strip=True)
                ]

            return "\n\n".join(article_text) if article_text else None

        except requests.exceptions.RequestException as error:
            print(f"Errore durante lo scraping di {url}: {error}")
            return None
