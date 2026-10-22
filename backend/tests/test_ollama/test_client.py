import httpx
import pytest

from src.ollama.client import ClientOllama, OllamaErreur


def test_embed_repond_avec_vecteur_valide():
    def gestionnaire(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/embed"
        return httpx.Response(200, json={"embeddings": [[0.1, 0.2, 0.3]]})

    client = ClientOllama(
        "http://localhost:11434",
        "embeddinggemma",
        timeout_s=1,
        tentatives=2,
        http_client=httpx.Client(transport=httpx.MockTransport(gestionnaire)),
    )
    assert client.embed("bonjour") == [0.1, 0.2, 0.3]
    client._client.close()


def test_embed_relance_en_cas_de_json_invalide():
    appels = {"count": 0}

    def gestionnaire(request: httpx.Request) -> httpx.Response:
        appels["count"] += 1
        if appels["count"] == 1:
            return httpx.Response(200, content=b"{not-json")
        return httpx.Response(200, json={"embeddings": [[0.5, 0.6, 0.7]]})

    client = ClientOllama(
        "http://localhost:11434",
        "embeddinggemma",
        timeout_s=1,
        tentatives=2,
        http_client=httpx.Client(transport=httpx.MockTransport(gestionnaire)),
    )
    assert client.embed("bonjour") == [0.5, 0.6, 0.7]
    client._client.close()


def test_chat_envoie_le_schema_et_les_images():
    import json

    def gestionnaire(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode("utf-8"))
        assert request.url.path == "/api/chat"
        assert body["model"] == "llama3.1"
        assert body["images"] == ["base64-1"]
        assert body["format"]["properties"]["reponse"]["type"] == "string"
        return httpx.Response(200, json={"message": {"content": "ok"}})

    client = ClientOllama(
        "http://localhost:11434",
        "embeddinggemma",
        timeout_s=1,
        tentatives=1,
        http_client=httpx.Client(transport=httpx.MockTransport(gestionnaire)),
    )
    reponse = client.chat(
        "llama3.1",
        [{"role": "user", "content": "bonjour"}],
        schema={"type": "object", "properties": {"reponse": {"type": "string"}}},
        images=["base64-1"],
    )
    assert reponse["message"]["content"] == "ok"
    client._client.close()


def test_embed_epuise_les_tentatives_et_leve_exception_metier():
    appels = {"count": 0}

    def gestionnaire(request: httpx.Request) -> httpx.Response:
        appels["count"] += 1
        raise httpx.ReadTimeout("timeout")

    client = ClientOllama(
        "http://localhost:11434",
        "embeddinggemma",
        timeout_s=1,
        tentatives=3,
        http_client=httpx.Client(transport=httpx.MockTransport(gestionnaire)),
    )
    with pytest.raises(OllamaErreur):
        client.embed("bonjour")
    assert appels["count"] == 3
    client._client.close()
