from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.base import Base
from app.db.models import News, User

EMBEDDING_DIM = 384


def seed() -> None:
    """Inserisce utenti e news fittizie per test locali veloci."""

    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        users = [
            {"name": "Giulia Rossi", "profile_text": "utente conservativa, preferisce stabilità, basso rischio, obbligazioni investment grade, ETF difensivi e protezione dall'inflazione."},
            {"name": "Marco Bianchi", "profile_text": "utente bilanciato, cerca diversificazione globale, macroeconomia, asset allocation e settori difensivi e ciclici in equilibrio."},
            {"name": "Elena Conti", "profile_text": "utente orientata alla crescita, interessata a tecnologia, AI, cloud, semiconduttori e trend globali azionari."},
            {"name": "Luca Ferri", "profile_text": "utente focalizzato sul reddito, segue dividendi, utility, infrastrutture e bond corporate di qualita."},
            {"name": "Sara Romano", "profile_text": "utente dinamica, valuta small cap, mercati emergenti e strategie fattoriali con orizzonte lungo."},
            {"name": "Davide Moretti", "profile_text": "utente prudente ma curioso, combina liquidita, BTP, ETF obbligazionari e quota selettiva azionaria."},
        ]

        news_items = [
            {"title": "Tassi BCE stabili ma inflazione ancora alta", "content_text": "La Banca Centrale Europea mantiene prudenza: inflazione elevata e mercato attento a tassi, spread e credito."},
            {"title": "ETF difensivi in evidenza", "content_text": "Gli ETF a bassa volatilità mostrano interesse tra gli investitori prudenti in un mercato volatile."},
            {"title": "Intelligenza artificiale e mercati azionari", "content_text": "Le aziende AI continuano ad attirare investimenti, con valutazioni in crescita nei segmenti software e semiconduttori."},
            {"title": "Obbligazioni e spread sul mercato europeo", "content_text": "Le obbligazioni europee restano un punto di attenzione per chi cerca stabilità e rendimento."},
            {"title": "Energia: petrolio volatile dopo dati sulla domanda", "content_text": "Le quotazioni del petrolio oscillano dopo dati contrastanti su domanda globale e scorte settimanali."},
            {"title": "Banche italiane, utili oltre le attese", "content_text": "Gli istituti italiani riportano utili robusti, sostenuti da margini di interesse e costi sotto controllo."},
            {"title": "BTP a 10 anni: rendimento in lieve calo", "content_text": "Il rendimento del BTP decennale arretra leggermente, con investitori in cerca di duration moderata."},
            {"title": "Mercati emergenti in recupero", "content_text": "Alcuni listini emergenti recuperano grazie a valute più stabili e attese di politica monetaria meno restrittiva."},
            {"title": "Tech europea spinta dal cloud", "content_text": "La domanda enterprise per servizi cloud sostiene i ricavi di diverse società tecnologiche europee."},
            {"title": "Oro vicino ai massimi annuali", "content_text": "L'oro rimane vicino ai massimi dell'anno, favorito da incertezza geopolitica e copertura contro volatilità."},
        ]

        for payload in users:
            session.merge(User(**payload, embedding=[0.0] * EMBEDDING_DIM))

        for payload in news_items:
            session.merge(News(**payload, embedding=[0.0] * EMBEDDING_DIM))

        session.commit()


if __name__ == "__main__":
    seed()
