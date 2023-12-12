"""
# font_config.py : load fonts for deaduction #
    

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

# TODO:
#  - charger les fontes dès le début, utiliser un setStylesheet avec un tag
#  math_widget, cf ProofTree:
#          self.setStyleSheet('QWidget#math_widget {font-family: Times
#          New Roman;'
#           self.setObjectName("math_widget_medium")
#  - settings
#       --> use system fonts for menus y/n
#  -    --> use custom file for math fonts


import logging
from PySide2.QtGui import QFontDatabase, QFont, QFontMetrics
from PySide2.QtWidgets import QApplication

import deaduction.pylib.config.vars as cvars
import deaduction.pylib.config.dirs as cdirs

log = logging.getLogger(__name__)


class DeaductionFonts:
    """Provides fonts for deaduction, one for text and one for mathematics,
    and provides alternative characters for missing ones.

    :attribute alt_characters   dict    for each character as a key which
    could be missing, use the value instead. If the character is available
    then value = key.
    """
    # dubious_characters_dic = {'ℕ': 'N',
    #                       'ℤ': 'Z',
    #                       'ℚ': 'Q',
    #                       'ℝ': 'R',
    #                       "𝒫": "P",
    #                       "↦": "→"
    #                       }
    # dubious_characters = ['ℕ', 'ℤ', 'ℚ', 'ℝ', "𝒫", "↦"]
    system_fonts = None

    def __init__(self, parent: QApplication = None):
        self.parent = parent
        self.fonts_name = ""
        self.math_fonts_name = ""
        self.loaded_fonts_files = []
        self.loaded_fonts_name = []

    @property
    def chooser_math_font_size(self):
        font_size = cvars.get("display.chooser_math_font_size", "16pt")
        return int(font_size[:-2])

    @property
    def main_font_size(self):
        font_size = cvars.get("display.main_font_size", "16pt")
        return int(font_size[:-2])

    @property
    def statements_font_size(self):
        font_size = cvars.get("display.statements_font_size", "14pt")
        return int(font_size[:-2])

    @property
    def target_font_size(self):
        font_size = cvars.get("display.target_font_size", "20pt")
        return int(font_size[:-2])

    @property
    def symbol_button_font_size(self):
        symbol_size = cvars.get('display.font_size_for_symbol_buttons')
        return int(symbol_size[:-2]) if symbol_size else None

    @property
    def tooltips_font_size(self):
        return cvars.get('display.tooltips_font_size', "14pt")

    def set_parent(self, parent):
        self.parent = parent

    @property
    def math_fonts_files(self):
        files = [file for file in cdirs.fonts.iterdir()
                 if file.suffix in ('.ttf', '.otf')]
        return files

    @property
    def math_fonts_file_names(self):
        return [file.name for file in self.math_fonts_files]

    @property
    def math_fonts_file_name(self):
        """
        Return the name of the file that should be used for maths fonts,
        or None if system fonts should be used.
        """
        # os = cvars.get("others.os", "linux")
        # file = cvars.get("display.math_font_file_for_windows",
        #                  "DejaVuMathTeXGyre.ttf") if os == "windows" \
        #     else cvars.get("display.math_font_file", "latinmodern-math.otf")
        # return file
        return cvars.get("display.math_font_file")

    @property
    def system_fonts_name(self):
        if self.system_fonts:
            return self.system_fonts.family()

    @property
    def style_sheet_size(self):
        """
        Return style_sheet string for font sizes.
        """
        #

        s = (
             #########################
             # ExerciseChooser sizes #
             #########################
             f"ExerciseChooser MathTextWidget "
             f"{{ font-size : {self.chooser_math_font_size}pt; }}"
             f"ExerciseChooser TargetLabel "
             f"{{ font-size : {self.chooser_math_font_size}pt; }}"
             f"ExerciseChooser MathObjectWidget "
             f"{{ font-size : {self.chooser_math_font_size}pt; }}"
             # f"MathObjectWidget, TargetLabel "
             # f"{{ font-size : {self.main_font_size}pt; }}"
             
             #######################
             # CentralWidget sizes #
             #######################
             # Context widgets:
             f"ExerciseCentralWidget MathObjectWidget"
             f"{{ font-size : {self.main_font_size}pt; }}"
             # Target:
             f"ExerciseCentralWidget TargetLabel"
             f"{{ font-size : {self.target_font_size}pt; }}"
             # Statements:
             f"ExerciseCentralWidget StatementsTreeWidget"
             f"{{ font-size : {self.statements_font_size}pt; }}"
             # Tooltips:
             f"ExerciseCentralWidget QToolTip"
             f"{{ font-size : {self.tooltips_font_size}pt; }}"
             ####################
             # Calculator sizes #
             ####################
             # Context:
             # f"CalculatorTargets GoalWidget"
             # f"{{ font-size : {self.chooser_math_font_size}pt; }}"
             f"CalculatorTargets MathObjectWidget"
             f"{{ font-size : {self.chooser_math_font_size}pt; }}"
             f"CalculatorTargets TargetLabel"
             f"{{ font-size : {self.chooser_math_font_size}pt; }}"
             f"CalculatorTargets GoalTextWidget"
             f"{{ font-size : {self.chooser_math_font_size}pt; }}"
             f"CalculatorTargets MathTextWidget"
             f"{{ font-size : {self.chooser_math_font_size}pt; }}"
             # Target
             f"CalculatorTarget"
             f"{{ font-size : {self.target_font_size}pt; }}"
             ####################
             # Proof Tree #
             ####################
             f"RawLabelMathObject"
             f"{{ font-size : {cvars.get('display.proof_tree_font_size')}pt; }}"
             )
        return s

    # @property
    # def style_sheet_font(self):
    #     # math_fonts = self.math_fonts_name
    #     # math_widgets = ["MathTextWidget", "MathObjectWidget", "TargetLabel"]
    #     # math_widgets = ", ".join(math_widgets)
    #     s = f"QWidget {{font-family : {self.fonts_name}; }} "
    #             # if self.fonts_name else ""
    #     # if math_fonts:
    #     #     t = (f"QWidget [math_widget='true'] {{font-family : {math_fonts};}}"
    #     #          f"{math_widgets} {{ font-family : {math_fonts}; }}")
    #     #     s += t
    #     return s

    @property
    def style_sheet(self):
        return self.style_sheet_size
        # return self.style_sheet_font + "\n" + self.style_sheet_size

    # def set_general_fonts(self):
    #     """
    #     Set fonts for application menus (and everything which is not maths).
    #     """
    #     if cvars.get('display.use_system_fonts'):
    #         self.fonts_name = self.system_fonts.family()
    #     else:
    #         general_font_file = (cdirs.fonts / self.fonts_file_name).resolve()
    #         # Debug
    #         # general_font_file = "/usr/share/fonts/opentype/malayalam/Chilanka-Regular.otf"
    #         font_id = QFontDatabase.addApplicationFont(str(general_font_file))
    #         if font_id < 0:
    #             log.warning(f"Error loading font {self.fonts_file_name}")
    #         else:
    #             log.info(f"Fonts loaded: {self.fonts_file_name}")
    #             families = QFontDatabase.applicationFontFamilies(font_id)
    #             self.fonts_name = families[0]

    def math_fonts(self, size=None) -> QFont:
        if self.math_fonts_name:
            if size:
                return QFont(self.math_fonts_name, size)
            else:
                return QFont(self.math_fonts_name)

    def set_math_fonts(self):
        """
        Try to load the font corresponding to self.math_fonts_file_name,
        after checking it has not been already loaded. In case of success,
        self.math_fonts_name receive the new fonts name, that can be used for
        styling.
        """

        if self.math_fonts_file_name in self.loaded_fonts_files:
            index = self.loaded_fonts_files.index(self.math_fonts_file_name)
            self.math_fonts_name = self.loaded_fonts_name[index]

        elif not self.math_fonts_file_name or \
                self.math_fonts_file_name.startswith('System fonts'):
            self.math_fonts_name = self.system_fonts.family()

        else:
            file = (cdirs.fonts / self.math_fonts_file_name).resolve()
            font_id = QFontDatabase.addApplicationFont(str(file))
            if font_id < 0:
                log.warning(f"Error loading maths font {str(file)}")
                self.math_fonts_name = self.system_fonts.family()
            else:
                log.info(f"Math fonts loaded: {str(file)}")
                families = QFontDatabase.applicationFontFamilies(font_id)
                self.math_fonts_name = families[0]
                self.loaded_fonts_files.append(self.math_fonts_file_name)
                self.loaded_fonts_name.append(self.math_fonts_name)

    def set_fonts(self):
        """
        Set self.math_fonts_name according to cvars, and set style sheet to
        QApplication.
        """
        if not self.parent:
            log.warning("DeaductionFont: attempt to set fonts with no parent")
            return
        # Get system fonts
        if not DeaductionFonts.system_fonts:
            DeaductionFonts.system_fonts = QApplication.font()
            log.info(f"Système fonts: {DeaductionFonts.system_fonts}")

        # Load and set math fonts
        self.set_math_fonts()

        # Set style sheet
        self.parent.setStyleSheet(self.style_sheet)
        # print("Style sheet:")
        # print(self.style_sheet)

    @staticmethod
    def background_color():
        return cvars.get("display.selection_color", "limegreen")


deaduction_fonts = DeaductionFonts()


