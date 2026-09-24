import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Configuration:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    modele_embedding: str = os.getenv("MODELE_EMBEDDING", "embeddinggemma")
    ollama_timeout_s: float = float(os.getenv("OLLAMA_TIMEOUT_S", "10"))
    dossier_fiches: str = os.getenv("DOSSIER_FICHES", "../donnees/fiches")
