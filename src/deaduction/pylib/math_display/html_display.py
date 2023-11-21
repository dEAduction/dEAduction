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

# import deaduction.pylib.config.vars as cvars
#
# from deaduction.pylib.math_display.more_display_utils import (cut_spaces,
#                                                               replace_dubious_characters)
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
    # html_pre = f"<font id='color'>"
    # html_post = '</font>'
    return html_pre + s + html_post


def variable_style(s) -> str:
    # FIXME: not used
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
        before, _, after = string.partition(r'\sub')
        string = before + subscript(after)
    if string.find(r'\super') != -1:
        before, _, after = string.partition(r'\super')
        string = before + superscript(after)

    return string


# def color_dummy_variables():
#     return (cvars.get('display.color_for_dummy_variables', None)
#             if cvars.get('logic.use_color_for_dummy_variables', True)
#             else None)
#
#
# def color_variables():
#     return (cvars.get('display.color_for_variables', None)
#             if cvars.get('logic.use_color_for_variables', True)
#             else None)
#
#
# def color_props():
#     return (cvars.get('display.color_for_applied_properties', None)
#             if cvars.get('logic.use_color_for_applied_properties', True)
#             else None)
#

# def font_wrapper(s: str, bf=True):
#     if not bf:
#         return s
#     else:
#         html_pre = "<b>"
#         html_post = "</b>"
#         return html_pre + s + html_post


def html_class_wrapper(s: str, class_name: str):
    html_pre = f"<font class='{class_name}'>"
    html_post = '</font>'
    return html_pre + s + html_post


# def html_style_classes(color=True):
#     if color:
#         style = "<style>" \
#                 f".variable  {{ color: {color_variables()} }}" \
#                 f".dummy_variable  {{ color: {color_dummy_variables()} }}" \
#                 f".used_prop  {{ color: {color_props()} }}" \
#                 "</style>"
#     else:
#         style = ""
#     return style


style_wrapper_dic = {r'\bf': ('<b>', '</b>'),
                     r'\sub': ('<sub>', '</sub>'),
                     '_': ('<sub>', '</sub>'),
                     r'\super': ('<sup>', '</sup>'),
                     '^': ('<sup>', '</sup>'),
                     r'\class': ("<font class='{}'>", '</font>'),
                     r'\variable': ("<font class='variable'>", '</font>'),
                     r'\math': ("<font class='math'>", '</font>'),
                     r'\dummy_variable': ("<font class='dummy_variable'>",
                                          '</font>'),
                     r'\used_property': ("<font class='used_prop'>", '</font>'),
                     # r'\color': ("<font style='color:{};'>", '</font>')
                     r'\marked': ("<font class='highlight'>", '</font>'),
                     r'\text': ("<font class='text'>", '</font>')
}


def pre_post_wrapper(math_list: list, formatter=None):
    """
    Wrap the list l with pre and post (if provided), or adapted pre and post
    (if style is one of the pre-defined styles).
    """

    pre, post = None, None

    if not formatter:
        formatter = math_list[0]
    if not isinstance(formatter, str):
        return None, None
    pre_post = style_wrapper_dic.get(formatter)
    if pre_post:
        pre, post = pre_post
    # if parameter:
    #     pre = pre.format(parameter)

    if pre:
        pre = math_list.formatter(pre)
    if post:
        post = math_list.formatter(post)
    return pre, post


def wrap(math_list, formatter=None, pre=None, post=None):
    if not (pre or post):
        pre, post = pre_post_wrapper(math_list, formatter)
    if pre:
        math_list.insert(0, pre)
    if post:
        math_list.append(post)


def html_display_single_string(string: str) -> str:
    # Do this BEFORE formatting:
    string = string.map(reserve_special_char)
    # Formatting subscript/superscript:
    string = string.map(sub_sup_to_html)
    return string


