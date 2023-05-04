"""
##########################################################
# high_level_request.py : somr utils for actions                      #
##########################################################


Author(s)     : - Frédéric Le Roux <frederic.le-rxou@imj-prg.fr>
Maintainer(s) : - Frédéric Le Roux <frederic.le-rxou@imj-prg.fr>

Created       : July 2020 (creation)
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

from typing import Union
from copy import copy

from deaduction.pylib.mathobj import MathObject


def which_number_set(string: str):
    """
    Return 'ℕ', 'ℤ', 'ℚ', 'ℝ' if string represents a number, else None
    """
    ind = -1
    if '.' in string or '/' in string:
        ind = 2  # at least Q
    string = string.replace('.', '')
    string = string.replace('/', '')
    if not string.isdigit():
        return None
    else:
        return MathObject.NUMBER_SETS_LIST[ind]


def add_type_indication(item: Union[str, MathObject],
                        math_type: MathObject=None) -> Union[str, MathObject]:
    """
    Add type indication for Lean. e.g.
    '0' -> (0:ℝ)
    'x' -> (x:ℝ)
    :param item:        either a string (provided by user in TextDialog) or
    MathObject
    :param math_type:   math_type indication to add. If None, largest number
    set used in current context will be indicated
    :return: either     string or MathObject, with type indication in name
    """
    if math_type:
        number_type = math_type.which_number_set(is_math_type=True)
    if isinstance(item, str):
        number_set = which_number_set(item)
        if number_set and ':' not in item:
            if not math_type:
                MathObject.add_numbers_set(number_set)
                # Add type indication = largest set of numbers among used
                number_type = MathObject.number_sets[-1]
            item = f"({item}:{number_type})"  # e.g. (0:ℝ)
        return item
    elif isinstance(item, MathObject):
        info = copy(item.info)
        if not math_type:
            number_type = MathObject.number_sets[-1]
            math_type = number_type
        name = item.display_name
        # Do not put 2 type indications!!
        if (':' not in name
                and hasattr(item, 'info')):
            info['name'] = f"({name}:{number_type})"
        new_item = MathObject(node=item.node,
                              info=info,
                              children=item.children,
                              math_type=math_type)
        return new_item


lean_dic = {'epsilon': "ε",
            "delta": "δ"}


def pre_process_lean_code(lean_code: str) -> str:
    # (During test it happens that lean_code is a number)
    if not isinstance(lean_code, str):
        return lean_code

    for key in lean_dic:
        lean_code = lean_code.replace(key, lean_dic[key])
    return lean_code


def extract_var(potential_var: MathObject) -> MathObject:
    """
    Try to extract objects (not prop) from properties. This is called in case
    usr has selected, say, an equality, e.g. y = f(x), but really want to
    select y.
    """

    if potential_var.is_equality():
        # Removed: this may not be pertinent if not equality
        # or potential_var.is_inequality(is_math_type=True)
        #     or potential_var.is_belongs_or_included(is_math_type=True)):
        return potential_var.math_type.children[0]
    else:
        return potential_var

