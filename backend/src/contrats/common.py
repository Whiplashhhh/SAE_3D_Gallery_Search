"""
@author:  AR

Types annotés (str avec leurs règles de validation) réutilisables par tous les contrats.

Types réutilisables partout ailleurs.
"""

from pathlib import PurePosixPath
from typing import Annotated

from pydantic import AfterValidator, StringConstraints

# identifiants

Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
"""Identifiant SHA-256 à partir du fichier 3D source : 64 caracteres hex minuscules."""

IdModele = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{16}$")]
"""Identifiant stable d'un modèle : les 16 premiers caractères du sha256."""


# Chemins

def _verifier_chemin_relatif(valeur: str) -> str:
    """Refuse les chemins absolus ou qui remonte hors du depot."""
    if valeur.startswith("/"):
        raise ValueError("chemin absolu interdit : il doit être relatif a la racine du depot")
    if ".." in PurePosixPath(valeur).parts:
        raise ValueError("remontée interdite : le chemin ne doit pas contenir '..'")
    return valeur


CheminRelatif = Annotated[
    str,
    StringConstraints(min_length=1, strip_whitespace=True),
    AfterValidator(_verifier_chemin_relatif),
]
"""Chemin relatif a la racine du depot."""

# Noms de vues

NomVue = Annotated[str, StringConstraints(pattern=r"^[a-z0-9_]{1,32}$")]
"""Nom court d'une prise de vue. Sert de nom de fichier donc ASCII minuscule,
chiffres et underscore uniquement, sans accent ni espace."""


# Textes

TexteNonVide = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
"""Texte libre généré par un modèle trim, jamais vide."""

MotCle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, to_lower=True, min_length=1, max_length=64),
]
"""Mot-clé de recherche : minuscules, sert de métadonnée pour ChromaDB."""


CodeEvenement = Annotated[str, StringConstraints(pattern=r"^[a-z0-9_]{1,64}$")]
"""Code machine d'un evenement (ex: json_malforme_relance). Sert a compter et
filtrer : il doit etre stable et reutilise a l'identique, pas reformule."""
