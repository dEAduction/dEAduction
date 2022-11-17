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
from dataclasses import dataclass
from typing import List, Any

from deaduction.pylib.give_name.names import (alphabet,
                                              greek_alphabet,
                                              pure_letter_lists,)


class NameHint:
    # instances = []  # type: List[NameHint]

    def __init__(self, letter, math_type):
        self.letter = letter
        self.math_type = math_type
        self.name_scheme = NameScheme.from_name_hint(self)
        # NameHint.instances.append(self)

    def __str(self):
        return self.letter

    @classmethod
    def from_math_type(cls, math_type, existing_hints):
        """
        Return the hint corresponding to math_type. If none, create a new
        hint and append it to existing_hints.
        """
        # (1) Search for math_type among existing hints
        for hint in existing_hints:
            if hint.math_type == math_type:
                return hint

        # (2) No existing hint: create one
        letter = math_type.name_hint_from_type()
        letters = [hint.letter for hint in existing_hints]
        if letter in letters:  # Search an acceptable letter
            letter = cls.new_letter_from_bad(letter, existing_hints)
        new_hint =  cls(letter, math_type)
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

        # (1) Find conflicting hint
        conflicting_hint = None
        for hint in existing_hints:
            if letter == hint.letter:
                conflicting_hint = hint
                break

        # (2) Find first available letter
        available_letter = ""
        letters = [hint.letter for hint in existing_hints]
        good_names = conflicting_hint.name_scheme.names()
        # e.g. [['f', 'g', 'h'],['f', 'F']]
        bad_names = list(alphabet + greek_alphabet)
        for names in sum(good_names, []) + bad_names:
            for letter in names:
                if letter not in letters:
                    available_letter = letter
                    break
            if available_letter:
                break
        if not available_letter:
            logging.warning("NO MORE LETTER AVAILABLE for naming!!")

        return available_letter

    # @classmethod
    # def clear(cls, types=None):
    #     if not types:
    #         types = []
    #     for self.math_type in cls.instances:
    #         if self not in types:
    #             cls.instances.remove(self)


@dataclass()
class NameScheme:
    base_hint: NameHint
    mode = 'letter'

    @classmethod
    def from_name_hint(cls, name_hint: NameHint):
        return cls(base_hint=name_hint)

    def names(self):
        letter = self.base_hint.letter
        return pure_letter_lists(letter)

    def first_available_name(self, given_names):
        for name in self.names():
            if name not in given_names:
                return name


