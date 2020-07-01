#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we connect a signal
of a QSlider to a slot of a QLCDNumber.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QWidget, QLCDNumber, QSlider, QVBoxLayout,
        QApplication)


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):

        # on créée un bouton et un slider
        number = QLCDNumber(self)
        slider = QSlider(Qt.Horizontal, self)

        # on les met tous deux dans un QVBoxLayout pour qu'ils soient affichés
        # l'un au dessus de l'autre
        vbox = QVBoxLayout()
        vbox.addWidget(number)
        vbox.addWidget(slider)
        self.setLayout(vbox)

        # Here we connect a valueChanged signal of the slider to the display
        # slot of the lcd number.
        slider.valueChanged.connect(number.display)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle("Signal and slut")
        self.show()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
