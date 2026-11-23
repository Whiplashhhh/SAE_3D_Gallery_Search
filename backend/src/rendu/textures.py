"""
@author: AR

Recherche des textures d'un modèle sur le disque.

Les FBX/OBJ gardent souvent le chemin de la machine de l'auteur
(ex : G:\\3D\\SCS soft\\texture.png) alors que l'image est rangée dans le
dossier textures/ du modèle : on la retrouve par son nom de fichier.
"""

import os
import re
from pathlib import Path

EXTENSIONS_IMAGES: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".tga", ".tif", ".tiff", ".bmp", ".exr", ".webp"}
)


def dossier_racine_modele(chemin_modele: str | Path) -> Path:
    """Dossier où chercher les textures.

    Les archives Sketchfab ont la forme <modele>/source/fichier.fbx et
    <modele>/textures/ : on remonte au-dessus de source/ s'il existe,
    sinon on reste dans le dossier du fichier.
    """
    dossier = Path(chemin_modele).resolve().parent
    for parent in (dossier, *dossier.parents):
        if parent.name.lower() == "source":
            return parent.parent
    return dossier


def indexer_images(racine: str | Path) -> dict[str, str]:
    """Associe chaque nom d'image (en minuscules) à son chemin, en parcourant racine.

    Le nom sans extension est aussi indexé : Sketchfab convertit parfois
    les .png en .jpeg. Le premier fichier trouvé l'emporte.
    """
    index: dict[str, str] = {}
    for dossier, _, fichiers in sorted(os.walk(racine)):
        for nom in sorted(fichiers):
            nom_min = nom.lower()
            base, extension = os.path.splitext(nom_min)
            if extension not in EXTENSIONS_IMAGES:
                continue
            chemin = os.path.join(dossier, nom)
            index.setdefault(nom_min, chemin)
            index.setdefault(base, chemin)
    return index


def retrouver_image(chemin_reference: str, index: dict[str, str]) -> str | None:
    """Chemin réel d'une image référencée par le modèle, ou None si introuvable.

    Le chemin de référence peut venir de Windows ('\\') ou d'Unix ('/'),
    et Blender préfixe les chemins relatifs par '//'.
    """
    nom = re.split(r"[\\/]", chemin_reference)[-1].lower()
    if not nom:
        return None
    return index.get(nom) or index.get(os.path.splitext(nom)[0])
