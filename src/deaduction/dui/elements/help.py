"""
########################
# help.py: Help window #
########################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 04 2022 (creation)
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

from PySide2.QtWidgets import QMessageBox
from PySide2.QtCore import Qt

from deaduction.pylib.mathobj import ContextMathObject


class HelpWindow(QMessageBox):
    """
    A class for a window displaying a help msg, with maybe a small set of
    possible user actions.
    """

    def __init__(self, math_object:ContextMathObject, target=False):
        super().__init__()
        if target:
            main_txt, detailed_txt, hint = math_object.help_target_msg()
        else:
            main_txt, detailed_txt, hint = math_object.help_context_msg()

        self.setTextFormat(Qt.RichText)
        self.setText(math_object.math_type.to_display(format_="html"))
        self.setInformativeText(main_txt)
        if detailed_txt:
            self.setDetailedText(detailed_txt)



