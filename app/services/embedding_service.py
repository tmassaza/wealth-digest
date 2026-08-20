from __future__ import annotations

from functools import lru_cache
from typing import Sequence

from sentence_transformers import SentenceTransformer

EMBEDDING_DIM = 384


@lru_cache(maxsize=4)
def _get_model(model_name: str) -> SentenceTransformer:
    model = SentenceTransformer(model_name)
    embedding_dim = model.get_embedding_dimension()
    if embedding_dim != EMBEDDING_DIM:
        raise ValueError(
            f"Model '{model_name}' produces {embedding_dim} dimensions, expected {EMBEDDING_DIM}."
        )
    return model


class EmbeddingService:
    """Servizio per generare embedding reali da testo.

    Il modello viene caricato una sola volta e poi riusato nelle chiamate successive.
    """

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") -> None:
        self.model_name = model_name

    def embed_text(self, text: str) -> list[float]:
        """Restituisce l'embedding normalizzato del testo.

        Per testo vuoto restituiamo un vettore nullo coerente con lo schema.
        """
        if not text or not text.strip():
            return [0.0] * EMBEDDING_DIM

        model = _get_model(self.model_name)
        vector = model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def embed_many(self, texts: Sequence[str]) -> list[list[float]]:
        """Applica embed_text a una sequenza di testi."""

        materialized_texts = list(texts)
        if not materialized_texts:
            return []

        model = _get_model(self.model_name)
        embeddings: list[list[float]] = []
        non_empty_indices: list[int] = []
        non_empty_texts: list[str] = []

        for index, text in enumerate(materialized_texts):
            if text and text.strip():
                non_empty_indices.append(index)
                non_empty_texts.append(text)

        embeddings = [[0.0] * EMBEDDING_DIM for _ in materialized_texts]
        if non_empty_texts:
            encoded = model.encode(non_empty_texts, normalize_embeddings=True)
            for index, vector in zip(non_empty_indices, encoded):
                embeddings[index] = vector.tolist()

        return embeddings
