from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.extract_news_service import ExtractNewsService


def extract_news(
    category: str = "business",
    language: str = "it",
    domain: str | None = None,
) -> int:
    """Importa le news usando lo stesso servizio richiamato dalle API."""
    return ExtractNewsService().extract_news(
        category=category,
        language=language,
        domain=domain,
    )


if __name__ == "__main__":
    extract_news()
