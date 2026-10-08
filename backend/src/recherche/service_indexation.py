from ..contrats.schemas.fiche import FicheModele
from .chargeur_fiches import ChargeurFiches
from .service_chroma import ServiceChroma


class ServiceIndexation:
    """Synchronise les fiches validées avec les vecteurs et métadonnées Chroma."""

    def __init__(self, chroma: ServiceChroma):
        """Construit le service avec le dépôt vectoriel à mettre à jour."""
        self.chroma = chroma

    def indexer(self, fiche: FicheModele) -> FicheModele:
        """Indexe une fiche avec son vecteur, sa description et ses métadonnées."""
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
        """Retire un modèle de l'index vectoriel."""
        self.chroma.supprimer(identifiant)

    def indexer_fiches(self, chargeur: ChargeurFiches) -> int:
        """Synchronise l'index complet et supprime les identifiants devenus obsolètes.

        Retourne le nombre de fiches chargées et indexées.
        """
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
