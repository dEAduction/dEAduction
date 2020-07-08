"""
Data Visualization Tool Tutorial / Chapter 3 - Create an empty QMainWindow
In this tutorial, you’ll learn about the data visualization capabilities of Qt
for Python. To start with, find some open data to visualize. For example, data
about the magnitude of earthquakes during the last hour published on the US
Geological Survey website. You could download the All earthquakes open data in a
CSV format for this tutorial.
https://doc.qt.io/qtforpython/tutorials/datavisualize/add_mainwindow.html

MainWindow.py
"""

from PySide2.QtCore import Slot, qApp
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMainWindow, QAction

class MainWindow(QMainWindow):
    def __init__(self): 
        QMainWindow.__init__(self)
        self.setWindowTitle("Earthquakes information")

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        self.file_menu.addActin(exit_action)

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Data loaded and plotted")

        # Window dimensions
        geometry = qApp.desktop().availableGeometry(self)
        self.setFixedSize(geometry.width * 0.8, geometry.height() * 0.7)