# def recursive_html_display(l: Union[list, str], depth, use_color=True,
#                            no_text=False) -> []:
#     """
#     Use the following tags as first child:
#     - \\sub, \\super for subscript/superscript
#     - \\dummy_variable for dummy vars
#     - \\applied_property for properties that have already been applied
#
#     :param l: abstract_string, i.e. a tree of strings
#     :param depth: depth in the abstract_string tree
#     :param use_color: if True, allow the use of color. This parameter is set to
#                       False when the whole text should be grey.
#     :param no_text: if True, only math fonts are used.
#     """
#     if isinstance(l, str):
#         return html_display_single_string(l)
#
#     assert isinstance(l, list)
#     head = l[0]
#     if head == r'\sub' or head == '_':
#         return subscript(recursive_html_display(l[1:], depth,
#                                                 use_color, no_text))
#     elif head == r'\super' or head == '^':
#         return superscript(recursive_html_display(l[1:], depth,
#                                                   use_color, no_text))
#     elif head == r'\text':
#         raw_string = recursive_html_display(l[1:], depth,
#                                             use_color, no_text)
#         return (raw_string if no_text
#                 else html_class_wrapper(raw_string, class_name='text'))
#     elif head == r'\variable':
#         raw_string = recursive_html_display(l[1:], depth, use_color, no_text)
#         formatted_string = variable_style(raw_string)
#         if use_color:
#             return html_class_wrapper(formatted_string, class_name="variable")
#         else:
#             return formatted_string
#     elif head == r'\dummy_variable':
#         raw_string = recursive_html_display(l[1:], depth, use_color, no_text)
#         formatted_string = variable_style(raw_string)
#         if use_color:
#             return html_class_wrapper(formatted_string,
#                                       class_name="dummy_variable")
#         else:
#             return formatted_string
#     elif head == r'\used_property':
#         if use_color:
#             # Use color and forbid other colors in the text
#             return html_class_wrapper(recursive_html_display(l[1:], depth,
#                                       use_color=False, no_text=no_text),
#                                       class_name="used_prop")
#         else:
#             return recursive_html_display(l[1:], depth, use_color, no_text)
#     elif head == r'\marked':
#         return html_class_wrapper(recursive_html_display(l[1:], depth,
#                                                          use_color=use_color,
#                                                          no_text=no_text),
#                                   class_name="highlight")
#
#     else:
#         # handle "\parentheses":
#         add_parentheses(l, depth)
#
#         # log.debug(f"Children to html: {l}")
#         strings = [recursive_html_display(child, depth+1, use_color, no_text)
#                    for child in l]
#         string = ''.join(strings)
#
#         # return html_class_wrapper(string, class_name='text')
#         return string
#         # return strings


def new_recursive_html_display(math_list: Union[list, str], depth,
                               use_color=True,
                               no_text=False) -> []:
    """
    Use the following tags as first child:
    - \\sub, \\super for subscript/superscript
    - \\dummy_variable for dummy vars
    - \\applied_property for properties that have already been applied

    :param math_list: a tree of strings, of type MathList
    :param depth: depth in the abstract_string tree
    :param use_color: if True, allow the use of color. This parameter is set to
                      False when the whole text should be grey.
    :param no_text: if True, only math fonts are used.
    """

    if math_list is None:
        return []

    if isinstance(math_list, str):
        return html_display_single_string(math_list)

    assert isinstance(math_list, list)

    # Check options
    if no_text and math_list[0] == r'\text':
        math_list.pop(0)
    if (not use_color) and math_list[0] in (r'\variable', r'\dummy_variable',
                                            r'\used_prop'):
        math_list.pop(0)

    # Main formatter. Pre and post will be added AFTER recursive formatting
    pre, post = pre_post_wrapper(math_list)
    if pre:  # First item was used to get wrapper
        math_list.pop(0)

    # Handle "\parentheses":
    add_parentheses(math_list, depth)

    # Format children
    idx = 0
    for child in math_list:
        formatted_child = new_recursive_html_display(child, depth+1, use_color,
                                                     no_text)
        math_list[idx] = formatted_child
        idx += 1

    # Add pre and post if pertinent
    if pre or post:
        wrap(math_list, pre=pre, post=post)

    return math_list


def html_display(math_list: Union[str, list], depth=0,
                 use_color=True,
                 bf=False,
                 no_text=False) -> str:
    """
    Return a html version of the string represented by abstract_string,
    which is a tree of string.
    """

    # TODO: take tex_depth into account
    new_recursive_html_display(math_list, depth, use_color=use_color,
                               no_text=no_text)

    # Boldface?
    if bf:
        wrap(math_list, formatter='\bf')

    # Math class
    wrap(math_list, formatter='\math')

    # General hygiene
    math_list.check_completeness()
    math_list.post_format()




