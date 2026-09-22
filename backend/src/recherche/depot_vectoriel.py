from pathlib import Path

from .service_chroma import ServiceChroma


class DepotVectoriel(ServiceChroma):
    """Façade de compatibilité vers le service ChromaDB."""

    def upsert(self, id: str, vecteur: list[float], metadonnees: dict, document: str = ""):
        self.indexer(id, vecteur, metadonnees)

    def query(self, vecteur: list[float], top_k: int = 10, filtres: dict | None = None):
        resultats = self.rechercher(vecteur, top_k, filtres)
        return {
            "ids": [[identifiant for identifiant, _ in resultats]],
            "distances": [[1 - score for _, score in resultats]],
            "metadatas": [[{} for _ in resultats]],
        }

    def get(self, id: str):
        result = self.collection.get(ids=[id])
        return result if result.get("ids") else None

    def stats(self) -> int:
        return self.compter()
