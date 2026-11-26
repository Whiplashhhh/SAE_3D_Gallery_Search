"""
@author: AR

Point d'entrée exécuté par Blender sans interface :

    blender --background --python-exit-code 1 --python src/rendu/script_blender.py --
        <modele> <dossier_sortie> [--vues a,b] [--resolution 512] [--vignette 256]

Si le modèle a des textures (intégrées ou retrouvées dans son dossier), elles
sont rendues telles quelles ; sinon chaque pièce reçoit une couleur de la palette.

Écrit <dossier_sortie>/<nom_vue>.png pour chaque vue demandée (et vignette.png
si --vignette > 0), puis affiche la ligne RENDU_MOTEUR=... lue par l'orchestrateur.
"""

import os
import sys

# Blender n'ajoute pas src/ au chemin d'import : on le fait pour trouver le paquet rendu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rendu import scene_blender
from rendu.arguments import lire_arguments
from rendu.vues import VUES_DIAGONALES_2

NOM_VIGNETTE = "vignette.png"
PREFIXE_MOTEUR = "RENDU_MOTEUR="


def main(argv: list[str]) -> None:
    arguments = lire_arguments(argv)
    os.makedirs(arguments.dossier_sortie, exist_ok=True)

    scene_blender.nettoyer_scene()

    print(f"Importation du modèle : {arguments.chemin_modele}")
    importes = scene_blender.importer_modele(arguments.chemin_modele)
    maillages = [obj for obj in importes if obj.type == "MESH"]
    scene_blender.relier_textures(arguments.chemin_modele, maillages)

    # Un modèle texturé garde ses matériaux d'origine ; sinon une couleur vive par pièce
    if scene_blender.a_des_textures(maillages):
        print("Textures d'origine conservées")
    else:
        maillages = scene_blender.separer_pieces(importes)
        scene_blender.colorer_pieces(maillages)
    scene_blender.normaliser(maillages)

    cam = scene_blender.creer_camera()
    scene_blender.configurer_rendu(arguments.resolution)

    for vue in arguments.vues:
        chemin_png = os.path.join(arguments.dossier_sortie, f"{vue.nom}.png")
        scene_blender.rendre_vue(cam, vue, chemin_png)

    if arguments.resolution_vignette > 0:
        scene_blender.configurer_rendu(arguments.resolution_vignette)
        chemin_vignette = os.path.join(arguments.dossier_sortie, NOM_VIGNETTE)
        scene_blender.rendre_vue(cam, VUES_DIAGONALES_2[0], chemin_vignette)

    print(f"{PREFIXE_MOTEUR}{scene_blender.version_moteur()}")
    print("Rendu normalisé terminé !")


if __name__ == "__main__":
    main(sys.argv)
