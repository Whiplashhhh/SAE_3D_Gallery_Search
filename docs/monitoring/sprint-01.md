# Sprint 1 — Fusion du Lot C, client Ollama commun & premiers pas des Lots A et B

**Période** : 06/10/2026 → 13/10/2026
**Commit de référence** : 2bc698a
**Membres :** Willem V. (WV) · Alex R. (AR) · Hugo S. (HS)

## Bilan du sprint précédent

Commits analysés : du 21/09/2026 (premier commit après la clôture du Sprint 0 le 11/09) au
26/09/2026, sur `main` et `origin/lotC`. Le commit qui a ajouté `sprint-00.md` (1efe825) vient
d'une branche fusionnée ensuite : la plage `1efe825..HEAD` n'était donc pas exploitable, le
découpage a été fait par date. Aucun commit entre le 27/09 et le 05/10.

| US | Statut | Commits liés |
|----|--------|--------------|
| US 0.1 — Environnements backend / frontend | ✅ Faite (Sprint 0) | antérieurs au 11/09 |
| US 0.2 — README + `docs/DECISION.md` | ✅ Faite (Sprint 0) | b6fb283 |
| US 0.3 — Types communs | ✅ Faite (Sprint 0) | 41def55, 220d870 |
| US 0.4 — Contrats manifeste / fiche | ✅ Faite (Sprint 0) | 3b7c511, 72ff680, 67f9674 |
| US 0.5 — Seeds de test | ✅ Faite (Sprint 0) | 3b7c511, 8be84b6, a50ac82 |
| Reporté — `pytest` en dépendance de dev | 🟡 Partielle | 0cffda1 (`pytest` et `ruff` déclarés dans `[project.optional-dependencies]`, mais `uv run pytest` échoue encore : *Failed to spawn: pytest*. Il faut lancer `uv run --extra dev pytest`, ce qui donne 75 passed) |
| Reporté — Enrichir `docs/DECISION.md` | ✅ Faite | 2bc698a (D1 → D26) |
| Reporté — E/S JSON + journal `indexation.jsonl` | ✅ Faite | 118511b (`io.py` + tests), 3c23c28 (`journal.py` + tests), 253e481 (correctif de merge) |
| Reporté — Interface web métier | 🟡 Partielle | 7d82e89, 48e4c2b, de72c63 : galerie, page d'ajout et suppression existent, mais **uniquement sur `origin/lotC`** (pas fusionné dans `main`) |

**Hors sprint** (commits non rattachés à une US) :
- e9c3120 (HS) — `config.py` avec pydantic-settings + `test_config.py` + `.env.example` (socle commun, conforme à D20–D22).
- 0cffda1 (WV) — `contrats/__init__.py` (imports depuis le paquet) + `test_paquet.py`.
- 616d67b (WV) — validation de l'unicité des couleurs dominantes dans la fiche + test.
- c2f5f45 (WV) — simplification des imports dans les tests.
- 8760122 (WV) — skill `/sprint` (génération de ce fichier).
- eab6113 (HS, `origin/lotC`) — backend de recherche : ChromaDB, routeur FastAPI, indexeur, client Ollama, vectorisation.
- e442db6 (HS, `origin/lotC`) — Dockerfile backend + `docker-compose.yml`.
- 6e706cf (HS, `origin/lotC`) — 3 fiches de démonstration (chaise, maison, voiture) dans `seed/fiches/` à la racine.

**Synthèse** : 15 commits — WV 7 · HS 7 · AR 1. Par lot : Lot A 0 · Lot B 0 · Lot C 6 · Commun 9.
Le socle commun est quasi figé (75 tests verts). Le Lot C a pris de l'avance, mais sur une branche
qui a divergé du socle. Les Lots A et B n'ont pas commencé.

## User Stories

### Commun

