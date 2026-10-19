"""
@author: AR

Tests pour FileHandler : dézippage des archives et listage des modèles 3D.
"""

import os
import zipfile

from rendu.FileHandler import FileHandler


def _creer_fichier(chemin: str, donnees: bytes = b"") -> str:
    """Crée un fichier (et ses dossiers parents) avec le contenu donné."""
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "wb") as fichier:
        fichier.write(donnees)
    return chemin


def _creer_zip(chemin: str, contenu: dict[str, bytes]) -> str:
    """Crée une archive zip contenant les fichiers donnés (nom -> octets)."""
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with zipfile.ZipFile(chemin, "w") as archive:
        for nom, donnees in contenu.items():
            archive.writestr(nom, donnees)
    return chemin


def _noms(chemins: list[str]) -> set[str]:
    return {os.path.basename(chemin) for chemin in chemins}


# extract_files

def test_extract_files_trouve_toutes_les_extensions(tmp_path):
    dossier = str(tmp_path)
    for nom in ("a.glb", "b.gltf", "c.stl", "d.obj", "e.fbx"):
        _creer_fichier(os.path.join(dossier, nom))

    assert _noms(FileHandler.extract_files(dossier)) == {
        "a.glb", "b.gltf", "c.stl", "d.obj", "e.fbx"
    }


def test_extract_files_ignore_les_autres_fichiers(tmp_path):
    dossier = str(tmp_path)
    for nom in ("modele.obj", "texture.png", "modele.mtl", "lisezmoi.txt", "archive.zip"):
        _creer_fichier(os.path.join(dossier, nom))

    assert _noms(FileHandler.extract_files(dossier)) == {"modele.obj"}


def test_extract_files_insensible_a_la_casse(tmp_path):
    dossier = str(tmp_path)
    _creer_fichier(os.path.join(dossier, "MAJUSCULE.OBJ"))
    _creer_fichier(os.path.join(dossier, "Mixte.Glb"))

    assert _noms(FileHandler.extract_files(dossier)) == {"MAJUSCULE.OBJ", "Mixte.Glb"}


def test_extract_files_recursif_et_chemins_complets(tmp_path):
    dossier = str(tmp_path)
    chaise = _creer_fichier(os.path.join(dossier, "a", "b", "c", "chaise.obj"))

    assert FileHandler.extract_files(dossier) == [chaise]


def test_extract_files_dossier_vide(tmp_path):
    assert FileHandler.extract_files(str(tmp_path)) == []


def test_extract_files_dossier_inexistant(tmp_path):
    assert FileHandler.extract_files(os.path.join(str(tmp_path), "inexistant")) == []


# unzip_folder

def test_unzip_folder_extrait_a_cote_de_l_archive(tmp_path):
    dossier = str(tmp_path)
    archive = _creer_zip(os.path.join(dossier, "chaise.zip"), {"chaise.obj": b"v 0 0 0"})

    destination = FileHandler.unzip_folder(archive)

    assert destination == os.path.join(dossier, "chaise")
    with open(os.path.join(dossier, "chaise", "chaise.obj"), "rb") as fichier:
        assert fichier.read() == b"v 0 0 0"


def test_unzip_folder_conserve_l_archive(tmp_path):
    archive = _creer_zip(os.path.join(str(tmp_path), "chaise.zip"), {"chaise.obj": b""})

    FileHandler.unzip_folder(archive)

    assert os.path.exists(archive)


def test_unzip_folder_conserve_l_arborescence(tmp_path):
    dossier = str(tmp_path)
    archive = _creer_zip(
        os.path.join(dossier, "voiture.zip"),
        {"source/voiture.fbx": b"", "textures/peinture.png": b""},
    )

    FileHandler.unzip_folder(archive)

    assert os.path.exists(os.path.join(dossier, "voiture", "source", "voiture.fbx"))
    assert os.path.exists(os.path.join(dossier, "voiture", "textures", "peinture.png"))


def test_unzip_folder_dezippe_les_zip_imbriques(tmp_path):
    dossier = str(tmp_path)
    interne = _creer_zip(os.path.join(dossier, "travail", "interne.zip"), {"maison.glb": b""})
    with open(interne, "rb") as fichier:
        octets_interne = fichier.read()
    archive = _creer_zip(os.path.join(dossier, "externe.zip"), {"sous/interne.zip": octets_interne})

    FileHandler.unzip_folder(archive)

    assert os.path.exists(os.path.join(dossier, "externe", "sous", "interne", "maison.glb"))
    # le zip imbriqué est lui aussi conservé
    assert os.path.exists(os.path.join(dossier, "externe", "sous", "interne.zip"))


def test_unzip_folder_refuse_un_faux_zip(tmp_path):
    dossier = str(tmp_path)
    faux = _creer_fichier(os.path.join(dossier, "faux.zip"), b"ceci n'est pas une archive")

    assert FileHandler.unzip_folder(faux) is None
    assert not os.path.exists(os.path.join(dossier, "faux"))


def test_unzip_folder_fichier_absent(tmp_path):
    assert FileHandler.unzip_folder(os.path.join(str(tmp_path), "absent.zip")) is None


# unzip_all

def test_unzip_all_dezippe_toutes_les_archives_triees(tmp_path):
    dossier = str(tmp_path)
    _creer_zip(os.path.join(dossier, "b.zip"), {"b.obj": b""})
    _creer_zip(os.path.join(dossier, "a.zip"), {"a.obj": b""})

    assert FileHandler.unzip_all(dossier) == [
        os.path.join(dossier, "a"),
        os.path.join(dossier, "b"),
    ]


def test_unzip_all_ignore_les_fichiers_non_zip(tmp_path):
    dossier = str(tmp_path)
    _creer_zip(os.path.join(dossier, "ok.zip"), {"ok.obj": b""})
    _creer_fichier(os.path.join(dossier, "modele.obj"))
    _creer_fichier(os.path.join(dossier, "faux.zip"), b"pas une archive")

    assert FileHandler.unzip_all(dossier) == [os.path.join(dossier, "ok")]


def test_unzip_all_ne_descend_pas_dans_les_sous_dossiers(tmp_path):
    dossier = str(tmp_path)
    _creer_zip(os.path.join(dossier, "sous_dossier", "cache.zip"), {"cache.obj": b""})

    assert FileHandler.unzip_all(dossier) == []
    assert not os.path.exists(os.path.join(dossier, "sous_dossier", "cache"))


def test_unzip_all_puis_extract_files(tmp_path):
    """Le scénario du __main__ : dézipper puis lister les modèles de chaque dossier."""
    dossier = str(tmp_path)
    _creer_zip(os.path.join(dossier, "chat.zip"), {"chat.obj": b"", "chat.mtl": b""})

    dossiers = FileHandler.unzip_all(dossier)

    assert [_noms(FileHandler.extract_files(d)) for d in dossiers] == [{"chat.obj"}]
