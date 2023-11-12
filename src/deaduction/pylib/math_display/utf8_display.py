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

from deaduction.pylib.math_display.more_display_utils import (cut_spaces,
                                                              text_to_subscript_or_sup,
                                                              first_descendant,
                                                              replace_dubious_characters)


def subscript(s: Union[list, str]) -> str:
    text = text_to_subscript_or_sup(s, format_="utf8", sup=False)
    if isinstance(text, list):
        text = "".join(text)
    return text


def superscript(s: str) -> str:
    text = text_to_subscript_or_sup(s, format_="utf8", sup=True)
    if isinstance(text, list):
        text = "".join(text)
    return text


def sub_sup_to_utf8(string: str) -> str:
    string = string.replace(r'_', r'\sub')
    string = string.replace(r'^', r'\super')
    if string.find(r'\sub') != -1:
        before, _, after = string.partition(r'\sub')
        string = before + subscript(after)
    if string.find(r'\super') != -1:
        before, _, after = string.partition(r'\super')
        string = before + superscript(after)

    return string


# def color_dummy_vars():
#     return (cvars.get('display.color_for_dummy_vars', None)
#             if cvars.get('logic..use_color_for_dummy_vars', True)
#             else None)
#
#
# def color_props():
#     return (cvars.get('display.color_for_applied_properties', None)
#             if cvars.get('logic.use_color_for_applied_properties', True)
#             else None)


def remove_leading_parentheses(l: list):
    """Remove leading parentheses. e.g.
    ['parentheses', ...] --> [...]
    ['parentheses', [['parentheses', ...]] --> [...]
    [['parentheses', [['parentheses', ...]]] --> [...]
    but keep parentheses in
    [['parentheses', ...], ... ]
    """
    if isinstance(l, list) and len(l) == 1 and isinstance(l[0], list):
        remove_leading_parentheses(l[0])
    elif len(l) > 0 and l[0] == r'\parentheses':
        l.pop(0)
        if len(l) == 1:
            remove_leading_parentheses(l)


def add_parentheses(l: list, depth):
    """
    Search for the \\parentheses macro and replace it by a pair of
    parentheses. Remove redundant parentheses, i.e.
    ((...)) or parentheses at depth 0.
    """
    # Remove unnecessary leading parentheses #
    if depth == 0:
        remove_leading_parentheses(l)

    for index in range(len(l) - 1):
        if l[index] == r'\parentheses':
            l[index] = l.formatter("(")
            if index == len(l)-2 and isinstance(l[-1], list):
                remove_leading_parentheses(l[-1])

            l.append(l.formatter(")"))


def recursive_utf8_display(l: list, depth) -> str:
    """
    Use the following tags as first child:
    - \sub, \super for subscript/superscript
    - \dummy_var for dummy vars
    - \applied_property for properties that have already been applied
    """
    if not l:
        return ""

    head = l[0]
    if head == r'\sub' or head == '_':
        return subscript(recursive_utf8_display(l[1:], depth))
    elif head == r'\super' or head == '^':
        return superscript(recursive_utf8_display(l[1:], depth))
    # No color in utf8 :-(
    elif head in (r'\variable', r'\dummy_variable', r'\used_property',
                  r'\text', r'\no_text', r'\marked'):
        return recursive_utf8_display(l[1:], depth)

    else:  # Generic case
        add_parentheses(l, depth)
        strings = [utf8_display(child, depth+1) for child in l]
        return ''.join(strings)


def utf8_display(abstract_string: Union[str, list], depth=0):
    """
    Return a utf8 version of the string represented by abstract_string,
    which is a tree of string.
    """
    if abstract_string is None:
        return ""

    if isinstance(abstract_string, list):
        string = recursive_utf8_display(abstract_string, depth)
    else:
        string = sub_sup_to_utf8(abstract_string)

    if isinstance(string, list):  # debug
        print(f"Variable string {string} should be a string, not a list!")
    return replace_dubious_characters(cut_spaces(string))


def recursive_lean_display(l: list, depth) -> str:
    """
    """
    if not l:
        return ""

    head = l[0]
    if head == r'\sub' or head == '_':
        return subscript(recursive_lean_display(l[1:], depth))
    elif head == r'\super' or head == '^':
        return superscript(recursive_lean_display(l[1:], depth))
    elif head in (r'\variable', r'\dummy_variable', r'\used_property',
                  r'\text', r'\no_text', r'\marked'):
        return recursive_lean_display(l[1:], depth)

    else:  # Generic case
        add_parentheses(l, depth=depth)
        strings = [lean_display(child, depth+1) for child in l]
        return ''.join(strings)


def lean_display(abstract_string: Union[str, list], depth=0):
    """
    Return a Lean version of the string represented by abstract_string,
    which is a tree of string.
    """
    if isinstance(abstract_string, list):
        string = recursive_lean_display(abstract_string, depth)
    else:  # FIXME
        # string = sub_sup_to_utf8(abstract_string)
        string = abstract_string
    if isinstance(string, list):  # debug
        print(f"Variable string {string} should be a string, not a list!")
    return cut_spaces(string)

