"""
##################################################
# give_name.py : provide names for new variables #
##################################################

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
# from deaduction.config.config import (EXERCISE)

import deaduction.pylib.config.vars as cvars

log = logging.getLogger(__name__)


def get_new_hyp(proof_step) -> str:
    """
    Call get_new_hyp_from_forbidden_names with a list of forbidden names
    that are the current goal's variables' names.
    :param proof_step: current proof_step, contains goal and property_counter
    :return: name for a new property, like 'H3'.
    """
    forbidden_names = proof_step.goal.extract_vars_names()
    return get_new_hyp_from_forbidden_names(proof_step,
                                            forbidden_names)


def get_new_hyp_from_forbidden_names(proof_step,
                                     forbidden_names: [str]) -> str:
    """
    Find a fresh name for a new property.
    The name is 'Hn' where n is the least integer such that Hn has never
    been given by the present function, and Hn is not in the current context.
    Makes use of the Python global var PROPERTY_COUNTER.

    :param proof_step: current proof_step
    :param forbidden_names: list of names of variables in the context
    :return:                str, a fresh name
    """
    counter = proof_step.property_counter
    potential_name = 'H' + str(counter)
    while potential_name in forbidden_names:
        counter += 1
        potential_name = 'H' + str(counter)
    proof_step.property_counter = counter + 1
    return potential_name


def give_local_name(math_type: MathObject,
                    body: MathObject,
                    hints: [str] = [],
                    forbidden_vars: [MathObject] = []) -> str:
    """
    Attribute a name to a local variable. See give_name below.
    Mainly computes all pertinent forbidden variables, by adding vars from
    body to the forbidden_vars list.

    :param math_type:       MathObject type of new variable
    :param body:            a MathObject inside which the new name will serve
                            as a bound variable
    :param hints:           a list of hints (str) for the future name
    :param forbidden_vars:  list of vars (MathObject) whose names are forbidden
    :return:                str, a name for the new variable
    """

    more_forbidden_vars = body.extract_local_vars()
    names = [var.info['name'] for var in forbidden_vars]
    # log.debug(f'Giving name to bound var, a priori forbidden names ={names}')
    more_names = [var.info['name'] for var in more_forbidden_vars]
    # log.debug(f'Additional forbidden names ={more_names}')
    forbidden_vars.extend(more_forbidden_vars)

    exclude_glob_vars = cvars.get(
                                'logic.do_not_name_dummy_vars_as_global_vars',
                                 False)
    if exclude_glob_vars:
        pass
        # FIXME: proof_step is not available here!
        # more_forbidden_vars = proof_step.goal.extract_vars()
        # forbidden_vars.extend(more_forbidden_vars)
    use_indices = cvars.get('logic.use_indices_for_dummy_variables', True)
    return give_name(math_type, forbidden_vars, hints, None, use_indices)


def give_global_name(math_type: MathObject,
                     proof_step,
                     hints: [str] = []) -> str:
    """
    Attribute a name to a global variable. See give_name below.
    Here the forbidden variables are all variables from the context.

    :param math_type:   PropObj type of new variable
    :param goal:        current_goal
    :param hints:       a list of hints for the future name
    :return:            a name for the new variable
    """
    forbidden_vars = proof_step.goal.extract_vars()
    return give_name(math_type, forbidden_vars, hints, proof_step)


def give_name(math_type,
              forbidden_vars: [MathObject],
              hints: [str]=[],
              proof_step=None,
              use_indices=False) -> str:
    """
    Provide a name for a new variable.
    Roughly speaking,
        - look if math_type has a name which starts with an uppercase letter,
        and if so add the corresponding lowercase letter as the main hint
        - if the hint is not in forbidden_names then it will be the name ; in
        the opposite case we will try the letters in alphabetical order from
        the hint.

    If display.use_primes_for_variables_names is True, then will try to use
    prime: e.g. if hint = ["x"] but "x" is already used, if math_type equals
    the math_type of x, then "x'" will be tried, and even "x''" if
    EXERCISE.USE_SECONDS_FOR_VARIABLES_NAMES is True.

    Exception: if math_type = set xxx, (the variable denotes a subset),
    attribute an uppercase letter

    NB : if x : X but the property 'x belongs to A' is in context, then
    math_type could be A for a better hinting.

    :param math_type:       PropObj type of new variable
    :param forbidden_vars:  list of variables that must be avoided
    :param hints:           a hint for the future name
    :param proof_step:      current proof_step, useful only for naming props.
    :return:                a name for the new variable
    """

    # FIXME: choice of names needs to be improved!

    # List of forbidden names (with repeat)
    forbidden_names = [var.info['name'] for var in forbidden_vars]
    # log.debug(f"giving name to var, hints = {hints} type={math_type}")
    # log.debug(f"forbidden names: {forbidden_names}")

    ######################
    # special math types #
    ######################
    # Subsets will be named with uppercase letters
    if math_type.node in ['SET', 'TYPE', 'PROP']:
        upper_case_name = True
    else:
        upper_case_name = False

    # Properties are named 'Hn' where n is an integer
    if math_type.is_prop():
        if proof_step:  # For global prop names (-> H1, H2, ...)
            return get_new_hyp_from_forbidden_names(proof_step,
                                                    forbidden_names)
        else:  # For local prop names
            pass
    ##################
    # Managing hints #
    ##################
    # Avoid bad hints, e.g. for families where hints could be {E_i, i in I}
    # All hints have to be acceptable variable names!
    alphabet_lower = "abcdefghijklmnopqrstuvwxyz"
    alphabet_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    alphabet_greek = "αβγδεζηθικλμνξοπρςστυφχψω" \
                     + "ΓΔΘΛΞΠΣΦΨΩ"
    alphabet = alphabet_lower + alphabet_upper + alphabet_greek
    for hint in hints:
        if hint not in alphabet:
            hints.remove(hint)

    if upper_case_name:
        hints = [hint[0].upper() for hint in hints]
        # Each hint is one uppercase letter
    else:
        hints = [hint[0].lower() for hint in hints]
        # Each hint is one lowercase letter

    # Lower case: add main hint
    # according to math_type's name
    # e.g. math_type is "X" -> hint[0] = 'x'
    # fixme: in some case main hint must be added in pole position,
    #  but not always...
    if (not upper_case_name) and 'name' in math_type.info:
        type_name = math_type.info["name"]
        if type_name[0] in alphabet_upper:
            hint = type_name[0].lower()
            # Insert iff hint is not already in hints
            # position = 0 --> pole position
            # position = 1 --> second position
            insert_maybe(hints, hint, position=0)

    # Standard hints
    standard_hints = ['A'] if math_type.node.startswith('SET') \
        else ['X'] if math_type.is_type(is_math_type=True) \
        else ['P'] if math_type.is_prop(is_math_type=True) \
        else ['f'] if math_type.is_function(is_math_type=True) \
        else ['n', 'm', 'p'] if math_type.is_nat(is_math_type=True) \
        else ['x']
    for standard_hint in standard_hints:
        insert_maybe(hints, standard_hint)

    ###########################
    # Easy case : use indices #
    ###########################
    if use_indices and hints:
        radical = hints[0]
        subscript = -1
        potential_name = radical  # Start with no index!
        while potential_name in forbidden_names:
            subscript += 1
            potential_name = radical + '_' + str(subscript)
        return potential_name
    ##########################################################
    # First trial: use hints, maybe with primes if permitted #
    ##########################################################
    for potential_name in hints:
        # Try each hints successively
        # log.debug(f"trying {potential_name}...")
        if potential_name not in forbidden_names:
            return potential_name
        # If hint = "x" and this is already the name of a variable with the
        # same math_type as the variable we want to name,
        # then try to use "x'"
        elif cvars.get("display.use_primes_for_variables_names"):
            # here potential_name are assumed to be the name of some variable
            name = potential_name
            index_ = forbidden_names.index(name)
            variable = forbidden_vars[index_]
            potential_name = name + "'"
            # log.debug(f"Trying {potential_name}...")
            if math_type == variable.math_type:
                # Use "x'" only if "x" has the same type
                if potential_name not in forbidden_names:
                    return potential_name
                elif cvars.get('display.use_seconds_for_variables_names'):
                    name = potential_name
                    index_ = forbidden_names.index(name)
                    variable = forbidden_vars[index_]
                    potential_name = name + "'"
                    # log.debug(f"Trying {potential_name}...")
                    if math_type == variable.math_type \
                            and not potential_name.endswith("'''") \
                            and potential_name not in forbidden_names:
                        return potential_name

    ########################################################
    # Second trial: use alphabetical order from first hint #
    ########################################################
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


#########
# UTILS #
#########
def next_(letter: str) -> str:
    """
    Given a letter, return the next letter in the alphabet
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
    Given a letter that is certified to belongs to letters,
    provide the next letter ( mod len(letters) )
    """
    index = letters.index(letter) + 1
    if index < len(letters):
        return letters[index]
    else:
        return letters[0]


def insert_maybe(L: list, item, position=None):
    """Insert or displace item in a list at the given position"""
    if item in L:
        L.remove(item)
    if position is None:
        position = len(L)
    L.insert(position, item)
