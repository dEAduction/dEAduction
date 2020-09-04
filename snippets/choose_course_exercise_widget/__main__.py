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

        # Result with a grid layout is better than with a pile of
        # horizontal layouts
        grid_layout = QGridLayout()

        for label, val in metadata.items():
            row = grid_layout.rowCount()
            grid_layout.addWidget(QLabel(f'{label}:'), row, 0)
            grid_layout.addWidget(QLabel(val),         row, 1)

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel(f'<i>{title}</i>'))
        main_layout.addLayout(grid_layout)

        # Default is 11 px in all directions
        main_layout.setContentsMargins(0, 17, 0, 0)
        
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

        metadata = {'Course name': 'Topologie algébrique',
                    'Teacher':     'Professeur Le Roux',
                    'School':      'Yet another Sorbonne',
                    'Year':        '2020-2021',
                    'Adress':      '~/Truc/Machin/Bidule/topalg.lean'}
        course_meta_data = CourseExercisePreview('Selected course', metadata)

        # ─────────────────── Main layout ────────────────── #

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel('Choose a previous course or browse files'))
        main_layout.addWidget(browse_btn)
        main_layout.addWidget(previous_courses_wgt)
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

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel('Exercises list'))
        main_layout.addWidget(exercises_list)
        main_layout.addWidget(exercise_preview_wgt)

        self.setLayout(main_layout)

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
