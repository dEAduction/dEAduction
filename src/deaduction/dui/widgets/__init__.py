"""
######################################################
# __init__.py : init file for deaduction.dui.widgets #
######################################################

    Provide deaduction.dui.widgets classes. Most of them inherit
    QWidget but some inherit smaller classes used in widgets such as
    items (QListItem, QTreeWidgetItem). Dialogs are provided in
    deaduction.dui.widgets.dialogs. Provided classes:
        - ActionButton,
        - ActionButtonsWidget,
        - DisclosureTriangle,
        - ExerciseCentralWidget,
        - ExerciseMainWindow,
        - HorizontalLine,
        - IconStatusBar,
        - LeanEditor,
        - MathObjectWidget,
        - MathObjectWidgetItem,
        - RecentCoursesLW,
        - RecentCoursesLWI,
        - StartExerciseDialog,
        - StatementsTreeWidget,
        - StatementsTreeWidgetItem,
        - StatementsTreeWidgetNode,
        - TargetWidget,
        - TextEditLogger.

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
Date           : July 2020

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

import actions_widgets_classes
import choose_course_exercise_widgets
import context_widgets_classes
import disclosure_triangle
import exercise_widgets
import horizontal_line
import lean_editor
import recent_courses_widgets
import statusbar
import text_edit_logger
