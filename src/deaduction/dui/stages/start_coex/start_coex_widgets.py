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
                               QEvent)
from PySide2.QtGui     import (QFont,
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

from deaduction.pylib.config.i18n   import _
from deaduction.dui.elements        import (MathObjectWidget,
                                            RecentCoursesLW,
                                            RecentCoursesLWI,
                                            StatementsTreeWidget,
                                            StatementsTreeWidgetItem)
from deaduction.dui.primitives      import (DisclosureTriangle,
                                            ButtonsDialog)
from deaduction.dui.utils           import (read_pkl_course,
                                            replace_widget_layout,
                                            HorizontalLine)
from deaduction.pylib.config.course import  add_to_recent_courses
from deaduction.pylib.coursedata    import (Course,
                                             Exercise)

log = logging.getLogger(__name__)


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
        :param exapand_details: Tell if the 'Details' disclosure tree is
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
        if details:
            details_wgt = DisclosureTriangle('Details', details)
            details_wgt.expand(expand_details)

            layout.addWidget(details_wgt)
        if description:
            description_wgt = QLabel(description)
            description_wgt.setWordWrap(True)
            layout.addWidget(description_wgt)
        if main_widget:
            layout.addWidget(main_widget)

        layout.addStretch()

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

    def __init__(self):
        """
        See AbstractCoExChooser.__init__ docstring. Here, the browser
        layout is made of a browse-button to browse courses files
        and a QListWidget displayling recent courses.
        """

        # Browse button
        self.__browse_btn = QPushButton(_('Browse files for course'))
        self.__browse_btn.setAutoDefault(False)
        self.__browse_btn.clicked.connect(self.__browse_courses)

        # Recent courses widget
        self.__recent_courses_wgt = RecentCoursesLW()
        browser_layout = QVBoxLayout()
        browser_layout.addWidget(self.__browse_btn)
        browser_layout.addWidget(self.__recent_courses_wgt)

        self.__recent_courses_wgt.itemClicked.connect(
                self.__recent_course_clicked)
        self.__recent_courses_wgt.itemDoubleClicked.connect(
                self.__recent_course_clicked)
        # Cannot connect signal directly to signal because
        # itemDoubleClicked sends an argument but goto_exercise
        # does not receive one. See snippets/connect_signal_to_signal.
        self.__recent_courses_wgt.itemDoubleClicked.connect(
                lambda x: self.goto_exercise.emit())

        super().__init__(browser_layout)

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

        # Title, subtitle, etc
        title       = course.title
        subtitle    = course.subtitle
        description = course.description

        # Details
        details = course.metadata
        # Remove title, subtitle and description from details
        # TODO: Prevent user for using a 'Path' attribute (in the course
        # file) when writing a course.
        # TODO: Add course path.
        for key in ['title', 'subtitle', 'description']:
            if key in details:
                details.pop(key)

        if not details:  # Set details to None if empty
            details = None

        super().set_preview(main_widget=None, title=title, subtitle=subtitle,
                            details=details, description=description,
                            expand_details=True)

        self.course_chosen.emit(course)

    #########
    # Slots #
    #########

    @Slot()
    def __browse_courses(self):
        """
        This method is called when the 'Browse courses' button is
        clicked on. It opens a file dialog, the user chooses a
        course-file, a Course object is instanciated and the method
        set_preview is called.
        """

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('*.lean *.pkl')

        # TODO: Stop using exec_, not recommended by documentation
        if dialog.exec_():
            course_path = Path(dialog.selectedFiles()[0])
            course = Course.from_file(course_path)

            title = course.title
            self.__recent_courses_wgt.add_browsed_course(course_path, title)
            self.set_preview(course)

    @Slot(RecentCoursesLWI, bool)
    def __recent_course_clicked(self, course_item: RecentCoursesLWI):
        """
        This method is called when the user clicks on an item in
        self.__recent_courses_wgt. It sends the corresponding
        RecentCoursesLWI and this method instanciates a Course object
        from it and passes it to set_preview.

        :course_item: The RecentCoursesLWI the user clicked on.
        """

        course_path = course_item.course_path
        course = Course.from_file(course_path)
        self.set_preview(course)


class ExerciseChooser(AbstractCoExChooser):
    """
    The exercise chooser. This widget is activated / shown when a course has
    been chosen by usr (signal
    StartExerciseDialog.__course_chooser.course_chosen).
    - The browser area is made of the course's StatementsTreeWidget
      displaying only the exercises (e.g. no theorems).
    - The preview area is more complex and depends on the course's
      filetype.
      - If the course was loaded from a .lean file, the preview is only
        made of the exercise's title, subtitle and description.
      - If the course was loaded from a .pkl file, exercise's title,
        subtitle and description are available, as well as its goal
        (target, math. objects and math. properties). This cannot be
        done (yet) if the file course is .lean because for displaying
        the goal, we would need to launch the lean server interface and
        we obviously do not want to do that for each exercise. Pickle
        files (see puthon modyle pickle) allow to store class instances
        and thus we can store the course if it has been pre-processed.
        Finally, this goal preview is either displayed as:
        - two lists for the math objects and properties and a line edit
          for the target;
        - or a single list with all these informations (this is called
          the text mode and it is toggle with a checkbox).
    """

    # This signal is emitted when an exercise is being previewed. It is
    # received in the instance ofStartExerciseDialog and the Start
    # exercise button is enabled and set to default.
    exercise_previewed = Signal()

    def __init__(self, course: Course):
        """
        See AbstractCoExChooser.__init__ docstring. Here, the browser layout is
        only made of the course's StatementsTreeWidget displaying only the
        exercises (e.g. no theorems). The course file type is used by
        set_preview to determine if an exercise is to be previewed with its
        goal or not (see self docstring).

        :param course: The course in which usr chooses an exercise.
        """

        browser_layout = QVBoxLayout()
        exercises_tree = StatementsTreeWidget(course.exercises_list(),
                                              course.outline)
        exercises_tree.resizeColumnToContents(0)
        browser_layout.addWidget(exercises_tree)
        self.__exercises_tree = exercises_tree

        exercises_tree.itemClicked.connect(self.__set_preview_from_click)

        super().__init__(browser_layout)

    def set_preview(self, exercise: Exercise):
        """
        Set exercise preview. See AbstractCoExChooser.set_preview
        docstring. The exercise's title, subtitle and description are
        displayed; if a preview is available (i.e. when course's file
        file-type is '.pkl', see self doctring), it is displayed. This
        method manages these two possibilities with a big if / else
        condition.

        :param exercise: The exercise to be previewed.
        """

        self.__exercise = exercise
        main_widget     = QWidget()
        main_widget_lyt = QVBoxLayout()
        main_widget_lyt.setContentsMargins(0, 0, 0, 0)

        with_preview = exercise.course.filetype == '.pkl'
        if with_preview:

            proofstate = exercise.initial_proof_state
            goal       = proofstate.goals[0]  # Only one goal (?)
            target     = goal.target
            context    = goal.tag_and_split_propositions_objects()
            objects    = context[0]
            properties = context[1]

            ###################
            # Friendly widget #
            ###################
            # The widget with lists for math. objects and properties
            # and a line edit for the target.

            # ───────────── Objects and properties ───────────── #

            propobj_lyt    = QHBoxLayout()
            objects_wgt    = MathObjectWidget(objects)
            properties_wgt = MathObjectWidget(properties)
            objects_lyt    = QVBoxLayout()
            properties_lyt = QVBoxLayout()

            objects_wgt.adjustSize()
            objects_wgt.setFont(QFont('Menlo'))
            properties_wgt.adjustSize()
            properties_wgt.setFont(QFont('Menlo'))

            objects_lyt.addWidget(QLabel(_('Objects:')))
            properties_lyt.addWidget(QLabel(_('Properties:')))
            objects_lyt.addWidget(objects_wgt)
            properties_lyt.addWidget(properties_wgt)
            propobj_lyt.addLayout(objects_lyt)
            propobj_lyt.addLayout(properties_lyt)

            # ───────────────────── Target ───────────────────── #

            target_wgt = QLineEdit()
            target_wgt.setText(target.math_type.to_display(format_="utf8",
                                                           is_math_type=True))
            target_wgt.setFont(QFont('Menlo'))

            # ────────────────────── Rest ────────────────────── #

            self.__friendly_wgt = QWidget()
            friendly_wgt_lyt    = QVBoxLayout()
            friendly_wgt_lyt.addLayout(propobj_lyt)
            friendly_wgt_lyt.addWidget(QLabel(_('Target:')))
            friendly_wgt_lyt.addWidget(target_wgt)
            self.__friendly_wgt.setLayout(friendly_wgt_lyt)

            ###############
            # Code widget #
            ###############
            # The goal is presented in a single list widget.

            self.__code_wgt = QTextEdit()
            self.__code_wgt.setReadOnly(True)
            self.__code_wgt.setFont(QFont('Menlo'))
            if exercise.initial_proof_state:
                text = goal.goal_to_text()
                self.__code_wgt.setText(text)

            ########
            # Rest #
            ########

            # Checkbox
            self.__text_mode_checkbox = QCheckBox(_('Text mode'))
            self.__text_mode_checkbox.clicked.connect(self.toggle_text_mode)
            cb_lyt = QHBoxLayout()
            cb_lyt.addStretch()
            cb_lyt.addWidget(self.__text_mode_checkbox)

            # Ugly margins
            for lyt in [main_widget_lyt, friendly_wgt_lyt]:
                # Somehow this works…
                lyt.setContentsMargins(0, 0, 0, 0)

            self.__text_mode_checkbox.setChecked(False)
            self.__friendly_wgt.show()
            self.__code_wgt.hide()

            main_widget_lyt.addWidget(self.__friendly_wgt)
            main_widget_lyt.addWidget(self.__code_wgt)
            main_widget_lyt.addLayout(cb_lyt)
        else:

            widget_lbl = QLabel(_('Goal preview only available when course '
                                  'file extension is .pkl.'))
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

    @Slot(StatementsTreeWidgetItem)
    def __set_preview_from_click(self, item: StatementsTreeWidgetItem):
        """
        When the user selects an exercise in the course's exercises
        tree, the signal itemClicked is emitted and this slot is called.
        One cannot directly call set_preview because at first we must be
        sure that the clicked item was an exercise item and not a nod
        (e.g. a course section).

        :param item: The clicked item (exercise item or nod item) in the
            course's exercises tree.
        """

        if isinstance(item, StatementsTreeWidgetItem):
            exercise = item.statement
            self.set_preview(exercise)

    @Slot()
    def toggle_text_mode(self):
        """
        Toggle the text mode for the previewed goal (see self docstring).
        """

        if self.__text_mode_checkbox.isChecked():
            self.__friendly_wgt.hide()
            self.__code_wgt.show()
        else:
            self.__friendly_wgt.show()
            self.__code_wgt.hide()


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

    def __init__(self, title: Optional[str], widget: Optional[QWidget],
                 exercise: Optional[Exercise]):
        """
        Init self by setting up the layouts, the buttons and the tab
        widget (see self docstring). 

        :param title: Optional window title.
        :param widget: Optional QWidget to be displayed on top of the
            CoEx chooser (e.g. a congratulations widget in
            StartCoExExerciseFinished).
        :param exercise: Optional Exercise to be preset / previewed
            (e.g. finished exercise in StartCoExExerciseFinished).
        """

        super().__init__()

        if title:
            self.setWindowTitle(title)
        self.setMinimumWidth(450)
        self.setMinimumHeight(550)

        self.__course_chooser   = CourseChooser()
        self.__exercise_chooser = QWidget()

        # Somehow the order of connections changes performances
        self.__course_chooser.goto_exercise.connect(self.__goto_exercise)
        self.__course_chooser.course_chosen.connect(self.__preview_exercises)

        # ───────────────────── Buttons ──────────────────── #

        self.__quit_btn     = QPushButton(_('Quit'))
        self.__start_ex_btn = QPushButton(_('Start exercise'))

        self.__quit_btn.setEnabled(False)
        self.__start_ex_btn.setEnabled(False)

        self.__start_ex_btn.clicked.connect(self.__start_exercise)

        # ───────────────────── Layouts ──────────────────── #

        self.__tabwidget = QTabWidget()
        self.__tabwidget.addTab(self.__course_chooser, _('Course'))
        self.__tabwidget.addTab(self.__exercise_chooser, _('Exercise'))

        buttons_lyt = QHBoxLayout()
        buttons_lyt.addStretch()
        buttons_lyt.addWidget(self.__quit_btn)
        buttons_lyt.addWidget(self.__start_ex_btn)

        main_layout = QVBoxLayout()
        if widget:
            main_layout.addWidget(widget)
        main_layout.addWidget(self.__tabwidget)
        main_layout.addLayout(buttons_lyt)

        self.setLayout(main_layout)

        # ───────────────────── Others ───────────────────── #

        self.__tabwidget.setTabEnabled(1, False)
        if exercise:
            self.__preset_exercise(exercise)

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

        self.__course_chooser.set_preview(exercise.course)
        self.__course_chooser.add_browsed_course(exercise.course)
        self.__exercise_chooser.set_preview(exercise)
        self.__goto_exercise()

    #########
    # Slots #
    #########

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
        self.__exercise_chooser = ExerciseChooser(course)
        self.__tabwidget.addTab(self.__exercise_chooser, _('Exercise'))

        self.__exercise_chooser.exercise_previewed.connect(
                self.__enable_start_ex_btn)

    @Slot()
    def __start_exercise(self):
        """
        This method is called when the user clicks on the 'Start
        exercise' button. It adds the corresponding course to the recent
        courses list if needed, emits the signal self.exercise_chosen
        (see self docstring) and closes the dialog.
        """

        exercise = self.__exercise_chooser.exercise

        # check if exercise must be negated (e.g. in an open question)
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
        self.accept()  # Fuck you and I'll see you tomorrow!


class StartCoExStartup(AbstractStartCoEx):
    """
    The CoEx chooser when starting up d∃∀duction (see
    AbstractStartCoEx docstring) This is the first widget
    activated / shown when launching d∃∀duction as it is the one which
    allows the user to:
    1. choose a course (from a file or from recent courses' list);
    2. browse / preview the exercises for the chosen course;
    3. start the chosen exercise (launchs the ExerciseMainWindow).

    This class is to be instanciated in deaduction.dui.__main__.py. The
    dialog is opened with QDialog.open and qtrio waits for the signal
    self.exercise_chosen to be emitted with the corresponding exercise.
    Once it is done, the program proceeds on launching the main exercise
    window.
    """

    def __init__(self, exercise: Exercise = None):
        """
        Init self.
        """

        title = _('Choose course and exercise — d∃∀duction')
        super().__init__(title=title, widget=None, exercise=exercise)

    def closeEvent(self, event: QEvent):
        """
        Overload native Qt closeEvent method — which is called when self
        is closed — to send the signal self.window_closed.

        :param event: Some Qt mandatory thing.
        """

        super().closeEvent(event)
        self.window_closed.emit()


class StartCoExExerciseFinished(AbstractStartCoEx):
    """
    The CoEx chooser after usr just finished an exercise. It displays a
    congratulation message and a CoEx chooser with the finished exercise
    being preset / previewed. See AbstractStartCoEx docstring.
    """

    def __init__(self, finished_exercise: Exercise):
        """
        Init self.

        :param finisehd_exercise: Exercise that usr just finished.
        """

        congrats_wgt = QWidget()
        lyt          = QHBoxLayout()
        img          = QLabel()
        pixmap       = QPixmap('confetti.png')
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

    ok = True  # default value
    open_question = exercise.info.setdefault('open_question', False)
    if ('negate_statement' in exercise.info
            and exercise.info['negate_statement']):
        exercise.negate_statement = True
    elif open_question:
        # exercise is an open question and the user has to choose her way
        if exercise.lean_variables:
            log.warning("Exercise is an open question but has variables:"
                        "negation will not be correct!!")

        title = _("Do you want to prove this statement or its negation?")
        if exercise.initial_proof_state:
            goal = exercise.initial_proof_state.goals[0]
            output = goal.goal_to_text(text_depth=0, to_prove=False)
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
        else:  # cancel exercise if no choice
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
