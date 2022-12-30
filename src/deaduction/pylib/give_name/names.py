"""
##################################################################
# names.py : provide name lists as potential names for variables #
##################################################################

This file provides utility functions for NameHint, which deal with strings.
The functions mainly provide lists of potential names for variables.

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
from deaduction.pylib.utils import inj_list

log = logging.getLogger(__name__)

# All Greek letters: "αβγδεζηθικλμνξοπρςστυφχψω" + "ΓΔΘΛΞΠΣΦΨΩ"
alphabet = 'abcdefghijklmnopqrstuvwxyz'
greek_alphabet = "αβγδεζηθικλμνξοπρςστυφχψω"
lower_lists = ['abcde', 'fgh', 'ijk', 'l', 'mn', 'nk', 'npq', 'pqr', 'rst',
               'uvw', 'xyzwt']
greek_list = ['αβγ', 'ε', 'δ', 'η', 'φψ', 'λμν', 'πρ', 'θα', 'στ']
greek_upper_list = ['ΓΛΔ', 'ΦΨ', 'Ξ', 'Σ', 'Ω']
upper_lists = ['ABCDE', 'FGH', 'IJ', 'KL', 'MK', 'N', 'PQR', 'RST',
               'UVW', 'XYZWT']
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


# def inj_list(list_: list):
#     """
#     Return a list with same elements of list_ but no repetition.
#     """
#     new_list = []
#     for item in list_:
#         if item not in new_list:
#             new_list.append(item)
#     return new_list


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
            index = None

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


def sort_lists_by_length(lists: [str]) -> [str]:
    """
    Return the list of strings in lists sorted by length.
    """
    # Change 20 if necessary...
    list_of_lists = [None]*26  # list_of_lists[l] = list of all str of length l
    for list_ in lists:
        index = len(list_)
        if list_of_lists[index] is not None:
            list_of_lists[index].append(list_)
        else:
            list_of_lists[index] = [list_]

    new_list = []
    for list_ in reversed(list_of_lists):
        if list_:
            new_list.extend(list_)

    return new_list


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

    direct_trials: [str] = []
    reverse_trials: [str] = []

    lists = (lower_lists + greek_list if case == Case.LOWER_ONLY
             else upper_lists + greek_upper_list if case == Case.UPPER_ONLY
             else upper_lists + greek_upper_list + lower_upper + lower_lists
             + greek_list if case == Case.UPPER_MOSTLY
             else lower_lists + greek_list + lower_upper + upper_lists
             + greek_upper_list)

    for s in lists:
        if letter in s:
            ind = s.find(letter)
            direct = s[ind:]
            reverse = s[:ind+1][::-1]
            if direct not in direct_trials:
                direct_trials.append(direct)
            if reverse not in reverse_trials:
                reverse_trials.append(reverse)

    direct_trials = sort_lists_by_length(direct_trials)
    reverse_trials = sort_lists_by_length(reverse_trials)

    index = '_' + str(index) if index is not None else ""
    letter_lists = []
    for string in direct_trials + reverse_trials:
        if len(string) >= min_length:
            list_ = [letter + ("'" * prime) + index for letter in string]
            letter_lists.append(list_)

    return letter_lists


def name_lists_from_name(hint: str,
                         min_length: int, max_length: int = 10,
                         case=None,
                         preferred_letter='',
                         exclude_primes=False,
                         exclude_indices=False) -> [str]:
    """
    Provide lists of proposed names of given length, ordered according to
    their proximity with hint.
    """
    hint, prime, index = analyse_hint(hint)

    if case:  # Turn hint into a string compatible with case preference
        hint = case.modify(hint, strongly=False)
    root = hint + "'"*prime

    # Get names lists:
    index_names: [str] = index_name_list(root,
                                         start=0 if index is None else index,
                                         length=max_length) \
        if not exclude_indices else []
    prime_names: [str] = prime_name_list(hint, prime, index, min_length) \
        if not exclude_primes else []

    letter_names: [[str]] = pure_letter_lists(hint, prime, index, min_length,
                                              case)

    # In general, we prefer pure letters rather than primes or indices,
    # except for some preferred_letter
    lonesome_letters = 'ε'
    if preferred_letter and preferred_letter in lonesome_letters:
        # Primes and index first
        if cvars.get('display.use_primes_over_indices') or prime:
            names = [prime_names] + [index_names] + letter_names
        else:
            names = [index_names] + [prime_names] + letter_names
    elif prime:  # Primes first
        names = [prime_names] + letter_names + [index_names]
    elif index:  # Index first
        names = [index_names] + letter_names + [prime_names]
    elif cvars.get('display.use_primes_over_indices'):
        names = letter_names + [prime_names, index_names]
    else:
        names = letter_names + [index_names, prime_names]

    return names


def are_friends(letter1, letter2):
    """
    True iff both letters belongs to a common list of letters. This is
    crucial to decide whether a NameHint may be used ti name some variable.
    """
    # Upper letter are not friend with lower letter (not symmetric):
    if letter2.isupper() and letter1.islower():
        return False

    name_lists = name_lists_from_name(letter1, min_length=2)
    tests = [letter2 in names for names in name_lists]
    return any(tests)


def potential_names(hint, length, friend_names: set, excluded_names: set,
                    case=None, preferred_letter='',
                    exclude_indices=False, exclude_primes=False) -> []:
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
                                 case=case,
                                 preferred_letter=preferred_letter,
                                 exclude_indices=exclude_indices,
                                 exclude_primes=exclude_primes)
    given_names = excluded_names.union(friend_names)

    # (2) Keep only sufficiently long lists, and if length==1 then put list
    # of length 1 at the end:
    long_lists = [names for names in lists
                  if len(set(names).difference(given_names)) >= max(length, 2)]
    if length == 1:
        long_lists += [names for names in lists
                       if len(set(names).difference(given_names)) == 1]

    # if length == 3:
    #     print("debug")

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

    # (4) Find all lists maximizing # of elements in friend_names
    score = -1
    winners = []
    for names in min_lists:
        common_nb = len(friend_names.intersection(set(names)))
        if common_nb > score:
            winners = [names]
            score = common_nb
        elif common_nb == score:
            winners.append(names)

    # (5) Keep one of the longest list (except if indices)
    if not exclude_indices:
        winner = winners[0] if winners else []
    else:
        score = -1
        winner = []
        for names in winners:
            if len(names) > score:
                winner = names
                score = len(names)

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

