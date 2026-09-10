# 3D Gallery Search

#### Willem V. - Alex R. - Hugo S.

SAÉ « Application intelligente » - BUT 3 Informatique.

Recherche de modèles 3D en langage naturel.

---

## 1. Ce que fait le logiciel

L'utilisateur tape **« chaise de bureau rouge à roulettes »** dans une galerie web et récupère les
modèles 3D correspondants, classés par pertinence, avec une vignette de prévisualisation.

Le problème : un fichier `.obj` / `.gltf` / `.stl` ne contient **aucun texte exploitable**, et son
apparence change complètement selon l'angle de vue.

La solution, en quatre temps :

1. on **photographie** le modèle sous plusieurs angles (rendu Blender headless) ;
2. un **VLM** décrit chaque vue **isolément** ;
3. un **LLM** fusionne ces descriptions partielles en une **fiche sémantique 360°** ;
4. la fiche est **vectorisée** et stockée ; à la recherche, on compare le vecteur de la requête à
   ceux des fiches.

Le cœur du sujet est l'étape 3 : la vue de face montre « une façade de maison intacte », la vue
arrière révèle « une toiture effondrée ». Une seule vue mène à une fiche fausse. C'est pour cela
que le champ `divergences_entre_vues` existe dans nos contrats : on ne cache pas les
contradictions, on les remonte.

---

## 2. Le pipeline

```
        INDEXATION HORS LIGNE (lente, une fois par modèle)                  RECHERCHE (rapide)
  ┌───────────────────────────────────────────────────────────┐        ┌────────────────────────┐
  │                                                           │        │                        │
  │   donnees/modeles/            LOT A            LOT B      │        │        LOT C           │
  │   chaise.obj  ──────────►  rendus/*.png  ──►  fiche_      │        │  ChromaDB + API REST   │
  │                            + manifeste_       modele.json ┼───────►│  + galerie Vue 3       │
  │                            rendu.json         (texte +    │        │                        │
  │                                               vecteur)    │        │  requête NL ──► top-k  │
  └───────────────────────────────────────────────────────────┘        └────────────────────────┘
        Blender headless        qwen3-vl:instruct                          embeddinggemma
                                gemma4:12b                                 (requête seule)
                                embeddinggemma
```

Tout passe par **Ollama en local** (API REST). Aucun service cloud, jamais.

---

## 3. Le découpage en 3 lots

**La règle qui rend les lots indépendants : un lot ne connaît jamais le code d'un autre lot. Il ne
connaît que des fichiers JSON sur le disque.**

Concrètement : les fichiers de `seed/` sont **écrits à la main**. Le lot B n'attend pas que le
lot A fonctionne, il travaille sur un faux `manifeste_rendu.json` + 6 PNG téléchargés. Le lot C
n'attend personne, il travaille sur trois fausses `fiche_modele.json`. Les trois lots peuvent donc
démarrer le même jour et se brancher ensemble à la fin.

| Lot   | Nom                    | Techno principale                | Entrée                       | Sortie                           |
|-------|------------------------|----------------------------------|------------------------------|----------------------------------|
| **A** | Rendu multi-vues       | Blender headless (script Python) | un fichier 3D                | des PNG + `manifeste_rendu.json` |
| **B** | Description sémantique | Ollama (VLM + LLM + embedding)   | `manifeste_rendu.json` + PNG | `fiche_modele.json`              |
| **C** | Recherche & interface  | ChromaDB + FastAPI + Vue 3       | `fiche_modele.json`          | API REST + galerie web           |

### Lot A — Rendu multi-vues

**Mission** : transformer un fichier 3D en images utilisables par un VLM.

- charger le mesh dans Blender sans interface (`blender --background --python script.py`) ;
- calculer la **boîte englobante** pour cadrer et éclairer le modèle correctement, quelle que soit
  son échelle (un modèle peut faire 0,01 ou 5000 unités) ;
- placer la caméra sur N azimuts (par défaut 6 : face, droite, arrière, gauche, haut, bas) avec une élévation
  fixe, rendre en 512×512 ;
- produire en plus une **vignette 256×256** (le front en affiche des dizaines, il ne doit pas
  charger les rendus pleine résolution) ;
- écrire le `manifeste_rendu.json`.

