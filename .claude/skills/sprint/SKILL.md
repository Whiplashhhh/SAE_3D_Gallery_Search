---
name: sprint
description: Génère le fichier du sprint suivant dans docs/monitoring/ à partir des commits faits depuis le dernier sprint, avec des objectifs réalisables pour la semaine à venir. À lancer manuellement en fin de semaine avec /sprint.
argument-hint: "[remarques optionnelles, ex. : 'Lucas absent mercredi']"
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Bash(git log:*), Bash(git show:*), Bash(git diff:*), Bash(git rev-parse:*), Bash(git branch:*), Bash(git fetch:*), Bash(ls:*)
---

# /sprint — Générer le sprint de la semaine suivante

Tu produis **un seul fichier** : `docs/monitoring/sprint-NN.md` (NN = numéro du dernier sprint + 1,
sur deux chiffres). Tu ne fais **aucun** `git add`, `git commit`, `git push`, `git checkout`,
`git stash` ni aucune commande qui modifie l'historique ou l'arbre de travail. Seule écriture
autorisée : le nouveau fichier de sprint.

Remarques de l'équipe pour ce sprint (peut être vide) : $ARGUMENTS

## Étape 1 — Trouver le dernier sprint

1. Liste `docs/monitoring/sprint-*.md` et prends celui qui a le plus grand numéro.
2. Lis-le en entier. Son **format** (titres, ordre des sections, numérotation des US, tableau des
   livrables, DoR, DoD, risques) est le modèle à reproduire à l'identique.
3. Si le fichier `sprint-NN.md` que tu t'apprêtes à créer existe déjà, arrête-toi et demande
   à l'utilisateur s'il faut l'écraser.

## Étape 2 — Déterminer le commit de départ

Dans cet ordre de priorité :

1. Si le dernier sprint contient une ligne `**Commit de référence** : <hash>`, utilise ce hash.
2. Sinon, prends le commit qui a **ajouté** le fichier du dernier sprint :
   `git log --all --diff-filter=A --format=%H -1 -- docs/monitoring/sprint-NN.md`
3. Si le fichier n'est pas encore commité, demande le commit ou la date de départ à l'utilisateur.

Puis récupère le commit de fin : `git rev-parse HEAD`.

## Étape 3 — Collecter ce qui a été fait

Lance d'abord `git fetch --all --quiet` (lecture seule côté local) pour voir les branches des
coéquipiers, puis :

```
git log --all --no-merges <depart>..HEAD --format="%h|%an|%ad|%s" --date=short
```

Si `--all` ramène des commits qui ne sont pas des descendants du départ, utilise plutôt
`git log --all --no-merges --since=<date du commit de départ>`.

Pour chaque commit dont le message est vague (« fix », « wip », « maj »), regarde
`git show --stat <hash>` pour comprendre ce qu'il touche. Ne lis pas les diffs complets sauf
si c'est indispensable.

Regroupe ensuite les commits **par lot** d'après les chemins touchés :
- Lot A : rendu Blender, orchestration
- Lot B : VLM, LLM, prompts, vectorisation
- Lot C : ChromaDB, recherche, API, interface Vue 3
- Commun : `src/contrats/`, config, CI, docs, tests transverses

## Étape 4 — Faire le bilan du sprint précédent

Pour chaque US du dernier sprint, décide à partir des commits :
- ✅ **Faite** : des commits la couvrent clairement.
- 🟡 **Partielle** : du travail existe mais le critère de DoD n'est pas atteint.
- ❌ **Non commencée** : aucun commit lié.

N'invente rien : si un lien entre un commit et une US n'est pas évident, classe l'US en
partielle ou non commencée et dis-le. Un commit qui ne correspond à aucune US va dans
« Hors sprint ».

## Étape 5 — Proposer les objectifs de la semaine suivante

Règles pour les nouvelles US :
- **Très réalisables en une semaine** par une équipe de trois étudiants qui ont aussi des cours :
  vise **3 à 5 US par lot au maximum**, chacune faisable par une personne en quelques heures
  à une journée.
- Priorité 1 : terminer les US 🟡 partielles. Priorité 2 : reprendre les ❌ encore pertinentes.
  Priorité 3 : la suite logique de ce qui vient d'être fait.
- Chaque US a un critère de vérification concret (test `pytest`, commande reproductible,
  fichier produit).
- Respecte les contraintes du projet : lots indépendants qui ne communiquent que par des JSON
  sur disque, rien en dur (URL, modèles, dimension d'embedding), chemins relatifs, code et clés
  en français sans accents.
- Tiens compte des remarques passées en argument (absences, examens, etc.) en réduisant la charge.

## Étape 6 — Écrire le fichier

Reprends le format du dernier sprint et ajoute en tête, juste sous le titre :

```
**Période** : <date de début> → <date de fin prévue, +7 jours>
**Commit de référence** : <hash court de HEAD>
```

Le commit de référence sert de point de départ au prochain `/sprint` : c'est ce qui évite de
rater ou de compter deux fois des commits.

Ajoute une section **« Bilan du sprint précédent »** avant les nouvelles user stories, avec :
- un tableau `US | Statut | Commits liés` ;
- la liste « Hors sprint » des commits non rattachés ;
- une ligne de synthèse : nombre de commits, répartition par membre et par lot.

Garde DoR et DoD identiques au sprint précédent sauf si un changement est justifié par ce qui
s'est passé ; dans ce cas, signale-le dans ta réponse. Mets à jour la section des risques.

## Étape 7 — Répondre à l'utilisateur

Réponds brièvement : chemin du fichier créé, plage de commits analysée, nombre d'US reportées et
de nouvelles US, et les points où tu as dû deviner (commits ambigus). Rappelle que rien n'a été
commité.