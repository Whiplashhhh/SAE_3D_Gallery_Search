"""
@author:  WV

Format de la réponse du VLM pour une seule vue (Lot B)

Ce n'est pas un contrat entre lots : c'est la sortie brute du VLM, avant la
fusion par le LLM. Le schéma JSON de ce modèle est passé à Ollama pour forcer
le VLM à répondre dans ce format.
"""

from pydantic import BaseModel, ConfigDict, Field

from contrats import MotCle, TexteNonVide


class SortieVueVlm(BaseModel):
    """Ce que le VLM voit sur une seule vue, sans déduction sur les faces cachées."""

    # Mode strict : un champ inconnu ou manquant est refusé
    model_config = ConfigDict(extra="forbid", frozen=True)

    description: TexteNonVide  # ce qui est visible sur l'image, en quelque phrases
    elements_visibles: list[MotCle] = Field(min_length=1, max_length=20)  # ex : dossier, roulette
    couleurs: list[MotCle] = Field(max_length=10)
    materiaux: list[MotCle] = Field(max_length=10)
