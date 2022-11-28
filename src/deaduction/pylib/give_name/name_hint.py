"""
##########################################################
# name_hint.py : provide classes NameHint and NameScheme #
##########################################################

This file provides utility functions for give_name, that deals with strings.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 11 2022 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2022 the dEAduction team

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

import deaduction.pylib.config.vars as cvars
from deaduction.pylib.give_name.names import (Case,
                                              alphabet,
                                              greek_alphabet,
                                              pure_letter_lists,
                                              potential_names)


# Typical letters used for some math types
letter_hints_from_type_node = {
    'TYPE': (('XYZW', 'EFG'), Case.UPPER_ONLY),
    'SET': (('ABCDEFG', ), Case.UPPER_ONLY),
    'SET_FAMILY': (('ABCDEFG', ), Case.UPPER_ONLY),
    'PROP': (('PQRST', ), Case.UPPER_ONLY),
    'FUNCTION': (('fgh', 'φψ', 'FGH', 'ΦΨ'), Case.LOWER_MOSTLY),
    'SEQUENCE': (('uvw', ), Case.LOWER_MOSTLY)
}


def letter_hints_from_type(math_type) -> tuple:
    """
    Return lists of preferred letters for naming a math object of given math
    type, and a (compatible) case preference.
    e.g. 'TYPE' --> (('XYZW', 'EFG'), Case.UPPER_ONLY)
    """
    letters = tuple()
    # TODO: add 'SET' if display.use_set_name_as_hint_for_naming_elements

    # (1) Names of elements
    # If self is a set, try to name its terms (elements) according to
    # its name, e.g. X -> x.
    case = Case.LOWER_MOSTLY  # Default
    if math_type.is_type():
        case = Case.LOWER_ONLY
        if math_type.display_name.isalpha() and math_type.display_name[0].isupper():
            letters = (math_type.display_name[0].lower(), )

    # (2) Names of sequences
    elif math_type.is_sequence():
        seq_type = math_type.children[1]
        if not seq_type.is_number():
            letters = (letter_hints_from_type(seq_type), )

    # (3) Standard hints
    more_letters, new_case = letter_hints_from_type_node.get(math_type.node,
                                                             (tuple(), None))

    if new_case:
        case = new_case

    if math_type.is_N() or math_type.is_Z():
        more_letters = ('npqk', )
        case = Case.LOWER_MOSTLY
    elif math_type.is_R():
        more_letters = ('xyztw', 'δεη')
        case = Case.LOWER_MOSTLY

    letters += more_letters

    return letters, case


def new_letter_from_bad(letter: str, existing_hints, case: Case) -> str:
    """
    Return a new letter for a NameHint, from a given letter which assumed to be
    equal to som other existing NameHint.
    The algorithm is to take as name hint the first
    available letter in the names list associated to the conflicting
    NameHint. If no letter is available, we use the pure_letter_lists()
    function, that provides some letters list containing the given letter.
    In case this fails, which should be very rare, we choose the first
    available letter in the alphabet(!).

    The letter will be compatible with case, except maybe if it comes from
    previously given names in the context which were not compatible.
    """

    # (1) Find conflicting hint
    conflicting_hint = None
    for hint in existing_hints:
        if letter == hint.letter:
            conflicting_hint = hint
            break

    # (2) Find first available letter
    available_letter = ""
    unavailable_letters = [hint.letter for hint in existing_hints]
    good_names = conflicting_hint.names if conflicting_hint else None
    if not good_names:
        good_names = sum(pure_letter_lists(letter, case=case), [])\
                     if letter else []
    # e.g. [['f', 'g', 'h'],['f', 'F']]
    bad_names = list(alphabet + greek_alphabet)
    for names in good_names + bad_names:
        for letter in names:
            letter = case.modify(letter, strongly=True)
            if letter not in unavailable_letters:
                available_letter = letter
                break
        if available_letter:
            break
    if not available_letter:
        logging.warning("NO MORE LETTER AVAILABLE for naming!!")

    return available_letter


class NameHint:
    """
    A class to provide names for all vars of a given type.
    There are two kinds of NameHint:
    - the generic NameHint is associated to a given math_type, and will be
    used naming all vars (bound vars of global vars introduced by "intro")
    of this type.
    - some NameHint are associated to a couple
        (math_type, preferred letter).
    This is used in particular for numbers, because real numbers that should
    be named 'epsilon' cannot be named 'x', and vice versa.
    Such a NameHint will be used to name all bound var sharing its math_type
    and preferred letter, as provided by BoundVar.preferred_letter() method.
    Actually, this last condition has been replaced by a less rigid one,
    i.e. the preferred letter should be in the NameHint's names list.

    The case enum tells if self accept lower/upper letters, and what if both
    are accepted, which one is preferred. The letter attribute must be
    compatible with this, and the names list takes it into account.
    """
    # TODO: test if case compatibility works

    letter: str = 'x'  # Default letter
    case: Case = Case.LOWER_MOSTLY
    use_index = cvars.get('display.use_indices', True)
    prime_over_index = cvars.get('display.use_primes_over_indices', True)

    def __init__(self, math_type, preferred_letter, letter, case):
        self.math_type = math_type
        self.preferred_letter = preferred_letter
        self.letter = letter
        self.case = case
        self.names = []

        if math_type.is_sequence(is_math_type=True):
            self.use_index = False

    def __str__(self):
        return self.letter

    @classmethod
    def from_math_type(cls, math_type, preferred_letter='',
                       existing_hints=None, friendly_names=None):
        """
        Return the hint corresponding to math_type and preferred_letter. The
        math_type must coincide, and preferred_letter must be in self.names.
        (Alternatively, we could impose the stronger condition that the
        preferred_letters coincide).

        If no hint fit,
        create a new hint and append it to existing_hints. The main task is
        to find a suitable letter for naming hint. The letter must be
        distinct of all letters of existing_hints.
        We try, in order,
            - the preferred letter,
            - friendly names (e.g. names already given to this math_type)
            - letters provided by the letter_hints_from_type() function.
            - letters provided by the new_letter_from_bad() function.
        """

        usable_letters = alphabet + greek_alphabet
        usable_letters += usable_letters.upper()
        if preferred_letter and preferred_letter not in usable_letters:
            preferred_letter = ''

        if not friendly_names:
            friendly_names = []
        if existing_hints is None:
            existing_hints = []

        # (1) Search for math_type among existing hints
        for hint in existing_hints:
            if hint.math_type == math_type:
                if not preferred_letter or preferred_letter in hint.names:
                    return hint

        # (2) No existing hint: create one
        # (a) Try strong_hint
        letters = []
        if preferred_letter:
            letters = [preferred_letter]

        # (b) Try (first letter of) friendly names
        letters.extend([friendly_name[0] for friendly_name in friendly_names
                        if friendly_name[0] in usable_letters])

        # (c) Ask letter_hints_from_type
        more_letters_tuple, case = letter_hints_from_type(math_type)
        # Merge letters lists:
        for more_letters in more_letters_tuple:
            letters.extend(more_letters)

        # (d) Exclude other hints
        excluded_letters = [hint.letter for hint in existing_hints]
        success = False
        for letter in letters:
            if letter not in excluded_letters:
                success = True
                break

        # (e) Find new letters from letters list
        if not success:
            letter = letters[0] if letters else ""
            letter = new_letter_from_bad(letter, existing_hints, case)

        new_hint = cls(math_type, preferred_letter, letter, case)
        existing_hints.append(new_hint)
        return new_hint

###############################
# Methods for providing names #
###############################
    def check_names(self, needed_length, given_names: set):
        """
        Check self has enough names for data.
        """
        available_length = len(set(self.names).difference(given_names))
        return available_length >= needed_length

    def update_names_list(self, length, friend_names, excluded_names):
        """
        Check if self.name_scheme is able to provide enough fresh names,
        namely a list of given length, disjoint from two  lists of already
        given names. If not, compute a new names list.
        """

        given_names = excluded_names.union(friend_names)
        if not self.check_names(length, given_names):
            self.names = potential_names(self.letter, length, friend_names,
                                         excluded_names, case=self.case)

    def provide_name(self, given_names) -> (str, bool):
        """
        Return first name in self.names which is not in given_names.
        Boolean indicate success (good naming).
        """
        for name in self.names:
            if name not in given_names:
                return name, True

        # Emergency name: we have no more good names for you...
        bad_names = list(alphabet + greek_alphabet)
        for name in bad_names:
            if name not in given_names:
                return name, False
