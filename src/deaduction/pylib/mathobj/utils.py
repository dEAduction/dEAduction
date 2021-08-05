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

def mark_bound_vars(bound_var_1, bound_var_2):
    """
    Mark two bound variables with a common number, so that we can follow
    them along two quantified expressions and check if these expressions
    are identical
    """
    MathObject.bound_var_number += 1
    bound_var_1.info['bound_var_number'] = MathObject.bound_var_number
    bound_var_2.info['bound_var_number'] = MathObject.bound_var_number


def unmark_bound_vars(bound_var_1, bound_var_2):
    """
    Mark two bound variables with a common number, so that we can follow
    them along two quantified expressions and check tif these expressions
    are identical
    """
    bound_var_1.info.pop('bound_var_number')
    bound_var_2.info.pop('bound_var_number')


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
        log.warning("error in list_string_join: argument should be list or "
                    f"str, not {type(structured_display)}")
        return "**"


def cut_spaces(string: str) -> str:
    """
    Remove unnecessary spaces inside string
    """
    while string.find("  ") != -1:
        string = string.replace("  ", " ")
    return string
