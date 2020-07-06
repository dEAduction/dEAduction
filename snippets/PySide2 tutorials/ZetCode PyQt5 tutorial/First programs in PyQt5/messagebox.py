#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

This program shows a confirmation
message box when we click on the close
button of the application window.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PySide2.QtWidgets import QWidget, QMessageBox, QApplication

class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle("Message box")
        self.show()

    # closeEvent est une méthode de la classe parente QWidget
    # et est appelée lorsque l'on essaie de fermer le QWidget courrant.
    # C'est pour cela qu'il suffit de la déclarer et qu'il n'y a pas 
    # besoin de l'appeler dans le programme. On remarquera par ailleurs
    # que cela ne marche plus si l'on change le nom de closeEvent.
    # https://doc.qt.io/qt-5/qcloseevent.html#QCloseEvent

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Message",
                                    "Are you sure to quit?", 
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No) # la réponse par défaut

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
