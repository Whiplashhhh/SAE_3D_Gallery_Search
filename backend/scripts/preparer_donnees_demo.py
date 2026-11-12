import json
from pathlib import Path

from contrats import FicheModele
from src.config import obtenir_config
from src.ollama.client import ClientOllama

BASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = BASE_DIR / "seed" / "fiches"
DATA_DIR = BASE_DIR / "data" / "fiches"


def main() -> None:
    configuration = obtenir_config()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with ClientOllama(
        str(configuration.ollama_base_url),
        configuration.modele_embedding,
        timeout_s=configuration.ollama_timeout_s,
        tentatives=configuration.ollama_tentatives,
    ) as ollama:
        for source in sorted(SOURCE_DIR.glob("*.json")):
            donnees = json.loads(source.read_text(encoding="utf-8"))
            identifiant = donnees["id_modele"]
            destination = DATA_DIR / f"{identifiant}.json"
            if destination.exists():
                continue

            vecteur = ollama.embed(donnees["description"])
            if len(vecteur) != configuration.dimension_embedding:
                raise ValueError(
                    f"Dimension d'embedding invalide pour {identifiant}: "
                    f"{len(vecteur)} au lieu de {configuration.dimension_embedding}."
                )

            donnees["embedding"]["modele"] = configuration.modele_embedding
            donnees["embedding"]["dimension"] = len(vecteur)
            donnees["embedding"]["vecteur"] = vecteur
            fiche = FicheModele.model_validate(donnees)
            temporaire = destination.with_suffix(".json.tmp")
            temporaire.write_text(
                json.dumps(fiche.model_dump(mode="json"), ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            temporaire.replace(destination)


if __name__ == "__main__":
    main()
