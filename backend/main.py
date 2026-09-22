from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import Configuration
from src.ia.service_embedding import ServiceEmbedding
from src.ia.vectorisation import vectoriser_texte
from src.ollama.client import ClientOllama
from src.recherche.chargeur_fiches import ChargeurFiches
from src.recherche.router import router as recherche_router
from src.recherche.service_chroma import ServiceChroma
from src.recherche.service_indexation import ServiceIndexation
from src.recherche.service_recherche import ServiceRecherche

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
MODELS_DIR = DATA_DIR / "models"
FICHES_DIR = BASE_DIR.parent / "donnees" / "fiches"
configuration = Configuration()
ollama = ClientOllama(
    configuration.ollama_base_url,
    configuration.modele_embedding,
    configuration.ollama_timeout_s,
)

app = FastAPI(
    title="3D Gallery Search API",
    description="API de recherche sémantique pour modèles 3D",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODELS_DIR.mkdir(parents=True, exist_ok=True)
chroma = ServiceChroma(VECTOR_STORE_DIR)
embeddings = ServiceEmbedding(vectoriser_texte, ollama.embed)
chargeur_fiches = ChargeurFiches(FICHES_DIR)
indexation = ServiceIndexation(chroma)
indexation.indexer_fiches(chargeur_fiches)

app.state.chroma = chroma
app.state.embeddings = embeddings
app.state.indexation = indexation
app.state.recherche = ServiceRecherche(chroma, embeddings, chargeur_fiches)
app.state.models_dir = MODELS_DIR
app.state.ollama = ollama
app.state.fiches_dir = FICHES_DIR
app.state.chargeur_fiches = chargeur_fiches
app.include_router(recherche_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "API 3D Gallery Search active", "status": "ok"}
