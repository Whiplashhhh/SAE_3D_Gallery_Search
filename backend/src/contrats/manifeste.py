"""
@author:  WV

Contrat manifeste_rendu.json : Lot A (rendu) -> Lot B (semantique).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Vue(BaseModel):
    """Une prise de vue du modèle 3D."""

    # Contraintes de validation : on met le mode strict (les champs manquants ou erreurs de type ne passeront pas)
    model_config = ConfigDict(extra="forbid", frozen=True)

    nom: str # le nom de la vue (ex : face)
    chemin: str # le chemin relatif où la vue est stockée
    azimut: float
    elevation: float


class ManifesteRendu(BaseModel):
    """Ce que le Lot A produit pour chaque modele 3D rendu."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str # la version du manifeste
    id_modele: str
    fichier_source: str
    sha256: str # identifiant sur 64 caractères hexa
    date_rendu: datetime
    moteur: str
    resolution: tuple[int, int]
    nombre_vues: int
    vues: list[Vue]
    vignette: str # chemin relatif pour l'affichage dans la bibliothèque
