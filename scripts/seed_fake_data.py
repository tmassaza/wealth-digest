from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings
from app.db.base import Base
from app.db.models import User
from app.services.embedding_service import EmbeddingService


def seed() -> None:
    """Inserisce utenti fittizi per test locali veloci."""

    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    embedding_service = EmbeddingService(model_name=settings.model_name)

    users = [
        {"name": "Giulia Rossi", "profile_text": "utente conservativa, preferisce stabilità, basso rischio, obbligazioni investment grade, ETF difensivi e protezione dall'inflazione."},
        {"name": "Marco Bianchi", "profile_text": "utente bilanciato, cerca diversificazione globale, macroeconomia, asset allocation e settori difensivi e ciclici in equilibrio."},
        {"name": "Elena Conti", "profile_text": "utente orientata alla crescita, interessata a tecnologia, AI, cloud, semiconduttori e trend globali azionari."},
        {"name": "Luca Ferri", "profile_text": "utente focalizzato sul reddito, segue dividendi, utility, infrastrutture e bond corporate di qualita."},
        {"name": "Sara Romano", "profile_text": "utente dinamica, valuta small cap, mercati emergenti e strategie fattoriali con orizzonte lungo."},
        {"name": "Davide Moretti", "profile_text": "utente prudente ma curioso, combina liquidita, BTP, ETF obbligazionari e quota selettiva azionaria."},
    ]

    with Session(engine) as session:
        # Aggiorna solo i profili demo esistenti; non eliminare utenti o notifiche.
        existing_users = {
            user.name: user
            for user in session.scalars(
                select(User).where(User.name.in_([payload["name"] for payload in users]))
            )
        }

        for payload in users:
            user = existing_users.get(payload["name"])
            if user is None:
                session.add(
                    User(
                        **payload,
                        embedding=embedding_service.embed_text(payload["profile_text"]),
                    )
                )
            elif user.profile_text != payload["profile_text"] or user.embedding is None:
                user.profile_text = payload["profile_text"]
                user.embedding = embedding_service.embed_text(payload["profile_text"])

        session.commit()


if __name__ == "__main__":
    seed()
