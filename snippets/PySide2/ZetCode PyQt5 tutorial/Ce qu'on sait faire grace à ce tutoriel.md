# Éléments d'interfaces ## Barres ### Types de barres
- barre des menus [Menus and toolbars in PyQt5/menubar.py] barre d'outil [Menus
- and toolbars in PyQt5/toolbar.py] barre de statut [Menus and toolbars in
- PyQt5/statusbar.py]
### Actions
- ajouter des actions et sous menus dans la barre des menus [Menus and toolbars
	in PyQt5/submenu.py]
- cocher ou décocher des actions de menus [Menus and toolbars in
	PyQt5/check_menu.py]
- créer un menu contextuel (clic droit) [Menus and toolbars in
	PyQt5/context_menu.py] ## Boutons
- ajouter un tooltip [First programs in PyQt5/tooltip.py, setToolTip]
- dimensionner le bouton [First programs in PyQt5/quit_button, resize] bouger
- le bouton [First programs in PyQt5/quit_button.py, move]
## Fenêtres
- Les fenêtres sont des objets (QWidget, QMainWindow) du module
- PySide2.QtWidgets.
### Types de fenêtres
- une petite fenêtre affichant un *question* (il y a un gros ? dessus) et deux boutons
	(Yes et No), chacun étant associé à une action [First programs in
	PyQt5/messagebox.py]
- une fenêtre vide toute conne (QWidget)
- une fenêtre principal d'application [Menus and toolbars in
	PyQt5/main_window.py]
### Actions
- ajouter un titre de fenêtre [First programs in PyQt5/simple.py,
- setWindowTitle] dimensionner la fenêtre [First programs in PyQt5/simple.py,
- resize] bouger la fenêtre [First programs in PyQt5/simple.py, move] on peut
- fusionner resize et move avec setGeometry fermer la fenêtre center la fenêtre
- [First programs in PyQt5/center.py]

# Processus
- ajouter un bouton pour quitter l'application [First programs in PyQt5/quit_button.py]


# Organisation des fenêtres
- les fenêtres sont organisées dans des layout (QHBoxLayout, QVBoxLayout, etc)
- on peut les organiser de manière absolue [Layout management in
	PyQt5/absolute.py]
- on peut organiser les fenêtres sur une grille [Layout management in
	PyQt5/calculator.py]
- l'équivalent du \hfill ou \vfill LaTeX pour pousser des éléments au sein d'un
	layout est la méthode setStretch
