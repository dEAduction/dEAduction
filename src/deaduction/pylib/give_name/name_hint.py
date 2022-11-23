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


# Letters lists,
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
    type.
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

    if math_type.is_nat(is_math_type=True):
        more_letters = ('npqk', )
        case = Case.LOWER_MOSTLY
    elif math_type.is_R():
        more_letters = ('xyztw', 'δεη')
        case = Case.LOWER_MOSTLY

    letters += more_letters

    return letters, case


class NameHint:
    """
    A class to provide names for all vars of a given type.
    """
    letter: str = 'x'  # Default letter
    case: Case = Case.LOWER_MOSTLY
    use_index = cvars.get('display.use_indices', True)
    prime_over_index = cvars.get('display.use_primes_over_indices', True)

    def __init__(self, letter, math_type, case, names=None):
        self.letter = letter
        self.math_type = math_type
        self.case = case
        # self.name_scheme = NameScheme.from_name_hint(self)
        #  and self.provide_name(given_names)
        self.names = names if names else []

        if math_type.is_sequence(is_math_type=True):
            self.use_index = False

    def __str__(self):
        return self.letter

    @classmethod
    def from_math_type(cls, math_type, existing_hints, friendly_names=None):
        """
        Return the hint corresponding to math_type. If none, create a new
        hint and append it to existing_hints. The main task is to find a
        suitable letter for naming hint. The letter must be distinct of all
        letters of existing_hints.
        """

        if not friendly_names:
            friendly_names = []

        # (1) Search for math_type among existing hints
        for hint in existing_hints:
            if hint.math_type == math_type:
                return hint

        # (2) No existing hint: create one
        # (a) Try (first letter of) friendly names
        letters = [friendly_name[0] for friendly_name in friendly_names
                   if friendly_name[0].isalpha()]

        # (b) Ask letter_hints_from_type
        more_letters_tuple, case = letter_hints_from_type(math_type)
        # Merge letters lists:
        for more_letters in more_letters_tuple:
            letters.extend(more_letters)

        # (c) Exclude other hints
        excluded_letters = [hint.letter for hint in existing_hints]
        success = False
        for letter in letters:
            if letter not in excluded_letters:
                success = True
                break

        if not success:
            letter = letters[0] if letters else ""
            letter = cls.new_letter_from_bad(letter, existing_hints)

        new_hint = cls(letter, math_type, case)
        existing_hints.append(new_hint)
        return new_hint

    @classmethod
    def new_letter_from_bad(cls, letter: str, existing_hints) -> str:
        """
        Construct a new NameHint from given letter, assumed to be equal to an
        existing NameHint. The algorithm is to take as name hint the first
        available letter in the NameScheme associated to the conflicting
        NameHint. If no letter is available, choose any(?).
        """
        # TODO: check case

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
            good_names = sum(pure_letter_lists(letter), []) if letter else []
        # e.g. [['f', 'g', 'h'],['f', 'F']]
        bad_names = list(alphabet + greek_alphabet)
        for names in good_names + bad_names:
            for letter in names:
                if letter not in unavailable_letters:
                    available_letter = letter
                    break
            if available_letter:
                break
        if not available_letter:
            logging.warning("NO MORE LETTER AVAILABLE for naming!!")

        return available_letter

    def check_names(self, needed_length, given_names: set):
        """
        Check self has enough names for data.
        """
        available_length = len(set(self.names).difference(given_names))
        return available_length >= needed_length

    def update_name_scheme(self, length, friend_names, excluded_names):
        """
        Check if self.name_scheme is able to provide enough fresh names,
        namely a list of given length, disjoint from two  lists of already
        given names. If not, compute a new NameScheme.
        """
        # FIXME: check case
        given_names = excluded_names.union(friend_names)
        if not self.check_names(length, given_names):
            self.names = potential_names(self.letter, length, friend_names,
                                         excluded_names, case=self.case)

    def provide_name(self, given_names):
        """
        Return first name in self.names which is not in given_names.
        """
        for name in self.names:
            if name not in given_names:
                return name
        # Emergency name: this should never happen!
        bad_names = list(alphabet + greek_alphabet)
        for name in bad_names:
            if name not in given_names:
                return name


# @dataclass()
# class NameScheme:
#     base_hint: NameHint
#     mode = 'letter'
# 
#     @classmethod
#     def from_name_hint(cls, name_hint: NameHint):
#         return cls(base_hint=name_hint)
# 
#     def names(self):
#         letter = self.base_hint.letter
#         return pure_letter_lists(letter)
# 
#     def first_available_name(self, given_names):
#         for name in self.names():
#             if name not in given_names:
#                 return name


