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
from pathlib import   Path
from gettext import   gettext as _
from typing  import ( Any,
                      Dict)

from PySide2.QtCore    import   Slot
from PySide2.QtWidgets import ( QApplication,
                                QFileDialog,
                                QGroupBox,
                                QHBoxLayout,
                                QLabel,
                                QLayout,
                                QListWidget,
                                QPushButton,
                                QVBoxLayout,
                                QWidget)

from deaduction.dui.utils        import DisclosureTree
from deaduction.pylib.coursedata import Course


class AbstractCoExChooser(QGroupBox):

    def __init__(self, title: str, left_layout: QLayout):

        super().__init__(title)
        
        nothing_to_preview = QWidget()
        nothing_to_preview_lyt = QVBoxLayout()
        nothing_to_preview_lyt.addStretch()
        nothing_to_preview_lyt.addWidget(QLabel(_('Nothing to preview')))
        nothing_to_preview_lyt.addStretch()
        nothing_to_preview.setLayout(nothing_to_preview_lyt)

        self.__preview_wgt = nothing_to_preview

        self.__main_layout = QHBoxLayout()
        self.__main_layout.addLayout(left_layout)
        self.__main_layout.addWidget(self.__preview_wgt)

        self.setLayout(self.__main_layout)

    def set_preview(self, widget: QWidget=None, title: str=None,
                    subtitle: str=None, details: Dict[str, str]=None,
                    description: str=None):

        preview_wgt = QWidget()
        layout      = QVBoxLayout()

        if title:
            title_wgt = QLabel(title)
            title_wgt.setStyleSheet('font-size: 16pt;' \
                                    'font-weight: bold;')

            layout.addWidget(title_wgt)

        if subtitle:
            subtitle_wgt = QLabel(subtitle)
            subtitle_wgt.setStyleSheet('font-style: italic;' \
                                       'color: gray;')
            subtitle_lyt = QHBoxLayout()
            subtitle_lyt.addWidget(title_wgt)
            subtitle_lyt.addWidget(subtitle_wgt)

            layout.addLayout(sub_title_lyt)

        if details:
            details_wgt = DisclosureTree('Details', details)

            layout.addWidget(details_wgt)

        if description:
            description_wgt = QLabel(description)
            description_wgt.setWordWrap(True)

            layout.addWidget(description_wgt)

        layout.addWidget(widget)
        preview_wgt.setWidget(layout)

        self.__main_layout.replaceWidget(self.__preview_wgt, preview_wgt)
        self.__preview_wgt.deleteLater()
        self.__preview_wgt = preview_wgt


class CourseChooser(AbstractCoExChooser):

    def __init__(self):

        # Browse files button
        browse_btn = QPushButton(_('Browse files for course'))
        browse_btn.clicked.connect(self.__browse_for_course)
        # TODO: Add previous courses
        self.previous_courses_wgt = QListWidget()

        left_layout = QVBoxLayout()
        left_layout.addWidget(browse_btn)
        left_layout.addWidget(self.previous_courses_wgt)

        super().__init__(_('Choose course (browse and preview)'), left_layout)

    def set_preview(self, course: Course):

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

        super().set_preview(widget=None, title=title, subtitle=subtitle,
                            details=details, description=description)

    @Slot()
    def __browse_for_course(self):

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('*.lean')

        if dialog.exec_():
            course_path = Path(dialog.selectedFiles()[0])
            course = Course.from_file(course_path)
            self.set_preview(course)


if __name__ == '__main__':
    app = QApplication()

    course_chooser = CourseChooser()
    course_chooser.show()

    sys.exit(app.exec_())
