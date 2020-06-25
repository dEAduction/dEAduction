#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

This program creates a quit
button. When we press the button,
the application terminates.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import QWidget, QPushButton, QApplication

class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        btn_quit = QPushButton("Quit", self)
        btn_quit.resize(btn_quit.sizeHint())
        btn_quit.move(50, 50)
        btn_quit.clicked.connect(QApplication.instance().quit)

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle("Quit button")
        self.show()

def main():

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
