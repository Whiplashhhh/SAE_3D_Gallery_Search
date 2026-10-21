"""
@author:  WV

Fichier de tests liés à la sortie du VLM pour une vue
"""
from pathlib import Path

import pytest
from pydantic import ValidationError

from semantique import SortieVueVlm

PROMPT = Path(__file__).parents[2] / "src" / "semantique" / "prompts" / "vue.md"


def exemple():
    return {
        "description": "Assise rouge et dossier ajoure noir vus de face, deux accoudoirs.",
        "elements_visibles": ["assise", "dossier", "accoudoir"],
        "couleurs": ["rouge", "noir"],
        "materiaux": ["plastique"],
    }


def test_exemple_valide_accepte():
    sortie = SortieVueVlm.model_validate(exemple())
    assert sortie.couleurs == ["rouge", "noir"]


def test_schema_interdit_les_champs_supplementaires():
    """Le schéma envoyé à Ollama ne doit pas autoriser de champ en plus"""
    schema = SortieVueVlm.model_json_schema()
    assert schema["additionalProperties"] is False


def test_champ_inconnu_refuse():
    donnees = exemple()
    donnees["face_cachee"] = "probablement un dossier plat"
    with pytest.raises(ValidationError):
        SortieVueVlm.model_validate(donnees)


def test_exemple_incomplet_refuse():
    donnees = exemple()
    del donnees["description"]
    with pytest.raises(ValidationError):
        SortieVueVlm.model_validate(donnees)


def test_prompt_existe():
    """Le prompt doit exister et imposer de ne décrire que le visible"""
    texte = PROMPT.read_text(encoding="utf-8")
    assert "uniquement ce qui est visible" in texte