**Fini quand** : je lance une commande sur `donnees/modeles/`, j'obtiens un dossier par modèle avec
les PNG et un manifeste valide, et relancer la commande ne refait pas le travail déjà fait.

**Test en solo** : ouvrir les PNG. Le modèle est-il entier, centré, éclairé, non coupé ?

### Lot B — Description sémantique

**Mission** : transformer des images en texte + vecteur.

- pour chaque vue, appeler le **VLM** (`qwen3-vl:instruct`) avec un **schéma JSON contraint** —
  interdiction du texte libre, on veut du JSON typé ;
- consigne stricte dans le prompt : décrire **uniquement ce qui est visible sur cette vue**, ne rien
  déduire, ne rien inventer sur les faces cachées ;
- appeler le **LLM** (`gemma4:12b`) avec les N descriptions pour produire la fiche unifiée : titre,
  description 360°, mots-clés, catégorie, couleurs, état, **et la liste des divergences entre vues** ;
- vectoriser la description avec `embeddinggemma` ;
- écrire le `fiche_modele.json`.

**Fini quand** : je pointe le programme sur un manifeste, j'obtiens une fiche valide ; et si Ollama
est éteint, le programme échoue **proprement** (message clair, ligne de journal, code de retour) au
lieu de planter sur un `KeyError`.

**Test en solo** : les seeds + un cas piège fabriqué exprès (3 vues d'une maison intacte, 1 vue
de ruine) pour vérifier que la divergence est bien remontée.

### Lot C — Recherche & interface

**Mission** : rendre les fiches interrogeables en langage naturel.

- charger les `fiche_modele.json` dans **ChromaDB** (`id_modele` comme identifiant, mots-clés /
  catégorie / couleurs en métadonnées) ;
- exposer une API REST : `GET /api/recherche?q=...&k=12`, `GET /api/modeles/{id}`,
  `GET /api/sante` (Ollama joignable ? combien de fiches indexées ?) ;
- au moment de la recherche, vectoriser **la requête** via `/api/embed` d'Ollama (une requête HTTP,
  pas une dépendance au code du lot B) ;
- filtrage + ranking combinant similarité vectorielle et métadonnées ;
- galerie Vue 3 : champ de recherche, grille de vignettes, **score de similarité affiché**, page
  détail avec les vues et l'extrait de description qui justifie le match.

**Fini quand** : je tape une requête dans le navigateur et j'obtiens des résultats triés, à partir
des seules seeds, sans que A ni B n'aient jamais tourné.

**Test en solo** : 5 seeds aux thèmes bien distincts (chaise, maison, voiture, arbre, épée) et
des requêtes dont on connaît d'avance le bon résultat.

---

## 4. Les contrats

Deux fichiers JSON + un journal. C'est tout. Ils sont validés par des modèles **Pydantic** dans
`backend/src/gallery3d/contrats/`, en mode strict (`extra="forbid"`, `frozen=True`) : un champ en
trop ou un type faux est une erreur immédiate, pas un bug découvert trois semaines plus tard.

### `manifeste_rendu.json` — Lot A → Lot B

```json
{
  "version": "1.0",
  "id_modele": "a3f1c2d4e5b60789",
  "fichier_source": "donnees/modeles/chaise_bureau.obj",
  "sha256": "a3f1c2d4e5b607890f4d2c8a91b7e6350d24fa8817cc9b0e6a5d3f21c47b8e9d",
  "date_rendu": "2026-09-10T14:32:10Z",
  "moteur": "blender-4.2.1",
  "resolution": [
    512,
    512
  ],
  "nombre_vues": 4,
  "vues": [
    {
      "nom": "face",
      "chemin": "donnees/rendus/a3f1c2d4e5b60789/face.png",
      "azimut": 0,
      "elevation": 15
    },
    {
      "nom": "droite",
      "chemin": "donnees/rendus/a3f1c2d4e5b60789/droite.png",
      "azimut": 90,
      "elevation": 15
    },
    {
      "nom": "arriere",
      "chemin": "donnees/rendus/a3f1c2d4e5b60789/arriere.png",
      "azimut": 180,
      "elevation": 15
    },
    {
      "nom": "gauche",
      "chemin": "donnees/rendus/a3f1c2d4e5b60789/gauche.png",
      "azimut": 270,
      "elevation": 15
    }
  ],
  "vignette": "donnees/rendus/a3f1c2d4e5b60789/vignette.png"
}
```

