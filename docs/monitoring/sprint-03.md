# Sprint 3 — Fusionner le Lot A, premier rendu, fusion LLM & vectorisation du Lot B, page détail

**Période** : 09/11/2026 → 16/11/2026
**Commit de référence** : 8fa3b89
**Membres :** Willem V. (WV) · Alex R. (AR) · Hugo S. (HS)

## Bilan du sprint précédent

Commits analysés : du 19/10/2026 au 09/11/2026, sur toutes les branches (`main`, `LOT_B`,
`lotA`, `lotC`, `contrats`). La plage `a419002..HEAD` ramenait des commits du 06/10 et du
08/10 (`lotC`, `LOT_C`) qui ne descendent pas de `a419002` et étaient déjà comptés au sprint 2 :
le découpage a donc été fait par date (`--since=2026-10-19`). Aucun commit après le 22/10.

| US | Statut | Commits liés |
|----|--------|--------------|
| US 2.1 — `uv run pytest` sans option | ✅ Faite | 70066e9 (PR #4) : `pytest` et `ruff` dans `[dependency-groups] dev`. `uv run pytest` → 97 tests passent |
| US 2.2 — Client Ollama commun | ✅ Faite | c943897 (PR #6) : `chat()`, nouvelles tentatives (`OLLAMA_TENTATIVES`), client construit depuis `obtenir_config()` dans `main.py`, `tests/test_ollama/test_client.py`. Répartition des tentatives notée en D28 |
| US 2.3 — Script `mesurer_dimension.py` | ✅ Faite | c943897 : `backend/scripts/mesurer_dimension.py` + commentaire `# DIMENSION_EMBEDDING=768` dans `.env.example`. L'exécution sur l'Ollama de l'IUT n'est pas vérifiable depuis l'historique |
| US 2.4 — Fin de la fusion du Lot C | 🟡 Partielle | c943897 + PR #6 : `contrats/schemas/fiche.py` supprimé, plus aucun `schemas.fiche`, `abb6ffa` (docstrings) est dans `main`. Mais les routes en double `POST /search` et `GET /health` sont toujours là alors que le front ne les appelle pas (`/models` et `/models/upload` restent, le front les utilise) |
| US 2.5 — Modèles de test + `FileHandler` testé | 🟡 Partielle | dbbe9a8 : `tests/test_rendu/test_file_handler.py`. Reste **uniquement sur `lotA`** (pas fusionné), extensions toujours en dur (`TODO: Mettre dans .env`), aucun fichier dans `donnees/modeles/` |
| US 2.6 — `script_blender.py` (vue de face) | ❌ Non commencée | `src/rendu/script_blender.py` est toujours vide sur `lotA` |
| US 2.7 — `SortieVueVlm` + `vue.md` dans `main` | ✅ Faite | a419002 fusionné par la PR #5, décision D27 dans `docs/DECISION.md` |
| US 2.8 — `decrire_vue()` | ✅ Faite | 0ca48ff (PR #5) : `semantique/vue.py` (appel via `ClientOllama.chat()`, nouvelle tentative, `journaliser()` dans `indexation.jsonl`) + `tests/test_semantique/test_vue.py`. L'essai manuel sur l'Ollama de l'IUT n'est pas vérifiable depuis l'historique |

**Hors sprint** (commits non rattachés à une US) :
- 2e2996f (HS, 21/10) — Lot C : aperçu 3D interactif (`ModelViewer.vue`) dans la page d'ajout de modèle, nouvelle dépendance front, et un fichier `frontend/readeMeLotC.md` (nom mal orthographié).
- 0c72a09 (WV) — `docs/monitoring/sprint-02.md`.

**Synthèse** : 6 commits (hors merges) — WV 3 · HS 2 · AR 1. Par lot : Lot A 1 · Lot B 1 · Lot C 1 ·
Commun 3 (c943897 touche à la fois le socle commun et `recherche/`). 5 US sur 8 terminées,
2 partielles, 1 non commencée. Le socle commun (client Ollama, dépendances, contrat unique) est
en place et les Lots B et C sont fusionnés dans `main`. Le Lot A n'a toujours rien dans `main`
et aucun rendu. Aucun commit depuis le 22/10 (plus de deux semaines).

## User Stories

### Commun

**US 3.1** (HS) — *Fin de l'US 2.4 + reporté du sprint 2.* En tant qu'équipe, les routes en double qui ne sont plus appelées par le front (`POST /api/search`, `GET /api/health`) sont retirées, et le `README.md` décrit l'arborescence et les commandes actuelles (`uv sync`, `uv run pytest`, lancement du back et du front, `scripts/mesurer_dimension.py`). `frontend/readeMeLotC.md` est renommé ou fusionné dans le README.
*Vérification* : `uv run pytest` passe, `grep -rn '"/search"\|"/health"' backend/src` ne renvoie rien, et les commandes du README fonctionnent telles quelles depuis un clone propre.

### Lot A — Rendu multi-vues (AR)

**US 3.2** — *Fin de l'US 2.5.* En tant que développeur du Lot A, les extensions acceptées par `FileHandler` ne sont plus écrites en dur dans la classe (constante de module ou champ de `obtenir_config()`), 2 ou 3 petits modèles libres de droits d'échelles très différentes sont dans `donnees/modeles/` (licence notée dans un `LICENCES.md`), et `lotA` est fusionnée dans `main`.
*Vérification* : sur `main`, `uv run pytest tests/test_rendu/` passe et `ls donnees/modeles/` liste les modèles de test.

**US 3.3** — *Report de l'US 2.6.* En tant que développeur du Lot A, `backend/src/rendu/script_blender.py` charge un modèle, le centre et le met à l'échelle grâce à sa boîte englobante, puis rend la vue de face en `RESOLUTION_RENDU` × `RESOLUTION_RENDU`.
*Vérification* : `blender --background --python src/rendu/script_blender.py -- <modele> <dossier_sortie>` produit `face.png`, avec un modèle entier et centré pour chaque modèle de l'US 3.2.

### Lot B — Description sémantique (WV)

**US 3.4** — *Suite de l'US 2.8.* En tant que développeur du Lot B, je dispose d'une fonction `fusionner_descriptions(descriptions)` qui envoie les `SortieVueVlm` de toutes les vues au LLM (`MODELE_LLM`, via `ClientOllama.chat()`) avec un prompt `prompts/fusion.md`, et renvoie une description globale et la liste `divergences_entre_vues`, validées par un modèle Pydantic strict. Les échecs suivent la même règle que `decrire_vue()` (D28).
*Vérification* : `uv run pytest tests/test_semantique/test_fusion.py` avec client simulé (réponse valide, JSON invalide puis nouvelle tentative et ligne de journal, épuisement des tentatives).

**US 3.5** — *Suite logique.* En tant que développeur du Lot B, je dispose d'une fonction `vectoriser(texte)` qui appelle `ClientOllama.embed()` et vérifie que la longueur du vecteur est égale à `dimension_embedding` de `obtenir_config()`. Sinon, elle lève une exception métier qui indique la dimension reçue et la dimension attendue.
*Vérification* : `uv run pytest tests/test_semantique/test_vectorisation.py` avec client simulé (bonne dimension, mauvaise dimension).

### Lot C — Recherche & interface (HS)

**US 3.6** — *Reporté du sprint 2.* En tant qu'utilisateur, en cliquant sur un résultat de recherche, j'arrive sur une page détail (`/modeles/:id`) qui affiche le nom, la description globale, la description de chaque vue (`par_vue`) et les divergences, à partir de `GET /api/modeles/{id}`, avec l'aperçu `ModelViewer` quand le fichier 3D est disponible.
*Vérification* : `cd frontend && npm run build` passe sans erreur, et la page s'affiche pour les 5 fiches de seed (vérification manuelle, capture jointe à la PR).

## Livrables

- Routes en double retirées, `README.md` à jour.
- Extensions de `FileHandler` hors de la classe, modèles de test dans `donnees/modeles/`, `lotA` fusionnée.
- `script_blender.py` qui rend `face.png`.
- `fusionner_descriptions()` + `prompts/fusion.md` et `vectoriser()`, avec tests dans `backend/tests/test_semantique/`.
- Page détail d'un modèle dans le front.
- Nouvelles décisions éventuelles ajoutées à `docs/DECISION.md`.

## DoR / DoD

**DoR** — L'US a un responsable et une commande de vérification. Ses entrées existent (seed, modèle de test ou contrat déjà présent dans `main`). Toute modification du socle commun (`contrats/`, `config.py`, `ollama/`) est annoncée aux deux autres membres avant d'être codée.

**DoD** — Le code est fusionné dans `main`. `uv run pytest` passe intégralement sans Ollama ni Blender. Aucune URL, aucun nom de modèle et aucune dimension d'embedding n'est écrit en dur (tout passe par `obtenir_config()`). Les chemins sont relatifs. Le code et les clés sont en français, sans accents. Les échanges entre lots passent uniquement par des JSON validés par `contrats`.

## Risques

- **Lot A bloquant** : trois sprints sans rendu, et `lotA` toujours pas fusionnée. Sans `manifeste_rendu.json`, le Lot B ne peut pas être testé de bout en bout. Le sprint se limite encore à la vue de face. Si l'US 3.3 bloque en milieu de semaine, l'équipe fait une séance commune dessus.
- **Branche `lotA` qui diverge** : elle part d'un `main` antérieur aux PR #4 à #6 (changement de `pyproject.toml`, suppression de `schemas/fiche.py`). L'US 3.2 doit commencer par une remise à jour sur `main`.
- **Rythme** : aucun commit depuis le 22/10. La charge reste à 2 US par personne, et chaque US doit pouvoir être fusionnée seule.
- **Qualité des sorties LLM** : la fusion des descriptions dépend du modèle configuré. Les tests restent avec client simulé ; un essai réel sur l'Ollama de l'IUT est conseillé mais ne fait pas partie de la DoD.
- **Accès à l'Ollama de l'IUT** : les essais manuels (fusion, vectorisation, mesure de dimension) exigent d'être sur le réseau de l'IUT. Tous les tests automatiques restent hors réseau.
- **Blender** : version et chemin variables selon les machines (`BLENDER_BIN`). Les tests de rendu doivent être ignorés proprement si Blender est absent.
- **Front non testé automatiquement** : seule la compilation (`npm run build`) vérifie le front. Les régressions d'affichage ne sont détectées qu'à la main.

## Reste à faire / reporté au Sprint 4

- Lot A : rendu des `NB_VUES` vues + vignette, puis orchestrateur qui écrit `manifeste_rendu.json` et saute les modèles déjà rendus.
- Lot B : pipeline complet `manifeste_rendu.json` → `decrire_vue()` × N → `fusionner_descriptions()` → `vectoriser()` → `fiche_modele.json` validée par `contrats`.
- Lot C : indexer les fiches produites par le Lot B dans ChromaDB ; afficher l'extrait de description qui justifie le match dans les résultats.
- Premier test de bout en bout sur un modèle de `donnees/modeles/`.
