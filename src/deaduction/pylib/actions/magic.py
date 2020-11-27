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

from deaduction.config import user_config, _
from deaduction.pylib.actions.actiondef import action
from deaduction.config import _
from deaduction.pylib.actions import (format_orelse,
                                      WrongUserInput)
from deaduction.pylib.mathobj import MathObject

# turn logic_button_texts into a dictionary
lbt = user_config.get('magic_button_texts').split(', ')
magic_list = ['action_compute']
magic_button_texts = {}
for key, value in zip(magic_list, lbt):
    magic_button_texts[key] = value


@action(_("Computation"), _('Computation'))
def action_compute(goal, selected_objects):
    target = goal.target
    if not (target.is_equality()
            or target.is_inequality()
            or target.is_false()):
        raise WrongUserInput(error="Target is not an equality or an "
                                   "inequality")
    # try_before = "try {apply div_pos}, " \
    #            + "try { all_goals {norm_num at *}}" \
    #             + ", "
    #simplify_1 = "simp only " \
    #             + "[*, ne.symm, ne.def, not_false_iff, lt_of_le_of_ne]"
    #possible_code = [try_before + "linarith",
    #                 try_before + simplify_1]
    # "finish" "norm_num *"
    # if user_config.getboolean('use_library_search_for_computations'):
    #     possible_code.append('library_search')

    possible_code = ["try {norm_num at *}, compute_n 10"]

    return format_orelse(possible_code)
