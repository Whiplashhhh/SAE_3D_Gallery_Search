"""
@author:  WV

Fichier de tests liés à decrire_vue(), avec un faux client (sans Ollama)
"""
import json

import pytest

from config import Config
from contrats import lire_journal
from semantique import DescriptionImpossible, decrire_vue

VALIDE = json.dumps({
    "description": "Assise rouge vue de face.",
    "elements_visibles": ["assise"],
    "couleurs": ["rouge"],
    "materiaux": [],
})
INVALIDE = json.dumps({"description": "Assise rouge vue de face."})


class FauxClient:
    """Renvoie les réponses données, dans l'ordre, et garde les appels"""

    def __init__(self, *reponses):
        self.reponses = list(reponses)
        self.appels = []

    def chat(self, modele, messages, schema=None, images=None):
        self.appels.append({"modele": modele, "schema": schema, "images": images})
        return self.reponses.pop(0)


@pytest.fixture
def config(monkeypatch, tmp_path):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://10.0.0.5:11434")
    monkeypatch.setenv("MODELE_VLM", "qwen3-vl:8b-instruct")
    monkeypatch.setenv("MODELE_LLM", "gemma4:26b")
    monkeypatch.setenv("MODELE_EMBEDDING", "embeddinggemma")
    monkeypatch.setenv("DIMENSION_EMBEDDING", "768")
    monkeypatch.setenv("OLLAMA_TENTATIVES", "2")
    monkeypatch.setenv("CHEMIN_JOURNAL", str(tmp_path / "indexation.jsonl"))
    return Config(_env_file=tmp_path / "absent.env")


@pytest.fixture
def png(tmp_path):
    chemin = tmp_path / "face.png"
    chemin.write_bytes(b"faux png")
    return chemin


def test_reponse_valide(config, png):
    client = FauxClient(VALIDE)
    sortie = decrire_vue(png, client, config=config)
    assert sortie.couleurs == ["rouge"]
    # Le VLM reçoit le bon modèle, le schéma et l'image
    appel = client.appels[0]
    assert appel["modele"] == "qwen3-vl:8b-instruct"
    assert appel["schema"]["additionalProperties"] is False
    assert appel["images"] == [b"faux png"]


def test_reponse_invalide_puis_valide(config, png):
    client = FauxClient(INVALIDE, VALIDE)
    decrire_vue(png, client, config=config)
    assert len(client.appels) == 2
    journal = lire_journal(config.chemin_journal)
    assert [e.evenement for e in journal] == ["sortie_vlm_invalide_relance"]


def test_echec_apres_toutes_les_tentatives(config, png):
    client = FauxClient(INVALIDE, INVALIDE)
    with pytest.raises(DescriptionImpossible):
        decrire_vue(png, client, config=config)
    journal = lire_journal(config.chemin_journal)
    assert journal[-1].evenement == "description_vue_abandonnee"
    assert journal[-1].niveau == "erreur"
