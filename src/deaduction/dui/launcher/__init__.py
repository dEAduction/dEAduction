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

from gettext import gettext as  _
import logging
import pickle
from pathlib import Path
import sys
from PySide2.QtWidgets import                   (QApplication,
                                                QFileDialog,
                                                QInputDialog)

import deaduction.pylib.logger as               logger
from deaduction.dui.utils import                (ButtonsDialog)
from deaduction.config import                   (user_config,
                                                write_config)
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
        course_path_str = str(course_path.resolve())
        log.info(f'Selected course: {course_path_str}')

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

        # store course file name in config file
        add_recent_courses(course_path_str)
        user_config['last_course'] = course_path_str
        # fixme: the following line store the recent courses,
        #  but also all the tooltips...
        # write_config()

        return course
    else:
        return None


def select_exercise(course: Course):
    """
    Open a combo box to choose an exercise and launch the exercise 
    window.

    If needed, ask the user to choose between proving the statement and its
    negation.

    :param course: An instance of the Course class, user-selected in
        select_course.
    :return: An instance of the Exercise class corresponding to the
        user-selected exercise from course.
    """
    exercise_list = course.exercises_list()
    exercise_ids = {exercise.lean_name: exercise for exercise in exercise_list}

    exercise_id, ok = QInputDialog().getItem(None,
                                             _('Please select an exercise'),
                                             _('Selected exercise:'),
                                             list(exercise_ids.keys()), 0,
                                             False)
    if ok:
        exercise = exercise_ids[exercise_id]
        open_question = exercise.info.setdefault('open_question', False)
        if 'negate_statement' in exercise.info:
            if exercise.info['negate_statement']:
                exercise.negate_statement = True
        elif open_question:
            # exercise is an open question and the user has to choose her way
            title = _("Do you want to prove this statement or its negation?")
            if exercise.initial_proof_state:
                output = ""  # fixme
            else:
                output = ""
            choices = [("1", "Prove statement"),
                       ("2", "Prove negation")]
            choice, ok2 = ButtonsDialog.get_item(choices,
                                                 title,
                                                 output)
            log.debug(f"choice: {choice}")
            if ok2:
                exercise.negate_statement = (choice == 1)
                log.debug(f"negate: {exercise.negate_statement}")
            else:  # cancel exercise if no choice
                ok = False
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

    return course, exercise


def pickled_items(filename):
    """ Unpickle a file of pickled data. """
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


def add_recent_courses(course_path: str):
    """
    Add course_path to the list of recent courses in user_config
    NB: do not save this in config.ini; write_config() must be called for that
    """
    try:
        max = user_config['max_recent_courses']
    except KeyError:
        max = 5
    try:
        recent_courses = user_config['recent_courses']
    except KeyError:
        recent_courses = ""
    recent_courses_list = recent_courses.split(',')
    if course_path not in recent_courses_list:
        recent_courses_list.append(course_path)
    if len(recent_courses_list) > max:
        # remove oldest
        recent_courses_list.pop(0)
    recent_courses_string = ','.join(recent_courses_list)
    user_config['recent_courses'] = recent_courses_string
