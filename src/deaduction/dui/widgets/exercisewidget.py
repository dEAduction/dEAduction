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

from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout
from PySide2.QtWidgets import QWidget


class ExerciseWidget(QWidget):

    def _init_layouts(self):
        """
        Initiate > all < the layouts in the windows.
        TODO: draw the damn thing.
        """

        self._main_layout =             QVBoxLayout()
        self._target_layout =           QHBoxLayout()
        self._context_actions_layout =  QHBoxLayout()
        self._context_layout =          QVBoxLayout() 
        self._actions_layout =          QVBoxLayout()
        self._logic_buttons_layout =    QHBoxLayout()
        self._proof_buttons_layout =    QHBoxLayout()

    def _init_actions(self):
        """
        Init the 'Actions' part of the interface, that is logic
        buttons, proof techniques buttons and available statements.
        Those will never change during the life of the exercise.
        """

    def __init__(self, exercise: Exercise):
        super().__init__()
        # Appeler server_interface.exercise_set(self)
        self.exercise = exercise
        _init_layouts()
        _init_actions()
