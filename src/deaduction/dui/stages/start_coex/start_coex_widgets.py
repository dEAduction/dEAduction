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
import logging
from functools import partial
from pathlib import   Path
from typing  import  (Dict,
                      Optional)

from PySide2.QtCore    import (Qt,
                               Signal,
                               Slot,
                               QEvent,
                               QSettings)
from PySide2.QtGui     import (QFont,
                               QFontMetrics,
                               QPixmap)
from PySide2.QtWidgets import (QApplication,
                               QCheckBox,
                               QDialog,
                               QFileDialog,
                               QHBoxLayout,
                               QLabel,
                               QLayout,
                               QLineEdit,
                               QSpacerItem,
                               QPushButton,
                               QTabWidget,
                               QTextEdit,
                               QVBoxLayout,
                               QWidget)

import deaduction.pylib.config.vars  as     cvars
import deaduction.pylib.config.dirs  as     cdirs
from deaduction.dui.primitives      import (DisclosureTriangle,
                                            ButtonsDialog,
                                            MathTextWidget)
from deaduction.dui.elements        import (MathObjectWidget,
                                            TargetLabel,
                                            RecentCoursesLW,
                                            RecentCoursesLWI,
                                            StatementsTreeWidget,
                                            StatementsTreeWidgetItem)

from deaduction.dui.elements.start_coex_widget_classes import ChooseExerciseWidgetItem

from deaduction.dui.utils           import (replace_widget_layout,
                                            HorizontalLine)
from deaduction.pylib.config.course import  add_to_recent_courses
from deaduction.pylib.coursedata    import (Course,
                                            Exercise)
