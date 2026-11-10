"""
@author: AR

Tests pour vues : jeux de 2 et 4 vues diagonales, placement et orientation de la caméra.
"""

import math

import pytest

from rendu.vues import (
    CATALOGUE,
    ELEVATION_DIAGONALE,
    VUES_DIAGONALES_2,
    VUES_DIAGONALES_4,
    VueCamera,
    distance_camera,
    position_camera,
    rotation_camera,
    vues_par_noms,
    vues_pour,
)


def _proche(a, b):
    return all(math.isclose(x, y, abs_tol=1e-9) for x, y in zip(a, b))


# jeux de vues

def test_deux_vues_par_defaut_opposees_et_vues_d_en_haut():
    premiere, seconde = vues_pour(2)

    assert (seconde.azimut - premiere.azimut) % 360 == 180
    assert premiere.elevation > 0 and seconde.elevation > 0


def test_les_quatre_vues_reprennent_les_deux_premieres():
    assert vues_pour(4)[:2] == vues_pour(2)
    assert len(vues_pour(4)) == 4


def test_les_quatre_vues_couvrent_les_quatre_diagonales():
    assert sorted(vue.azimut for vue in VUES_DIAGONALES_4) == [45.0, 135.0, 225.0, 315.0]


def test_les_noms_respectent_le_contrat_nom_vue():
    for vue in VUES_DIAGONALES_4:
        assert all(c.islower() or c == "_" for c in vue.nom)
        assert 1 <= len(vue.nom) <= 32
    assert len(CATALOGUE) == len(VUES_DIAGONALES_4)


def test_elevation_diagonale_vise_le_coin_d_un_cube():
    # le coin (1, -1, 1) vu depuis l'origine
    assert math.isclose(ELEVATION_DIAGONALE, math.degrees(math.atan2(1, math.sqrt(2))))


@pytest.mark.parametrize("nb_vues", [0, 1, 3, 6])
def test_vues_pour_refuse_les_autres_nombres(nb_vues):
    with pytest.raises(ValueError, match="non supporté"):
        vues_pour(nb_vues)


def test_vues_par_noms_garde_l_ordre():
    noms = ["arriere_gauche_haut", "avant_droite_haut"]
    assert [vue.nom for vue in vues_par_noms(noms)] == noms


def test_vues_par_noms_refuse_un_nom_inconnu():
    with pytest.raises(ValueError, match="face"):
        vues_par_noms(["avant_droite_haut", "face"])


# placement de la caméra

@pytest.mark.parametrize(
    ("vue", "attendu"),
    [
        (VueCamera("face", 0, 0), (0, -1, 0)),
        (VueCamera("droite", 90, 0), (1, 0, 0)),
        (VueCamera("arriere", 180, 0), (0, 1, 0)),
        (VueCamera("gauche", 270, 0), (-1, 0, 0)),
        (VueCamera("dessus", 0, 90), (0, 0, 1)),
        (VueCamera("dessous", 0, -90), (0, 0, -1)),
    ],
)
def test_position_camera_sur_les_axes(vue, attendu):
    assert _proche(position_camera(vue, 1.0), attendu)


@pytest.mark.parametrize(
    ("vue", "signes"),
    [
        (VUES_DIAGONALES_4[0], (1, -1, 1)),   # avant droite haut
        (VUES_DIAGONALES_4[1], (-1, 1, 1)),   # arriere gauche haut
        (VUES_DIAGONALES_4[2], (1, 1, 1)),    # arriere droite haut
        (VUES_DIAGONALES_4[3], (-1, -1, -1)), # avant gauche bas
    ],
)
def test_position_camera_des_vues_diagonales(vue, signes):
    rayon = math.sqrt(3)
    assert _proche(position_camera(vue, rayon), signes)


def test_position_camera_respecte_le_rayon():
    for vue in VUES_DIAGONALES_4:
        assert math.isclose(math.dist(position_camera(vue, 3.2), (0, 0, 0)), 3.2)


@pytest.mark.parametrize(
    ("vue", "attendu_degres"),
    [
        # mêmes angles que les 6 vues de l'ancien main.py
        (VueCamera("face", 0, 0), (90, 0, 0)),
        (VueCamera("droite", 90, 0), (90, 0, 90)),
        (VueCamera("dessus", 0, 90), (0, 0, 0)),
        (VueCamera("dessous", 0, -90), (180, 0, 0)),
    ],
)
def test_rotation_camera_compatible_avec_l_ancien_script(vue, attendu_degres):
    assert _proche(rotation_camera(vue), [math.radians(a) for a in attendu_degres])


def _direction_visee(rotation):
    """Direction -Z locale de la caméra après rotation Euler XYZ."""
    rx, _, rz = rotation  # ry vaut toujours 0
    # Rx puis Rz appliqués à (0, 0, -1)
    x, y, z = 0.0, math.sin(rx), -math.cos(rx)
    return (x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz), z)


def test_la_camera_vise_l_origine_pour_chaque_vue():
    for vue in VUES_DIAGONALES_4:
        position = position_camera(vue, 1.0)
        vers_origine = tuple(-c for c in position)
        assert _proche(_direction_visee(rotation_camera(vue)), vers_origine)


def test_distance_camera_identique_a_l_ancien_calcul():
    fov = math.radians(39.6)
    assert math.isclose(distance_camera(fov, 2.0), 1.0 / math.tan(fov / 2) * 1.15)


def test_distance_camera_englobe_la_sphere_de_l_objet():
    """Un objet de diagonale 2 tient dans une sphère de rayon 1, qui doit être dans le champ."""
    fov = math.radians(39.6)
    assert distance_camera(fov, 2.0) >= 1.0 / math.sin(fov / 2)
