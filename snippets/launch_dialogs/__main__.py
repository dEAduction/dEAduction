import sys
from pathlib import             Path
from PySide2.QtCore import      Slot
from PySide2.QtWidgets import ( QApplication,
                                QGridLayout,
                                QGroupBox,
                                QFileDialog,
                                QPushButton,
                                QListWidget,
                                QWidget,
                                QLabel,
                                QListWidgetItem,
                                QVBoxLayout,
                                QHBoxLayout)


class CourseChooseAndPreview(QGroupBox):

    def __init__(self):

        super().__init__()
        self.setTitle('Choose course')

        # ─────────────── Widgets and layouts ────────────── #

        browse_btn = QPushButton('Browse files')
        browse_btn.clicked.connect(self.__browse_for_course)
        browse_btn_lyt = QVBoxLayout()
        browse_btn_lyt.addWidget(browse_btn)
        browse_btn_lyt.addStretch()

        previous_courses_wgt = QListWidget()
        previous_courses_wgt.itemClicked.connect(
                self.enable_choose_this_course_btn)
        previous_courses_wgt.addItem(QListWidgetItem('Test item'))

        choose_course_lyt = QHBoxLayout()
        choose_course_lyt.addWidget(previous_courses_wgt)
        choose_course_lyt.addLayout(browse_btn_lyt)

        course_meta_data = QGridLayout()
        course_meta_data.addWidget(QLabel('Adress:'),   0, 0)
        course_meta_data.addWidget(QLabel('Teacher:'),  1, 0)
        course_meta_data.addWidget(QLabel('Uni:'),      2, 0)
        course_meta_data.addWidget(QLabel('Year:'),     3, 0)

        # ─────────────────── Main layout ────────────────── #

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel('Choose a previous course or browse files'))
        main_layout.addLayout(choose_course_lyt)
        main_layout.addStretch()
        main_layout.addWidget(QLabel('<i>Selected course</i>'))
        main_layout.addLayout(course_meta_data)
        self.setLayout(main_layout)


    @Slot()
    def enable_choose_this_course_btn(self):

        self.choose_this_course_btn.setEnabled(True)

    @Slot()
    def __browse_for_course(self):

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('*.lean')

        if dialog.exec_():
            course_file_path = Path(dialog.selectedFiles()[0])


class ExerciseChooseAndPreview(QGroupBox):

    def __init__(self):

        super().__init__()
        self.setTitle('Choose exercise')


class ChooseCourseExercise(QWidget):

    def __init__(self):

        super().__init__()

        course_cap =   CourseChooseAndPreview()
        exercise_cap = ExerciseChooseAndPreview()
        selection_zone_lyt = QHBoxLayout()
        selection_zone_lyt.addWidget(course_cap)
        selection_zone_lyt.addWidget(exercise_cap)

        buttons_lyt = QHBoxLayout()
        help_btn = QPushButton('Get help')
        quit_btn = QPushButton('Quit')
        self.choose_this_course_btn = QPushButton('Launch exercise')
        buttons_lyt.addWidget(help_btn)
        buttons_lyt.addWidget(quit_btn)
        buttons_lyt.addStretch()
        buttons_lyt.addWidget(self.choose_this_course_btn)

        # ─────────────────── Main layout ────────────────── #
        
        main_lyt = QVBoxLayout()
        main_lyt.addLayout(selection_zone_lyt)
        main_lyt.addLayout(buttons_lyt)
        self.setLayout(main_lyt)

        # ─────────────────────── UI ─────────────────────── #

        self.setWindowTitle('d∃∀duction — Choose course and exercise')


if __name__ == '__main__':
    app = QApplication()

    blanquistes_du_nil = ChooseCourseExercise()
    blanquistes_du_nil.show()

    sys.exit(app.exec_())
