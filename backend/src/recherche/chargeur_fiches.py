import json
from pathlib import Path

from ..contrats.schemas.fiche import FicheModele


class ChargeurFiches:
    def __init__(self, dossier: Path | str):
        self.dossier = Path(dossier)

    def charger(self) -> list[FicheModele]:
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
        return len(list(self.dossier.glob("*.json"))) if self.dossier.exists() else 0

    def supprimer(self, identifiant: str) -> bool:
        chemin = self.dossier / f"{identifiant}.json"
        if not chemin.is_file():
            return False
        chemin.unlink()
        return True
