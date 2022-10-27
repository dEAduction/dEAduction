"""
base_math_widgets_styling.py : provide the MathLabel, MathItem and
MathTextWidget classes that takes care of html stylesheet.

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
    Also provides the following methods:
    - set_use_color: enable/disable use of colors, default = True.
    - set_text_mode: if text_mode is True then systems font will be used
    except for maths elements. Default is False.
    (- set_font_size. This is unused.)
    """

    def __init__(self, use_color=True, font_size=None, text_mode=False):
        self.use_color = use_color
        self.font_size = font_size  # FIXME: not used
        self.text_mode = text_mode

    def set_use_color(self, yes=True):
        self.use_color = yes

    def set_font_size(self, size):
        self.font_size = size

    def set_text_mode(self, yes=True):
        self.text_mode = yes

    def math_font_style(self):
        fonts_name = deaduction_fonts.math_fonts_name
        # print(f"Math font name: {fonts_name}")
        if not fonts_name:
            return ""

        if not self.text_mode:
            style = f"* {{ font-family: {fonts_name} }}"
        else:
            style = f".math, .variable, .dummy_variable, .used_prop" \
                    f"{{ font-family: {fonts_name} }}"

        return style

    def text_font_style(self):
        fonts_name = deaduction_fonts.fonts_name
        if not self.text_mode or not fonts_name:
            return ""

        style = f"*, .text {{ font-family: {fonts_name} }}"
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
    def html_style(self):
        style = ("<style> " + self.text_font_style()
                 + self.math_font_style() + self.color_styles()
                 + "</style>")
        return style


class MathLabel(QLabel, AbstractMathHtmlText):
    """
    A QLabel subclass to display math in html, incorporating styling.
    """

    def __init__(self):
        super().__init__()
        self.set_use_color()
        self.set_text_mode(False)

    def setText(self, text: str):
        super().setText(self.html_style + '<div>' + text + '</div>')


class MathItem(QStandardItem, AbstractMathHtmlText):
    """
    A QStandardItem subclass to display math in html, incorporating styling.
    """
    def __init__(self):
        super().__init__()
        self.set_use_color()
        self.set_text_mode(False)

    def setText(self, text: str):
        super().setText(self.html_style + '<div>' + text + '</div>')


class MathTextWidget(QTextEdit, AbstractMathHtmlText):
    """
    A QTextEdit subclass to display math in html, incorporating styling.
    """
    def __init__(self):
        super().__init__()
        self.set_use_color()
        self.set_text_mode(False)

    def setHtml(self, text: str):
        # print(self.html_style + text)
        super().setHtml(self.html_style + '<div>' + text + '</div>')












