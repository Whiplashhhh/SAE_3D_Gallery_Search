from pathlib import Path

import chromadb


class ServiceChroma:
    """Encapsule le stockage persistant et les requêtes de similarité ChromaDB."""

    def __init__(
        self,
        chemin_persist: Path | str,
        nom_collection: str = "modeles_3d_lot_c",
    ):
        """Ouvre ou crée la collection Chroma persistée dans ``chemin_persist``."""
        self.chemin_persist = Path(chemin_persist)
        self.chemin_persist.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.chemin_persist))
        self.collection = self.client.get_or_create_collection(
            name=nom_collection,
            metadata={"hnsw:space": "cosine"},
        )

    def indexer(
        self,
        identifiant_modele: str,
        vecteur: list[float],
        metadonnees: dict[str, str] | None = None,
        document: str | None = None,
    ) -> None:
        """Insère ou remplace un vecteur, ses métadonnées et son document associé."""
        donnees: dict[str, list] = {
            "ids": [identifiant_modele],
            "embeddings": [vecteur],
            "metadatas": [metadonnees or {}],
        }
        if document is not None:
            donnees["documents"] = [document]
        self.collection.upsert(
            **donnees,
        )

    def supprimer(self, identifiant_modele: str) -> None:
        """Supprime de la collection le modèle correspondant à son identifiant."""
        self.collection.delete(ids=[identifiant_modele])

    def supprimer_plusieurs(self, identifiants: list[str]) -> None:
        """Supprime plusieurs modèles ; ne contacte pas Chroma si la liste est vide."""
        if identifiants:
            self.collection.delete(ids=identifiants)

    def rechercher(
        self,
        vecteur: list[float],
        top_k: int = 10,
        filtres: dict[str, str | None] | None = None,
    ) -> list[tuple[str, float]]:
        """Retourne les meilleurs identifiants et leurs scores de similarité.

        Les filtres vides sont ignorés. Chroma renvoie une distance cosinus,
        convertie ici en score (``1 - distance``) puis bornée dans ``[0, 1]``.
        """
        where = {
            cle: valeur
            for cle, valeur in (filtres or {}).items()
            if valeur is not None and valeur != ""
        }
        resultat = self.collection.query(
            query_embeddings=[vecteur],
            n_results=max(1, top_k),
            where=where or None,
            include=["distances"],
        )
        ids = resultat.get("ids", [[]])[0]
        distances = resultat.get("distances", [[]])[0]
        return [(identifiant, max(0.0, min(1.0, 1.0 - float(distance)))) for identifiant, distance in zip(ids, distances)]

    def compter(self) -> int:
        """Retourne le nombre de vecteurs stockés dans la collection."""
        return int(self.collection.count())

    def lister_identifiants(self) -> list[str]:
        """Retourne tous les identifiants stockés, sans charger les vecteurs."""
        resultat = self.collection.get(include=[])
        return [str(identifiant) for identifiant in resultat.get("ids", [])]
