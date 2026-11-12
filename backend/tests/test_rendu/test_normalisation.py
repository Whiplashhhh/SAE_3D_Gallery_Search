"""
@author: AR

Tests pour normalisation : boîte englobante, centre, diagonale et facteur d'échelle.
"""

import math

import pytest

from rendu.normalisation import TAILLE_CIBLE, boite_englobante, facteur_echelle


def test_boite_englobante_de_plusieurs_pieces():
    coins = [(0, 0, 0), (1, 2, 3), (-1, 5, -2)]

    boite = boite_englobante(coins)

    assert boite.minimum == (-1, 0, -2)
    assert boite.maximum == (1, 5, 3)


def test_dimensions_centre_et_diagonale():
    boite = boite_englobante([(10, 20, 30), (13, 24, 30)])

    assert boite.dimensions == (3, 4, 0)
    assert boite.centre == (11.5, 22, 30)
    assert boite.diagonale == 5


def test_boite_englobante_accepte_un_generateur():
    boite = boite_englobante((i, -i, 0) for i in range(4))
    assert boite.maximum == (3, 0, 0)


def test_boite_englobante_sans_point():
    with pytest.raises(ValueError, match="aucun point"):
        boite_englobante([])


@pytest.mark.parametrize("diagonale", [0.01, 1.0, 5000.0])
def test_facteur_echelle_ramene_a_la_taille_cible(diagonale):
    """Un modèle peut faire 0,01 ou 5000 unités : il finit toujours à TAILLE_CIBLE."""
    assert math.isclose(diagonale * facteur_echelle(diagonale), TAILLE_CIBLE)


def test_facteur_echelle_objet_degenere():
    assert facteur_echelle(0.0) == 1.0
