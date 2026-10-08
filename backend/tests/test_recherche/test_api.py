import json
from collections.abc import Iterator
from copy import deepcopy
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.ia.service_embedding import ServiceEmbedding
from src.recherche.chargeur_fiches import ChargeurFiches
from src.recherche.router import router
from src.recherche.service_chroma import ServiceChroma
from src.recherche.service_indexation import ServiceIndexation
from src.recherche.service_recherche import ServiceRecherche

FICHE_CHAISE = Path(__file__).parents[2] / "seed" / "fiches" / "chaise_bureau.json"
ID_CHAISE = "a3f1c2d4e5b60789"


class FauxOllama:
    def est_joignable(self) -> bool:
        return False


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    fiches_dir = tmp_path / "fiches"
    fiches_dir.mkdir()
    fiche_chaise = json.loads(FICHE_CHAISE.read_text(encoding="utf-8"))
    fiches = [
        (deepcopy(fiche_chaise), ID_CHAISE, "Chaise de bureau", [1.0, 0.0, 0.0]),
        (
            deepcopy(fiche_chaise),
            "b4e2d6f8a1c30579",
            "Maison de campagne",
            [0.0, 1.0, 0.0],
        ),
        (
            deepcopy(fiche_chaise),
            "c5f3e7a9b2d41680",
            "Voiture compacte",
            [0.6, 0.8, 0.0],
        ),
    ]

    for donnees, identifiant, titre, vecteur in fiches:
        donnees["id_modele"] = identifiant
        donnees["titre"] = titre
        donnees["embedding"]["vecteur"] = vecteur
        (fiches_dir / f"{identifiant}.json").write_text(
            json.dumps(donnees),
            encoding="utf-8",
        )

    chargeur = ChargeurFiches(fiches_dir)
    chroma = ServiceChroma(tmp_path / "chroma")
    indexation = ServiceIndexation(chroma)
    indexation.indexer_fiches(chargeur)

    embeddings = ServiceEmbedding(encodeur=lambda _: [1.0, 0.0, 0.0])
    app = FastAPI()
    app.state.chroma = chroma
    app.state.chargeur_fiches = chargeur
    app.state.ollama = FauxOllama()
    app.state.recherche = ServiceRecherche(chroma, embeddings, chargeur)
    app.include_router(router, prefix="/api")

    with TestClient(app) as test_client:
        yield test_client


def test_api_sante_repond_sans_ollama(client: TestClient):
    response = client.get("/api/sante")

    assert response.status_code == 200
    assert response.json() == {
        "ollama_joignable": False,
        "fiches_indexees": 3,
        "vecteurs_indexes": 3,
    }


def test_api_modele_existant_repond_200(client: TestClient):
    response = client.get(f"/api/modeles/{ID_CHAISE}")

    assert response.status_code == 200
    assert response.json()["id"] == ID_CHAISE
    assert response.json()["nom"] == "Chaise de bureau"


def test_api_modele_absent_repond_404(client: TestClient):
    response = client.get("/api/modeles/ffffffffffffffff")

    assert response.status_code == 404


def test_api_recherche_trie_les_resultats_par_score(client: TestClient):
    response = client.get("/api/recherche", params={"q": "chaise", "k": 3})

    assert response.status_code == 200
    donnees = response.json()
    resultats = donnees["resultats"]
    scores = [resultat["score"] for resultat in resultats]

    assert donnees["nb_total"] == 3
    assert len(resultats) == 3
    assert resultats[0]["id"] == ID_CHAISE
    assert scores == sorted(scores, reverse=True)
