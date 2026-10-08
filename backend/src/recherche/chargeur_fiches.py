import json
from pathlib import Path

from ..contrats.schemas.fiche import FicheModele


class ChargeurFiches:
    """Accède aux fiches JSON du Lot B et les valide avec le contrat Pydantic."""

    def __init__(self, dossier: Path | str):
        """Prépare l'accès au dossier contenant les fiches."""
        self.dossier = Path(dossier)

    def charger(self) -> list[FicheModele]:
        """Charge toutes les fiches et vérifie que leur nom correspond à leur identifiant.

        Un dossier absent est traité comme un catalogue vide. Une fiche invalide
        ou un nom de fichier incohérent interrompt le chargement avec une erreur.
        """
        if not self.dossier.exists():
            return []

        fiches: list[FicheModele] = []
        for chemin in sorted(self.dossier.glob("*.json")):
            with chemin.open(encoding="utf-8") as fichier:
                fiche = FicheModele.model_validate(json.load(fichier))
            if chemin.stem != fiche.id_modele:
                raise ValueError(
                    f"Le nom de fichier {chemin.name} doit correspondre à "
                    f"id_modele={fiche.id_modele}."
                )
            fiches.append(fiche)
        return fiches

    def obtenir(self, identifiant: str) -> FicheModele | None:
        """Retourne la fiche identifiée, ou ``None`` si son fichier est absent."""
        chemin = self.dossier / f"{identifiant}.json"
        if not chemin.is_file():
            return None
        with chemin.open(encoding="utf-8") as fichier:
            fiche = FicheModele.model_validate(json.load(fichier))
        if fiche.id_modele != identifiant:
            raise ValueError(
                f"La fiche {chemin.name} contient un id_modele incohérent."
            )
        return fiche

    def compter(self) -> int:
        """Compte les fichiers JSON présents dans le dossier des fiches."""
        return len(list(self.dossier.glob("*.json"))) if self.dossier.exists() else 0

    def supprimer(self, identifiant: str) -> bool:
        """Supprime le fichier d'une fiche et indique s'il existait."""
        chemin = self.dossier / f"{identifiant}.json"
        if not chemin.is_file():
            return False
        chemin.unlink()
        return True
