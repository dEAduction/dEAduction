"""
#########################################################
# read_pkl_course.py : Provide read_pkl_course function #
#########################################################

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
Date           : January 2021

Copyright (c) 2021 the dEAduction team

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

from pathlib import Path
import pickle

from deaduction.pylib.coursedata import Course


# TODO: Put this function somewhere else (course classmethod?)
def read_pkl_course(course_path: Path) -> Course:
    """
    Extract an instance of the class Course from a .pkl file.

    :param course_path: The path of the course we want to instanciate.
    :return: The instance of the Course class.
    """

    with course_path.open(mode='rb') as input:
        course = pickle.load(input)

    return course
