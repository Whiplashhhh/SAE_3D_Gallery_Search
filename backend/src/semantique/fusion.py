"""
@author: WV

Fusion des descriptions de toutes les vues par le LLM (Lot B)

Même règle que decrire_vue() (D28) : le client Ollama s'occupe du réseau et de
ses propres tentatives. Ici, on vérifie seulement que la réponse respecte
SortieFusionLlm, et on redemande au LLM si ce n'est pas le cas
"""

import json
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from config import Config, obtenir_config
from contrats import journaliser
from ollama.client import ClientOllama
from semantique.modeles import SortieFusionLlm, SortieVueVlm

PROMPT_FUSION = (Path(__file__).parent / "prompts" / "fusion.md").read_text(encoding="utf-8")


class FusionImpossible(Exception):
    """Le LLM n'a donné aucune réponse valide après toutes les tentatives."""


def fusionner_descriptions(
    descriptions: Sequence[SortieVueVlm],
    client: ClientOllama,
    *,
    id_modele: str | None = None,
    config: Config | None = None,
) -> SortieFusionLlm:
    """Demande au LLM de fusionner les descriptions des vues et renvoie sa réponse validée.

    throw ValueError si la liste est vide (aucun appel au LLM).
    throw FusionImpossible si aucune réponse n'est valide, après avoir écrit
    l'échec dans le journal.
    """
    if not descriptions:
        raise ValueError("Aucune description de vue à fusionner.")

    config = config or obtenir_config()
    vues = [description.model_dump() for description in descriptions]
    messages = [
        {"role": "system", "content": PROMPT_FUSION},
        {"role": "user", "content": json.dumps(vues, ensure_ascii=False, indent=2)},
    ]

    for tentative in range(1, config.ollama_tentatives + 1):
        texte = client.chat(
            config.modele_llm,
            messages,
            schema=SortieFusionLlm.model_json_schema(),
        )
        try:
            return SortieFusionLlm.model_validate_json(texte)
        except ValidationError:
            # Réponse hors format : on redemande
            journaliser(
                config.chemin_journal,
                "B",
                "sortie_llm_invalide_relance",
                f"fusion de {len(descriptions)} vues : réponse refusée (tentative {tentative})",
                niveau="avertissement",
                id_modele=id_modele,
            )

    journaliser(
        config.chemin_journal,
        "B",
        "fusion_abandonnee",
        f"fusion de {len(descriptions)} vues : aucune réponse valide "
        f"après {config.ollama_tentatives} tentatives",
        niveau="erreur",
        id_modele=id_modele,
    )
    raise FusionImpossible(f"{len(descriptions)} vues")
