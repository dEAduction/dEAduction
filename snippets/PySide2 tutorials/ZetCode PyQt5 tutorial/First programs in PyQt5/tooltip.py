#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

This example shows a tooltip on
a window and a button.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import QWidget, QToolTip, QPushButton, QApplication
from PySide2.QtGui import QFont


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 30))
        self.setToolTip("This is a <b>QWidget</b> widget")

        btn = QPushButton("Hey gorge", self)
        btn.setToolTip("This is a <b>QPushButton</b> widget")
        btn.resize(btn.sizeHint())
        btn.move(100, 100)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle("Tooltips")
        self.show()

def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
