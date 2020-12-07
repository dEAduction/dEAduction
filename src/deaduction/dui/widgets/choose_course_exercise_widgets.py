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
import pickle
from gettext import   gettext as _
from typing  import ( Any,
                      Dict )

from PySide2.QtCore    import ( Signal,
                                Slot )
from PySide2.QtGui     import ( QFont,
                                QPixmap )
from PySide2.QtWidgets import ( QApplication,
                                QCheckBox,
                                QDialog,
                                QFileDialog,
                                QFrame,
                                QGroupBox,
                                QHBoxLayout,
                                QLabel,
                                QLayout,
                                QLineEdit,
                                QListWidget,
                                QSpacerItem,
                                QPushButton,
                                QTabWidget,
                                QTextEdit,
                                QVBoxLayout,
                                QWidget )

from deaduction.dui.widgets      import ( MathObjectWidget,
                                          StatementsTreeWidget,
                                          StatementsTreeWidgetItem )
from deaduction.dui.utils        import   DisclosureTree
from deaduction.pylib.coursedata import ( Course,
                                          Exercise )


# TODO: Put this function somewhere else
def read_pkl_course(course_path: Path) -> Course:
    """
    Extract an instance of the class Course from a .pkl file.
    """

    with course_path.open(mode='rb') as input:
        course = pickle.load(input)

    return course


class HorizontalLine(QFrame):

    def __init__(self):

        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class AbstractCoExChooser(QWidget):

    def __init__(self, browser_layout: QLayout):

        super().__init__()

        no_preview_yet = QLabel(_('No preview yet.'))
        no_preview_yet.setStyleSheet('color: gray;')
        self.__preview_wgt = no_preview_yet

        self.__main_layout = QVBoxLayout()
        self.__main_layout.addLayout(browser_layout)
        self.__main_layout.addItem(QSpacerItem(1, 5))
        self.__main_layout.addWidget(HorizontalLine())
        self.__main_layout.addItem(QSpacerItem(1, 5))
        self.__main_layout.addWidget(self.__preview_wgt)

        self.setLayout(self.__main_layout)

    def set_preview(self, widget: QWidget=None, title: str=None,
                    subtitle: str=None, details: Dict[str, str]=None,
                    description: str=None):

        preview_wgt = QWidget()
        layout      = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        if title:
            title_wgt = QLabel(title)
            title_wgt.setStyleSheet('font-weight: bold;' \
                                    'font-size:   17pt;')
            layout.addWidget(title_wgt)

        if subtitle:
            subtitle_wgt = QLabel(subtitle)
            subtitle_wgt.setStyleSheet('font-style: italic;' \
                                       'color:      gray;')
            subtitle_lyt = QHBoxLayout()
            subtitle_lyt.addWidget(title_wgt)
            subtitle_lyt.addWidget(subtitle_wgt)
            layout.addLayout(sub_title_lyt)

        if details:
            details_wgt = DisclosureTree('Details', details)
            layout.addWidget(details_wgt)

        if description:
            # TODO: Make text unselectable
            description_wgt = QTextEdit(description)
            description_wgt.setReadOnly(True)
            # TODO: QSlider is ugly, make it not. that. way.
            description_wgt.setStyleSheet('background-color: transparent')
            layout.addWidget(description_wgt)

        if widget:
            layout.addWidget(widget)

        layout.addStretch()

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

        browser_lyt = QVBoxLayout()
        browser_lyt.addWidget(self.browse_btn)
        browser_lyt.addWidget(self.previous_courses_wgt)

        super().__init__(browser_lyt)

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

    def __init__(self, course: Course, course_filetype: str):

        self.__course_filetype = course_filetype  # 'lean' or 'pkl'

        browser_layout = QVBoxLayout()
        exercises_tree = StatementsTreeWidget(course.exercises_list(),
                                              course.outline)
        exercises_tree.resizeColumnToContents(0)
        # TODO: Expand items (write function in StatementsTreeWidget)
        browser_layout.addWidget(exercises_tree)

        exercises_tree.itemClicked.connect(self.__call_set_preview)

        super().__init__(browser_layout)

    def set_preview(self, exercise: Exercise):

        widget = QWidget()
        widget_lyt = QVBoxLayout()
        widget_lyt.setContentsMargins(0, 0, 0, 0)
        self.__exercise = exercise

        if self.__course_filetype == '.pkl':

            proofstate = exercise.initial_proof_state
            goal = proofstate.goals[0]  # Only one goal (?)
            target = goal.target
            context = goal.tag_and_split_propositions_objects()
            objects = context[0]
            properties = context[1]

            # ───────────────── Friendly widget ──────────────── #

            propobj_lyt = QHBoxLayout()
            objects_wgt = MathObjectWidget(objects)
            properties_wgt = MathObjectWidget(properties)
            objects_lyt, properties_lyt = QVBoxLayout(), QVBoxLayout()
            objects_wgt.setFont(QFont('Menlo'))
            properties_wgt.setFont(QFont('Menlo'))

            objects_lyt.addWidget(QLabel(_('Objects:')))
            properties_lyt.addWidget(QLabel(_('Properties:')))
            objects_lyt.addWidget(objects_wgt)
            properties_lyt.addWidget(properties_wgt)
            propobj_lyt.addLayout(objects_lyt)
            propobj_lyt.addLayout(properties_lyt)

            target_wgt = QLineEdit()
            target_wgt.setText(target.math_type.to_display(format_="utf8",
                                                           is_math_type=True))
            target_wgt.setFont(QFont('Menlo'))

            self.__friendly_wgt = QWidget()
            friendly_wgt_lyt = QVBoxLayout()
            friendly_wgt_lyt.addLayout(propobj_lyt)
            friendly_wgt_lyt.addWidget(QLabel(_('Target:')))
            friendly_wgt_lyt.addWidget(target_wgt)
            self.__friendly_wgt.setLayout(friendly_wgt_lyt)

            # ─────────────────── Code widget ────────────────── #

            self.__code_wgt = QTextEdit()
            self.__code_wgt.setReadOnly(True)
            self.__code_wgt.setFont(QFont('Menlo'))
            # TODO: Set value

            # ──────────────────── Checkbox ──────────────────── #

            self.__text_mode_checkbox = QCheckBox(_('Text mode'))
            self.__text_mode_checkbox.clicked.connect(self.toggle_text_mode)
            cb_lyt = QHBoxLayout()
            cb_lyt.addStretch()
            cb_lyt.addWidget(self.__text_mode_checkbox)

            # ──────────────── Contents margins ──────────────── #

            for lyt in [widget_lyt, friendly_wgt_lyt]:
                # Somehow this works…
                lyt.setContentsMargins(0, 0, 0, 0)

            # ──────────────── Organize widgets ──────────────── #

            self.__text_mode_checkbox.setChecked(False)
            self.__friendly_wgt.show()
            self.__code_wgt.hide()

            widget_lyt.addWidget(self.__friendly_wgt)
            widget_lyt.addWidget(self.__code_wgt)
            widget_lyt.addLayout(cb_lyt)

        # FIXME: Bug with course and exercise widgets
        elif self.__course_filetype == '.lean':

            # TODO: Say "Preview is available if…"
            widget_lbl = QLabel(_('Goal preview only available when course ' \
                                  'file extension is .pkl.'))
            widget_lbl.setStyleSheet('color: gray;')

            widget_lyt.addWidget(widget_lbl)

        widget.setLayout(widget_lyt)

        # ───────────────────── Others ───────────────────── #

        # TODO: Add subtitle, task…
        title = exercise.pretty_name
        description = exercise.description

        super().set_preview(widget=widget, title=title, description=description)

    def selected_exercise(self) -> Exercise:
        if self.__exercise:
            return self.__exercise
        else:
            return None

    @Slot(StatementsTreeWidgetItem)
    def __call_set_preview(self, item: StatementsTreeWidgetItem):
        if isinstance(item, StatementsTreeWidgetItem):
            exercise = item.statement
            self.set_preview(exercise)

    @Slot()
    def toggle_text_mode(self):
        if self.__text_mode_checkbox.isChecked():
            self.__friendly_wgt.hide()
            self.__code_wgt.show()
        else:
            self.__friendly_wgt.show()
            self.__code_wgt.hide()


