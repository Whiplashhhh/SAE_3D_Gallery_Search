from pydantic import BaseModel, ConfigDict, Field


class VueModele(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    nom: str
    description: str


class EmbeddingFiche(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    modele: str
    dimension: int = Field(gt=0)
    vecteur: list[float]


class FicheModele(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str
    id_modele: str
    titre: str
    description: str
    categorie: str
    mots_cles: list[str]
    couleurs_dominantes: list[str]
    etat: str
    par_vue: list[VueModele]
    divergences_entre_vues: list[str]
    embedding: EmbeddingFiche
    duree_ms: dict[str, int] = Field(default_factory=dict)
