from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

import httpx


class OllamaErreur(RuntimeError):
    """Exception métier levée quand Ollama ne répond pas correctement."""


class ClientOllama:
    """Client HTTP minimal pour les opérations Ollama utilisées par l'API."""

    def __init__(
        self,
        base_url: str,
        modele_embedding: str,
        timeout_s: float = 10,
        tentatives: int = 3,
        http_client: httpx.Client | None = None,
    ):
        """Mémorise l'URL du serveur, le modèle d'embedding et le délai maximal."""
        self.base_url = base_url.rstrip("/")
        self.modele_embedding = modele_embedding
        self.timeout_s = float(timeout_s)
        self.tentatives = max(1, int(tentatives))
        self._client = http_client or httpx.Client()

    def __enter__(self) -> "ClientOllama":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self._client.close()
        return False

    def _requete_json(self, methode: str, chemin: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Effectue une requête avec relance automatique en cas d'échec temporaire."""
        dernier_erreur: Exception | None = None
        for essai in range(1, self.tentatives + 1):
            try:
                reponse = self._client.request(
                    methode,
                    f"{self.base_url}{chemin}",
                    json=payload,
                    timeout=self.timeout_s,
                )
                reponse.raise_for_status()
                return reponse.json()
            except (httpx.HTTPError, ValueError, json.JSONDecodeError) as erreur:
                dernier_erreur = erreur
                if essai == self.tentatives:
                    break
        raise OllamaErreur(
            f"Échec de la requête Ollama {methode} {chemin} après {self.tentatives} tentative(s)."
        ) from dernier_erreur

    def embed(self, textes: str | Sequence[str]) -> list[float] | list[list[float]]:
        """Demande des embeddings à Ollama et valide leur structure.

        La méthode accepte un texte unique ou une suite de textes. Une seule
        chaîne renvoie un vecteur simple ; plusieurs entrées renvoient une liste
        de vecteurs. Les erreurs HTTP/JSON déclenchent les tentatives puis une
        exception métier.
        """
        if isinstance(textes, str):
            donnees = [textes]
            mode_unique = True
        else:
            donnees = list(textes)
            mode_unique = False

        payload = {"model": self.modele_embedding, "input": donnees if not mode_unique else donnees[0]}
        reponse = self._requete_json("POST", "/api/embed", payload)
        embeddings = reponse.get("embeddings")
        if not isinstance(embeddings, list) or not embeddings:
            raise OllamaErreur("Réponse Ollama /api/embed invalide : embeddings absent.")

        if mode_unique:
            vecteur = embeddings[0]
            if not isinstance(vecteur, list) or not vecteur:
                raise OllamaErreur("Réponse Ollama /api/embed invalide : vecteur vide.")
            return [float(valeur) for valeur in vecteur]

        resultat: list[list[float]] = []
        for vecteur in embeddings:
            if not isinstance(vecteur, list) or not vecteur:
                raise OllamaErreur("Réponse Ollama /api/embed invalide : un vecteur est vide.")
            resultat.append([float(valeur) for valeur in vecteur])
        return resultat

    def chat(
        self,
        modele: str,
        messages: Sequence[dict[str, Any]],
        schema: Any | None = None,
        images: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Envoie un message à l'API de chat Ollama en mode JSON structuré."""
        payload: dict[str, Any] = {
            "model": modele,
            "messages": list(messages),
            "stream": False,
        }
        if schema is not None:
            if hasattr(schema, "model_json_schema"):
                payload["format"] = schema.model_json_schema()
            else:
                payload["format"] = schema
        if images is not None:
            payload["images"] = list(images)
        return self._requete_json("POST", "/api/chat", payload)

    def est_joignable(self) -> bool:
        """Indique si l'endpoint Ollama répond avec un statut HTTP de succès."""
        try:
            reponse = self._client.get(f"{self.base_url}/api/tags", timeout=self.timeout_s)
            return reponse.is_success
        except httpx.HTTPError:
            return False
