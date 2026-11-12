"""
@author: AR

Calculs de normalisation d'un modèle : boîte englobante, centre et facteur d'échelle.

Python pur (sans bpy) : le script Blender lui passe les coins des boîtes de
chaque pièce, déjà en coordonnées monde.
"""

import math
from typing import Iterable, NamedTuple

Point = tuple[float, float, float]


TAILLE_CIBLE: float = 2.0
"""Diagonale imposée à tous les modèles après normalisation (en unités Blender)."""


class BoiteEnglobante(NamedTuple):
    minimum: Point
    maximum: Point

    @property
    def dimensions(self) -> Point:
        return tuple(self.maximum[i] - self.minimum[i] for i in range(3))

    @property
    def centre(self) -> Point:
        return tuple((self.minimum[i] + self.maximum[i]) / 2.0 for i in range(3))

    @property
    def diagonale(self) -> float:
        return math.sqrt(sum(d ** 2 for d in self.dimensions))


def boite_englobante(coins: Iterable[Point]) -> BoiteEnglobante:
    """Boîte alignée sur les axes qui contient tous les points donnés."""
    minimum = [float("inf")] * 3
    maximum = [float("-inf")] * 3

    for coin in coins:
        for i in range(3):
            minimum[i] = min(minimum[i], coin[i])
            maximum[i] = max(maximum[i], coin[i])

    if minimum[0] == float("inf"):
        raise ValueError("aucun point : impossible de calculer une boîte englobante")

    return BoiteEnglobante(tuple(minimum), tuple(maximum))


def facteur_echelle(diagonale: float, taille_cible: float = TAILLE_CIBLE) -> float:
    """Facteur à appliquer pour ramener la diagonale à taille_cible.
    Un objet plat (diagonale nulle) n'est pas redimensionné."""
    if diagonale <= 0:
        return 1.0
    return taille_cible / diagonale
