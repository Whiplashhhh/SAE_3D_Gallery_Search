from time import perf_counter

from ..contrats.schemas.fiche import FicheModele
from ..contrats.schemas.recherche import (
    RechercheReponse,
    RechercheRequete,
    ResultatRecherche,
)
from ..ia.service_embedding import ServiceEmbedding
from .chargeur_fiches import ChargeurFiches
from .service_chroma import ServiceChroma


class ServiceRecherche:
    def __init__(
        self,
        chroma: ServiceChroma,
        embeddings: ServiceEmbedding,
        fiches: ChargeurFiches,
    ):
        self.chroma = chroma
        self.embeddings = embeddings
        self.fiches = fiches

    def rechercher(self, requete: RechercheRequete) -> RechercheReponse:
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
                    metadonnees=self._metadonnees(fiche),
                )
            )

        return RechercheReponse(
            resultats=resultats,
            nb_total=len(resultats),
            temps_ms=(perf_counter() - debut) * 1000,
        )

    @staticmethod
    def _metadonnees(fiche: FicheModele) -> dict[str, str]:
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
