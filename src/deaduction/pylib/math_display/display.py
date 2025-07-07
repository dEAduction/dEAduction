"""
# display.py : turn abstract_string into string of various format #

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 12 2021 (creation)
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
from typing import Union
from .utf8_display import (utf8_display, lean_display, remove_formaters,
                           latex_process, latex_display)

from .html_display import html_display
from deaduction.pylib.math_display import MathDisplay

# latex_to_utf8 = MathDisplay.latex_to_utf8
# latex_to_lean = MathDisplay.latex_to_lean


# def format_math_list(math_list: Union[list, str], format_,
#                               use_color=True,
#                               bf=False,
#                               no_text=False) -> str:
#     """
#     Adapt the abstract_string in various format.
#     """
#     display = ""
#
#     # (1) Replace latex macro by utf8/lean versions
#     if format_ == 'lean':  # FIXME:
#         # math_list = MathDisplay.latex_to_lean(math_list)
#         math_list.recursive_map(MathDisplay.latex_to_lean)
#
#     if format_ in ('lean', 'utf8', 'html'):  # Replace latex macro by utf8:
#         # abstract_string = MathDisplay.latex_to_utf8(abstract_string)
#         math_list.recursive_map(MathDisplay.latex_to_utf8)
#     else:
#         raise ValueError("Wrong format_ type, must be one of 'lean', 'utf8', "
#                          "'html'")
#     # (2) Format
#     if format_ == 'html':
#         html_display(math_list, use_color=use_color, bf=bf, no_text=no_text)
#         display = math_list.to_string()  # TODO: move outside func
#
#     elif format_ == 'utf8':  # FIXME:
#         display = utf8_display(math_list)
#     elif format_ == 'lean':  # FIXME:
#         display = lean_display(math_list)
#
#     # Put here general hygiene, and remove to_string
#
#     return display
