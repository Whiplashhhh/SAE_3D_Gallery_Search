"""
@author:  WV

Contrat manifeste_rendu.json : Lot A (rendu) -> Lot B (semantique).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from contrats.common import NomVue, CheminRelatif, IdModele, Sha256


class Vue(BaseModel):
    """Une prise de vue du modèle 3D."""

    # Contraintes de validation : on met le mode strict (les champs manquants ou erreurs de type ne passeront pas)
    model_config = ConfigDict(extra="forbid", frozen=True)

    nom: NomVue  # le nom de la vue (ex : face)
    chemin: CheminRelatif  # le chemin relatif où la vue est stockée
    azimut: float
    elevation: float


class ManifesteRendu(BaseModel):
    """Ce que le Lot A produit pour chaque modele 3D rendu."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str  # la version du manifeste
    id_modele: IdModele
    fichier_source: CheminRelatif
    sha256: Sha256  # identifiant sur 64 caractères hexa
    date_rendu: datetime
    moteur: str
    resolution: tuple[int, int]
    nombre_vues: int = Field(ge=1) # au moins un élément
    vues: list[Vue] = Field(min_length=1) # il faut au moins une vue
    vignette: CheminRelatif  # chemin relatif pour l'affichage dans la bibliothèque


    # Règles portant sur plusieurs champs a la fois

    @model_validator(mode="after") # on passe la validation sur plusieurs champs après la création du modèle
    def _verifier_nombre_vues(self) -> "ManifesteRendu":
        """nombre_vues doit correspondre à la taille réelle de la liste."""
        if len(self.vues) != self.nombre_vues:
            raise ValueError(
                f"nombre_vues={self.nombre_vues} mais {len(self.vues)} vue(s) presente(s)"
            )
        return self

    @model_validator(mode="after")
    def _verifier_id_derive_du_sha256(self) -> "ManifesteRendu":
        """id_modele doit être les 16 premiers caractères du sha256."""
        attendu = self.sha256[:16]
        if self.id_modele != attendu:
            raise ValueError(
                f"id_modele='{self.id_modele}' incoherent avec sha256 : attendu '{attendu}'"
            )
        return self

    @model_validator(mode="after")
    def _verifier_noms_de_vues_uniques(self) -> "ManifesteRendu":
        """Deux vues ne peuvent pas porter le meme nom (il sert de nom de fichier)."""
        noms_vues = [vue.nom for vue in self.vues]

        doublons = set()
        for nom in noms_vues:
            if noms_vues.count(nom) > 1:
                doublons.add(nom)

        if doublons:
            raise ValueError(f"noms de vues en doublon : {', '.join(doublons)}")
        return self
