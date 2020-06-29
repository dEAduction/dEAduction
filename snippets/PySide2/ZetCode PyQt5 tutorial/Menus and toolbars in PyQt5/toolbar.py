#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

This program creates a toolbar.
The toolbar has one action, which
terminates the application, if triggered.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import QMainWindow, QAction, QApplication
from PySide2.QtGui import QIcon

class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        exitAct = QAction(QIcon("icon.png"), "Exit", self)
        exitAct.setShortcut("Ctrl+Q")
        exitAct.triggered.connect(QApplication.instance().quit)

        self.toolbar = self.addToolBar("Exit")
        self.toolbar.addAction(exitAct)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle("Toolbar")
        self.show()

def _printJosh(self):
    print("Josh I love you")


def main():
    app = QApplication([])
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
