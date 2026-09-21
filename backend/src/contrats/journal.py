"""
@author : AR

Un fichier JSONL append-only (une ligne JSON par événement)

Particularité de ce module : il ne doit jamais faire échouer le programme
qu'il observe.
C'est le contraire de io.py qui refuse d'écrire au moindre doute
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from contrats.common import CodeEvenement, IdModele, TexteNonVide

Lot = Literal["A", "B", "C"]
"""Qui écrit la ligne : 
A = rendu, 
B = sémantique, 
C = recherche."""

Niveau = Literal["info", "avertissement", "erreur"]
"""info = déroulement normal,
avertissement = dégrade mais on continue,
erreur = le traitement de ce modèle est abandonne."""


def _maintenant() -> datetime:
    """Horodatage UTC, toujours avec fuseau"""
    return datetime.now(timezone.utc)


class EntreeJournal(BaseModel):
    """Une ligne du journal"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    horodatage: datetime = Field(default_factory=_maintenant)
    lot: Lot
    id_modele: IdModele | None = None
    niveau: Niveau = "info"
    evenement: CodeEvenement
    message: TexteNonVide


# écriture

def journaliser(
    chemin: Path,
    lot: Lot,
    evenement: CodeEvenement,
    message: str,
    *,
    niveau: Niveau = "info",
    id_modele: str | None = None,
) -> None:
    """Ajoute une ligne au journal. Ne lève jamais d'exception.

    Le mode "a" garantit que chaque écriture se place à la fin du fichier, même
    si les trois lots tournent en parallèle. Une ligne = un seul appel a
    write(), ce qui évite que deux événements se mélangent.
    """
    try:
        entree = EntreeJournal(
            lot=lot,
            id_modele=id_modele,
            niveau=niveau,
            evenement=evenement,
            message=message,
        )
        chemin = Path(chemin)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        with chemin.open("a", encoding="utf-8") as fichier:
            fichier.write(entree.model_dump_json() + "\n")
    except Exception as erreur:
        # Dernier recours : on ne perd pas l'information, on ne bloque rien
        print(
            f"[journal indisponible] {lot}/{evenement} : {message} ({erreur})",
            file=sys.stderr,
        )


# Lecture

def lire_journal(chemin: Path) -> list[EntreeJournal]:
    """Relit le journal en ignorant les lignes illisibles.

    Tolérant par construction : une interruption pendant l'écriture peut laisser
    une dernière ligne tronquée. Elle ne doit pas empécher de lire les autres.
    """
    chemin = Path(chemin)
    if not chemin.exists():
        return []

    entrees: list[EntreeJournal] = []
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        if not ligne.strip():
            continue
        try:
            entrees.append(EntreeJournal.model_validate_json(ligne))
        except (ValidationError, json.JSONDecodeError):
            continue
    return entrees