"""
@author:  WV

Fichier de tests liés au manifeste
"""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from contrats import ManifesteRendu

SEED = Path(__file__).parents[2] / "seed" / "manifestes" / "chaise_bureau.json"

def charger():
    return json.loads(SEED.read_text(encoding="utf-8"))

def test_le_seed_est_valide():
    """Le manifeste de reference du depot doit passer le contrat."""
    manifeste = ManifesteRendu.model_validate(charger())
    assert manifeste.id_modele == "a3f1c2d4e5b60789"
    assert len(manifeste.vues) == 4


def test_champ_inconnu_refuse():
    donnees = charger()
    donnees["vignete"] = "faute_de_frappe.png"
    with pytest.raises(ValidationError):
        ManifesteRendu.model_validate(donnees)


def test_champ_manquant_refuse():
    donnees = charger()
    del donnees["sha256"]
    with pytest.raises(ValidationError):
        ManifesteRendu.model_validate(donnees)


def test_azimut_non_numerique_refuse():
    donnees = charger()
    donnees["vues"][0]["azimut"] = "nord"
    with pytest.raises(ValidationError):
        ManifesteRendu.model_validate(donnees)


def test_id_modele_invalide_refuse():
    donnees = charger()
    donnees["id_modele"] = "pas_un_hex"
    with pytest.raises(ValidationError):
        ManifesteRendu.model_validate(donnees)


def test_chemin_absolu_refuse():
    donnees = charger()
    donnees["vues"][0]["chemin"] = "/tmp/face.png"
    with pytest.raises(ValidationError):
        ManifesteRendu.model_validate(donnees)


def test_nombre_vues_incoherent_refuse():
    donnees = charger()
    donnees["nombre_vues"] = 6 # alors que la liste en contient 4
    with pytest.raises(ValidationError, match="nombre_vues"):
        ManifesteRendu.model_validate(donnees)


def test_id_modele_non_derive_du_sha256_refuse():
    donnees = charger()
    donnees["id_modele"] = "0000000000000000"
    with pytest.raises(ValidationError, match="incoherent avec sha256"):
        ManifesteRendu.model_validate(donnees)


def test_noms_de_vues_en_doublon_refuse():
    donnees = charger()
    donnees["vues"][1]["nom"] = donnees["vues"][0]["nom"]
    with pytest.raises(ValidationError, match="doublon"):
        ManifesteRendu.model_validate(donnees)


def test_liste_de_vues_vide_refuse():
    donnees = charger()
    donnees["vues"] = []
    donnees["nombre_vues"] = 0
    with pytest.raises(ValidationError):
        ManifesteRendu.model_validate(donnees)
