"""
@author:  HS

Fichier de tests liés aux fiches
"""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from contrats.fiche import FicheModele

SEED = Path(__file__).parents[2] / "seed" / "fiches" / "chaise_bureau.json"


def charger():
    return json.loads(SEED.read_text(encoding="utf-8"))


def test_le_seed_est_valide():
    fiche = FicheModele.model_validate(charger())
    assert fiche.id_modele == "a3f1c2d4e5b60789"
    assert fiche.divergences_entre_vues == []


def test_dimension_invalide_refuse():
    donnees = charger()
    donnees["embedding"]["dimension"] = 0
    with pytest.raises(ValidationError, match="dimension"):
        FicheModele.model_validate(donnees)


def test_etat_inconnu_refuse():
    donnees = charger()
    donnees["etat"] = "un peu abime"
    with pytest.raises(ValidationError):
        FicheModele.model_validate(donnees)


def test_mots_cles_normalises_en_minuscules():
    donnees = charger()
    donnees["mots_cles"] = ["Chaise", "  BUREAU  "]
    fiche = FicheModele.model_validate(donnees)
    assert fiche.mots_cles == ["chaise", "bureau"]


def test_mots_cles_en_doublon_refuse():
    donnees = charger()
    donnees["mots_cles"] = ["chaise", "Chaise"]   # doublon apres normalisation
    with pytest.raises(ValidationError, match="doublon"):
        FicheModele.model_validate(donnees)

def test_couleurs_en_doublon_refuse():
    donnees = charger()
    donnees["couleurs_dominantes"] = ["rouge", "Rouge"]   # doublon apres normalisation
    with pytest.raises(ValidationError, match="doublon"):
        FicheModele.model_validate(donnees)


def test_par_vue_vide_refuse():
    donnees = charger()
    donnees["par_vue"] = []
    with pytest.raises(ValidationError):
        FicheModele.model_validate(donnees)


def test_divergences_vides_acceptees():
    donnees = charger()
    donnees["divergences_entre_vues"] = []
    assert FicheModele.model_validate(donnees).divergences_entre_vues == []


def test_description_vide_refuse():
    donnees = charger()
    donnees["par_vue"][0]["description"] = "   "
    with pytest.raises(ValidationError):
        FicheModele.model_validate(donnees)