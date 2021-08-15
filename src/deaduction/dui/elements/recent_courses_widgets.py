"""
##################################################################
# recent_courses_widgets.py : Provide classes for recent courses #
##################################################################
    
    Provide classes:
        - RecentCoursesLW;
        - RecentCoursesLWI.
    Those two classes are used dEAduction's 'Start exercise' dialog to
    display the list of recent courses used by usr.

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

from PySide2.QtWidgets import ( QListWidget,
                                QListWidgetItem)

from deaduction.pylib.config.course import get_recent_courses


class RecentCoursesLW(QListWidget):
    """
    An adaptated QListWidget to display *the* list of *recent* (i.e.
    last five courses done in dEAduction by usr) courses' paths and
    minor metadata (e.g. course title). Consequently, no arguments are
    given to __init__ since the function get_recent_courses gets the
    recent courses itself. Therefore, the items do not contain Course
    objects since only courses' paths and minor metadata are saved in
    the config files. This class uses the RecentCoursesLWI for items
    instead of QListWidgetItem.
    """

    def __init__(self):
        """
        Init self. See self docstring.
        """

        super().__init__()

        courses_paths, titles, exercise_numbers = get_recent_courses()
        info = zip(courses_paths, titles, exercise_numbers)
        for course_path, course_title, exercise_number in info:
            if course_path.exists():
                item = RecentCoursesLWI(course_path, course_title)
                self.addItem(item)

    def add_browsed_course(self, course_path: Path, course_title: str):
        """
        Insert a course at the top of the list and mark (in the item
        text) the course as browsed. This is useful in dEaduction
        courses's chooser (see CourseChooser and StartExerciseDialog
        from deaduction.widgets): when a user browses a course, this
        allows to temporarly save the course. This way, the user can
        preview other courses without having to rebrowse the files
        everytime they want to see the first browsed course.

        :param course_path: The course path of the browsed course.
        :param course_title: The course title of the browsed course.
        """

        displayed_title = f'(browsed) {course_title}'
        item = RecentCoursesLWI(course_path, displayed_title)
        self.insertItem(0, item)
        self.setItemSelected(item, True)


class RecentCoursesLWI(QListWidgetItem):
    """
    Course items used in the class RecentCoursesLW (see the docstring).
    Those courses are not instanciated with an instance of the Course
    class but with a course's path and title. Indeed: RecentCoursesLW
    displays the recent courses in which the user did exercises, and
    only those data are in the config files.

    :property course_path: Self's course path.
    """

    def __init__(self, course_path: Path, course_title: str):
        """
        Init self, see self docstring.

        :param course_path: The course path of the recent course saved
            in the config files.
        :param course_title: The course title of the recent course
            savec in the config files.
        """

        # w_or_wo = 'w/' if course_path.suffix == '.pkl' else 'w/o'
        # super().__init__(f'{course_title} [{w_or_wo} preview]')

        super().__init__(course_title)
        self.setToolTip(str(course_path))
        self.__course_path = course_path

    @property
    def course_path(self):
        """
        Return the item's course path (self.__course_path)
        """

        return self.__course_path
