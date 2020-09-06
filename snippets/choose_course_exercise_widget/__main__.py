import sys
from pathlib import Path
from typing import  OrderedDict

from PySide2.QtCore import      Slot
from PySide2.QtWidgets import ( QApplication,
                                QGridLayout,
                                QGroupBox,
                                QFileDialog,
                                QPushButton,
                                QTextEdit,
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

        # ──────────────────── Selection ─────────────────── #

        browse_btn = QPushButton('Browse files')
        browse_btn.clicked.connect(self.__browse_for_course)
        previous_courses_wgt = QListWidget()
        previous_courses_wgt.addItem(QListWidgetItem('Test item'))

        selection_lyt = QVBoxLayout()
        selection_lyt.setContentsMargins(0, 0, 0, 0)
        selection_lyt.addWidget(QLabel('Choose a previous course or browse'
                                       'files'))
        selection_lyt.addWidget(browse_btn)
        selection_lyt.addWidget(previous_courses_wgt)
        selection_wgt = QWidget()
        selection_wgt.setLayout(selection_lyt)

        # ───────────────────── Preview ──────────────────── #

        course_title_lyt = QHBoxLayout()
        course_title_lyt.addWidget(QLabel('<b>Topologie algébrique</b>'))

        course_meta_1_wgt = QLabel('<i>Yet another Sorbonne University — 2020-2021</i>')
        course_meta_2_wgt = QLabel('<i>Frédéric Le Roux')
        course_meta_1_lyt = QHBoxLayout()
        course_meta_1_lyt.addStretch()
        course_meta_1_lyt.addWidget(course_meta_1_wgt)
        course_meta_2_lyt = QHBoxLayout()
        course_meta_2_lyt.addStretch()
        course_meta_2_lyt.addWidget(course_meta_2_wgt)

        comment = "Lorem ipsum dolor sit amet, consectetur adipiscing elit." \
                'Mauris tempus congue turpis mollis consequat. Nulla finibus tempor' \
                'pharetra. Duis accumsan nisl tincidunt lacus aliquet, vel sodales nunc' \
                'blandit. Phasellus ligula tortor, venenatis in quam in, pretium' \
                'faucibus dolor. Morbi quis orci in mauris scelerisque ultricies at ut' \
                'augue. In et libero quis arcu tincidunt vestibulum. Etiam at odio eget' \
                'felis interdum tincidunt. Aenean neque metus, semper vitae metus vitae,' \
                'euismod dictum lectus. Pellentesque vel turpis metus. Phasellus sed' \
                'eros vel quam viverra sagittis. Class aptent taciti sociosqu ad litora' \
                'torquent per conubia nostra, per inceptos himenaeos. Aliquam bibendum' \
                'ipsum arcu, eu condimentum massa ultricies et. Fusce facilisis felis' \
                'dictum nunc placerat, ut malesuada lectus maximus. Nam dignissim orci' \
                'ipsum, id luctus mauris iaculis condimentum. Aliquam arcu eros, tempor' \
                'vitae vulputate eget, viverra quis metus.'

        course_comment = QTextEdit(comment)
        course_comment.setReadOnly(True)

        preview_lyt = QVBoxLayout()
        preview_lyt.setContentsMargins(0, 0, 0, 0)
        preview_lyt.addLayout(course_title_lyt)
        preview_lyt.addLayout(course_meta_1_lyt)
        preview_lyt.addLayout(course_meta_2_lyt)
        preview_lyt.addWidget(course_comment)
        preview_wgt = QWidget()
        preview_wgt.setLayout(preview_lyt)

        # ─────────────────── Main layout ────────────────── #

        main_layout = QHBoxLayout()
        main_layout.addWidget(selection_wgt)
        main_layout.addWidget(preview_wgt)
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

        main_layout = QHBoxLayout()
        main_layout.addWidget(QLabel('Exercises list'))
        main_layout.addWidget(exercises_list)
        main_layout.addWidget(exercise_preview_wgt)

        self.setLayout(main_layout)

class ChooseCourseExercise(QWidget):

    def __init__(self):

        super().__init__()

        course_cap =   CourseChooseAndPreview()
        exercise_cap = ExerciseChooseAndPreview()
        selection_zone_lyt = QVBoxLayout()
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
