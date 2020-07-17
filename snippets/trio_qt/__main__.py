"""
fml
credits to Florian
"""

from PySide2.QtWidgets  import (
    QWidget,
    QHBoxLayout,
    QTextEdit
)
from PySide2.QtCore     import Qt, Signal
from PySide2.QtGui      import QColor, QBrush, QIcon
from sys import exit

import trio
import qtrio

import deaduction.pylib.logger as logger

class MainWindow(QWidget):
    closed = Signal()

    def __init__( self, parent=None ):
        super().__init__( parent )

        self.setWindowTitle("Test lean")

        # Widgets
        self.w_layout = QHBoxLayout(self)
        self.w_edit   = QTextEdit  ("", parent=self)
        self.w_msgs   = QTextEdit  ("", parent=self)

        self.w_layout.addWidget(self.w_edit)
        self.w_layout.addWidget(self.w_msgs)

        # Layout validation
        self.setLayout(self.w_layout)

    def closeEvent(self, ev):
        super().closeEvent(ev)
        self.closed.emit()

async def main():
    logger.configure()
    win = MainWindow()

    async with qtrio.enter_emissions_channel(signals=[win.closed]) as emissions:
        win.show()
        await emissions.channel.receive()

if __name__=="__main__":
    qtrio.run(main)
