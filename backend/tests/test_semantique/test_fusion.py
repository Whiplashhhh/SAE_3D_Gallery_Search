"""
@author:  WV

Fichier de tests liés à fusionner_descriptions(), avec un faux client (sans Ollama)
"""
import json

import pytest

from config import Config
from contrats import lire_journal
from semantique import FusionImpossible, SortieVueVlm, fusionner_descriptions

VALIDE = json.dumps({
    "description": "Chaise de bureau rouge à roulettes, avec un dossier haut.",
    "divergences_entre_vues": ["La vue de face montre 4 roulettes, la vue de dessus 5."],
})
INVALIDE = json.dumps({"description": "Chaise de bureau rouge."})


class FauxClient:
    """Renvoie les réponses données, dans l'ordre, et garde les appels"""

    def __init__(self, *reponses):
        self.reponses = list(reponses)
        self.appels = []

    def chat(self, modele, messages, schema=None, images=None):
        self.appels.append(
            {"modele": modele, "messages": messages, "schema": schema, "images": images}
        )
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
def descriptions():
    return [
        SortieVueVlm(
            description="Chaise rouge vue de face.",
            elements_visibles=["dossier", "roulette"],
            couleurs=["rouge"],
            materiaux=["tissu"],
        ),
        SortieVueVlm(
            description="Chaise vue de dessus.",
            elements_visibles=["assise"],
            couleurs=["rouge", "noir"],
            materiaux=[],
        ),
    ]


def test_reponse_valide(config, descriptions):
    client = FauxClient(VALIDE)
    sortie = fusionner_descriptions(descriptions, client, config=config)
    assert sortie.description.startswith("Chaise de bureau rouge")
    assert len(sortie.divergences_entre_vues) == 1
    # Le LLM (pas le VLM) reçoit le schéma strict, sans image
    appel = client.appels[0]
    assert appel["modele"] == "gemma4:26b"
    assert appel["schema"]["additionalProperties"] is False
    assert appel["images"] is None
    # Toutes les vues sont envoyées au LLM
    message_utilisateur = appel["messages"][-1]["content"]
    assert "Chaise rouge vue de face." in message_utilisateur
    assert "Chaise vue de dessus." in message_utilisateur


def test_reponse_invalide_puis_valide(config, descriptions):
    client = FauxClient(INVALIDE, VALIDE)
    fusionner_descriptions(descriptions, client, config=config)
    assert len(client.appels) == 2
    journal = lire_journal(config.chemin_journal)
    assert [e.evenement for e in journal] == ["sortie_llm_invalide_relance"]
    assert journal[0].niveau == "avertissement"


def test_echec_apres_toutes_les_tentatives(config, descriptions):
    client = FauxClient(INVALIDE, INVALIDE)
    with pytest.raises(FusionImpossible):
        fusionner_descriptions(descriptions, client, config=config)
    assert len(client.appels) == config.ollama_tentatives
    journal = lire_journal(config.chemin_journal)
    assert journal[-1].evenement == "fusion_abandonnee"
    assert journal[-1].niveau == "erreur"


def test_liste_vide_refusee_sans_appel(config):
    client = FauxClient()
    with pytest.raises(ValueError):
        fusionner_descriptions([], client, config=config)
    assert client.appels == []
