"""
@author: WV

Vectorisation semantique par Ollama pour le Lot B.
"""

from typing import Protocol

from config import Config, obtenir_config


class ClientEmbedding(Protocol):
    def embed(self, textes: str) -> list[float]: ...


class DimensionEmbeddingInvalide(Exception):
    """Le vecteur recu n'a pas la dimension attendue."""

    def __init__(self, recue: int, attendue: int):
        self.recue = recue
        self.attendue = attendue
        super().__init__(
            f"Dimension d'embedding recue: {recue}; dimension attendue: {attendue}"
        )


def vectoriser(
    texte: str,
    client: ClientEmbedding,
    *,
    config: Config | None = None,
) -> list[float]:
    """Vectorise un texte avec Ollama et verifie sa dimension configuree."""
    if not texte or not texte.strip():
        raise ValueError("Le texte a vectoriser ne peut pas etre vide")

    config = config or obtenir_config()
    vecteur = client.embed(texte)
    if not isinstance(vecteur, list):
        raise DimensionEmbeddingInvalide(0, config.dimension_embedding)

    dimension_recue = len(vecteur)
    if dimension_recue != config.dimension_embedding:
        raise DimensionEmbeddingInvalide(
            dimension_recue,
            config.dimension_embedding,
        )

    return [float(valeur) for valeur in vecteur]
