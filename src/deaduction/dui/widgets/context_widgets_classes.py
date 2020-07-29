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
from PySide2.QtGui import QBrush, QColor, QIcon
from PySide2.QtWidgets import (QLabel,
                               QWidget,
                               QListWidget,
                               QListWidgetItem)
from deaduction.pylib.mathobj import ProofStatePO

#############
# Utilities #
#############


class _TagIcon(QIcon):

    def __init__(self, tag: str):
        icons_folder = Path('share/graphical_resources/icons/')

        if tag not in ['=', '+', '≠']:
            raise ValueError('tag must be one of "=", "+", "≠". tag: {tag}.')
        elif tag == '=':
            super().__init__('')  # No icon, empty icon trick
            return None
        elif tag == '+':
            icon_path = icons_folder / 'tag_plus.png'
        elif tag == '≠':
            icon_path = icons_folder / 'tag_different.png'

        super().__init__(str(icon_path.resolve()))


###############################
# ProofStatePO widget classes #
###############################


class ProofStatePOItem(QListWidgetItem):

    def __init__(self, proofstatepo: ProofStatePO, tag: str):
        super().__init__()
        # Set icon
        self.setIcon(_TagIcon(tag))
        # Set text
        caption = f'{proofstatepo.format_as_utf8()} : ' \
                  f'{proofstatepo.math_type.format_as_utf8()}'
        self.setText(caption)

        # User cannot have selected it before the init
        self.is_user_selected = False

    def __eq__(self, other):
        """
        Do not delete! Useful for 'for pspoitem in list:' stuff, used
        to check if an item is in the current user selection.
        """
        return self is other

    def mark_user_selected(self, yes=True):
        if yes:
            brush = QBrush(QColor('limegreen'))
        else:
            brush = QBrush()

        self.is_user_selected = yes
        self.setBackground(brush)


class ProofStatePOWidget(QListWidget):

    def __init__(self,
            tagged_proofstatepos: List[Tuple[ProofStatePO, str]]=[]):
        super().__init__()
        for proofstatepo, tag in tagged_proofstatepos:
            self.addItem(ProofStatePOItem(proofstatepo, tag))


#######################
# Target widget class #
#######################


class TargetLabel(QLabel):

    def __init__(self, target: ProofStatePO=None, tag: str=None):
        super().__init__()
        # Display
        #   ∀ x ∈ X, ∃ ε, …
        # and not
        #   H : ∀ x ∈ X, ∃ ε, …
        # where H might be the lean name of the target. That's what
        # the .math_type is for.
        self.setText(target.math_type.format_as_utf8() if target else '…')
        if tag:
            self.setIcon(_TagIcon(tag))

        # Cosmetics
        self.setStyleSheet('font-size: 24px;')


class TargetWidget(QWidget):

    def __init__(self, target: ProofStatePO=None, tag: str=None):
        super().__init__()
        self.target = target
        self.tag = tag

        self.target_label = TargetLabel(self.target, self.tag)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.target_label)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)
