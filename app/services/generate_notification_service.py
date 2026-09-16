import os
import json
from dataclasses import dataclass

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
from google.genai import types

from app.services.recommendation_service import ScoredNews

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY non trovata. "
        "Controlla di aver creato il file .env nella root del progetto."
    )

# Inizializzo il client Gemini
client = genai.Client(api_key=api_key)


@dataclass(slots=True)
class GeneratedNotificationNews:
    id: str
    title: str
    date: str
    summary: str
    relevance: str
    source: str


@dataclass(slots=True)
class GeneratedNotification:
    generated_news: list[GeneratedNotificationNews]

class GenerateNotificationService:
    def __init__(self):
        pass

    def build_prompt(self, profile: str, selected_articles: list[ScoredNews]) -> str:
        """
        Costruisce il prompt da inviare al modello generativo.
        """

        articles_text = ""

        for article in selected_articles:
            articles_text += f"""
    ARTICOLO

    ID: {article.news.id}
    Titolo: {article.news.title}
    Data: {article.news.date}
    Score di rilevanza: {article.score}
    URL: {article.news.link}

    Contenuto:
    {article.news.content_text}

    ----------------------------
    """

        prompt = f"""
    Sei un assistente che prepara notifiche finanziarie
    personalizzate per i clienti di una società di investimento.

    PROFILO DEL CLIENTE

    {profile}


    ARTICOLI SELEZIONATI

    {articles_text}


    COMPITO

    Genera una notifica personalizzata per questo cliente.

    Per ogni articolo devi fornire:

    1. Titolo
    2. Data
    3. Un sommario chiaro e conciso della notizia
    4. Una spiegazione specifica del motivo per cui
       la notizia è rilevante per questo cliente
    5. Il link originale dell'articolo


    REGOLE

    - Usa esclusivamente le informazioni fornite.
    - Non inventare informazioni.
    - Non modificare i titoli.
    - Non modificare le date.
    - Non inventare dati, numeri o eventi.
    - Non dare consigli di investimento.
    - Non suggerire di comprare, vendere o mantenere strumenti finanziari.
    - Spiega la rilevanza della notizia facendo riferimento
      esclusivamente al profilo del cliente.
    - Mantieni un linguaggio professionale e comprensibile.
    - Tratta ogni articolo separatamente.
    - Non aggiungere informazioni che non siano presenti
      negli articoli o nel profilo del cliente.


    OUTPUT

    La risposta deve contenere una notifica con un elemento
    per ogni articolo selezionato.
    
    La struttura e i campi della risposta sono definiti dallo
    schema fornito all'API Gemini. Non aggiungere campi ulteriori.

    """

        return prompt

    def generate_notification(
            self,
            profile: str,
            selected_articles: list[ScoredNews],
    ) -> GeneratedNotification | None:
        """
        Invia profilo cliente e articoli a Gemini
        e restituisce la notifica generata.
        """

        prompt = self.build_prompt(profile, selected_articles)

        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GeneratedNotification,
                )
            )
        except ServerError as error:
            raise RuntimeError(error.message)

        response_text = response.text
        if response_text is None:
            raise RuntimeError("Gemini non ha restituito alcun testo.")
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            raise ValueError(f"Gemini ha restituio un JSON non valido:\n {response_text}")
        notification = GeneratedNotification(
            generated_news=[
                GeneratedNotificationNews(**generated_news)
                for generated_news in data["generated_news"]
            ]
        )

        return notification