from deaduction.pylib.math_display.pattern_init import pattern_init
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

        self.__preview_wgt = QLabel(_('No preview yet.'))
        self.__preview_wgt.setStyleSheet('color: gray;')
        spacer1             = QSpacerItem(1, 5)
        spacer2             = QSpacerItem(1, 5)
        self.__main_layout = QVBoxLayout()
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
            description_wgt.setWordWrap(True)
            layout.addWidget(description_wgt)
        if details:
            details_wgt = DisclosureTriangle(_('Details:'), details)
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
    goto_exercise = Signal()

    def __init__(self, servint):
        """
        See AbstractCoExChooser.__init__ docstring. Here, the browser
        layout is made of a browse-button to browse courses files
        and a QListWidget displayling recent courses.
        """

        self.current_course = None  # Useful to save initial proof states

        self.servint: ServerInterface = servint

        # Browse button
        self.__browse_btn = QPushButton(_('Browse files...'))
        self.__browse_btn.setAutoDefault(False)
        self.__browse_btn.clicked.connect(self.__browse_courses)

        # Recent courses widget
        self.__recent_courses_wgt = RecentCoursesLW()
        browser_layout = QVBoxLayout()
        browser_layout.addWidget(self.__browse_btn)
        label_title = QLabel(_("Recent files") + _(":"))
        browser_layout.addWidget(label_title)
        browser_layout.addWidget(self.__recent_courses_wgt)

        # Signals
        self.__recent_courses_wgt.currentItemChanged.connect(
            self.current_item_changed)
        self.__recent_courses_wgt.itemDoubleClicked.connect(
                lambda x: self.goto_exercise.emit())

        super().__init__(browser_layout)

    def current_item_changed(self):
        course_item = self.__recent_courses_wgt.currentItem()
        course_path = course_item.course_path
        course = Course.from_file(course_path)
        self.__set_initial_proof_states(course)
        self.set_preview(course)

    def add_browsed_course(self, course: Course):
        """
        Add the Course course to the list of recent courses
        (self.__recent_courses_wgt) as if usr had chose this course by
        clicking on the 'Browse file' button and browsing files. This is
        useful in the method AbstractCoExChooser.__preset_exercise to
        preset / preview an exercise.

        :param course: Course to be added to the recent courses list.
        """

        course_path  = course.relative_course_path
        course_title = course.title
        self.__recent_courses_wgt.add_browsed_course(course_path, course_title)

    def set_preview(self, course: Course):
        """
        Set course preview course being previewed given as an argument. See
        AbstractCoExChooser.set_preview docstring. Course metadata is displayed
        in the disclosure triangle by passing them as details in
        super().set_preview. When a course is selected (either by browsing
        course files or clicking on a recent course in
        self.__recent_courses_wgt), the signal course_chosen is emitted with
        the course. It is received in StartExerciseDialog, which then
        instanciates an ExerciseChooser for this course and the view is set to
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
            pattern_init(display_constant)

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
        remaining_statements = [st for st in course.statements if not
                                st.initial_proof_state]
        exercises = [st for st in remaining_statements
                     if isinstance(st, Exercise)]
        non_exercises = [st for st in remaining_statements
                         if not isinstance(st, Exercise)]
        if exercises or non_exercises:
            log.debug("Asking Lean for initial proof states...")
            # Ask Lean for missing ips
            self.servint.set_statements(course, exercises)
            self.servint.set_statements(course, non_exercises)

        elif self.servint.request_seq_num == -1:
            # Ask a first request to the Lean server
            # (that speeds up a lot when exercise starts)
            log.debug(f"Launching Lean with {course.statements[0].pretty_name}")
            self.servint.set_statements(course, [course.statements[0]])

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
        directory = cvars.get('others.course_directory',
                              str(cdirs.usr_lean_exercises_dir))
        dialog = QFileDialog(directory=directory)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('*.lean')
        # dialog.setNameFilter('*.lean *.pkl')

        # TODO: Stop using exec_, not recommended by documentation
        if dialog.exec_():
            course_path = Path(dialog.selectedFiles()[0])
            course = Course.from_file(course_path)

            title = course.title
            self.__recent_courses_wgt.add_browsed_course(course_path, title)
            self.__set_initial_proof_states(course)
            self.set_preview(course)


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

    def __init__(self, course: Course, servint: ServerInterface):
        """
        See AbstractCoExChooser.__init__ docstring. Here, the browser layout is
        only made of the course's StatementsTreeWidget displaying only the
        exercises (e.g. no theorems).

        :param course: The course in which usr chooses an exercise.
        """
        self.course = course
        self.servint = servint

        self.__exercise = None
        browser_layout = QVBoxLayout()
        # exercises = course.exercises
        # saved_exercises = course.saved_exercises_in_history_course()
        # history_course = course.history_course(course)
        # if history_course:
        #     history_exercises = history_course.exercises
        #     if history_exercises:
        #         exercises = history_exercises

        exercises = course.exercises_including_saved_version()
        exercises_tree = StatementsTreeWidget(exercises,
                                              course.outline,
                                              is_exercise_list=True)

        exercises_tree.resizeColumnToContents(0)
        browser_layout.addWidget(exercises_tree)

        exercises_tree.currentItemChanged.connect(self.current_item_changed)

        self.__exercises_tree = exercises_tree
        self.__text_mode_checkbox = None
        self.__main_widget_lyt    = None
        self.__goal_widget        = None
        self.__text_wgt           = None
        self.__ui_wgt             = None

        self.__scrollbar_current_item_pos = 0

        # Load fonts for math widgets
        # self.deaduction_fonts = DeaductionFonts(self)
        # font_size = self.deaduction_fonts.chooser_math_font_size
        # self.math_fonts = self.deaduction_fonts.math_fonts
        # self.math_fonts.setPointSize(font_size)

        super().__init__(browser_layout)

    def current_item_changed(self):
        item = self.__exercises_tree.currentItem()
        if isinstance(item, StatementsTreeWidgetItem):
            exercise = item.statement
            self.set_preview(exercise)

    def exercises_tree_double_clicked_connect(self, slot):
        self.__exercises_tree.itemDoubleClicked.connect(slot)

    def set_preview(self, exercise: Exercise):
        """
        Set exercise preview. See AbstractCoExChooser.set_preview
        docstring. The exercise's title, subtitle and description are
        displayed; if a preview is available (i.e. exercise.initial_proof_state
        is not None), it is displayed ; if not, Lean server is asked for the
        missing information. This method manages these two possibilities
        with a big if / else condition.

        :param exercise: The exercise to be previewed.
        """

        self.__exercise = exercise
        main_widget     = QWidget()
        main_widget_lyt = QVBoxLayout()
        main_widget_lyt.setContentsMargins(0, 0, 0, 0)

        # with_preview = exercise.course.filetype == '.pkl'
        # TODO: in case no initial ps, do the same thing except the text,
        #  so that the window does not resize.
        #  When Lean's answer comes, just call a fonction that changes the
        #  text.

        if exercise.initial_proof_state:

            # Checkbox
            self.__text_mode_checkbox = QCheckBox(_('Text mode'))
            self.__text_mode_checkbox.clicked.connect(self.toggle_text_mode)
            cb_lyt = QHBoxLayout()
            cb_lyt.addStretch()
            cb_lyt.addWidget(self.__text_mode_checkbox)

            main_widget_lyt.setContentsMargins(0, 0, 0, 0)

            # Toggle text mode if needed
            text_mode = cvars.get('display.text_mode_in_chooser_window', False)
            self.__text_mode_checkbox.setChecked(text_mode)

            # Create goal widget, either in text mode or in deaduction mode,
            # according to self.__text_mode_checkbox.
            self.__goal_widget = self.create_widget()
            main_widget_lyt.addWidget(self.__goal_widget)
            main_widget_lyt.addStretch()  # -> check box at bottom
            main_widget_lyt.addLayout(cb_lyt)
            self.__main_widget_lyt = main_widget_lyt
        else:
            self.servint.initial_proof_state_set.connect(
                                        self.__check_proof_state_for_preview)
            # Try to get preview with high priority:
            self.servint.set_statements(exercise.course,
                                        [exercise],
                                        on_top=True)
            widget_lbl = QTextEdit(_('Preview not available (be patient...)'))
            widget_lbl.setStyleSheet('color: gray;')

            main_widget_lyt.addWidget(widget_lbl)

        main_widget.setLayout(main_widget_lyt)

        # ───────────────────── Others ───────────────────── #

        # TODO: Add subtitle, task…
        title       = exercise.pretty_name
        description = exercise.description

        self.__exercises_tree.goto_statement(exercise)

        super().set_preview(main_widget=main_widget, title=title,
                            subtitle=None, details=None,
                            description=description, expand_details=False)

        self.exercise_previewed.emit()
        # item = self.__exercises_tree.currentItem()
        # self.__exercises_tree.scrollToItem(item)
                               # hint=self.__exercises_tree.PositionAtCenter)

    def create_widget(self):
        """
        This method creates the goal widget, which will be either a
        __text_wgt, with exercise's content displayed as a text, or a __ui_wgt,
        with content displayed as it will be in the prover UI.
        The widget is actually created only at first call.
        """
        # Logical data
        exercise = self.__exercise
        proofstate = exercise.initial_proof_state
        goal = proofstate.goals[0]  # Only one goal

        # ────────────────────── Rest ────────────────────── #
        if self.__text_mode_checkbox.isChecked():
            ###############
            # Text widget #
            ###############
            # The goal is presented in a single widget.
            self.__text_wgt = MathTextWidget()

            self.__text_wgt.setReadOnly(True)
            # self.__text_wgt.setFont(self.math_fonts)
            text = goal.goal_to_text(format_="html",
                                     text_mode=True,
                                     open_problem=exercise.is_open_question)
            self.__text_wgt.setHtml(text)
            widget = self.__text_wgt
        else:
            #############
            # UI widget #
            #############
            # The widget with lists for math. objects and properties
            # and a QLAbel for the target.
            target = goal.target
            objects = goal.context_objects
            properties = goal.context_props

            # ───────────── Objects and properties ───────────── #
            propobj_lyt = QHBoxLayout()
            objects_wgt = MathObjectWidget(objects)
            properties_wgt = MathObjectWidget(properties)
            objects_lyt = QVBoxLayout()
            properties_lyt = QVBoxLayout()

            # Math font
            objects_wgt.adjustSize()
            # objects_wgt.setFont(self.math_fonts)
            properties_wgt.adjustSize()
            # properties_wgt.setFont(self.math_fonts)

            objects_lyt.addWidget(QLabel(_('Objects:')))
            properties_lyt.addWidget(QLabel(_('Properties:')))
            objects_lyt.addWidget(objects_wgt)
            properties_lyt.addWidget(properties_wgt)
            propobj_lyt.addLayout(objects_lyt)
            propobj_lyt.addLayout(properties_lyt)

            # ───────────────────── Target ───────────────────── #
            # target_wgt = MathObjectWidget(target=target)
            target_wgt = TargetLabel(target)
            # target_wgt.setFont(self.math_fonts)
            # Set target_wgt height to 1 line: USELESS with QLabel
            # font_metrics = QFontMetrics(math_font)
            # text_size = font_metrics.size(0, target.math_type_to_display())
            # text_height = text_size.height() * 2  # Need to tweak
            # target_wgt.setMaximumHeight(text_height)

            self.__ui_wgt = QWidget()

            friendly_wgt_lyt = QVBoxLayout()
            friendly_wgt_lyt.addLayout(propobj_lyt)
            friendly_wgt_lyt.addWidget(QLabel(_('Target:')))
            friendly_wgt_lyt.addWidget(target_wgt)
            self.__ui_wgt.setLayout(friendly_wgt_lyt)
            friendly_wgt_lyt.setContentsMargins(0, 0, 0, 0)

            widget = self.__ui_wgt

        return widget

    ##############
    # Properties #
    ##############
    @property
    def exercise(self) -> Optional[Exercise]:
        """
        Return self.__exercise if it exists, None otherwise. Useful in
        StartExerciseDialog.__start_exercise to get the exercise being
        previewed and start it.

        :return: The exercise being previewed if it is not none, None
            otherwise.
        """

        if self.__exercise is not None:
            return self.__exercise
        else:
            return None

    #########
    # Slots #
    #########

    @Slot()
    def toggle_text_mode(self):
        """
        Toggle the text mode for the previewed goal (see self docstring).
        """
        cvars.set('display.text_mode_in_chooser_window',
                  self.__text_mode_checkbox.isChecked())
        self.set_preview(self.__exercise)
        # NB: cvars will be saved only when (and if) exercise starts

    @Slot()
    def __check_proof_state_for_preview(self):
        if self.__exercise and self.__exercise.initial_proof_state:
            log.debug("Lean initial proof state received, updating preview")
            self.set_preview(self.__exercise)
        self.__exercises_tree.update_tooltips()


class AbstractStartCoEx(QDialog):
    """
    The base class course and exercise chooser (inherits QDialog); it is
    inherited by StartCoExStartup and
    StartCoExExerciseFinished, which are the classes instanciated
    elsewhere in the program. This abstract class was made because
    StartCoExStartup and StartCoExExerciseFinished are
    almost the same — this class could almost be instanciated as is
    (e.g. StartCoExStartup definition is very small).

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
    (and the exercise is kept in self.__exercise_chooser.__exercise,
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

        settings = QSettings("deaduction")
        geometry = settings.value("coex_chooser/Geometry")
        # maximised = settings.value("coex_chooser/isMaximised")
        if geometry:
            self.restoreGeometry(geometry)
            # if maximised:
            #     self.showMaximized()

        self.servint = servint
        if title:
            self.setWindowTitle(title)
        self.setMinimumWidth(450)
        self.setMinimumHeight(550)

        self.course_chooser   = CourseChooser(servint)
        self.__exercise_chooser = QWidget()

        # Somehow the order of connections changes performances
        self.course_chooser.goto_exercise.connect(self.__goto_exercise)
        self.course_chooser.course_chosen.connect(self.__preview_exercises)

        # ───────────────────── Buttons ──────────────────── #

        self.__quit_btn     = QPushButton(_('Quit'))
        # self.__quit_btn.setDefault(False)
        self.__quit_btn.setAutoDefault(False)
        self.__start_ex_btn = QPushButton(_('Start exercise'))

        # self.__quit_btn.setEnabled(False)
        self.__start_ex_btn.setEnabled(False)

        self.__quit_btn.clicked.connect(self.quit_deaduction)
        self.__start_ex_btn.clicked.connect(self.__start_exercise)

        self.disable_start_btn = None

        # ───────────────────── Layouts ──────────────────── #

        self.__tabwidget = QTabWidget()
        self.__tabwidget.addTab(self.course_chooser, _('Files'))
        self.__tabwidget.addTab(self.__exercise_chooser, _('Exercises'))

        buttons_lyt = QHBoxLayout()
        buttons_lyt.addStretch()
        buttons_lyt.addWidget(self.__quit_btn)
        buttons_lyt.addWidget(self.__start_ex_btn)

        main_layout = QVBoxLayout()
        # # FIXME: put this in the right place
        # explanation = _("First select a course, then choose "
        #                                "an exercise.")
        # explanation_widget= QLabel(explanation)
        # main_layout.addWidget(explanation_widget)
        if widget:
            main_layout.addWidget(widget)
        main_layout.addWidget(self.__tabwidget)
        main_layout.addLayout(buttons_lyt)

        self.setLayout(main_layout)

        # ───────────────────── Others ───────────────────── #

        self.__tabwidget.setTabEnabled(1, False)
        if exercise:
            self.__preset_exercise(exercise)

    def closeEvent(self, event: QEvent):
        """
        Overload native Qt closeEvent method — which is called when self
        is closed — to send the signal self.window_closed.

        :param event: Some Qt mandatory thing.
        """
        if self.course_chooser.current_course:
            # Save ips of the previous course if any
            self.course_chooser.current_course.save_initial_proof_states()

        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("coex_chooser/isMaximised", self.isMaximized())
        self.showNormal()
        settings.setValue("coex_chooser/Geometry", self.saveGeometry())

        self.window_closed.emit()
        super().closeEvent(event)
        # super().closeEvent(event)
        # self.deleteLater()

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

        self.course_chooser.set_preview(exercise.course)
        self.course_chooser.add_browsed_course(exercise.course)
        # self.course_chooser.course_chosen.emit()
        self.__exercise_chooser.set_preview(exercise)
        self.__goto_exercise()

    #########
    # Slots #
    #########
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
            self.__start_ex_btn.setEnabled(True)
            self.__start_ex_btn.setDefault(True)

    @Slot()
    def __goto_exercise(self):
        """
        Go to the exercise tab.
        """

        self.__tabwidget.setCurrentIndex(1)

    @Slot(Course, str)
    def __preview_exercises(self, course: Course):
        """
        This method is called when the user chose a course and the
        signal self.__course_chooser.course_chosen is emitted. It
        instanciates an ExerciseChooser object for the corresponding
        course, puts it in the second tab and activates the tab.
        Furthermore, this method connects the signal
        self.__exercise_chooser.exercise_previewed to the slot
        self.__enable_start_ex_btn (see __enable_start_ex_btn for the
        why).

        :param course: The instance of the Course class the user just chose.
        """

        self.__start_ex_btn.setEnabled(False)

        # Tab 0 is course, 1 is exercise
        self.__tabwidget.removeTab(1)
        self.__tabwidget.setTabEnabled(1, True)
        self.__exercise_chooser = ExerciseChooser(course, self.servint)
        self.__tabwidget.addTab(self.__exercise_chooser, _('Exercises'))

        self.__exercise_chooser.exercise_previewed.connect(
                self.__enable_start_ex_btn)
        self.__exercise_chooser.exercises_tree_double_clicked_connect(
            self.__process_double_click)

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

        # (1) Check if exercise is from history file
        if exercise.history_date():
            # Back to original, incorporating auto_steps
            exercise = exercise.from_history_exercise()

        # check if exercise must be negated (e.g. is an open question)
        # TODO: this should be moved elsewhere, e.g. in __main__
        else:
            if not check_negate_statement(exercise):
                return

        # Save course_path, title, and exercise number
        # in user_config's previous_courses_list
        # TODO: Rename the list recent_courses_list?
        course_type = exercise.course.filetype
        course      = exercise.course
        course_path = course.relative_course_path
        title       = course.title
        if exercise in course.statements:
            exercise_number = course.statements.index(exercise)
        else:
            exercise_number = -1
        add_to_recent_courses(course_path, course_type, title,
                              exercise_number)

        # Send exercise_chosen signal and close dialog
        self.exercise_chosen.emit(exercise)
        # log.debug("Exercise chosen, closing window")
        self.close()  # Fuck you and I'll see you tomorrow!


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


class StartCoExExerciseFinished(AbstractStartCoEx):
    """
    The CoEx chooser after usr just finished an exercise. It displays
    a CoEx chooser with the finished exercise
    being preset / previewed. See AbstractStartCoEx docstring.
    """
    # FIXME: not used

    def __init__(self, finished_exercise: Exercise):
        """
        Init self.

        :param finisehd_exercise: Exercise that usr just finished.
        """

        congrats_wgt = QWidget()
        lyt          = QHBoxLayout()
        img          = QLabel()
        pixmap       = QPixmap(cdirs.icons / 'confetti.png')
        pixmap       = pixmap.scaledToHeight(100, Qt.SmoothTransformation)
        img.setPixmap(pixmap)
        lyt.addWidget(img)
        lyt.addStretch()
        lyt.addWidget(QLabel(_('Congratulations, exercise finished!')))
        congrats_wgt.setLayout(lyt)
        title = _('Exercise finished — d∃∀duction')

        super().__init__(title=title, widget=congrats_wgt,
                         exercise=finished_exercise)

    def closeEvent(self, event: QEvent):
        """
        Overload native Qt closeEvent method — which is called when self
        is closed — to send the signal self.window_closed.

        :param event: Some Qt mandatory thing.
        """

        super().closeEvent(event)
        self.window_closed.emit()


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
        if exercise.lean_variables:
            log.warning("Exercise is an open question but has variables:"
                        "negation will not be correct!!")

        title = _("Do you want to prove this statement or its negation?")
        if exercise.initial_proof_state:
            goal = exercise.initial_proof_state.goals[0]
            output = goal.goal_to_text(text_mode=False, to_prove=False)
        else:
            output = exercise.lean_variables + "   " \
                     + exercise.lean_core_statement
        choices = [("1", _("Prove statement")),
                   ("2", _("Prove negation"))]
        choice, ok2 = ButtonsDialog.get_item(choices,
                                             title,
                                             output)
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
