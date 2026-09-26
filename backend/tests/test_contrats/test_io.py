"""
@author: WV

Tests pour les fonctions d'entrée/sortie des contrats.
"""

import json
from pathlib import Path

import pytest

from contrats import (
    ContratInvalide,
    charger_manifeste,
    deja_traite,
    ecrire_json,
)

SEED = Path(__file__).parents[2] / "seed" / "manifestes" / "chaise_bureau.json"


def test_aller_retour_conserve_les_donnees(tmp_path):
    """Ecrire puis relire doit redonner un objet identique."""
    origine = charger_manifeste(SEED)
    cible = tmp_path / "sortie" / "manifeste_rendu.json"

    ecrire_json(origine, cible)

    assert charger_manifeste(cible) == origine


def test_cree_les_dossiers_parents(tmp_path):
    manifeste = charger_manifeste(SEED)
    cible = tmp_path / "a" / "b" / "c" / "manifeste_rendu.json"
    ecrire_json(manifeste, cible)
    assert cible.exists()


def test_ne_laisse_pas_de_fichier_temporaire(tmp_path):
    manifeste = charger_manifeste(SEED)
    cible = tmp_path / "manifeste_rendu.json"
    ecrire_json(manifeste, cible)
    assert list(tmp_path.glob("*.tmp")) == []


def test_ecrase_une_sortie_existante(tmp_path):
    manifeste = charger_manifeste(SEED)
    cible = tmp_path / "manifeste_rendu.json"
    cible.write_text("contenu precedent corrompu", encoding="utf-8")

    ecrire_json(manifeste, cible)

    assert charger_manifeste(cible) == manifeste


def test_fichier_invalide_mentionne_le_chemin(tmp_path):
    """Le message d'erreur doit dire QUEL fichier est fautif."""
    donnees = json.loads(SEED.read_text(encoding="utf-8"))
    del donnees["sha256"]
    cible = tmp_path / "casse.json"
    cible.write_text(json.dumps(donnees), encoding="utf-8")

    with pytest.raises(ContratInvalide, match="casse.json"):
        charger_manifeste(cible)


def test_json_malforme_refuse(tmp_path):
    cible = tmp_path / "tronque.json"
    cible.write_text('{"version": "1.0", "id_mod', encoding="utf-8")

    with pytest.raises(ContratInvalide):
        charger_manifeste(cible)


def test_fichier_absent_leve_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        charger_manifeste(tmp_path / "inexistant.json")


def test_deja_traite(tmp_path):
    cible = tmp_path / "fiche.json"
    assert deja_traite(cible) is False
    cible.write_text("{}", encoding="utf-8")
    assert deja_traite(cible) is True
