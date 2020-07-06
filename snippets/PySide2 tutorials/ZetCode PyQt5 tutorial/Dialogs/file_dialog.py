#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we select a file with a
QFileDialog and display its contents
in a QTextEdit.

Author: Jan Bodnar
Website: zetcode.com
"""

from PySide2.QtWidgets import (QMainWindow, QTextEdit, QAction, QFileDialog,
        QApplication)
from PySide2.QtGui import QIcon
import sys
from pathlib import Path


class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.textEdit = QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.statusBar()

        openFile = QAction(QIcon('icon.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(openFile)

        self.setGeometry(300, 300, 550, 450)
        self.setWindowTitle('File dialog')
        self.show()


    # Comme showDialog n'est utilisée que dans initUI et que initUI est appelée
    # une unique fois (enfin en principe), on peut la définir DANS initUI pour
    # faire plus joli sans que ça soit trop coûteux.
    def showDialog(self):

        # We pop up the QFileDialog. The first string in the getOpenFileName()
        # method is the caption. The second string specifies the dialog working
        # directory. We use the path module to determine the user's home
        # directory. By default, the file filter is set to All files (*).
        home_dir = str(Path.home())
        fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir)

        if fname[0]:
            with open(fname[0], 'r') as f:
                data = f.read()
                self.textEdit.setText(data)

def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
