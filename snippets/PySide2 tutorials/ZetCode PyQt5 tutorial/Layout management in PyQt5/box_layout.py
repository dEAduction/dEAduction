#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we position two push
buttons in the bottom-right corner
of the window.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
                                QApplication)

class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        JoshButton = QPushButton("Josh")
        okButton = QPushButton("Ok")
        cancelButton = QPushButton("Cancel")

        # We create a horizontal box layout and add a stretch factor and both
        # buttons. The stretch adds a stretchable space before the two buttons.
        # This will push them to the right of the window.
        # De ce que je comprends, le Layout joue comme un div en css dans
        # lequel on fout des trucs, juste qu'ici on précise horizontal ou
        # vertical. Ici, le Stretch correspond à un \hfill de LaTeX, il sert à
        # remplir l'espace pour foutre tous les objets déclarés après à droite.
        # Je crois qu'on n'a même pas besoin de mettre d'argument. Du coup, ça
        # ressemble à ça :
        # -------------------------------------------|
        # | Josh   ssssttreeettccchhhh   Ok   Cancel |
        # --------------------------------------------
        hbox = QHBoxLayout()
        hbox.addWidget(JoshButton)
        hbox.addStretch(1)
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)

        # The horizontal layout is placed into the vertical layout. The stretch
        # factor in the vertical box will push the horizontal box with the
        # buttons to the bottom of the window.
        # Ici on ajoute le hbox (Layout) au vbox comme si c'était un élément
        # normal et on fout un stretch pour le pousser vers le bas. En ayant
        # combiné les deux stretch, les boutons se retrouvent en bas à droite.
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Buttons')
        self.show()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
