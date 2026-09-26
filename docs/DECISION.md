# Journal des décisions

Les décisions importantes du projet, dans l'ordre où elles ont été prises.
Pour chacune : **ce qu'on a choisi** et **pourquoi**.

---

## 09-09-2026 — Démarrage du projet

### D1. Python pour le backend, Vue.js pour le frontend
- **Choix** : Python pour le backend, Vue 3 (avec Vite et TypeScript) pour le frontend.
- **Pourquoi** : Python s'intègre facilement avec l'IA et permet de piloter Blender.
  Vue.js par affinité, et parce qu'il se branche simplement sur une API REST.

### D2. `uv` pour gérer le projet Python
- **Choix** : les dépendances Python sont gérées par `uv`, avec un fichier `uv.lock`.
- **Pourquoi** : tout le monde installe exactement les mêmes versions.

### D3. Un dossier par partie : `backend/`, `frontend/`, `docs/`
- **Choix** : le code Python va dans `backend/`, le code Vue dans `frontend/`,
  la documentation dans `docs/`.
- **Pourquoi** : chaque partie a sa place et ses propres fichiers de config.

### D4. Les fichiers de l'IDE ne vont pas sur Git
- **Choix** : le dossier `.idea/` est supprimé du dépôt et ajouté au `.gitignore`.
- **Pourquoi** : ces fichiers sont propres à chaque machine et créent des conflits inutiles.

---

## 10-09-2026 — Cadrage dans le README

### D5. Le projet est découpé en 3 lots
- **Choix** :
  - **Lot A** : rendu du modèle 3D sous plusieurs angles avec Blender (sans interface).
  - **Lot B** : description du modèle par l'IA (Ollama).
  - **Lot C** : recherche (ChromaDB + FastAPI) et galerie web (Vue).
- **Pourquoi** : chacun peut avancer sur sa partie en même temps que les autres.

### D6. Les lots ne se parlent qu'avec des fichiers JSON
- **Choix** : un lot ne connaît jamais le code d'un autre lot. Il lit et écrit seulement
  des fichiers JSON : `manifeste_rendu.json` (A → B) et `fiche_modele.json` (B → C).
- **Pourquoi** : les lots restent indépendants. Si un lot change son code, les autres
  ne sont pas touchés tant que le format JSON reste le même.

### D7. Des fausses données écrites à la main (`seed/`)
- **Choix** : on écrit à la main des exemples de fichiers JSON dans `backend/seed/`.
- **Pourquoi** : le lot B n'a pas besoin d'attendre le lot A, ni le lot C d'attendre le lot B.
  On peut tester chaque lot tout seul.

