"""
@author: WV

Lecture et écriture des fichiers de contrat.

Règle du projet : la présence du fichier de sortie est le signal de succès.
Il faut que l'écriture soit atomique, d'où ecrire_json().
"""

import os
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from contrats.fiche import FicheModele
from contrats.manifeste import ManifesteRendu

TypeContrat = TypeVar("TypeContrat", bound=BaseModel)


class ContratInvalide(Exception):
    """Un fichier de contrat existe mais ne respecte pas son schema."""


# Lecture

def charger(modele: type[TypeContrat], chemin: Path) -> TypeContrat:
    """Lit un JSON et le valide contre le modèle donné.

    FileNotFoundError si absent, ContratInvalide si le contenu est mauvais.
    """
    contenu = Path(chemin).read_text(encoding="utf-8")
    try:
        return modele.model_validate_json(contenu)
    except ValidationError as erreur:
        raise ContratInvalide(f"{chemin} : {erreur}") from erreur


def charger_manifeste(chemin: Path) -> ManifesteRendu:
    """Charge un manifeste_rendu.json (entrée du Lot B)."""
    return charger(ManifesteRendu, chemin)


def charger_fiche(chemin: Path) -> FicheModele:
    """Charge une fiche_modele.json (entrée du Lot C)."""
    return charger(FicheModele, chemin)



# écriture

def ecrire_json(objet: BaseModel, chemin: Path) -> Path:
    """écrit un contrat en JSON de facon atomique.

    On écrit d'abord dans un fichier temporaire du même dossier, puis on le
    renomme.
    os.replace() est atomique : le fichier final n'existe jamais à moitié
    écrit. Un plantage en cours de route laisse au pire un .tmp seul,
    jamais un fichier de sortie incomplet qui passerait pour un succès.
    """
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    # Le fichier temporaire est créé dans le même dossier pour que
    # os.replace() puisse effectuer un remplacement atomique.
    tmp = chemin.with_suffix(chemin.suffix + ".tmp")

    try:
        with tmp.open("w", encoding="utf-8") as fichier:
            fichier.write(objet.model_dump_json(indent=2))

            # Vide le tampon Python vers le système d'exploitation.
            fichier.flush()

            # S'assure que les données sont réellement écrites sur le disque.
            os.fsync(fichier.fileno())

        # Le fichier final n'est remplacé qu'une fois l'écriture terminée.
        os.replace(tmp, chemin)
    except BaseException:
        # Supprime le fichier temporaire en cas d'interruption ou d'erreur,
        # puis conserve l'erreur d'origine.
        tmp.unlink(missing_ok=True)
        raise

    return chemin


# Cache

def deja_traite(chemin: Path) -> bool:
    """Vrai si la sortie existe deja : le travail peut être sauté."""
    return Path(chemin).exists()