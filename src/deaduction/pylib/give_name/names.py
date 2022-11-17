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

from typing import Tuple, Optional
import logging

import deaduction.pylib.config.vars as cvars

log = logging.getLogger(__name__)

# "αβγδεζηθικλμνξοπρςστυφχψω" + "ΓΔΘΛΞΠΣΦΨΩ"
alphabet = 'abcdefghijklmnopqrstuvwxyz'
greek_alphabet = "αβγδεζηθικλμνξοπρςστυφχψω"
lower_lists = ['abcde', 'fgh', 'ijkl', 'mn', 'nk', 'npq', 'pqr', 'rst', 'uvw',
               'xyzwt']
greek_list = ['αβγ', 'δεη', 'φψ', 'λμν', 'πρ', 'θα', 'στ', 'ΓΛΔ']
upper_lists = [s.upper() for s in lower_lists]
lower_upper = [a + a.upper() for a in alphabet]

# TODO: handle cases of hint with index or prime.


def analyse_hint(hint: str) -> (str, int, Optional[int]):
    """
    n''_0 --> ('n', 2, 0)
    n' --> ('n', 1, None)
    """
    index = None
    if '_' in hint:
        hint, index = hint.split('_')
        index = int(index)

    prime = hint.count("'")
    if prime:
        hint = hint[:hint.find("'")]

    return hint, prime, index


def index_name_list(root: str, start: int, max_length: int) -> [str]:
    """
    e.g.
    (n, 1, 3) --> n_1, n_2, n_3.
    (n', 0, 2) --> n'_0, n'_1, n'_2
    """
    return [root + '_' + str(i)
            for i in range(start, start+max_length)]


def prime_name_list(start_name: str, start: int, index: Optional[int],
                    min_length: int) -> [str]:
    """
    e.g.
    n, 1, None, 2 --> n', n'' (if seconds allowed)
    n, 0, 0, 2 --> n_0, n'_0, n''_0
    n, 1, None, 3 --> []
    """

    use_prime = cvars.get('display.allow_primes_for_names')
    if not use_prime:
        return []
    use_second = cvars.get('display.allow_seconds_for_names')
    end = 2 if use_second else 1
    if end - start + 1 < min_length:
        return []
    else:
        suffix = '_' + str(index) if index is not None else ''
        return [start_name + "'"*i + suffix for i in range(start, end+1)]


def pure_letter_lists(letter: str, prime=0, index: Optional[int] = None,
                      min_length=2) -> [Tuple[str]]:
    """
    Return lists of letters that belongs to a common string in name_lists or
    lower_upper. The priority is lower_lists first, direct order first,
    then reverse order.
    e.g.
    (t, 3) --> (t, s, r), (t, w, z)
    (k, 2) --> (k, l), (k, j), (k, n), (k, K).
    (x', 2) --> (x', y') ...
    """

    direct_trials = []
    reverse_trials = []
    for s in lower_lists + upper_lists + greek_list + lower_upper:
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
                         min_length: int, max_length: int) -> [str]:
    """
    Provide lists of proposed names of given length, ordered according to
    their proximity with hint.
    """
    hint, prime, index = analyse_hint(hint)
    root = hint + "'"*prime
    index_names = index_name_list(root,
                                  start=0 if index is None else index,
                                  max_length=max_length)
    prime_names = prime_name_list(hint, prime, index, min_length)

    letter_names = pure_letter_lists(hint, prime, index, min_length)

    # We prefer prime rather than indices, and use both only if necessary:
    if prime:
        names = [prime_names] + letter_names + [index_names]
    elif index:
        names = [index_names] + letter_names + [prime_names]
    else:
        names = letter_names + [prime_names, index_names]

    return names


def potential_names(hint, length, friend_names, excluded_names):
    """
    Provides one list of potential names, of given length, for a given hint.
    The list friend_names contains the names already given to some
    variables for the same hint; the list must be as close as possible to
    given_names but must not contain any names from it, nor from
    other_given_names. e.g.
    ('x', 2, ['x_0']) --> x_1, x_2
    ('x', 2,  ('x', 'y') -> z, w

    The algorithm is to ask the previous methods for sufficiently long lists
    compatible with hint, and keep the one that contains the greatest nb of
    elements of given_names_for_hint, as far as it contains enough new names.

    NB: other_given_names is assumed to be disjoint from friend_names.
    """

    lists = name_lists_from_name(hint, min_length=length,
                                 max_length=length + len(excluded_names))
    score = -1
    winner = None
    for names in lists:
        names = [name for name in names if name not in excluded_names]
        print(names)
        if len(names) >= length:
            # Compute nb of friend_names in names
            new_score = [friend in names for friend in friend_names].count(True)
            print("score:" + str(new_score))
            if len(names) >= length + new_score \
                    and new_score > score:
                winner = names
                score = new_score

    print("Winner:")
    print(winner)
    winner = [name for name in winner if name not in friend_names]
    return winner[:length]


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

