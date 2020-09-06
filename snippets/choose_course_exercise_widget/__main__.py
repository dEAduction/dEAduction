import sys
from pathlib import Path
from typing import  OrderedDict, List

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
                                QLayout,
                                QListWidgetItem,
                                QVBoxLayout,
                                QHBoxLayout)


class ChoosePreviewCourseExerciseLayout(QHBoxLayout):

    def __init__(self, choose_title:  str, choose_lyt:  QLayout,
                       preview_title: str, preview_lyt: QLayout):

        super().__init__()

        choose_gb = QGroupBox(choose_title)
        choose_gb.setLayout(choose_lyt)
        
        preview_gb = QGroupBox(preview_title)
        preview_gb.setLayout(preview_lyt)

        self.setContentsMargins(0, 0, 0, 0)
        self.addWidget(choose_gb)
        self.addWidget(preview_gb)


class CourseExerciseTitle(QLabel):

    def __init__(self, text: str):

        super().__init__(text)
        self.setStyleSheet('font-size: 20pt;')


class MetainfoBloc(QWidget):

    def __init__(self, list_info: List[str]):

        super().__init__()

        main_layout = QVBoxLayout()

        for info in list_info:
            layout = QHBoxLayout()
            layout.addStretch()
            label = QLabel(info)
            label.setStyleSheet('font-style: italic;')
            layout.addWidget(label)
            main_layout.addLayout(layout)

        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)


class CourseChoosePreview(QWidget):

    def __init__(self):

        super().__init__()

        # ────────────── Choose course layout ────────────── #

        browse_btn = QPushButton('Browse files')
        browse_btn.clicked.connect(self.__browse_for_course)
        previous_courses_wgt = QListWidget()

        choose_course_lyt = QVBoxLayout()
        choose_course_lyt.addWidget(browse_btn)
        choose_course_lyt.addWidget(previous_courses_wgt)

        # ────────────── Preview course layout ───────────── #

        course_title_lyt = QHBoxLayout()
        course_title_lyt.addWidget(CourseExerciseTitle('Topologie algébrique'))

        course_metainfo_list = ['Yet another Sorbonne University, 2020-2021',
                                 'Frédéric Le Roux']
        course_metainfo_bloc = MetainfoBloc(course_metainfo_list)

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

        preview_course_lyt = QVBoxLayout()
        preview_course_lyt.addLayout(course_title_lyt)
        preview_course_lyt.addWidget(course_metainfo_bloc)
        preview_course_lyt.addWidget(course_comment)

        # ─────────────────── Main layout ────────────────── #

        main_layout = ChoosePreviewCourseExerciseLayout(
                'Choose course (browse files or previous course)',
                choose_course_lyt,
                'Preview course',
                preview_course_lyt)
        self.setLayout(main_layout)


    @Slot()
    def __browse_for_course(self):

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('*.lean')

        if dialog.exec_():
            course_file_path = Path(dialog.selectedFiles()[0])


class ExerciseChoosePreview(QWidget):

    def __init__(self):

        super().__init__()

        # ───────────────── Choose exercise ──────────────── #

        exercises_list = QListWidget()
        choose_exercise_lyt = QVBoxLayout()
        choose_exercise_lyt.addWidget(exercises_list)

        # ──────────────── Preview Exercise ──────────────── #

        preview_exercise_lyt = QVBoxLayout()

        # ─────────────────── Main layout ────────────────── #

        main_layout = ChoosePreviewCourseExerciseLayout(
                'Choose exercise (from the list)',
                choose_exercise_lyt,
                'Preview exercise',
                preview_exercise_lyt)
        self.setLayout(main_layout)

class ChooseCourseExercise(QWidget):

    def __init__(self):

        super().__init__()

        course_cap =   CourseChoosePreview()
        exercise_cap = ExerciseChoosePreview()
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
