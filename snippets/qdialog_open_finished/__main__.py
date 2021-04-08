import sys

from PySide2.QtCore    import ( Signal,
                                Slot )
from PySide2.QtWidgets import ( QApplication,
                                QDialog,
                                QLabel,
                                QLineEdit,
                                QMainWindow,
                                QPushButton,
                                QVBoxLayout )


class MyDialog(QDialog):

    text_chosen = Signal(str)

    def __init__(self):

        super().__init__()
        self.setModal(True)

        self.__editor = QLineEdit()
        self.__btn = QPushButton('Send text')
        self.__btn.clicked.connect(self.__btn_clicked)

        mlyt = QVBoxLayout()
        mlyt.addWidget(QLabel('My dialog'))
        mlyt.addWidget(self.__editor)
        mlyt.addWidget(self.__btn)
        self.setLayout(mlyt)

    @Slot()
    def __btn_clicked(self):

        text = self.__editor.text()
        self.text_chosen.emit(text)

        super().accept()


class MyMainWindow(QMainWindow):

    def __init__(self):

        self.my_dialog = MyDialog()
        self.my_dialog.text_chosen.connect(self.show_editor_result)
        self.my_dialog.open()

        self.label = QLabel()
        self.label.resize(200, 200)
        self.label.show()

        super().__init__()

    @Slot(str)
    def show_editor_result(self, text: str):
        self.label.setText(text)


if __name__ == '__main__':

    app = QApplication()
    my_main_window = MyMainWindow()
    sys.exit(app.exec_())
