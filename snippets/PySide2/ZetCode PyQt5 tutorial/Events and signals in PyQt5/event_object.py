#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we display the x and y
coordinates of a mouse pointer in a label widget.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QApplication, QGridLayout, QLabel


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        x = 0
        y = 0

        self.text = f'x: {x},  y: {y}'

        self.label = QLabel(self.text, self)
        grid.addWidget(self.label, 0, 0, Qt.AlignTop)

        # Mouse tracking is disabled by default, so the widget only receives
        # mouse move events when at least one mouse button is pressed while the
        # mouse is being moved. If mouse tracking is enabled, the widget
        # receives mouse move events even if no buttons are pressed.
        self.setMouseTracking(True)

        self.setLayout(grid)

        self.setGeometry(300, 300, 450, 300)
        self.setWindowTitle('Event object')
        self.show()

    # mouseMoveEvent est une méthode de QWidget
    # https://doc.qt.io/qt-5/qwidget.html#mouseMoveEvent attention, avoir
    # re-défini cette méthode ne sert à rien si l'on n'a pas activé le tracking
    # de la souris avec self.setMouseTracking(True)
    # J'imagine que activer le tracking appelle automatiquement la méthode
    # mouseMoveEvent avec le bon event
    # The event is the event object; it contains data about the event that was
    # triggered; in our case, a mouse move event.
    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()
        text = f'x: {x},  y: {y}'
        self.label.setText(text)


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
