#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we create a bit
more complicated window layout using
the QGridLayout manager.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import (QWidget, QLabel, QLineEdit,
                             QTextEdit, QGridLayout, QApplication)

class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        title = QLabel('Title')
        author = QLabel('Author')
        review = QLabel('Review')

        titleEdit = QLineEdit()
        authorEdit = QLineEdit()
        reviewEdit = QTextEdit()

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title, 0, 0)
        grid.addWidget(titleEdit, 0, 1)

        grid.addWidget(author, 1, 0)
        grid.addWidget(authorEdit, 1, 1)

        # (foo, x, y)
        # (foo, x, y, row span, column span)
        # on met reviewEdit troisième ligne, colonne 1 (commence à 0) et il a
        # une hauteur de cinq lignes pour une largeur de une colonne.
        grid.addWidget(review, 2, 0)
        grid.addWidget(reviewEdit, 2, 1, 5, 1)

        # Il faut noter que dans son tuto, l'auteur fait commencer les indices
        # des lignes à 1 et non 0 comme les colonnes. C'est parfaitement légal.
        # En fait, on peut même faire commencer les lignes à 4 ou 23867868. Je
        # hais Python.
        
        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Review')
        self.show()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
