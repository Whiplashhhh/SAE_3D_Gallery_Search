# Sprint 4 — Rendu des vues diagonales, pipeline du Lot B, `main` au vert

**Période** : 23/11/2026 → 30/11/2026
**Commit de référence** : 2ff3523
**Membres :** Willem V. (WV) · Alex R. (AR) · Hugo S. (HS)

## Bilan du sprint précédent

Commits analysés : du 09/11/2026 au 23/11/2026, sur toutes les branches (`main`, `lotA`,
`lotb/US_3.4`, `US-3.6`, `pull_request`). Le commit de référence du sprint 3 (`8fa3b89`, 22/10)
est antérieur à l'écriture du sprint : la plage `8fa3b89..HEAD` ramenait `dbbe9a8`, `14fae9f`
(19/10) et `0b8d596` (06/10), déjà comptés au sprint 2. Le découpage a donc été fait par date
(`--since=2026-11-09`). Aucun commit après le 15/11.

| US | Statut | Commits liés |
|----|--------|--------------|
| US 3.1 — Routes en double retirées, README à jour | 🟡 Partielle | 1887f59 (PR #11) : le `README.md` et `docs/` décrivent le lancement Docker/Ollama et la page détail. Mais `POST /search` et `GET /health` sont toujours dans `recherche/router.py` (l. 84 et 223), et `frontend/readeMeLotC.md` existe toujours |
| US 3.2 — Extensions hors de `FileHandler`, modèles de test, `lotA` fusionnée | 🟡 Partielle | Aucun commit sur ce point. `lotA` a 5 commits absents de `main` (pas fusionnée), extensions toujours en dur (`# TODO: Mettre dans .env`), pas de dossier `donnees/modeles/` |
| US 3.3 — `script_blender.py` rend `face.png` | 🟡 Partielle | 6b46da7 : `rendu/vues.py` (catalogue de vues et placement caméra) + `test_vues.py`. 0362a3b : `rendu/normalisation.py` (mise à l'échelle par boîte englobante) + tests. Ces briques sont testées, mais `script_blender.py` est toujours vide sur `lotA` et aucun rendu n'est produit. **À noter** : `vues.py` remplace la vue de face par 2 vues diagonales (`VUES_DIAGONALES_2`), choix non encore consigné dans `docs/DECISION.md` |
| US 3.4 — `fusionner_descriptions()` | ✅ Faite | 36bdaf0 (`SortieFusionLlm` strict + tests), 28cc80c (`semantique/fusion.py`, `prompts/fusion.md`, `tests/test_semantique/test_fusion.py`), fusionnés dans `main` par 2ff3523 |
| US 3.5 — `vectoriser()` avec contrôle de dimension | ❌ Non commencée | Aucun commit. `semantique/` ne contient pas de `vectoriser()` (seul `ia/vectorisation.py`, le vecteur local du Lot C, existe) |
| US 3.6 — Page détail `/modeles/:id` | 🟡 Partielle | 63c63f6 (page `ModelDetailView.vue`, route `GET /api/modeles/{id}`), fusionné par 150a379 (PR #9), c738624 (PR #10), cfba6a6 (PR #11). Fonctionnalité livrée, mais la DoD n'est pas tenue : sur `main`, `uv run pytest` donne **2 échecs** (`test_api_modele_existant_repond_200`, `test_api_modele_absent_repond_404` : `'State' object has no attribute 'models_dir'`), la fixture de test ne renseigne pas `app.state.models_dir`. La capture manuelle n'est pas vérifiable depuis l'historique |

**Hors sprint** (commits non rattachés à une US) :
- 835f89c (WV) — `docs/monitoring/sprint-03.md`.
- 2487e18, 7873b4d (WV) — documentation MkDocs et déploiement sur GitHub Pages (`.github/workflows/docs.yml`, `docs/reference/`).
- b4ad664 (AR) — `.gitignore`.
- 1312908 (HS) — Docker : Ollama local dans `docker-compose.yml`, script `scripts/preparer_donnees_demo.py` qui vectorise les fiches de seed.

**Synthèse** : 11 commits (hors merges) — WV 5 · AR 3 · HS 3. Par lot : Lot A 2 · Lot B 2 · Lot C 1 ·
Commun 6 (docs, CI, Docker). 1 US sur 6 terminée, 4 partielles, 1 non commencée. Le Lot B a sa
fusion LLM dans `main` et le Lot C sa page détail. Le Lot A avance (normalisation, caméra) mais
toujours sans rendu ni fusion dans `main`. `main` n'est plus au vert (2 tests en échec). Aucun
commit depuis le 15/11.

## User Stories

### Commun

**US 4.1** (HS) — *Fin des US 3.1 et 3.6.* En tant qu'équipe, `uv run pytest` passe à nouveau intégralement sur `main` : la fixture de `tests/test_recherche/test_api.py` renseigne `models_dir` (dossier temporaire), ou la route le lit depuis la configuration. Dans le même temps, les routes en double `POST /api/search` et `GET /api/health` sont retirées et `frontend/readeMeLotC.md` est fusionné dans le `README.md`.
*Vérification* : `uv run pytest` passe sans échec, `grep -rn '"/search"\|"/health"' backend/src` ne renvoie rien, `ls frontend/readeMeLotC.md` échoue.

### Lot A — Rendu multi-vues (AR)

**US 4.2** — *Fin de l'US 3.2.* En tant que développeur du Lot A, `lotA` est remise à jour sur `main` puis fusionnée : extensions de `FileHandler` hors de la classe (constante de module ou `obtenir_config()`), 2 ou 3 petits modèles libres de droits dans `donnees/modeles/` avec `LICENCES.md`, et le passage de la vue de face aux 2 vues diagonales (`VUES_DIAGONALES_2`) consigné dans `docs/DECISION.md`.
*Vérification* : sur `main`, `uv run pytest tests/test_rendu/` passe, `ls donnees/modeles/` liste les modèles de test, `git log main..origin/lotA` est vide.

**US 4.3** — *Fin de l'US 3.3.* En tant que développeur du Lot A, `backend/src/rendu/script_blender.py` charge un modèle, le normalise avec `normalisation.py`, place la caméra avec `vues.py` et rend chaque vue de `VUES_DIAGONALES_2` en `RESOLUTION_RENDU` × `RESOLUTION_RENDU`.
*Vérification* : `blender --background --python src/rendu/script_blender.py -- <modele> <dossier_sortie>` produit `avant_droite_haut.png` et `arriere_gauche_haut.png`, modèle entier et centré, pour chaque modèle de l'US 4.2.

### Lot B — Description sémantique (WV)

**US 4.4** — *Report de l'US 3.5.* En tant que développeur du Lot B, je dispose d'une fonction `vectoriser(texte)` dans `semantique/` qui appelle `ClientOllama.embed()` et vérifie que la longueur du vecteur est égale à `dimension_embedding` de `obtenir_config()`. Sinon, elle lève une exception métier qui indique la dimension reçue et la dimension attendue.
*Vérification* : `uv run pytest tests/test_semantique/test_vectorisation.py` avec client simulé (bonne dimension, mauvaise dimension).

**US 4.5** — *Suite logique.* En tant que développeur du Lot B, je dispose d'une fonction `indexer_modele(manifeste)` qui prend un manifeste de rendu validé par `contrats` (`manifeste.py`), enchaîne `decrire_vue()` pour chaque vue, `fusionner_descriptions()` puis `vectoriser()`, et écrit une fiche validée par `FicheModele` dans le dossier des fiches lu par le Lot C.
*Vérification* : `uv run pytest tests/test_semantique/test_pipeline.py` avec client simulé et images factices : la fiche écrite se relit avec `FicheModele`, et un échec sur une vue est journalisé sans fiche partielle.

### Lot C — Recherche & interface (HS)

**US 4.6** — *Suite logique (reporté au sprint 4 par le sprint 3).* En tant qu'utilisateur, chaque résultat de recherche affiche un court extrait de la description (globale ou d'une vue) qui justifie le match, renvoyé par l'API dans `ResultatRecherche`.
*Vérification* : un test dans `tests/test_recherche/` vérifie la présence de l'extrait dans la réponse de `POST /api/recherche`, et `cd frontend && npm run build` passe.

## Livrables

- `main` au vert (`uv run pytest` sans échec), routes en double retirées, README unique.
- `lotA` fusionnée : extensions hors de la classe, modèles de test, décision sur les vues diagonales.
- `script_blender.py` qui rend les 2 vues diagonales.
- `vectoriser()` et `indexer_modele()` avec tests dans `backend/tests/test_semantique/`.
- Extrait justificatif dans les résultats de recherche.
- Nouvelles décisions ajoutées à `docs/DECISION.md`.

## DoR / DoD

**DoR** — L'US a un responsable et une commande de vérification. Ses entrées existent (seed, modèle de test ou contrat déjà présent dans `main`). Toute modification du socle commun (`contrats/`, `config.py`, `ollama/`) est annoncée aux deux autres membres avant d'être codée.

**DoD** — Le code est fusionné dans `main`. `uv run pytest` passe intégralement sans Ollama ni Blender. Aucune URL, aucun nom de modèle et aucune dimension d'embedding n'est écrit en dur (tout passe par `obtenir_config()`). Les chemins sont relatifs. Le code et les clés sont en français, sans accents. Les échanges entre lots passent uniquement par des JSON validés par `contrats`.

## Risques

- **`main` cassé** : une PR a été fusionnée avec 2 tests en échec. Avant chaque fusion, lancer `uv run pytest` sur la branche à jour ; l'US 4.1 est à faire en premier.
- **Lot A bloquant** : quatre sprints sans rendu, et `lotA` toujours pas fusionnée (base `988a764`, antérieure aux PR #7 à #11). Sans rendu, l'US 4.5 ne peut être testée qu'avec des images factices. Si l'US 4.3 bloque en milieu de semaine, l'équipe fait une séance commune dessus.
- **Décision non tracée** : le passage de la vue de face à 2 vues diagonales change ce que reçoit le Lot B ; il doit être écrit dans `docs/DECISION.md` avant la fusion de `lotA`.
- **Rythme** : aucun commit depuis le 15/11. La charge reste à 2 US par personne, et chaque US doit pouvoir être fusionnée seule.
- **Dimension en dur côté Lot C** : `ia/vectorisation.py` a `dimensions: int = 768` par défaut, contraire à la DoD. À remplacer par `dimension_embedding` lors d'un passage sur ce fichier.
- **Qualité des sorties LLM** : la fusion et la description dépendent du modèle configuré. Les tests restent avec client simulé ; un essai réel (Ollama de l'IUT ou Ollama local du `docker-compose.yml`) est conseillé mais ne fait pas partie de la DoD.
- **Blender** : version et chemin variables selon les machines (`BLENDER_BIN`). Les tests de rendu doivent être ignorés proprement si Blender est absent.
- **Front non testé automatiquement** : seule la compilation (`npm run build`) vérifie le front. Les régressions d'affichage ne sont détectées qu'à la main.

## Reste à faire / reporté au Sprint 5

- Lot A : orchestrateur qui écrit le manifeste de rendu, génère la vignette et saute les modèles déjà rendus.
- Lot B : brancher `indexer_modele()` sur les manifestes réels du Lot A.
- Lot C : indexer automatiquement dans ChromaDB les nouvelles fiches écrites par le Lot B.
- Premier test de bout en bout sur un modèle de `donnees/modeles/`.
