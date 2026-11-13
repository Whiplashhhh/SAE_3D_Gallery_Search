# Installation & déploiement

## Prérequis

- Docker Desktop démarré avec le plugin Docker Compose.
- Une connexion Internet au premier lancement pour récupérer les images Docker et le modèle
  Ollama `embeddinggemma`.
- Assez d'espace disque pour les images et les données persistantes. Le premier téléchargement peut
  prendre plusieurs minutes.

## Lancer l'application

Depuis la racine du dépôt :

```powershell
docker compose up --build
```

Adresses locales :

| Service | Adresse |
|---|---|
| Galerie Vue | <http://localhost:8080> |
| Documentation OpenAPI | <http://localhost:8000/docs> |
| Santé API | <http://localhost:8080/api/sante> |
| Ollama (hôte local seulement) | <http://localhost:11434> |

Compose démarre Ollama, télécharge `embeddinggemma`, puis construit les fiches de démonstration
avec de vrais embeddings avant de lancer l'API. Le backend communique avec Ollama à l'adresse
interne `http://ollama:11434`; il n'a pas besoin d'accéder au serveur Ollama de l'IUT.

Pour démarrer en arrière-plan :

```powershell
docker compose up --build -d
```

Suivre les journaux :

```powershell
docker compose logs -f ollama
docker compose logs -f ollama-models
docker compose logs -f backend
```

Arrêter les conteneurs :

```powershell
docker compose down
```

Les données restent conservées dans les volumes nommés `backend-data` et `ollama-models`.
`docker compose down -v` les supprime aussi, y compris les fiches et index générés ainsi que le
modèle Ollama téléchargé.

## Vérifier l'état

```powershell
Invoke-RestMethod http://localhost:8080/api/sante
```

Quand l'initialisation est terminée, la réponse doit indiquer `ollama_joignable: true`,
`fiches_indexees: 5` et `vecteurs_indexes: 5`.

## Développement sans Docker

Le frontend peut être lancé séparément :

```powershell
cd frontend
npm ci
npm run dev
```

Le backend local requiert Python 3.11 à 3.14, `uv` et une instance Ollama joignable. Sa configuration
est chargée depuis les variables d'environnement et `.env`; les valeurs requises sont listées dans
`backend/src/config.py`. Depuis `backend/` :

```powershell
uv sync --locked
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Le proxy Vite transmet les appels `/api` vers `http://127.0.0.1:8000`. Configurez
`OLLAMA_BASE_URL` pour pointer vers votre instance Ollama et vérifiez que le modèle d'embedding
configuré y est disponible.

## Dépannage

- **L'API ne répond pas ou le front affiche une erreur** : vérifiez `docker compose ps`, puis les
  journaux du backend. L'API est publiée sur `127.0.0.1:8000` et le site la contacte via Nginx.
- **`ollama_joignable` vaut `false`** : vérifiez que le service `ollama` est sain et que
  `ollama-models` s'est terminé sans erreur.
- **Aucune fiche n'est indexée** : vérifiez les journaux du backend pendant le chargement des seeds
  et la création des embeddings.
- **La page détail n'a pas d'aperçu 3D** : les fiches de démonstration sont des données
  sémantiques; elles ne fournissent pas de fichier OBJ/GLTF/STL.
