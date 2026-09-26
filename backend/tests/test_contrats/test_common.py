"""
@author:  AR

Fichier de tests liés aux types communs
"""

import pytest
from pydantic import TypeAdapter, ValidationError

from contrats import CheminRelatif, IdModele, NomVue, Sha256

SHA_VALIDE = "a3f1c2d4e5b607890f4d2c8a91b7e6350d24fa8817cc9b0e6a5d3f21c47b8e9d"


def valider(annotation, valeur):
    """Valide une valeur contre un type annote."""
    return TypeAdapter(annotation).validate_python(valeur)


# Sha256

def test_sha256_accepte_64_hex_minuscules():
    assert valider(Sha256, SHA_VALIDE) == SHA_VALIDE


@pytest.mark.parametrize(
    "valeur",
    [
        SHA_VALIDE[:63],  # trop court
        SHA_VALIDE + "a",  # trop long
        SHA_VALIDE.upper(),  # majuscules
        SHA_VALIDE[:-1] + "z",  # caractere non hex
        "",  # vide
    ],
)
def test_sha256_refuse(valeur):
    with pytest.raises(ValidationError):
        valider(Sha256, valeur)


# IdModele

def test_id_modele_accepte_16_hex():
    assert valider(IdModele, "a3f1c2d4e5b60789") == "a3f1c2d4e5b60789"


@pytest.mark.parametrize(
    "valeur",
    [
        "a3f1c2d4e5b6078",  # trop court
        SHA_VALIDE,  # trop long
        "A3F1C2D4E5B60789",  # majuscules
        ""  # vide
    ]
)
def test_id_modele_refuse(valeur):
    with pytest.raises(ValidationError):
        valider(IdModele, valeur)
        
        
        
        # CheminRelatif

@pytest.mark.parametrize(
    "valeur",
    [
        "donnees/rendus/a3f1c2d4e5b60789/face.png",  #
        "chaise.obj",
        "seed/fiches/maison_ruine.json",
    ],
)
def test_chemin_relatif_accepte(valeur):
    assert valider(CheminRelatif, valeur) == valeur


@pytest.mark.parametrize(
    "valeur",
    [
        "/etc/passwd",  # absolu
        "/donnees/rendus/face.png",  # absolu
        "../../secret.txt",  # remontee
        "donnees/../../secret.txt",  # remontee au milieu
        "",  # vide
        "   ",  # vide apres strip
    ],
)
def test_chemin_relatif_refuse(valeur):
    with pytest.raises(ValidationError):
        valider(CheminRelatif, valeur)


def test_chemin_relatif_nettoie_les_espaces():
    assert valider(CheminRelatif, "  chaise.obj  ") == "chaise.obj"


# NomVue

@pytest.mark.parametrize(
    "valeur",
    [
        "face",
        "arriere",
        "trois_quarts",
        "vue_02"
    ]
)
def test_nom_vue_accepte(valeur):
    assert valider(NomVue, valeur) == valeur


@pytest.mark.parametrize(
    "valeur",
    [
        "arrière",  # accent
        "vue face",  # espace
        "FACE",  # majuscules
        "face/png",  # caractère spécial
        ""  # vide
    ]
)
def test_nom_vue_refuse(valeur):
    with pytest.raises(ValidationError):
        valider(NomVue, valeur)