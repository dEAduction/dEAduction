"""
#######################################################################
# choose_course_exercise_widgets.py : course/exercise chooser widgets #
#######################################################################

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

import sys
from pathlib import Path
from gettext import gettext as _
from typing  import Dict

from PySide2.QtCore    import   Slot
from PySide2.QtWidgets import ( QApplication,
                                QFileDialog,
                                QLabel,
                                QLayout,
                                QListWidget,
                                QGroupBox,
                                QHBoxLayout,
                                QPushButton,
                                QVBoxLayout)

from deaduction.dui.utils        import DisclosureTree
from deaduction.pylib.coursedata import Course


class AbstractCExChooser(QGroupBox):

    def __init__(self, gb_title):

        super().__init__(gb_title)

        self.left_layout  = QVBoxLayout()
        self.right_layout = QVBoxLayout()

    def set_left_layout(self, layout: QLayout):
        
        self.left_layout = layout
        self.__set_main_layout()

    def set_right_layout(self, layout: QLayout=None, title: str=None,
                         subtitle: str=None, details: Dict[str, str]=None,
                         description: str=None):

        # TODO: Keep previously created right layouts in a
        # Dict[cls, QLayout], where cls is either Course or Exercise.
        # It is probably useless tho.

        right_layout = QVBoxLayout()

        if title:
            title_wgt = QLabel(title)
            title_wgt.setStyleSheet('font-size: 16pt;' \
                                    'font-weight: bold;')

            right_layout.addWidget(title_wgt)

        if subtitle:
            subtitle_wgt = QLabel(subtitle)
            subtitle_wgt.setStyleSheet('font-style: italic;' \
                                       'color: gray;')
            subtitle_lyt = QHBoxLayout()
            subtitle_lyt.addWidget(title_wgt)
            subtitle_lyt.addWidget(subtitle_wgt)

            right_layout.addLayout(sub_title_lyt)

        if details:
            details_wgt = DisclosureTree('Details', details)

            right_layout.addWidget(details_wgt)

        if description:
            description_wgt = QLabel(description)
            description_wgt.setWordWrap(True)

            right_layout.addWidget(description_wgt)

            if layout:
                right_layout.addLayout(layout)

        self.right_layout = right_layout
        self.__set_main_layout()

    def __set_main_layout(self):
        main_layout = QHBoxLayout()
        main_layout.addLayout(self.left_layout)
        main_layout.addLayout(self.right_layout)
        self.setLayout(main_layout)


class CourseChooser(AbstractCExChooser):

    def __init__(self):

        super().__init__(_('Choose course (browse and preview)'))
        self.set_left_layout()

    def set_left_layout(self):

        # Browse files button
        browse_btn = QPushButton(_('Browse files for course'))
        browse_btn.clicked.connect(self.__browse_for_course)
        # Previous courses
        # TODO: Add the damn feature
        self.previous_courses_wgt = QListWidget()

        left_layout = QVBoxLayout()
        left_layout.addWidget(browse_btn)
        left_layout.addWidget(self.previous_courses_wgt)

        super().set_left_layout(left_layout)


    def set_right_layout(self, course: Course):

        title       = course.metadata.get('Title',       None)
        subtitle    = course.metadata.get('Subtitle',    None)
        description = course.metadata.get('Description', None)

        details = course.metadata
        # Remove title, subtitle and description from details
        for key in ['Title', 'Subtitle', 'Description']:
            if key in details:
                details.pop(key)
        if not details:  # Set details to None if empty
            details = None

        # TODO: Prevent user for using a 'Path' attribute when writing
        # a course.
        # TODO: Add course path.

        super().set_right_layout(layout=None, title=title, subtitle=subtitle,
                                 details=details, description=description)

    @Slot()
    def __browse_for_course(self):

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('*.lean')

        if dialog.exec_():
            course_path = Path(dialog.selectedFiles()[0])
            course = Course.from_file(course_path)
            self.set_right_layout(course)


if __name__ == '__main__':
    app = QApplication()

    course_chooser = CourseChooser()
    course_chooser.show()

    sys.exit(app.exec_())
