"""
#####################################################
# classes.py : Utilitary classes for deaduction.dui #
#####################################################

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
Date           : October 2020

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

from pathlib import Path
from typing  import Dict

from PySide2.QtCore    import   Qt
from PySide2.QtWidgets import ( QFrame,
                                QListWidget,
                                QListWidgetItem,
                                QTreeWidget,
                                QTreeWidgetItem)

#from deaduction.config import ( add_to_recent_courses,
#                                get_recent_courses )
from deaduction.pylib.config.course import ( add_to_recent_courses,
                                             get_recent_courses )

class DisclosureTriangle(QTreeWidget):
    """
    An (very basic) implementation of a DisclosureTriangle, i.e. a
    widget that looks like this:

    ____________________
    |                  |
    |  |> Title:       |
    |      key1: val1  |
    |      key2: val2  |
    |      …           |
    --------------------

    This triangle can be expanded or collapsed and is instanciated with
    a title and a dictionnary of keys and values. Made with the help of
    musicamente on Stackoverflow:  https://stackoverflow.com/questions/
    63862724/
    qtreeview-dynamic-height-according-to-content-disclosure-triangle.
    """

    def __init__(self, title: str, data: Dict[str, str]):
        """
        Init self with a title and a dictionnary of keys and values (see
        self docstring).

        :param title: The title of the disclosure tree (e.g. 'Details'
            in dEAduction's course and exercise choosers.
        :param data: The data to be displayed in the disclosure
            triangle.
        """

        super().__init__()

        # ─────────────────── Add content ────────────────── #

        self.setColumnCount(2)
        self.__parent_item = QTreeWidgetItem(self, [f'{title} : '])
        self.__parent_item.set_selectable(False)
        self.addTopLevelItem(self.__parent_item)

        for key, val in data.items():
            item = QTreeWidgetItem(self.__parent_item, [f'{key} : ', val])
            self.__parent_item.addChild(item)

            # Cosmetics
            item.set_selectable(False)
            item.setTextAlignment(0, Qt.AlignRight)

        # ──────────────────── Cosmetics ─────────────────── #

        # Hide header
        self.header().hide()

        # No background
        self.setStyleSheet('background-color: transparent;')

        # Dynamically change height when widget is collapsed or expanded
        # You have to update the maximum height of the widget, based on
        # its contents. For each top item you need to get the height for
        # that row using rowHeight() and do the same recursively for
        # child items whenever the item is expanded. Also, you need to
        # overwrite the sizeHint and minimumSizeHint.
        self.expanded.connect(self.update_height)
        self.collapsed.connect(self.update_height)

    def expand(self, yes: bool=True):
        """
        Expand the tree is yes is True, collapse it otherwise.

        :param yes: See above.
        """

        if yes:
            self.expandItem(self.__parent_item)
        else:
            self.collapseItem(self.__parent_item)

    #####################
    # Redifined methods #
    #####################

    # See
    # https://stackoverflow.com/questions/63862724/
    # qtreeview-dynamic-height-according-to-content-disclosure-triangle

    def update_height(self):
        self.setMaximumHeight(self.sizeHint().height())

    def get_height(self, parent=None):
        height = 0
        if not parent:
            parent = self.rootIndex()
        for row in range(self.model().rowCount(parent)):
            child = self.model().index(row, 0, parent)
            height += self.rowHeight(child)
            if self.isExpanded(child) and self.model().hasChildren(child):
                    height += self.get_height(child)
        return height

    def sizeHint(self):
        hint = super().sizeHint()
        # The + 10 avoids an ugly scroll bar
        hint.setHeight(self.get_height() + 10 + self.frameWidth() * 2)
        return hint

    def minimumSizeHint(self):
        return self.sizeHint()


class HorizontalLine(QFrame):
    """
    An horizontal line (like <hr> in HTML) QWidget.
    """

    def __init__(self):

        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class RecentCoursesLW(QListWidget):
    """
    An adaptated QListWidget to display *the* list of courses' paths and
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

        w_or_wo = 'w/' if course_path.suffix == '.pkl' else 'w/o'
        super().__init__(f'{course_title} [{w_or_wo} preview]')

        self.setToolTip(str(course_path))
        self.__course_path = course_path

    @property
    def course_path(self):
        """
        Return the item's course path (self.__course_path)
        """

        return self.__course_path
