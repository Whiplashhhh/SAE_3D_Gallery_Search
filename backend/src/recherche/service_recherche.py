from time import perf_counter

from contrats import FicheModele

from ..contrats.schemas.recherche import (
    RechercheReponse,
    RechercheRequete,
    ResultatRecherche,
)
from ..ia.service_embedding import ServiceEmbedding
from .chargeur_fiches import ChargeurFiches
from .service_chroma import ServiceChroma

TAILLE_MAX_EXTRAIT = 200


class ServiceRecherche:
    """Coordonne l'encodage d'une requête, ChromaDB et la résolution des fiches."""

    def __init__(
        self,
        chroma: ServiceChroma,
        embeddings: ServiceEmbedding,
        fiches: ChargeurFiches,
    ):
        """Configure les dépendances utilisées pour chaque recherche."""
        self.chroma = chroma
        self.embeddings = embeddings
        self.fiches = fiches

    def rechercher(self, requete: RechercheRequete) -> RechercheReponse:
        """Classe les fiches par similarité et construit la réponse de l'API.

        Les filtres et le nombre maximal de résultats viennent de la requête.
        Les résultats sans fiche correspondante et ceux sous le seuil éventuel
        sont exclus ; le temps mesuré couvre l'ensemble du traitement.
        """
        debut = perf_counter()
        resultats_chroma = self.chroma.rechercher(
            self.embeddings.encoder(requete.texte),
            top_k=requete.top_k,
            filtres={
                "categorie": requete.categorie,
                "couleurs_dominantes": requete.couleur,
            },
        )

        resultats = []
        for identifiant, score in resultats_chroma:
            fiche = self.fiches.obtenir(identifiant)
            if fiche is None or (
                requete.seuil is not None and score < requete.seuil
            ):
                continue
            resultats.append(
                ResultatRecherche(
                    id=fiche.id_modele,
                    score=score,
                    extrait=self._extrait(fiche.description),
                    metadonnees=self._metadonnees(fiche),
                )
            )

        return RechercheReponse(
            resultats=resultats,
            nb_total=len(resultats),
            temps_ms=(perf_counter() - debut) * 1000,
        )

    @staticmethod
    def _extrait(description: str) -> str:
        """Retourne un extrait de la description globale, limité à 200 caractères."""
        if len(description) <= TAILLE_MAX_EXTRAIT:
            return description

        debut = description[: TAILLE_MAX_EXTRAIT - 1]
        dernier_espace = debut.rfind(" ")
        if dernier_espace > 0:
            debut = debut[:dernier_espace]
        return f"{debut.rstrip()}…"

    @staticmethod
    def _metadonnees(fiche: FicheModele) -> dict[str, str]:
        """Adapte les champs de la fiche au format de métadonnées exposé par l'API."""
        couleurs = "|".join(fiche.couleurs_dominantes)
        mots_cles = "|".join(fiche.mots_cles)
        return {
            "nom": fiche.titre,
            "titre": fiche.titre,
            "description": fiche.description,
            "categorie": fiche.categorie,
            "couleur": couleurs,
            "couleurs_dominantes": couleurs,
            "mots_cles": mots_cles,
        }
