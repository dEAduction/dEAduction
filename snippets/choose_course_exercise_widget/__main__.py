import sys
from pathlib import Path
from typing import  OrderedDict, List

from PySide2.QtCore import      Slot
from PySide2.QtGui  import      QPixmap
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


class InfoBloc(QWidget):

    def __init__(self, list_info: List[str]):

        super().__init__()

        main_layout = QVBoxLayout()

        for info in list_info:
            layout = QHBoxLayout()
            layout.addStretch()
            label = QLabel(info)
            label.setStyleSheet('font-style: italic;' \
                                'color: gray;')
            layout.addWidget(label)
            main_layout.addLayout(layout)

        main_layout.setSpacing(0)
        self.setLayout(main_layout)


class CourseExercisePreviewLayout(QVBoxLayout):

    def __init__(self, title: str, info_list: List[str], long_text: str):
        super().__init__()

        # Title
        title_wgt = QLabel(title)
        title_wgt.setStyleSheet('font-size: 20pt;')
        self.addWidget(title_wgt)

        # Info bloc
        self.addWidget(InfoBloc(info_list))

        # Long text
        long_text_wgt = QTextEdit(long_text)
        long_text_wgt.setReadOnly(True)
        self.addWidget(long_text_wgt)


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

        title = 'Topologie algébrique'
        info_list = ['Yet another Sorbonne University, 2020-2021',
                     'Frédéric Le Roux',
                     '~/Ka/Mou/Lox/Prof_le_Roux/topalg.lean']
        long_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit." \
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

        preview_course_lyt = CourseExercisePreviewLayout(title, info_list,
                long_text)

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

        title = 'Le groupe fondamental de la sphère est trivial'
        info_list = ['Some info']
        long_text = "Montrer que le groupe fondamental du cercle est "\
                    "isomorphe (comme groupe) à (Z, +)."

        preview_exercise_lyt = CourseExercisePreviewLayout(title, info_list,
                long_text)

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
        help_btn = QPushButton('Help')
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
