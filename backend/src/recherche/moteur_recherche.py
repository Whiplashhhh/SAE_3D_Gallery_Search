from time import perf_counter

from ..contrats.schemas.recherche import RechercheRequete, RechercheReponse, ResultatRecherche
from .depot_vectoriel import DepotVectoriel


class MoteurRecherche:
    def __init__(self, depot: DepotVectoriel, vectoriser_texte):
        self.depot = depot
        self.vectoriser_texte = vectoriser_texte

    def peupler_modeles_demo(self):
        self.depot.seed_demo_models(self.vectoriser_texte)

    def rechercher(self, requete: RechercheRequete) -> RechercheReponse:
        t0 = perf_counter()
        vecteur = self.vectoriser_texte(requete.texte)

        filtres = {
            "categorie": requete.categorie,
            "couleur": requete.couleur,
            "format_fichier": requete.format_fichier,
        }
        bruts = self.depot.query(vecteur, top_k=requete.top_k, filtres=filtres)

        resultats: list[ResultatRecherche] = []
        ids = bruts.get("ids", [[]])[0]
        distances = bruts.get("distances", [[]])[0]
        metadatas = bruts.get("metadatas", [[]])[0]

        for id_, dist, meta in zip(ids, distances, metadatas):
            try:
                score = max(0.0, min(1.0, 1.0 - float(dist)))
            except (TypeError, ValueError):
                continue

            if requete.seuil is not None and score < requete.seuil:
                continue
            resultats.append(ResultatRecherche(id=id_, score=score, metadonnees=meta or {}))

        return RechercheReponse(
            resultats=resultats,
            nb_total=len(resultats),
            temps_ms=(perf_counter() - t0) * 1000,
        )