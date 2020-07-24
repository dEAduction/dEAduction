"""
###################################################################
# context_widgets_classes.py : context widgets for ExerciseWidget #
###################################################################

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

from pathlib import Path
from PySide2.QtWidgets import QHBoxLayout, QPushButton, QLabel

class ProofStatePOLayout(QHBoxLayout):

    def __init__(self, proofstatepo: ProofStatePO, tag: str):
        super().__init__()

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, tag):
        icons_folder = Path('../graphical_resources/')

        if tag not in ['+', '≠', '=']:
            raise ValueError('ProofStatePOLayout.tag must be one of "+", "="'
