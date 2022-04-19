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
from .utf8_display import utf8_display
from .html_display import html_display
from deaduction.pylib.math_display import latex_to_utf8, latex_to_lean


def abstract_string_to_string(abstract_string: Union[list, str], format_,
                              use_color=True) \
        -> str:
    """
    Turn an abstract string into a string in various formats.
    """
    display = ""
    if format_ == 'lean':
        abstract_string = latex_to_lean(abstract_string)
    # Replace latex macro by utf8:
    if format_ in ('lean', 'utf8', 'html'):
        abstract_string = latex_to_utf8(abstract_string)
    else:
        raise ValueError("Wrong format_ type, must be one of 'lean', 'utf8', "
                         "'html'")
    # Concatenate and format:
    if format_ == 'html':
        display = html_display(abstract_string, use_color=use_color)
    elif format_ == 'utf8':
        display = utf8_display(abstract_string)
    elif format_ == 'lean':  # FIXME: should be adapted to Lean
        display = utf8_display(abstract_string)

    return display