class StartExerciseDialog(QDialog):

    exercise_choosen = Signal(Exercise)

    def __init__(self):

        super().__init__()
        self.setWindowTitle(_('Choose course and exercise — d∃∀duction'))

        self.__course_chooser = CourseChooser()
        self.__exercise_chooser = QWidget()

        self.__start_ex_btn = QPushButton(_('Start exercise'))
        self.__start_ex_btn.clicked.connect(self.__start_exercise)

        # ───────────────────── Layouts ──────────────────── #

        self.__coex_tabwidget = QTabWidget()
        self.__coex_tabwidget.addTab(self.__course_chooser, _('Course'))
        self.__coex_tabwidget.addTab(self.__exercise_chooser, _('Exercise'))

        buttons_lyt = QHBoxLayout()
        buttons_lyt.addStretch()
        buttons_lyt.addWidget(QPushButton(_('Quit')))
        buttons_lyt.addWidget(QPushButton(_('Load goal')))
        buttons_lyt.addWidget(self.__start_ex_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.__coex_tabwidget)
        main_layout.addLayout(buttons_lyt)

        self.setLayout(main_layout)

        # ───────────────────── Others ───────────────────── #

        self.__coex_tabwidget.setTabEnabled(1, False)
        self.__course_chooser.browse_btn.clicked.connect(self.__browse_courses)

    def __set_course(self, course: Course, course_filetype: str):
        self.__coex_tabwidget.removeTab(1)
        self.__coex_tabwidget.setTabEnabled(1, True)
        self.__course_chooser.set_preview(course)
        self.__exercise_chooser = ExerciseChooser(course, course_filetype)
        self.__coex_tabwidget.addTab(self.__exercise_chooser, _('Exercise'))
        self.__coex_tabwidget.setCurrentIndex(1)

    @Slot()
    def __browse_courses(self):

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('*.lean *.pkl')

        if dialog.exec_():
            course_path = Path(dialog.selectedFiles()[0])
            course_filetype = course_path.suffix

            if course_filetype == '.lean':
                course = Course.from_file(course_path)
            elif course_filetype == '.pkl':
                course = read_pkl_course(course_path)

            self.__set_course(course, course_filetype)

    @Slot()
    def __start_exercise(self):

        exercise = self.__exercise_chooser.selected_exercise()
        self.exercise_choosen.emit(exercise)

        self.accept()  # Fuck you and I'll see you tomorrow!


if __name__ == '__main__':
    app = QApplication()

    start_exercise_dialog = StartExerciseDialog()
    start_exercise_dialog.show()

    sys.exit(app.exec_())
