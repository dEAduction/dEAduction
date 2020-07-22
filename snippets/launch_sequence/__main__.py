import logging
from pathlib import Path
import sys

from PySide2.QtWidgets import QApplication, QFileDialog, QLabel
from PySide2.QtWidgets import QListWidget, QListWidgetItem, QWidget

import deaduction.pylib.logger as logger
from deaduction.pylib.coursedata.course import Course


log = logging.getLogger(__name__)

class SelectExercise(QWidget):

    def _init_list(self, exercises_list):
        self.exercises_list_widget = QListWidget
        for exercise in exercises_list:
            self.exercises_list_widget.addItem([exercise.pretty_name])

    def _init_caption(self):
        self.caption = QLabel(_('Please select an exercise.'))

    def __init__(self, exercises_list):
        super().__init__()
        self._init_list(exercises_list)
        self._init_caption()
        lyt = QVBoxLayout
        lyt.addWidget(self.caption)
        lyt.addWidget(self.exercises_list_widget)
        self.setLayout(lyt)


def select_course_dir() -> Path:
    course_file = Path(QFileDialog.getOpenFileName()[0])
    log.info(f'Selected course (from dialog): {str(course_file.resolve())}')

    return course_file


def launch_dEAduction():
    course_dir_path = select_course_dir()
    course = Course.from_directory(course_dir_path)
    exercises_list = course.extract_exercise()
    select_exercise = SelectExercise(exercises_list)
    select_exercise.show()


if __name__ == '__main__':
    logger.configure()

    app = QApplication([])
    course_dir_path = Path('../../tests/lean_files/short_course/')
    course = Course.from_directory(course_dir_path)
    # select_exercise = SelectExercise(course.extract_exercise())
    # select_exercise.show()

    sys.exit(app.exec_())
