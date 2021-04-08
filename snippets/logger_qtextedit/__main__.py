"""
Display a logger (logging module) in a QTextEdit.
Shamelessly copied from
https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
"""

import datetime
import logging
import sys

from PySide2.QtGui     import   QFontDatabase
from PySide2.QtWidgets import ( QApplication,
                                QPushButton,
                                QTextEdit,
                                QVBoxLayout,
                                QWidget )


class LoggerTextEdit(logging.Handler, QTextEdit):
    # Multiple inheritance yay

    def __init__(self, log_format: str):

        logging.Handler.__init__(self)
        QTextEdit.__init__(self)

        self.setFormatter(logging.Formatter(log_format))
        self.setReadOnly(True)
        self.setMinimumHeight(400)
        self.setMinimumWidth(600)
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.setFont(font)

    # This overloads logging.Handler.emit method
    def emit(self, record):
        msg = self.format(record)
        self.append(msg)


class MyWidget(QWidget):

    def __init__(self):

        super().__init__()

        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        lte = LoggerTextEdit(log_format)
        logging.getLogger().addHandler(lte)

        btn = QPushButton('Test logger printing')
        btn.clicked.connect(self.log_time)

        lyt = QVBoxLayout()
        lyt.addWidget(lte)
        lyt.addWidget(btn)

        self.setLayout(lyt)

    def log_time(self):
        now = datetime.datetime.now()
        logging.warning(f'Current time: {str(now)}')


if __name__ == '__main__':
    app = QApplication()

    mw = MyWidget()
    mw.show()

    sys.exit(app.exec_())
