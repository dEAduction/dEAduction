"""
Your First QtWidgets Application
https://doc.qt.io/qtforpython/tutorials/basictutorial/widgets.html
"""

import sys
from PySide2.QtWidgets import QApplication, QLabel

app = QApplication([])
label = QLabel("<font color=red size=40>Hello World!</font>")
label.show()
app.exec_()
