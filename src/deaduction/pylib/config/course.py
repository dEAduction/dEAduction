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
import deaduction.pylib.config.dirs as cdirs

log = logging.getLogger(__name__)


def real_path_relative_to_home(path):
    """
    Try to find a file from path, and return real path to this file relative
    to home dir.
    """
    for real_path in [path, cdirs.local / path, cdirs.home / path,
                      cdirs.usr_lean_exercises_dir / path]:
        if real_path.exists():
            return cdirs.relative_to_home(real_path)

    print(f"Path {path} not found")


def absolute_real_path(path):
    """
    Try to find a file from path, and return real path to this file relative
    to home dir. If nothing is found, then return None.
    """

    directories = [path, cdirs.local / path, cdirs.home / path,
                   cdirs.usr_lean_exercises_dir / path]
    for real_path in directories:
        if real_path.exists():
            return real_path

    print(f"Path {path} not found")


def courses_paths() -> [Path]:
    """
    Get list of all (abs paths to) lean files in Lean exercises dir.
    """

    exercise_dir = cdirs.usr_lean_exercises_dir
    paths = list(exercise_dir.glob('*.lean'))
    # real_paths = [real_path_relative_to_home(path) for path in paths]
    # return [path for path in real_paths if path]
    return paths


def get_preset_courses() -> ([Path], [str], [int]):
    """
    Return the list of (preset course, paths title)
    found in the config file.
    """
    preset_courses = cvars.get('course.preset_courses', None)
    if preset_courses:
        courses = [absolute_real_path(Path(course))
                   for course in preset_courses]
        if None in courses:
            log.warning("Preset course path not found")
            courses = [course for course in courses if course]
    else:
        courses = courses_paths()
    file_titles = [file.stem for file in courses]
    titles = [title.replace('_', ' ') for title in file_titles]

    return courses, titles, [-1]*len(courses)


def get_recent_courses() -> ([Path], [str], [int]):
    """
    Return the list of (recent course path, title)
     found in the config file.
    """

    recent_paths        = cvars.get("course.recent_courses", [])
    courses_titles        = cvars.get("course.recent_courses_titles", [])
    exercises_numbers     = cvars.get("course.exercise_numbers", [])

    courses_paths = [absolute_real_path(Path(path))
                     for path in recent_paths if path]

    if None in courses_paths:
        log.warning("Recent course path not found")
        return [], [], []

    exercises_numbers = exercises_numbers or ([-1] * len(recent_paths))

    return courses_paths, courses_titles, exercises_numbers


def erase_recent_courses():
    """
    Erase all recent courses. This is called when version nb is modified.
    """
    cvars.set("course.recent_courses", [])
    cvars.set("course.recent_courses_titles", [])
    cvars.set("course.exercise_numbers", [])


def add_to_recent_courses(course_path: Path,
                          # course_type: str = ".lean",
                          title: str = "",
                          exercise_number: int = -1):
    """
    Add course_path to the list of recent courses in cvars["course"].
    This should be an absolute path, as is course.abs_course_path.
    """

    max_ = cvars.get("functionality.max_recent_courses", 5)

    # if course_type == ".pkl" and course_path.suffix == ".lean":
    #     course_path = course_path.with_suffix(".pkl")

    course_path = absolute_real_path(course_path)
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

    cvars.set("course.recent_courses"       , courses_paths_strings)
    cvars.set("course.recent_courses_titles", courses_titles)
    cvars.set("course.exercise_numbers"     , exercises_numbers)

    # Save config file
    cvars.save_single_key("course.recent_courses")
    cvars.save_single_key("course.recent_courses_titles")
    cvars.save_single_key("course.exercise_numbers")


