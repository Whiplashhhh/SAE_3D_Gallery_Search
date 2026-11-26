"""
@author : WV

Lot B : description sémantique des modèles 3D

"""

from semantique.fusion import FusionImpossible, fusionner_descriptions
from semantique.modeles import SortieFusionLlm, SortieVueVlm
from semantique.pipeline import indexer_modele
from semantique.vectorisation import DimensionEmbeddingInvalide, vectoriser
from semantique.vue import DescriptionImpossible, decrire_vue

__all__ = [
    "DescriptionImpossible",
    "DimensionEmbeddingInvalide",
    "FusionImpossible",
    "SortieFusionLlm",
    "SortieVueVlm",
    "decrire_vue",
    "fusionner_descriptions",
    "indexer_modele",
    "vectoriser",
]
