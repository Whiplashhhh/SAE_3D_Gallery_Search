"""
@author:  AR

Dézippe les archives de modèles 3D (zip imbriqués compris, sans les supprimer)
et liste les fichiers 3D exploitables pour le rendu.
"""

import os
import zipfile
from typing import Final


class FileHandler :

    __valid_extensions: Final[tuple[str, ...]] = (".glb", ".gltf", ".stl", ".obj", ".fbx") # TODO: Mettre dans .env


    @staticmethod
    def extract_files(folder_path: str) -> list[str] :
        """Retourne les chemins complets des modèles 3D trouvés dans le dossier (récursif)."""

        valid_files: list[str] = []

        for root, _, files in os.walk(folder_path) :
            for file in files :
                if file.lower().endswith(FileHandler.__valid_extensions) :
                    valid_files.append(os.path.join(root, file))

        return valid_files



    @staticmethod
    def unzip_folder(zip_path: str) -> str | None :
        """Dézippe l'archive à côté d'elle, dans un dossier du même nom (sans .zip).
        Les zip imbriqués sont aussi dézippés. Les archives ne sont jamais supprimées."""

        if not zipfile.is_zipfile(zip_path) :
            return None

        folder_destination: str = os.path.splitext(zip_path)[0]

        try :
            with zipfile.ZipFile(zip_path) as z :
                z.extractall(folder_destination)
        except (zipfile.BadZipFile, OSError) :
            return None

        for root, _, files in os.walk(folder_destination) :
            for file in files :
                if file.lower().endswith(".zip") :
                    FileHandler.unzip_folder(os.path.join(root, file))

        return folder_destination



    @staticmethod
    def unzip_all(folder_path: str) -> list[str] :
        """Dézippe toutes les archives .zip présentes directement dans le dossier."""

        extracted: list[str] = []

        for file in sorted(os.listdir(folder_path)) :
            if file.lower().endswith(".zip") :
                destination: str | None = FileHandler.unzip_folder(os.path.join(folder_path, file))
                if destination is not None :
                    extracted.append(destination)

        return extracted



if __name__ == "__main__" :
    model_folder: str = os.path.join(os.path.dirname(__file__), "..", "..", "..", "model_3d")

    for folder in FileHandler.unzip_all(model_folder) :
        print(os.path.basename(folder), FileHandler.extract_files(folder))
