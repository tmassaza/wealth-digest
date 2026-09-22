import os
import json
from enum import Enum
from pydantic import BaseModel

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
from google.genai import types

from openai import OpenAI

from app.services.recommendation_service import ScoredNews

load_dotenv()

class LLMModel(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    

class GeneratedNotificationNews(BaseModel):
    id: str
    title: str
    date: str
    summary: str
    relevance: str
    source: str

class GeneratedNotification(BaseModel):
    generated_news: list[GeneratedNotificationNews]


class InvalidGeneratedNewsError(ValueError):
    """La risposta dell'LLM contiene una news non presente tra le candidate."""


def validate_generated_notification(
    notification: GeneratedNotification,
    selected_news: list[ScoredNews],
) -> GeneratedNotification:
    """Accetta solo news proposte al modello e ripristina i dati originali."""
    candidates = {item.news.id: item.news for item in selected_news}
    seen_ids: set[int] = set()
    validated_news: list[GeneratedNotificationNews] = []

    for generated_news in notification.generated_news:
        try:
            news_id = int(generated_news.id)
        except (TypeError, ValueError) as error:
            raise InvalidGeneratedNewsError(
                f"L'LLM ha restituito un ID di news non valido: {generated_news.id!r}."
            ) from error

        news = candidates.get(news_id)
        if news is None:
            raise InvalidGeneratedNewsError(
                f"L'LLM ha restituito la news {news_id}, non presente tra le candidate."
            )
        if news_id in seen_ids:
            continue

        seen_ids.add(news_id)
        validated_news.append(
            GeneratedNotificationNews(
                id=str(news_id),
                title=news.title,
                date=str(news.date),
                summary=generated_news.summary,
                relevance=generated_news.relevance,
                source=news.link,
            )
        )

    return GeneratedNotification(generated_news=validated_news)


class GenerateNotificationService:
    def __init__(self):
        pass

    def build_prompt(self, profile: str, selected_news: list[ScoredNews]) -> str:
        """
        Costruisce il prompt da inviare al modello generativo.
        """

        news_text = ""

        for scored_news in selected_news:
            news_text += f"""
    NEWS

    ID: {scored_news.news.id}
    Titolo: {scored_news.news.title}
    Data: {scored_news.news.date}
    URL: {scored_news.news.link}

    Contenuto:
    {scored_news.news.content_text}

    ----------------------------
    """

        prompt = f"""
    Sei un assistente che prepara notifiche finanziarie
    personalizzate per i clienti di una società di investimento.
    
    Il tuo compito si divide in DUE FASI.
    
    FASE 1 — SELEZIONE DELLE NOTIZIE
    
    Analizza tutte le notizie disponibili e seleziona esclusivamente
    quelle che sono realmente rilevanti per questo specifico cliente.
    
    La selezione deve essere effettuata esclusivamente sulla base
    della coerenza tra il profilo del cliente e il contenuto delle
    singole notizie.
    
    NON devi selezionare un numero prestabilito di notizie.
    
    Puoi selezionare:
    - nessuna notizia, se nessuna è sufficientemente rilevante;
    - una sola notizia;
    - alcune notizie;
    - tutte le notizie, se tutte risultano realmente rilevanti.
    
    Non includere una notizia solamente perché è una notizia
    finanziaria.
    
    Per determinare la rilevanza considera esclusivamente le
    informazioni disponibili nel profilo del cliente e negli articoli.
    
    In particolare, considera quando applicabile:
    
    - gli interessi esplicitamente indicati nel profilo;
    - gli strumenti finanziari indicati nel profilo;
    - i settori di interesse;
    - le aree geografiche di interesse;
    - gli obiettivi esplicitamente indicati;
    - le preferenze esplicitamente indicate;
    - la relazione concreta tra il contenuto della notizia
      e il profilo del cliente.
    
    Una notizia deve essere inclusa solo quando esiste una
    motivazione concreta e verificabile per considerarla rilevante
    per quel cliente.
    
    In caso di dubbio sulla rilevanza, non includere la notizia.
    
    Dopo aver selezionato le notizie rilevanti, ordinalle dalla
    PIÙ RILEVANTE alla MENO RILEVANTE per questo specifico cliente.
    
    L'ordinamento deve riflettere esclusivamente la rilevanza
    della notizia rispetto al profilo del cliente e non la data
    dell'articolo, l'ordine con cui gli articoli sono stati forniti
    o altri criteri non pertinenti.
    
    FASE 2 — GENERAZIONE DELLA NOTIFICA
    
    Per ogni notizia selezionata nella FASE 1, genera una
    notifica personalizzata.
    
    Per ogni articolo devi fornire:
    
    1. Titolo
    2. Data
    3. Un sommario chiaro e conciso della notizia
    4. Una spiegazione specifica del motivo per cui la notizia
       è rilevante per questo cliente
    5. Il link originale dell'articolo
    
    
    PROFILO DEL CLIENTE
    
    {profile}
    
    
    ARTICOLI DISPONIBILI
    
    {news_text}
    
    
    REGOLE
    
    - Usa esclusivamente le informazioni fornite.
    - Non inventare informazioni.
    - Non modificare i titoli.
    - Non modificare le date.
    - Non inventare dati, numeri o eventi.
    - Non dare consigli di investimento.
    - Non suggerire di comprare, vendere o mantenere strumenti finanziari.
    - Non formulare raccomandazioni di investimento implicite.
    - Spiega la rilevanza della notizia facendo riferimento
      esclusivamente al profilo del cliente e al contenuto
      dell'articolo.
    - Mantieni un linguaggio professionale e comprensibile.
    - Tratta ogni articolo selezionato separatamente.
    - Non aggiungere informazioni che non siano presenti
      negli articoli o nel profilo del cliente.
    - Non includere articoli che non siano stati selezionati
      nella FASE 1.
    - Non cercare di raggiungere un numero minimo o massimo
      di articoli.
    - Se nessun articolo è sufficientemente rilevante,
      restituisci una lista vuota secondo lo schema dell'API.
    
    
    OUTPUT
    
    La risposta deve contenere esclusivamente le notizie
    selezionate nella FASE 1.
    
    Deve esserci un elemento per ogni notizia selezionata
    e nessun elemento per le notizie non selezionate.
    
    Gli elementi devono essere restituiti in ordine decrescente
    di rilevanza per il cliente: il primo elemento deve essere
    la notizia più rilevante, l'ultimo elemento la meno rilevante
    tra quelle selezionate.
    
    La struttura e i campi della risposta sono definiti dallo
    schema fornito all'API. Non aggiungere campi ulteriori.

    """

        return prompt

    def run_openai(self, prompt: str) -> GeneratedNotification:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY non trovata: configura la chiave per usare OpenAI.")

        try:
            client = OpenAI(api_key=api_key)
            response = client.responses.parse(
                model="gpt-5",
                input=prompt,
                text_format=GeneratedNotification,
            )
        except Exception as error:
            raise RuntimeError(f"Errore OpenAI: {error}")
        notification = response.output_parsed

        if notification is None:
            raise RuntimeError("OpenAI non ha restituito alcun risultato strutturato.")

        return notification

    def run_gemini(self, prompt: str):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY non trovata: configura la chiave per usare Gemini.")

        try:
            client = genai.Client(api_key=api_key)
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

    def generate_notification(
            self,
            profile: str,
            selected_news: list[ScoredNews],
            llm_model: LLMModel = LLMModel.OPENAI
    ) -> GeneratedNotification | None:

        prompt = self.build_prompt(profile, selected_news)

        notification = self.run_openai(prompt) if llm_model is LLMModel.OPENAI else self.run_gemini(prompt)
        return validate_generated_notification(notification, selected_news)
