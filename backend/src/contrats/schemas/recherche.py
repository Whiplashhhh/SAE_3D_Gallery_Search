from pydantic import BaseModel, Field

class RechercheRequete(BaseModel):
    texte: str = Field(min_length=1)
    top_k: int = Field(default=10, ge=1, le=100)
    seuil: float | None = Field(default=None, ge=0, le=1)
    categorie: str | None = None
    couleur: str | None = None
    format_fichier: str | None = None

class ResultatRecherche(BaseModel):
    id: str
    score: float
    metadonnees: dict

class RechercheReponse(BaseModel):
    resultats: list[ResultatRecherche]
    nb_total: int
    temps_ms: float

class ModeleInfo(BaseModel):
    id: str
    nom: str
    metadonnees: dict

class StatsReponse(BaseModel):
    nb_modeles_indexes: int
    taille_collection: int
    ollama_actif: bool
    derniere_indexation: str | None = None