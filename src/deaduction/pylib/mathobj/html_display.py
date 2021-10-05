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

from deaduction.pylib.mathobj.utils import cut_spaces, first_descendant
from deaduction.pylib.mathobj.utf8_display import add_parentheses

log = logging.getLogger(__name__)

utf8_to_html_dic = {
    "<": "&lt",
    ">": "&gt",
    "'": "&apos",
    # "&": "&amp",
    # '"': "&quot"
}


def reserve_special_char(s: str) -> str:
    stripped_s = s.strip()
    if stripped_s == "<":
        s.replace("<", "&lt")
    elif stripped_s == ">":
        s.replace(">", "&gt")
    s.replace("'", "&apos")
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


def color_dummy_vars():
    return (cvars.get('display.color_for_dummy_vars', None)
            if cvars.get('logic..use_color_for_dummy_vars', True)
            else None)


def color_props():
    return (cvars.get('display.color_for_applied_properties', None)
            if cvars.get('logic.use_color_for_applied_properties', True)
            else None)


def recursive_html_display(l: list, depth) -> str:
    """
    Use the following tags as first child:
    - \\sub, \\super for subscript/superscript
    - \\dummy_var for dummy vars
    - \\applied_property for properties that have already been applied
    """
    head = l[0]
    if head == r'\sub' or head == '_':
        return subscript(recursive_html_display(l[1:], depth))
    elif head == r'\super' or head == '^':
        return superscript(recursive_html_display(l[1:], depth))
    elif head == r'\dummy_var':
        color = color_dummy_vars()
        if color:
            return html_color(recursive_html_display(l[1:], depth), color)
        else:
            return recursive_html_display(l[1:], depth)
    elif head == r'\applied_property':
        color = color_props()
        if color:
            return html_color(recursive_html_display(l[1:], depth), color)
        else:
            return recursive_html_display(l[1:], depth)

    else:
        # handle "\parentheses":
        add_parentheses(l, depth)

        log.debug(f"Children to html: {l}")
        strings = [html_display(child, depth+1) for child in l]
        return ''.join(strings)


def html_display(abstract_string: Union[str, list], depth=0) -> str:
    """
    Return a html version of the string represented by string, which is a
    tree of string.
    """
    # FIXME: take tex_depth into account
    if isinstance(abstract_string, list):
        string = recursive_html_display(abstract_string, depth)
    else:
        # Do this BEFORE formatting:
        abstract_string = reserve_special_char(abstract_string)
        # Formatting subscript/superscript:
        string = sub_sup_to_html(abstract_string)

    return cut_spaces(string)


