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

from deaduction.pylib.math_display.utils import (cut_spaces,
                                                 text_to_subscript_or_sup,
                                                 first_descendant)


def subscript(s: str) -> str:
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
    string = string.replace('_', r'\sub')
    string = string.replace('^', r'\super')
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


def add_parentheses(l: list, depth):
    """
    Search for the \\parentheses macro and replace it by a pair of
    parentheses. Remove redundant parentheses, i.e.
    ((...)) or parentheses at depth 0.
    """
    # Remove first parentheses at any depth if depth=0
    if depth == 0:
        # Find first leaf of the tree
        last_node = l
        first_leaf = last_node[0]
        while isinstance(first_leaf, list):
            last_node = first_leaf
            first_leaf = last_node[0]
        if first_leaf == r'\parentheses':
            last_node.pop(0)
    
    for index in range(len(l) - 1):
        child = l[index]
        if child == r'\parentheses':
            next_child = l[index + 1]
            if (first_descendant(next_child) == r'\parentheses' or
                    (index == 0 and depth == 0)):
                # Remove redundant parentheses
                l[index] = ""
            else:
                l[index] = "("
                l.append(")")


def recursive_utf8_display(l: list, depth) -> str:
    """
    Use the following tags as first child:
    - \sub, \super for subscript/superscript
    - \dummy_var for dummy vars
    - \applied_property for properties that have already been applied
    """
    head = l[0]
    if head == r'\sub' or head == '_':
        return subscript(recursive_utf8_display(l[1:], depth))
    elif head == r'\super' or head == '^':
        return superscript(recursive_utf8_display(l[1:], depth))
    elif head == r'\dummy_var':  # No color in utf8 :-(
        return recursive_utf8_display(l[1:], depth)
    elif head == r'\applied_property':  # No color in utf8 :-(
        return recursive_utf8_display(l[1:], depth)
    # elif head == r'\parentheses':
    #     # Avoid redundant parentheses:
    #     if len(l) > 1 and first_descendant(l[1]) == r'\parentheses':
    #         return recursive_utf8_display(l[1:], depth)
    #     else:
    #         return "(" + recursive_utf8_display(l[1:], depth) + ")"

    else:  # Generic case
        add_parentheses(l, depth)
        strings = [utf8_display(child, depth+1) for child in l]
        return ''.join(strings)


def utf8_display(abstract_string: Union[str, list], depth=0):
    """
    Return a html version of the string represented by string, which is a
    tree of string.
    """
    if isinstance(abstract_string, list):
        string = recursive_utf8_display(abstract_string, depth)
    else:
        string = sub_sup_to_utf8(abstract_string)

    if isinstance(string, list):  # debug
        print(f"Variable string {string} should be a string, not a list!")
    return cut_spaces(string)


