"""
@author:  HS

Fichier de tests liés à la configuration des variables d'environnement
"""

import pytest
from pydantic import ValidationError

from config import Config

MINIMAL = {
    "OLLAMA_BASE_URL": "http://10.0.0.5:11434",
    "MODELE_VLM": "qwen3-vl:8b-instruct",
    "MODELE_LLM": "gemma4:26b",
    "MODELE_EMBEDDING": "embeddinggemma",
    "DIMENSION_EMBEDDING": "768",
}


def construire(monkeypatch, tmp_path, **variables):
    """Construit une Config à partir des seules variables fournies."""
    for cle, valeur in {**MINIMAL, **variables}.items():
        monkeypatch.setenv(cle, str(valeur))
    return Config(_env_file=tmp_path / "absent.env")


def test_config_minimale_valide(monkeypatch, tmp_path):
    config = construire(monkeypatch, tmp_path)
    assert config.modele_llm == "gemma4:26b"
    assert config.dimension_embedding == 768
    assert config.nb_vues == 6


def test_variable_obligatoire_manquante(monkeypatch, tmp_path):
    for cle in MINIMAL:
        monkeypatch.setenv(cle, str(MINIMAL[cle]))
    monkeypatch.delenv("MODELE_LLM")
    with pytest.raises(ValidationError, match="modele_llm"):
        Config(_env_file=tmp_path / "absent.env")


def test_url_invalide_refusee(monkeypatch, tmp_path):
    with pytest.raises(ValidationError):
        construire(monkeypatch, tmp_path, OLLAMA_BASE_URL="htp:/fausse_url")


def test_dimension_nulle_refusee(monkeypatch, tmp_path):
    with pytest.raises(ValidationError):
        construire(monkeypatch, tmp_path, DIMENSION_EMBEDDING="0")


def test_surcharge_par_variable_environnement(monkeypatch, tmp_path):
    config = construire(monkeypatch, tmp_path, NB_VUES="4")
    assert config.nb_vues == 4


def test_config_gelee(monkeypatch, tmp_path):
    config = construire(monkeypatch, tmp_path)
    with pytest.raises(ValidationError):
        config.nb_vues = 12