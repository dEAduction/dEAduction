"""
##################################################################
# recent_courses_widgets.py : Provide classes for recent courses #
##################################################################
    
    Provide classes:
        - CoursesLW;
        - CoursesLWI.
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

import deaduction.pylib.config.dirs as cdirs

from deaduction.pylib.config.course import (get_recent_courses,
                                            get_preset_courses)
global _


class CoursesLW(QListWidget):
    """
    An adaptated QListWidget to display *the* list of *recent* (i.e.
    last five or ten courses done in dEAduction by usr) courses' paths and
    minor metadata (e.g. course title). Consequently, no arguments are
    given to __init__ since the function get_recent_courses gets the
    recent courses itself. Therefore, the items do not contain Course
    objects since only courses' paths and minor metadata are saved in
    the config files. This class uses the CoursesLWI for items
    instead of QListWidgetItem.
    """

    def __init__(self, recent=False):
        """
        Init self. See self docstring.
        """

        super().__init__()
        if recent:
            courses_paths, titles, exercise_numbers = get_recent_courses()
        else:
            courses_paths, titles, exercise_numbers = get_preset_courses()

        self.course_paths = courses_paths
        info = zip(courses_paths, titles, exercise_numbers)
        for course_path, course_title, exercise_number in info:
            if course_path and course_path.exists():
                item = CoursesLWI(course_path, course_title)
                self.addItem(item)

    def select_first_item(self):
        if self.count():
            self.setCurrentItem(self.item(0))
            self.setItemSelected(self.item(0), True)

    def get_index(self, abs_course_path):
        for index in range(self.count()):
            if abs_course_path == self.item(index).abs_course_path:
                return index

    def set_current_item(self, course) -> bool:
        """
        If course_path is in self.course_paths, set the current
        corresponding item and return True. If not, return False.
        """

        course_path = course.abs_course_path
        index = self.get_index(course_path)
        if index is not None:
            item = self.item(index)
            self.setCurrentItem(item)
            item.course = course
            return True
        else:
            return False

    def add_browsed_course(self, course, browsed=False):
        """
        Insert a course at the top of the list and mark (in the item
        text) the course as browsed. This is useful in dEaduction
        courses's chooser (see CourseChooser and StartExerciseDialog
        from deaduction.widgets): when a user browses a course, this
        allows to temporarily save the course. This way, the user can
        preview other courses without having to rebrowse the files
        everytime they want to see the first browsed course.
        """

        index = self.get_index(course.abs_course_path)
        if index is not None:
            item = self.takeItem(index)
        else:
            course_title = course.title
            displayed_title = (_('(browsed)') + ' ' + course_title if browsed
                               else course_title)
            item = CoursesLWI(course.abs_course_path, displayed_title)

        item.course = course
        self.insertItem(0, item)
        self.setCurrentItem(item)

    def find_course(self, abs_course_path):
        index = self.get_index(abs_course_path)
        if index:
            course = self.item(index).course
            return course


class CoursesLWI(QListWidgetItem):
    """
    Course items used in the class CoursesLW (see the docstring).
    Those courses are not instanciated with an instance of the Course
    class but with a course's path and title. Indeed: CoursesLW
    displays the recent courses in which the user did exercises, and
    only those data are in the config files.

    :property course_path: Self's course path.
    """

    def __init__(self, abs_course_path: Path, course_title: str):
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
        self.setToolTip(str(abs_course_path))
        self.__abs_course_path = abs_course_path
        self.__course = None

    @property
    def abs_course_path(self):
        """
        Return the item's course path (self.__course_path)
        """

        return self.__abs_course_path

    @property
    def course(self):
        return self.__course

    @course.setter
    def course(self, course):
        self.__course = course