"""
########################################################
# exercisewidget.py : provide the ExerciseWidget class #
########################################################

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

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout
from PySide2.QtWidgets import QMainWindow, QWidget

def _replace_widget_in_layout(layout: QLayout, old: QWidget, new: QWidget,
        flag=Qt.FindChildrenRecursively):
    layout.replaceWidget(old, new, flag)
    old.deleteLater()

class ExerciseCentralWidget(QWidget):

    def _init_all_layout_boxes(self):
        # TODO: draw the damn thing

        # Layouts
        self._main_lyt = QVBoxLayout()
        self._context_actions_lyt = QHBoxLayout()
        self._context_lyt = QVBoxLayout()
        self._actions_lyt = QVBoxLayout()

        # Group boxes
        self._actions_gb = QGroupBox(_('Actions (transform context)'))
        self._context_gb = QGroupBox(_('Context (properties and objects)'))

    def _init_actions(self):
        # Init tool buttons
        self.logic_btns = \
                ActionButtonsWidget(self.exercise.available_logic)
        # Init proof techniques buttons
        self.proof_techniques_btns = \
                ActionButtonsWidget(self.exercise.available_proof_techniques)
        # Init statements tree
        self.statements_tree = \
                StatementsTreeWidget(self.exercise.available_statements,
                                     self.exercise.course.outline) 

    def _init_goal(first_goal: Goal):
        self.current_goal = first_goal

        # Get objects and properties as two list of (ProofStatePO, 
        # str), the str being the tag of the prop. or obj.
        context = self.current_goal.tag_and_split_propositions_objects()
        self.objects_wgt = ProofStatePOWidget(context[0])
        self.props_wgt = ProofStatePOWidget(context[1])
        # Finally the target
        self.target_wgt = TargetWidget(self.current_goal.target)

    def _init_put_widgets_in_layouts(self):
        # Actions
        self._actions_lyt.addWidget(self.logic_btns)
        self._actions_lyt.addWidget(self.proof_techniques_btns)
        self._actions_lyt.addWidget(self.statements_tree)
        self._actions_gb.setLayout(self._actions_lyt)

        # Context
        self._context_lyt.addWidget(self.objects_wgt)
        self._context_lyt.addWidget(self.props_wgt)
        self._context_gb.setLayout(self._context_lyt)

        # https://i.kym-cdn.com/photos/images/original/001/561/446/27d.jpg
        self._context_actions_lyt.addWidget(self._actions_gb)
        self._context_actions_lyt.addWidget(self._context_gb)
        self._main_lyt.addWidget(self.target_wgt)
        self._main_lyt.addLayout(self._context_actions_lyt)

    def __init__(self, exercise: Exercise, first_goal: Goal):
        super().__init__()
        self.exercise = exercise
        self._init_all_layout_boxes()
        self._init_actions()
        self._init_goal()
        self._init_put_widgets_in_layouts()
        self.setLayout(self._main_lyt)

    def update_goal(self, new_goal: Goal):

        # Get new objects
        new_context = new_goal.tag_and_split_propositions_objects()
        new_objects_wgt = ProofStatePOWidget(new_context[0])
        new_props_wgt = ProofStatePOWidget(new_context[1])
        new_target_wgt = TargetWidget(self.current_goal.target)

        # Replace in the layouts
        _replace_widget_in_lyt(self._context_lyt,
                               self.objects_wgt, new_objects_wgt)
        _replace_widget_in_layout(self._context_lyt,
                                  self.props_wgt, new_props_wgt)
        _replace_widget_in_layout(self._main_lyt,
                                  self.target_wgt, new_target_wgt,
                                  ~Qt.FindChildrenRecursively)

        # Set the attributes to the new values
        self.objects_wgt = new_objects_wgt
        self.props_wgt = new_props_wgt
        self.target_wgt = new_target_wgt
        self.current_goal = new_goal        


class ExerciseMainWindow(QMainWindow):

    def __init__(self, exercise: Exercise):
        super().__init__()
        self.exercise = exercise
        self.setCentralWidget(ExerciseCentralWidget(exercise))