**US 1.1** (WV) — En tant que développeur, je lance `uv run pytest` dans `backend/` sans option et toute la suite passe, parce que `pytest` et `ruff` sont déclarés dans `[dependency-groups] dev` (installés par défaut par `uv`) et plus dans `[project.optional-dependencies]`.
*Vérification* : `cd backend && uv sync && uv run pytest` → 0 échec, et `git status` ne montre pas `uv.lock` modifié (aujourd'hui le `uv.lock` commité ne contient pas `pytest` : lancer les tests le réécrit).

**US 1.2** (WV) — En tant que développeur des Lots B et C, je dispose d'un client Ollama commun `backend/src/ollama/client.py` (en partant de celui de `origin/lotC`) qui lit URL, modèles, timeout et nombre de tentatives depuis `obtenir_config()` et qui expose `embed(textes)` et `chat(modele, messages, schema, images)`. En cas d'erreur réseau ou de JSON invalide, il réessaie puis lève une exception métier (pas de `KeyError`).
*Vérification* : `uv run pytest tests/test_ollama/` avec `httpx.MockTransport` (sans Ollama) qui couvre la réponse valide, le timeout, le JSON invalide et l'épuisement des tentatives.

**US 1.3** (HS) — En tant que développeur, je dispose d'un script `backend/scripts/mesurer_dimension.py` qui appelle `/api/embed` une fois et affiche la dimension du modèle d'embedding configuré, à recopier dans `DIMENSION_EMBEDDING` du `.env` (décision D22).
*Vérification* : `uv run python scripts/mesurer_dimension.py` sur l'Ollama de l'IUT affiche un entier. La valeur est reportée dans `.env.example` en commentaire.

### Lot C — Recherche & interface (HS)

**US 1.4** — En tant qu'équipe, la branche `lotC` est fusionnée dans `main` en s'appuyant sur le socle commun : `src/contrats/schemas/fiche.py` est supprimé au profit de `contrats.FicheModele`, le `config.py` de `lotC` (dataclass + `os.getenv` avec URL et modèle en dur) est remplacé par `obtenir_config()`, et les routes sont celles du README (`/api/recherche`, `/api/modeles/{id}`, `/api/sante`).
*Vérification* : sur `main`, `uv run pytest` passe et `grep -rnE "127\.0\.0\.1|embeddinggemma|11434" backend/src/recherche` ne renvoie rien.

**US 1.5** — En tant que développeur du Lot C, je dispose de 5 fiches de démonstration aux thèmes distincts (chaise, maison, voiture, arbre, epee) dans `backend/seed/fiches/`, toutes acceptées par le contrat `FicheModele`.
*Vérification* : test `pytest` paramétré qui charge chaque fichier de `backend/seed/fiches/` avec `contrats.io` sans erreur.

**US 1.6** — En tant qu'utilisateur, une recherche renvoie des résultats triés par score. Ce comportement est garanti par des tests d'API sans Ollama (embedding simulé) et une base Chroma temporaire.
*Vérification* : `uv run pytest tests/test_recherche/` avec `TestClient`. Les tests couvrent `/api/sante`, `/api/modeles/{id}` (200 et 404) et `/api/recherche?q=chaise&k=3`, qui doit renvoyer en premier la fiche chaise, avec des scores décroissants.

### Lot A — Rendu multi-vues (AR)

**US 1.7** — En tant que développeur du Lot A, je dispose de 2 ou 3 petits modèles libres de droits (`.obj` ou `.glb`) dans `donnees/modeles/`, d'échelles très différentes, pour tester le cadrage.

**US 1.8** — En tant que développeur du Lot A, je dispose d'un script `backend/src/rendu/script_blender.py` qui charge un modèle, le centre et le met à l'échelle grâce à sa boîte englobante, puis rend les vues en `RESOLUTION_RENDU` × `RESOLUTION_RENDU`.
*Vérification* : `blender --background --python src/rendu/script_blender.py -- <modele> <dossier_sortie>` produit `face.png`, avec un modèle entier et centré pour les modèles de l'US 1.7.

**US 1.9** — En tant que développeur du Lot A, le script rend les `NB_VUES` vues (face, droite, arriere, gauche, haut, bas) et une vignette `RESOLUTION_VIGNETTE`.
*Vérification* : même commande que l'US 1.8, qui produit 6 PNG + `vignette.png` aux bonnes dimensions (contrôle par un petit test `pytest` sur les PNG produits, marqué `blender` et ignoré si Blender est absent).

### Lot B — Description sémantique (WV)

**US 1.10** — En tant que développeur du Lot B, je dispose du modèle Pydantic strict `DescriptionVue` (sortie du VLM pour une vue) et du prompt `backend/src/semantique/prompts/vue.md`. Le prompt impose de décrire uniquement ce qui est visible et de ne rien déduire sur les faces cachées.
*Vérification* : test `pytest` qui vérifie que `DescriptionVue.model_json_schema()` interdit les champs supplémentaires, qu'un exemple valide est accepté et qu'un exemple incomplet est refusé.

**US 1.11** — En tant que développeur du Lot B, je dispose d'une fonction `decrire_vue(chemin_png)` qui appelle le VLM via le client commun (US 1.2) avec le schéma `DescriptionVue`. En cas d'échec, elle écrit un événement dans `indexation.jsonl`.
*Vérification* : `uv run pytest tests/test_semantique/` avec client simulé (réponse valide, puis JSON invalide qui produit une nouvelle tentative et une ligne de journal), et un essai manuel sur une vue PNG de seed contre l'Ollama de l'IUT.

## Livrables

- `uv run pytest` fonctionne sans option dans `backend/`.
- Client Ollama commun dans `backend/src/ollama/client.py` + tests dans `backend/tests/test_ollama/`.
- Script `backend/scripts/mesurer_dimension.py`.
- Branche `lotC` fusionnée dans `main`, sans doublon de contrat ni de configuration.
- 5 fiches de démonstration dans `backend/seed/fiches/` + tests d'API dans `backend/tests/test_recherche/`.
- Modèles de test dans `donnees/modeles/` et script `backend/src/rendu/script_blender.py` (6 vues + vignette).
- `backend/src/semantique/` : `DescriptionVue`, prompt `vue.md`, `decrire_vue()` + tests dans `backend/tests/test_semantique/`.
- Nouvelles décisions éventuelles ajoutées à `docs/DECISION.md`.

## DoR / DoD

**DoR** — L'US a un responsable et une commande de vérification. Ses entrées existent (seed, modèle de test ou contrat déjà présent dans `main`). Toute modification du socle commun (`contrats/`, `config.py`, `ollama/`) est annoncée aux deux autres membres avant d'être codée.

**DoD** — Le code est fusionné dans `main`. `uv run pytest` passe intégralement sans Ollama ni Blender. Aucune URL, aucun nom de modèle et aucune dimension d'embedding n'est écrit en dur (tout passe par `obtenir_config()`). Les chemins sont relatifs. Le code et les clés sont en français, sans accents. Les échanges entre lots passent uniquement par des JSON validés par `contrats`.

## Risques

- **Divergence de `lotC`** : la branche a son propre `config.py` et son propre schéma de fiche, moins stricts que le socle. Elle place aussi ses seeds dans `seed/` à la racine au lieu de `backend/seed/`. Plus la fusion attend, plus elle coûtera. C'est pourquoi l'US 1.4 passe en premier.
- **Lots A et B à l'arrêt** : aucun commit depuis le Sprint 0. Les US 1.7 → 1.11 sont volontairement petites pour amorcer ces lots sans attendre les autres (seeds).
- **Dépendance au client Ollama** : l'US 1.11 dépend de l'US 1.2, elle-même à faire après la fusion de l'US 1.4 (le client part de celui de `lotC`). Ordre conseillé : 1.4 → 1.2 → 1.11.
- **Accès à l'Ollama de l'IUT** : les US 1.3 et 1.11 (essai manuel) exigent d'être sur le réseau de l'IUT. Tous les tests automatiques restent hors réseau.
- **Blender** : version et chemin variables selon les machines (`BLENDER_BIN`). Les tests de rendu doivent être ignorés proprement si Blender est absent.
- **Rythme** : aucun commit pendant 10 jours (27/09 → 05/10). La charge du sprint est limitée à 3–4 US par personne.

## Reste à faire / reporté au Sprint 2

- Lot A : orchestrateur qui écrit `manifeste_rendu.json` et saute les modèles déjà rendus.
- Lot B : fusion LLM des descriptions par vue (`gemma4:12b`), calcul des divergences, vectorisation, puis écriture de `fiche_modele.json`.
- Lot C : affichage des vues et de l'extrait de description justifiant le match dans la page détail.
- Mettre à jour le `README.md` (arborescence et commandes) après la fusion de `lotC`.
