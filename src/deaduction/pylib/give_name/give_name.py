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

# from .math_object import MathObject
# class MathObject:
#     pass

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


# def give_local_name(math_type,
#                     body,
#                     hints: [str] = None,
#                     forbidden_vars = None) -> str:
#     """
#     Attribute a name to a local variable. See give_name below.
#     Mainly computes all pertinent forbidden variables, by adding vars from
#     body to the forbidden_vars list.
#
#     :param math_type:       MathObject type of new variable
#     :param body:            a MathObject inside which the new name will serve
#                             as a bound variable
#     :param hints:           a list of hints (str) for the future name
#     :param forbidden_vars:  list of vars (MathObject) whose names are forbidden
#     :return:                str, a name for the new variable
#     """
#
#     if hints is None:
#         hints = []
#     if forbidden_vars is None:
#         forbidden_vars = []
#     # Fixme: used only in display_math
#     more_forbidden_vars = body.extract_local_vars()
#     names = [var.info['name'] for var in forbidden_vars]
#     # log.debug(f'Giving name to bound var, a priori forbidden names ={names}')
#     more_names = [var.info['name'] for var in more_forbidden_vars]
#     # log.debug(f'Additional forbidden names ={more_names}')
#     forbidden_vars.extend(more_forbidden_vars)
#
#     exclude_glob_vars = cvars.get(
#                                 'logic.do_not_name_dummy_vars_as_global_vars',
#                                  False)
#     if exclude_glob_vars:
#         pass
#         # FIXME: proof_step is not available here!
#         # more_forbidden_vars = proof_step.goal.extract_vars()
#         # forbidden_vars.extend(more_forbidden_vars)
#     use_indices = cvars.get('logic.use_indices_for_dummy_variables', True)
#     return give_name(math_type, forbidden_vars, hints, None, use_indices)


def give_global_name(math_type,
                     proof_step,
                     hints: [str] = None,
                     strong_hint: str = '') -> str:
    """
    Attribute a name to a global variable. See give_name below.
    Here the forbidden variables are all variables from the context.

    :param math_type:   PropObj type of new variable
    :param goal:        current_goal
    :param hints:       a list of hints for the future name
    (only the initial is taken into account)
    :param strong_hint:  a strong hint, to be used if possible
    :return:            a name for the new variable
    """
    if not hints:
        hints = []
    forbidden_vars = proof_step.goal.context_objects
    if strong_hint:
        forbidden_names = [var.info['name'] for var in forbidden_vars]
        if strong_hint not in forbidden_names:
            return strong_hint

    return give_name(math_type, forbidden_vars, hints, proof_step)


