"""
calculator.py : provide the CalculatorButton class, whose main feature is
that the text displayed is in html. There is also a sophisticated system of (
automatically computed) shortcuts.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 06 2023 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2023 the d∃∀duction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    d∃∀duction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging

from PySide2.QtCore import Qt
from PySide2.QtGui     import  QTextDocument
from PySide2.QtWidgets import (QToolButton,
                               QHBoxLayout,
                               QSizePolicy, QMenu, QAction)

from deaduction.dui.primitives          import (MathLabel)

global _
log = logging.getLogger(__name__)


class RichTextToolButton(QToolButton):
    """
    An html QToolButton.
    """
    def __init__(self, parent=None, text=None):
        if parent is not None:
            super().__init__(parent)
        else:
            super().__init__()
        # self.__lbl = QLabel(self)
        self.__lbl = MathLabel()
        if text is not None:
            self.__lbl.setText(text)
        self.__lyt = QHBoxLayout()
        self.__lyt.setContentsMargins(0, 0, 0, 0)
        self.__lyt.setSpacing(0)
        self.setLayout(self.__lyt)
        self.__lbl.setAttribute(Qt.WA_TranslucentBackground)
        self.__lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.__lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Horizontal alignment:
        self.__lbl.setAlignment(Qt.AlignCenter)
        # self.__lyt.setAlignment(Qt.AlignCenter)
        self.__lbl.setTextFormat(Qt.RichText)
        self.__lbl.setMaximumHeight(22)
        self.__lyt.addStretch()
        self.__lyt.addWidget(self.__lbl)
        self.__lyt.addStretch()

        # self.setFixedSize(70, 30)
        self.setMinimumSize(70, 30)
        return

    def setText(self, text):
        self.__lbl.setText(text.strip())
        self.updateGeometry()
        return

    def text(self):
        html_text = self.__lbl.text()
        doc = QTextDocument()
        doc.setHtml(html_text)
        text = doc.toPlainText()
        return text

    def sizeHint(self):
        # FIXME: probably useless?
        s = QToolButton.sizeHint(self)
        w = self.__lbl.sizeHint()
        s.setWidth(max(w.width() + 10, 40))
        # s.setHeight(max(w.height() + 10, 30))
        s.setHeight(max(w.height(), 30))
        return s

    def set_font(self, font):
        self.__lbl.setFont(font)

    def set_text_mode(self, yes=True):
        self.__lbl.set_text_mode(yes)
