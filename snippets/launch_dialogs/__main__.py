import sys
from pathlib import             Path
from PySide2.QtCore import      Slot
from PySide2.QtWidgets import ( QApplication,
                                QFileDialog,
                                QPushButton,
                                QListWidget,
                                QWidget,
                                QLabel,
                                QListWidgetItem,
                                QVBoxLayout,
                                QHBoxLayout)


@Slot()
def browse_for_course():

    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.ExistingFile)
    dialog.setNameFilter('*.lean')

    if dialog.exec_():
        course_file_path = Path(dialog.selectedFiles()[0])


class CourseChooser(QWidget):

    def __init__(self):
        super().__init__()

        # ─────────────── Widgets and layouts ────────────── #
        
        browse_btn = QPushButton('Browse files')
        browse_btn.clicked.connect(browse_for_course)
        browse_btn_lyt = QHBoxLayout()
        browse_btn_lyt.addWidget(browse_btn)
        browse_btn_lyt.addStretch()

        previous_courses_lyt = QVBoxLayout()
        previous_courses_list_wgt = QListWidget()
        previous_courses_list_wgt.itemClicked.connect(
                self.enable_choose_this_course_btn)
        previous_courses_list_wgt.addItem(QListWidgetItem('Test item'))
        previous_courses_lyt.addWidget(QLabel('Or choose a previous course'))
        previous_courses_lyt.addWidget(previous_courses_list_wgt)

        buttons_lyt = QHBoxLayout()
        help_btn = QPushButton('Get help')
        quit_btn = QPushButton('Quit')
        self.choose_this_course_btn = QPushButton('Choose this course')
        self.choose_this_course_btn.setEnabled(False)
        buttons_lyt.addWidget(help_btn)
        buttons_lyt.addWidget(quit_btn)
        buttons_lyt.addStretch()
        buttons_lyt.addWidget(self.choose_this_course_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(browse_btn_lyt)
        main_layout.addLayout(previous_courses_lyt)
        main_layout.addStretch()
        main_layout.addLayout(buttons_lyt)
        self.setLayout(main_layout)

        # ─────────────────────── UI ─────────────────────── #

        self.setWindowTitle('Choose a course file')

    @Slot()
    def enable_choose_this_course_btn(self):

        self.choose_this_course_btn.setEnabled(True)
        


if __name__ == '__main__':
    app = QApplication()

    cc = CourseChooser()
    cc.show()

    sys.exit(app.exec_())
