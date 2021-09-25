"""
# html_display.py : <#ShortDescription> #
    
    <#optionalLongDescription>

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


def cut_spaces(string: str) -> str:
    """
    Remove unnecessary spaces inside string
    """
    while string.find("  ") != -1:
        string = string.replace("  ", " ")
    return string


def html_subscript(s: str):
    html_pre = '<sub>'
    html_post = '</sub>'
    return html_pre + s + html_post


def html_superscript(s: str):
    html_pre = '<sup>'
    html_post = '</sup>'
    return html_pre + s + html_post


def html_color(s: str, color: str):
    html_pre = f"<div style='color:{color};'>"
    html_post = '</div>'
    return html_pre + s + html_post


def color_dummy_vars():
    return (cvars.get('color_for_dummy_vars', None)
            if cvars.get('use_color_for_dummy_vars', True)
            else None)


def color_props():
    return (cvars.get('color_for_applied_properties', None)
            if cvars.get('use_color_for_applied_properties', True)
            else None)


def recursive_html_display(l: list, text_depth=0):
    """
    Use the following tags as first child:
    - @sub, @sup for subscript/superscript
    - @dummy_var for dummy vars
    - @applied_property for properties that have already been applied
    """
    head = l[0]
    if head == '@sub':
        return html_subscript(recursive_html_display(l[1:]))
    elif head == '@sup':
        return html_superscript(recursive_html_display(l[1:]))
    elif head == '@dummy_var':
        color = color_dummy_vars()
        if color:
            return html_color(recursive_html_display(l[1:]), color)
        else:
            return recursive_html_display(l[1:])
    elif head == '@applied_property':
        color = color_props()
        if color:
            return html_color(recursive_html_display(l[1:]), color)
        else:
            return recursive_html_display(l[1:])
    else:  # Generic case
        strings = [html_display(child) for child in l]
        return ''.join(strings)


def html_display(string: Union[str, list], text_depth=0):
    """
    Return a html version of the string represented by string, which is a
    tree of string.
    """
    # FIXME: take tex_depth into account
    if isinstance(string, list):
        string = recursive_html_display(string, text_depth)

    return cut_spaces(string)


