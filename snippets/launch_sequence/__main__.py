from gettext import gettext as _
import logging
from pathlib import Path
import sys

from PySide2.QtWidgets import QApplication, QFileDialog, QInputDialog

import deaduction.pylib.logger as logger
from deaduction.pylib.coursedata.course import Course

log = logging.getLogger(__name__)


def select_course():
    """
    Open a file dialog to choose a course lean file.

    :return: An instance of the Course class corresponding to the 
        user-selected course.
    """

    course_path = Path(QFileDialog.getOpenFileName()[0])
    log.info(f'Selected course (from dialog): {str(course_path.resolve())}')
    course = Course.from_file(course_path)

    return course


def select_exercise(course: Course):
    """
    Open a combo box to choose an exercise and launch the exercise 
    window.

    :param course: An instance of the Course class, user-selected in
        select_course.
    :return: An instance of the Exercise class corresponding to the
        user-selected exercise from course.
    """

    exercises_list = course.exercises
    exercise_from_id = {ex.pretty_name: ex for ex in exercises_list}

    # See the example in the link below for the syntax:
    # https://doc.qt.io/qtforpython/PySide2/QtWidgets/QInputDialog.html#
    # PySide2.QtWidgets.PySide2.QtWidgets.QInputDialog.getItem
    ex_name, ok = QInputDialog().getItem(None, 'Please select an exercise',
            'Selected exercise:', list(exercise_from_id.keys()), 0, False)

    if ok:  # Ok is pressed
        # TODO: launch exercise
        pass
    else:   # Cancel is pressed, chose another course
        select_course()

def select_course_and_exercise():
    """
    Open a file dialog to chose a course, then a dialog to chose an 
    exercise from this course and launch it.
    """

    course = select_course()
    select_exercise(course)


if __name__ == '__main__':
    logger.configure()
    app = QApplication([])

    select_course_and_exercise()

    sys.exit(app.exec_())
