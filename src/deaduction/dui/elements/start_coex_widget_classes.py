"""
#########################################################
# actions_widgets_classes.py : exercise actions widgets #
#########################################################

    Provide widgets classes for an exercise's actions area, that is the
    two rows of action buttons (logic buttons and proof techniques
    buttons) and the so-called statements tree : course definitions,
    theorems and exercises used as theorems are displayed in a tree
    whose structure is that of the course. Those widgets will be
    instantiated in ExerciseCentralWidget, which itself will be
    instantiated as an attribute of ExerciseMainWindow. Provided
    classes:
        - ActionButton;
        - ActionButtonsLine;
        - StatementsTreeWidgetNode;
        - StatementsTreeWidgetItem;
        - StatementsTreeWidget.

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

# import logging

from PySide2.QtGui import QIcon

import deaduction.pylib.config.vars as cvars
import deaduction.pylib.config.dirs as cdirs
import deaduction.pylib.utils.filesystem as fs

from deaduction.dui.elements.actions_widgets_classes import StatementsTreeWidgetItem


class ChooseExerciseWidgetItem(StatementsTreeWidgetItem):

    def set_icon(self):
        # icons_base_dir = cvars.get("icons.path")
        icons_base_dir = cdirs.icons

        exercise = self.statement

        if exercise.is_solved_in_history_course():
            path = icons_base_dir / 'checked.png'
        elif exercise.is_in_history_course():
            path = icons_base_dir / 'icons8-in-progress-96.png'

        self.setIcon(0, QIcon(str(path.resolve())))





