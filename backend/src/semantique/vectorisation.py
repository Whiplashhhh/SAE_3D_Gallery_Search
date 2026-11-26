"""
@author: WV

Vectorisation d'un texte par le modèle d'embedding (Lot B)

Le client Ollama s'occupe du réseau et de ses tentatives. Ici, on vérifie
seulement que le vecteur a la dimension attendue par la configuration : un
vecteur d'une autre taille rendrait la fiche inutilisable dans l'index du Lot C
"""

from config import Config, obtenir_config
from ollama.client import ClientOllama


class DimensionEmbeddingInvalide(Exception):
    """Le vecteur renvoyé n'a pas la dimension attendue par la configuration."""

    def __init__(self, recue: int, attendue: int):
        self.recue = recue
        self.attendue = attendue
        super().__init__(
            f"Dimension d'embedding invalide : {recue} reçue, {attendue} attendue."
        )


def vectoriser(
    texte: str,
    client: ClientOllama,
    *,
    config: Config | None = None,
) -> list[float]:
    """Renvoie le vecteur d'embedding du texte, après contrôle de sa dimension.

    throw ValueError si le texte est vide (aucun appel à Ollama).
    throw DimensionEmbeddingInvalide si la longueur du vecteur diffère de
    dimension_embedding.
    """
    if not texte.strip():
        raise ValueError("Aucun texte à vectoriser.")

    config = config or obtenir_config()
    vecteur = client.embed(texte)
    if len(vecteur) != config.dimension_embedding:
        raise DimensionEmbeddingInvalide(len(vecteur), config.dimension_embedding)
    return vecteur
