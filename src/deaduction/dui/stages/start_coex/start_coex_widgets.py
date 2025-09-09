"""
############################################################
# choose_coex_widgets.py : course/exercise chooser widgets #
############################################################

    Provide StartCoExStartup and StartCoExExerciseFinished: dialogs used
    by usr at the start-up of the program and after an exercise is
    finisehd to choose, preview and start an exercise.

    The classes to be used elsewhere in the program are StartCoExStartup
    and StartCoExExerciseFinished (inherits QDialog). The other classes
    (AbstractCoExChooser, CourseChooser, ExerciseChooser) are meant to
    be used in this file only, for technical purposes.

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
from os import environ
import logging
from functools import partial
from pathlib import   Path
from typing  import  (Dict,
                      Optional)

from PySide2.QtCore    import (Qt,
                               QTimer,
                               Signal,
                               Slot,
                               QEvent,
                               QSettings)
from PySide2.QtGui     import  QKeySequence, QIcon
from PySide2.QtWidgets import (QApplication, QCheckBox, QDialog, QFileDialog,
                               QHBoxLayout, QLabel, QLayout, QSpacerItem,
                               QPushButton, QTabWidget, QTextEdit, QVBoxLayout,
                               QWidget, QShortcut, QToolBar, QAction, QFrame,
                               QStackedLayout, QMessageBox)

import deaduction.pylib.config.vars  as     cvars
import deaduction.pylib.config.dirs  as     cdirs

import deaduction.pylib.utils.filesystem as fs
from deaduction.dui.primitives      import (DisclosureDict,
                                            ButtonsDialog,
                                            GoalTextWidget,
                                            YesNoDialog)
from deaduction.dui.elements        import (CoursesLW,
                                            CoursesLWI,
                                            StatementsTreeWidget,
                                            StatementsTreeWidgetItem,
                                            GoalTextWidget,
                                            GoalMathWidget,
                                            GoalWidget)

from deaduction.dui.elements.start_coex_widget_classes import ChooseExerciseWidgetItem

from deaduction.dui.utils           import (replace_widget_layout,
                                            HorizontalLine)
from deaduction.dui.primitives import DeaductionTutorialDialog
from deaduction.pylib.config.course import  add_to_recent_courses
from deaduction.pylib.coursedata    import (Course,
                                            Exercise)
from deaduction.pylib.math_display.pattern_init import PatternInit
from deaduction.pylib.server import ServerInterface

log = logging.getLogger(__name__)
global _


class AbstractCoExChooser(QWidget):
    """
    This class was made for technical purposes and is not to be used
    outside this file. In StartExerciseDialog, both the course chooser
    and the exercise chooser have the same structure:
    - a browser area (browse courses or browse exercices inside one
      course) on top;
    - a previewer area (preview the title, task, description, etc) on
      bottom.
    In other words, course and exercise choosers contain different
    widgets which are organized in the same way. Therefore, both
    CourseChooser and ExerciseChooser inherit from this class . It looks
    like this:

    |------------|
    |   browser  |
    |------------|
    |   preview  |
    |------------|

    For the details, the bowser part never changes and is instanciated
    at init (browser_layout passed as argument). On the opposite, there
    is a preview only if something (a course or exercise) has been
    chosen. This preview is set with the method set_preview. Now,
    CourseChooser and ExerciseChooser need to have their own
    sub-widgets. The way to do that here is to redefine __init__ (for
    the browser) and set_preview (for the preview), define the
    sub-widgets inside the definitions, and call super().__init__ and
    super().set_preview with the defined widgets.

    Finally, data such as the course being previewed is kept as private class
    atributes.
    """

    def __init__(self, browser_layout: QLayout):
        """
        Init self by preparing layouts and adding the (fixed)
        browser_layout (not a QWidget!).

        :param browser_layout: QLayout to be displayed for the browser
            area.
        """

        super().__init__()

        self.__preview_wgt = QTextEdit(_('No preview yet.'))
        self.__preview_wgt.setReadOnly(True)
        self.__preview_wgt.setStyleSheet('color: gray;')
        spacer1             = QSpacerItem(1, 5)
        spacer2             = QSpacerItem(1, 5)
        self.__main_layout = QVBoxLayout()
        self.__browser_layout = browser_layout
        self.__main_layout.addLayout(browser_layout)
        self.__main_layout.addItem(spacer1)
        self.__main_layout.addWidget(HorizontalLine())
        self.__main_layout.addItem(spacer2)
        self.__main_layout.addWidget(self.__preview_wgt)

        self.setLayout(self.__main_layout)

    def set_preview(self, main_widget: Optional[QWidget], title: Optional[str],
                    subtitle: Optional[str], details: Optional[Dict[str, str]],
                    description: Optional[str], expand_details: Optional[bool]):
        # TODO: Make widget a QLayout instead?
        """
        Set the preview area of the choosen course or exercise (given
        something has been chosen). The preview area is made of a title,
        a substitle, details, a description and a main widget. This
        widget is of course specific to CourseChooser or ExerciseChooser
        and defined when the set_preview method is redefined in
        CourseChooser or ExerciseChooser. Visually, the preview area
        looks like this:

        |----------------------------|
        | title (big)                |
        | subtitle (small, italic)   |
        | |> Details:                |
        |     …: …                   |
        |     …: …                   |
        |                            |
        | description .............. |
        | .......................... |
        | .......................... |
        |                            |
        | |------------------------| |
        | |      main_widget       | |
        | |------------------------| |
        |----------------------------|

        :param main_widget: The main widget of the preview (nothing for
            the course, goal preview for the exercise).
        :param title: Course or exercise title.
        :param subtitle: Course or exercise subtitle.
        :param details: Other data for the course or exercise such as
            the course's year, teacher, school, etc.
        :param description: The course or exercise description.
        :param expand_details: Tell if the 'Details' disclosure tree is
            expanded at __init__ (True) or not (False).
        """

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        if title:
            title_wgt = QLabel(title)
            title_wgt.setStyleSheet('font-weight: bold;'
                                    'font-size:   17pt;')
            layout.addWidget(title_wgt)
        if subtitle:
            subtitle_wgt = QLabel(subtitle)
            subtitle_lyt = QHBoxLayout()
            subtitle_wgt.setStyleSheet('font-style: italic;'
                                       'color:      gray;')
            subtitle_lyt.addWidget(subtitle_wgt)
            layout.addLayout(subtitle_lyt)
        if description:
            description_wgt = QLabel(description)
            description_wgt.setStyleSheet('font-size:   15pt;')
            description_wgt.setWordWrap(True)
            layout.addWidget(description_wgt)
        if details:
            details_wgt = DisclosureDict(_('Details:'), details)
            details_wgt.expand(expand_details)

            layout.addWidget(details_wgt)

        layout.addStretch()  # Fixme: useless??

        if main_widget:
            layout.addWidget(main_widget)

        widget.setLayout(layout)
        replace_widget_layout(self.__main_layout, self.__preview_wgt, widget)
        self.__preview_wgt = widget


class CourseChooser(AbstractCoExChooser):
    """
    The course chooser, see AbstractCoExChooser docstring.
    - The browser part is made of a browse-button to browse courses
      files and a QListWidget displaying recent courses.
    - The preview area has no main_widget.
    """

    course_chosen = Signal(Course)
    goto_exercises = Signal()
    recent_courses_checkbox = None

    def __init__(self, servint, select_first_item=True):
        """
        See AbstractCoExChooser.__init__ docstring. Here, the browser
        layout is made of a browse-button to browse courses files
        and a QListWidget displayling recent courses.
        """

        self.current_course = None  # Useful to save initial proof states
        self.loaded_courses = []  # Set of all loaded courses

        self.servint: ServerInterface = servint

        # Browse button
        self.__browse_btn = QPushButton(_('Browse all files...'))
        self.__browse_btn.setAutoDefault(False)
        self.__browse_btn.clicked.connect(self.__browse_courses)

        # Recent courses widget
        self.__courses_lyt = QStackedLayout()
        self.__preset_courses_wgt = CoursesLW(recent=False)
        self.__recent_courses_wgt = CoursesLW(recent=True)
        self.__courses_lyt.addWidget(self.__preset_courses_wgt)
        self.__courses_lyt.addWidget(self.__recent_courses_wgt)

        browser_layout = QVBoxLayout()
        self.__label_title = QLabel()
        self.__label_title.setStyleSheet('font-weight: bold;')
                                         # 'font-size:   17pt;')
        browser_layout.addWidget(self.__label_title)
        browser_layout.addLayout(self.__courses_lyt)
        browser_layout.addWidget(self.__browse_btn)

        # Signals
        self.__courses_wgt = self.__preset_courses_wgt
        self.__preset_courses_wgt.currentItemChanged.connect(
            self.current_item_changed)
        self.__preset_courses_wgt.itemDoubleClicked.connect(
                lambda x: self.goto_exercises.emit())
        self.__recent_courses_wgt.currentItemChanged.connect(
            self.current_item_changed)
        self.__recent_courses_wgt.itemDoubleClicked.connect(
                lambda x: self.goto_exercises.emit())
        self.servint.initial_proof_state_set.connect(
            self.__check_all_statements)

        super().__init__(browser_layout)
        self.show_recent_courses()
        if select_first_item and self.__courses_wgt:
            self.__courses_wgt.select_first_item()
            # self.current_item_changed()

    @property
    def current_index(self):
        """
        Return
            0 if self.__preset_courses_wgt is displayed
            1 if self.__recent_course_widget is displayed.
        """
        return self.__courses_lyt.currentIndex()

    @property
    def __current_item(self):
        return self.__courses_wgt.currentItem()

    def set_selected_course(self):
        """
        Select the current course item:
            - Call for loading of initial proof states
            - Preview course.
        """
        course_item: CoursesLWI = self.__courses_wgt.currentItem()
        if course_item:
            if not course_item.course:
                abs_path = course_item.abs_course_path
                for course in self.loaded_courses:  # Check in loaded courses
                    if course.abs_course_path == abs_path:
                        course_item.course = course
                if not course_item.course:  # Load course
                    course_item.course = Course.from_file(abs_path)
                    self.loaded_courses.append(course_item.course)

                self.__set_initial_proof_states(course_item.course)
            self.set_preview(course_item.course)

    def give_focus_to_course_wdg(self):
        """
        Give the focus to the course list. This should be called after any
        action that gives focus to another part of the window. It allows usr
        to select course with the keyboard's arrows.
        """
        self.__courses_wgt.setFocus()
        if self.__current_item:
            self.__courses_wgt.setItemSelected(self.__current_item, True)

    @Slot()
    def current_item_changed(self):
        """
        This is called when the course item changes: the course is selected,
        usr sees the details, and we give focus back to the course list widget.
        """
        self.set_selected_course()
        self.give_focus_to_course_wdg()

    @Slot()
    def show_recent_courses(self, yes=None):
        """
        Select recent courses / preset courses.
        If yes is None then select according to the config settings.
        """
        if yes is None:
            # Show recent courses if settings asks and there are some
            yes = (cvars.get('functionality.show_recent_courses_only') and
                   cvars.get("course.recent_courses", []))
        else:
            cvars.set('functionality.show_recent_courses_only', yes)

        if self.recent_courses_checkbox:
            self.recent_courses_checkbox.setChecked(yes)

        if yes:
            self.__courses_lyt.setCurrentIndex(1)
            self.__courses_wgt = self.__recent_courses_wgt
            title = _("Recent files")

        else:
            self.__courses_lyt.setCurrentIndex(0)
            self.__courses_wgt = self.__preset_courses_wgt
            title = _("Preset files")

        # self.__label_title.setText(title + _(" (double click to select file):"))
        self.__label_title.setText(title + _(":"))
        self.current_item_changed()

    def add_browsed_course(self, course: Course, browsed=False):
        """
        Add the Course course to the list of recent courses
        (self.__recent_courses_wgt) as if usr had chose this course by
        clicking on the 'Browse file' button and browsing files. This is
        useful in the method AbstractCoExChooser.__preset_exercise to
        preset / preview an exercise.

        If browsed is True, then indicate that the course has been browsed.

        :param course: Course to be added to the recent courses list.
        """
        # Add course on top of self.__recent_course_wgt,
        # and set the current corresponding item
        self.__recent_courses_wgt.add_browsed_course(course,
                                                     browsed=browsed)
        yes = cvars.get('functionality.show_recent_courses_only')
        if not yes:
            # Try to select course in preset courses
            in_preset = self.__preset_courses_wgt.set_current_item(course)
            # If fails, switch to recent courses to display course
            if not in_preset:
                self.show_recent_courses(yes=True)

    def set_preview(self, course: Course):
        """
        Set course preview course being previewed given as an argument. See
        AbstractCoExChooser.set_preview docstring. Course metadata is displayed
        in the disclosure triangle by passing them as details in
        super().set_preview. When a course is selected (either by browsing
        course files or clicking on a recent course in
        self.__recent_courses_wgt), the signal course_chosen is emitted with
        the course. It is received in StartExerciseDialog, which then
        instantiates an ExerciseChooser for this course and the view is set to
        the exercise chooser.
        """

        if self.current_course:
            # Save ips of the previous course if any,
            # and reload ips_dict to benefit from
            # potential new ips for the new chosen course
            self.current_course.save_initial_proof_states()

        self.current_course = course

        # Title, subtitle, etc
        title       = course.title
        subtitle    = course.subtitle
        description = course.description

        # Details
        details = course.nice_metadata
        # Remove title, subtitle and description from details
        # TODO: Prevent user for using a 'Path' attribute (in the course
        # file) when writing a course.
        # TODO: Add course path.
        for key in ['title', 'subtitle', 'description']:
            if key in details:
                details.pop(key)

        if not details:  # Set details to None if empty
            details = None

        log.info(course.metadata)
        # print(course.metadata)
        display_constant = course.metadata.get('display')
        # print(display_constant)
        if display_constant:
            PatternInit.pattern_init(display_constant)

        super().set_preview(main_widget=None, title=title, subtitle=subtitle,
                            details=details, description=description,
                            expand_details=False)

        self.course_chosen.emit(course)

    def __set_initial_proof_states(self, course):
        """
        Ask Lean for initial proof states of all exercises.
        Each time some initial proof state is set,
        ServerInterface emit the signal initial_proof_state_set
        which is connected to ExerciseChooser.__check_proof_state_for_preview
        which update exercise preview if initial_proof_state for exercise
        has just been set.
        """
        # Load stored initial proof states
        # log.debug("Setting initial proof states")
        course.load_initial_proof_states()

        # Get missing ips
        exercises = [st for st in course.incomplete_statements
                     if isinstance(st, Exercise)]
        non_exercises = [st for st in course.incomplete_statements
                         if not isinstance(st, Exercise)]
        if exercises or non_exercises:
            log.debug("Asking Lean for initial proof states...")
            # Ask Lean for missing ips
            self.servint.set_statements(course, exercises)
            self.servint.set_statements(course, non_exercises)

        else:
            self.__check_all_statements()  # Save to text file
            if self.servint.request_seq_num == -1:
                # Ask a first request to the Lean server
                # (that speeds up a lot when exercise starts)
                log.debug(f"Launching Lean with {course.statements[0].pretty_name}")
                self.servint.set_statements(course, [course.statements[0]])

    def __check_all_statements(self):
        """
        If all statements have initial proof states, then save a text file.
        """

        saving = cvars.get('course.save_all_statements_to_text_file', True)
        text_format = cvars.get('course.text_file_format', 'utf8')
        if not saving:
            return

        for course in self.loaded_courses:
            ips_complete = course.initial_proofs_complete
            if ips_complete:
                course.save_all_exercises_text(text_format=text_format)

    def find_course(self, abs_course_path):
        course = self.__preset_courses_wgt.find_course(abs_course_path)
        if not course:
            course = self.__recent_courses_wgt.find_course(abs_course_path)
        return course

    #########
    # Slots #
    #########
    @Slot()
    def __browse_courses(self):
        """
        This method is called when the 'Browse courses' button is
        clicked on. It opens a file dialog, the user chooses a
        course-file, a Course object is instantiated and the method
        set_preview is called.
        """

        # FIXME: directory and filter do not work on Linux?!
        directory = cvars.get('others.course_directory',
                              str(cdirs.usr_lean_exercises_dir.resolve()))
        # directory = str(cdirs.home.resolve())
        dialog = QFileDialog(directory=directory)
        if 'SNAP' in environ:
            dialog.setOption(QFileDialog.DontUseNativeDialog)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('*.lean')

        # TODO: Stop using exec_, not recommended by documentation
        if dialog.exec_():
            abs_path = Path(dialog.selectedFiles()[0]).resolve()
            # course_path = cdirs.relative_to_home(path)
            course = self.find_course(abs_path)
            if not course:
                abs_path = self.servint.lean_env.check_file_path(abs_path)
                course = Course.from_file(abs_path)

            if course:
                self.add_browsed_course(course, browsed=True)
            else:
                dialog = QMessageBox()  # title=_('File selector')
                dialog.setWindowTitle(_('File selector') + '— d∃∀duction')
                dialog.setText(_("No file selected!\nSelect a '.lean' file"))
                dialog.setIcon(QMessageBox.Warning)
                dialog.exec_()


class ExerciseChooser(AbstractCoExChooser):
    """
    The exercise chooser. This widget is activated / shown when a course has
    been chosen by usr (signal
    StartExerciseDialog.__course_chooser.course_chosen).
    - The browser area is made of the course's StatementsTreeWidget
      displaying only the exercises (e.g. no theorems/def).
    - The preview area is more complex and depends on the availability of the
    exercise's initial proof state.
      - If initial proof state is not available, the preview is only
        made of the exercise's title, subtitle and description.
        Note the initial proof states of all the exercises should have been
        asked to the Lean server by the course chooser when the course has
        been selected, and when the initial proof state will be received,
        the corresponding signal will trigger the display.
      - If the initial proof state is available, then this goal preview is
      either displayed as:
        - two lists for the math objects and properties and a line edit
          for the target (imitating the appearance of the prover dui) ;
        - or a text with all these pieces of information (this is called
          the text mode and it is toggle with a checkbox).
    """

    # This signal is emitted when an exercise is being previewed. It is
    # received in the instance ofStartExerciseDialog and the Start
    # exercise button is enabled and set to default.
    exercise_previewed = Signal()
    # current_exercise_changed = Signal()

    def __init__(self, course: Course, servint: ServerInterface):
        """
        See AbstractCoExChooser.__init__ docstring. Here, the browser layout is
        only made of the course's StatementsTreeWidget displaying only the
        exercises (e.g. no theorems).

        :param course: The course in which usr chooses an exercise.
        """
        self.course = course
        self.servint = servint
        self.servint.initial_proof_state_set.connect(
            self.__check_proof_state_for_preview)

        browser_layout = QVBoxLayout()

        exercises = course.exercises_including_saved_version()
        exercises_tree = StatementsTreeWidget(exercises,
                                              course.outline,
                                              is_exercise_list=True)
        exercises_tree.resizeColumnToContents(0)

        browser_layout.addWidget(exercises_tree)

        self.__exercises_tree = exercises_tree
        self.__vertical_bar = exercises_tree.verticalScrollBar()
        self.__previous_vertical_value = 0
        self.__vertical_max = -1
        self.__main_widget_lyt    = None
        self.__goal_widget        = None
        self.__text_wgt           = None
        self.__ui_wgt             = None

        self.__vertical_bar.valueChanged.connect(self.__on_scrolling)

        super().__init__(browser_layout)

    def __on_scrolling(self):
        if self.__vertical_max == -1:
            self.__vertical_max = self.__vertical_bar.maximum()
        # print([self.__vertical_bar.value(), self.__vertical_bar.maximum()])
        current_value = self.__vertical_bar.value()
        # if abs(current_value-self.__previous_vertical_value) > 1:
        if self.__vertical_bar.maximum() == 0:
            # print("Adjusting")
            self.__vertical_bar.setRange(0, self.__vertical_max)
            self.__vertical_bar.setValue(self.__previous_vertical_value)
        self.__previous_vertical_value = self.__vertical_bar.value()

    @property
    def __current_item(self):
        item = self.__exercises_tree.currentItem()
        if hasattr(item, 'statement'):
            return item

    @property
    def current_item_changed(self):
        if self.__exercises_tree:
            return self.__exercises_tree.currentItemChanged

    @property
    def exercise(self):
        if self.__exercises_tree:
            item = self.__exercises_tree.currentItem()
            if isinstance(item, StatementsTreeWidgetItem):
                exercise = item.statement
                return exercise

    def goto_exercise(self, exercise=None):
        self.__exercises_tree.goto_statement(exercise)

    def give_focus_to_exercises_wdg(self):
        self.__exercises_tree.setFocus()
        if not self.__current_item:
            self.goto_exercise()  # Go to first exercise

        self.__exercises_tree.setItemSelected(self.__current_item, True)

    def show_statements(self, statements, yes=True):
        """
        Show or hide all the provided statements. Based on item_from_statement.
        """
        tree_widget = self.__exercises_tree
        tree_widget.hide_statements(statements, not yes)
        tree_widget.setColumnCount(2 if yes else 1)

    def exercises_tree_double_clicked_connect(self, slot):
        self.__exercises_tree.itemDoubleClicked.connect(slot)

    def give_focus_to_exercises_tree(self):
        self.__exercises_tree.setFocus()

    def selected_exercise_is_from_history_file(self):
        exercise = self.exercise
        if exercise:
            return exercise.history_date()

    def preview_exercise(self):
        """
        Set exercise preview. See AbstractCoExChooser.set_preview
        docstring. The exercise's title, subtitle and description are
        displayed; if a preview is available (i.e. exercise.initial_proof_state
        is not None), it is displayed ; if not, Lean server is asked for the
        missing information. This method manages these two possibilities
        with a big if / else condition.

        :param exercise: The exercise to be previewed.
        """

        main_widget     = QWidget()
        main_widget_lyt = QVBoxLayout()
        main_widget_lyt.setContentsMargins(0, 0, 0, 0)

        exercise = self.exercise
        if not exercise:
            return

        if exercise.initial_proof_state:

            btns_lyt = QHBoxLayout()
            main_widget_lyt.setContentsMargins(0, 0, 0, 0)

            # Create goal widget and Toggle text mode if needed
            self.__goal_widget = self.create_widget()
            text_mode = cvars.get('display.text_mode_in_chooser_window', False)
            self.__goal_widget.text_mode_checkbox.setChecked(text_mode)

            main_widget_lyt.addWidget(self.__goal_widget)
            main_widget_lyt.addStretch()  # -> check box at bottom
            main_widget_lyt.addLayout(btns_lyt)
            self.__main_widget_lyt = main_widget_lyt
        else:
            # Try to get preview with high priority:
            exercise_ = (exercise if not exercise.original_exercise
                         else exercise.original_exercise)
            self.servint.set_statements(exercise.course,
                                        [exercise_],
                                        on_top=True)
            widget_lbl = QTextEdit(_('Preview not available (be patient...)'))
            widget_lbl.setStyleSheet('color: gray;')

            main_widget_lyt.addWidget(widget_lbl)

        main_widget.setLayout(main_widget_lyt)

        # ───────────────────── Others ───────────────────── #

        title = exercise.pretty_name
        if exercise.history_date():
            title += " " + _("(saved proof)")

        description = exercise.complete_description

        # vertical_value = self.__vertical_bar.value()
        # vertical_max = self.vertical_bar.maximum()
        super().set_preview(main_widget=main_widget, title=title,
                            subtitle=None, details=None,
                            description=description, expand_details=False)
        # self.vertical_bar.setRange(0, vertical_max)
        # self.vertical_bar.setValue(vertical_value)
        # print(f"Setting to max = {vertical_max}, value = {vertical_value}")

        # self.exercise_previewed.emit()

    def create_widget(self):
        """
        This method creates the goal widget, which will be either a
        __text_wgt, with exercise's content displayed as a text, or a __ui_wgt,
        with content displayed as it will be in the prover UI.
        The widget is actually created only at first call.
        """
        # Logical data
        exercise = self.exercise
        proof_state = exercise.initial_proof_state
        goal = proof_state.goals[0]  # Only one goal

        open_problem = exercise.is_open_question
        to_prove = not exercise.is_complete_statement

        return GoalWidget(goal=goal,
                          to_prove=to_prove,
                          open_problem=open_problem,
                          display_empty_context=True,
                          apply_statement=False)

    @Slot()
    def __check_proof_state_for_preview(self):
        if self.exercise and self.exercise.initial_proof_state:
            log.debug("Lean initial proof state received, updating preview")
            self.preview_exercise()
        self.__exercises_tree.update_tooltips()


class AbstractStartCoEx(QDialog):
    """
    The base class course and exercise chooser (inherits QDialog); it is
    inherited by StartCoExStartup (hisotrically alslso by
    StartCoExExerciseFinished).

    AbstractStartCoEx is divided in two main sub-widgets
    (presented in a QTabWidget): the course chooser
    (self.__course_chooser) and the exercise chooser
    (self.__exercise_chooser), see those choosers docstrings. At first,
    only the course chooser is enabled: usr browses courses. When usr
    selects a course, the course is previewed by calling the method
    self.__course_choser.set_preview, with the course as argument. An
    ExerciseChooser object is instanciated (self.__exercise_chooser) in
    a new tab and usr browses exercises.  When usr clicks on an
    exercise, this exercise is kept as is previewed by calling
    self.__exercise_chooser.set_preview with the exercise as argument
    (and the exercise is kept in self.__exercise_chooser.exercise,
    accessible with a property).  Once usr confirms their choice of
    exercice, they click on the 'Start exercise' button, which closes
    the dialog and sends a signal to launch the exercice main window.

    This class also has a __preset_exercise method allowing to preset /
    preview a given exercise (see its docstring for specifics).

    The communication between this class, the two choosers and the rest
    of the program can be tricky and the actual solution is
    not-so-elegant; enhancements encouraged and welcome. For example,
    the 'Start exercise' button is not always enabled. At init, it is
    disabled and it is enabled when the user clicks on an exercise item
    in self.__exercise_chooser and the signal
    self.__exercise_chooser.exercise_previewed is emitted.
    """

    exercise_chosen = Signal(Exercise)
    window_closed = Signal()
    quit_deaduction = Signal()

    def __init__(self, title: Optional[str], widget: Optional[QWidget],
                 exercise: Optional[Exercise],
                 servint: ServerInterface = None):
        """
        Init self by setting up the layouts, the buttons and the tab
        widget (see self docstring). 

        :param title: Optional window title.
        :param widget: Optional QWidget to be displayed on top of the
            CoEx chooser (e.g. a congratulations widget in
            StartCoExExerciseFinished).
        :param exercise: Optional Exercise to be preset / previewed
            (e.g. finished exercise in StartCoExExerciseFinished).
        :param servint: ServerInterface to get exercises' initial proof states.
        """

        super().__init__()

        # Init dict statement --> item
        StatementsTreeWidgetItem.from_lean_name = {}

        self.exercise_chooser_from_course_path = dict()
        self.servint = servint

        settings = QSettings("deaduction")
        geometry = settings.value("coex_chooser/Geometry")
        if geometry:
            self.restoreGeometry(geometry)

        self.toolbar = QToolBar()
        self.__init_toolbar()

        if title:
            self.setWindowTitle(title)
        self.setMinimumWidth(450)
        self.setMinimumHeight(550)

        yes = False if exercise else True
        self.__course_chooser = CourseChooser(servint, select_first_item=yes)
        self.__course_chooser.recent_courses_checkbox = self.__recent_courses_action
        recent_courses = self.__course_chooser.current_index
        self.__recent_courses_action.setChecked(recent_courses)
        self.__exercise_chooser = QWidget()

        # Somehow the order of connections changes performances?
        self.__course_chooser.goto_exercises.connect(self.__goto_exercises)
        self.__course_chooser.course_chosen.connect(self.__preview_exercises)

        # ───────────────────── Buttons ──────────────────── #

        self.__quit_btn     = QPushButton(_('Quit'))
        self.__quit_btn.setAutoDefault(False)
        self.__start_ex_btn = QPushButton(_('Start exercise'))

        self.__start_ex_btn.setEnabled(False)

        self.__quit_btn.clicked.connect(self.quit_deaduction)
        self.__start_ex_btn.clicked.connect(self.__start_exercise)
        self.disable_start_btn = None

        # ───────────────────── Layouts ──────────────────── #
        self.__tabwidget = QTabWidget()
        self.__tabwidget.addTab(self.__course_chooser, _('Files'))
        self.__tabwidget.addTab(self.__exercise_chooser, _('Exercises'))
        self.__tabwidget.currentChanged.connect(self.__current_tab_changed)

        buttons_lyt = QHBoxLayout()
        buttons_lyt.addWidget(self.__quit_btn)
        buttons_lyt.addStretch()
        buttons_lyt.addWidget(self.__start_ex_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.toolbar)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        # main_layout.addWidget(separator)
        # # FIXME: put this in the right place
        # explanation = _("First select a course, then choose "
        #                                "an exercise.")
        # explanation_widget= QLabel(explanation)
        # main_layout.addWidget(explanation_widget)
        if widget:
            main_layout.addWidget(widget)
        main_layout.addWidget(self.__tabwidget)
        # main_layout.addLayout(history_buttons_lyt)
        main_layout.addLayout(buttons_lyt)

        self.setLayout(main_layout)

        # ───────────────────── Others ───────────────────── #
        self.__enter_shortcut = QShortcut(QKeySequence(Qt.Key_Return),
                                          self.__course_chooser)
        self.__enter_shortcut.activated.connect(self.__goto_exercises)

        self.__tabwidget.setTabEnabled(1, False)

        # show_history = cvars.get('display.show_saved_exercises')
        # self.__history_checkbox.setChecked(show_history)

        if exercise:
            self.__preset_exercise(exercise)
            self.__enter_shortcut.setEnabled(False)
            self.__toggle_history()
            self.__exercise_chooser.give_focus_to_exercises_wdg()
        else:
            self.__enter_shortcut.setEnabled(True)
            self.__course_chooser.set_selected_course()
            self.__course_chooser.give_focus_to_course_wdg()

        if not self.__show_history_action.isChecked():
            self.__delete_history_action.setDisabled(True)

    # def keyPressEvent(self, event) -> None:
    #     print(event.key, event.type)

    def __init_toolbar(self):
        icons_base_dir = cvars.get("icons.path")
        icons_dir = fs.path_helper(icons_base_dir)

        # Tab action
        self.__change_tab_action = QAction("Change tab")
        self.__change_tab_action.setShortcut(QKeySequence.NextChild)
        self.__change_tab_action.triggered.connect(self.change_tab)

        # Courses actions
        self.__recent_courses_action = QAction(
            QIcon(str((icons_dir / 'icons8-history-folder-96.png').resolve())),
            _('Show only recent files'), self)
        self.__recent_courses_action.setCheckable(True)
        show_recent_courses = cvars.get('functionality.show_recent_courses_only')
        self.__recent_courses_action.setChecked(show_recent_courses)

        # Exercises actions
        self.__show_history_action = QAction(
            QIcon(str((icons_dir / 'icons8-save-96.png').resolve())),
            _("Show saved proofs"), self)
        self.__show_history_action.setCheckable(True)
        show_history = cvars.get('display.show_saved_exercises')
        self.__show_history_action.setChecked(show_history)

        self.__delete_history_action = QAction(
            QIcon(str((icons_dir / 'icons8-delete-96.png').resolve())),
            _("Delete saved proofs"), self)
        self.__delete_history_action.setShortcut(QKeySequence.Delete)

        self.toolbar.addAction(self.__recent_courses_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.__delete_history_action)
        self.toolbar.addAction(self.__show_history_action)

        # Connect signals:
        self.__show_history_action.triggered.connect(self.__toggle_history)
        self.__delete_history_action.triggered.connect(self.__delete_history)
        self.__recent_courses_action.triggered.connect(
            self.__show_recent_courses)

    # def show(self):
    #     if self.course:
    #         self.__toggle_history()
    #     super().show()

    @Slot()
    def change_tab(self):
        tab = self.__tabwidget
        tab.setCurrentIndex(1 - tab.currentIndex())

    def closeEvent(self, event: QEvent):
        """
        Overload native Qt closeEvent method — which is called when self
        is closed — to send the signal self.window_closed.

        :param event: Some Qt mandatory thing.
        """
        if self.__course_chooser.current_course:
            # Save ips of the previous course if any
            self.__course_chooser.current_course.save_initial_proof_states()

        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("coex_chooser/isMaximised", self.isMaximized())
        self.showNormal()
        settings.setValue("coex_chooser/Geometry", self.saveGeometry())

        self.window_closed.emit()
        super().closeEvent(event)
        # super().closeEvent(event)
        # self.deleteLater()

    @property
    def course(self):
        if self.__course_chooser:
            return self.__course_chooser.current_course

    @property
    def exercise(self):
        if self.__exercise_chooser:
            return self.__exercise_chooser.exercise

    def __preset_exercise(self, exercise: Exercise):
        """
        Preset / preview the Exercise exercise as if usr had chose
        exercise.course and then previewed exercise by clicking on it.
        This is useful in StartCoExExerciseFinished to display the
        exercise that was just finished by usr. On top of previewing
        exercise and its course, usr's clicks are emulated by adding the
        Course as a browsed course in
        self.__course_chooser.__recent_courses_wgt and selecting the
        exercise in self.__exercise_chooser.__exercises_tree. The code
        for this is not very smart so if you want to enhance it, do it
        (see CONTRIBUTING.md file).
        """
        if self.course is not exercise.course:
            self.__course_chooser.set_preview(exercise.course)

        self.__course_chooser.add_browsed_course(exercise.course)
        yes = cvars.get('functionality.show_recent_courses_only')
        self.__recent_courses_action.setChecked(yes)

        self.__preview_exercises(self.course)  # Init __exercise_choser
        self.__exercise_chooser.goto_exercise(exercise)
        self.__exercise_chooser.preview_exercise()
        self.__toggle_history()
        self.__goto_exercises()

    #########
    # Slots #
    #########
    @Slot()
    def __show_recent_courses(self):
        yes = self.__recent_courses_action.isChecked()
        self.__course_chooser.show_recent_courses(yes)

    @Slot()
    def __toggle_history(self):
        """
        Show or hide all saved versions according to bool yes.
        """

        show_history = self.__show_history_action.isChecked()
        cvars.set('display.show_saved_exercises', show_history)
        history_versions = self.course.saved_exercises_in_history_course()
        # tree_widget = self.__exercises_tree
        # tree_widget.hide_statements(history_versions, not yes)
        # tree_widget.setColumnCount(2 if yes else 1)
        ex_chooser = self.__exercise_chooser
        if isinstance(ex_chooser, ExerciseChooser):
            # Hide / show history exercises
            ex_chooser.show_statements(history_versions, show_history)
            if ((not show_history) and self.exercise
                    and self.exercise.original_exercise):
                ex_chooser.goto_exercise(self.exercise.original_exercise)

        if self.course:
            # is_history = bool(self.exercise.history_date())
            freeze = not show_history  # and is_history)
        else:
            freeze = True
        self.__delete_history_action.setDisabled(freeze)
        if isinstance(ex_chooser, ExerciseChooser):
            ex_chooser.give_focus_to_exercises_wdg()

    @Slot()
    def emw_not_ready(self):
        """
        Called when emw is frozen, waiting for a new proof state. Start
        button is disabled to avoid collision of exercises.
        """

        self.disable_start_btn = True
        self.__start_ex_btn.setEnabled(False)
        self.__start_ex_btn.setDefault(False)

    @Slot()
    def emw_ready(self):
        """
        Called when emw is unfrozen. Start button is disabled if an exercise
        is set.
        """
        self.disable_start_btn = False
        self.__enable_start_ex_btn()

    @Slot()
    def __enable_start_ex_btn(self):
        """
        This method is called when an exercise item is clicked on in the
        exercise chooser and therefore is being previewed.  Its goal is
        to enable the 'Start exercise' button which may have been
        disabled until then. The corresponding signal is
        self.__exercise_chooser.exercise_previewed. However note that it
        is not connected in self.__init__. Indeed, when self is
        instanciated, self.__exercise_chooser is a simple QWidget and
        not an instance of ExerciseChooser. Consequently,
        exercise_previewed is at this stage *not* an attribute of
        self.__exercise_chooser. So the signal is connected in
        __preview_exercises once self.__exercise_chooser has been set to
        an ExerciseChooser object.
        """

        if self.__exercise_chooser and self.__exercise_chooser.exercise and \
                not self.disable_start_btn:
            start_btn = self.__start_ex_btn
            if not self.exercises_tab_is_selected:
                start_btn.setEnabled(False)
            else:
                start_btn.setEnabled(True)
            start_btn.setDefault(True)
            if self.__exercise_chooser.selected_exercise_is_from_history_file():
                start_btn.setText(_('Load proof'))
            else:
                start_btn.setText(_('Start exercise'))

        # start_btn = self.__start_ex_btn
        # if self.courses_tab_is_selected:
        #     start_btn.setText(_('Select file'))
        # elif self.exercises_tab_is_selected:
        #     if self.__exercise_chooser.selected_exercise_is_from_history_file():
        #         start_btn.setText(_('Load history'))
        #     else:
        #         start_btn.setText(_('Start exercise'))
        #
        # start_btn.setEnabled(True)

    @property
    def exercises_tab_is_selected(self):
        return self.__exercise_chooser and self.__tabwidget.currentIndex() == 1
    
    @property
    def courses_tab_is_selected(self):
        return self.__tabwidget.currentIndex() == 0

    @property
    def exercises_tab_is_selected(self):
        return self.__tabwidget.currentIndex() == 1

    @Slot()
    def __current_tab_changed(self):
        """
        This method is called when usr select a tab, i.e. files or exercises.
        """
        if self.courses_tab_is_selected:
            # ex_chooser = self.__exercise_chooser
            # log.debug('Course tab')
            self.__start_ex_btn.setEnabled(False)
            self.__course_chooser.give_focus_to_course_wdg()
            self.__enter_shortcut.setEnabled(True)
            # self.__course_chooser.set_selected_recent_course()
        else:
            # self.__preview_exercises(self.course)
            # log.debug('Ex tab')
            # log.debug(self.__tabwidget.currentIndex())
            self.__enter_shortcut.setEnabled(False)
            self.__enable_start_ex_btn()
            self.__exercise_chooser.give_focus_to_exercises_wdg()

    @Slot()
    def __goto_exercises(self):
        """
        Go to the exercise tab.
        """
        if self.__tabwidget.isTabEnabled(1):
            self.__tabwidget.setCurrentIndex(1)

    def __goto_courses(self):
        """
        Go to the file tab.
        """
        self.__tabwidget.setCurrentIndex(0)

    def get_exercise_chooser_from_course(self, course):
        """
        Serach in the exercise_chooser_from_course_path dict if an
        ExerciseChooser has already been set up for course.
            - If so, return it;
            - if not, create a new one.
        """

        ec_dic = self.exercise_chooser_from_course_path
        course_path = course.abs_course_path
        exercise_chooser = ec_dic.get(course_path)
        if not exercise_chooser:
            exercise_chooser = ExerciseChooser(course, self.servint)
            ec_dic[course_path] = exercise_chooser
        return exercise_chooser

    @Slot(Course, str)
    def __preview_exercises(self, course: Course):
        """
        This method is called when the user chose a course and the
        signal self.__course_chooser.course_chosen is emitted. It
        instantiates an ExerciseChooser object for the corresponding
        course, puts it in the second tab and activates the tab.
        Furthermore, this method connects the signal
        self.__exercise_chooser.exercise_previewed to the slot
        self.__enable_start_ex_btn (see __enable_start_ex_btn for the
        why).

        :param course: The instance of the Course class the user just chose.
        """

        self.__start_ex_btn.setEnabled(False)

        # Tab 0 is course, 1 is exercise
        # self.__exercise_chooser = ExerciseChooser(course, self.servint)
        self.__exercise_chooser = self.get_exercise_chooser_from_course(course)
        self.__tabwidget.removeTab(1)
        self.__tabwidget.addTab(self.__exercise_chooser, _('Exercises'))
        self.__tabwidget.setTabEnabled(1, True)

        self.__exercise_chooser.current_item_changed.connect(
            self.__current_exercise_changed)
        self.__exercise_chooser.exercise_previewed.connect(
                self.__enable_start_ex_btn)
        self.__exercise_chooser.exercises_tree_double_clicked_connect(
            self.__process_double_click)

        self.__toggle_history()

    @Slot()
    def __current_exercise_changed(self):
        exercise = self.exercise
        if exercise:
            self.__exercise_chooser.preview_exercise()

        freeze = not self.__show_history_action.isChecked()
        # is_history = bool(exercise.history_date())
        # freeze = not yes  # and is_history)
        # else:
        #     freeze = True
        self.__delete_history_action.setDisabled(freeze)

    @Slot()
    def __delete_history(self):

        exercise = self.exercise

        #######################
        # Warning message box #
        #######################
        yes_no_dialog = YesNoDialog()
        # (1st case) Delete all saved proofs for 1 file!
        if not exercise:
            yes_no_dialog.setWindowTitle(_('Deleting all saved proofs?'))
            yes_no_dialog.setIcon(QMessageBox.Warning)
            yes_no_dialog.setText(_("This will delete ALL saved proofs for "
                                    "this file. Are you sure about this?"))
        # (2nd case) Delete all saved proofs for 1 exercise!
        elif not exercise.history_date():
            yes_no_dialog.setWindowTitle(_('Deleting all saved proofs'))
            yes_no_dialog.setIcon(QMessageBox.Warning)
            yes_no_dialog.setText(_("This will delete ALL saved proofs for "
                                    "this exercise. Are you sure about this?"))
        # (3rd case) Delete one saved proof
        else:
            yes_no_dialog.setWindowTitle(_('Deleting a saved proof'))
            yes_no_dialog.setText(_("Do you want to delete this saved proof?"))

        yes_no_dialog.exec_()
        if yes_no_dialog.no:
            # log.debug('no')
            return

        ##############################
        # Delete, and handle display #
        ##############################
        # (1st case) Delete all saved proofs for 1 file!
        if not exercise:
            log.info("Deleting saved proof file")
            course = self.course
            course.delete_history_file()
            self.course.set_history_course()
            exercise_to_display = None

        # (2nd case) Delete all saved proofs for 1 exercise!
        elif not exercise.history_date():
            log.info("Deleting all saved proofs for this exercise")
            course = self.course
            course.delete_all_saved_proofs_of_exercise(exercise)
            exercise_to_display = exercise
        # (3rd case) Delete one saved proof
        else:
            log.info("Deleting this saved proof")
            exercise_to_display = exercise.next_exercise()
            exercise.delete_in_history_file()

        # Reset history course since file has changed
        # FIXME:
        self.exercise_chooser_from_course_path.pop(self.course.abs_course_path)
        self.course.set_history_course()
        self.__preview_exercises(self.course)
        if exercise_to_display:
            self.__exercise_chooser.goto_exercise(exercise_to_display)
            self.__exercise_chooser.preview_exercise()
            self.__goto_exercises()
        else:
            self.__goto_courses()

    @Slot()
    def __process_double_click(self, tree_item):
        if isinstance(tree_item, StatementsTreeWidgetItem):
            self.__start_ex_btn.animateClick()

    @Slot()
    def __start_exercise(self):
        """
        This method is called when the user clicks on the 'Start
        exercise' button. It adds the corresponding course to the recent
        courses list if needed, emits the signal self.exercise_chosen
        (see self docstring) and closes the dialog.
        """

        exercise = self.__exercise_chooser.exercise
        # FIXME:
        if (self.course.abs_course_path in
                self.exercise_chooser_from_course_path):
            self.exercise_chooser_from_course_path.pop(
                self.course.abs_course_path)

        # (1) Check if exercise is from history file
        if exercise.history_date():
            # Back to original, incorporating auto_steps
            exercise = exercise.from_history_exercise()
            exercise.launch_in_history_mode = True
        else:
            exercise.launch_in_history_mode = False
            # check if exercise must be negated (e.g. is an open question)
            # TODO: this should be moved elsewhere, e.g. in __main__
            if not check_negate_statement(exercise):
                return

        # Save course_path, title, and exercise number
        # in user_config's previous_courses_list
        # TODO: Rename the list recent_courses_list?
        # course_type = exercise.course.filetype
        course      = exercise.course
        statements = course.statements
        exercise_nb = (statements.index(exercise) if exercise in statements
                       else -1)
        add_to_recent_courses(course.abs_course_path, course.title,
                              exercise_nb)

        # Send exercise_chosen signal and close dialog
        self.exercise_chosen.emit(exercise)
        # Moved to __main__.WindowManager:
        # # log.debug("Exercise chosen, closing window")
        # self.close()  # Fuck you and I'll see you tomorrow!


class StartCoExStartup(AbstractStartCoEx):
    """
    The CoEx chooser when starting up d∃∀duction (see
    AbstractStartCoEx docstring) This is the first widget
    activated / shown when launching d∃∀duction as it is the one which
    allows the user to:
    1. choose a course (from a file or from recent courses' list);
    2. browse / preview the exercises for the chosen course;
    3. start the chosen exercise (launch the ExerciseMainWindow).

    This class is to be instanciated in deaduction.dui.__main__.py. The
    dialog is opened with QDialog.open and qtrio waits for the signal
    self.exercise_chosen to be emitted with the corresponding exercise.
    Once it is done, the program proceeds on launching the main exercise
    window.
    """

    def __init__(self, exercise: Exercise = None, servint=None):
        """
        Init self.
        """
        log.debug("Starting chooser window")
        title = _('Choose file and exercise — d∃∀duction')
        super().__init__(title=title,
                         widget=None,
                         exercise=exercise,
                         servint=servint)

        QTimer.singleShot(0, self.__show_intro)

    def __show_intro(self):
        text = None
        cname = "dialogs.chooser_intro"
        cname2 = "dialogs.chooser_intro_2"
        if cvars.get(cname):
            config_name = cname
            text = _("Welcome to the d∃∀duction file and exercise selector. "
                     "Select a file in the 'Files' tab, then select your "
                     "exercise in the 'Exercises' tab.")

        elif cvars.get(cname2):
            config_name = cname2
            text = _("Use the toolbar to display recent files and saved "
                     "exercises.")
        if text:
            calc_intro_box = DeaductionTutorialDialog(config_name=config_name,
                                                      text=text, parent=self)
            calc_intro_box.exec()

def check_negate_statement(exercise) -> bool:
    """
    If needed, ask the user to choose between proving the statement
    or its negation. Change the attribute exercise.negate_statement
    accordingly.

    :param exercise: Exercise.
    :return: True if choice has been made, else False.
    """
    # TODO: this should be moved elsewhere, e.g. in a separate module.

    ok = True  # default value
    open_question = exercise.info.setdefault('open_question', False)
    if exercise.info.get('negate_statement', False):
        exercise.negate_statement = True
    elif open_question:
        # exercise is an open question and user has to choose her way
        # if exercise.lean_variables:
        #     log.warning("Exercise is an open question but has variables:"
        #                 "negation will not be correct!!")

        title = _("True or False?")
        if exercise.initial_proof_state:
            goal = exercise.initial_proof_state.goals[0]
            ask = _("Do you want to prove this statement or its negation?")
            output = goal.goal_to_text(text_mode=False, to_prove=False)
            # output = ask + "\n \n" + output + "\n"
        else:
            ask = ""
            output = exercise.lean_variables + "   " \
                     + exercise.lean_core_statement
        choices = [("1", _("Prove statement")),
                   ("2", _("Prove negation"))]
        choice, ok2 = ButtonsDialog.get_item(choices,
                                             title,
                                             output_math=output,
                                             output_text=ask)
        if ok2:
            exercise.negate_statement = (choice == 1)
        else:  # Cancel exercise if no choice
            ok = False
    return ok


if __name__ == '__main__':
    app = QApplication()

    # Test StartCoExStartup
    start_coex_dialog_startup = StartCoExStartup()
    start_coex_dialog_startup.show()

    # Test StartCoExExerciseFinished
    # course_path = Path('../../../../../tests/lean_files/courses/' \
    #                    'exercices_logique_propositionnelle.pkl')
    # course = Course.from_file(course_path)
    # finished_exercise = course.exercises_list()[0]
    #
    # start_coex_dialog_exercise_finished = StartCoExExerciseFinished(finished_exercise)
    # start_coex_dialog_exercise_finished.show()

    sys.exit(app.exec_())
