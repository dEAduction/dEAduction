"""
# choose_coex_for test.py : methods for selecting course and exercise #



Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 04 2021 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the d∃∀duction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    d∃∀duction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
from sys import version_info
if version_info[1] < 8:
    import pickle5 as pickle
else:
    import pickle

from pathlib import Path
from typing import Any

from PySide2.QtWidgets import QFileDialog
from deaduction.pylib.coursedata import (Course,
                                         Exercise)

log = logging.getLogger(__name__)


def pickled_items(filename):
    """ Unpickle a file of pickled data. """
    with filename.open(mode="rb") as input:
        while True:
            try:
                yield pickle.load(input)
            except EOFError:
                break


def select_course(course_path: Any = None) -> Course:
    """
    Select a course from a Path, a path string, or by opening a QFileDialog.
    :param course_path: a Path, a string, or None.
    :return: a instance of Course.
    """

    course = None
    if not course_path:
        course_path, ok = QFileDialog.getOpenFileName()
        if not ok:
            quit()
    if isinstance(course_path, str):
        if not course_path.endswith('.lean') \
        and not course_path.endswith('.pkl'):
            course_path += '.lean'
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
    else:
        log.error("Wrong file format")

    return course


def select_exercise(course_like: Any, exercise_like: any) -> (Course,
                                                              Exercise):
    """

    :param course_like: either a Course, a Path, a string.
    :param exercise_like: either a number, a name, or None.
    :return: an instance of Exercise.
    """

    exercise = None
    if not isinstance(course_like, Course):
        course = select_course(course_like)
    else:
        course = course_like

    if isinstance(exercise_like, int):
        exercise_nb = exercise_like
        exercise = course.exercises[exercise_nb]
    elif isinstance(exercise_like, str):
        name = exercise_like
        exercise = course.statement_from_name(name)

    return course, exercise

