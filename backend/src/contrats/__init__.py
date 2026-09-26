"""
@author : WV

Contrats d'échange entre les lots du projet

Les lots ne partagent aucun code métier : ils communiquent uniquement par des
fichiers JSON, décrits et validés ici

manifeste_rendu.json   Lot A -> Lot B    ManifesteRendu
fiche_modele.json      Lot B -> Lot C    FicheModele
indexation.jsonl       les trois lots    EntreeJournal

Tout s'importe depuis ce paquet, jamais depuis les modules internes, ex :

    from contrats import FicheModele, charger_manifeste, ecrire_json
"""

from contrats.common import (
    CheminRelatif,
    CodeEvenement,
    IdModele,
    MotCle,
    NomVue,
    Sha256,
    TexteNonVide,
)
from contrats.fiche import (
    DescriptionVue,
    DureeMs,
    Embedding,
    EtatModele,
    FicheModele,
)
from contrats.io import (
    ContratInvalide,
    charger,
    charger_fiche,
    charger_manifeste,
    deja_traite,
    ecrire_json,
)
from contrats.journal import EntreeJournal, Lot, Niveau, journaliser, lire_journal
from contrats.manifeste import ManifesteRendu, Vue

VERSION_CONTRATS = "1.0"
"""Version des contrats. Doit correspondre au champ "version" des fichiers JSON.
A incrementer si un changement casse la compatibilité avec les fichiers déjà
produits."""

__all__ = [ # définit le 'import *'
    # Modèles
    "ManifesteRendu",
    "Vue",
    "FicheModele",
    "DescriptionVue",
    "Embedding",
    "DureeMs",
    "EntreeJournal",
    # Types et énumerations
    "Sha256",
    "IdModele",
    "CheminRelatif",
    "NomVue",
    "MotCle",
    "TexteNonVide",
    "CodeEvenement",
    "EtatModele",
    "Lot",
    "Niveau",
    # Lecture / écriture
    "charger",
    "charger_manifeste",
    "charger_fiche",
    "ecrire_json",
    "deja_traite",
    "journaliser",
    "lire_journal",
    "ContratInvalide",
    # Divers
    "VERSION_CONTRATS",
]