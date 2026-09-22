from ..contrats.schemas.fiche import FicheModele
from .chargeur_fiches import ChargeurFiches
from .service_chroma import ServiceChroma


class ServiceIndexation:
    def __init__(self, chroma: ServiceChroma):
        self.chroma = chroma

    def indexer(self, fiche: FicheModele) -> FicheModele:
        couleurs = "|".join(fiche.couleurs_dominantes)
        mots_cles = "|".join(fiche.mots_cles)
        self.chroma.indexer(
            fiche.id_modele,
            fiche.embedding.vecteur,
            {
                "id_modele": fiche.id_modele,
                "titre": fiche.titre,
                "categorie": fiche.categorie,
                "couleurs_dominantes": couleurs,
                "mots_cles": mots_cles,
            },
            document=fiche.description,
        )
        return fiche

    def supprimer(self, identifiant: str) -> None:
        self.chroma.supprimer(identifiant)

    def indexer_fiches(self, chargeur: ChargeurFiches) -> int:
        fiches = chargeur.charger()
        identifiants = {fiche.id_modele for fiche in fiches}
        obsoletes = [
            identifiant
            for identifiant in self.chroma.lister_identifiants()
            if identifiant not in identifiants
        ]
        self.chroma.supprimer_plusieurs(obsoletes)
        for fiche in fiches:
            self.indexer(fiche)
        return len(fiches)
