"""
#######################################################################
# choose_course_exercise_widgets.py : course/exercise chooser widgets #
#######################################################################

    Provide StartExerciseDialog: the dialog used by the user to choose
    a course, then an exercise, and start the latter. 

    The class to be used elsewhere in the program is
    StartExerciseDialog (inherits QDialog). The other classes
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
from gettext import   gettext as _
from pathlib import   Path
from typing  import ( Dict,
                      Optional )

from PySide2.QtCore    import ( Signal,
                                Slot )
from PySide2.QtGui     import   QFont
from PySide2.QtWidgets import ( QApplication,
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
                                QWidget )

from deaduction.config           import   add_to_recent_courses
from deaduction.dui.widgets      import ( MathObjectWidget,
                                          StatementsTreeWidget,
                                          StatementsTreeWidgetItem )
from deaduction.dui.utils        import ( DisclosureTriangle,
                                          HorizontalLine,
                                          RecentCoursesLW,
                                          RecentCoursesLWI,
                                          read_pkl_course,
                                          replace_widget_layout,
                                          ButtonsDialog)
from deaduction.pylib.coursedata import ( Course,
                                          Exercise )

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

    Finally, data such as the course being previewed and its filetype
    are kept as private class atributes.
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
        spacer             = QSpacerItem(1, 5)
        self.__main_layout = QVBoxLayout()
        self.__main_layout.addLayout(browser_layout)
        self.__main_layout.addItem(spacer)
        self.__main_layout.addWidget(HorizontalLine())
        self.__main_layout.addItem(spacer)
        self.__main_layout.addWidget(self.__preview_wgt)

        self.setLayout(self.__main_layout)

    def set_preview(self, main_widget: QWidget = None, title: str = None,
                    subtitle: str = None, details: Dict[str, str] = None,
                    description: str = None, expand_details: bool = False):
        # TODO: Make widget a QLayout instead?
        """
        Set the preview area of the choosze (given something (course or
        exercise) has been chosen). The preview area is made of a title,
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

    course_chosen = Signal(Course, str, bool)

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
        self.__recent_courses_wgt.itemClicked.connect(partial(
                self.__recent_course_clicked, goto_exercise=False))
        self.__recent_courses_wgt.itemDoubleClicked.connect(partial(
                self.__recent_course_clicked, goto_exercise=True))

        browser_layout = QVBoxLayout()
        browser_layout.addWidget(self.__browse_btn)
        browser_layout.addWidget(self.__recent_courses_wgt)

        super().__init__(browser_layout)

    def set_preview(self):
        """
        Set course preview. See AbstractCoExChooser.set_preview
        docstring.  Here, there is no main_widget. Course metadata are
        displayed in the disclosure triangle by passing them as details
        in super().set_preview.  When a course is selected (either by
        browsing course files or clicking on a recent course in
        self.__recent_courses_wgt), the signal course_chosen is emitted
        with the course (and additional info). It is received in
        StartExerciseDialog, which then instanciates an ExerciseChooser
        for this course.

        :param Course: Course to be previewed.
        """

        # Title, subtitle, etc
        title       = self.__course.title
        subtitle    = self.__course.subtitle
        description = self.__course.description

        # Details
        details = self.__course.metadata
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

        self.course_chosen.emit(self.__course, self.__course_filetype,
                                self.__goto_exercise)

    # TODO: Make this a course classmethod?
    def __instanciate_course(self, course_path: Path):
        """
        Given a course path, instanciate a Course object and save the
        course and its file type ('.lean' or '.pkl') ass private class
        atributes.

        :param course_path: The course-file path of the course we want
            to instanciate.
        """

        course_filetype = course_path.suffix
        if course_filetype == '.lean':
            course = Course.from_file(course_path)
        elif course_filetype == '.pkl':
            course = read_pkl_course(course_path)

        self.__course          = course
        self.__course_filetype = course_filetype

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
            self.__instanciate_course(course_path)

            title = self.__course.title
            self.__recent_courses_wgt.add_browsed_course(
                    course_path, title)
            self.__goto_exercise = False
            self.set_preview()

    @Slot(RecentCoursesLWI, bool)
    def __recent_course_clicked(self, course_item: RecentCoursesLWI,
                                goto_exercise: bool):
        """
        This method is called when the user clicks on an item in
        self.__recent_courses_wgt. It sends the corresponding
        RecentCoursesLWI and this method instanciates a Course object
        from it and passes it to set_preview. Furthermore, is this slot
        was called by a simple click, goto_exercise is True; if it was
        called by a double click, goto_exercise is False. This
        information will be sent (in self.exercise_selected signal by
        set_preview) to the instance of StartExerciseDialog and
        determines whether or not the interface directly goes to the
        exercise viewer when the course has been chosen.
        """

        self.__goto_exercise = goto_exercise
        course_path          = course_item.course_path
        self.__instanciate_course(course_path)
        self.set_preview()


