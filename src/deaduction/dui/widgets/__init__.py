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

# Retourne une erreur dès le premier fichier
# from . import actions_widgets_classes
# from . import context_widgets_classes
# from . import disclosure_triangle
# from . import exercise_widgets
# from . import horizontal_line
# from . import lean_editor
# from . import recent_courses_widgets
# from . import icon_status_bar
# from . import text_edit_logger

# Retourne une erreur seulement à partir de icon_status_bar
from .actions_widgets_classes import *
from .context_widgets_classes import *
from .disclosure_triangle import *
from .exercise_widgets import *
from .horizontal_line import *
from .lean_editor import *
from .recent_courses_widgets import *
from .icon_status_bar import *
from .text_edit_logger import *

# Invalid syntax
# import .actions_widgets_classes
# import .context_widgets_classes
# import .disclosure_triangle
# import .exercise_widgets
# import .horizontal_line
# import .lean_editor
# import .recent_courses_widgets
# import .icon_status_bar
# import .text_edit_logger
