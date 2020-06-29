#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

This program creates a menubar. The
menubar has one menu with an exit action.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import QMainWindow, QAction, QApplication
from PySide2.QtGui import QIcon

class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # In the tutorial, it is menubar.addMenu("&File") and "&Exit" in
        # QAction. But this does not work on mac since those item titles are
        # "reserved" by macOS itself. It also does not work with variations of
        # "&Exit", "&Quit", "&Quit application", etc, and it is expected
        # behavior. There are workarounds for this:
        # https://stackoverflow.com/questions/39574105/missing-menubar-in-pyqt5/45171461#45171461
        # but it is just not good practice to override macOS. Also see the two
        # links at the end of the comment.
        # The setShortcut and setStatusTip also do NOT work on macOS.

        # Create a menu bar and a File menu
        menubar = self.menuBar()
        mb_File = menubar.addMenu("&RHCP")
        # Create an exit action for the menu bar and add it to FIle
        exit_action = QAction(QIcon('exit.png'), '&Josh Klinghoffer', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QApplication.instance().quit)
        mb_File.addAction(exit_action)

        # Status bar
        self.statusBar()

        # Standard shit
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle("Simple menu")

        self.show()

def main():
    app = QApplication([])
    ex = Example()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
