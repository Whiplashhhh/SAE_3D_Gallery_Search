from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile

from ..contrats.schemas.fiche import FicheModele
from ..contrats.schemas.recherche import (
    ModeleInfo,
    RechercheReponse,
    RechercheRequete,
    StatsReponse,
)
from ..ollama.client import ClientOllama
from .chargeur_fiches import ChargeurFiches
from .service_chroma import ServiceChroma
from .service_indexation import ServiceIndexation
from .service_recherche import ServiceRecherche

router = APIRouter(tags=["recherche"])
TAILLE_MAX_MODELE = 50 * 1024 * 1024
FORMATS_MODELES_ACCEPTES = {".obj", ".gltf", ".stl"}


def get_chroma(request: Request) -> ServiceChroma:
    return request.app.state.chroma


def get_recherche(request: Request) -> ServiceRecherche:
    return request.app.state.recherche


def get_models_dir(request: Request) -> Path:
    return request.app.state.models_dir


def get_ollama(request: Request) -> ClientOllama:
    return request.app.state.ollama


def get_chargeur_fiches(request: Request) -> ChargeurFiches:
    return request.app.state.chargeur_fiches


def get_indexation(request: Request) -> ServiceIndexation:
    return request.app.state.indexation


def fiche_info(fiche: FicheModele) -> ModeleInfo:
    couleurs = "|".join(fiche.couleurs_dominantes)
    mots_cles = "|".join(fiche.mots_cles)
    return ModeleInfo(
        id=fiche.id_modele,
        nom=fiche.titre,
        metadonnees={
            "nom": fiche.titre,
            "titre": fiche.titre,
            "description": fiche.description,
            "categorie": fiche.categorie,
            "couleur": couleurs,
            "couleurs_dominantes": couleurs,
            "mots_cles": mots_cles,
        },
    )


@router.post("/search", response_model=RechercheReponse)
def search(requete: RechercheRequete, service: ServiceRecherche = Depends(get_recherche)):
    return service.rechercher(requete)


@router.get("/recherche", response_model=RechercheReponse)
def recherche_get(
    q: str = Query(min_length=1),
    k: int = Query(default=12, ge=1, le=100),
    service: ServiceRecherche = Depends(get_recherche),
):
    return service.rechercher(RechercheRequete(texte=q, top_k=k))


@router.post("/models/upload", response_model=ModeleInfo, status_code=201)
async def upload_model(
    fichier: UploadFile = File(...),
    models_dir: Path = Depends(get_models_dir),
):
    nom_original = Path(fichier.filename or "").name
    extension = Path(nom_original).suffix.lower()
    if not nom_original or extension not in FORMATS_MODELES_ACCEPTES:
        raise HTTPException(
            status_code=400,
            detail="Seuls les fichiers .obj, .gltf et .stl sont acceptés.",
        )

    contenu = await fichier.read(TAILLE_MAX_MODELE + 1)
    if len(contenu) > TAILLE_MAX_MODELE:
        raise HTTPException(status_code=413, detail="Le fichier ne doit pas dépasser 50 Mo.")

    identifiant = f"upload-{uuid4().hex}"
    chemin = models_dir / f"{identifiant}{extension}"
    chemin.write_bytes(contenu)
    nom = Path(nom_original).stem.replace("_", " ").replace("-", " ").strip() or identifiant
    return ModeleInfo(
        id=identifiant,
        nom=nom,
        metadonnees={
            "nom": nom,
            "description": f"Modèle importé depuis {nom_original}",
            "categorie": "import",
            "couleur": "",
            "format_fichier": extension[1:],
            "nom_fichier_original": nom_original,
            "indexation": "en attente d'une fiche_modele.json produite par le Lot B",
        },
    )


@router.get("/models", response_model=list[ModeleInfo])
def list_models(chargeur: ChargeurFiches = Depends(get_chargeur_fiches)):
    return [fiche_info(fiche) for fiche in chargeur.charger()]


@router.get("/models/{id}", response_model=ModeleInfo)
def get_model(id: str, chargeur: ChargeurFiches = Depends(get_chargeur_fiches)):
    fiche = chargeur.obtenir(id)
    if fiche is None:
        raise HTTPException(status_code=404, detail="modèle introuvable")
    return fiche_info(fiche)


@router.get("/modeles/{id}", response_model=ModeleInfo)
def get_modele(id: str, chargeur: ChargeurFiches = Depends(get_chargeur_fiches)):
    return get_model(id, chargeur)


@router.delete("/modeles/{id}", status_code=204)
def delete_modele(
    id: str,
    chargeur: ChargeurFiches = Depends(get_chargeur_fiches),
    indexation: ServiceIndexation = Depends(get_indexation),
    models_dir: Path = Depends(get_models_dir),
):
    if chargeur.obtenir(id) is None:
        raise HTTPException(status_code=404, detail="modèle introuvable")

    indexation.supprimer(id)
    if not chargeur.supprimer(id):
        raise HTTPException(status_code=500, detail="Impossible de supprimer la fiche.")

    for fichier in models_dir.glob(f"{id}.*"):
        fichier.unlink()


@router.get("/stats", response_model=StatsReponse)
def stats(
    chargeur: ChargeurFiches = Depends(get_chargeur_fiches),
    chroma: ServiceChroma = Depends(get_chroma),
):
    return StatsReponse(
        nb_modeles_indexes=chargeur.compter(),
        taille_collection=chroma.compter(),
        ollama_actif=True,
    )


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/sante")
def sante(
    chargeur: ChargeurFiches = Depends(get_chargeur_fiches),
    chroma: ServiceChroma = Depends(get_chroma),
    ollama: ClientOllama = Depends(get_ollama),
):
    return {
        "ollama_joignable": ollama.est_joignable(),
        "fiches_indexees": chargeur.compter(),
        "vecteurs_indexes": chroma.compter(),
    }
