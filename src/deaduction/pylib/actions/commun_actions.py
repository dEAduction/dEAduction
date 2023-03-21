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

from deaduction.pylib.actions.utils import pre_process_lean_code
from deaduction.pylib.actions import (InputType,
                                      MissingParametersError,
                                      WrongUserInput,
                                      action,
                                      CodeForLean)

from deaduction.pylib.give_name import get_new_hyp

from deaduction.pylib.math_display import new_objects, new_properties

log = logging.getLogger(__name__)
global _


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
        output = new_properties
        raise MissingParametersError(InputType.Text,
                                     title=_("Introduce a new subgoal"),
                                     output=output)
    elif len(user_input) == 2:
        sub_goal = pre_process_lean_code(user_input[1])

    # (C) Code:
    if sub_goal:
        new_hypo_name = get_new_hyp(proof_step)
        codes = CodeForLean.from_string(f"have {new_hypo_name}:"
                                        f" ({sub_goal})")
        codes.add_success_msg(_("New target will be added to the context "
                                "after being proved"))
        codes.add_subgoal(sub_goal)

    return codes

