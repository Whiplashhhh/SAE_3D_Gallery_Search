from collections.abc import Callable

import httpx


class ClientOllama:
    def __init__(self, base_url: str, modele_embedding: str, timeout_s: float = 10):
        self.base_url = base_url.rstrip("/")
        self.modele_embedding = modele_embedding
        self.timeout_s = timeout_s

    def embed(self, texte: str) -> list[float]:
        response = httpx.post(
            f"{self.base_url}/api/embed",
            json={"model": self.modele_embedding, "input": texte},
            timeout=self.timeout_s,
        )
        response.raise_for_status()
        payload = response.json()
        embeddings = payload.get("embeddings")
        if not isinstance(embeddings, list) or not embeddings:
            raise ValueError("Réponse Ollama /api/embed invalide.")
        vecteur = embeddings[0]
        if not isinstance(vecteur, list) or not vecteur:
            raise ValueError("Vecteur Ollama vide.")
        return [float(valeur) for valeur in vecteur]

    def est_joignable(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=self.timeout_s)
            return response.is_success
        except httpx.HTTPError:
            return False
