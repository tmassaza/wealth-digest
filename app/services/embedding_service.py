from __future__ import annotations

from typing import Sequence


class EmbeddingService:
    """Servizio minimo per generare embedding da testo.

    Al momento il comportamento è volutamente semplice: ci serve un contratto stabile
    mentre prepariamo l'integrazione del modello reale.
    """

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") -> None:
        self.model_name = model_name

    def embed_text(self, text: str) -> list[float]:
        """Restituisce un vettore placeholder della dimensione prevista dallo schema.

        La logica reale verrà introdotta quando attiveremo l'embedding con il modello.
        """
        vector = [0.0] * 384
        if text:
            vector[0] = 1.0
        return vector

    def embed_many(self, texts: Sequence[str]) -> list[list[float]]:
        """Applica embed_text a una sequenza di testi."""

        return [self.embed_text(text) for text in texts]
