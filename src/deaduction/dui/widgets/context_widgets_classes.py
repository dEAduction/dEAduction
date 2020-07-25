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
from typing import List
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QHBoxLayout, QPushButton, QLabel


##############################
# ProofStatePOLayout classes #
##############################



class _TagIcon(QLabel):

    def __init__(self, tag: str):
        super().__init__()
        icons_folder = Path('../graphical_resources/')

        if tag not in ['=', '+', '≠']:
            raise ValueError('tag must be one of "=", "+", "≠". tag: {tag}.')
        elif tag == '=':
            return None
        elif tag == '+':
            icon_path = icons_folder / 'icon_tag_plus.png'
        elif tag == '≠':
            icon_path = icons_folder / 'icon_tag_different.png'

        icon_pixmap = QPixmap(str(icon_path.resolve()))
        icon_pixmap = icon_pixmap.scaledToWidth(10)
        self.setPixmap(icon_pixmap)


class _ProofStatePOButton(QPushButton):

    def __init__(self, proofstatepo: ProofStatePO):
        super().__init__()
        caption = f'{proofstatepo.format_as_utf8()} : ' \
                  f'{proofstatepo.math_type.format_as_utf8()}'
        self.setText(caption)


class ProofStatePOItem(QHBoxLayout):

    def __init__(self, proofstatepo: ProofStatePO, tag: str):
        super().__init__()
        self.tag_icon = _TagIcon(tag)
        self.pspo_button = _ProofStatePOButton(proofstatepo)

        self.addWidget(self.tag_icon)
        self.addWidget(self.pspo_button)


class ProofStatePOLayout(QVBoxLayout):

    def __init__(self, proofstatepos: List[ProofStatePO]):
        super().__init__()
        for proofstatepo in proofstatepos:
            self.addLayout(ProofStatePOItem(proofstatepo))


#######################
# Target widget class #
#######################


class TargetWidget(QPushButton):

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
