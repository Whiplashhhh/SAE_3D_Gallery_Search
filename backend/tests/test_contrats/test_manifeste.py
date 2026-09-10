import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from contrats.manifeste import ManifesteRendu

SEED = Path(__file__).parents[2] / "seed" / "manifestes" / "chaise_bureau.json"


def test_le_seed_est_valide():
    """Le manifeste de reference du depot doit passer le contrat."""
    manifeste = ManifesteRendu.model_validate_json(SEED.read_text(encoding="utf-8"))
    assert manifeste.id_modele == "a3f1c2d4e5b60789"
    assert len(manifeste.vues) == 4


def test_champ_inconnu_refuse():
    donnees = json.loads(SEED.read_text(encoding="utf-8"))
    donnees["vignete"] = "faute_de_frappe.png"
    with pytest.raises(ValidationError):
        ManifesteRendu.model_validate(donnees)


def test_champ_manquant_refuse():
    donnees = json.loads(SEED.read_text(encoding="utf-8"))
    del donnees["sha256"]
    with pytest.raises(ValidationError):
        ManifesteRendu.model_validate(donnees)


def test_azimut_non_numerique_refuse():
    donnees = json.loads(SEED.read_text(encoding="utf-8"))
    donnees["vues"][0]["azimut"] = "nord"
    with pytest.raises(ValidationError):
        ManifesteRendu.model_validate(donnees)