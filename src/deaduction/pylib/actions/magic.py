"""
# magic.py : #ShortDescription #
    
    (#optionalLongDescription)

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

import logging

import deaduction.pylib.logger as logger

# from deaduction.pylib.config.i18n import _
from deaduction.pylib.text import tooltips

from deaduction.pylib.actions.actiondef import action
from deaduction.pylib.actions import (CodeForLean,
                                      WrongUserInput,
                                      test_selection)
from deaduction.pylib.mathobj import (MathObject,
                                      Goal)


# log = logging.getLogger("magic")
#
# # Turn magic_button_texts into a dictionary
# lbt = tooltips.get('magic_button_texts').split(', ')
# magic_list = ['compute', 'assumption']
# magic_button_texts = {}
# for key, value in zip(magic_list, lbt):
#     magic_button_texts[key] = value


@action()
def action_compute(proof_step,
                   selected_objects,
                   target_selected: bool = True):
    """
    If the target is an equality, an inequality (or 'False'), then send
    tactics trying to prove the goal by (mainly linearly) computing.
    """

    goal = proof_step.goal

    target = goal.target
    if not (target.is_equality()
            or target.is_inequality()
            or target.is_false()):
        error = _("Target is not an equality, an inequality, "
                  "nor a contradiction")
        raise WrongUserInput(error)
    # try_before = "try {apply div_pos}, " \
    #            + "try { all_goals {norm_num at *}}" \
    #             + ", "
    # simplify_1 = "simp only " \
    #             + "[*, ne.symm, ne.def, not_false_iff, lt_of_le_of_ne]"
    # possible_code = [try_before + "linarith",
    #                 try_before + simplify_1]
    # "finish" "norm_num *"
    # if user_config.getboolean('use_library_search_for_computations'):
    #     possible_code.append('library_search')
    code1 = CodeForLean.from_string("norm_num at *").solve1()
    code2 = CodeForLean.from_string("compute_n 10")
    code3 = CodeForLean.from_string("norm_num at *").try_().and_then(code2)
    possible_code = code1.or_else(code3)
    #possible_code = [solve1_wrap("norm_num at *"),
    #                 solve1_wrap("try {norm_num at *}, compute_n 10")]
    return possible_code


def solve_equality(prop: MathObject) -> CodeForLean:
    """
    Assuming prop is an equality or an iff, return a list of tactics trying to 
    solve prop as a target.
    """

    code = CodeForLean.empty_code()

    if prop.math_type.children[0] == prop.math_type.children[1]:
        code = code.or_else('refl')
    # try to use associativity and commutativity
    code = code.or_else('ac_reflexivity')
    # try to permute members of the goal equality
    code = code.or_else('apply eq.symm, assumption')
    # congruence closure, solves e.g. (a=b, b=c : f a = f c)
    code = code.or_else('cc')
    return code


def solve_target(prop):
    """
    Try to solve 'prop' as a target, without splitting conjunctions.    
    """
    
    code = CodeForLean.empty_code()
    # if len(l) == 0:
    code = code.or_else('assumption')
    code = code.or_else('contradiction')

    # (1) Equality, inequality, iff
    if prop.is_equality() or prop.is_iff():
        code = code.or_else(solve_equality(prop))
    elif prop.is_inequality():
        # try to permute members of the goal equality
        code = code.or_else('apply ne.symm, assumption')

    # (2) Try some symmetry rules
    if prop.is_iff():
        code = code.or_else('apply iff.symm, assumption')
    elif prop.is_and():  # todo: change to "id_and_like"
        code = code.or_else('apply and.symm, assumption')
    # The following will be tried only after context splitting:
    #     code = code.or_else('split, assumption, assumption')
    elif prop.is_or():
        code = code.or_else('apply or.symm, assumption')
        # The following is too much?
        code = code.or_else('left, assumption')
        code = code.or_else('right, assumption')

    return code


def search_specific_prop(proof_step):
    """Search context for some specific properties to conclude the proof."""

    goal = proof_step.goal

    more_code = CodeForLean.empty_code()
    for prop in goal.context:
        math_type = prop.math_type
        # Conclude from "x in empty set"
        if (math_type.node == "PROP_BELONGS"
                and math_type.children[1].node == "SET_EMPTY"):
            hypo = prop.info['name']
            if goal.target.node != "PROP_FALSE":
                more_code = CodeForLean.from_string("exfalso")
            else:
                more_code = CodeForLean.empty_code()
            more_code = more_code.and_then(f"exact set.not_mem_empty _ {hypo}")

    return more_code


def split_conjunctions_in_context(proof_step):

    goal = proof_step.goal

    code = CodeForLean.empty_code()
    counter = 0
    for prop in goal.context:
        if prop.is_and():
            name = prop.info['name']
            h0 = f"H_aux_{counter}"  # these hypotheses will disappear
            h1 = f"H_aux_{counter + 1}"  # so names are unimportant
            code = code.and_then(f"cases {name} with {h0} {h1}")
            counter += 2
    return code


@action()
def action_assumption(proof_step,
                      selected_objects: [MathObject],
                      target_selected: bool = True) -> CodeForLean:
    """
    Translate into string of lean code corresponding to the action.
    """

    goal = proof_step.goal

    # (1) First trials
    target = goal.target
    improved_assumption = solve_target(target)
    codes = [improved_assumption]

    # (2) Use user selection
    if len(selected_objects) == 1:
        apply_user = CodeForLean.from_string(
                                f'apply {selected_objects[0].info["name"]}')
        codes.append(apply_user.solve1())

    # (3) Conjunctions: try to split hypotheses once
    # TODO: recursive splitting in hypo
    # And then retry many things (in improved_assumption_2).
    split_conj = split_conjunctions_in_context(proof_step)

    improved_assumption_2 = solve_target(target)
    # Split target
    if target.is_and():
        # TODO: recursive splitting in target, and_then for each subgoal
        #  apply improved_assumption
        split_code = CodeForLean.from_string('split, assumption, assumption')
        improved_assumption_2 = improved_assumption_2.or_else(split_code)

    # Try norm_num
    if (goal.target.is_equality()
            or goal.target.is_inequality()
            or goal.target.is_false()):
        # Do not remove above test, since norm_num may solve some
        # not-so-trivial goal, e.g. implications
        norm_num_code = CodeForLean.from_string('norm_num at *').solve1()
        improved_assumption_2 = improved_assumption_2.or_else(norm_num_code)

    # Try specific properties
    more_assumptions = search_specific_prop(proof_step)
    if not more_assumptions.is_empty():
        improved_assumption_2 = improved_assumption_2.or_else(more_assumptions)
    more_code = split_conj.and_then(improved_assumption_2)
    codes.append(more_code)
    code = CodeForLean.or_else_from_list(codes)
    code = code.solve1()
    code.add_error_msg(_("I don't know how to conclude"))
    return code
