"""
#########################################################
# display_math: methods to display mathematical objects #
#########################################################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 06 2020 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

    This file is part of dEAduction.

    dEAduction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    dEAduction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""


import logging
from typing import Union

from deaduction.pylib.math_display import MathDisplay

log = logging.getLogger(__name__)
global _


def shorten(string: str) -> str:
    """
    Try to shorten string for concise display: e.g.
    "an element of " -> "element of "
    "is injective" -> injective.
    Note that this is called after translation.
    """
    # FIXME: to be adapted according to languages
    to_be_shortened = {_("a function"): _("function"),
                       _("an element"): _("element"),
                       _("a subset"): _("subset"),
                       _('a proposition'): _("proposition"),
                       _("a family"): _("family")
                       }
    to_be_suppressed = (r'\text_is', " ")
    to_be_replaced = {r'\text_is_not': " " + _("not") + " "}

    striped_string = string.strip()
    for phrase in to_be_shortened:
        if striped_string.startswith(phrase):
            shortened_phrase = to_be_shortened[phrase]
            # words = phrase.split(" ")
            # prefix = words[0]
            # # Just replace first occurrence:
            # string = string.replace(prefix+" ", "", 1)
            string = string.replace(phrase, shortened_phrase)
    for word in to_be_suppressed:
        if striped_string == word:
            string = " "

    for word in to_be_replaced:
        if striped_string == word:
            string = string.replace(word, to_be_replaced[word], 1)

    return string


def latex_to_text_func(string: str) -> (str, bool):
    """
    Translate latex into text. We import the latex_to_text dic here so that
    the selected language is applied even if it has changed since the launch
    of deaduction.
    """
    # from .display_data import latex_to_text  # FIXME: done in settings
    # for macro in latex_to_text:
    #     if macro in string:
    #         text_string = string.replace(macro, latex_to_text[macro])
    #         return text_string, True
    striped_string = string.strip()  # Remove spaces
    if striped_string in MathDisplay.latex_to_text:
        text_stripped = MathDisplay.latex_to_text[striped_string]
        text_string = string.replace(striped_string, text_stripped)
        return text_string, True
    return string, False


def shallow_latex_to_text(math_list: Union[list, str], text_depth=0) \
        -> Union[list, str]:
    """
    Try to change symbols for text in a tree representing some MathObject,
    but only until depth given by text_depth. The deepest branches are left
    untouched (so they still contain latex macro that are NOT suitable to
    display without either latex compilation or conversion to utf8).
    """

    # TODO: move this as methods of MathString and MathList

    if not math_list:
        return math_list

    if isinstance(math_list, list):
        # Stop conversion to text in some cases
        if math_list[0] == r'\no_text':
            text_depth = 0
            math_list.pop(0)
        # Recursion
        # abstract_string = [shallow_latex_to_text(item, text_depth-1) for
        #                    item in abstract_string]
        idx = 0
        for item in math_list:
            new_string = shallow_latex_to_text(item, text_depth - 1)
            # FIXME: class method
            math_list.replace_string(idx, new_string)
            # abstract_string[idx] = shallow_latex_to_text(item, text_depth-1)
            idx += 1

        # log.debug(f"    --> Shallow_to_text: {string}")
        return math_list

    elif isinstance(math_list, str):
        if text_depth > 0:  # Try to convert to text
            new_string, success = latex_to_text_func(math_list)
            if success:  # Add a tag to indicate this is text (not math).
                new_math_str = math_list.replace_string(math_list,
                                                        new_string)
                formatter = math_list.formatter(r'\text')
                string = [formatter, new_math_str]
        else:  # Try to shorten
            new_string = shorten(math_list)
            if new_string != math_list:
                new_string = math_list.replace_string(math_list,
                                                      new_string)

        return new_string



