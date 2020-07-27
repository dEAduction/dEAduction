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
from typing import List, Tuple
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QListWidget, QListWidgetItem


###############################
# ProofStatePO widget classes #
###############################


class _TagIcon(QIcon):

    def __init__(self, tag: str):
        icons_folder = Path('../graphical_resources/')

        if tag not in ['=', '+', '≠']:
            raise ValueError('tag must be one of "=", "+", "≠". tag: {tag}.')
        elif tag == '=':
            super().__init__('')  # No icon, empty icon trick
            return None
        elif tag == '+':
            icon_path = icons_folder / 'icon_tag_plus.png'
        elif tag == '≠':
            icon_path = icons_folder / 'icon_tag_different.png'

        super().__init__(str(icon_path.resolve()))


class ProofStatePOItem(QListWidgetItem):

    def __init__(self, proofstatepo: ProofStatePO, tag: str):
        super().__init__()
        # Set icon
        self.setIcon(_TagIcon(tag))
        # Set text
        caption = f'{proofstatepo.format_as_utf8()} : ' \
                  f'{proofstatepo.math_type.format_as_utf8()}'
        self.setText(caption)


class ProofStatePOWidget(QListWidget):

    def __init__(self, tagged_proofstatepos: List[Tuple[ProofStatePO, str]]):
        super().__init__()
        for proofstatepo, tag in tagged_proofstatepos:
            self.addItem(ProofStatePOItem(proofstatepo, tag))


#######################
# Target widget class #
#######################


class _TargetButton(QPushButton):

    def _initUI(self):
        """
        Set cosmetics.
        """

        self.resize_width()
        self.setFlat(True)
        self.setStyleSheet('font-size: 24px;')

        # Resize the button to be about the size of the displayed text.
        text_width = self.fontMetrics().boundingRect(self.text()).width()
        self.setFixedWidth(text_width + 40)


    def __init__(self, target: ProofStatePO):
        super().__init__()
        self.target = target

        # Display
        #   ∀ x ∈ X, ∃ ε, …
        # and not
        #   H : ∀ x ∈ X, ∃ ε, …
        # where H might be the lean name of the target. That's what
        # the .math_type is for.
        self.setText(target.math_type.format_as_utf8())

        self._initUI()


class TargetWidget(QWidget):

    def __init__(self, target: ProofStatePO):
        super().__init__()
        self.target = target
        self.button = _TargetButton(target)

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.button)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)
