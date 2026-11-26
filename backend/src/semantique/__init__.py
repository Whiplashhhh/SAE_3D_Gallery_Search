"""
@author : WV

Lot B : description sémantique des modèles 3D

"""

from semantique.modeles import SortieVueVlm
from semantique.vue import DescriptionImpossible, decrire_vue
from semantique.vectorisation import DimensionEmbeddingInvalide, vectoriser

__all__ = [
    "DescriptionImpossible",
    "DimensionEmbeddingInvalide",
    "SortieVueVlm",
    "decrire_vue",
    "vectoriser",
]
