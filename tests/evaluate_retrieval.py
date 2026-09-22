"""Valuta il retrieval MiniLM su profili e news sintetici, senza usare il DB.

Esecuzione dalla root del progetto:
    python -m tests.evaluate_retrieval
    python -m tests.evaluate_retrieval --user U03 --top 20
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

from app.services.embedding_service import EmbeddingService, build_news_embedding_text

DATI_PROVA = Path(__file__).parent / "dati_prova"
MINILM_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
RELEVANT_FROM = 2


def load_fixture(name: str) -> dict:
    return json.loads((DATI_PROVA / name).read_text(encoding="utf-8"))


def load_dataset() -> tuple[list[dict], list[dict], dict[str, dict[str, int]]]:
    users_data = load_fixture("users.json")
    news_data = load_fixture("news.json")
    relevance_data = load_fixture("relevance.json")
    versions = {
        users_data["dataset_version"],
        news_data["dataset_version"],
        relevance_data["dataset_version"],
    }
    if len(versions) != 1:
        raise ValueError("Le versioni dei tre fixture non coincidono")

    users = users_data["users"]
    news = news_data["news"]
    user_ids = [user["id"] for user in users]
    news_ids = [item["id"] for item in news]
    if len(user_ids) != 6 or len(set(user_ids)) != 6:
        raise ValueError("Sono richiesti sei utenti con ID univoci")
    if len(news_ids) != 60 or len(set(news_ids)) != 60:
        raise ValueError("Sono richieste 60 news con ID univoci")
    if any(not user["profile_text"].strip() for user in users):
        raise ValueError("Un profilo è vuoto")
    if any(not item["title"].strip() or not item["summary"].strip() for item in news):
        raise ValueError("Una news ha titolo o summary vuoto")

    labels: dict[str, dict[str, int]] = {}
    for row in relevance_data["ratings"]:
        news_id = row["news_id"]
        if news_id in labels or set(row) != {"news_id", *user_ids}:
            raise ValueError(f"Voti duplicati o incompleti per {news_id}")
        ratings = {user_id: row[user_id] for user_id in user_ids}
        if any(type(value) is not int or value not in (0, 1, 2, 3) for value in ratings.values()):
            raise ValueError(f"Voto fuori scala per {news_id}")
        labels[news_id] = ratings
    if set(labels) != set(news_ids):
        raise ValueError("Le news e i voti non coincidono")
    return users, news, labels


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Replica 1 - distanza coseno su vettori già normalizzati dal servizio."""
    dot = math.fsum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(math.fsum(value * value for value in left))
    right_norm = math.sqrt(math.fsum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        raise ValueError("Un embedding è nullo")
    return dot / (left_norm * right_norm)


def dcg(scores: list[int]) -> float:
    return sum((2**score - 1) / math.log2(rank + 1) for rank, score in enumerate(scores, start=1))


def evaluate_user(
    user: dict,
    user_vector: list[float],
    news: list[dict],
    news_vectors: list[list[float]],
    labels: dict[str, dict[str, int]],
) -> tuple[list[tuple[dict, float, int]], dict[str, float | int]]:
    user_id = user["id"]
    ranking = [
        (item, cosine_similarity(user_vector, vector), labels[item["id"]][user_id])
        for item, vector in zip(news, news_vectors, strict=True)
    ]
    ranking.sort(key=lambda row: (-row[1], row[0]["id"]))

    grades = [row[2] for row in ranking]
    total_relevant = sum(grade >= RELEVANT_FROM for grade in grades)
    ideal_grades = sorted(grades, reverse=True)

    def hits_at(k: int) -> int:
        return sum(grade >= RELEVANT_FROM for grade in grades[:k])

    target_for_90_percent = math.ceil(total_relevant * 0.9)
    found_relevant = 0
    rank_for_90_percent = 0
    for rank, grade in enumerate(grades, start=1):
        found_relevant += grade >= RELEVANT_FROM
        if found_relevant >= target_for_90_percent:
            rank_for_90_percent = rank
            break

    metrics: dict[str, float | int] = {
        "relevant_total": total_relevant,
        "precision_at_10": hits_at(10) / 10,
        "recall_at_10": hits_at(10) / total_relevant,
        "recall_at_20": hits_at(20) / total_relevant,
        "recall_at_30": hits_at(30) / total_relevant,
        "recall_at_40": hits_at(40) / total_relevant,
        "recall_at_50": hits_at(50) / total_relevant,
        "rank_for_90_percent": rank_for_90_percent,
        "last_strong_rank": max(
            (rank for rank, grade in enumerate(grades, start=1) if grade == 3),
            default=0,
        ),
        "ndcg_at_10": dcg(grades[:10]) / dcg(ideal_grades[:10]),
        "irrelevant_at_10": sum(grade == 0 for grade in grades[:10]),
        "missed_at_20": total_relevant - hits_at(20),
    }
    return ranking, metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", help="Mostra solo questo ID utente, per esempio U03")
    parser.add_argument("--top", type=int, default=20, help="Quante news mostrare per utente (default: 20)")
    parser.add_argument("--summary-only", action="store_true", help="Mostra solo le metriche")
    args = parser.parse_args()
    if not 1 <= args.top <= 60:
        parser.error("--top deve essere compreso fra 1 e 60")

    users, news, labels = load_dataset()
    if args.user and args.user not in {user["id"] for user in users}:
        parser.error(f"Utente sconosciuto: {args.user}")

    print(f"Modello: {MINILM_MODEL}")
    print("Input news: titolo + summary; rilevante = voto atteso 2 o 3")
    service = EmbeddingService(model_name=MINILM_MODEL)
    news_vectors = service.embed_many(
        [build_news_embedding_text(item["title"], item["summary"]) for item in news]
    )
    selected_users = [user for user in users if not args.user or user["id"] == args.user]
    user_vectors = service.embed_many([user["profile_text"] for user in selected_users])

    results = []
    for user, user_vector in zip(selected_users, user_vectors, strict=True):
        ranking, metrics = evaluate_user(user, user_vector, news, news_vectors, labels)
        results.append((user, ranking, metrics))
        if not args.summary_only:
            print(f"\n{user['id']} {user['name']}")
            for rank, (item, score, grade) in enumerate(ranking[: args.top], start=1):
                print(f"{rank:2}. {item['id']}  score={score:.4f}  voto={grade}  {item['title']}")
            missed = [
                (rank, item["id"], score, grade)
                for rank, (item, score, grade) in enumerate(ranking, start=1)
                if rank > 20 and grade >= RELEVANT_FROM
            ]
            print(f"Pertinenti fuori dalla Top 20: {len(missed)}")
            for rank, news_id, score, grade in missed[:5]:
                print(f"  posizione {rank}: {news_id}, score={score:.4f}, voto={grade}")

    print("\nRIEPILOGO")
    print("Utente             P@10  R@20  R@30  R@40  R@50  N90  ultimo3  0@10")
    for user, _ranking, metrics in results:
        print(
            f"{user['name']:<18}"
            f"{metrics['precision_at_10']:>5.0%} "
            f"{metrics['recall_at_20']:>5.0%} "
            f"{metrics['recall_at_30']:>5.0%} "
            f"{metrics['recall_at_40']:>5.0%} "
            f"{metrics['recall_at_50']:>5.0%} "
            f"{metrics['rank_for_90_percent']:>4} "
            f"{metrics['last_strong_rank']:>8} "
            f"{metrics['irrelevant_at_10']:>5}"
        )
    overall = Counter()
    for _user, _ranking, metrics in results:
        overall["irrelevant_at_10"] += int(metrics["irrelevant_at_10"])
        overall["missed_at_20"] += int(metrics["missed_at_20"])
    print(
        f"Totale: {overall['irrelevant_at_10']} risultati con voto 0 nelle Top 10; "
        f"{overall['missed_at_20']} coppie utente-news pertinenti oltre la posizione 20."
    )
    print("N90 = posizione minima che recupera almeno il 90% delle news con voto 2 o 3.")
    print("ultimo3 = posizione dell'ultima news con voto 3.")


if __name__ == "__main__":
    main()
