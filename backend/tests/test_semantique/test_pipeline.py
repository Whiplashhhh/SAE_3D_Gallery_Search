"""
@author: WV

Fichier de tests liés à indexer_modele(), avec un faux client (sans Ollama)
et des images factices
"""
import json
from datetime import UTC, datetime

import pytest

from config import Config
from contrats import ManifesteRendu, Vue, charger_fiche, lire_journal
from semantique import DescriptionImpossible, DimensionEmbeddingInvalide, indexer_modele

SHA256 = "ab" * 32
ID_MODELE = SHA256[:16]
DIMENSION = 4


def sortie_vue(description, couleurs):
    return json.dumps({
        "description": description,
        "elements_visibles": ["assise"],
        "couleurs": couleurs,
        "materiaux": ["tissu"],
    })


FUSION = json.dumps({
    "titre": "Chaise de bureau rouge",
    "description": "Chaise de bureau rouge à roulettes, avec un dossier haut.",
    "categorie": "mobilier",
    "mots_cles": ["chaise", "bureau", "Chaise"],
    "etat": "intact",
    "divergences_entre_vues": [],
})


class FauxClient:
    """Renvoie les réponses de chat données, dans l'ordre, et un vecteur fixe"""

    def __init__(self, *reponses, vecteur=None):
        self.reponses = list(reponses)
        self.vecteur = vecteur if vecteur is not None else [0.1] * DIMENSION
        self.modeles_chat = []
        self.textes_embed = []

    def chat(self, modele, messages, schema=None, images=None):
        self.modeles_chat.append(modele)
        return self.reponses.pop(0)

    def embed(self, textes):
        self.textes_embed.append(textes)
        return self.vecteur


@pytest.fixture
def config(monkeypatch, tmp_path):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://10.0.0.5:11434")
    monkeypatch.setenv("MODELE_VLM", "qwen3-vl:8b-instruct")
    monkeypatch.setenv("MODELE_LLM", "gemma4:26b")
    monkeypatch.setenv("MODELE_EMBEDDING", "embeddinggemma")
    monkeypatch.setenv("DIMENSION_EMBEDDING", str(DIMENSION))
    monkeypatch.setenv("OLLAMA_TENTATIVES", "2")
    monkeypatch.setenv("CHEMIN_JOURNAL", str(tmp_path / "indexation.jsonl"))
    return Config(_env_file=tmp_path / "absent.env")


@pytest.fixture
def manifeste(tmp_path):
    """Manifeste à 2 vues, dont les PNG factices existent sous tmp_path (racine)"""
    noms = ["avant_droite_haut", "arriere_gauche_haut"]
    vues = []
    for nom in noms:
        chemin = f"donnees/rendus/{ID_MODELE}/{nom}.png"
        (tmp_path / chemin).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / chemin).write_bytes(b"faux png")
        vues.append(Vue(nom=nom, chemin=chemin, azimut=45.0, elevation=30.0))
    return ManifesteRendu(
        version="1.0",
        id_modele=ID_MODELE,
        fichier_source="donnees/modeles/chaise.glb",
        sha256=SHA256,
        date_rendu=datetime.now(UTC),
        moteur="blender",
        resolution=(512, 512),
        nombre_vues=len(vues),
        vues=vues,
        vignette=f"donnees/rendus/{ID_MODELE}/vignette.png",
    )


def chemin_fiche(config, tmp_path):
    return tmp_path / config.dossier_fiches / f"{ID_MODELE}.json"


def test_fiche_ecrite_et_valide(config, manifeste, tmp_path):
    client = FauxClient(
        sortie_vue("Chaise rouge vue de l'avant.", ["rouge", "noir"]),
        sortie_vue("Chaise vue de l'arrière.", ["Rouge", "gris"]),
        FUSION,
    )

    chemin = indexer_modele(manifeste, client, config=config, racine=tmp_path)

    assert chemin == chemin_fiche(config, tmp_path)
    fiche = charger_fiche(chemin)  # se relit avec FicheModele
    assert fiche.id_modele == ID_MODELE
    assert fiche.titre == "Chaise de bureau rouge"
    assert [vue.nom for vue in fiche.par_vue] == ["avant_droite_haut", "arriere_gauche_haut"]
    assert fiche.par_vue[0].description == "Chaise rouge vue de l'avant."
    # Mots-clés et couleurs sans doublon, dans l'ordre d'apparition
    assert fiche.mots_cles == ["chaise", "bureau"]
    assert fiche.couleurs_dominantes == ["rouge", "noir", "gris"]
    assert fiche.embedding.modele == "embeddinggemma"
    assert fiche.embedding.dimension == DIMENSION
    # 2 vues au VLM, puis la fusion au LLM, puis la description globale vectorisée
    assert client.modeles_chat == ["qwen3-vl:8b-instruct"] * 2 + ["gemma4:26b"]
    assert client.textes_embed == [fiche.description]


def test_echec_sur_une_vue_sans_fiche(config, manifeste, tmp_path):
    invalide = json.dumps({"description": "Réponse incomplète."})
    client = FauxClient(sortie_vue("Chaise rouge.", ["rouge"]), invalide, invalide)

    with pytest.raises(DescriptionImpossible):
        indexer_modele(manifeste, client, config=config, racine=tmp_path)

    # Ni fiche partielle, ni fichier temporaire
    assert not (tmp_path / config.dossier_fiches).exists()
    entrees = lire_journal(config.chemin_journal)
    abandon = [e for e in entrees if e.evenement == "indexation_abandonnee"]
    assert len(abandon) == 1
    assert abandon[0].id_modele == ID_MODELE
    assert abandon[0].niveau == "erreur"


def test_mauvaise_dimension_sans_fiche(config, manifeste, tmp_path):
    client = FauxClient(
        sortie_vue("Chaise rouge.", ["rouge"]),
        sortie_vue("Chaise rouge.", ["rouge"]),
        FUSION,
        vecteur=[0.1, 0.2],
    )

    with pytest.raises(DimensionEmbeddingInvalide):
        indexer_modele(manifeste, client, config=config, racine=tmp_path)

    assert not chemin_fiche(config, tmp_path).exists()
    evenements = [e.evenement for e in lire_journal(config.chemin_journal)]
    assert "indexation_abandonnee" in evenements
