"""
 compute_utils.py : helper fcts for compute and assumption actions

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 10 2023 (creation)
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

import logging
from typing import Optional

from deaduction.pylib.mathobj import MathObject
from deaduction.pylib.actions import CodeForLean

log = logging.getLogger("magic")
global _


def pre_unify(H1: MathObject, H2: MathObject):
    """
    Return a list of couples of arithmetic expr so that H1 unifies to H2 up to
    equalities of each couple.
    e.g.
    (H: abs((x-l) + (y-l')) < 1)
    (H': abs ((x+y) -(l+l')) < 1)
    --> [((x-l) + (y-l'), (x+y) -(l+l'))]

    If pre-unification is impossible, return False.
    If equality holds, return True.
    """

    if H1 == H2:
        return True

    if H1.ring_expr() is not False and H2.ring_expr() is not False:
        return [(H1, H2)]

    if ((not H1.node == H2.node) or
            (not len(H1.children) == len(H2.children))):
        return False

    # Now same node
    if len(H1.children) == 0:
        return True

    # Now same nb of children, at least 1
    couples = []
    pertinent_children = list(zip(H1.children, H2.children))
    first_child1 = H1.children[0]
    # first_child2 = H2.children[0]
    # FIXME:
    #   Ugly trick !!
    if first_child1.display_name in ['abs']:
        pertinent_children = [pertinent_children[0], pertinent_children[-1]]
    elif first_child1.display_name in ['min', 'max']:
        pertinent_children = [pertinent_children[0]] + pertinent_children[-2:]

    for child1, child2 in pertinent_children:
        # if child1.is_ring_expr() and child2.is_ring_expr():
        #     couples.append((child1, child2))
        # elif
        child_unif = pre_unify(child1, child2)
        if child_unif is False:
            return False
        elif isinstance(child_unif, list):
            couples.extend(child_unif)
        # NB: if child_unif is True then there is nothing to do

    if couples:
        return couples
    else:
        # All child are equal: this should not happen.
        return True


def equal_by_ring(e1, e2, hyp_name) -> CodeForLean:
    """
    Try to get a new equality e1 = e2, and name it hyp_name.
    e1, e2 should be MathObject consisting solely of ring operations.
    """

    t1 = e1.to_display(format_="lean")
    t2 = e2.to_display(format_="lean")
    code_string = f"have {hyp_name}: {t1} = {t2}"
    code = CodeForLean(code_string).and_then("ring")
    return code


def list_equal_by_ring(couples) -> (CodeForLean, []):
    """
    Apply previous method to all couples.
    Return the LeanCode and the list of hypo names for the new props.
    """

    counter = 0
    ring_codes = []
    hyp_names = []
    for e1, e2 in couples:
        new_hyp = 'Haux' + str(counter)
        ring_codes.append(equal_by_ring(e1, e2, new_hyp))
        hyp_names.append(new_hyp)
        counter += 1

    code = CodeForLean.and_then_from_list(ring_codes)
    return code, hyp_names


def sort_by_length(names, couples):
    """
    Sort names by length of couple[0].
    """

    sorted_list = zip(names, couples).sort(key=lambda term:
                                            term[1][0].length())

    return [term[0] for term in sorted_list]


def rw_target(hyp_names) -> CodeForLean:
    """
    Successively try to rw target using hypos in list.
    """

    code = CodeForLean()
    for name in hyp_names:
        more_code = CodeForLean(f'rw {name}').or_else(f'simp_rw {name}')
        code = code.and_then(more_code)

    return code


def unify_by_ring(H, target) -> Optional[CodeForLean]:
    """
    If H and target are equal up to sub ring expr, try to prove target by
    unifying all those and substitute in H.

    H and target should be the MathObject containing the sub expr (not terms
     of such).
    """

    ring_couples = pre_unify(target, H)

    if not isinstance(ring_couples, list):
        return

    ring_code, hyp_names = list_equal_by_ring(ring_couples)
    # TODO: sort by decreasing length
    # hyp_names = sort_by_length(hyp_names, ring_couples)

    rw_code = rw_target(hyp_names)

    code = (ring_code.and_then(rw_code)).and_then('assumption')

    return code






