# Guide d'utilisation

## Ouvrir la galerie

Démarrez les services avec `docker compose up --build`, puis ouvrez
<http://localhost:8080>. La page d'accueil présente jusqu'à trois modèles et des suggestions de
recherche. **Voir le catalogue** ouvre la liste complète.

## Rechercher un modèle

1. Entrez une description dans le champ de recherche, par exemple `chaise` ou `voiture`.
2. Lancez la recherche. Les résultats sont classés par pertinence; le score apparaît sur chaque
   carte.
3. Cliquez sur une carte pour ouvrir sa fiche détaillée.

Une recherche vide dans le catalogue affiche les modèles disponibles. Le jeu de démonstration
contient cinq thèmes : chaise, maison, voiture, arbre et épée.

## Consulter la fiche détaillée

La page `/modeles/{id}` présente le titre, la catégorie, la description globale, les descriptions
de chaque vue et les divergences détectées entre les vues. Si le backend dispose du fichier 3D
correspondant, un aperçu interactif est également proposé.

Les seeds fournis sont des fiches sémantiques sans fichier source 3D; leur aperçu est donc absent.

## Ajouter un modèle

Dans **Ajouter un modèle**, choisissez ou déposez un fichier `.obj`, `.gltf` ou `.stl` de 50 Mo
maximum. Un aperçu local permet de vérifier le fichier avant l'envoi.

L'envoi sauvegarde le fichier, mais ne génère pas encore ses vues ou sa fiche sémantique. Le modèle
ne sera pas dans les résultats avant son traitement par les Lots A et B puis son indexation.

## Vérifier les services

La page <http://localhost:8080/api/sante> indique si Ollama répond ainsi que le nombre de fiches et
de vecteurs indexés. La documentation interactive de l'API est disponible sur
<http://localhost:8000/docs>.
