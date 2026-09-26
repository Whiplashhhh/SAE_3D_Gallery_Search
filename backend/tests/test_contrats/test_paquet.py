"""
@author:  WV

Fichier de tests liés imports
"""

import contrats


def test_import_depuis_le_paquet():
    """Les lots doivent pouvoir tout importer depuis `contrats`"""
    from contrats import FicheModele, ManifesteRendu, charger_manifeste, ecrire_json

    assert ManifesteRendu is not None
    assert FicheModele is not None
    assert callable(charger_manifeste)
    assert callable(ecrire_json)


def test_all_est_coherent():
    """Tout ce qui est annoncé dans __all__ existe réellement"""
    manquants = [nom for nom in contrats.__all__ if not hasattr(contrats, nom)]
    assert manquants == []


def test_version_des_contrats_alignee_sur_les_seeds():
    """La version du paquet doit correspondre à celle des fichiers de référence"""
    from pathlib import Path

    from contrats import VERSION_CONTRATS, charger_manifeste

    seed = Path(__file__).parents[2] / "seed" / "manifestes" / "chaise_bureau.json"
    assert charger_manifeste(seed).version == VERSION_CONTRATS