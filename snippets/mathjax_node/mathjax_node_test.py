import sys
import json

from PySide2.QtWidgets import QWidget, QLineEdit, QMainWindow, QVBoxLayout, \
    QApplication
from PySide2.QtSvg import QSvgWidget

import requests


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        """The main window containing everything."""
        super().__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.resize(800, 600)

        self.setWindowTitle("Mathjax Qt test")

        self.input_widget = QLineEdit(self)
        self.input_widget.setPlaceholderText("Enter math here and press enter")
        self.input_widget.returnPressed.connect(self.input_widget_validate)

        self.svg = QSvgWidget()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.input_widget)
        layout.addWidget(self.svg)

    def input_widget_validate(self):
        math = self.input_widget.text()

        data = { "format": "TeX", "math": math, "svg": True }
        r = requests.post('http://localhost:8003', data=json.dumps(data))
        self.svg.load(r.content)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
