"""
@author: AR

Tests pour textures : dossier de recherche, index des images et
résolution des chemins cassés laissés par les FBX/OBJ.
"""

from pathlib import Path

import pytest

from rendu.textures import dossier_racine_modele, indexer_images, retrouver_image


@pytest.fixture
def modele_sketchfab(tmp_path) -> Path:
    """<modele>/source/House.fbx et <modele>/textures/*, comme dans model_3d."""
    racine = tmp_path / "maison"
    (racine / "source").mkdir(parents=True)
    (racine / "textures").mkdir()
    (racine / "source" / "House.fbx").write_bytes(b"")
    (racine / "textures" / "Texture.png").write_bytes(b"")
    (racine / "textures" / "sol_ao.jpeg").write_bytes(b"")
    (racine / "textures" / "notes.txt").write_bytes(b"")
    return racine


def test_racine_au_dessus_du_dossier_source(modele_sketchfab):
    chemin = modele_sketchfab / "source" / "House.fbx"
    assert dossier_racine_modele(chemin) == modele_sketchfab.resolve()


def test_racine_avec_sous_dossier_dans_source(tmp_path):
    chemin = tmp_path / "varina" / "source" / "varina" / "scene.gltf"
    assert dossier_racine_modele(chemin) == (tmp_path / "varina").resolve()


def test_racine_sans_dossier_source(tmp_path):
    chemin = tmp_path / "modeles" / "cube.obj"
    assert dossier_racine_modele(chemin) == (tmp_path / "modeles").resolve()


def test_index_ignore_les_fichiers_non_images(modele_sketchfab):
    index = indexer_images(modele_sketchfab)

    assert "texture.png" in index
    assert "notes.txt" not in index


def test_retrouve_un_chemin_windows_d_une_autre_machine(modele_sketchfab):
    index = indexer_images(modele_sketchfab)

    trouve = retrouver_image("G:\\3D\\SCS soft\\texture.png", index)

    assert trouve == str(modele_sketchfab / "textures" / "Texture.png")


def test_retrouve_un_chemin_relatif_blender(modele_sketchfab):
    index = indexer_images(modele_sketchfab)
    assert retrouver_image("//../textures/texture.png", index) is not None


def test_retrouve_une_image_convertie_dans_un_autre_format(modele_sketchfab):
    index = indexer_images(modele_sketchfab)

    trouve = retrouver_image("C:/export/sol_ao.png", index)

    assert trouve == str(modele_sketchfab / "textures" / "sol_ao.jpeg")


def test_image_introuvable(modele_sketchfab):
    index = indexer_images(modele_sketchfab)

    assert retrouver_image("kristen\\source\\beiguang.png", index) is None
    assert retrouver_image("", index) is None
