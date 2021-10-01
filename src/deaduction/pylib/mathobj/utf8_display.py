"""
utf8_display.py : compute a displayble utf8 string for MthObjects 

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 09 2021 (creation)
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

import deaduction.pylib.config.vars as cvars

from deaduction.pylib.mathobj.utils import (cut_spaces,
                                            text_to_subscript_or_sup,
                                            first_descendant)


def subscript(s: str):
    return text_to_subscript_or_sup(s, format_="utf8", sup=False)


def superscript(s: str):
    return text_to_subscript_or_sup(s, format_="utf8", sup=True)


def sub_sup_to_utf8(string: str) -> str:
    string = string.replace('_', r'\sub')
    string = string.replace('^', r'\super')
    if string.find(r'\sub') != -1:
        before, _, after = string.partition(r'\sub')
        string = before + subscript(after)
    if string.find(r'\super') != -1:
        before, _, after = string.partition(r'\super')
        string = before + superscript(after)

    return string


def color_dummy_vars():
    return (cvars.get('display.color_for_dummy_vars', None)
            if cvars.get('logic..use_color_for_dummy_vars', True)
            else None)


def color_props():
    return (cvars.get('display.color_for_applied_properties', None)
            if cvars.get('logic.use_color_for_applied_properties', True)
            else None)


def recursive_utf8_display(l: list):
    """
    Use the following tags as first child:
    - \sub, \super for subscript/superscript
    - \dummy_var for dummy vars
    - \applied_property for properties that have already been applied
    """
    head = l[0]
    if head == r'\sub' or head == '_':
        return subscript(recursive_utf8_display(l[1:]))
    elif head == r'\super' or head == '^':
        return superscript(recursive_utf8_display(l[1:]))
    elif head == r'\dummy_var':  # No color in utf8 :-(
        return recursive_utf8_display(l[1:])
    elif head == r'\applied_property':  # No color in utf8 :-(
        return recursive_utf8_display(l[1:])
    elif head == r'\parentheses':
        # Avoid redundant parentheses:
        if len(l) > 1 and first_descendant(l[1]) == r'\parentheses':
            return recursive_utf8_display(l[1:])
        else:
            return "(" + recursive_utf8_display(l[1:]) + ")"

    else:  # Generic case
        strings = [utf8_display(child) for child in l]
        return ''.join(strings)


def utf8_display(abstract_string: Union[str, list]):
    """
    Return a html version of the string represented by string, which is a
    tree of string.
    """
    if isinstance(abstract_string, list):
        string = recursive_utf8_display(abstract_string)
    else:
        string = sub_sup_to_utf8(abstract_string)

    return cut_spaces(string)


