"""
########################################################
# exercisewidget.py : provide the ExerciseWidget class #
########################################################

Author(s)      : - Kryzar <antoine@hugounet.com>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : - Kryzar <antoine@hugounet.com>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>
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

import logging
from gettext import gettext as _
from pathlib import Path

from PySide2.QtCore import (    Signal,
                                Slot,
                                Qt)
from PySide2.QtGui import       QIcon
from PySide2.QtWidgets import ( QAction,
                                QGroupBox,
                                QHBoxLayout,
                                QMainWindow,
                                QToolBar,
                                QVBoxLayout,
                                QWidget)

from deaduction.dui.utils import        replace_delete_widget
from deaduction.dui.widgets import (    ActionButtonsWidget,
                                        StatementsTreeWidget,
                                        ProofStatePOWidget,
                                        ProofStatePOWidgetItem,
                                        TargetWidget)
from deaduction.pylib.coursedata import Exercise
from deaduction.pylib.mathobj import    Goal
from deaduction.pylub.server import     ServerInterface

log = logging.getLogger(__name__)


###########
# Widgets #
###########


class ExerciseToolbar(QToolBar):

    def __init__(self):
        super().__init__(_('Toolbar'))

        icons_dir = Path('graphical_resources/icons/')
        self.undo_action = QAction(
            QIcon(str((icons_dir / 'undo_action.png').resolve()),
            _('Undo action'), self)
        self.undo_action = QAction(
            QIcon(str((icons_dir / 'redo_action.png').resolve()),
            _('Redo action'), self)
        self.undo_action = QAction(
            QIcon(str((icons_dir / 'clear_selection.png').resolve()),
           _('Undo action'), self)


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
        self.logic_btns = ActionButtonsWidget(self.exercise.available_logic)
        # Init proof techniques buttons
        self.proof_techniques_btns = ActionButtonsWidget(
                self.exercise.available_proof_techniques)
        # Init statements tree
        statements = self.exercise.available_statements
        outline = self.exercise.course.outline
        self.statements_tree = StatementsTreeWidget(statements, outline)

    def _init_goal(self):
        # Create empty widgets while waiting for Lean
        self.current_goal = None
        self.objects_wgt = ProofStatePOWidget()
        self.props_wgt = ProofStatePOWidget()
        self.target_wgt = TargetWidget()

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

    def __init__(self, exercise: Exercise):
        super().__init__()
        self.exercise = exercise
        self._init_all_layout_boxes()
        self._init_actions()
        self._init_goal()
        self._init_put_widgets_in_layouts()
        self.setLayout(self._main_lyt)

    def update_goal(self, new_goal: Goal):

        # Init context (objects and properties). Get them as two list of
        # (ProofStatePO, str), the str being the tag of the prop. or obj.
        new_context = new_goal.tag_and_split_propositions_objects()
        new_objects_wgt = ProofStatePOWidget(new_context[0])
        new_props_wgt = ProofStatePOWidget(new_context[1])
        new_target = new_goal.target
        new_target_tag = new_target.future_tags[1]
        new_target_wgt = TargetWidget(new_target, new_target_tag)

        # Replace in the layouts
        replace_delete_widget(self._context_lyt,
                              self.objects_wgt, new_objects_wgt)
        replace_delete_widget(self._context_lyt,
                              self.props_wgt, new_props_wgt)
        replace_delete_widget(self._main_lyt,
                              self.target_wgt, new_target_wgt,
                              ~Qt.FindChildrenRecursively)

        # Set the attributes to the new values
        self.objects_wgt = new_objects_wgt
        self.props_wgt = new_props_wgt
        self.target_wgt = new_target_wgt
        self.current_goal = new_goal


###############
# Main window #
###############


class ExerciseMainWindow(QMainWindow):

    window_closed = Signal()

    ################
    # Init methods #
    ################

    def _init_signals_slots(self):
        self.exercise_cw.objects_wgt.clicked.connect(
                self.process_context_click)
        self.exercise_cw.props_wgt.clicked.connect(
                self.process_context_click)

    def __init__(self, exercise: Exercise, servint: ServerInteface):
        super().__init__()
        self.exercise = exercise
        self.exercise_cw = ExerciseCentralWidget(self.exercise)
        self.current_context_selection = []
        self.servint = servint
        self.toolbar = ExerciseToolBar()

        self.setCentralWidget(self.exercise_cw)
        self.addToolBar(self.toolbar)
        self._init_signals_slots()
        # Start server task
        self.servint.nursery.start_soon(self.server_task)

    ###########
    # Methods #
    ###########
    
    def closeEvent(self, event):
        super().closeEvent(event)
        self.window_closed.emit()

    def pretty_user_selection(self):
        msg = 'Current user selection: '
        msg += str([item.text() for item in self.current_context_selection])

        return msg

    ###############
    # Async tasks #
    ###############
   
    async def server_task(self):
        await self.servint.exercise_set(self.exercise)
        async with qtio.enter_emissions_channel(
                signals=[self.window_closed]) as emissions:
            async for emission in emissions.channel:
                if emission.is_from(self.window_closed):
                    break

    #########
    # Slots #
    #########

    @Slot()
    def clear_user_selection(self):
        log.debug('Clearing user selection')
        for item in self.current_context_selection:
            item.mark_user_selected(False)

        self.current_context_selection = []
        log.debug(self.pretty_user_selection())

    @Slot()
    def freeze(yes=True):
        self.setEnabled(not yes)

    @Slot(ProofStatePOWidgetItem)
    def process_context_click(self, item: ProofStatePOWidgetItem):
        log.debug('Recording user selection')
        item.setSelected(False)

        if not item.is_user_selected:
            if item not in self.current_context_selection:
                item.mark_selected(True)
                self.current_context_selection.append(item)
        elif item.is_user_selected:
            item.mark_selected(False)
            self.current_context_selection.remove(item)

        log.debug(self.pretty_user_selection())
