"""
@author : WV

Lot B : description sémantique des modèles 3D

"""

from semantique.fusion import FusionImpossible, fusionner_descriptions
from semantique.modeles import SortieFusionLlm, SortieVueVlm
from semantique.pipeline import indexer_modele
from semantique.vectorisation import DimensionEmbeddingInvalide, vectoriser
from semantique.vue import DescriptionImpossible, decrire_vue
from semantique.vectorisation import DimensionEmbeddingInvalide, vectoriser

__all__ = [
    "DescriptionImpossible",
    "DimensionEmbeddingInvalide",
    "SortieVueVlm",
    "decrire_vue",
    "vectoriser",
]
