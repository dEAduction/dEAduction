# Old
## dui.widgets
ActionButton
ActionButtonsWidget
DisclosureTriangle
ExerciseCentralWidget
ExerciseMainWindow
ExerciseToolBar
HorizontalLine
IconStatusBar
LeanEditor
MathObjectWidget
MathObjectWidgetItem
RecentCoursesLW
RecentCoursesLWI
StatementsTreeWidget
StatementsTreeWidgetItem
StatementsTreeWidgetNode
TargetWidget
TextEditLogger
## dui.widgets.dialogs
ButtonsDialog
InstallingMissingDependencies
ReallyWantQuit
StartExerciseDialog
WantInstallMissingDependencies
YesNoDialog
## dui.functions
read_pkl_course
replace_widget_layout
set_item_selectable

# New?

Philosophie générale. La nouvelle organisation est sémentique pour
l'utilisation (de dEAduction) plutôt que sémentique pour le code ; on ne
regroupe plus les classes par commun parent (p. ex. `QWidget`). L'utilisation
est divisée en *phases* (`dui.phases`) : phase de choix d'exercice
(`dui.startex`), phase durant laquelle usr fait son exercice (`dui.emw`, pour
*exercise main window*), etc. Tout ne rentre pas dans les *phases* et il y a
d'autres modules.

## dui.elements

Éléments d'interfaces utilisés à l'intérieur d'autres plus gros éléments
d'interface (p. ex. la liste des cours est un *element* de la fenêtre
d'exercice) qui sont utilisés dans plusieurs *phases* (voir `dui.phases`)
différentes, voire même dans un autre module que `dui`. Ici, « utilisation » ne
veut pas forcément dire « instanciation » : la plupart de ces types ne seront
importés que pour signer une fonction. À la création d'un élément d'interface,
il est préférable de le laisser si possible dans sa phase correspondante et de
ne pas trop charger `dui.elements`.

- ActionButton
- ActionButtonsWidget
- LeanEditor
- MathObjectWidget
- MathObjectWidgetItem
- RecentCoursesLW
- RecentCoursesLWI
- StatementsTreeWidget
- StatementsTreeWidgetItem
- StatementsTreeWidgetNode
- TargetWidget

## dui.parents

Les classes de `dui.parents` sont des classes « générales » qui doivent être
dérivées pour un usage spécifique (ou dans une moindre mesure instanciées et
modifiées avec les méthodes et `__init__`). Par exemple, `YesNoDialog` est
dérivée dans un autre module en `ReallyWantQuit`. Ce module peut aussi contenir
des classes abstraites (*abstract* au sens de Qt) qui contiennent toute la
mécanique pour un usage spécifique mais doivent impérativement être dérivées
pour être utilisées. Noter que toutes ces telles classes ne sont pas dans
`dui.parents` : il y a p. ex. une classe AbstractCoExChooser n'est utilisée que
dans un module bien spécifique et n'a donc pas lieu d'être répertoriée dans
`dui.parents`. On ne met donc dans `dui.parents` que des classes suffisamment
générales ou abstraites pour être utilisées ailleurs.

- ButtonsDialog
- DisclosureTriangle
- TextEditLogger
- YesNoDialog

## dui.phases

### dui.phases.emw

Phase durant laquelle usr fait l'exercice.

- ExerciseCentralWidget
- ExerciseMainWindow
- ExerciseToolBar
- IconStatusBar

### dui.phases.missdep

Phase de gestion des dépendances manquantes.

- WantInstallMissingDependencies
- InstallingMissingDependencies

### dui.phases.quitdead

Phase de sortie (quit) de dEAduction.

- ReallyWantQuit

### dui.phases.startex

Phase de choix et démarrage d'un nouvel exercice (au lancement de dEAduction
comme à la fin d'un exercice).

- StartExerciseDialog

## dui.utils

Fourre tout à utilitaires qui peuvent être instanciés *as is*

- read_pkl_course
- replace_widget_layout
- HorizontalLine
- set_item_selectable
