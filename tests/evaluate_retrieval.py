"""Valuta il retrieval MiniLM su profili e news sintetici, senza usare il DB.

Esecuzione dalla root del progetto:
    python -m tests.evaluate_retrieval
    python -m tests.evaluate_retrieval --user U03 --top 20
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from app.services.embedding_service import EmbeddingService, build_news_embedding_text

DATI_PROVA = Path(__file__).parent / "dati_prova"
REPORT_PATH = Path(__file__).parent / "reports" / "risultati-minilm.md"
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
        raise ValueError("Le versioni dei tre file di dati non coincidono")

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
    """Replica la similarità coseno usata dal ranking dell'applicazione."""
    dot = math.fsum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(math.fsum(value * value for value in left))
    right_norm = math.sqrt(math.fsum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        raise ValueError("Un embedding è nullo")
    return dot / (left_norm * right_norm)


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
    top_10 = grades[:10]
    top_20 = grades[:20]
    total_relevant = sum(grade >= RELEVANT_FROM for grade in grades)
    top_20_relevant = sum(grade >= RELEVANT_FROM for grade in top_20)
    metrics: dict[str, float | int] = {
        "top_10_relevant": sum(grade >= RELEVANT_FROM for grade in top_10),
        "top_10_partial": sum(grade == 1 for grade in top_10),
        "top_10_irrelevant": sum(grade == 0 for grade in top_10),
        "top_20_relevant": top_20_relevant,
        "outside_top_20_relevant": total_relevant - top_20_relevant,
        "total_relevant": total_relevant,
    }
    return ranking, metrics


def percentage(part: int, total: int) -> str:
    return f"{part / total:.0%}"


def totals(results: list[tuple[dict, list[tuple[dict, float, int]], dict]]) -> dict[str, int]:
    summary = {
        "top_10_relevant": sum(int(row[2]["top_10_relevant"]) for row in results),
        "top_10_partial": sum(int(row[2]["top_10_partial"]) for row in results),
        "top_10_irrelevant": sum(int(row[2]["top_10_irrelevant"]) for row in results),
        "top_20_relevant": sum(int(row[2]["top_20_relevant"]) for row in results),
        "outside_top_20_relevant": sum(
            int(row[2]["outside_top_20_relevant"]) for row in results
        ),
        "total_relevant": sum(int(row[2]["total_relevant"]) for row in results),
        "top_10_total": len(results) * 10,
    }
    return summary


def print_summary(results: list[tuple[dict, list[tuple[dict, float, int]], dict]]) -> None:
    print("\nQUALITA TOP 10")
    print("Utente             Affini Top 10  Parziali  Fuori tema")
    for user, _ranking, metrics in results:
        print(
            f"{user['name']:<19}"
            f"{int(metrics['top_10_relevant']):>5}/10"
            f"{int(metrics['top_10_partial']):>11}"
            f"{int(metrics['top_10_irrelevant']):>12}"
        )

    overall = totals(results)
    print(
        f"{'TOTALE':<19}"
        f"{overall['top_10_relevant']:>5}/{overall['top_10_total']:<2}"
        f"{overall['top_10_partial']:>10}"
        f"{overall['top_10_irrelevant']:>12}"
    )

    print("\nRECUPERO DELLE NEWS PERTINENTI NELLA TOP 20")
    print("Utente             Totale   Nella Top 20    Fuori Top 20")
    for user, _ranking, metrics in results:
        total = int(metrics["total_relevant"])
        recovered = int(metrics["top_20_relevant"])
        outside = int(metrics["outside_top_20_relevant"])
        print(
            f"{user['name']:<19}"
            f"{total:>4}"
            f"{recovered:>10}/{total:<2} ({percentage(recovered, total):>3})"
            f"{outside:>10}/{total:<2} ({percentage(outside, total):>3})"
        )
    print(
        f"{'TOTALE':<19}"
        f"{overall['total_relevant']:>4}"
        f"{overall['top_20_relevant']:>10}/{overall['total_relevant']:<3} "
        f"({percentage(overall['top_20_relevant'], overall['total_relevant']):>3})"
        f"{overall['outside_top_20_relevant']:>9}/{overall['total_relevant']:<3} "
        f"({percentage(overall['outside_top_20_relevant'], overall['total_relevant']):>3})"
    )

def build_report(results: list[tuple[dict, list[tuple[dict, float, int]], dict]]) -> str:
    overall = totals(results)
    lines = [
        "# Risultati del test MiniLM",
        "",
        "- Dataset: 6 profili e 60 news sintetiche.",
        "- Input delle news: titolo + summary.",
        "- Voto manuale: da 0 (fuori tema) a 3 (molto affine).",
        "- News pertinente: voto 2 o 3.",
        "",
        "## Qualità delle Top 10",
        "",
        "| Utente | Affini | Parziali | Fuori tema |",
        "|---|---:|---:|---:|",
    ]
    for user, _ranking, metrics in results:
        lines.append(
            f"| {user['name']} | {int(metrics['top_10_relevant'])}/10 | "
            f"{int(metrics['top_10_partial'])} | {int(metrics['top_10_irrelevant'])} |"
        )
    lines.extend(
        [
            f"| **Totale** | **{overall['top_10_relevant']}/{overall['top_10_total']} "
            f"({percentage(overall['top_10_relevant'], overall['top_10_total'])})** | "
            f"**{overall['top_10_partial']}/{overall['top_10_total']} "
            f"({percentage(overall['top_10_partial'], overall['top_10_total'])})** | "
            f"**{overall['top_10_irrelevant']}/{overall['top_10_total']} "
            f"({percentage(overall['top_10_irrelevant'], overall['top_10_total'])})** |",
            "",
            "## Recupero delle news pertinenti nella Top 20",
            "",
            "| Utente | Pertinenti totali | Nella Top 20 | Fuori dalla Top 20 |",
            "|---|---:|---:|---:|",
        ]
    )
    for user, _ranking, metrics in results:
        total = int(metrics["total_relevant"])
        recovered = int(metrics["top_20_relevant"])
        outside = int(metrics["outside_top_20_relevant"])
        lines.append(
            f"| {user['name']} | {total} | {recovered}/{total} "
            f"({percentage(recovered, total)}) | {outside}/{total} "
            f"({percentage(outside, total)}) |"
        )
    lines.extend(
        [
            f"| **Totale** | **{overall['total_relevant']}** | "
            f"**{overall['top_20_relevant']}/{overall['total_relevant']} "
            f"({percentage(overall['top_20_relevant'], overall['total_relevant'])})** | "
            f"**{overall['outside_top_20_relevant']}/{overall['total_relevant']} "
            f"({percentage(overall['outside_top_20_relevant'], overall['total_relevant'])})** |",
            "",
        ]
    )
    return "\n".join(lines)


def grade_label(grade: int) -> str:
    return {0: "fuori tema", 1: "parziale", 2: "affine", 3: "molto affine"}[grade]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", help="Mostra il dettaglio di un utente, per esempio U03")
    parser.add_argument("--top", type=int, default=20, help="Risultati mostrati nel dettaglio (default: 20)")
    args = parser.parse_args()
    if not 1 <= args.top <= 60:
        parser.error("--top deve essere compreso fra 1 e 60")

    users, news, labels = load_dataset()
    if args.user and args.user not in {user["id"] for user in users}:
        parser.error(f"Utente sconosciuto: {args.user}")

    print(f"Modello: {MINILM_MODEL}")
    print("Dataset: 6 utenti, 60 news sintetiche, 360 valutazioni manuali")
    print("Input news: titolo + summary")
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

    print_summary(results)

    if args.user:
        user, ranking, _metrics = results[0]
        print(f"\nDETTAGLIO {user['name'].upper()}")
        for rank, (item, score, grade) in enumerate(ranking[: args.top], start=1):
            print(
                f"{rank:2}. {item['id']}  score={score:.4f}  "
                f"voto={grade} ({grade_label(grade)})  {item['title']}"
            )
    else:
        REPORT_PATH.write_text(build_report(results), encoding="utf-8")
        print(f"\nReport aggiornato: {REPORT_PATH.as_posix()}")


if __name__ == "__main__":
    main()
