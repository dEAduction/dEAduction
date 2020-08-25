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


def give_local_name(math_type,
                    body,
                    hints: [str] = []):
    """
    :param math_type: PropObj type of new variable
    :param body: a PropObj inside which the new name will serve for a bound
    variable
    :param hints: a list of hints for the future name
    :return: a name for the new variable
    """
    forbidden_names = body.extract_local_vars_names()
    return give_name(math_type, forbidden_names, hints)


def give_global_name(math_type,
                     goal,
                     hints: [str] = []):
    """
    :param math_type: PropObj type of new variable
    :param goal: current_goal
    :param hints: a list of hints for the future name
    :return: a name for the new variable
    """
    forbidden_names = goal.extract_var_names()
    return give_name(math_type, forbidden_names, hints)


def give_name(math_type,
              forbidden_names: [str],
              hints: [str] = []) -> str:
    """
    Provide a name for a new variable. Baby version.
    Roughly speaking,
        - look if math_type has a name which starts with an upperwase letter,
        and if so add the corresponding lowercase letter as the main hint
        - if the hint is not in forbidden_names then it will be the name ; in
        the opposite case we will try the letters in alphabetical order from the
        hint.

    NB : if x : X but the property 'x belongs to A' is in context, then
    math_type could be A.

    :param math_type: PropObj type of new variable
    :param forbidden_names: list of names of other variables that must be
    avoided
    :param hints: a hint for the future name
    :return: a name for the new variable
    """
    # log.debug(f"giving name to bound var, type={math_type}, hints={hints}")
    # log.debug(f"forbidden names: {forbidden_names}")
    if hasattr(math_type, "lean_data"):
        type_name = math_type.lean_data["name"]
        if type_name[0].isupper():
            hint = type_name[0].lower()
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
    while potential_name in forbidden_names and counter < max_letters + 1:
        potential_name = next_(potential_name)
        counter += 1
    if counter != max_letters:
        return potential_name
    # last trial: starting_name + subscript
    # TODO: use index in utf8
    potential_name = starting_name
    counter = 0
    while potential_name + '_' + str(counter) in forbidden_names:
        counter += 1
    return potential_name + '_' + str(counter)

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