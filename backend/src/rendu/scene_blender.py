"""
@author: AR

Opérations sur la scène Blender : nettoyage, import, couleurs, normalisation,
caméra, lumière et rendu des vues.

Ce module importe bpy : il ne s'exécute que dans Blender (voir script_blender.py).
Les calculs purs sont dans vues.py et normalisation.py.
"""

import os

import bpy
import mathutils

from rendu.normalisation import TAILLE_CIBLE, boite_englobante, facteur_echelle
from rendu.textures import dossier_racine_modele, indexer_images, retrouver_image
from rendu.vues import VueCamera, distance_camera, position_camera, rotation_camera


PALETTE_PIECES: tuple[tuple[float, float, float, float], ...] = (
    (1.0, 0.0, 0.0, 1.0),  # Rouge pur
    (0.0, 0.0, 1.0, 1.0),  # Bleu pur
    (0.0, 1.0, 0.0, 1.0),  # Vert pur
    (1.0, 1.0, 0.0, 1.0),  # Jaune pur
    (1.0, 0.0, 1.0, 1.0),  # Magenta pur
    (0.0, 1.0, 1.0, 1.0),  # Cyan pur
    (1.0, 0.5, 0.0, 1.0),  # Orange vif
    (0.5, 0.0, 0.5, 1.0),  # Violet
)
"""Couleurs ultra-saturées : chaque pièce indépendante est bien distincte pour le VLM."""


def _importer_obj(chemin: str) -> None:
    bpy.ops.wm.obj_import(filepath=chemin)


def _importer_stl(chemin: str) -> None:
    bpy.ops.wm.stl_import(filepath=chemin)


def _importer_gltf(chemin: str) -> None:
    bpy.ops.import_scene.gltf(filepath=chemin)


def _importer_fbx(chemin: str) -> None:
    bpy.ops.import_scene.fbx(filepath=chemin)


IMPORTEURS = {
    ".obj": _importer_obj,
    ".stl": _importer_stl,
    ".glb": _importer_gltf,
    ".gltf": _importer_gltf,
    ".fbx": _importer_fbx,
}


def nettoyer_scene() -> None:
    """Supprime tous les objets de la scène de démarrage (cube, caméra, lampe...)."""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def importer_modele(chemin: str) -> list:
    """Importe le fichier 3D et retourne les objets créés."""
    extension = os.path.splitext(chemin)[1].lower()
    if extension not in IMPORTEURS:
        raise ValueError(f"format non supporté : {extension}")

    avant = set(bpy.context.scene.objects)
    IMPORTEURS[extension](chemin)
    importes = [obj for obj in bpy.context.scene.objects if obj not in avant]

    if not any(obj.type == "MESH" for obj in importes):
        raise ValueError(f"aucun maillage trouvé dans {chemin}")
    return importes


def _image_disponible(image) -> bool:
    """Image intégrée au fichier (glb), générée, ou présente sur le disque."""
    if image.source != "FILE" or image.packed_file:
        return True
    return os.path.exists(bpy.path.abspath(image.filepath))


def _noeuds_images(materiau) -> list:
    if not materiau or not materiau.use_nodes:
        return []
    return [noeud for noeud in materiau.node_tree.nodes if noeud.type == "TEX_IMAGE" and noeud.image]


def relier_textures(chemin_modele: str, maillages: list) -> None:
    """Retrouve dans le dossier du modèle les images dont le chemin est faux.

    Une image toujours introuvable est débranchée : Blender l'afficherait
    en rose. Le matériau garde alors sa couleur de base.
    """
    index = None
    for obj in maillages:
        for materiau in obj.data.materials:
            for noeud in _noeuds_images(materiau):
                image = noeud.image
                if _image_disponible(image):
                    continue
                if index is None:  # on ne parcourt le disque que si une image manque
                    index = indexer_images(dossier_racine_modele(chemin_modele))
                trouve = retrouver_image(image.filepath, index)
                if trouve:
                    image.filepath = trouve
                    image.reload()
                else:
                    print(f"Texture introuvable : {image.filepath}")
                    for sortie in noeud.outputs:
                        for lien in list(sortie.links):
                            materiau.node_tree.links.remove(lien)


def _images_en_amont(prise, deja_vus: set) -> list:
    """Images qui alimentent une entrée de nœud, même à travers des nœuds Mix."""
    images = []
    for lien in prise.links:
        noeud = lien.from_node
        if noeud in deja_vus:
            continue
        deja_vus.add(noeud)
        if noeud.type == "TEX_IMAGE" and noeud.image:
            images.append(noeud.image)
        for entree in noeud.inputs:
            images.extend(_images_en_amont(entree, deja_vus))
    return images


