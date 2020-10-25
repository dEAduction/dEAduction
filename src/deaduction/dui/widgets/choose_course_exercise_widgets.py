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

from deaduction.dui.widgets      import StatementsTreeWidget
from deaduction.dui.utils        import DisclosureTree
from deaduction.pylib.coursedata import Course


class AbstractCoExChooser(QGroupBox):

    def __init__(self, title: str, browser_layout: QLayout):

        super().__init__(title)
        
        nothing_to_preview = QWidget()
        nothing_to_preview_lyt = QVBoxLayout()
        nothing_to_preview_lyt.addStretch()
        nothing_to_preview_lyt.addWidget(QLabel(_('Nothing to preview')))
        nothing_to_preview_lyt.addStretch()
        nothing_to_preview.setLayout(nothing_to_preview_lyt)

        self.__preview_wgt = nothing_to_preview

        self.__main_layout = QHBoxLayout()
        self.__main_layout.addLayout(browser_layout)
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

        if widget:
            layout.addWidget(widget)

        preview_wgt.setLayout(layout)
        self.__main_layout.replaceWidget(self.__preview_wgt, preview_wgt)
        self.__preview_wgt.deleteLater()
        self.__preview_wgt = preview_wgt


class CourseChooser(AbstractCoExChooser):

    def __init__(self):

        # Browse files button
        self.browse_btn = QPushButton(_('Browse files for course'))
        # TODO: Add previous courses
        self.previous_courses_wgt = QListWidget()

        browser_layout = QVBoxLayout()
        browser_layout.addWidget(self.browse_btn)
        browser_layout.addWidget(self.previous_courses_wgt)

        super().__init__(_('Choose course (browse and preview)'), browser_layout)

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

        # FIXME: seg fault after this, created in CourseChooser
        super().set_preview(widget=None, title=title, subtitle=subtitle,
                            details=details, description=description)


class ExerciseChooser(AbstractCoExChooser):

    def __init__(self, course: Course):

        browser_layout = QVBoxLayout()
        self.__exercises_tree = StatementsTreeWidget(course.exercises_list(),
                                                     course.outline)
        browser_layout.addWidget(self.__exercises_tree)

        super().__init__(_('Choose exercise from selected course (browse and '\
                           'preview)'), browser_layout)


class DuiLauncher(QWidget):

    def __init__(self):

        super().__init__()
        self.setWindowTitle(_('Choose course and exercise'))

        self.__course_chooser = CourseChooser()
        self.__course_chooser.browse_btn.clicked.connect(self.__browse_courses)
        self.__exercise_chooser = QWidget()

        # ───────────────────── Layouts ──────────────────── #

        self.__coex_lyt = QVBoxLayout()
        self.__coex_lyt.addWidget(self.__course_chooser)
        self.__coex_lyt.addWidget(self.__exercise_chooser)

        buttons_lyt = QHBoxLayout()
        buttons_lyt.addStretch()
        buttons_lyt.addWidget(QPushButton(_('Quit')))
        buttons_lyt.addWidget(QPushButton(_('Start exercise')))

        self.__mlyt = QVBoxLayout()
        self.__mlyt.addLayout(self.__coex_lyt)
        self.__mlyt.addLayout(buttons_lyt)

        self.setLayout(self.__mlyt)

    @Slot()
    def __browse_courses(self):

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('*.lean')

        if dialog.exec_():
            course_path = Path(dialog.selectedFiles()[0])
            course = Course.from_file(course_path)
            self.__set_course(course)

    def __set_course(self, course: Course):
        self.__course_chooser.set_preview(course)  # FIXME seg fault here
        exercise_chooser = ExerciseChooser(course)
        self.__mlyt.replaceWidget(self.__exercise_chooser, exercise_chooser)
        self.__exercise_chooser.deleteLater()
        self.__exercise_chooser = exercise_chooser


if __name__ == '__main__':
    app = QApplication()

    dui_launcher = DuiLauncher()
    dui_launcher.show()

    sys.exit(app.exec_())
