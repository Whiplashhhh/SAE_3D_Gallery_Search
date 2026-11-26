"""
@author: WV

Indexation d'un modèle rendu (Lot B) : manifeste du Lot A -> fiche pour le Lot C

Enchaîne decrire_vue() pour chaque vue, fusionner_descriptions() puis
vectoriser(). La fiche n'est écrite qu'à la toute fin, de façon atomique : un
échec à n'importe quelle étape est journalisé et ne laisse aucune fiche partielle
"""

import time
from collections.abc import Iterable
from pathlib import Path

from config import RACINE, Config, obtenir_config
from contrats import (
    VERSION_CONTRATS,
    DescriptionVue,
    DureeMs,
    Embedding,
    FicheModele,
    ManifesteRendu,
    ecrire_json,
    journaliser,
)
from ollama.client import ClientOllama, OllamaErreur
from semantique.fusion import FusionImpossible, fusionner_descriptions
from semantique.vectorisation import DimensionEmbeddingInvalide, vectoriser
from semantique.vue import DescriptionImpossible, decrire_vue

NB_MAX_COULEURS = 10
"""Limite de couleurs_dominantes dans FicheModele."""

ERREURS_INDEXATION = (
    DescriptionImpossible,
    FusionImpossible,
    DimensionEmbeddingInvalide,
    OllamaErreur,
)


def _sans_doublon(valeurs: Iterable[str]) -> list[str]:
    """Retire les doublons (sans tenir compte de la casse) en gardant l'ordre."""
    return list(dict.fromkeys(valeur.strip().lower() for valeur in valeurs))


def _ms_depuis(debut: float) -> int:
    return round((time.perf_counter() - debut) * 1000)


def indexer_modele(
    manifeste: ManifesteRendu,
    client: ClientOllama,
    *,
    config: Config | None = None,
    racine: Path = RACINE,
) -> Path:
    """Produit la fiche du modèle décrit par le manifeste et renvoie son chemin.

    Les chemins du manifeste et dossier_fiches sont relatifs à `racine`.
    throw DescriptionImpossible, FusionImpossible, DimensionEmbeddingInvalide
    ou OllamaErreur si une étape échoue, après avoir écrit l'abandon dans le
    journal. Aucune fiche n'est alors écrite.
    """
    config = config or obtenir_config()
    id_modele = manifeste.id_modele

    try:
        debut = time.perf_counter()
        descriptions = [
            decrire_vue(racine / vue.chemin, client, id_modele=id_modele, config=config)
            for vue in manifeste.vues
        ]
        duree_vlm = _ms_depuis(debut)

        debut = time.perf_counter()
        fusion = fusionner_descriptions(descriptions, client, id_modele=id_modele, config=config)
        duree_llm = _ms_depuis(debut)

        debut = time.perf_counter()
        vecteur = vectoriser(fusion.description, client, config=config)
        duree_embedding = _ms_depuis(debut)
    except ERREURS_INDEXATION as erreur:
        journaliser(
            config.chemin_journal,
            "B",
            "indexation_abandonnee",
            f"{type(erreur).__name__} : {erreur}",
            niveau="erreur",
            id_modele=id_modele,
        )
        raise

    toutes_les_couleurs: list[str] = []
    for description in descriptions:
        toutes_les_couleurs.extend(description.couleurs)
    couleurs = _sans_doublon(toutes_les_couleurs)

    par_vue: list[DescriptionVue] = []
    for vue, description in zip(manifeste.vues, descriptions, strict=True):
        par_vue.append(DescriptionVue(nom=vue.nom, description=description.description))

    fiche = FicheModele(
        version=VERSION_CONTRATS,
        id_modele=id_modele,
        titre=fusion.titre,
        description=fusion.description,
        categorie=fusion.categorie,
        mots_cles=_sans_doublon(fusion.mots_cles),
        couleurs_dominantes=couleurs[:NB_MAX_COULEURS],
        etat=fusion.etat,
        par_vue=par_vue,
        divergences_entre_vues=fusion.divergences_entre_vues,
        embedding=Embedding(
            modele=config.modele_embedding,
            dimension=len(vecteur),
            vecteur=vecteur,
        ),
        duree_ms=DureeMs(vlm=duree_vlm, llm=duree_llm, embedding=duree_embedding),
    )
    return ecrire_json(fiche, racine / config.dossier_fiches / f"{id_modele}.json")
