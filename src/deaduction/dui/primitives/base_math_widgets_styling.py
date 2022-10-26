"""
base_math_widgets_styling.py : provide the MathLabel class that takes care of html stylesheet.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 10 2022 (creation)
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

from PySide2.QtWidgets import QLabel, QTextEdit
from PySide2.QtGui import QStandardItem

import deaduction.pylib.config.vars as cvars
from .font_config import deaduction_fonts


def color_dummy_variables():
    return (cvars.get('display.color_for_dummy_variables', None)
            if cvars.get('logic.use_color_for_dummy_variables', True)
            else None)


def color_variables():
    return (cvars.get('display.color_for_variables', None)
            if cvars.get('logic.use_color_for_variables', True)
            else None)


def color_props():
    return (cvars.get('display.color_for_applied_properties', None)
            if cvars.get('logic.use_color_for_applied_properties', True)
            else None)


class AbstractMathHtmlText:
    """
    A class to display math text in html, or msgs related to maths.
    Essentially compute the style in html format for the richtext content.
    """

    def __init__(self, use_color, font_size):
        self.use_color = use_color
        self.font_size = font_size  # FIXME: not used

    @staticmethod
    def math_font_style():
        fonts_name = deaduction_fonts.math_fonts_name
        if fonts_name:
            style = f".math, .variable, .dummy_variable, .used_prop" \
                    f"{{ font-family: {fonts_name} }}"
        else:
            style = ""

        return style

    @staticmethod
    def text_font_style():
        fonts_name = deaduction_fonts.fonts_name
        if fonts_name:
            style = f"*, .text {{ font-family: {fonts_name} }}"
        else:
            style = ""

        return style

    def color_styles(self):
        if self.use_color:
            style = f".variable  {{ color: {color_variables()} }}" \
                    f".dummy_variable  {{ color: {color_dummy_variables()} }}" \
                    f".used_prop  {{ color: {color_props()} }}"
        else:
            style = ""

        return style

    @property
    def style(self):
        style = ("<style> " + self.text_font_style()
                 + self.math_font_style() + self.color_styles()
                 + "</style>")
        return style


class MathLabel(QLabel):
    """
    A QLabel subclass to display math in html, incorporating styling.
    """

    def __init__(self, use_color=True, font_size=None):
        self.abstract_html_text = AbstractMathHtmlText(use_color=use_color,
                                                       font_size=font_size)
        super().__init__()

    @property
    def style(self):
        return self.abstract_html_text.style

    def setText(self, text: str):
        super().setText(self.style + text)


class MathItem(QStandardItem):
    """
    A QStandardItem subclass to display math in html, incorporating styling.
    """
    def __init__(self, use_color=True, font_size=None):
        self.abstract_html_text = AbstractMathHtmlText(use_color=use_color,
                                                       font_size=font_size)
        super().__init__()

    @property
    def style(self):
        return self.abstract_html_text.style

    def setText(self, text: str):
        super().setText(self.style + text)


class MathTextWidget(QTextEdit):
    """
    A QStandardItem subclass to display math in html, incorporating styling.
    """
    def __init__(self, use_color=True, font_size=None):
        self.abstract_html_text = AbstractMathHtmlText(use_color=use_color,
                                                       font_size=font_size)
        super().__init__()

    @property
    def style(self):
        return self.abstract_html_text.style

    # def setText(self, text: str):
    #     super().setText(self.style + text)

    def setHtml(self, text: str):
        super().setHtml(self.style + text)












