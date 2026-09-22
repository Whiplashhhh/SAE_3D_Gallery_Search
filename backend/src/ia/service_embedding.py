from collections.abc import Callable
import logging

import httpx

LOGGER = logging.getLogger(__name__)


class ServiceEmbedding:
    def __init__(
        self,
        encodeur: Callable[[str], list[float]],
        encodeur_distant: Callable[[str], list[float]] | None = None,
    ):
        self._encodeur = encodeur
        self._encodeur_distant = encodeur_distant

    def encoder(self, texte: str) -> list[float]:
        if self._encodeur_distant is not None:
            try:
                return self._encodeur_distant(texte)
            except (httpx.HTTPError, ValueError) as erreur:
                LOGGER.warning("Embedding Ollama indisponible, fallback local: %s", erreur)
        return self._encodeur(texte)
