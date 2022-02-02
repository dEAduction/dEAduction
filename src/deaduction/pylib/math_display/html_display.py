"""
html_display.py : compute a displayable html string for a MathObject

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
import logging

import deaduction.pylib.config.vars as cvars

from deaduction.pylib.math_display.utils import (cut_spaces,
                                                 replace_dubious_characters)
from deaduction.pylib.math_display.utf8_display import add_parentheses

log = logging.getLogger(__name__)

utf8_to_html_dic = {
    "<": "&lt;",
    ">": "&gt;",
    "'": "&apos;",
    # "&": "&amp;",
    # '"': "&quot;"
}


def reserve_special_char(s: str) -> str:
    stripped_s = s.strip()
    if stripped_s == "<":
        s = s.replace("<", "&lt;")
    elif stripped_s == ">":
        s = s.replace(">", "&gt;")
    s = s.replace("'", "&apos;")
    return s


def subscript(s: str) -> str:
    html_pre = '<sub>'
    html_post = '</sub>'
    return html_pre + s + html_post


def superscript(s: str) -> str:
    html_pre = '<sup>'
    html_post = '</sup>'
    return html_pre + s + html_post


def html_color(s: str, color: str) -> str:
    # html_pre = f"<div style='color:{color};'>"
    # html_post = '</div>'
    html_pre = f"<font style='color:{color};'>"
    html_post = '</font>'
    return html_pre + s + html_post


def variable_style(s) -> str:
    italic = False
    html_pre = ""
    html_post = ""
    if italic:
        html_pre = '<i> '
        html_post = ' </i>'
    return html_pre + s + html_post


def sub_sup_to_html(string: str) -> str:
    string = string.replace('_', r'\sub')
    string = string.replace('^', r'\super')
    if string.find(r'\sub') != -1:
        before, _, after  = string.partition(r'\sub')
        string = before + subscript(after)
    if string.find(r'\super') != -1:
        before, _, after  = string.partition(r'\super')
        string = before + superscript(after)

    return string


def color_dummy_variables():
    return (cvars.get('display.color_for_dummy_variables', None)
            if cvars.get('logic.use_color_for_dummy_variables', True)
            else None)


def color_variables():
    return (cvars.get('display.color_for_variables', None)
            if cvars.get('logic.use_color_for_variables', True)
            else None)


def color_props():
    return (cvars.get('display.color_for_applied_properties', None)
            if cvars.get('logic.use_color_for_applied_properties', True)
            else None)


def recursive_html_display(l: Union[list, str], depth, use_color=True) -> str:
    """
    Use the following tags as first child:
    - \\sub, \\super for subscript/superscript
    - \\dummy_variable for dummy vars
    - \\applied_property for properties that have already been applied

    :param l: abstract_string, i.e. a tree of strings
    :param depth: depth in the abstract_string tree
    :param use_color: if True, allow the use of color. This parameter is set to
                      False when the whole text should be grey.
    """
    if isinstance(l, str):
        return html_display_single_string(l)

    assert isinstance(l, list)
    head = l[0]
    if head == r'\sub' or head == r'_':
        return subscript(recursive_html_display(l[1:], depth, use_color))
    elif head == r'\super' or head == r'^':
        return superscript(recursive_html_display(l[1:], depth, use_color))
    elif head == r'\variable':
        color = color_variables()
        raw_string = recursive_html_display(l[1:], depth, use_color)
        formatted_string = variable_style(raw_string)
        if color and use_color:
            return html_color(formatted_string, color)
        else:
            return formatted_string
    elif head == r'\dummy_variable':
        color = color_dummy_variables()
        raw_string = recursive_html_display(l[1:], depth, use_color)
        formatted_string = variable_style(raw_string)
        if color and use_color:
            return html_color(formatted_string, color)
        else:
            return formatted_string
    elif head == r'\used_property':
        color = color_props()
        if color and use_color:
            # Use color and forbid other colors in the text
            return html_color(recursive_html_display(l[1:], depth,
                                                     use_color=False),
                              color)
        else:
            return recursive_html_display(l[1:], depth, use_color)

    else:
        # handle "\parentheses":
        add_parentheses(l, depth)

        # log.debug(f"Children to html: {l}")
        strings = [recursive_html_display(child, depth+1, use_color)
                   for child in l]
        return ''.join(strings)


def html_display_single_string(string: str) -> str:
    # Do this BEFORE formatting:
    string = reserve_special_char(string)
    # Formatting subscript/superscript:
    string = sub_sup_to_html(string)
    return string


def html_display(abstract_string: Union[str, list], depth=0) -> str:
    """
    Return a html version of the string represented by abstract_string,
    which is a tree of string.
    """
    # FIXME: take tex_depth into account
    # if isinstance(abstract_string, list):
    string = recursive_html_display(abstract_string, depth)
    # else:
    #     # Do this BEFORE formatting:
    #     abstract_string = reserve_special_char(abstract_string)
    #     # Formatting subscript/superscript:
    #     string = sub_sup_to_html(abstract_string)
    assert isinstance(string, str)
    string = cut_spaces(string)
    string = replace_dubious_characters(string)
    return string


