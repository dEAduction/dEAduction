"""
############################################
# __init__.py : provide dEAduction widgets #
############################################

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

from .actions_widgets_classes import (
        ActionButton,
        ActionButtonsWidget,
        StatementsTreeWidgetItem,
        StatementsTreeWidgetNode,
        StatementsTreeWidget)

from .context_widgets_classes import (
        MathObjectWidgetItem,
        MathObjectWidget,
        TargetWidget)

from .choose_course_exercise_widgets import (
        StartExerciseDialog)

from .lean_editor import (
        LeanEditor)

from .exercise_widgets import (
        ExerciseCentralWidget,
        ExerciseMainWindow)
