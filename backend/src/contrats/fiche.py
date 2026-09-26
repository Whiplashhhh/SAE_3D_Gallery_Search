"""
@author: HS

Contrat fiche_modele.json : Lot B (sémantique) -> Lot C (recherche).
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from contrats.common import IdModele, MotCle, NomVue, TexteNonVide

EtatModele = Literal[
    "intact",
    "endommage",
    "ruine",
    "incomplet",
    "indetermine"
]
"""Valeurs autorisées pour l'état. Il ne faut pas que le LLM invente ses propres libellés."""

class DescriptionVue(BaseModel):
    """Ce que le VLM a vu sur une seule prise de vue, sans deduction."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    nom: NomVue
    description: TexteNonVide


class Embedding(BaseModel):
    """Le vecteur de la description 360 et sa provenance."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    modele: TexteNonVide
    dimension: int = Field(ge=1)
    vecteur: list[float] = Field(min_length=1)


class DureeMs(BaseModel):
    """Temps d'inférence par étape, en millisecondes (statistiques)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    vlm: int = Field(ge=0)
    llm: int = Field(ge=0)
    embedding: int = Field(ge=0)
    
class FicheModele(BaseModel):
    """La fiche sémantique 360 produit par le Lot B pour un modèle 3D."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str
    id_modele: IdModele
    titre: TexteNonVide = Field(max_length=200)
    description: TexteNonVide
    categorie: MotCle
    mots_cles: list[MotCle] = Field(min_length=1, max_length=30)
    couleurs_dominantes: list[MotCle] = Field(max_length=10)
    etat: EtatModele
    par_vue: list[DescriptionVue] = Field(min_length=1)
    divergences_entre_vues: list[TexteNonVide]
    embedding: Embedding
    duree_ms: DureeMs

    # Règles portant sur plusieurs champs a la fois

    @model_validator(mode="after")
    def _verifier_noms_de_vues_uniques(self) -> "FicheModele":
        """Une vue ne peut apparaitre qu'une fois dans par_vue."""
        noms_vues = [vue.nom for vue in self.par_vue]

        doublons = set()
        for nom in noms_vues:
            if noms_vues.count(nom) > 1:
                doublons.add(nom)

        if doublons:
            raise ValueError(f"noms de vues en doublon dans par_vue : {', '.join(doublons)}")
        return self

    @model_validator(mode="after")
    def _verifier_mots_cles_uniques(self) -> "FicheModele":
        """Des mots-clés dupliqués faussent le filtrage cote Lot C."""
        doublons = set()
        for nom in self.mots_cles:
            if self.mots_cles.count(nom) > 1:
                doublons.add(nom)

        if doublons:
            raise ValueError(f"mots_cles en doublon : {', '.join(doublons)}")
        return self

    @model_validator(mode="after")
    def _verifier_couleurs_dominantes_uniques(self) -> "FicheModele":
        """Des couleurs dominantes dupliquées faussent le filtrage cote Lot C."""
        doublons = set()
        for nom in self.couleurs_dominantes:
            if self.couleurs_dominantes.count(nom) > 1:
                doublons.add(nom)

        if doublons:
            raise ValueError(f"couleurs_dominantes en doublon : {', '.join(doublons)}")
        return self