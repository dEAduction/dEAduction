"""
Mathjax d'Amsterdam, go Cruijff.
"""

from PySide2.QtWidgets  import QApplication, QWidget, QListWidget, QListWidgetItem
from PySide2.QtWidgets  import QHBoxLayout
from PySide2.QtCore import QUrl 
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
import pathlib
import sys


def main():
    app = QApplication(sys.argv)

    # Web widget
    mathjax_webview = QWebEngineView()
    relative_path = pathlib.Path('mathjax_test.html')
    absolute_path = relative_path.resolve()
    url = QUrl.fromLocalFile(str(absolute_path))
    mathjax_webview.load(url)

    # List widget
    list_widget = QListWidget()
    list_widget.addItem(QListWidgetItem('list item'))
    list_widget.setAlternatingRowColors(True)

    # Don't forget me
    main_window = QWidget()
    main_window.setWindowTitle("Mathjax d'Amsterdam, go Cruijff.")
    main_layout = QHBoxLayout()
    main_layout.addWidget(mathjax_webview)
    main_layout.addWidget(list_widget)
    main_window.setLayout(main_layout)
    main_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
