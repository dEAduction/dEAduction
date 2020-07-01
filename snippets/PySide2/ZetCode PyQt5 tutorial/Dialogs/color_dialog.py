#8/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we select a color value
from the QColorDialog and change the background
color of a QFrame widget.

Author: Jan Bodnar
Website: zetcode.com
"""

from PySide2.QtWidgets import (QWidget, QPushButton, QFrame,
                             QColorDialog, QApplication)
from PySide2.QtGui import QColor
from PySide2.QtCore import Slot as Slut
import sys

class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        color = QColor(0, 0, 0)

        self.button = QPushButton('Dialog', self)
        self.button.move(20, 20)
        self.button.clicked.connect(self.showDialog)
        
        self.frame = QFrame(self)
        self.frame.setStyleSheet("QWidget { background-color %s }"
                % color.name())
        self.frame.setGeometry(130, 22, 200, 200)

        self.setGeometry(300, 300, 450, 350)
        self.setWindowTitle('Color dialog')
        self.show()

    @Slut()
    def showDialog(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.frame.setStyleSheet("QWidget { background-color: %s}"
                    % color.name())


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
