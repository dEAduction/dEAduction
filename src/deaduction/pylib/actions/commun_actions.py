"""
#########################################################
# commun_actions.py : lean code used in several actions #
#########################################################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 12 2022 (creation)
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
from typing import Optional

from deaduction.pylib.actions.utils import pre_process_lean_code
from deaduction.pylib.actions import (InputType,
                                      MissingParametersError,
                                      CodeForLean)

from deaduction.pylib.give_name import get_new_hyp

from deaduction.pylib.mathobj import MathObject
from deaduction.pylib.math_display import new_properties

log = logging.getLogger(__name__)
global _


# TODO: move all these functions to CodeForLean class methods

def introduce_new_subgoal(proof_step, premise=None) -> CodeForLean:
    # selected_objects = proof_step.selection
    user_input = proof_step.user_input
    sub_goal = None
    codes = CodeForLean()

    # (A) Sub-goal from selection
    # if selected_objects:
    #     premise = selected_objects[0].premise()
    if premise:
        sub_goal = premise.to_display(format_='lean')

    # (B) User enter sub-goal
    elif len(user_input) == 1:
        # output = new_properties
        # raise MissingParametersError(InputType.Text,
        #                              title=_("Introduce a new subgoal"),
        #                              output=output)
        raise MissingParametersError(InputType.Calculator,
                                     title=_("Introduce a new subgoal"),
                                     target=MathObject.PROP)  # FIXME
        # raise MissingParametersError(InputType.Text,
        #                                  title=_("Introduce a new object"),
        #                                  output=output)
        # else:  # Send code
        #     name = pre_process_lean_code(user_input[1])
        #     new_hypo_name = get_new_hyp(proof_step, name='Def')
        #     new_object = user_input[2].to_display(format_='lean')
    elif len(user_input) == 2:
        sub_goal = user_input[1]
        if isinstance(sub_goal, MathObject):
            sub_goal = sub_goal.to_display(format_='lean')

    # (C) Code:
    if sub_goal:
        new_hypo_name = get_new_hyp(proof_step)
        codes = CodeForLean.from_string(f"have {new_hypo_name}:"
                                        f" ({sub_goal})")
        codes.add_success_msg(_("New target will be added to the context "
                                "after being proved"))
        codes.add_subgoal(sub_goal)

    return codes


def rw_with_defi(definition, object_=None) -> CodeForLean:
    defi = definition.lean_name
    if object_:
        name = object_.info['name']
        code = CodeForLean.from_string(f"rw {defi} at {name}")
    else:
        code = CodeForLean.from_string(f"rw {defi}")
    return code


# TODO: move to MathObject
def inequality_from_pattern_matching(math_object: MathObject,
                                     variable: MathObject) -> Optional[MathObject]:
    """
    Check if math_object.math_type has the form
    ∀ x:X, (x R ... ==> ...)
    where R is some inequality relation, and if this statement may be
    applied to variable. If so, return inequality with x replaced by variable
    """
    inequality = None
    if not math_object.is_for_all(implicit=True):
        return None

    if not math_object.is_for_all(is_math_type=False):
        # Implicit "for all"
        math_object = MathObject.last_rw_object
    else:
        math_object = math_object.math_type

    math_type, var, body = math_object.children
    # NB: following line does not work because of coercions
    # if var.math_type == variable.math_type:
    if body.is_implication(is_math_type=True):
        premise = body.children[0]  # children (2,0)
        if (premise.is_inequality(is_math_type=True) and
                var == premise.children[0]):
            children = [variable, premise.children[1]]
            inequality = MathObject(node=premise.node,
                                    info={},
                                    children=children,
                                    math_type=premise.math_type)
    return inequality


def have_new_property(arrow: MathObject,
                      variable_names: [str],
                      new_hypo_name: str,
                      success_msg=None,
                      iff_direction='') -> CodeForLean:
    """
    Compute Lean code to apply an implication or a universal property to a
    property or a variable.

    :param arrow:           a MathObject which is either an implication or a
                            universal property
    :param variable_names:  a list of names of variables (or properties) to
                            which "arrow" will be applied
    :param new_hypo_name:   a fresh name for the new property

    :param success_msg:     A success msg, if None then the standard one will be
                            used.

    :param iff_direction:   = 'mp' if arrow is an iff that we want to use as an
                            implication, 'mpr' for reverse direction,
                            '' if arrow is an implication.
    return:                 Lean Code to produce the wanted new property,
                            taking into account implicit parameters
    """

    # TODO: add smart guess for placeholders, by matching math types
    #  May even try to guess parameters from the context
    #  (e.g. if we need a function and there is only one in the context)

    # try with up to 4 implicit parameters
    # implicit_codes = [command + ' ' + arguments,
    #                   command + ' _ ' + arguments,
    #                   command + ' _ _ ' + arguments,
    #                   command + ' _ _ _ ' + arguments,
    #                   command + ' _ _ _ _ ' + arguments]
    #
    # explicit_codes = [command_explicit + ' ' + arguments,
    #                   command_explicit + ' _ ' + arguments,
    #                   command_explicit + ' _ _ ' + arguments,
    #                   command_explicit + ' _ _ _ ' + arguments,
    #                   command_explicit + ' _ _ _ _ ' + arguments]

    # Try several codes, e.g. "have H10 := (@H1 _ _ ).mp H2"
    # (new_hypo_name = "H10", arrow = "H1", arguments = ["H2"], iff_direction
    # = "mp")
    selected_hypo = arrow.info["name"]
    have = f'have {new_hypo_name} := '
    arguments = ' '.join(variable_names)
    implicit_codes = []
    explicit_codes = []
    for nb in range(6):
        imp_code = f'{selected_hypo} ' + '_ '*nb
        exp_code = f'@{selected_hypo} ' + '_ '*nb
        if iff_direction:
            if nb > 0:
                imp_code = '(' + imp_code + ')'
                exp_code = '(' + exp_code + ')'
            imp_code = imp_code + '.' + iff_direction + ' '
            exp_code = exp_code + '.' + iff_direction + ' '
        implicit_codes.append(have + imp_code + arguments)
        explicit_codes.append(have + exp_code + arguments)

    code = CodeForLean.or_else_from_list(implicit_codes + explicit_codes)
    if success_msg is None:
        success_msg = _("Property {} added to the context").format(new_hypo_name)
    if success_msg:
        code.add_success_msg(success_msg)

    code.operator = arrow
    return code
