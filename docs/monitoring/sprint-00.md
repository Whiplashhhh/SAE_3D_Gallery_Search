# Sprint 0 — Socle technique, architecture & contrats inter-lots

**Période :** 09/09/2026 → 11/09/2026
**Membres :** Willem V. (WV) · Alex R. (AR) · Hugo S. (HS)

## User Stories

**US 0.1** — En tant que développeur, je dispose des environnements de développement initialisés pour le backend (Python 3.11+ géré par `uv`, avec `uv.lock` et configuration `pytest` dans `pyproject.toml`) et pour le frontend (Vue 3 avec Vite, TypeScript et Vue Router), afin de pouvoir démarrer les développements des trois lots en parallèle.

**US 0.2** — En tant que développeur, je dispose d'une documentation de cadrage (`README.md`) formalisant le pipeline 3D, le découpage en trois lots et leurs responsabilités, les formats d'échange JSON, l'arborescence du dépôt, la configuration et les conventions de travail, ainsi que d'un journal de décisions techniques (`docs/DECISION.md`) actant le choix des langages.

**US 0.3** — En tant que développeur, je dispose d'une base de types stricts et réutilisables (`sha256` 64 hex minuscules, `id_modele` 16 hex, chemins relatifs sécurisés refusant l'absolu et `..`, noms de vues ASCII minuscules, textes non vides, mots-clés normalisés) validés unitairement, pour garantir l'intégrité des échanges entre lots.

**US 0.4** — En tant que développeur, je dispose des modèles Pydantic stricts (`extra="forbid"`, `frozen=True`) pour `manifeste_rendu.json` (Lot A → Lot B) et `fiche_modele.json` (Lot B → Lot C), avec leurs règles métier : cohérence `id_modele` = 16 premiers caractères du `sha256`, cohérence `nombre_vues` / taille de la liste, unicité des noms de vues, unicité des mots-clés, états autorisés par énumération fermée.

**US 0.5** — En tant que développeur, je dispose d'un premier jeu de données de test (`backend/seed/`) contenant un manifeste et une fiche sémantique valides, afin de tester les modèles et les parseurs de façon isolée.

## Livrables

- Projets `backend/` et `frontend/` initialisés et fonctionnels à la racine du dépôt.
- Types communs implémentés dans `backend/src/contrats/common.py`.
- Contrats Pydantic implémentés dans `backend/src/contrats/manifeste.py` et `backend/src/contrats/fiche.py`.
- Suite de tests unitaires `pytest` dans `backend/tests/test_contrats/` : 27 tests (9 types communs, 10 manifeste, 8 fiche), sans dépendance externe (ni Ollama, ni Blender).
- Jeux de données de seed conformes aux schémas : `backend/seed/manifestes/chaise_bureau.json` et `backend/seed/fiches/chaise_bureau.json`.
- Documentation de cadrage dans `README.md` (pipeline, lots, contrats `manifeste_rendu.json` / `fiche_modele.json` / `journal/indexation.jsonl`, arborescence, configuration, conventions, checklist des exigences du sujet).
- Journal des décisions techniques dans `docs/DECISION.md`.

## DoR / DoD

**DoR** — Sujet de la SAÉ lu et découpé en trois lots ; langages et frameworks arbitrés ; formats d'échange entre lots rédigés dans le `README.md` avant toute implémentation.

**DoD** — Les trois contrats JSON sont décrits dans le `README.md` et implémentés en Pydantic strict ; `uv run pytest` passe intégralement sur `backend/tests/test_contrats/` ; les fichiers de seed sont acceptés par les modèles ; chaque membre a contribué au dépôt (commits WV, AR, HS).

## Reste à faire / reporté au Sprint 1

- Déclarer explicitement `pytest` en dépendance de développement dans `backend/pyproject.toml` (aujourd'hui seule la section `[tool.pytest.ini_options]` est présente).
- Enrichir `docs/DECISION.md` : il ne contient à ce stade que la décision du 09/09 sur les langages.
- Implémentation des entrées/sorties JSON et du journal d'événements `indexation.jsonl` (contrats spécifiés, code non écrit à la clôture du sprint).
- Interface web métier (le frontend est au stade du scaffold Vite par défaut).