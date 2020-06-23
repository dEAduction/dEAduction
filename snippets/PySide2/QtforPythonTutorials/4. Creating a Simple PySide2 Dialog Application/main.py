"""
Creating a Simple PySide2 Dialog Application
https://doc.qt.io/qtforpython/tutorials/basictutorial/dialog.html#create-the-widgets
main.py

This tutorial shows how to build a simple dialog with some basic widgets. The
idea is to let users provide their name in a QLineEdit, and the dialog greets
them on click of a QPushButton.
"""

import sys
from PySide2.QtWidgets import QApplication, QDialog, QLineEdit
from PySide2.QtWidgets import QPushButton, QVBoxLayout

class Form(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("My Form")

        # create widgets We are going to create two widgets: a QLineEdit where
        # users can enter their name, and a QPushButton that prints the contents
        # of the QLineEdit. So, let’s add the following code to the init()
        # method of our Form:
        self.edit =     QLineEdit("Write my name here…")
        self.button =   QPushButton("Show Greetings")

        # create layout and add widgets Qt comes with layout-support that helps
        # you organize the widgets in your application. In this case, let’s use
        # QVBoxLayout to lay out the widgets vertically. Add the following code
        # to the init() method, after creating the widgets:
        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        # set dialog layout
        self.setLayout(layout)
        # Add button signal to greetings slot
        self.button.clicked.connect(self.greetings)

    def greetings(self):
        print("Hello %s" % format(self.edit.text()))

if __name__ == '__main__':
    app = QApplication([])
    form = Form()
    form.show()
    sys.exit(app.exec_())
