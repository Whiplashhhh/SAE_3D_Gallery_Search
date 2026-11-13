# Recherche (Lot C)

## Routes exposées

Le frontend utilise principalement ces routes, préfixées par `/api` :

| Méthode | Route | Rôle |
|---|---|---|
| `GET` | `/recherche?q=...&k=12` | Recherche vectorielle et résultats classés par score. |
| `GET` | `/models` | Liste les fiches disponibles; utilisée pour le catalogue. |
| `GET` | `/modeles/{id}` | Renvoie le détail d'une fiche, les descriptions par vue et les divergences. |
| `GET` | `/modeles/{id}/fichier` | Renvoie le fichier 3D si disponible. |
| `DELETE` | `/modeles/{id}` | Supprime la fiche et ses entrées associées. |
| `POST` | `/models/upload` | Sauvegarde un fichier `.obj`, `.gltf` ou `.stl` (50 Mo maximum); ne le rend pas recherchable. |
| `GET` | `/sante` | Indique l'état d'Ollama et les compteurs du catalogue et de ChromaDB. |
| `GET` | `/stats` | Renvoie les compteurs du catalogue et de la collection. |

La page détail `/modeles/:id` du frontend consomme `GET /api/modeles/{id}`. Elle affiche la fiche
sémantique et demande le fichier source séparément seulement si `fichier_3d_disponible` vaut
`true`.

Pour lancer la pile locale Ollama + backend + frontend, consultez
[Installation & déploiement](../technique/deploiement.md).

## Routes de l'API

::: recherche.router

## Service de recherche

::: recherche.service_recherche

## Service d'indexation

::: recherche.service_indexation

## Chargeur de fiches

::: recherche.chargeur_fiches

## Service ChromaDB

::: recherche.service_chroma

## Dépôt vectoriel

::: recherche.depot_vectoriel

## Moteur de recherche

::: recherche.moteur_recherche
