#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

This program creates a context menu.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import QMainWindow, QMenu, QApplication


class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle("Context menu")
        self.show()

    # contextMenuEvent() is a method of QMainWindow
    # it is activated with a right mouse click
    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        newAct = cmenu.addAction("New")
        joshAct = cmenu.addAction("Josh")
        quitAct = cmenu.addAction("Quit")
        # The context menu is displayed with the exec_() method. The get the
        # coordinates of the mouse pointer from the event object. The
        # mapToGlobal() method translates the widget coordinates to the global
        # screen coordinates.
        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == quitAct:
            QApplication.instance().quit()

        if action == joshAct:
            print("Josh I love you")


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
