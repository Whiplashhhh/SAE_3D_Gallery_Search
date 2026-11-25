"""
@author: AR

Tests pour arguments : lecture de la ligne de commande passée au script Blender.
"""

import os

import pytest

from rendu.arguments import lire_arguments
from rendu.vues import VUES_DIAGONALES_2

DEBUT = ["blender", "--background", "--python", "script_blender.py", "--"]


def test_valeurs_par_defaut_deux_vues_diagonales():
    arguments = lire_arguments(DEBUT + ["chaise.obj", "sortie"])

    assert arguments.chemin_modele == os.path.abspath("chaise.obj")
    assert arguments.dossier_sortie == os.path.abspath("sortie")
    assert tuple(arguments.vues) == VUES_DIAGONALES_2
    assert arguments.resolution == 512
    assert arguments.resolution_vignette == 0


def test_options_explicites():
    arguments = lire_arguments(
        DEBUT
        + ["chaise.obj", "sortie", "--vues", "arriere_droite_haut, avant_gauche_bas",
           "--resolution", "256", "--vignette", "128"]
    )

    assert [vue.nom for vue in arguments.vues] == ["arriere_droite_haut", "avant_gauche_bas"]
    assert arguments.resolution == 256
    assert arguments.resolution_vignette == 128


def test_ignore_les_arguments_de_blender_avant_le_separateur():
    arguments = lire_arguments(["blender", "--vues", "rien", "--", "a.obj", "b"])
    assert arguments.chemin_modele == os.path.abspath("a.obj")


def test_separateur_absent():
    with pytest.raises(ValueError, match="'--'"):
        lire_arguments(["blender", "--background"])


def test_dossier_de_sortie_manquant():
    with pytest.raises(ValueError, match="invalides"):
        lire_arguments(DEBUT + ["chaise.obj"])


def test_vue_inconnue():
    with pytest.raises(ValueError, match="dessus"):
        lire_arguments(DEBUT + ["chaise.obj", "sortie", "--vues", "dessus"])


def test_liste_de_vues_vide():
    with pytest.raises(ValueError, match="au moins une vue"):
        lire_arguments(DEBUT + ["chaise.obj", "sortie", "--vues", " , "])


def test_resolution_invalide():
    with pytest.raises(ValueError, match="positives"):
        lire_arguments(DEBUT + ["chaise.obj", "sortie", "--resolution", "0"])
