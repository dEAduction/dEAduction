#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

This example shows an icon
in the titlebar of the window.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtGui import QIcon


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle("Icon, setWindowTitle")
        self.setWindowIcon(QIcon("icon.png"))

        self.show()

def main():

    app = QApplication(sys.argv)
    exInstance = Example()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
