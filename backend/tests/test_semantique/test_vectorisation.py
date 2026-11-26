"""
@author: WV

Fichier de tests liés à vectoriser(), avec un faux client (sans Ollama)
"""
import pytest

from config import Config
from semantique import DimensionEmbeddingInvalide, vectoriser


class FauxClient:
    """Renvoie le vecteur donné et garde les textes reçus"""

    def __init__(self, vecteur):
        self.vecteur = vecteur
        self.appels = []

    def embed(self, textes):
        self.appels.append(textes)
        return self.vecteur


@pytest.fixture
def config(monkeypatch, tmp_path):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://10.0.0.5:11434")
    monkeypatch.setenv("MODELE_VLM", "qwen3-vl:8b-instruct")
    monkeypatch.setenv("MODELE_LLM", "gemma4:26b")
    monkeypatch.setenv("MODELE_EMBEDDING", "embeddinggemma")
    monkeypatch.setenv("DIMENSION_EMBEDDING", "4")
    return Config(_env_file=tmp_path / "absent.env")


def test_bonne_dimension(config):
    client = FauxClient([0.1, 0.2, 0.3, 0.4])
    vecteur = vectoriser("Chaise de bureau rouge.", client, config=config)
    assert vecteur == [0.1, 0.2, 0.3, 0.4]
    # Un seul texte envoyé, tel quel
    assert client.appels == ["Chaise de bureau rouge."]


def test_mauvaise_dimension(config):
    client = FauxClient([0.1, 0.2, 0.3])
    with pytest.raises(DimensionEmbeddingInvalide) as erreur:
        vectoriser("Chaise de bureau rouge.", client, config=config)
    assert erreur.value.recue == 3
    assert erreur.value.attendue == 4
    # Le message indique les deux dimensions
    assert "3" in str(erreur.value)
    assert "4" in str(erreur.value)


@pytest.mark.parametrize("texte", ["", "   \n"])
def test_texte_vide(config, texte):
    client = FauxClient([0.1, 0.2, 0.3, 0.4])
    with pytest.raises(ValueError):
        vectoriser(texte, client, config=config)
    # Aucun appel à Ollama
    assert client.appels == []
