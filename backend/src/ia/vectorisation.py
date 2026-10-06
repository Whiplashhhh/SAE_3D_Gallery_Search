import hashlib
import re
from collections import Counter

VOCABULAIRE = {
    "maison",
    "architecture",
    "chateau",
    "villa",
    "table",
    "chaise",
    "meuble",
    "bureau",
    "lampe",
    "voiture",
    "vehicule",
    "sport",
    "dragster",
    "route",
    "nature",
    "forêt",
    "forest",
    "arbre",
    "plante",
    "jungle",
    "animal",
    "dragon",
    "serpent",
    "chien",
    "oiseau",
    "personnage",
    "robot",
    "statue",
    "sculpture",
    "art",
    "design",
    "paysage",
    "terrain",
    "objet",
    "cadeau",
    "boite",
    "musique",
    "sonore",
    "console",
    "console_jeu",
    "jeu",
    "fantasy",
    "moderne",
    "ancien",
    "classique",
    "minimal",
    "futuriste",
    "vintage",
}


def vectoriser_texte(texte: str, dimensions: int = 768) -> list[float]:
    if not texte:
        return [0.0] * dimensions

    tokens = [token for token in re.findall(r"[a-zA-Z0-9_àâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ-]+", texte.lower()) if token]
    if not tokens:
        return [0.0] * dimensions

    counts = Counter(tokens)
    vecteur = [0.0] * dimensions

    for token, frequence in counts.items():
        index = int(hashlib.sha1(token.encode("utf-8")).hexdigest(), 16) % dimensions
        vecteur[index] += float(frequence)

        if token in VOCABULAIRE:
            vecteur[abs(hash(token)) % dimensions] += 0.5

    norme = sum(val * val for val in vecteur) ** 0.5
    if norme > 0:
        return [val / norme for val in vecteur]
    return vecteur
