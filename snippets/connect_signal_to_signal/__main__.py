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

    signal_1 = Signal()
    signal_2 = Signal()
    signal_3 = Signal()

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

        self.show()

    @Slot()
    def print_datetime(self):
        now = datetime.now()
        self.lbl.setText(str(now))


if __name__ == '__main__':
    app = QApplication()
    my_widget = MyWidget()
    sys.exit(app.exec_())
