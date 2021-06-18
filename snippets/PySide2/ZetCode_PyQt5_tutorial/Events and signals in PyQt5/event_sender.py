#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we determine the event sender
object.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import QMainWindow, QPushButton, QApplication
from PySide2.QtCore import Slot


class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        btn1 = QPushButton("Button 1", self)
        btn1.move(30, 50)

        btn2 = QPushButton("Button 2", self)
        btn2.move(150, 50)

        btn1.clicked.connect(self.buttonClicked)
        btn2.clicked.connect(self.buttonClicked)

        self.statusBar()

        self.setGeometry(300, 300, 450, 350)
        self.setWindowTitle("Event sender")
        self.show()

    # The Slot decorator is not used in ZetCode's turorial but it is
    # recommended to use it in PySide2 official tutorial, see
    # https://doc.qt.io/qtforpython/tutorials/basictutorial/clickablebutton.html
    @Slot()
    def buttonClicked(self):
        # À propos de .sender(). Returns a pointer to the object that sent the
        # signal, if called in a slot activated by a signal; otherwise it
        # returns nullptr. The pointer is valid only during the execution of
        # the slot that calls this function from this object's thread context.
        # Voir https://doc.qt.io/qt-5/qobject.html#sender
        # Both buttons are connected to the same slot.
        # We determine the signal source by calling the sender() method. In the
        # statusbar of the application, we show the label of the button being
        # pressed.
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + " was pressed")

def main():
    app = QApplication([])
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
