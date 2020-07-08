"""
A Simple Button Tutorial
https://doc.qt.io/qtforpython/tutorials/basictutorial/clickablebutton.html
main.py

In this tutorial, we’ll show you how to handle signals and slots using Qt for
Python. Signals and slots is a Qt feature that lets your graphical widgets
communicate with other graphical widgets or your python code. Our application
creates a button that logs the Button clicked, Hello! message to the python
console each time you click it.
"""
import sys
from PySide2.QtWidgets  import QApplication, QPushButton
from PySide2.QtCore     import Slot

# The @Slot() is a decorator that identifies a function as a slot. It is not
# important to understand why for now, but use it always to avoid unexpected
# behavior.
@Slot()
def say_hello():
    print("Button clicked, hello!")

# Create the Qt Application
app = QApplication(sys.argv)

# Create a button
button = QPushButton("Click me")

# Before we show the button, we must connect it to the say_hello() function that
# we defined earlier. There are two ways of doing this; using the old style or
# the new style, which is more pythonic. Let’s use the new style in this case.
# You can find more information about both these styles in the Signals and Slots
# in PySide2 wiki page.
button.clicked.connect(say_hello)

button.show()
app.exec_()
