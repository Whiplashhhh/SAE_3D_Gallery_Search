"""
@author: AR

Lecture des arguments passés au script Blender après le séparateur '--' :

    blender --background --python script_blender.py -- <modele> <dossier_sortie>
        [--vues avant_droite_haut,arriere_gauche_haut] [--resolution 512] [--vignette 256]

Python pur (sans bpy) pour être testé sans Blender.
"""

import argparse
import os
from typing import NamedTuple

from rendu.vues import VUES_DIAGONALES_2, VueCamera, vues_par_noms


class ArgumentsRendu(NamedTuple):
    chemin_modele: str
    dossier_sortie: str
    vues: list[VueCamera]
    resolution: int
    resolution_vignette: int  # 0 = pas de vignette


def _construire_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(prog="script_blender.py")
    parseur.add_argument("chemin_modele")
    parseur.add_argument("dossier_sortie")
    parseur.add_argument(
        "--vues",
        default=",".join(vue.nom for vue in VUES_DIAGONALES_2),
        help="noms des vues à rendre, séparés par des virgules",
    )
    parseur.add_argument("--resolution", type=int, default=512)
    parseur.add_argument("--vignette", type=int, default=0)
    return parseur


def lire_arguments(argv: list[str]) -> ArgumentsRendu:
    """Lit les arguments situés après '--' dans la ligne de commande Blender.

    ValueError si '--' est absent, si une vue est inconnue ou si une
    résolution est invalide.
    """
    if "--" not in argv:
        raise ValueError("vous devez spécifier le modèle et le dossier de sortie après '--'")

    try:
        brut = _construire_parseur().parse_args(argv[argv.index("--") + 1:])
    except SystemExit as erreur:  # argparse quitte au lieu de lever une exception
        raise ValueError("arguments invalides après '--'") from erreur

    noms = [nom.strip() for nom in brut.vues.split(",") if nom.strip()]
    if not noms:
        raise ValueError("au moins une vue doit être demandée")
    if brut.resolution < 1 or brut.vignette < 0:
        raise ValueError("les résolutions doivent être positives")

    return ArgumentsRendu(
        chemin_modele=os.path.abspath(brut.chemin_modele),
        dossier_sortie=os.path.abspath(brut.dossier_sortie),
        vues=vues_par_noms(noms),
        resolution=brut.resolution,
        resolution_vignette=brut.vignette,
    )
