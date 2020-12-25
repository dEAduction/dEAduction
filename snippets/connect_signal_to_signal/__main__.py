from datetime import datetime
import sys

from PySide2.QtCore   import  ( Signal,
                                Slot )
from PySide2.QtWidgets import ( QApplication,
                                QWidget,
                                QPushButton,
                                QVBoxLayout,
                                QLabel )

# Tests for connecting signals directly to signals instead of slots.


class BabyClass(QWidget):

    baby_signal = Signal()

    def __init__(self):

        super().__init__()


class MyWidget(QWidget):

    # Snake
    signal_1 = Signal()
    signal_2 = Signal()
    signal_3 = Signal()

    # Emit no argument but should receive argument
    signal_4 = Signal()
    signal_5 = Signal(int)
    # Emit argument but should not receive one
    signal_6 = Signal(str)
    signal_7 = Signal()

    def __init__(self):

        super().__init__()

        self.btn = QPushButton('Print datetime')
        self.lbl = QLabel()
        self.bbc = BabyClass()

        lyt = QVBoxLayout()
        lyt.addWidget(self.btn)
        lyt.addWidget(self.lbl)
        self.setLayout(lyt)

        self.btn.clicked.connect(self.signal_1)
        self.signal_1.connect(self.signal_2)
        self.signal_2.connect(self.bbc.baby_signal)
        self.bbc.baby_signal.connect(self.signal_3)
        self.signal_3.connect(self.print_datetime)

        # Everything worked until there, but the following connections
        # fail:

        self.signal_4.connect(self.signal_5)
        self.signal_6.connect(self.signal_7)

        self.show()

    @Slot()
    def print_datetime(self):
        now = datetime.now()
        self.lbl.setText(str(now))


if __name__ == '__main__':
    app = QApplication()
    my_widget = MyWidget()
    sys.exit(app.exec_())
