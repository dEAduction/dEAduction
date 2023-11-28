"""
# high_level_request.py : <#ShortDescription> #
    
    <#optionalLongDescription>

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 08 2021 (creation)
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

from typing import Optional

import deaduction.pylib.config.vars as cvars


def cut_spaces(string: str) -> Optional[str]:
    """
    Remove unnecessary spaces inside string.
    """

    new_string = string
    while new_string.find("  ") != -1:
        new_string = new_string.replace("  ", " ")
    new_string = new_string.replace("( ", "(")
    new_string = new_string.replace(" )", ")")

    if new_string != string:
        return new_string


def cut_successive_spaces(string1, string2: str) -> Optional[str]:
    """
    Remove unnecessary spaces between sucessive strings.
    """

    if not (string1 and string2):
        return

    # if string1[-1] in (' ', '(', ')'):
    if string1[-1] in (' ', '('):
        if string2[0] == ' ':
            return string2[:-1]


def text_to_subscript_or_sup(structured_string,
                             format_="latex",
                             sup=False
                             ):
    """
    Convert structured_string to subscript of superscript

    :param structured_string:   list
    :param format_:             "latex" or "utf8" or "lean"
    :param sup:                 True if superscript, else subscript
    :return:                    list, converted structured string
    """
    # log.debug(f"converting into sub/superscript {structured_string}")
    if format_ == 'latex':
        if sup:
            structured_string.insert(0, r'^{')
            structured_string.append(r'}')
            # return [r'^{', structured_string, r'}']
            return structured_string
        else:
            structured_string.insert(0, r'_{')
            structured_string.append(r'}')
            # return [r'_{', structured_string, r'}']
            return structured_string
    else:
        sub_or_sup, is_subscriptable = recursive_subscript(structured_string,
                                                           sup)
        if not is_subscriptable:
            if sup:
                sub_or_sup = ['^', structured_string]
            else:
                sub_or_sup = ['_', structured_string]
            # [sub] necessary in case sub is an (unstructured) string
        # log.debug(f"--> {sub_or_sup}")
        return sub_or_sup, is_subscriptable


SOURCE = {'sub': " 0123456789" + "aeioruv",
          'sup': " -1"}
TARGET = {'sub': " ₀₁₂₃₄₅₆₇₈₉" + "ₐₑᵢₒᵣᵤᵥ",
          'sup': " ⁻¹"}


def recursive_subscript(structured_string, sup):
    """
    Recursive version, for strings to be displayed use global_subscript instead
    This is not for latex format.

    :param structured_string:   list of structured string
    :param sup:                 bool
    :return: the structured string in a subscript version if available,
                or the structured string unchanged if not,
                and a boolean is_subscriptable
    """
    is_subscriptable = True
    if isinstance(structured_string, list):
        sub_list = []
        for item in structured_string:
            sub, still_is_sub = recursive_subscript(item, sup)
            if not still_is_sub:  # Not subscriptable
                return structured_string, False
            else:
                sub_list.append(sub)
        return sub_list, True

    # From now on structured_string is assumed to be a string
    style = 'sup' if sup else 'sub'
    for letter in structured_string:
        if letter not in SOURCE[style]:
            is_subscriptable = False
    if is_subscriptable:
        subscript_string = ""
        for letter in structured_string:
            pos = SOURCE[style].index(letter)
            subscript_string += TARGET[style][pos]
    else:
        subscript_string = structured_string
    return subscript_string, is_subscriptable


def first_descendant(l):
    if isinstance(l, list):
        return first_descendant(l[0])
    else:
        return l


