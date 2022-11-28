"""
##################################################################
# names.py : provide name lists as potential names for variables #
##################################################################

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

from enum import IntEnum
from typing import Tuple, Optional
import logging

import deaduction.pylib.config.vars as cvars

log = logging.getLogger(__name__)

# All Greek letters: "αβγδεζηθικλμνξοπρςστυφχψω" + "ΓΔΘΛΞΠΣΦΨΩ"
alphabet = 'abcdefghijklmnopqrstuvwxyz'
greek_alphabet = "αβγδεζηθικλμνξοπρςστυφχψω"
lower_lists = ['abcde', 'fgh', 'ijkl', 'mn', 'nk', 'npq', 'pqr', 'rst', 'uvw',
               'xyzwt']
greek_list = ['αβγ', 'ε', 'δ', 'η', 'φψ', 'λμν', 'πρ', 'θα', 'στ']
greek_upper_list = ['ΓΛΔ', 'ΦΨ', 'Ξ', 'Σ', 'Ω']
upper_lists = [s.upper() for s in lower_lists]
lower_upper = [a + a.upper() for a in alphabet]


class Case(IntEnum):
    LOWER_ONLY = 1
    LOWER_MOSTLY = 2
    UPPER_MOSTLY = 3
    UPPER_ONLY = 4

    def modify(self, s: str, strongly=True):
        """
        Turn the string s into lower or upper, so that it is compatible with
        self.
        """
        if not strongly:
            s_mod = (s if self in (2, 3)
                     else s.lower() if self == 1 else s.upper())
        else:
            s_mod = s.lower() if self in (1, 2) else s.upper()

        return s_mod


def analyse_hint(hint: str) -> (str, int, Optional[int]):
    """
    Analyse the hint structure in terms of number of primes and index.
    n''_0 --> ('n', 2, 0)
    n' --> ('n', 1, None)
    Ens_1 --> 'Ens', 1, None)
    """
    index = None
    if '_' in hint:
        hint, index = hint.split('_')
        try:
            index = int(index)
        except ValueError:
            pass

    prime = hint.count("'")
    if prime:
        hint = hint[:hint.find("'")]

    return hint, prime, index


def index_name_list(root: str, start: int, length: int) -> [str]:
    """
    Return a list of indexed names of given length.
    e.g.
    (n, 1, 3) --> n_1, n_2, n_3.
    (n', 0, 2) --> n'_0, n'_1, n'_2
    """
    return [root + '_' + str(i)
            for i in range(start, start + length)]


def prime_name_list(start_name: str, start: int, index: Optional[int],
                    min_length: int) -> [str]:
    """
    e.g.
    n, 1, None, 2 --> n', n'' (if seconds allowed)
    n, 0, 0, 2 --> n_0, n'_0, n''_0
    n, 1, None, 3 --> []
    """

    use_prime = cvars.get('display.allow_primes_for_names', True)
    if not use_prime:
        return []
    use_second = cvars.get('display.allow_seconds_for_names', True)
    end = 2 if use_second else 1
    if end - start + 1 < min_length:
        return []
    else:
        suffix = '_' + str(index) if index is not None else ''
        return [start_name + "'"*i + suffix for i in range(start, end+1)]


def pure_letter_lists(letter: str, prime=0, index: Optional[int] = None,
                      min_length=2, case=None) -> [[str]]:
    """
    Return lists of letters that contains letter.
    The priority is lower_lists first, direct order first,
    then reverse order.
    e.g.
    (t, 3) --> (t, s, r), (t, w, z, y, x)
    (k, 2) --> (k, l), (k, j, i), (k, n), (k, K).
    (x', 2) --> (x', y', z', w', t'), (x', X') ...
    """

    direct_trials = []
    reverse_trials = []

    lists = (lower_lists + greek_list if case == Case.LOWER_ONLY
             else upper_lists + greek_upper_list if case == Case.UPPER_ONLY
             else upper_lists + greek_upper_list + lower_lists + greek_list
             + lower_upper if case == Case.UPPER_MOSTLY
             else lower_lists + upper_lists + greek_list + greek_upper_list
             + lower_upper)

    for s in lists:
        if letter in s:
            ind = s.find(letter)
            direct_trials.append(s[ind:])
            reverse_trials.append(s[:ind+1][::-1])

    index = '_' + str(index) if index is not None else ""
    letter_lists = [[letter + ("'" * prime) + index for letter in li]
                    for li in direct_trials + reverse_trials
                    if len(li) >= min_length]

    return letter_lists


def name_lists_from_name(hint: str,
                         min_length: int, max_length: int,
                         case=None) -> [str]:
    """
    Provide lists of proposed names of given length, ordered according to
    their proximity with hint.
    """
    hint, prime, index = analyse_hint(hint)

    if case:  # Turn hint into a string compatible with case preference
        hint = case.modify(hint, strongly=False)
    root = hint + "'"*prime

    # Get names list:
    index_names = index_name_list(root,
                                  start=0 if index is None else index,
                                  length=max_length)
    prime_names = prime_name_list(hint, prime, index, min_length)

    letter_names = pure_letter_lists(hint, prime, index, min_length, case)

    # We prefer pure letters rather than primes or indices:
    if prime:
        names = [prime_names] + letter_names + [index_names]
    elif index:
        names = [index_names] + letter_names + [prime_names]
    elif cvars.get('display.use_primes_over_indices'):
        names = letter_names + [prime_names, index_names]
    else:
        names = letter_names + [index_names, prime_names]

    return names


def potential_names(hint, length, friend_names: set, excluded_names: set,
                    case=None):
    """
    Provides one list of potential names, of given length, for a given hint.
    The list friend_names contains the names already given to some
    variables for the same hint; the list must be as close as possible to
    friend_names but must not contain any names from it, nor from
    other_given_names. e.g.
    ('x', 2, ['x_0']) --> x_0, x_1, x_2
    ('x', 2,  ['x', 'y']) -> x, y, z, w

    The algorithm is to ask the previous methods for sufficiently long lists
    compatible with hint, and keep the one that contains the greatest nb of
    elements of given_names_for_hint, as far as it contains enough new names.

    NB: excluded_names is assumed to be disjoint from friend_names.
    length is the nb of needed additional (new) names.
    NB2: the index list should always be of sufficient length, i.e.
    length equal to length + len(friend_name) + 10.
    NB3: the returned list may include forbidden names. This is useful since
    context may vary, these forbidden names may disappear from the
    context, and then we will be happy to use them for a new variable.
    """

    # (1) Get all lists compatible with data
    lists = name_lists_from_name(hint, min_length=length,
                                 max_length=length + len(excluded_names) + 10,
                                 case=case)
    winner = None
    given_names = excluded_names.union(friend_names)

    # (2) Keep only sufficiently long lists:
    long_lists = [names for names in lists
                  if len(set(names).difference(given_names)) >= length]

    # (3) Extract lists minimizing # of elements in excluded_names
    score = 2000
    min_lists = []
    for names in long_lists:
        common_nb = len(excluded_names.intersection(set(names)))
        if common_nb < score:  # New minimum, clear all previous names
            min_lists = [names]
            score = common_nb  # New score!
        elif common_nb == score:  # New minimizer, add to list
            min_lists.append(names)

    # (4) Find a list maximizing # of elements in friend_names
    score = -1
    for names in min_lists:
        common_nb = len(friend_names.intersection(set(names)))
        if common_nb > score:
            winner = names
            score = common_nb

    return winner


if __name__ == "__main__":
    # print(analyse_hint("rot_10"))
    # print("*********")
    #
    # print(pure_letter_lists('n', 0, None, 3))
    # print(pure_letter_lists('n', 0, 0, 3))
    # print(pure_letter_lists('x', 1, 0, 3))
    # print(pure_letter_lists('y', 1, 0, 2))
    # print("*********")
    #
    # print(prime_name_list('x', 1, index=1, min_length=2))
    # print(prime_name_list('x', 1, index=1, min_length=3))
    #
    # print("*********")
    # print("x, 2 à 5:")
    # print(name_lists_from_name('x', 2, 5))
    # print("y, 2 à 5:")
    # print(name_lists_from_name('y', 2, 5))
    # print("z', 2 à 5:")
    # print(name_lists_from_name("z'", 2, 5))
    # print("p_0, 2 à 5:")
    # print(name_lists_from_name("p_0", 2, 5))
    # print("p'_0, 2 à 5:")
    # print(name_lists_from_name("p'_0", 2, 5))

    # print(potential_names('x', 3, [], []))
    # print(potential_names('x', 3, ["x'"], ['y']))
    # print(potential_names('x', 2, ["x'"], ['y']))
    print(potential_names("x''", 1, ["y"], ['z']))

