#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

This program creates a skeleton of
a classic GUI application with a menubar,
toolbar, statusbar, and a central widget.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PySide2.QtGui import QIcon


class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        # Here we create a text edit widget. We set it to be the central widget
        # of the QMainWindow. The central widget occupies all space that is
        # left.
        textEdit = QTextEdit()
        self.setCentralWidget(textEdit)

        # En l'état, il n'y a qu'une seule action dans le menu File, c'est
        # l'action Exit, et donc Qt la met automatiquement dans Python >
        # Quitter l'application, car c'est le comportement standard sur macOS.
        # Si l'on veut afficher l'action de quitter dans le menu fichier il
        # faut lui changer de nom, mettre " Exit" plutôt que "Exit" ou override
        # le système avec un trick commenté dans un fichier précédent de ce
        # tuto. Let mac be mac tho.
        exitAct = QAction(QIcon("exit.png"), "Exit (mouse hoover)", self)
        exitAct.setShortcut("Ctrl+Q")
        # setStatusTip marche ici pour la barre d'outils mais ne marchait pas
        # dans simple_menu.py avec une action de la barre de menus.
        exitAct.setStatusTip("Exit application")
        # Ici on utilise self.close et non QApplication.instance().quit, ça
        # change.
        exitAct.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(exitAct)

        toolbar = self.addToolBar("Exit")
        toolbar.addAction(exitAct)

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Main window')
        self.show()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
