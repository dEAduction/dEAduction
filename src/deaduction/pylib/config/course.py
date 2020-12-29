"""
################################################
# course.py : Manage recent courses list, etc. #
################################################

Author(s)      : Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
Maintainers(s) : - Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>

Date           : October 2020 (creation)

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

import logging
from   pathlib import Path

import deaduction.pylib.config.vars as cvars

log = logging.getLogger(__name__)

def get_recent_courses() -> ([Path], [str], [int]):
    """
    Return the list of (recent course, title) found in the user_config dict
    """

    recent_courses        = cvars.get("course.recent_courses", [])
    courses_titles        = cvars.get("course.recent_courses_titles", [])
    exercises_numbers     = cvars.get("course.exercise_numbers", [])

    courses_paths         = list(map(Path, recent_courses))
    exercises_numbers     = exercises_numbers or ([-1] * len(recent_courses))

    #if recent_courses:
    #    recent_courses_list = recent_courses.split(',')
    #    courses_paths = list(map(Path, recent_courses_list))
    #    courses_titles = titles.split(',')
    #    exercises_numbers = [-1] * len(recent_courses_list)
    #else:
    #    courses_paths = []
    #    courses_titles = []
    #    exercises_numbers = []

    #if exercises_numbers:
    #    try:
    #        exercises_numbers = list(map(int, numbers.split(',')))
    #    except ValueError:
    #        pass
    return courses_paths, courses_titles, exercises_numbers


def add_to_recent_courses(course_path: Path,
                          course_type: str = ".lean",
                          title: str = "",
                          exercise_number: int = -1):
    """
    Add course_path to the list of recent courses in cvars["course"]
    """

    max_ = cvars.get("course.max_recent_courses", 5)

    if course_type == ".pkl" and course_path.suffix == ".lean":
        course_path = course_path.with_suffix(".pkl")

    course_path = course_path.resolve()
    courses_paths, courses_titles, exercises_numbers = get_recent_courses()
    if course_path in courses_paths:
        # We want the course to appear in pole position
        # 0 = newest, last = oldest
        n = courses_paths.index(course_path)
        courses_paths.pop(n)
        courses_titles.pop(n)
        exercises_numbers.pop(n)
    courses_paths.insert(0, course_path)
    courses_titles.insert(0, title)
    exercises_numbers.insert(0, exercise_number)

    if len(courses_paths) > max_:
        # Remove oldest
        courses_paths.pop()
        courses_titles.pop()
        exercises_numbers.pop()

    # Turn each list into a single string
    courses_paths_strings = [str(path.resolve()) for path in courses_paths]

    #courses_paths_string   = ','.join(courses_paths_strings)
    #courses_titles_string = ','.join(courses_titles)
    #exercises_numbers_string = ','.join(map(str, exercises_numbers))

    cvars.set("course.recent_courses"       , courses_paths_strings)
    cvars.set("course.recent_courses_titles", courses_titles)
    cvars.set("course.exercise_numbers"     , exercises_numbers)

    # Save config file
    cvars.save()


