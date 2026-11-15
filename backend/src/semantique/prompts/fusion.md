Tu reçois les descriptions de plusieurs vues d'un même objet 3D. Chaque vue a été
décrite séparément, à partir d'une seule image prise autour de l'objet.

Ton travail est de fusionner ces descriptions en une seule description de l'objet.

Règles :

- Utilise uniquement les informations présentes dans les descriptions des vues.
- N'invente aucun détail qui n'apparaît dans aucune vue.
- Si deux vues se contredisent (nombre de pieds, couleur, matériau, forme...),
  ne choisis pas en silence : écris la contradiction dans `divergences_entre_vues`.
- Une partie visible sur une vue et absente d'une autre n'est pas une contradiction :
  elle est peut-être simplement cachée sur l'autre vue.
- Écris en français, avec des phrases courtes et factuelles.

Réponds uniquement avec un objet JSON, sans texte autour, avec ces champs :

- `description` : la description globale de l'objet, en quelques phrases.
- `divergences_entre_vues` : une phrase par contradiction entre les vues
  (ex : ["La vue de face montre 4 pieds, la vue de dessus en montre 5."]).
  Liste vide s'il n'y a aucune contradiction.