class ExerciseChooser(AbstractCoExChooser):
    """
    The exercise chooser. This widget is activated / shown when a course
    has been chosen by the user (signal
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

    def __init__(self, course: Course, course_filetype: str):
        """
        See AbstractCoExChooser.__init__ docstring. Here, the browser
        layout is only made of the course's StatementsTreeWidget
        displaying only the exercises (e.g. no theorems). The course
        file type is stored as a class private attribute and will be
        used by set_preview to determine if an exercise is to be
        previewed with its goal or not (see self docstring).

        :param course: The course in which the user chooses an exercise.
        :param course_filetype: The course's file file-type ('.lean' or
            '.pkl'), see self docstring.
        """

        self.__course_filetype = course_filetype

        browser_layout = QVBoxLayout()
        exercises_tree = StatementsTreeWidget(course.exercises_list(),
                                              course.outline)
        exercises_tree.resizeColumnToContents(0)
        browser_layout.addWidget(exercises_tree)

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

        with_preview = self.__course_filetype == '.pkl'
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

        super().set_preview(main_widget=main_widget, title=title,
                            description=description,
                            expand_details=False)

        self.exercise_previewed.emit()

    ##############
    # Properties #
    ##############

    @property
    def course_filetype(self) -> str:
        """
        Return self.__course_filetype. Usefull in
        StartExerciseDialog.__start_exercise to add the corresponding
        course to the recent courses' list.
        """

        return self.__course_filetype

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


class StartExerciseDialog(QDialog):
    """
    The course and exercise chooser (inherits QDialog). This is the
    first widget activated / shown when launching d∃∀duction as it is
    the one which allows the user to:
    1. choose a course (from a file or from recent courses' list);
    2. browse / preview the exercises for the chosen course;
    3. start the chosen exercise (launchs the ExerciseMainWindow).

    This class is to be instanciated in deaduction.dui.__main__.py. The
    dialog is opened with QDialog.open and qtrio waits for the signal
    self.exercise_chosen to be emitted with the corresponding exercise.
    Once it is done, the program proceeds on launching the main exercise
    window.

    StartExerciseDialog is divided in two main sub-widgets (presented in
    a QTabWidget): the course chooser (self.__course_chooser) and the
    exercise chooser (self.__exercise_chooser), see those choosers
    docstrings. At first, only the course chooser is enabled. When the
    user selects a course (either by browsing files or clicking on the
    recent courses list), the signal self.__course_chooser.course_chosen
    is emitted and the slot __set_course is called (with the
    corresponding courses and other data). An ExerciseChooser object is
    instanciated (self.__exercise_chooser) in a new tab and the user can
    browse exercises and preview them. Once the user chose a course,
    they click on the 'Start exercise' button, which closes the dialog
    and launches the exercise main window.

    The communication between this class, the two choosers and the rest
    of the program can be tricky and the actual solution is
    not-so-elegant; enhancements encouraged and welcome. For example,
    the 'Start exercise' button is not always enabled. At init, it is
    disabled and it is enabled when the user clicks on an exercise item
    in self.__exercise_chooser and the signal
    self.__exercise_chooser.exercise_previewed is emitted.
    """

    exercise_chosen = Signal(Exercise)

    def __init__(self):
        """
        Init self by setting up the layouts, the buttons and the tab
        widget (see self docstring).
        """

        super().__init__()

        self.setWindowTitle(_('Choose course and exercise — d∃∀duction'))
        self.setMinimumWidth(450)
        self.setMinimumHeight(550)

        self.__course_chooser   = CourseChooser()
        self.__exercise_chooser = QWidget()

        self.__course_chooser.course_chosen.connect(self.__preview_exercises)

        # ───────────────────── Buttons ──────────────────── #

        self.__quit_btn     = QPushButton(_('Quit'))
        self.__start_ex_btn = QPushButton(_('Start exercise'))

        self.__quit_btn.setEnabled(False)
        self.__start_ex_btn.setEnabled(False)

        self.__start_ex_btn.clicked.connect(self.__start_exercise)

        # ───────────────────── Layouts ──────────────────── #

        self.__coex_tabwidget = QTabWidget()
        self.__coex_tabwidget.addTab(self.__course_chooser, _('Course'))
        self.__coex_tabwidget.addTab(self.__exercise_chooser, _('Exercise'))

        buttons_lyt = QHBoxLayout()
        buttons_lyt.addStretch()
        buttons_lyt.addWidget(self.__quit_btn)
        buttons_lyt.addWidget(self.__start_ex_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.__coex_tabwidget)
        main_layout.addLayout(buttons_lyt)

        self.setLayout(main_layout)

        # ───────────────────── Others ───────────────────── #

        self.__coex_tabwidget.setTabEnabled(1, False)

    #########
    # Slots #
    #########

    @Slot()
    def __enable_start_ex_btn(self):
        """
        This method is called when an exercise item is clicked on in the
        exercise chooser and therefore is being previewed.  Its goal is
        to enable the 'Start exercise' button which may have been
        disabled until then.  The corresponding signal is
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

    @Slot(Course, Path, bool)
    def __preview_exercises(self, course: Course, course_filetype: Path,
                            goto_exercise: bool):
        """
        This method is called when the user chose a course an the signal
        self.__course_chooser.course_chosen is emitted. It instanciates
        an ExerciseChooser object for the corresponding course, puts it
        in the second tab and activates the tab. Furthermore, this
        method connects the signal
        self.__exercise_chooser.exercise_previewed to the slot
        self.__enable_start_ex_btn (see __enable_start_ex_btn for the
        why).
        """

        self.__start_ex_btn.setEnabled(False)

        self.__coex_tabwidget.removeTab(1)
        self.__coex_tabwidget.setTabEnabled(1, True)
        self.__exercise_chooser = ExerciseChooser(course, course_filetype)
        self.__coex_tabwidget.addTab(self.__exercise_chooser, _('Exercise'))
        if goto_exercise:
            self.__coex_tabwidget.setCurrentIndex(1)

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
        ok = check_negate_statement(exercise)
        if not ok:
            return

        # Save course_path, title, and exercise number
        # in user_config's previous_courses_list
        # TODO: Rename the list recent_courses_list?
        course_type     = self.__exercise_chooser.course_filetype
        course          = exercise.course
        course_path     = course.course_path
        title           = course.title
        if exercise in course.statements:
            exercise_number = course.statements.index(exercise)
        else:
            exercise_number = -1
        add_to_recent_courses(course_path,
                              course_type,
                              title,
                              exercise_number)

        # Send exercise_chosen signal and close dialog
        self.exercise_chosen.emit(exercise)
        self.accept()  # Fuck you and I'll see you tomorrow!


def check_negate_statement(exercise) -> bool:
    """
    If needed, ask the user to choose between proving the statement
    or its negation. Change the attribute exercise.negate_statement
    accordingly.
    :param exercise:    Exercise
    :return:            True if choice has been made, else False

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

    start_exercise_dialog = StartExerciseDialog()
    start_exercise_dialog.show()

    sys.exit(app.exec_())


#         db         db
#       d88           88
#      888            888
#     d88             888b
#     888             d88P
#     Y888b  /``````\8888
#   ,----Y888        Y88P`````\
#   |        ,'`\_/``\ |,,    |
#    \,,,,-| | o | o / |  ```'
#          |  """ """  |
#         /             \
#        |               \
#        |  ,,,,----'''```|
#        |``   @    @     |
#         \,,    ___    ,,/
#            \__|   |__/
#               | | |
#               \_|_/
