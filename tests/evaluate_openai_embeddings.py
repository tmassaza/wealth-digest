"""Confronta due modelli OpenAI sugli stessi dati del benchmark MiniLM.

Non modifica database, configurazione dell'app o vettori salvati. Ogni modello
riceve una sola volta i 6 profili e le 60 news del dataset sintetico.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

from app.services.embedding_service import build_news_embedding_text
from tests.evaluate_retrieval import evaluate_user, load_dataset

MODELS = ("text-embedding-3-small", "text-embedding-3-large")
API_URL = "https://api.openai.com/v1/embeddings"


def embed_many(model: str, texts: list[str], api_key: str) -> tuple[list[list[float]], int]:
    response = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model, "input": texts, "encoding_format": "float"},
        timeout=120,
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        # L'errore HTTP non deve stampare header o credenziali.
        raise RuntimeError(f"{model}: API HTTP {response.status_code}") from exc

    payload = response.json()
    data = sorted(payload["data"], key=lambda row: row["index"])
    if len(data) != len(texts) or [row["index"] for row in data] != list(range(len(texts))):
        raise ValueError(f"{model}: numero o ordine degli embedding inatteso")
    vectors = [row["embedding"] for row in data]
    if not vectors or any(len(vector) != len(vectors[0]) for vector in vectors):
        raise ValueError(f"{model}: dimensioni dei vettori incoerenti")
    return vectors, payload["usage"]["total_tokens"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Controlla i dati senza chiamare l'API")
    args = parser.parse_args()

    users, news, labels = load_dataset()
    news_texts = [build_news_embedding_text(item["title"], item["summary"]) for item in news]
    user_texts = [user["profile_text"] for user in users]
    texts = news_texts + user_texts
    print(f"Dataset: {len(users)} profili, {len(news)} news, {len(labels) * len(users)} voti")
    print("Testo: profilo utente vs. titolo + summary; distanza: coseno; nessun database")
    if args.dry_run:
        print(f"Dry-run: {len(texts)} testi per modello; nessuna chiamata API")
        return

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        parser.error("OPENAI_API_KEY non disponibile: aggiungila al .env o all'ambiente, senza condividerla in chat")

    for model in MODELS:
        vectors, token_count = embed_many(model, texts, api_key)
        news_vectors = vectors[: len(news)]
        user_vectors = vectors[len(news) :]
        print(f"\n{model}: {len(vectors[0])} dimensioni, {token_count} token input")
        print("Utente  P@10  R@20  R@30  R@40  R@50  N90  ultimo3  0@10  top10 (ID:voto)")
        total_zero_at_10 = 0
        total_missed_at_20 = 0
        for user, user_vector in zip(users, user_vectors, strict=True):
            ranking, metrics = evaluate_user(user, user_vector, news, news_vectors, labels)
            top10 = " ".join(f"{item['id']}:{grade}" for item, _score, grade in ranking[:10])
            weakest_relevant = max(
                ((rank, item["id"], score, grade) for rank, (item, score, grade) in enumerate(ranking, 1) if grade >= 2),
                key=lambda row: row[0],
            )
            strongest_nonrelevant = next(
                (rank, item["id"], score, grade)
                for rank, (item, score, grade) in enumerate(ranking, 1)
                if grade < 2
            )
            total_zero_at_10 += int(metrics["irrelevant_at_10"])
            total_missed_at_20 += int(metrics["missed_at_20"])
            print(
                f"{user['id']}     {metrics['precision_at_10']:>3.0%}   "
                f"{metrics['recall_at_20']:>3.0%}   {metrics['recall_at_30']:>3.0%}   "
                f"{metrics['recall_at_40']:>3.0%}   {metrics['recall_at_50']:>3.0%}   "
                f"{metrics['rank_for_90_percent']:>3}   {metrics['last_strong_rank']:>3}   "
                f"{metrics['irrelevant_at_10']:>2}    {top10}"
            )
            print(
                f"        Pertinente piu bassa: {weakest_relevant[1]} "
                f"posto {weakest_relevant[0]}, score {weakest_relevant[2]:.4f}; "
                f"non pertinente piu alta: {strongest_nonrelevant[1]} "
                f"posto {strongest_nonrelevant[0]}, score {strongest_nonrelevant[2]:.4f}"
            )
        print(
            f"Totale: {total_zero_at_10} risultati con voto 0 nelle Top 10; "
            f"{total_missed_at_20} coppie pertinenti oltre la Top 20"
        )


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, RuntimeError, ValueError, KeyError) as exc:
        print(f"Test interrotto: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
