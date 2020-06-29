#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

This program creates a statusbar.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import QMainWindow, QApplication

class Example(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.statusBar().showMessage("Ready")

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle("Status bar")
        self.show()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
