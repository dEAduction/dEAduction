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

from deaduction.pylib.mathobj import MathObject
from deaduction.config.config import (user_config,
                                      EXERCISE)

log = logging.getLogger(__name__)
EXERCISE.PROPERTY_COUNTER = 1
EXERCISE.USE_PRIMES_FOR_VARIABLES_NAMES = \
    user_config.getboolean('use_primes_for_variables_names')
EXERCISE.USE_SECONDS_FOR_VARIABLES_NAMES = \
    user_config.getboolean('use_seconds_for_variables_names')


def get_new_hyp(goal):
    """Find a fresh name for a new property
    The name is 'Hn' where n is the least integer such that Hn has never
    been given by the present function, and Hn is not in the current context

    Makes us of the Python global var Global.PROPERTY_COUNTER
    """
    forbidden_names = goal.extract_vars_names()

    counter = EXERCISE.PROPERTY_COUNTER
    potential_name = 'H' + str(counter)
    while potential_name in forbidden_names:
        counter += 1
        potential_name = 'H' + str(counter)
    EXERCISE.PROPERTY_COUNTER = counter + 1
    return potential_name


def give_local_name(math_type, body, hints: [str] = []):
    """
    Attribute a name to a local variable. See give_name below.

    :param math_type:   PropObj type of new variable
    :param body:        a PropObj inside which the new name will serve for a
    bound variable
    :param hints:       a list of hints for the future name
    :return:            a name for the new variable
    """
    forbidden_vars = body.extract_local_vars()
    return give_name(math_type, forbidden_vars, hints)


def give_global_name(math_type, goal, hints: [str] = []):
    """
    Attribute a name to a global variable See give_name below.

    :param math_type:   PropObj type of new variable
    :param goal:        current_goal
    :param hints:       a list of hints for the future name
    :return:            a name for the new variable
    """
    forbidden_vars = goal.extract_vars()
    return give_name(math_type, forbidden_vars, hints)


def give_name(math_type,
              forbidden_vars: [MathObject],
              hints: [str] = []) -> str:
    """
    Provide a name for a new variable. Baby version.
    Roughly speaking,
        - look if math_type has a name which starts with an uppercase letter,
        and if so add the corresponding lowercase letter as the main hint
        - if the hint is not in forbidden_names then it will be the name ; in
        the opposite case we will try the letters in alphabetical order from the
        hint.

    Exception: if math_type = set xxx, (the variable denotes a subset),
    attribute an uppercase letter

    NB : if x : X but the property 'x belongs to A' is in context, then
    math_type could be A.

    :param math_type:       PropObj type of new variable
    :param forbidden_vars:  list of variables that must be avoided
    :param hints:           a hint for the future name
    :return:                a name for the new variable
    """

    # determine list of forbidden names from forbidden variables
    forbidden_names = []  # a list of strings with no duplication
    for math_object in forbidden_vars:
        name = math_object.info['name']
        if name not in forbidden_names:
            forbidden_names.append(name)
    log.debug(f"giving name to bound var, hints = {hints} type={math_type}")
    log.debug(f"forbidden names: {forbidden_names}")

    ######################
    # special math types #
    ######################
    # subsets will be named with uppercase letters
    if math_type.node in ['SET', 'TYPE', 'PROP']:
        upper_case_name = True
    else:
        upper_case_name = False

    # Properties are named 'Hn' where n is an integer
    if math_type.is_prop():
        return get_new_hyp()

    ##################
    # managing hints #
    ##################

    if upper_case_name:
        hints = [hint[0].upper() for hint in hints]  # so each hint has only
        # one uppercase letter
    else:
        hints = [hint[0].lower() for hint in hints]  # so each hint has only
        # one lowercase letter

    # lower case: add main hint according to math_type's name
    if not upper_case_name and 'name' in math_type.info.keys():
        type_name = math_type.info["name"]
        if type_name[0].isupper():
            hint = type_name[0].lower()
            insert_maybe(hints, hint, position=0)

    # standard hints
    standard_hint = 'A' if math_type.node.startswith('SET') \
        else 'X' if math_type.node == 'TYPE' \
        else 'P' if math_type.node == 'PROP' \
        else 'f' if math_type.node == 'FUNCTION' \
        else 'x'
    insert_maybe(hints, standard_hint)

    ##########################################################
    # first trial: use hints, maybe with primes if permitted #
    ##########################################################
    for potential_name in hints:
        log.debug(f"trying {potential_name}...")
        if potential_name not in forbidden_names:
            new_name = potential_name
            return new_name
        # if hint = "x" and this is already the name of a variable with the
        # same math_type as the variable we want to name,
        # then try to use "x'"
        # here all hints are assumed to be the name of some variable
        elif EXERCISE.USE_PRIMES_FOR_VARIABLES_NAMES:
            name = potential_name
            index_ = forbidden_names.index(name)
            variable = forbidden_vars[index_]
            potential_name = name + "'"
            log.debug(f"trying {potential_name}...")
            if math_type == variable.math_type:
                if potential_name not in forbidden_names:
                    return potential_name
                elif EXERCISE.USE_SECONDS_FOR_VARIABLES_NAMES:
                    name = potential_name
                    index_ = forbidden_names.index(name)
                    variable = forbidden_vars[index_]
                    potential_name = name + "'"
                    log.debug(f"trying {potential_name}...")
                    if math_type == variable.math_type \
                            and not potential_name.endswith("'''") \
                            and not potential_name in forbidden_names:
                        return potential_name

    ########################################
    # second trial: use alphabetical order #
    ########################################
    starting_name = hints[0]
    counter = 0
    potential_name = starting_name
    max_letters = 3  # NB : must be ≤ 26 !
    while potential_name in forbidden_names and counter < max_letters + 1:
        potential_name = next_(potential_name)
        counter += 1
    if counter != max_letters:
        return potential_name
    #########################################
    # last trial: starting_name + subscript #
    #########################################
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
        return next_in_list(letter, upper_list)
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


def insert_maybe(L: list, item, position=None):
    """Insert in a list if item is not already in"""
    if item in L:
        return
    else:
        if position is None:
            position = len(L)
        L.insert(position, item)
