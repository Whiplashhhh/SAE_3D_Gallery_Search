"""
@author: WV

Description d'une seule vue PNG par le VLM (Lot B)

Le client Ollama s'occupe du réseau et de ses propres tentatives.
Ici, on vérifie seulement que la réponse respecte SortieVueVlm, et on
redemande au VLM si ce n'est pas le cas
"""

from pathlib import Path

from pydantic import ValidationError

from config import Config, obtenir_config
from contrats import journaliser
from ollama.client import ClientOllama
from semantique.modeles import SortieVueVlm

PROMPT_VUE = (Path(__file__).parent / "prompts" / "vue.md").read_text(encoding="utf-8")


class DescriptionImpossible(Exception):
    """Le VLM n'a donné aucune réponse valide après toutes les tentatives."""


def decrire_vue(
    chemin_png: Path,
    client: ClientOllama,
    *,
    id_modele: str | None = None,
    config: Config | None = None,
) -> SortieVueVlm:
    """Demande au VLM de décrire une vue et renvoie sa réponse validée.

    throw DescriptionImpossible si aucune réponse n'est valide, après avoir
    écrit l'échec dans le journal.
    """
    config = config or obtenir_config()
    chemin_png = Path(chemin_png)
    messages = [
        {"role": "system", "content": PROMPT_VUE},
        {"role": "user", "content": "Décris cette vue."},
    ]

    for tentative in range(1, config.ollama_tentatives + 1):
        texte = client.chat(
            config.modele_vlm,
            messages,
            schema=SortieVueVlm.model_json_schema(),
            images=[chemin_png.read_bytes()],
        )
        try:
            return SortieVueVlm.model_validate_json(texte)
        except ValidationError:
            # Réponse hors format : on redemande
            journaliser(
                config.chemin_journal,
                "B",
                "sortie_vlm_invalide_relance",
                f"{chemin_png.name} : réponse refusée (tentative {tentative})",
                niveau="avertissement",
                id_modele=id_modele,
            )

    journaliser(
        config.chemin_journal,
        "B",
        "description_vue_abandonnee",
        f"{chemin_png.name} : aucune réponse valide après {config.ollama_tentatives} tentatives",
        niveau="erreur",
        id_modele=id_modele,
    )
    raise DescriptionImpossible(chemin_png.name)
