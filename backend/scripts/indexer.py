from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.recherche.chargeur_fiches import ChargeurFiches
from src.recherche.service_chroma import ServiceChroma
from src.recherche.service_indexation import ServiceIndexation


def indexer_demo() -> None:
    data_dir = ROOT / "data"
    service = ServiceIndexation(
        ServiceChroma(data_dir / "vector_store"),
    )
    fiches_dir = ROOT.parent / "donnees" / "fiches"
    nombre_fiches = service.indexer_fiches(ChargeurFiches(fiches_dir))
    print(f"Fiches indexées : {nombre_fiches}")
    print(f"Vecteurs ChromaDB : {service.chroma.compter()}")


if __name__ == "__main__":
    indexer_demo()
