"""
@author:  AR

Fichier de tests liés au journal
"""

from datetime import timezone
from pathlib import Path

from contrats import EntreeJournal, journaliser, lire_journal


def test_ecrit_une_ligne_par_appel(tmp_path):
    chemin = tmp_path / "journal" / "indexation.jsonl"

    journaliser(chemin, "A", "rendu_termine", "4 vues generees")
    journaliser(chemin, "B", "fiche_ecrite", "synthese 360 produite")

    assert len(chemin.read_text(encoding="utf-8").splitlines()) == 2
    assert len(lire_journal(chemin)) == 2


def test_conserve_les_champs(tmp_path):
    chemin = tmp_path / "indexation.jsonl"
    journaliser(
        chemin, "B", "json_malforme_relance", "Sortie VLM non parsable",
        niveau="avertissement", id_modele="a3f1c2d4e5b60789",
    )

    entree = lire_journal(chemin)[0]
    assert entree.lot == "B"
    assert entree.niveau == "avertissement"
    assert entree.id_modele == "a3f1c2d4e5b60789"
    assert entree.horodatage.tzinfo is not None


def test_horodatage_automatique(tmp_path):
    chemin = tmp_path / "indexation.jsonl"
    journaliser(chemin, "A", "demarrage", "ok")
    assert lire_journal(chemin)[0].horodatage.tzinfo == timezone.utc


def test_id_modele_facultatif(tmp_path):
    chemin = tmp_path / "indexation.jsonl"
    journaliser(chemin, "B", "ollama_injoignable", "connexion refusee", niveau="erreur")
    assert lire_journal(chemin)[0].id_modele is None


def test_message_multiligne_reste_sur_une_ligne(tmp_path):
    """Un message avec retour a la ligne ne doit pas casser le format JSONL."""
    chemin = tmp_path / "indexation.jsonl"
    journaliser(chemin, "B", "trace_erreur", "ligne 1\nligne 2\nligne 3")

    assert len(chemin.read_text(encoding="utf-8").splitlines()) == 1
    assert lire_journal(chemin)[0].message == "ligne 1\nligne 2\nligne 3"


def test_ne_plante_pas_si_le_journal_est_inaccessible(tmp_path, capsys):
    """Un journal indisponible se replie sur stderr, sans exception."""
    obstacle = tmp_path / "obstacle"
    obstacle.write_text("je suis un fichier, pas un dossier", encoding="utf-8")

    journaliser(obstacle / "indexation.jsonl", "A", "rendu_termine", "ok")

    assert "journal indisponible" in capsys.readouterr().err


def test_evenement_invalide_ne_plante_pas(tmp_path, capsys):
    chemin = tmp_path / "indexation.jsonl"
    journaliser(chemin, "A", "Rendu Termine !", "code avec majuscules et espaces")

    assert lire_journal(chemin) == []
    assert "journal indisponible" in capsys.readouterr().err


def test_ligne_tronquee_ignoree(tmp_path):
    """Une interruption peut laisser une derniere ligne incomplete."""
    chemin = tmp_path / "indexation.jsonl"
    journaliser(chemin, "A", "rendu_termine", "ok")
    with chemin.open("a", encoding="utf-8") as fichier:
        fichier.write('{"lot": "B", "evene')

    assert len(lire_journal(chemin)) == 1


def test_journal_absent_retourne_liste_vide(tmp_path):
    assert lire_journal(tmp_path / "rien.jsonl") == []