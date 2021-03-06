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
from deaduction.pylib.mathobj import Goal, ProofStatePO, PropObj


def give_name0(goal: Goal, math_type: PropObj, hints: List[str] = []) -> str:
    """
    Provide a name for a new variable. Baby version.
    The list of names of all current variables is extracted from goal

    NB : if x : X but the property 'x belongs to A' is in context, then
    math_type could be A.

    :param goal: current_goal
    :param math_type: type of new variable
    :param hints: a hint for the future name
    :return: a name for the new variable
    """
    names = goal.extract_var_names()
    if isinstance(math_type, ProofStatePO):
        type_name = math_type.lean_data["name"]
        if len(type_name) == 1 and type_name.isupper():
            hint = type_name.lower()
            hints.append(hint)
    # first trial
    for potential_name in hints:
        if potential_name not in names:
            new_name = potential_name
            return new_name
    # second trial
    potential_name = hint[0]
    counter = 0
    while potential_name in names and counter < 26:
        potential_name = next(potential_name)
        counter += 1
    if counter != 26:
        return potential_name
    # third trial
    # TODO: try potential_name[0] + indice
    # but beware that latex and utf-8 must be treated differently.


def give_name(goal: Goal, math_type: PropObj, hints: List[str] = []) -> str:
    """
    Provide a name for a new variable. UNFINISHED VERSION.
    The list of names of all current variables is extracted from goal

    NB : if x : X but the property 'x belongs to A' is in context, then
    math_type could be A.

    :param goal: current_goal
    :param math_type: type of new variable
    :param hints: a hint for the future name
    :return: a name for the new variable
    """
    names = goal.extract_var_names()
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
    if isinstance(math_type, ProofStatePO):
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
        if potential_name not in names:
            new_name = potential_name
            return new_name
    # Second trial: hints with alphabetical order
    for name in hints:
        if name in mti_names:
            potential_name = next(name)
    # TODO : uncomplete

    new_name = ""
    return new_name


def next(letter: str) -> str:
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
        return letters(index)
    else:
        return letters[0]


def name_prolongate(names: List[str]) -> str:
    """
    given a list of variable names, compute the "next logical name"
    if any
    """
    # TODO
    pass


def pre_give_names(goal: Goal, math_types: List[PropObj]) -> List[List[str]]:
    """
    compute lists of possible names for each element of math_types,
    with empty pairwise intersection
    :param goal: current goal
    :param math_types: list of math types
    """
    # TODO: not implemented
    pass
