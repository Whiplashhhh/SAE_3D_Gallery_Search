# Sprint 2 — Finir la fusion du Lot C, client Ollama commun & premiers livrables des Lots A et B

**Période** : 19/10/2026 → 26/10/2026
**Commit de référence** : a419002
**Membres :** Willem V. (WV) · Alex R. (AR) · Hugo S. (HS)

## Bilan du sprint précédent

Commits analysés : du 06/10/2026 au 19/10/2026, sur toutes les branches (`main`, `LOT_B`,
`LOT_C`, `lotA`, `lotC`). La plage `2bc698a..HEAD` ramenait d'anciens commits de `lotC`
(septembre) qui ne descendent pas de `2bc698a` : le découpage a donc été fait par date
(`--since=2026-10-06`). Aucun commit entre le 09/10 et le 18/10.

| US | Statut | Commits liés |
|----|--------|--------------|
| US 1.1 — `uv run pytest` sans option | ❌ Non commencée | aucun : `pyproject.toml` déclare toujours `pytest` et `ruff` dans `[project.optional-dependencies]` |
| US 1.2 — Client Ollama commun | ❌ Non commencée | abb6ffa n'ajoute que des docstrings. Sur `main`, `ClientOllama` ne fait que `embed()` et `est_joignable()` : pas de `chat()`, pas de nouvelles tentatives, pas de lecture de `obtenir_config()`, pas de `tests/test_ollama/` |
| US 1.3 — Script `mesurer_dimension.py` | ❌ Non commencée | aucun |
| US 1.4 — Fusion de `lotC` dans `main` | 🟡 Partielle | 64af5e3 (merge), 31ac149 (`uv.lock`), 0b8d596 (`.gitignore`). Fusion faite et aucune URL ni modèle en dur dans `src/recherche`, mais `src/contrats/schemas/fiche.py` (second `FicheModele`) est toujours utilisé par `recherche/`, `obtenir_config()` n'est appelé nulle part, et des routes en anglais (`/search`, `/models`, `/health`) doublonnent celles du README |
| US 1.5 — 5 fiches de démonstration | ✅ Faite | d66b51f (fusionné par la PR #2) : `arbre`, `epee`, `maison`, `voiture` + `chaise_bureau` existante, test `test_seed_fiches.py` |
| US 1.6 — Tests d'API sans Ollama | ✅ Faite | f145ca2 (fusionné par la PR #3) : `/api/sante`, `/api/modeles/{id}` (200 et 404), `/api/recherche?q=chaise&k=3` trié par score |
| US 1.7 — Modèles 3D de test | ❌ Non commencée | aucun fichier dans `donnees/modeles/` |
| US 1.8 — `script_blender.py` (vue de face) | ❌ Non commencée | 14fae9f crée `src/rendu/script_blender.py`, mais le fichier est **vide** |
| US 1.9 — 6 vues + vignette | ❌ Non commencée | aucun |
| US 1.10 — Modèle de sortie VLM + prompt `vue.md` | 🟡 Partielle | a419002 : modèle strict nommé `SortieVueVlm` (au lieu de `DescriptionVue`), prompt `prompts/vue.md` et tests. Il reste **uniquement sur `LOT_B`** (pas fusionné dans `main`) |
| US 1.11 — `decrire_vue()` | ❌ Non commencée | aucun (bloquée par l'US 1.2) |

**Hors sprint** (commits non rattachés à une US) :
- 14fae9f (AR, `lotA`, 19/10) — `rendu/FileHandler.py` : décompression des archives (zip imbriqués) et liste des fichiers 3D exploitables. Utile au Lot A, mais sans test et avec les extensions écrites en dur (`TODO: Mettre dans .env`).
- abb6ffa (HS, `LOT_C`) — docstrings sur les fonctions clés du back et du front de recherche (non fusionné dans `main`).
- 988a764 (WV) — `docs/monitoring/sprint-01.md`.

**Synthèse** : 8 commits (hors merges) — HS 5 · WV 2 · AR 1. Par lot : Lot A 1 · Lot B 1 · Lot C 3 ·
Commun 3. 2 US sur 11 terminées, 2 partielles. Le Lot C est fusionné et testé, mais garde des
doublons du socle. Les Lots A et B ont démarré, chacun sur sa branche, sans rien dans `main`.

## User Stories

### Commun

**US 2.1** (WV) — *Report de l'US 1.1.* En tant que développeur, je lance `uv run pytest` dans `backend/` sans option et toute la suite passe, parce que `pytest` et `ruff` sont déclarés dans `[dependency-groups] dev` et plus dans `[project.optional-dependencies]`.
*Vérification* : `cd backend && uv sync && uv run pytest` → 0 échec, et `git status` ne montre pas `uv.lock` modifié.

**US 2.2** (HS) — *Report de l'US 1.2.* En tant que développeur des Lots B et C, le client `backend/src/ollama/client.py` (déjà dans `main`) est construit à partir de `obtenir_config()` (URL, modèles, timeout, nombre de tentatives) et expose `embed(textes)` et `chat(modele, messages, schema, images)`. En cas d'erreur réseau ou de JSON invalide, il réessaie puis lève une exception métier.
*Vérification* : `uv run pytest tests/test_ollama/` avec `httpx.MockTransport` (sans Ollama) : réponse valide, timeout, JSON invalide, épuisement des tentatives.

**US 2.3** (HS) — *Report de l'US 1.3.* En tant que développeur, je dispose de `backend/scripts/mesurer_dimension.py`, qui appelle `embed()` une fois et affiche la dimension du modèle d'embedding configuré (décision D22).
*Vérification* : `uv run python scripts/mesurer_dimension.py` sur l'Ollama de l'IUT affiche un entier, reporté en commentaire dans `.env.example`.

### Lot C — Recherche & interface (HS)

**US 2.4** — *Fin de l'US 1.4.* En tant qu'équipe, le Lot C n'utilise plus que le socle commun : `src/contrats/schemas/fiche.py` est supprimé au profit de `contrats.FicheModele`, et les routes en anglais en double (`/search`, `/models`, `/models/{id}`, `/health`) sont retirées si le front ne les appelle plus. La branche `LOT_C` (docstrings abb6ffa) est fusionnée dans `main`.
*Vérification* : sur `main`, `uv run pytest` passe, `test -e backend/src/contrats/schemas/fiche.py` échoue et `grep -rn "schemas.fiche" backend/src` ne renvoie rien.

### Lot A — Rendu multi-vues (AR)

**US 2.5** — *Report de l'US 1.7 + suite de 14fae9f.* En tant que développeur du Lot A, je dispose de 2 ou 3 petits modèles libres de droits dans `donnees/modeles/`, d'échelles très différentes, et `FileHandler` est testé. Ses extensions acceptées ne sont plus écrites en dur dans la classe.
*Vérification* : `uv run pytest tests/test_rendu/test_file_handler.py` (zip imbriqué créé dans `tmp_path`, extraction, liste des fichiers 3D trouvés), puis `lotA` fusionné dans `main`.

**US 2.6** — *Report de l'US 1.8.* En tant que développeur du Lot A, `backend/src/rendu/script_blender.py` charge un modèle, le centre et le met à l'échelle grâce à sa boîte englobante, puis rend la vue de face en `RESOLUTION_RENDU` × `RESOLUTION_RENDU`.
*Vérification* : `blender --background --python src/rendu/script_blender.py -- <modele> <dossier_sortie>` produit `face.png`, avec un modèle entier et centré pour chaque modèle de l'US 2.5.

### Lot B — Description sémantique (WV)

**US 2.7** — *Fin de l'US 1.10.* En tant qu'équipe, le modèle `SortieVueVlm` et le prompt `prompts/vue.md` sont fusionnés dans `main`. Le nom `SortieVueVlm` remplace `DescriptionVue` (noté dans `docs/DECISION.md`).
*Vérification* : sur `main`, `uv run pytest tests/test_semantique/` passe (champ supplémentaire refusé, exemple valide accepté, exemple incomplet refusé).

**US 2.8** — *Report de l'US 1.11.* En tant que développeur du Lot B, je dispose d'une fonction `decrire_vue(chemin_png)` qui appelle le VLM via `ClientOllama.chat()` (US 2.2) avec le schéma de `SortieVueVlm`. En cas d'échec, elle écrit un événement dans `indexation.jsonl`.
*Vérification* : `uv run pytest tests/test_semantique/` avec client simulé (réponse valide, puis JSON invalide qui produit une nouvelle tentative et une ligne de journal), et un essai manuel sur une vue PNG de seed contre l'Ollama de l'IUT.

## Livrables

- `uv run pytest` fonctionne sans option dans `backend/`.
- Client Ollama commun branché sur `obtenir_config()`, avec `chat()` et tests dans `backend/tests/test_ollama/`.
- Script `backend/scripts/mesurer_dimension.py`.
- `src/contrats/schemas/fiche.py` supprimé, routes en double retirées, `LOT_C` fusionnée.
- Modèles de test dans `donnees/modeles/`, `FileHandler` testé, `script_blender.py` qui rend `face.png`, `lotA` fusionnée.
- `SortieVueVlm` + `vue.md` dans `main`, `decrire_vue()` + tests dans `backend/tests/test_semantique/`.
- Nouvelles décisions éventuelles ajoutées à `docs/DECISION.md`.

## DoR / DoD

**DoR** — L'US a un responsable et une commande de vérification. Ses entrées existent (seed, modèle de test ou contrat déjà présent dans `main`). Toute modification du socle commun (`contrats/`, `config.py`, `ollama/`) est annoncée aux deux autres membres avant d'être codée.

**DoD** — Le code est fusionné dans `main`. `uv run pytest` passe intégralement sans Ollama ni Blender. Aucune URL, aucun nom de modèle et aucune dimension d'embedding n'est écrit en dur (tout passe par `obtenir_config()`). Les chemins sont relatifs. Le code et les clés sont en français, sans accents. Les échanges entre lots passent uniquement par des JSON validés par `contrats`.

## Risques

- **Travail qui reste sur les branches** : `LOT_B`, `LOT_C` et `lotA` contiennent chacune du travail non fusionné. Plus elles vivent longtemps, plus elles divergent. Chaque US prévoit sa fusion dans `main`.
- **Doublon de contrat** : tant que `contrats/schemas/fiche.py` existe, le Lot C valide les fiches avec un schéma différent de celui que le Lot B produira. C'est pourquoi l'US 2.4 passe tôt dans la semaine.
- **Dépendance au client Ollama** : l'US 2.8 dépend de l'US 2.2. Pour ne pas bloquer, WV et HS fixent la signature de `chat()` dès le début du sprint ; `decrire_vue()` est testée avec un client simulé.
- **Lot A en retard** : aucun rendu après deux sprints. Le sprint se limite à la vue de face ; les 6 vues et la vignette sont reportées.
- **Accès à l'Ollama de l'IUT** : les US 2.3 et 2.8 (essai manuel) exigent d'être sur le réseau de l'IUT. Tous les tests automatiques restent hors réseau.
- **Blender** : version et chemin variables selon les machines (`BLENDER_BIN`). Les tests de rendu doivent être ignorés proprement si Blender est absent.
- **Rythme** : aucun commit du 09/10 au 18/10. La charge est réduite à 2–3 US par personne, toutes reprises du sprint précédent.

## Reste à faire / reporté au Sprint 3

- Lot A : rendu des `NB_VUES` vues + vignette (ancienne US 1.9), puis orchestrateur qui écrit `manifeste_rendu.json` et saute les modèles déjà rendus.
- Lot B : fusion LLM des descriptions par vue, calcul des divergences, vectorisation, puis écriture de `fiche_modele.json`.
- Lot C : brancher l'indexation sur le client commun ; affichage des vues et de l'extrait de description justifiant le match dans la page détail.
- Mettre à jour le `README.md` (arborescence et commandes) après la fusion de `lotC`.
