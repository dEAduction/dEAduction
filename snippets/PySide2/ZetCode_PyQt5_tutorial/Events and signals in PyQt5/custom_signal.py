#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we show how to
emit a custom signal.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtCore import Signal, QObject
from PySide2.QtWidgets import QMainWindow, QApplication

class Communicate(QObject):

    closeApp = Signal()


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # The custom closeApp signal is connected to the close() slot of the
        # QMainWindow
        self.c = Communicate()
        self.c.closeApp.connect(self.close)
    
        self.setGeometry(300, 300, 450, 350)
        self.setWindowTitle('Emit signal')
        self.show()
    
    # On émet le signal closeApp lorsque que l'on clique avec la souris
    def mousePressEvent(self, event):
        self.c.closeApp.emit()


def main():
    app = QApplication()
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