### D8. Toute l'IA tourne en local avec Ollama
- **Choix** : on utilise Ollama (sur le serveur de l'IUT) pour tous les modèles d'IA.
  Aucun service cloud.
- **Pourquoi** : c'est demandé par le sujet, et on garde la maîtrise des données.

### D9. Des règles communes pour toute l'équipe
- **Choix** :
  - Tout est en **français** (champs JSON, messages, commentaires), et les clés JSON **sans accent**.
  - Commits au format **Conventional Commits**, en français (`feat(contrat) : ...`).
  - Les tests tournent **sans Ollama et sans Blender**, grâce aux fichiers `seed/`.
- **Pourquoi** : un code homogène est plus facile à relire, et des tests sans réseau
  sont rapides et fiables.

---

## 10-09 → 11-09-2026 — Les contrats entre lots

### D10. Pydantic en mode strict pour valider les JSON
- **Choix** : chaque format JSON est décrit par un modèle Pydantic avec
  `extra="forbid"` (pas de champ inconnu) et `frozen=True` (pas de modification après création).
- **Pourquoi** : un fichier mal formé est refusé tout de suite, au lieu de causer
  un bug plus loin dans un autre lot.

### D11. Des types communs réutilisés partout (`common.py`)
- **Choix** : les règles de base sont écrites une seule fois : sha256, identifiant de modèle,
  chemin relatif, nom de vue, mot-clé, texte non vide.
- **Pourquoi** : la même règle s'applique partout, et on ne la réécrit pas trois fois.

### D12. L'identifiant d'un modèle vient de son empreinte sha256
- **Choix** : `id_modele` = les 16 premiers caractères du sha256 du fichier 3D.
- **Pourquoi** : le même fichier donne toujours le même identifiant, même s'il est renommé.

### D13. Les chemins sont toujours relatifs et sans `..`
- **Choix** : les chemins absolus et les chemins qui contiennent `..` sont refusés.
- **Pourquoi** : le projet marche sur n'importe quelle machine, et un fichier ne peut pas
  pointer en dehors du dépôt.

### D14. Des règles qui vérifient la cohérence des données
- **Choix** :
  - `nombre_vues` doit être égal au nombre de vues dans la liste.
  - Pas deux vues avec le même nom (le nom sert de nom de fichier).
  - Pas de doublon dans les mots-clés.
- **Pourquoi** : un doublon ou un chiffre faux fausserait la recherche du lot C.

### D15. L'état d'un modèle est choisi dans une liste fermée
- **Choix** : `etat` ne peut valoir que `intact`, `endommage`, `ruine`, `incomplet` ou `indetermine`.
- **Pourquoi** : sinon l'IA invente ses propres mots, et on ne peut plus filtrer.

---

## 21-09-2026 — Lecture, écriture et journal

### D16. Un fichier de sortie présent = travail réussi
- **Choix** : pas de champ « statut ». Si le fichier de sortie existe, le travail est fait
  et on ne le refait pas (`deja_traite()`).
- **Pourquoi** : c'est simple, et si le programme s'arrête, on relance et il reprend
  là où il en était.

### D17. Écriture des fichiers « tout ou rien »
- **Choix** : on écrit d'abord dans un fichier `.tmp`, puis on le renomme avec `os.replace()`.
- **Pourquoi** : un fichier à moitié écrit (après un plantage) ne peut jamais être pris
  pour un succès.

### D18. Un journal commun aux 3 lots, qui ne plante jamais
- **Choix** : chaque événement est ajouté comme une ligne JSON à la fin de
  `indexation.jsonl`. Si le journal n'arrive pas à écrire, il affiche l'erreur
  mais ne bloque pas le programme. À la lecture, les lignes abîmées sont ignorées.
- **Pourquoi** : le journal sert à observer. Il ne doit jamais faire échouer
  le traitement qu'il observe.

### D19. Des codes d'événement fixes
- **Choix** : chaque événement a un code court et stable (ex : `json_malforme_relance`)
  et un niveau (`info`, `avertissement`, `erreur`).
- **Pourquoi** : on peut compter et filtrer les événements facilement.

---

## 25-09-2026 — Configuration

### D20. Aucune valeur écrite en dur dans le code
- **Choix** : l'URL d'Ollama, les noms des modèles, les chemins, etc. sont lus depuis
  le fichier `.env` (avec `pydantic-settings`). Un `.env.example` montre les valeurs à remplir.
- **Pourquoi** : on peut changer de modèle ou de serveur sans toucher au code.

### D21. Les valeurs de config sont vérifiées au démarrage
- **Choix** : chaque valeur a des limites (ex : entre 1 et 24 vues, au moins 1 seconde de timeout).
  La config est lue une seule fois et ne change plus ensuite.
- **Pourquoi** : une mauvaise valeur est repérée tout de suite, pas au milieu d'un traitement.

### D22. La taille des vecteurs est mesurée, pas devinée
- **Choix** : `DIMENSION_EMBEDDING` est mesurée une fois sur l'Ollama de l'IUT (768 pour
  `embeddinggemma`), puis écrite dans le `.env`.
- **Pourquoi** : une mauvaise taille casserait la base de recherche ChromaDB.

---

## 26-09-2026 — Organisation des imports

### D23. On importe tout depuis le paquet `contrats`
- **Choix** : on écrit `from contrats import FicheModele`, jamais depuis les fichiers internes.
- **Pourquoi** : on peut réorganiser les fichiers internes sans casser le code des lots.

### D24. Les contrats ont un numéro de version
- **Choix** : `VERSION_CONTRATS = "1.0"`. On l'augmente si un changement rend les anciens
  fichiers JSON incompatibles.
- **Pourquoi** : on sait tout de suite si un fichier a été produit avec un ancien format.

### D25. `pytest` et `ruff` déclarés comme outils de développement
- **Choix** : ils sont ajoutés dans les dépendances `dev` du `pyproject.toml`.
- **Pourquoi** : tout le monde a les mêmes outils pour tester et vérifier le code.

### D26. Pas de doublon dans les couleurs dominantes
- **Choix** : comme pour les mots-clés, une couleur ne peut apparaître qu'une fois.
- **Pourquoi** : les doublons fausseraient les filtres du lot C.