def a_des_textures(maillages: list) -> bool:
    """Vrai si au moins un matériau tire sa couleur de base d'une image disponible."""
    for obj in maillages:
        for materiau in obj.data.materials:
            if not materiau or not materiau.use_nodes:
                continue
            # Recherche par type : les importeurs ne nomment pas tous le nœud "Principled BSDF"
            for bsdf in materiau.node_tree.nodes:
                if bsdf.type != "BSDF_PRINCIPLED":
                    continue
                images = _images_en_amont(bsdf.inputs["Base Color"], set())
                if any(_image_disponible(image) for image in images):
                    return True
    return False


def separer_pieces(objets: list) -> list:
    """Sépare chaque maillage en ses pièces indépendantes (parties non reliées).
    Retourne tous les maillages de la scène après séparation."""
    maillages = [obj for obj in objets if obj.type == "MESH"]

    bpy.ops.object.select_all(action="DESELECT")
    for obj in maillages:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = maillages[0]

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")

    return [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]


def colorer_pieces(maillages: list) -> None:
    """Donne à chaque pièce une couleur de la palette (en boucle)."""
    for idx, obj in enumerate(maillages):
        mat = bpy.data.materials.new(name=f"Mat_{obj.name}")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = PALETTE_PIECES[idx % len(PALETTE_PIECES)]
            bsdf.inputs["Roughness"].default_value = 0.3

        obj.data.materials.clear()
        obj.data.materials.append(mat)


def normaliser(maillages: list, taille_cible: float = TAILLE_CIBLE) -> None:
    """Centre le modèle en (0, 0, 0) et ramène sa diagonale à taille_cible.

    Toutes les pièces sont rattachées à un conteneur vide placé au centre de
    la boîte englobante, puis c'est le conteneur qu'on déplace et redimensionne :
    les pièces ne se désolidarisent pas.
    """
    boite = boite_englobante(
        tuple(obj.matrix_world @ mathutils.Vector(coin))
        for obj in maillages
        for coin in obj.bound_box
    )

    conteneur = bpy.data.objects.new("Conteneur", None)
    bpy.context.collection.objects.link(conteneur)
    conteneur.location = boite.centre
    bpy.context.view_layer.update()

    # On ne rattache que les racines, pour garder la hiérarchie d'un glTF/FBX
    racines = [obj for obj in bpy.context.scene.objects if obj.parent is None and obj is not conteneur]
    for obj in racines:
        obj.parent = conteneur
        obj.matrix_parent_inverse = conteneur.matrix_world.inverted()

    conteneur.location = (0.0, 0.0, 0.0)
    facteur = facteur_echelle(boite.diagonale, taille_cible)
    conteneur.scale = (facteur, facteur, facteur)

    bpy.context.view_layer.update()
    print(f"Normalisation terminée -> diagonale {taille_cible} et centre en 0,0,0")


def creer_camera():
    """Crée la caméra de rendu et une lampe frontale sans ombres qui la suit."""
    scene = bpy.context.scene

    cam = bpy.data.objects.new("Camera_IA", bpy.data.cameras.new("Camera_IA"))
    bpy.context.collection.objects.link(cam)
    scene.camera = cam

    lumiere_data = bpy.data.lights.new(name="Lumiere_Frontale", type="SUN")
    lumiere_data.energy = 2.5
    lumiere_data.use_shadow = False

    lumiere = bpy.data.objects.new(name="Lumiere_Frontale", object_data=lumiere_data)
    bpy.context.collection.objects.link(lumiere)
    lumiere.parent = cam
    lumiere.rotation_euler = (0.0, 0.0, 0.0)

    return cam


def configurer_rendu(resolution: int) -> None:
    """Fond blanc pur, couleurs non retouchées et sortie PNG carrée."""
    scene = bpy.context.scene

    if scene.world is None:
        scene.world = bpy.data.worlds.new("Monde")
    scene.world.use_nodes = True
    fond = scene.world.node_tree.nodes.get("Background")
    if fond:
        fond.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)

    scene.view_settings.view_transform = "Standard"

    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False


def rendre_vue(cam, vue: VueCamera, chemin_png: str, taille_cible: float = TAILLE_CIBLE) -> None:
    """Place la caméra sur la vue demandée et écrit le PNG."""
    rayon = distance_camera(cam.data.angle, taille_cible)
    cam.location = position_camera(vue, rayon)
    cam.rotation_euler = rotation_camera(vue)
    bpy.context.view_layer.update()

    bpy.context.scene.render.filepath = chemin_png
    print(f"Calcul de l'image : {vue.nom}...")
    bpy.ops.render.render(write_still=True)


def version_moteur() -> str:
    """Ex : 'blender-5.2.0' (champ moteur du manifeste)."""
    return "blender-" + ".".join(str(n) for n in bpy.app.version)
