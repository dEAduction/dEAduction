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

# from deaduction.pylib.text import replace_dubious_characters
from deaduction.pylib.math_display.more_display_utils import (cut_spaces,
                                                              text_to_subscript_or_sup
                                                              )


# FIXME: use MathString.map / replace_string
def subscript(s: Union[list, str]) -> (str, bool):
    text, is_subscriptable = text_to_subscript_or_sup(s, format_="utf8",
                                                      sup=False)
    if isinstance(text, list):
        text = "".join(text)
    return text, is_subscriptable


# FIXME: use MathString.map / replace_string
def superscript(s: Union[list, str]) -> (str, bool):
    text, is_subscriptable = text_to_subscript_or_sup(s, format_="utf8",
                                                      sup=True)
    if isinstance(text, list):
        text = "".join(text)
    return text, is_subscriptable


# FIXME: use MathString.map / replace_string
def sub_sup_to_utf8(string: str) -> (str, bool):
    string = string.replace(r'_', r'\sub')
    string = string.replace(r'^', r'\super')

    is_subscriptable = True
    if string.find(r'\sub') != -1:
        before, _, after = string.partition(r'\sub')
        before, is_subscriptable = subscript(after)
        string = before + after
    if string.find(r'\super') != -1:
        before, _, after = string.partition(r'\super')
        after, is_subscriptable = superscript(after)
        string = before + after

    return string, is_subscriptable


def remove_leading_parentheses(math_list: list):
    """Remove leading parentheses. e.g.
    ['parentheses', ...] --> [...]
    ['parentheses', [['parentheses', ...]] --> [...]
    [['parentheses', [['parentheses', ...]]] --> [...]
    but keep parentheses in
    [['parentheses', ...], ... ]
    """
    if (isinstance(math_list, list) and len(math_list) == 1
            and isinstance(math_list[0], list)):
        remove_leading_parentheses(math_list[0])
    elif len(math_list) > 0 and math_list[0] == r'\parentheses':
        math_list.pop(0)
        if len(math_list) == 1:
            remove_leading_parentheses(math_list)


def add_parentheses(math_list: list, depth=1):
    """
    Search for the \\parentheses macro and replace it by a pair of
    parentheses. Remove redundant parentheses, i.e.
    ((...)) or parentheses at depth 0.
    """
    # Remove unnecessary leading parentheses #
    if depth == 0:
        remove_leading_parentheses(math_list)

    for index in range(len(math_list) - 1):
        paren = math_list[index]
        if paren == r'\parentheses':
            if not hasattr(paren, 'replace_string'):
                math_list[index] = math_list.string("(")
            else:
                math_list[index] = paren.replace_string(paren, "(")
            if index == len(math_list)-2 and isinstance(math_list[-1], list):
                remove_leading_parentheses(math_list[-1])

            if not hasattr(paren, 'replace_string'):
                math_list.append(math_list.string(")"))
            else:
                math_list.append(paren.replace_string(paren, ")"))


def recursive_utf8_display(math_list, depth):
    """
    Use the following tags as first child:
    - \sub, \super for subscript/superscript

    Note that math_list itself is formatted; we return the formatted
    math_list just for the leaf case of a string.

    The parameter depth is used to remove leading parentheses.
    """
    if not math_list:
        return ""

    if isinstance(math_list, str):  # Real type = MathString
        new_string, is_subscriptable = sub_sup_to_utf8(math_list)
        # Replace even if not subscriptable ('\sub' --> '_')
        math_list = math_list.replace_string(math_list, new_string)
        return math_list

    prefix = None
    head = math_list[0]
    if head == r'\sub' or head == '_':
        math_list.pop(0)
        prefix = '_'
    elif head == r'\super' or head == '^':
        math_list.pop(0)
        prefix = '^'
    # No color in utf8 :-(
    elif head in (r'\variable', r'\dummy_variable', r'\used_property',
                  r'\text', r'\no_text', r'\marked'):
        math_list.pop(0)

    add_parentheses(math_list, depth)

    # Recursively format children
    idx = 0
    for child in math_list:
        if child:
            formatted_child = recursive_utf8_display(child, depth + 1)
            math_list[idx] = formatted_child
        idx += 1

    # Process sup/sub prefix
    if prefix == '_':
        tentative_string, is_subscriptable = subscript(math_list.to_string())
        if is_subscriptable:
            return tentative_string
        else:
            math_list.insert(0, prefix)
    elif prefix == '^':
        tentative_string, is_subscriptable = superscript(math_list.to_string())
        if is_subscriptable:
            return tentative_string
        else:
            math_list.insert(0, prefix)

    return math_list


def utf8_display(math_list, depth=0):
    """
    Return a utf8 version of the string represented by abstract_string,
    which is a tree of string.
    """

    # if abstract_string is None:
    #     return ""

    recursive_utf8_display(math_list, depth)

    # return math_list


def lean_display(math_list: list):
    """
    Just remove formatters.
    """
    if not math_list:
        return ""

    if not isinstance(math_list, list):
        return math_list



    return math_list


# def lean_display(math_list, depth=0):
#     """
#     Return a Lean version of the string represented by math_list.
#     """
#
#     recursive_utf8_display(math_list, depth)
#
#     # return math_list