def give_name(math_type,
              forbidden_vars,
              hints: [str] = None,
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

    if hints is None:
        hints = []
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
        elif cvars.get("display.allow_primes_for_names"):
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
                elif cvars.get('display.allow_seconds_for_names'):
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


alphabet_lower = "abcdefghijklmnopqrstuvwxyz"
alphabet_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
alphabet_greek = "αβγδεζηθικλμνξοπρςστυφχψω" \
                 + "ΓΔΘΛΞΠΣΦΨΩ"
ALPHABET = alphabet_lower + alphabet_upper + alphabet_greek


def hints_from_type(math_type, hints=None):
    """
    Provides a non void list of hints for naming a new var of type math_type.

    * The name of math_type can sometimes provide a hint.
    * For some types, hint is provided by tradition
    (e.g. functions, sets, ...).
    """
    if not hints:
        hints = []

    # Avoid bad hints, e.g. for families where hints could be {E_i, i in I}
    # All hints have to be acceptable variable names!
    for hint in hints:
        if hint not in ALPHABET:
            hints.remove(hint)

    # Subsets will be named with uppercase letters
    upper_case_name = (math_type.node in ['SET', 'TYPE', 'PROP'])

    if upper_case_name:
        hints = [hint[0].upper() for hint in hints]
        # Each hint is one uppercase letter
    else:
        hints = [hint[0].lower() for hint in hints]
        # Each hint is one lowercase letter

    # Try first letter of math_type if upper
    if (not upper_case_name) and 'name' in math_type.info:
        type_name = math_type.info["name"]
        if type_name[0] in alphabet_upper:
            hint = type_name[0].lower()
            insert_maybe(hints, hint, position=0)
            # if main_hint:
            #     insert_maybe(hints, hint, position=1)
            # else:
            #     insert_maybe(hints, hint, position=0)
            #     main_hint = True

    # Standard hints
    standard_hints = ['A'] if math_type.node.startswith('SET') \
        else ['X'] if math_type.is_type(is_math_type=True) \
        else ['P'] if math_type.is_prop(is_math_type=True) \
        else ['f'] if math_type.is_function(is_math_type=True) \
        else ['n', 'm', 'p'] if math_type.is_nat(is_math_type=True) \
        else ['x']
    for standard_hint in standard_hints:
        insert_maybe(hints, standard_hint)

    return hints


def hints_by_name(named_vars, unnamed_var_nb: int):
    """
    Look into named_vars: if they all start by the same letter,
    then this is our main hint. If not, return a sequence of new letters.
    """

    letters = {var.display_name[0] for var in named_vars}
    if not letters:
        return []
    elif len(letters) == 1:
        letter = letters.pop()
        return [letter]
    else:
        letters = list(letters)
        letters.sort()
        new_letters = near(letters, unnamed_var_nb)
        return new_letters


def name_with_index(unnamed_vars, radical, forbidden_names, start=0):
    """
    Name unnamed vars using radical and indices, avoiding forbidden_names,
    with index starting at start. Always succeeds!
    """
    subscript = start
    potential_name = radical + '_' + str(subscript)
    for var in unnamed_vars:
        while potential_name in forbidden_names:
            subscript += 1
            potential_name = radical + '_' + str(subscript)
        var.give_name(potential_name)
        subscript += 1
        potential_name = radical + '_' + str(subscript)


def try_names(vars_to_name, forbidden_names, names):
    """
    Try to name all vars_to_name according to names, avoiding
    forbidden_names.

    :param vars_to_name: MathObject, dummy_vars.
    :param forbidden_names: list of names already used, to be avoided.
    :param names: list of potential names.
    """

    # allowed_names = [name for name in names if name not in forbidden_names]
    # if len(allowed_names) >= len(vars_to_name):
    #     for var, name in zip(vars_to_name, allowed_names):
    #         var.give_name(name)
    #     return True
    # else:
    #     return False
    names = allowed_names(names, forbidden_names, len(vars_to_name))
    if names:
        for var, name in zip(vars_to_name, names):
            var.give_name(name)
        return True
    else:
        return False


def allowed_names(names: [str], forbidden_names: [str], number: int):
    """
    If possible, return <number> item from <names> that are not in
    forbidden_names. If not, return False.
    """
    allowed = [name for name in names if name not in forbidden_names]
    if len(allowed) >= number:
        return allowed[:number]
    else:
        return False


def indexed_names(radical, forbidden_names, start=0, number=1):
    """
    Return names using radical and indices, avoiding forbidden_names,
    with index starting at start. Always succeeds!
    """
    names = []
    subscript = start
    potential_name = radical + '_' + str(subscript)
    for i in range(number):
        while potential_name in forbidden_names:
            subscript += 1
            potential_name = radical + '_' + str(subscript)
        names.append(potential_name)
        subscript += 1
        potential_name = radical + '_' + str(subscript)

    return names


def names_for_types(math_types, proof_step, number=1,
                    hints=None, strong_hint=None) -> [str]:
    """
    Provide <number> names for vars of given math_types, given the goal
    indicated in proof_step.
    math_types is either one MathObject or a list of MathObject.
    """

    # Case of multiple math_types:
    if isinstance(math_types, list):
        distinct_types = inj_list(math_types)
        names = []
        for math_type in distinct_types:
            number = math_types.count(math_type)
            names.extend(names_for_types(math_type, proof_step, number))
        return names

    math_type = math_types
    context = proof_step.goal.context_objects
    forbidden_vars = context
    named_var = [var for var in context if var.math_type == math_type]
    return names_for_type(math_type, named_var, forbidden_vars, number,
                          hints, strong_hint)


def names_for_type(math_type, named_vars, forbidden_vars, number=1,
                   hints=None, strong_hint=None, use_indices=False) -> [str]:
    """
    Provide a list of <number> names for math_type, avoiding names from
    forbidden_vars, using hints and strong_hint. The tag use_indices forces
    the use of indices.
    """
    forbidden_names = inj_list([var.info['name'] for var in forbidden_vars])

    if not hints:
        hints = []

    if strong_hint:
        if number == 1:
            name = allowed_names([strong_hint], forbidden_names, 1)
            if name:
                return name
        insert_maybe(hints, strong_hint, position=0)

    named_vars_names = [var.info['name'] for var in named_vars]  # No rep

    hints_from_vars = hints_by_name(named_vars, number)
    hints_type = hints_from_type(math_type)
    assert hints_type != []

    ###########################
    # Easy case : use indices #
    ###########################
    if use_indices:
        hint = strong_hint if strong_hint else hints_type[0]
        return indexed_names(hint, forbidden_names, number=number)

    if len(hints_from_vars) == number:
        # If no name is forbidden, use this for naming
        matching = True
        for name in hints_from_vars:
            if name in forbidden_names:
                matching = False
        if matching:
            return hints_from_vars

    # Main hint is hints_from_vars if there is only one, otherwise from type
    more_hints = hints_from_vars + hints_type if len(hints_from_vars) == 1 \
        else hints_type + hints_from_vars
    hints += more_hints

    allow_indices = cvars.get("logic.allow_indices_for_names", True)
    allow_primes  = cvars.get("display.allow_primes_for_names", True)
    allow_seconds = cvars.get("display.allow_seconds_for_names")

    for hint in hints:
        # Try each hint successively
        # log.debug(f"trying {hint}...")
        hint_prime = hint + "'"
        hint_second = hint + "''"
        total_vars_nb = len(forbidden_vars) + number
        # (1) Collect a sequence of trials
        trials = []  # Each term will be a potential LIST of names
        if allow_primes:
            trials.append([hint, hint_prime])
            if allow_seconds and hint_prime in named_vars_names:
                # Consider second only if prime is already used
                trials.append([hint,
                               hint_prime,
                               hint_second])
        if allow_indices:
            index_trial = [hint + "_" + str(nb)
                           for nb in range(total_vars_nb - 1)]
            trials.append(index_trial)
        letters_trial = near([hint], total_vars_nb)
        trials.append(letters_trial)
        # (2) Try each trial
        for trial in trials:
            names = allowed_names(trial, forbidden_names, number)
            if names:
                return names

    # Use indices, finally!
    hint = hints[0]
    return indexed_names(hint, forbidden_names, number=number)


def name_bound_vars(math_type,
                    named_vars,
                    unnamed_vars,
                    forbidden_vars):
    """
    Name all vars in unnamed_vars, assumed to be dummy vars sharing type
    math_type, using named_vars (of the same type) as clues, and avoiding
    names of forbidden_vars.

    :param math_type:
    :param named_vars:
    :param unnamed_vars: list of dummy vars to be named, ordered
    :param forbidden_vars:
    """
    # log.debug("Naming vars (type, named, unnamed, forbidden):")
    # log.debug(math_type.to_display())
    # log.debug(f"{[var.to_display() for var in named_vars]}")
    # log.debug(f"{[var.to_display() for var in unnamed_vars]}")
    # log.debug(f"{[var.to_display() for var in forbidden_vars]}")

    forbidden_names = inj_list([var.info['name'] for var in forbidden_vars])
    named_vars_names = [var.info['name'] for var in named_vars]  # No rep

    hints_from_vars = hints_by_name(named_vars, len(unnamed_vars))
    hints_type = hints_from_type(math_type)
    assert hints_type != []

    if math_type.display_name == 'ℝ':
        var = unnamed_vars[0]
        if 'hint_name' in var.info:
            initial = var.info['hint_name']
        insert_maybe(hints_type, initial, position=0)

    ###########################
    # Easy case : use indices #
    ###########################
    use_indices = cvars.get("logic.force_indices_for_dummy_vars", False)
    if use_indices:  # Force indices in dummy vars
        hint = hints_type[0]
        name_with_index(unnamed_vars, hint, forbidden_names)
        return

    if len(hints_from_vars) == len(unnamed_vars):
        # If no name is forbidden, use this for naming
        matching = True
        for name in hints_from_vars:
            if name in forbidden_names:
                matching = False
        if matching:
            for name, var in zip(hints_from_vars, unnamed_vars):
                var.give_name(name)
                # var.info["name"] = name
            return

    # Main hint is hints_from_vars if there is only one, otherwise from type
    hints = hints_from_vars + hints_type if len(hints_from_vars) == 1 \
        else hints_type + hints_from_vars

    allow_indices = cvars.get("logic.allow_indices_for_names", True)
    allow_primes  = cvars.get("display.allow_primes_for_names", True)
    allow_seconds = cvars.get("display.allow_seconds_for_names")
    success = False

    for hint in hints:
        # Try each hint successively
        # log.debug(f"trying {hint}...")
        hint_prime = hint + "'"
        hint_second = hint + "''"
        total_vars_nb = len(forbidden_vars) + len(unnamed_vars)
        # (1) Collect a sequence of trials
        trials = []  # Each term will be a potential LIST of names
        if allow_primes:
            trials.append([hint, hint_prime])
            if allow_seconds: # and hint_prime in named_vars_names:
                # Consider second only if prime is already used?
                trials.append([hint,
                               hint_prime,
                               hint_second])
        if allow_indices:
            index_trial = [hint + "_" + str(nb)
                           for nb in range(total_vars_nb)]
            trials.append(index_trial)
        letters_trial = near([hint], total_vars_nb)
        trials.append(letters_trial)
        # (2) Try each trial
        for trial in trials:
            success = try_names(unnamed_vars, forbidden_names, trial)
            if success:
                break
        if success:
            break

    if not success:
        # Use indices, finally!
        hint = hints_type[0]
        name_with_index(unnamed_vars, hint, forbidden_names)
        return


def name_single_bound_var(bound_var):
    """
    Give name to some isolated bound var, e.g. useful for sequences where
    variable "n" is used independently of the context.

    :param bound_var: MathObject
    """
    name_bound_vars(bound_var.math_type, named_vars=[],
                    unnamed_vars=[bound_var], forbidden_vars=[])


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


def near(letters, nb_new_letters):
    """
    Return a letter which is "near" letters:
    - first which is not in letters, starting with letters[0]
    - except if this is void, in that case fisrt before letters[0].
    """
    letters.sort()
    new_letters = []
    for alphabet in [alphabet_lower, alphabet_upper, alphabet_greek]:
        if letters[0] in alphabet:
            index = 0
            letter = letters[index]
            alphabet_index = alphabet.index(letter)
            end_of_alphabet = False
            # First search in the positive direction
            while index < len(letters)-1:
                letter = letters[index]
                next_letter = letters[index + 1]
                if next_letter not in alphabet:
                    new_letters.extend(alphabet[alphabet_index+1:])
                    end_of_alphabet = True
                    break
                # next_letter is in alphabet: get new letters, and go on
                next_alphabet_index = alphabet.index(next_letter)
                new_letters.extend(alphabet[alphabet_index + 1:
                                            next_alphabet_index])
                index += 1
                letter = letters[index]
                alphabet_index = alphabet.index(letter)

            if len(new_letters) < nb_new_letters:  # Not enough
                if not end_of_alphabet:  # last letter is in alphabet
                    last_index = alphabet.index(letters[-1])
                    new_letters.extend(alphabet[last_index + 1:])
                first_index = alphabet.index(letters[0])
                # Add beginning of alphabet in reverse order
                more = list(alphabet[:first_index])
                more.reverse()
                new_letters.extend(more)

            if len(new_letters) < nb_new_letters:  # Failure
                return None
            else:
                new_letters = new_letters[:nb_new_letters]
                return new_letters

    return None


def inj_list(list_: list):
    """
    Return a list with same elements of list_ but no repetition.
    """
    inj_list = []
    for item in list_:
        if item not in inj_list:
            inj_list.append(item)
    return inj_list


def insert_maybe(L: list, item, position=None):
    """Insert or displace item in a list at the given position"""
    if item in L:
        L.remove(item)
    if position is None:
        position = len(L)
    L.insert(position, item)


if __name__ == "__main__":
    letters = ['A', 'C']
    L = near(letters, 3)
    print(L)

