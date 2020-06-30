#!/usr/bin/python

"""
On essaie de disposer trois boutons sur une grid en ne donnant que deux
positions. On se rend compte que si l'on essaie de mettre un boutton à une
position BBB sur laquelle était déjà un autre bouton AAA, Qt ne le met pas et
ignore l'instruction.

Il n'y a pas besoin de définir la grille au début, mais une case est ajoutée à
chaque fois que l'on utilise grid.addWidge(btn, *pos). On définit donc une
grille avec une liste de positions de N^2 à la volée.
"""

import sys
from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication

class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)

        btnAAA = QPushButton("AAA")
        btnBBB = QPushButton("BBB")

        positions = [(0, 0)]
        
        for pos, btn in zip(positions, [btnAAA, btnBBB]):
            grid.addWidget(btn, *pos)

        self.show()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
