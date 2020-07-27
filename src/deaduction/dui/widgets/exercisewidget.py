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

    def _init_all_layout_boxes(self):
        # TODO: draw the damn thing

        # Layouts
        self._main_layout = QVBoxLayout()
        self._context_actions_layout = QHBoxLayout()
        self._context_layout = QVBoxLayout()
        self._actions_layout = QVBoxLayout()

        # Group boxes
        self._actions_gb = QGroupBox(_('Actions (transform context)'))
        self._context_gb = QGroupBox(_('Context (properties and objects)'))

    def _init_actions(self):
        # Init tool buttons
        self.logic_buttons = \
                ActionButtonsWidget(self.exercise.available_logic)
        # Init proof techniques buttons
        self.proof_techniques_buttons = \
                ActionButtonsWidget(self.exercise.available_proof_techniques)
        # Init statements tree
        self.statements_tree = \
                StatementsTreeWidget(self.exercise.available_statements,
                                     self.exercise.course.outline) 

    def _init_goal(first_goal: Goal):
        self.current_goal = first_goal

        # Get objects and properties as two list of (ProofStatePO, 
        # str), the str being the tag of the prop. or obj.
        goal_tagged_pspo = self.current_goal.tag_and_split_propositions_objects()
        goal_tagged_objects = goal_tagged_pspo[0]
        goal_tagged_props = goal_tagged_pspo[1]
        # And create the widgets
        self.goal_tagged_objects = ProofStatePOWidget(goal_tagged_objects)
        self.goal_tagged_props = ProofStatePOWidget(goal_tagged_props)

        # Finally the target
        self.goal_target = TargetWidget(self.current_goal.target)

    def _init_put_widgets_in_layouts(self):
        # Actions
        self._actions_layout.addWidget(self.logic_buttons)
        self._actions_layout.addWidget(self.proof_techniques_buttons)
        self._actions_layout.addWidget(self.statements_tree)
        self._actions_gb.setLayout(self._actions_layout)

        # Context
        self._context_layout.addWidget(self.goal_tagged_objects)
        self._context_layout.addWidget(self.goal_tagged_props)
        self._context_gb.setLayout(self._context_layout)

        # https://i.kym-cdn.com/photos/images/original/001/561/446/27d.jpg
        self._context_actions_layout.addWidget(self._actions_gb)
        self._context_actions_layout.addWidget(self._context_gb)
        self._main_layout.addWidget(self.goal_target)
        self._main_layout.addLayout(self._context_actions_layout)

    def __init__(self, exercise: Exercise, first_goal: Goal):
        super().__init__()
        self.exercise = exercise
        self._init_all_layout_boxes()
        self._init_actions()
        self._init_goal()
        self._init_put_widgets_in_layouts()
        self.setLayout(self._main_layout)


class ExerciseMainWindow(QMainWindow):

    pass
