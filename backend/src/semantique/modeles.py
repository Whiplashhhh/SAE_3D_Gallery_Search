"""
@author:  WV

Format des réponses du VLM (une vue) et du LLM (fusion des vues) pour le Lot B

Ce ne sont pas des contrats entre lots : ce sont les sorties brutes des
modèles. Le schéma JSON de chaque modèle est passé à Ollama pour forcer la
réponse dans ce format.
"""

from pydantic import BaseModel, ConfigDict, Field

from contrats import EtatModele, MotCle, TexteNonVide


class SortieVueVlm(BaseModel):
    """Ce que le VLM voit sur une seule vue, sans déduction sur les faces cachées."""

    # Mode strict : un champ inconnu ou manquant est refusé
    model_config = ConfigDict(extra="forbid", frozen=True)

    description: TexteNonVide  # ce qui est visible sur l'image, en quelque phrases
    elements_visibles: list[MotCle] = Field(min_length=1, max_length=20)  # ex : dossier, roulette
    couleurs: list[MotCle] = Field(max_length=10)
    materiaux: list[MotCle] = Field(max_length=10)


class SortieFusionLlm(BaseModel):
    """Ce que le LLM renvoie après avoir fusionné les descriptions de toutes les vues."""

    # Mode strict, comme SortieVueVlm
    model_config = ConfigDict(extra="forbid", frozen=True)

    # Mêmes règles que les champs de FicheModele (D29)
    titre: TexteNonVide = Field(max_length=200)
    description: TexteNonVide  # description globale de l'objet, toutes vues confondues
    categorie: MotCle
    mots_cles: list[MotCle] = Field(min_length=1, max_length=30)
    etat: EtatModele
    divergences_entre_vues: list[TexteNonVide]  # contradictions entre vues, liste vide si aucune
