"""
@author: AR

Catalogue des prises de vue et calculs de placement de la caméra.

Convention des angles :
    azimut    0 = face (caméra en -Y), 90 = droite (+X), 180 = arrière, 270 = gauche
    elevation 0 = à hauteur de l'objet, 90 = au-dessus, -90 = en dessous
"""

import math
from typing import NamedTuple


class VueCamera(NamedTuple):
    """Une prise de vue : son nom (sert de nom de fichier) et l'angle de la caméra."""

    nom: str
    azimut: float
    elevation: float


ELEVATION_DIAGONALE: float = math.degrees(math.atan(1 / math.sqrt(2)))
"""~35.26° : l'angle qui vise un coin de la boîte englobante depuis le coin opposé.
Une vue sur cette diagonale voit trois faces de la boîte d'un coup."""


VUES_DIAGONALES_2 = (
    VueCamera("avant_droite_haut", 45.0, ELEVATION_DIAGONALE),
    VueCamera("arriere_gauche_haut", 225.0, ELEVATION_DIAGONALE),
)
"""Rendu par défaut : deux coins opposés vus d'en haut. Pas de vue de dessous :
les modèles sont souvent des scènes posées au sol, le dessous n'apporte rien."""

VUES_DIAGONALES_4 = VUES_DIAGONALES_2 + (
    VueCamera("arriere_droite_haut", 135.0, ELEVATION_DIAGONALE),
    VueCamera("avant_gauche_bas", 315.0, -ELEVATION_DIAGONALE),
)
"""Rendu de secours si la description à 2 vues ne convient pas : on garde les deux
premières vues et on ajoute les deux autres diagonales."""

JEUX_DE_VUES = {
    2: VUES_DIAGONALES_2,
    4: VUES_DIAGONALES_4,
}
"""Nombre de vues demandé -> vues à rendre."""

CATALOGUE: dict[str, VueCamera] = {vue.nom: vue for vue in VUES_DIAGONALES_4}
"""Toutes les vues connues, par nom (le script Blender reçoit des noms)."""


def vues_pour(nb_vues: int) -> tuple[VueCamera, ...]:
    """Retourne le jeu de vues correspondant au nombre demandé (2 ou 4)."""
    if nb_vues not in JEUX_DE_VUES:
        raise ValueError(
            f"nb_vues={nb_vues} non supporté : choisir parmi {sorted(JEUX_DE_VUES)}"
        )
    return JEUX_DE_VUES[nb_vues]


def vues_par_noms(noms: list[str]) -> list[VueCamera]:
    """Retrouve les vues du catalogue à partir de leurs noms, dans l'ordre donné."""
    inconnues = [nom for nom in noms if nom not in CATALOGUE]
    if inconnues:
        raise ValueError(f"vue(s) inconnue(s) : {', '.join(inconnues)}")
    return [CATALOGUE[nom] for nom in noms]


def distance_camera(fov: float, taille_cible: float, marge: float = 1.15) -> float:
    """Distance caméra-origine pour qu'un objet de diagonale taille_cible tienne
    dans le champ (fov en radians), avec une marge (1.15 = 15 %)."""
    return (taille_cible / 2.0) / math.tan(fov / 2.0) * marge


def position_camera(vue: VueCamera, rayon: float) -> tuple[float, float, float]:
    """Position de la caméra sur la sphère de rayon donné, centrée sur l'origine."""
    azimut = math.radians(vue.azimut)
    elevation = math.radians(vue.elevation)
    return (
        rayon * math.cos(elevation) * math.sin(azimut),
        -rayon * math.cos(elevation) * math.cos(azimut),
        rayon * math.sin(elevation),
    )


def rotation_camera(vue: VueCamera) -> tuple[float, float, float]:
    """Rotation Euler XYZ (radians) qui oriente la caméra vers l'origine.

    Une caméra Blender sans rotation regarde vers -Z : on la bascule de
    (90° - elevation) autour de X, puis on la tourne de l'azimut autour de Z.
    """
    return (
        math.radians(90.0 - vue.elevation),
        0.0,
        math.radians(vue.azimut),
    )

