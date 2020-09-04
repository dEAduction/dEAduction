import sys
from pathlib import Path
from typing import  OrderedDict

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


class CourseExercisePreview(QWidget):

    def __init__(self, title: str, metadata: OrderedDict[str, str]):
        super().__init__()

        grid_layout = QGridLayout()

        for label, val in metadata.items():
            row = grid_layout.rowCount()
            grid_layout.addWidget(QLabel(f'{label}:'), row, 0)
            grid_layout.addWidget(QLabel(val),         row, 1)

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel(f'<i>{title}</i>'))
        main_layout.addLayout(grid_layout)

        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(main_layout)



class CourseChooseAndPreview(QGroupBox):

    def __init__(self):

        super().__init__()
        self.setTitle('Choose course')

        # ─────────────── Widgets and layouts ────────────── #

        browse_btn = QPushButton('Browse files')
        browse_btn.clicked.connect(self.__browse_for_course)
        previous_courses_wgt = QListWidget()
        previous_courses_wgt.addItem(QListWidgetItem('Test item'))
        choose_course_lyt = QVBoxLayout()
        choose_course_lyt.addWidget(QLabel('Choose a previous course or browse files'))
        choose_course_lyt.addWidget(browse_btn)
        choose_course_lyt.addWidget(previous_courses_wgt)

        metadata = {'Adress': '', 'Teacher': '', 'School': '', 'Year': ''}
        course_meta_data = CourseExercisePreview('Selected course', metadata)

        # ─────────────────── Main layout ────────────────── #

        main_layout = QVBoxLayout()
        main_layout.addLayout(choose_course_lyt)
        main_layout.addStretch()
        main_layout.addWidget(course_meta_data)
        self.setLayout(main_layout)


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

        exercises_list = QListWidget()
        exercises_list.addItem(QListWidgetItem(
            "L'image réciproque d'un ouvert est un ouvert"))

        metadata = {'Name': '', 'Instructions': '', 'Comments': '', 'L∃∀N code': ''}
        exercise_preview_wgt = CourseExercisePreview('Selected exercise', metadata)

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(QLabel('Exercises list'))
        main_lyt.addWidget(exercises_list)
        main_lyt.addStretch()
        main_lyt.addWidget(exercise_preview_wgt)

        self.setLayout(main_lyt)

class ChooseCourseExercise(QWidget):

    def __init__(self):

        super().__init__()

        course_cap =   CourseChooseAndPreview()
        exercise_cap = ExerciseChooseAndPreview()
        selection_zone_lyt = QHBoxLayout()
        selection_zone_lyt.setContentsMargins(0, 0, 0, 0)
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
