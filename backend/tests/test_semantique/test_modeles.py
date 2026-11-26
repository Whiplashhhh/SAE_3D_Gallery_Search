"""
@author:  WV

Fichier de tests liés à la sortie du VLM pour une vue
"""
from pathlib import Path

import pytest
from pydantic import ValidationError

from semantique import SortieVueVlm
from semantique.modeles import SortieFusionLlm

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


# Sortie du LLM après fusion des vues

def exemple_fusion():
    return {
        "titre": "Chaise de bureau rouge",
        "description": "Chaise de bureau rouge à roulettes, avec un dossier haut.",
        "categorie": "mobilier",
        "mots_cles": ["chaise", "bureau"],
        "etat": "intact",
        "divergences_entre_vues": ["La vue de face montre 4 roulettes, la vue de dessus 5."],
    }


def test_fusion_exemple_valide_accepte():
    sortie = SortieFusionLlm.model_validate(exemple_fusion())
    assert len(sortie.divergences_entre_vues) == 1


def test_fusion_sans_divergence_acceptee():
    donnees = exemple_fusion()
    donnees["divergences_entre_vues"] = []
    assert SortieFusionLlm.model_validate(donnees).divergences_entre_vues == []


def test_fusion_schema_interdit_les_champs_supplementaires():
    assert SortieFusionLlm.model_json_schema()["additionalProperties"] is False


def test_fusion_champ_inconnu_refuse():
    donnees = exemple_fusion()
    donnees["prix"] = "12 euros"
    with pytest.raises(ValidationError):
        SortieFusionLlm.model_validate(donnees)


def test_fusion_etat_hors_liste_refuse():
    donnees = exemple_fusion()
    donnees["etat"] = "neuf"
    with pytest.raises(ValidationError):
        SortieFusionLlm.model_validate(donnees)


@pytest.mark.parametrize(
    "champ",
    ["titre", "description", "categorie", "mots_cles", "etat", "divergences_entre_vues"],
)
def test_fusion_champ_manquant_refuse(champ):
    donnees = exemple_fusion()
    del donnees[champ]
    with pytest.raises(ValidationError):
        SortieFusionLlm.model_validate(donnees)
