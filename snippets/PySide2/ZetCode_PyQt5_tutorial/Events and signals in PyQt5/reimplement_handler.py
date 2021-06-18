#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we reimplement an
event handler.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QApplication


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Event handler')
        self.show()

    # We reimplement the keyPressEvent() event handler.
    # event is of type QKeyEvent
    # https://doc.qt.io/qt-5/qkeyevent.html
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
