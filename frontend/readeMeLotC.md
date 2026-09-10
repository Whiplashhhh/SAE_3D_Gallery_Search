## Fonctionnement du Lot c

Le Lot C est composé d'un frontend Vue 3, d'une API FastAPI, d'une base SQLite
pour les informations métier et de ChromaDB pour la recherche vectorielle.

```text
Utilisateur
    ↓
Frontend Vue 3
    ↓
API FastAPI
    ↓
Service d'embedding
    ↓
ChromaDB : recherche des IDs proches
    ↓
SQLite : récupération des informations complètes
    ↓
Frontend : affichage des résultats
```

### Les deux stockages

SQLite est la source de vérité pour les modèles 3D. Elle contient les informations
complètes :

```text
backend/data/gallery.sqlite3
```

On y trouve notamment :

- l'identifiant du modèle ;
- son nom et sa description ;
- sa catégorie ;
- son chemin de fichier ;
- son format ;
- sa couleur ;
- son nom de fichier original ;
- sa date de création.

ChromaDB est le moteur de recherche vectorielle :

```text
backend/data/vector_store/
```

Elle conserve l'embedding et l'identifiant du modèle SQLite, ainsi que quelques
métadonnées utiles aux filtres. Elle ne remplace pas SQLite pour les informations
complètes.

Le même identifiant relie les deux stockages :

```text
SQLite   : id = upload-abc123
ChromaDB : id = upload-abc123
```

Les fichiers 3D importés sont stockés dans :

```text
backend/data/models/
```

### Ajout d'un modèle

Depuis l'interface, un fichier `.obj`, `.gltf` ou `.stl` est :

1. validé par l'API ;
2. sauvegardé dans `backend/data/models/` ;
3. enregistré dans SQLite ;
4. transformé en texte indexable ;
5. vectorisé ;
6. enregistré dans ChromaDB avec le même identifiant.

### Recherche

Pour une requête comme `chaise moderne noire` :

1. le frontend envoie la requête à FastAPI ;
2. le texte est transformé en embedding ;
3. ChromaDB retourne les IDs et les scores de similarité ;
4. SQLite récupère les fiches complètes correspondantes ;
5. FastAPI renvoie les résultats enrichis au frontend.

Lorsque Ollama est disponible, l'embedding de la requête est généré via
`POST /api/embed`. En développement hors connexion, un vectoriseur local de
secours est utilisé.

## 12. Démarrage local

### Backend

Depuis un terminal PowerShell :

```powershell
cd "C:\chemin\vers\SAE_3D_Gallery_Search\backend"
uv sync
uv run python scripts/indexer.py
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

L'API est disponible sur `http://127.0.0.1:8000`.
La documentation interactive est disponible sur `http://127.0.0.1:8000/docs`.

### Frontend

Dans un deuxième terminal :

```powershell
cd "C:\chemin\vers\SAE_3D_Gallery_Search\frontend"
npm install
npm run dev
```

L'interface est disponible sur `http://localhost:5173`.

### Vérifications rapides

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
Invoke-RestMethod http://127.0.0.1:8000/api/stats
Invoke-RestMethod http://127.0.0.1:8000/api/sante
```

Routes Lot C principales :

```text
GET  /api/recherche?q=chaise%20rouge&k=12
GET  /api/modeles/{id}
GET  /api/sante
POST /api/models/upload
```

## 13. Configuration Ollama

Les paramètres Ollama peuvent être définis dans un fichier `.env` à la racine du
backend :

```dotenv
OLLAMA_BASE_URL=http://127.0.0.1:11434
MODELE_EMBEDDING=embeddinggemma
OLLAMA_TIMEOUT_S=30
```

Ollama ne doit pas être exposé directement sur Internet. En production, il doit
rester accessible sur le réseau privé du serveur.

## 14. Mise en ligne

L'architecture recommandée est la suivante :

```text
Internet
    ↓
Nginx ou Caddy
    ├── frontend/dist/
    └── /api → FastAPI
                  ├── SQLite
                  ├── ChromaDB
                  ├── fichiers 3D
                  └── Ollama privé
```

### Préparation du serveur

Sur un serveur Linux ou une VM :

```bash
git clone URL_DU_REPOSITORY
cd SAE_3D_Gallery_Search/backend
uv sync
uv run python scripts/indexer.py
```

Construire ensuite le frontend :

```bash
cd ../frontend
npm install
npm run build
```

Le site compilé se trouve dans `frontend/dist/`. Il peut être servi par Nginx ou
Caddy. FastAPI doit écouter uniquement en local :

```bash
cd ../backend
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

Exemple de configuration Nginx :

```nginx
server {
    listen 80;
    server_name galerie.example.com;

    root /var/www/3d-gallery/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
    }
}
```

En production, il faudra également :

- remplacer `allow_origins=["*"]` par le domaine réel ;
- activer HTTPS avec Caddy ou Let's Encrypt ;
- conserver `client_max_body_size 50M` pour les fichiers 3D ;
- ne pas exposer ChromaDB ni Ollama publiquement ;
- sauvegarder `backend/data/gallery.sqlite3` ;
- sauvegarder `backend/data/vector_store/` ;
- sauvegarder `backend/data/models/` ;
- sauvegarder `donnees/fiches/`.
