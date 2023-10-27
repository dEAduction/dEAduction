"""
calculator.py : provide the CalculatorButton class.

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

if __name__ == '__main__':
    from deaduction.dui.__main__ import language_check
    language_check()

import logging

from PySide2.QtCore import Signal, Slot, Qt
from PySide2.QtGui     import  QTextDocument
from PySide2.QtWidgets import (QToolButton,
                               # QPushButton,
                               QHBoxLayout,
                               QLabel,
                               QSizePolicy)

from deaduction.pylib.pattern_math_obj import (MarkedPatternMathObject,
                                               calc_shortcuts_macro)
from deaduction.pylib.pattern_math_obj.calculator_pattern_strings import CalculatorAbstractButton

from deaduction.dui.primitives          import deaduction_fonts


global _
log = logging.getLogger(__name__)

if __name__ == "__main__":
    from deaduction.pylib import logger
    logger.configure(domains="deaduction",
                     display_level="debug",
                     filename=None)


class RichTextToolButton(QToolButton):
    def __init__(self, parent=None, text=None):
        if parent is not None:
            super().__init__(parent)
        else:
            super().__init__()
        self.__lbl = QLabel(self)
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


class CalculatorButton(RichTextToolButton, CalculatorAbstractButton):
    """
    A class to display a button associated to a (list of)
    MarkedPatternMathObjects. Pressing the button insert (one of) the pattern
    at the current cursor position in the MarkedPatternMathObject under
    construction.

    shortcut_dic is a dictionary with
        keys = shortcuts (strings typed by usr)
        values = list of CalculatorButton whose shortcut startswith the key,
                ordered by length
    A given button appear in the dic for all keys that are starting sub-words
    of self.shortcut.
    """

    send_pattern = Signal(MarkedPatternMathObject)

    shortcuts_dic = dict()

    def __init__(self, symbol, tooltip=None, patterns=None, menu=False):
        super().__init__()
        CalculatorAbstractButton.__init__(self, symbol, tooltip, patterns, menu)
        # self.patterns = CalculatorPatternLines.marked_patterns[symbol]

        # action = QAction(self.symbol)
        # action.triggered.connect(self.process_click)
        # self.setDefaultAction(action)
        self.clicked.connect(self.process_click)
        self.setText(symbol)
        self.shortcut = ''
        self.add_shortcut()
        self.set_tooltip()
        symbol_size = deaduction_fonts.symbol_button_font_size
        self.set_font(deaduction_fonts.math_fonts(size=symbol_size))

    def set_tooltip(self):
        tooltip = ""
        if self.shortcut:
            tooltip = "(type " + self.shortcut + ")"
        if self.tooltip:
            tooltip = self.tooltip + "\n" + "\n" + tooltip if tooltip \
                else self.tooltip
        if tooltip:
            self.setToolTip(tooltip)

        symbol_size = deaduction_fonts.symbol_button_font_size
        self.setFont(deaduction_fonts.math_fonts(size=symbol_size))

    def insert_by_length(self, calc_buttons: list):
        """
        Insert string s in list l, ordered by length.
        """

        if not calc_buttons:
            calc_buttons.append(self)

        idx = None  # note that calc_buttons is not the trivial list
        broken = False
        for idx in range(len(calc_buttons)):
            button = calc_buttons[idx]
            if len(self.text()) < len(button.text()):
                broken = True
                break
            elif self is button:
                return

        if broken:
            calc_buttons.insert(idx, self)
        else:  # self is the longest
            calc_buttons.append(self)

    def reset_text(self, text):
        self.setText(text)
        self.shortcut = ''
        self.add_shortcut()

    def add_shortcut(self):
        """
        Add a pertinent beginning of self.text() as a shortcut for self.

        If the text of some button is a beginning word of one or more others,
        its shortcut will be a tuple containing all these buttons.

        If two buttons have the same text, only one will have a shortcut.
        """

        text = self.text()

        # (0) Macros
        # Case of calc_shortcuts_macro, mainly latex-like patterns, e.g. \implies
        for key, value in calc_shortcuts_macro.items():
            if text.startswith(value):
                text = text.replace(value, key)

        shortcut = ''
        sdic = self.shortcuts_dic

        for car in text:
            shortcut += car
            # if shortcut == 'l':
            #     print('hlleo')
            conflicting_buttons = sdic.get(shortcut, [])
            self.insert_by_length(conflicting_buttons)
            sdic[shortcut] = conflicting_buttons

            # if shortcut in sdic:
            #     # Modify conflicting shortcut
            #     conflicting_button = sdic.get(shortcut)
            #     if isinstance(conflicting_button, tuple):
            #         conflicting_button = conflicting_button[0]
            #     conflicting_text = conflicting_button.text()
            #     new_length = len(shortcut) + 1
            #
            #     if len(conflicting_text) >= new_length:
            #         new_shortcut = conflicting_button.text()[:new_length]
            #         sdic[new_shortcut] = conflicting_button
            #         if len(text) == new_length - 1:
            #             # conflicting_text is a proper starting word of
            #             # self.text()
            #             sdic[shortcut] = (self, conflicting_button)
            #     elif len(text) >= new_length:
            #         # self.text() is a proper starting word of
            #         # conflicting_text
            #         sdic[shortcut] = (conflicting_button, self)
            #     # NB: if both conflicting_text and self.text() have length <
            #     # new_length, then they coincide, and self will have no
            #     # shortcut.
            #
            # else:
            #     sdic[shortcut] = self

        # if ((len(conflicting_buttons) == 1
        #         or (shortcut == text and conflicting_buttons[0] is self))
        #         and not self.shortcut):
        #     self.shortcut = shortcut

        if shortcut in sdic and sdic[shortcut][0] == self:
            self.shortcut = shortcut

    @classmethod
    def find_shortcut(cls, text_buffer, timeout=False, text_is_macro=False):
        """
        If timeout is False, and one and only one shortcut match text_buffer,
        return the corresponding button.

        If timeout is True:
        If only one shortcut match text_buffer (i.e. has text_buffer as a
        sub-word), return the corresponding
        button, even if there may be some other shortcut starting with
        text_buffer.


        """

        buttons = cls.shortcuts_dic.get(text_buffer)
        if buttons and (len(buttons) == 1 or timeout):
            return buttons[0]

        # Try to find text in calc_shortcuts_macro
        if not text_is_macro:
            macro = calc_shortcuts_macro.get(text_buffer)
            if macro:
                button = cls.find_shortcut(text_buffer=macro, timeout=timeout,
                                           text_is_macro=True)
                return button

        # # FIXME: not optimal
        # match = [key for key in cls.shortcuts_dic if key.startswith(text_buffer)]
        # more_match = [calc_shortcuts_macro[key] for key in calc_shortcuts_macro
        #               if key.startswith(text_buffer)
        #               and calc_shortcuts_macro[key] in cls.shortcuts_dic]
        # match += more_match
        # if len(match) == 1:
        #     return cls.shortcuts_dic[match[0]]
        # elif len(match) > 1:
        #     # OK if all shortcuts refer to the same text
        #     first_match = match[0]
        #     test = all(cls.shortcuts_dic[other_match].text() ==
        #                cls.shortcuts_dic[first_match].text()
        #                for other_match in match[1:])
        #     if test:
        #         # Several match of 'the same' button
        #         return cls.shortcuts_dic[match[0]]

    @Slot()
    def process_click(self):
        """
        Send a signal so that Calculator process the click.
        """
        self.send_pattern.emit(self.patterns)

    @classmethod
    def process_key_events(cls, key_event_buffer, timeout=False):
        # button = cls.shortcuts_dic.get(key_event_buffer)
        button = cls.find_shortcut(key_event_buffer, timeout)
        if button:
            button.animateClick(100)
            return True



