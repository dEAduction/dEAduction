"""
########################################################
# exercisewidget.py : provide the ExerciseWidget class #
########################################################

Author(s)      : Kryzar antoine@hugounet.com
Maintainers(s) : Kryzar antoine@hugounet.com
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

from PySide2.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout
from PySide2.QtWidgets import QMainWindow, QWidget


class ExerciseCentralWidget(QWidget):

    def _init_actions(self):
        # Init tool buttons
        self.tool_buttons = \
                ActionButtonsWidget(self.exercise.available_logic)
        # Init proof techniques buttons
        self.proof_buttons = \
                ActionButtonsWidget(self.exercise.available_proof_techniques)
        # Init statements tree
        self.statements_tree = \
                StatementsTreeWidget(self.exercise.available_statements,
                                     self.exercise.course.outline) 

    def _init_layout_boxes(self):
        # TODO: draw the damn thing

        # Layouts
        self._main_layout = QVBoxLayout()
        self._context_actions_layout = QHBoxLayout()
        self._context_layout = QVBoxLayout()
        self._actions_layout = QVBoxLayout()

        # Group boxes
        self.context_gb = QGroupBox(_('Context (properties and objects)'))
        self.actions_gb = QGroupBox(_('Actions (transform context)'))

    def __init__(self, exercise: Exercise, first_goal: Goal):
        super().__init__()
        self.exercise = exercise

        self._init_layout_boxes()
        self._init_actions()

    def update_goal(new_goal: Goal):
        self.goal = new_goal

        # Get objects and properties as two list of (ProofStatePO, 
        # str), the str being the tag of the prop. or obj.
        tagged_goal_pspos = self.goal.tag_and_split_propositions_objects()
        tagged_goal_objects = goal_actions_pspos[0]
        tagged_actions_prop = goal_actions_pspos[1]

        # Create the widgets
        self.tagged_goal_objects = ProofStatePOWidget(tagged_goal_objects)
        self.tagged_goal_prop = ProofStatePOWidget(tagged_goal_prop)

        # Put them in layouts


class ExerciseMainWindow(QMainWindow):

    pass
