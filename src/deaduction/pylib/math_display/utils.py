"""
# utils.py : <#ShortDescription> #
    
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

# def mark_bound_vars(bound_var_1, bound_var_2):
#     """
#     Mark two bound variables with a common number, so that we can follow
#     them along two quantified expressions and check if these expressions
#     are identical
#     """
#     MathObject.bound_var_number += 1
#     bound_var_1.info['bound_var_number'] = MathObject.bound_var_number
#     bound_var_2.info['bound_var_number'] = MathObject.bound_var_number
#
#
# def unmark_bound_vars(bound_var_1, bound_var_2):
#     """
#     Mark two bound variables with a common number, so that we can follow
#     them along two quantified expressions and check tif these expressions
#     are identical
#     """
#     bound_var_1.info.pop('bound_var_number')
#     bound_var_2.info.pop('bound_var_number')

import deaduction.pylib.config.vars as cvars


def structured_display_to_string(structured_display) -> str:
    """
    Turn a (structured) latex or utf-8 display into a latex string.

    :param structured_display:  type is recursively defined as str or list of
                                structured_display
    """
    if isinstance(structured_display, str):
        return structured_display
    elif isinstance(structured_display, list):
        string = ""
        for lr in structured_display:
            lr = structured_display_to_string(lr)
            string += lr
        return cut_spaces(string)
    else:
        print("error in list_string_join: argument should be list or "
                    f"str, not {type(structured_display)}")
        return "**"


def cut_spaces(string: str) -> str:
    """
    Remove unnecessary spaces inside string
    """
    while string.find("  ") != -1:
        string = string.replace("  ", " ")
    string = string.replace("( ", "(")
    string = string.replace(" )", ")")
    return string


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
            return [r'^{', structured_string, r'}']
        else:
            return [r'_{', structured_string, r'}']
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
        return sub_or_sup


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


def replace_dubious_characters(s: str) -> str:
    dubious_characters = "ℕ, ℤ, ℚ, ℝ, 𝒫, ↦"
    replacement_characters: str = cvars.get("display.dubious_characters")
    if replacement_characters == dubious_characters:
        return s
    else:
        character_translation_dic = {}
        default_list = dubious_characters.split(', ')
        new_list = replacement_characters.split(',')
        if len(default_list) != len(new_list):
            return s

        for default, new in zip(default_list, new_list):
            character_translation_dic[default] = new.strip()

        new_string = ""
        for char in s:
            new_char = (character_translation_dic[char]
                        if char in character_translation_dic
                        else char)
            new_string += new_char
        return new_string
