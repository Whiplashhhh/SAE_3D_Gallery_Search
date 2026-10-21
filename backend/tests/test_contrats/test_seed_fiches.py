from pathlib import Path

import pytest

from contrats.io import charger_fiche

DOSSIER_FICHES = Path(__file__).parents[2] / "seed" / "fiches"
FICHIERS_ATTENDUS = {
    "chaise_bureau.json",
    "maison.json",
    "voiture.json",
    "arbre.json",
    "epee.json",
}
FICHIERS_FICHES = sorted(DOSSIER_FICHES.glob("*.json"))


def test_le_dossier_contient_les_cinq_themes_attendus():
    assert {chemin.name for chemin in FICHIERS_FICHES} == FICHIERS_ATTENDUS


@pytest.mark.parametrize("chemin", FICHIERS_FICHES, ids=lambda chemin: chemin.stem)
def test_les_fiches_de_demo_respectent_le_contrat(chemin: Path):
    assert charger_fiche(chemin).id_modele
