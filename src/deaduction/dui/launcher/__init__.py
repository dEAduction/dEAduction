"""
##################
# __init__.py :  #
##################

Author(s)      : - Kryzar <antoine@hugounet.com>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : - Kryzar <antoine@hugounet.com>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : July 2020

Copyright (c) 2020 the dEAduction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    d∃∀duction is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with d∃∀duction. If not, see <https://www.gnu.org/licenses/>.
"""

from gettext import             gettext as  _
import                          logging
import                          pickle
from pathlib import             Path
import sys
from PySide2.QtWidgets import ( QApplication,
                                QFileDialog,
                                QInputDialog)

import deaduction.pylib.logger as               logger
from deaduction.pylib.coursedata.course import (Exercise,
                                                Course)

log = logging.getLogger(__name__)

def select_course():
    """
    Open a file dialog to choose a course lean file.

    :return: TODO
    """

    course_path, ok = QFileDialog.getOpenFileName()

    if ok:
        course_path = Path(course_path)
        log.info(f'Selected course: {str(course_path.resolve())}')
        extension = course_path.suffix
        # case of a standard Lean file
        if extension == '.lean':
            course = Course.from_file(course_path)
        # case of a pre-processed .pkl file
        elif extension == '.pkl':
            [course] = pickled_items(course_path)
            # h = hash function of file_content
            # TODO: compare file_content with Lean file, and raise a warning
            # if different (or if no Lean file)
        else:
            log.error("Wrong file format")
        return course
    else:
        return None


def select_exercise(course: Course):
    """
    Open a combo box to choose an exercise and launch the exercise 
    window.

    :param course: An instance of the Course class, user-selected in
        select_course.
    :return: An instance of the Exercise class corresponding to the
        user-selected exercise from course.
    """
    exercise_list = course.exercises_list()
    exercise_ids = {exercise.lean_name: exercise for exercise in exercise_list}

    exercise_id, ok = QInputDialog().getItem(None,
            _('Please select an exercise'), _( 'Selected exercise:'),
            list(exercise_ids.keys()), 0, False)

    return exercise_ids[exercise_id] if ok else None


def select_course_exercise():
    """
    Open a file dialog to chose a course, then a dialog to chose an 
    exercise from this course and launch it.
    """

    course = None
    exercise = None

    while exercise is None:
        course = select_course()

        if course is None:
            break

        exercise = select_exercise(course)

    return (course, exercise)


def pickled_items(filename):
    """ Unpickle a file of pickled data. """
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break
