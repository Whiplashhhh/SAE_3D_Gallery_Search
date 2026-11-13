# FAQ

## Pourquoi je ne vois aucun modèle ?

Vérifiez que Docker Compose a terminé son démarrage et que la santé API indique cinq fiches :

```powershell
docker compose ps
Invoke-RestMethod http://localhost:8080/api/sante
```

Au premier lancement, attendez que l'image Ollama et `embeddinggemma` soient téléchargés, puis
consultez `docker compose logs -f backend`.

## Est-ce qu'il faut être connecté au réseau de l'IUT ?

Non pour le lancement Docker documenté ici : Compose démarre Ollama localement et le backend s'y
connecte sur le réseau Docker. Le port `11434` n'est publié que sur l'interface locale.

## Pourquoi la page détail n'affiche pas de modèle 3D ?

Les fiches de démonstration n'ont pas de fichier `.obj`, `.gltf` ou `.stl` associé. La page affiche
leurs informations textuelles. L'aperçu apparaît uniquement lorsqu'un fichier source est présent
pour l'identifiant demandé.

## J'ai envoyé un modèle : pourquoi ne sort-il pas dans la recherche ?

L'import enregistre le fichier, mais les Lots A et B (rendu multi-vues et fiche sémantique) ne sont
pas lancés automatiquement. Il faut produire et indexer la fiche avant qu'elle soit recherchable.

## Comment voir les journaux ?

```powershell
docker compose logs -f backend
docker compose logs -f ollama
docker compose logs -f ollama-models
```

## Comment réinitialiser les données ?

`docker compose down` arrête les conteneurs en conservant les volumes. La commande
`docker compose down -v` efface également les données du backend et les modèles Ollama téléchargés;
le prochain démarrage devra les reconstruire et les retélécharger.
