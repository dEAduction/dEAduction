import sys
from PySide2.QtCore import Slot
from PySide2.QtWidgets import (
        QApplication,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QHBoxLayout,
        QVBoxLayout,
        QWidget)


class WetSand(QWidget):

    def __init__(self):
        super().__init__()

        # Init list
        self.list = QListWidget()
        self.list.addItem(QListWidgetItem("You don't form in the wet sand"))
        self.list.addItem(QListWidgetItem("You don't form at all"))

        # Init buttons
        self.johs =  QPushButton('johs')
        self.jon =   QPushButton('jon')
        self.feel =  QPushButton('feel')
        self.chat =  QPushButton('chat')
        self.tony =  QPushButton('tony')

        # Freeze and unfreeze buttons
        self.freeze_btn =    QPushButton('Freeze me')
        self.unfreeze_btn =  QPushButton('Unfreeze me')

        # Layout stuff
        self.btn_lyt = QVBoxLayout()
        for btn in [self.johs, self.jon, self.feel, self.chat, self.tony]:
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

        # Connect actions to buttons
        self.freeze_btn.clicked.connect(self.freeze)
        self.unfreeze_btn.clicked.connect(self.unfreeze)

        # Don't forget me
        self.setLayout(self.main_lyt)
        self.show()

    @Slot()
    def freeze(self):
        pass

    @Slot()
    def unfreeze(self):
        pass


if __name__ == '__main__':
    app = QApplication([])

    youdontformatall = WetSand()

    sys.exit(app.exec_())
