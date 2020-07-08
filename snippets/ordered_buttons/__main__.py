

import buttons_config

import sys
from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QHBoxLayout
)

KEYS = ["implies","NO","OR","exists"] # Test keys to play with

class Main_Window(QWidget):
    def __init__( self, keys, parent=None ):
        super().__init__( parent )
        self.setWindowTitle("Showing off buttons")

        self.layout = QHBoxLayout(self)
        for btn in buttons_config.build_from_config(
                keys, buttons_config.LOGIC_BUTTONS,
                parent=self
        ):
            self.layout.addWidget(btn)

        self.setLayout(self.layout)

if __name__=="__main__":
    app = QApplication(sys.argv)

    win = Main_Window(KEYS)
    win.show()

    sys.exit(app.exec_())
