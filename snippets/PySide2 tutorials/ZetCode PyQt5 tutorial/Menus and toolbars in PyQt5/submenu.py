#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

This program creates a submenu.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import QMainWindow, QAction, QMenu, QApplication

class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a menu bar
        menubar = self.menuBar()

        # Build a menu that looks like this.
        # +-- RHCP
        # |   +-- New
        # |   +-- Import >
        # |   |   +-- Import mail
        # RHCP and Import are QMenu whereas New and Import mail are QAction.

        # Define and add (sub)menus
        RHCP_menu = menubar.addMenu("RHCP")
        Import_menu = QMenu("Import", self)
        RHCP_menu.addMenu(Import_menu)
        
        # Define and add actions to (sub)menus
        Import_action = QAction("Import mail", self)
        Import_menu.addAction(Import_action)
        New_action = QAction("New", self)
        RHCP_menu.addAction(New_action)

        self.setWindowTitle('Submenu')
        self.show()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
