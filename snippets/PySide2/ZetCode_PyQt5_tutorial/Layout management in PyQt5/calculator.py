#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we create a skeleton
of a calculator using QGridLayout.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication

# Ce code n'est pas très joli car plutôt que deux faire deux layouts, avec un
# premier pour la première ligne et un deuxième pour les chiffres et opérations
# mathématiques, il met tout dans un seul layout et créée un « bouton vide »
# pour mettre un espace. Remarque, ça permet d'avoir les bons alignements.

# Pour comprendre comment fonctionne la grille, voir la docstring
# snippets/Divers/Kryzar/grid.py

class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # The instance of a QGridLayout is created and set to be the layout for
        # the application window.
        grid = QGridLayout()
        self.setLayout(grid)

        names = ['Cls', 'Bck', '', 'Close',
                 '7', '8', '9', '/',
                 '4', '5', '6', '*',
                 '1', '2', '3', '-',
                 '0', '.', '=', '+']

        positions = [(i, j) for i in range(5) for j in range(4)]

        for position, name in zip(positions, names):
            if name != '': 
                button = QPushButton(name)
                grid.addWidget(button, *position)

        self.move(300, 150)
        self.setWindowTitle("Calculator")
        self.show()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
