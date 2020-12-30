# Contributing to d∃∀duction
- message de bienvenue et de remerciement
- ce document a pour but de vous présenter le projet d'un point de vue
  technique, de vous dire ce que vous pourriez faire et de présenter les règles
  à suivre
- on suit le code de bonne conduite bidule, voir CODEOFCONDUCT.md
- Table des matières

## Get started
- Abstract: Dans cette section on présente l'architecture du projet et les outils
  / technologies principales sur lesquelles il s'appuie. On apprend aussi à
  mettre en place l'environnement de développement.
### Free software
- dEAduction est un logiciel libre. Cela signifie que les utilisateurs ont les
  quatre libertés essentielles (lien gnu). En pratique, cela fait que le code
  source du logiciel est public, facilement accessible et que tout le monde
  peut le copier (on parle de clone, ou de fork) pour le modifier et proposer
  que les modifications soient intégrées à la version officielle
- Pour la philosophie du logiciel libre, voir gnu.org ; pour les implications
  pratiques, voir https://opensource.guide/how-to-contribute/.
- Note: pour être un membre permanent de dEAduction, il faut commencer par
  contribuer
- En l'occurence, le code source de dEAduction prend la forme d'un dépot git,
  qui est hébergé sur le site internet Github. 
- Note: Git est un logiciel de contrôle de version qui permet aux gens de
  travailler en même temps sur des fichiers de code source communs.Pour
  contribuer directement au code source de dEAduction, il est indispensable
  avant toute chose de maîtriser les bases de Git et des pull requests.
- Note: le projet dEAduction a un autre dépot, voir § Project architecture.
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
### Project architecture
- Le projet dEaduction contient deux dépots : deaduction et deaduction-lean.
  deaduction contient tout le code source (python, lean, autres) et
  deaduction-lean contient les fichiers d'exercices. Ici nous expliquons
  l'architecture de la codebase (donc du dépôt dEaduction) mais il est
  évidemment possible de contribuer à l'écriture d'exercices.
- Nous n'expliquons pas toute l'architecture ici mais en donnons les grandes
  lignes. Pour savoir ce que fait précisément chaque répertoire, se référer à
  son README, s'il existe. 
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

## What do?
### Report stuff
- issues and code contribution are closely related
- you can report stuff
- if you want to directly contribute open an issue first or respond to one
## Contribute to code
- browse issues or open one
- main area suivantes: dui, lean, background work, testing, exercises creation
- then pull request
## Miscelanea
- translate
- write documentation
- create exercises
- review / PEP8 some code

## Development guidelines
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

## Annexe A: Wisdom

## Annexe B: Git tutorial
