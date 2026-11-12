# Ollama

Dans le lancement Docker, le service `ollama` est local au projet. Le conteneur
`ollama-models` télécharge le modèle d'embedding configuré avant le démarrage du backend. Le
backend utilise l'adresse Docker `http://ollama:11434`; l'hôte publie le port `11434` uniquement
sur `127.0.0.1`.

Le modèle d'embedding sert aux requêtes de recherche et à l'initialisation des cinq fiches
d'exemple. Le traitement VLM/LLM des Lots A et B n'est pas lancé par la galerie.

::: ollama.client