Règles vérifiées par la validation :

- `sha256` : 64 caractères hexadécimaux minuscules, calculé sur le fichier 3D source ;
- `id_modele` = les **16 premiers caractères** du `sha256` (identifiant stable, indépendant du nom
  de fichier — renommer un modèle ne le réindexe pas) ;
- `len(vues) == nombre_vues` ;
- `nom` de vue en **ASCII sans accent ni espace** (il sert de nom de fichier) ;
- tous les chemins sont **relatifs à la racine du dépôt**.

### `fiche_modele.json` — Lot B → Lot C

```json
{
  "version": "1.0",
  "id_modele": "a3f1c2d4e5b60789",
  "titre": "Chaise de bureau rouge a roulettes",
  "description": "Chaise de bureau pivotante a assise rouge, dossier ajoure noir, pietement en etoile a cinq branches equipe de roulettes. Accoudoirs fixes. Verin de reglage en hauteur visible sous l'assise.",
  "categorie": "mobilier",
  "mots_cles": [
    "chaise",
    "bureau",
    "roulettes",
    "pivotante",
    "assise rouge"
  ],
  "couleurs_dominantes": [
    "rouge",
    "noir"
  ],
  "etat": "intact",
  "par_vue": [
    {
      "nom": "face",
      "description": "Assise rouge et dossier ajoure noir vus de face, deux accoudoirs."
    },
    {
      "nom": "droite",
      "description": "Profil montrant le verin central et le pietement en etoile."
    },
    {
      "nom": "arriere",
      "description": "Dossier vu de dos, structure en plastique noir moule."
    },
    {
      "nom": "gauche",
      "description": "Profil gauche, une roulette partiellement masquee."
    }
  ],
  "divergences_entre_vues": [],
  "embedding": {
    "modele": "embeddinggemma",
    "dimension": 768,
    "vecteur": [
      0.0123,
      -0.0456,
      0.0789
    ]
  },
  "duree_ms": {
    "vlm": 8200,
    "llm": 3100,
    "embedding": 140
  }
}
```

- **`par_vue` est conservé en entier.** L'étape VLM est la plus lente du pipeline ; garder les
  descriptions brutes permet de rejouer la synthèse LLM (nouveau prompt, autre modèle) sans
  relancer le VLM. C'est aussi ce qui rend la traçabilité possible dans l'interface.
- **`divergences_entre_vues` est un champ de premier niveau**, pas une note noyée dans la
  description. C'est la réponse directe à la problématique du sujet.

`dimension` : à vérifier une fois pour de bon avec `POST /api/embed` sur l'instance de l'IUT, et à
faire valider par le contrat (une dimension incohérente casse la base vectorielle en silence).

### `journal/indexation.jsonl` — partagé par les trois lots

Un fichier **append-only**, une ligne JSON par événement.

```json
{
  "horodatage": "2026-09-10T14:32:10Z",
  "lot": "B",
  "id_modele": "a3f1c2d4e5b60789",
  "niveau": "avertissement",
  "evenement": "json_malforme_relance",
  "message": "Sortie VLM non parsable sur la vue arriere, 2e tentative"
}
```

### Cache et reprise sur erreur

Pas de champ `statut` nulle part. **La présence du fichier de sortie est le signal de succès.**

Écriture atomique obligatoire : on écrit dans `fiche.json.tmp`, puis `os.replace()` vers
`fiche.json`. Un `kill -9` en pleine inférence ne laisse donc jamais un fichier à moitié écrit qui
serait pris pour un succès. Relancer l'indexation reprend exactement là où elle s'était arrêtée.

---

## 5. Arborescence du dépôt

