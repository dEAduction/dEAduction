"""
# font_config.py : <#ShortDescription> #
    
    <#optionalLongDescription>

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 10 2021 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the d∃∀duction team

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

import sys
from PySide2.QtGui import QFontDatabase, QFont, QFontMetrics
from PySide2.QtWidgets import QApplication

import deaduction.pylib.config.vars as cvars


class DeaductionFonts:
    """Provides fonts for deaduction, one for text and one for mathematics,
    and provides alternative characters for missing ones.

    :attribute alt_characters   dict    for each character as a key which
    could be missing, use the value instead. If the character is available
    then value = key.
    """
    dubious_characters = {'ℕ': 'N',
                          'ℤ': 'Z',
                          'ℚ': 'Q',
                          'ℝ': 'R',
                          "𝒫": "P",
                          "↦": "→"
                          }

    def __init__(self, parent: QApplication):
        self.parent = parent
        font_size = cvars.get("display.chooser_math_font_size", "14pt")
        self.chooser_math_font_size = int(font_size[:-2])
        font_size = cvars.get("display.main_font_size", "16pt")
        self.main_font_size = int(font_size[:-2])
        font_size = cvars.get("display.target_font_size", "20pt")
        self.target_font_size = int(font_size[:-2])
        symbol_size = cvars.get('display.font_size_for_symbol_buttons', "14pt")
        self.symbol_button_font_size = int(symbol_size[:-2])
        self.tooltips_font_size = cvars.get('display.tooltips_font_size',
                                            "14pt")

        self.alt_characters = {}
        in_font = QFontMetrics(self.math_font()).inFont
        for default in self.dubious_characters:
            if in_font(default):
                self.alt_characters[default] = default
            else:
                self.alt_characters[default] = self.dubious_characters[default]

    def math_font(self):
        math_font = cvars.get("display.mathematics_font", None)
        if math_font:
            return QFont(math_font)
        else:
            return self.parent.font()

    def background_color(self):
        return cvars.get("display.selection_color", "limegreen")


# class MissingCharacters:
#     @classmethod
#     def dic(cls):

