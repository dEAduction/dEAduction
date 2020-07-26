import sys
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, \
        QPushButton


class Workshop(QWidget):

    def __init__(self):
        super().__init__()
        self.n = 0
        self.btn = QPushButton('Push me')
        self.lbl = QLabel(str(self.n))

        self.main_layout = QVBoxLayout()
        self.sub_layout = QVBoxLayout()
        self.sub_layout.addWidget(self.lbl)
        self.sub_layout.addWidget(self.btn)
        self.main_layout.addLayout(self.sub_layout)

        self.btn.clicked.connect(self.change_label)
        self.setLayout(self.main_layout)
        self.show()

    def replace_label(self, old_label, new_label):
        """
        Replace old_label by new_label in self.main_layout and its
        sub layouts. Do NOT set old_label to be new_label, the change
        is only in self.main_layout!

        You may see on [my post](https://stackoverflow.com/questions/
        63094202/qlayout-replace-not-replacing/63094407#63094407) that
        self.main_layout.replaceWidget(old_label, new_label) does not
        do the job. We need to also use old_label.deleteLater(). By 
        the way, it is written on the C++ documentation but NOT the 
        Python one that:
        > The parent of widget from is left unchanged.
        This is idiotic. I hate it, and I am currently listening to 
        Banco del Mutuo Soccorso so I should instead be happy. Fuck
        that. Also, fuck Trump.

        :param old_label: Label to be replaced and deleted.
        :param new_label: Label to replace old_label.
        """
        
        self.main_layout.replaceWidget(old_label, new_label)
        old_label.deleteLater()

    @Slot()
    def change_label(self):
        new_label = QLabel(str(self.n + 1))
        self.replace_label(self.lbl, new_label)
        self.n += 1
        self.lbl = new_label

    @Slot()
    def change_label_USELESS(self):
        """
        By using this fuction around line 21 in:
        self.btn.clicked.connect(self.change_label_useless)
        we see that simply setting self.lbl = new_label does not
        change it in the interface.
        """

        new_label = QLabel(str(self.n + 1))
        self.n += 1
        self.lbl = new_label


if __name__ == '__main__':
    app = QApplication()

    w = Workshop()

    sys.exit(app.exec_())
