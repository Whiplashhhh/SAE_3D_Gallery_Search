from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import obtenir_config
from src.ollama.client import ClientOllama


def main() -> None:
    config = obtenir_config()
    client = ClientOllama(
        str(config.ollama_base_url),
        config.modele_embedding,
        timeout_s=config.ollama_timeout_s,
        tentatives=config.ollama_tentatives,
    )
    vecteur = client.embed("test")
    print(len(vecteur))


if __name__ == "__main__":
    main()
