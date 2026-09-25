"""
@author: HS

Configuration de l'application, lue depuis l'environnement et le .env.

Pas d'URL, pas de nom de modèle, pas de chemin écrit en dur dans le code :
tout passe par ici.
C'est ce qui permet de changer de modèle sans toucher au code.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

RACINE = Path(__file__).resolve().parents[2]
"""Racine du dépot"""


class Config(BaseSettings):
    """Paramètres de l'application.

    Chaque attribut correspond à une variable d'environnement de même nom en
    majuscules : ollama_base_url <- OLLAMA_BASE_URL.
    """

    model_config = SettingsConfigDict(
        env_file=RACINE / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    # Ollama
    ollama_base_url: HttpUrl
    modele_vlm: str
    modele_llm: str
    modele_embedding: str
    ollama_timeout_s: int = Field(default=180, ge=1)
    ollama_tentatives: int = Field(default=3, ge=1, le=10)

    # Mesuré une fois contre l'Ollama de l'IUT (POST /api/embed), jamais deviné.
    dimension_embedding: int = Field(ge=1)

    # Rendu (Lot A)
    blender_bin: str = "blender"
    nb_vues: int = Field(default=6, ge=1, le=24)
    resolution_rendu: int = Field(default=512, ge=64)
    resolution_vignette: int = Field(default=256, ge=32)

    # Chemins
    dossier_modeles: Path = Path("donnees/modeles")
    dossier_rendus: Path = Path("donnees/rendus")
    dossier_fiches: Path = Path("donnees/fiches")
    chemin_chroma: Path = Path("donnees/chroma")
    chemin_journal: Path = Path("donnees/journal/indexation.jsonl")


@lru_cache
def obtenir_config() -> Config:
    """Retourne la configuration, lis le .env une seule fois par processus."""
    return Config()