# Contributing to d∃∀duction

- Welcome et merci ! Contribuer à dEAduction est le meilleur moyen de nous
  soutenir ! We don't know what we're doing.

- dEAduction est un logiciel libre (voir Annexe A) : tout le monde peut
  contribuer à dEAduction. Ce document dit en quoi vous pouvez aider et comment
  vous pouvez le faire.

- Table des matières

## Get started
- Abstract: Dans cette section on présente l'architecture du projet, les outils
  utilisés et l'env. de traail
### Project architecture
- Le projet dEaduction contient deux dépots : deaduction et deaduction-lean.
  deaduction contient tout le code source (python, lean, autres) et
  deaduction-lean contient les fichiers d'exercices. Ici nous expliquons
  l'architecture de la codebase (donc du dépôt dEaduction) mais il est
  évidemment possible de contribuer à l'écriture d'exercices.
- En gros :
	* dui/: tout ce qui relève de l'interface graphique (widgets et éléments
	  Qt, resources graphiques) et du démarrage de dEAduction (fichier main);
	* pylib/: Ce dossier contient la plupart (tous ?) des modules Python qui ne
	  relèvent pas de dui/. Le parsage des cours et exercices est fait dans
	  coursedata/, les classes d'objets mathématiques sont dans mathobj/, la
	  communication entre LEAN et l'interface sont dans /server, 
### Environment configuration
- source envconfig
- vim
- you can also use an IDE, PyCharm is recommanded
### Prérequis
- voir pour chaque partie de What do?

## What do?
### Report stuff
- issues and code contribution are closely related
- you can report stuff
- if you want to directly contribute open an issue first or respond to one
### Contribute to code
- browse issues or open one
- main area suivantes: dui, lean, background work, testing, exercises creation
- then pull request
### Translate
### Write documentation
### Create exercises
### Review / PEP8 some code

## Guidelines
### Git commit messages
### Git branch workflow
### Github issues format
### Pull requests
### Files format
- header
### Python code
- PEP8 modifié
- typing
- signatures
- fichiers init
### Git commit messages
### Code documentation
- document your code
- what should comments tell
- docstrings
- function signatures

## Annexe A: Logiciel libre

- dEAduction est un logiciel libre. En gros, le logiciel libre c'est …. En
  pratique, cela fait que le code source du logiciel est public, facilement
  accessible et que tout le monde peut le copier (on parle de clone, ou de
  fork) pour le modifier et proposer que les modifications soient intégrées à
  la version officielle
- Pour la philosophie du logiciel libre, voir gnu.org ; pour les implications
  pratiques, voir https://opensource.guide/how-to-contribute/.
- En l'occurence, le code source de dEAduction prend la forme d'un dépot git
  (voir Annexe B), qui est hébergé sur le site internet Github. 
- En général, les personnes qui contribuent à un projet logiciel libre peuvent
  être classés ainsi (https://opensource.guide/how-to-contribute/, § Anatomy of
  an open source project). Ici les auteurs / owners sont machins et trucs, si
  vous contribuez vous serez contributeurs.
- Il n'y a pas de rétribution financière pour la contribution à dEAduction.
  Tout contributeur sera cependant crédité (liste dans README) et est bien
  évidemment désigné comme auteur de ses contributions.
- Il est possible de dialoguer avec les membres de l'équipe. Pour respecter la
  philosophie du logiciel libre, il faut si possible faire en sorte que les
  discussions soient publiques. Il faut pour cela utiliser les issues Github,
  voire § What do? ¶ Report stuff.

## Annexe B: Git tutorial

## Annexe C: Wisdom
