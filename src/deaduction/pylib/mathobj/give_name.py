"""
# give_name.py : provide names for new variables

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 07 2020 (creation)
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
from typing import List
import logging

import deaduction.pylib.logger as logger

log = logging.getLogger(__name__)


def give_name(goal,
              math_type,
              authorized_names: [str] = [],
              hints: [str] = [],
              po=None,     # todo : change name : local_context
              format_='utf8') -> str:
    """
    Provide a name for a new variable. Baby version.
    The list of names of all current variables is extracted from goal

    NB : if x : X but the property 'x belongs to A' is in context, then
    math_type could be A.

    :param goal: current_goal
    :param math_type: PropObj type of new variable
    :param authorized_names: list of names which can be used even in forbidden
    list
    (useful for applying an existence statement)
    :param hints: a hint for the future name
    :param po: a PropObj inside which the new name will serve for a bound
    variable
    :param format_: utf or latex. No difference for the moment.
    :return: a name for the new variable
    """
    if po:
        forbidden_names = po.extract_local_vars_names()
        # for name in authorized_names:
        #     try:
        #         forbidden_names.remove(name)
        #     except ValueError:
        #         pass
    else:
        forbidden_names = goal.extract_var_names()
    #log.debug(f"giving name to bound var, type={math_type}, hints={hints}")
    #log.debug(f"forbidden names: {forbidden_names}")
    if hasattr(math_type, "lean_data"):
        type_name = math_type.lean_data["name"]
        if len(type_name) == 1 and type_name.isupper():
            hint = type_name.lower()
            hints.insert(0, hint)
    # first trial
    for potential_name in hints:
        if potential_name not in forbidden_names:
            new_name = potential_name
            return new_name
    # second trial: use alphabetical order
    if hints:
        starting_name = hints[0]
    else:
        starting_name = 'x'
    counter = 0
    potential_name = starting_name
    max_letters = 3  # NB : must be ≤ 26 !
    while potential_name in forbidden_names and counter < max_letters:
        potential_name = next_(potential_name)
        counter += 1
    if counter != 26:
        return potential_name
    # last trial: starting_name + subscript
    # TODO: use index in utf8
    potential_name = starting_name
    counter = 0
    while potential_name + '_' + str(counter) in forbidden_names:
        counter += 1


# TODO: implement the following more sophisticated version
def give_name_v2(goal, math_type, hints: List[str] = []) -> str:
    """
    Provide a name for a new variable. UNFINISHED VERSION.
    The list of names of all current variables is extracted from goal

    NB : if x : X but the property 'x belongs to A' is in context, then
    math_type could be A.

    :param goal: current_goal
    :param math_type: PropObj, type of new variable
    :param hints: a hint for the future name
    :return: a name for the new variable
    """
    forbidden_names = goal.extract_var_names()
    mt_index = [mt for mt, mti in goal.math_types].index(math_type)
    mt_instances = goal.math_types[mt_index][1]
    mti_names = [pfpo.lean_data["name"] for pfpo in
                 mt_instances]
    ###########################
    # compute a list of hints #
    ###########################
    # first look in the names of instances of math_type, if any
    if len(mti_names) > 1:
        hint = name_prolongate(mti_names)
        if hint != "FAILED_":
            hints.insert(0, hint)
        else:
            hint = mti_names[0]
            hints.insert(0, hint)
    elif len(mti_names) == 1:
        hint = mti_names[0]
        hints.insert(0, hint)
    # then look at the name of math_type
    if hasattr(math_type, "lean_data"):
        type_name = math_type.lean_data["name"]
        if len(type_name) == 1 and type_name.isupper():
            hint = type_name.lower()
            hints.append(hint)
    # or use tradition for specific types
    if math_type.node == "FUNCTION":
        hints.append("f")

    ###############################
    # compute new name from hints #
    ###############################
    # First trial: raw hints
    for potential_name in hints:
        if potential_name not in forbidden_names:
            new_name = potential_name
            return new_name
    # Second trial: hints with alphabetical order
    for name in hints:
        if name in mti_names:
            potential_name = next_(name)
    # TODO : uncomplete

    new_name = ""
    return new_name


def next_(letter: str) -> str:
    """
    given a letter, return the next letter in the alphabet
    """
    lower_list = "abcdefghijklmnopqrstuvwxyz"
    upper_list = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    utf8_subscript_digits = "₀₁₂₃₄"  # TODO
    if letter in lower_list:
        return next_in_list(letter, lower_list)
    elif letter in upper_list:
        return next_in_list(letter, lower_list)
    elif letter in utf8_subscript_digits:
        return next_in_list(letter, utf8_subscript_digits)


def next_in_list(letter: str, letters: List[str]):
    """
    given a letter that is certified to belongs to letters,
    provide the next letter ( mod len(letters) )
    """
    index = letters.index(letter) + 1
    if index < len(letters):
        return letters[index]
    else:
        return letters[0]


def name_prolongate(names: List[str]) -> str:
    """
    given a list of variable names, compute the "next logical name"
    if any
    """
    # TODO
    pass


def pre_give_names(goal, math_types: list) -> List[List[str]]:
    """
    compute lists of possible names for each element of math_types,
    with empty pairwise intersection
    :param goal: current goal
    :param math_types: list of math types
    """
    # TODO: not implemented
    pass
