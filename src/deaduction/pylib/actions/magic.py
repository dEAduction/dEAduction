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

from deaduction.pylib.config.i18n import _
from deaduction.pylib.text import tooltips

from deaduction.pylib.actions.actiondef import action
from deaduction.pylib.actions import (format_orelse,
                                      CodeForLean,
                                      solve1_wrap,
                                      WrongUserInput)
from deaduction.pylib.mathobj import (MathObject,
                                      Goal)


# Turn magic_button_texts into a dictionary
lbt = tooltips.get('magic_button_texts').split(', ')
magic_list = ['compute', 'assumption']
magic_button_texts = {}
for key, value in zip(magic_list, lbt):
    magic_button_texts[key] = value


@action(tooltips.get('tooltip_compute'),
        magic_button_texts['compute'])
def action_compute(goal, selected_objects):
    target = goal.target
    if not (target.is_equality()
            or target.is_inequality()
            or target.is_false()):
        error = _("target is not an equality, an inequality, "
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
    possible_code = [solve1_wrap("norm_num at *"),
                     solve1_wrap("try {norm_num at *}, compute_n 10")]

    return CodeForLean.or_else_from_list(possible_code)


@action(tooltips.get('tooltip_assumption'),
        magic_button_texts['assumption'])
def action_assumption(goal: Goal, l: [MathObject]) -> str:
    """
    Translate into string of lean code corresponding to the action

    :param goal: current goal
    :param l: list of MathObject arguments preselected by the user
    :return: string of lean code
    """
    # NB: this button should either solve the goal or fail.
    # For this we wrap the non "solve-or-fail" tactics
    # into the combinator "solve1"

    possible_codes = []
    if len(l) == 0:
        possible_codes.append('assumption')
        possible_codes.append('contradiction')
        if goal.target.is_equality() or goal.target.is_iff():
            if goal.target.math_type.children[0] == \
                    goal.target.math_type.children[1]:
                possible_codes.append('refl')
            # try to use associativity and commutativity
            possible_codes.append('ac_reflexivity')
            # try to permute members of the goal equality
            possible_codes.append('apply eq.symm, assumption')
            # congruence closure, solves e.g. (a=b, b=c : f a = f c)
            possible_codes.append('cc')
        # possible_codes.append('apply iff.symm, assumption')

        # Try some symmetry rules
        if goal.target.is_iff():
            possible_codes.append('apply iff.symm, assumption')
        elif goal.target.is_and():  # todo: change to "id_and_like"
            possible_codes.append('apply and.symm, assumption')
            possible_codes.append('split, assumption, assumption')
        elif goal.target.is_or():
            possible_codes.append('apply or.symm, assumption')
            # The following is too much?
            # possible_codes.append('left, assumption')
            # possible_codes.append('right, assumption')

        # Try to split hypotheses that are conjunctions
        code = ""
        counter = 0
        for prop in goal.context:
            if prop.is_and():
                name = prop.info['name']
                H0 = f"H_aux_{counter}"  # these hypotheses will disappear
                H1 = f"H_aux_{counter + 1}"  # so names are unimportant
                code += f"cases {name} with {H0} {H1}, "
                counter += 2
        if code:
            code += 'assumption'
            possible_codes.append(code)
        # Search for specific prop
        for prop in goal.context:
            math_type = prop.math_type
            # conclude from "x in emptyset"
            if (math_type.node == "PROP_BELONGS"
                    and math_type.children[1].node == "SET_EMPTY"):
                H2 = prop.info['name']
                if goal.target.node != "PROP_FALSE":
                    code = "exfalso, "
                else:
                    code = ""
                code += f"exact set.not_mem_empty _ {H2}"
                possible_codes.append(code)

    if len(l) == 1:
        possible_codes.append(solve1_wrap(f'apply {l[0].info["name"]}'))
    if (goal.target.is_equality()
            or goal.target.is_inequality()
            or goal.target.is_false()):
        # Do not remove above test, since norm_num may solve some
        # not-so-trivial goal, e.g. implications
        possible_codes.append(solve1_wrap('norm_num at *'))
    return CodeForLean.or_else_from_list(possible_codes)