```
3d-gallery-search/
├── README.md                     ← ce fichier
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── decisions.md
│   └── contrats.md               ← version longue de la section 4
├── donnees/                      ← dataset de démo (versionné, petits fichiers !)
│   ├── modeles/                  ← .obj / .gltf / .stl
│   ├── rendus/                   ← sortie Lot A     (git-ignoré)
│   ├── fiches/                   ← sortie Lot B     (git-ignoré)
│   ├── chroma/                   ← base vectorielle (git-ignoré)
│   └── journal/indexation.jsonl  (git-ignoré)
├── seed/                         ← données de départ (versionnées)
│   ├── manifestes/
│   ├── rendus/
│   └── fiches/
├── backend/
│   ├── pyproject.toml
│   ├── src/gallery3d/
│   │   ├── config.py             ← commun : lecture du .env
│   │   ├── contrats/             ← commun : modèles Pydantic + io
│   │   ├── ollama/               ← commun : client HTTP (timeouts, retries, parsing défensif)
│   │   ├── rendu/                ← LOT A
│   │   ├── semantique/           ← LOT B
│   │   └── recherche/            ← LOT C (indexation Chroma + API FastAPI)
│   └── tests/
│       ├── test_contrats/
│       ├── test_rendu/
│       ├── test_semantique/
│       └── test_recherche/
└── frontend/                     ← LOT C — Vue 3 + Vite
```

`contrats/`, `config.py` et `ollama/` sont le **socle commun** : personne ne les modifie seul, toute
évolution se discute (elle change l'interface des trois lots).


---

## 6. Configuration

Rien de codé en dur. Tout dans `.env` (non versionné), avec un `.env.example` à jour dans le dépôt.

```dotenv
# Ollama (instance locale IUT)
OLLAMA_BASE_URL=http://xxx.xxx.xxx.xxx:11434
MODELE_VLM=qwen3-vl:instruct
MODELE_LLM=gemma4:12b
MODELE_EMBEDDING=embeddinggemma
OLLAMA_TIMEOUT_S=180
OLLAMA_TENTATIVES=3

# Rendu
BLENDER_BIN=blender
NB_VUES=6
RESOLUTION_RENDU=512
RESOLUTION_VIGNETTE=256

# Chemins
DOSSIER_MODELES=./donnees/modeles
DOSSIER_RENDUS=./donnees/rendus
DOSSIER_FICHES=./donnees/fiches
CHEMIN_CHROMA=./donnees/chroma
CHEMIN_JOURNAL=./donnees/journal/indexation.jsonl
```

Les noms de modèles doivent pouvoir être changés **sans toucher au code**.

---

## 7. Installation et lancement

à définir

---

## 8. Conventions

- **Français partout** : noms de champs JSON, contenus générés, interface, messages du journal,
  commentaires. Les clés JSON sont **sans accent** (`date_rendu`, pas `daté_rendu`).
- **Python** : `snake_case`, typage systématique, Pydantic pour toute donnée qui traverse une
  frontière de lot.
- **Git** : Conventional Commits, en français, avec le lot —
  `fix(A) : Cadrage camera sur boite englobante`, `feat(Contrat) validation sha256`.
- **Tests** : chaque lot a ses tests qui tournent **sans Ollama et sans Blender** (seeds).
  Un test qui exige le réseau n'est pas un test unitaire.

---

## 9. Checklist des exigences du sujet

- **Robustesse Ollama** : serveur éteint, erreur 500, timeout, dépassement de contexte, JSON
  malformé en sortie de modèle. Chaque cas est géré et journalisé, aucun ne fait planter le
  programme.
- **Sorties structurées** : le VLM et le LLM sont appelés avec un schéma JSON strict, et la
  sortie est validée avant d'être écrite (parsing défensif, pas de confiance aveugle).
- **Configuration externalisée** : aucune URL ni nom de modèle en dur.
- **Couche d'abstraction** : changer de modèle ou de base vectorielle ne doit toucher qu'un
  fichier.
- **Observabilité** : temps d'inférence, tokens/seconde, score de similarité cosinus brut,
  affichés dans les interfaces (`duree_ms` dans les fiches sert à ça).
- **Dataset de démo** versionné : quelques petits modèles 3D, dont au moins un cas de
  divergence entre vues.
- **Documentation à jour en continu** : architecture, contrats, guide d'installation.

---

## 10. Répartition et suivi

| Lot                                                 | Responsable |
|-----------------------------------------------------|-------------|
| Socle commun (`contrats/`, `config`, client Ollama) | tous les 3  |
| A — Rendu multi-vues                                | Alex R.     |
| B — Description sémantique                          | Willem V.   |
| C — Recherche & interface                           | Hugo S.     |

Le socle commun est un travail à part : il doit être fini (ou au moins figé sur `manifeste` et
`fiche`) **avant** que les trois lots avancent loin, sinon on refactore trois fois.
