"""
Good info on signals and slots:
    - https://wiki.qt.io/Qt_for_Python_Signals_and_Slots ;
    - https://doc.qt.io/qt-5/signalsandslots.html.
"""

from functools import partial
import logging
import sys
from PySide2.QtCore import (
        Signal,
        Slot,
        QObject)
from PySide2.QtWidgets import (
        QApplication,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QHBoxLayout,
        QVBoxLayout,
        QWidget)
import deaduction.pylib.logger as logger


class WetButton(QPushButton):

    def __init__(self, text):
        super().__init__(text)

    @Slot()
    def freeze(self):
        log.debug('WetButton received signal')
        self.setEnabled(False)

    @Slot()
    def unfreeze(self):
        log.debug('WetButton received signal')
        self.setEnabled(True)

class WetSand(QWidget):

    def _connect_signals_slots(self):
        # Freeze interface
        for btn in self.btns:
            self.freeze_btn.clicked.connect(btn.freeze)

        # Unfreeze interface
        for btn in self.btns:
            self.unfreeze_btn.clicked.connect(btn.unfreeze)

    def __init__(self):
        super().__init__()

        # Init list
        self.list = QListWidget()
        self.list.addItem(QListWidgetItem("You don't form in the wet sand"))
        self.list.addItem(QListWidgetItem("You don't form at all"))

        # Init buttons
        self.btns = [WetButton('johs'),
                WetButton('jon'),
                WetButton('feel'),
                WetButton('chat'),
                WetButton('tony')]

        # Freeze and unfreeze buttons
        self.freeze_btn =    QPushButton('Freeze me')
        self.unfreeze_btn =  QPushButton('Unfreeze me')

        # Layout stuff
        self.btn_lyt = QVBoxLayout()
        for btn in self.btns:
            self.btn_lyt.addWidget(btn)

        self.top_lyt = QHBoxLayout()
        self.top_lyt.addWidget(self.list)
        self.top_lyt.addLayout(self.btn_lyt)

        self.bottom_lyt = QHBoxLayout()
        self.bottom_lyt.addWidget(self.freeze_btn)
        self.bottom_lyt.addWidget(self.unfreeze_btn)

        self.main_lyt = QVBoxLayout()
        self.main_lyt.addLayout(self.top_lyt)
        self.main_lyt.addLayout(self.bottom_lyt)

        # Signals and slots
        self._connect_signals_slots()

        # Don't forget me
        self.setLayout(self.main_lyt)
        self.show()


if __name__ == '__main__':
    logger.configure()
    log = logging.getLogger(__name__)

    app = QApplication([])

    youdontformatall = WetSand()

    sys.exit(app.exec_())
