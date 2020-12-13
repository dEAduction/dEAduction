"""
# generic.py : # Contain actions the graphic interface has to call #
# when the user selects a definition or a theorem                  #
    
    (#optionalLongDescription)

Author(s)     : Marguerite Bin bin.marguerite@gmail.com
Maintainer(s) : Marguerite Bin bin.marguerite@gmail.com
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

from dataclasses import dataclass
import logging
from deaduction.pylib.actions import (  WrongUserInput,
                                        format_orelse)
from deaduction.pylib.coursedata import Statement
from deaduction.pylib.mathobj import (  Goal,
                                        MathObject,
                                        get_new_hyp)


def action_definition(goal : Goal, selected_objects : [MathObject], definition : Statement):
    possible_codes = []
    defi = definition.lean_name
    if len(selected_objects) == 0:
        possible_codes.append(f'rw {defi}')
        possible_codes.append(f'rw <- {defi}')
        possible_codes.append(f'simp_rw {defi}')
        possible_codes.append(f'simp_rw <- {defi}')
        
    else:
        names = [item.info['name'] for item in selected_objects]
        arguments = ' '.join(names)
        possible_codes.append(f'rw {defi} at {arguments}')
        possible_codes.append(f'rw <- {defi} at {arguments}')
        possible_codes.append(f'simp_rw {defi} at {arguments}')
        possible_codes.append(f'simp_rw <- {defi} at {arguments}')
        
    return format_orelse(possible_codes)


def action_theorem(goal : Goal, selected_objects : [MathObject], theorem : Statement):
    possible_codes = []
    h = get_new_hyp(goal)
    th = theorem.lean_name
    if len(selected_objects) == 0:
        possible_codes.append(f'apply {th}')
        possible_codes.append(f'have {h} := @{th}')
    else:
        command = f'have {h} := {th}'
        command_implicit = f'have {h} := @{th}'
        names = [item.info['name'] for item in selected_objects]
        arguments = ' '.join(names)
        # up to 4 implicit arguments
        possible_codes.append(f'apply {th} {arguments}')
        possible_codes.append(f'apply @{th} {arguments}')
        more_codes = [command + arguments,
                      command_implicit + arguments,
                      command + ' _ ' + arguments,
                      command_implicit + ' _ ' + arguments,
                      command + ' _ _ ' + arguments,
                      command_implicit + ' _ _ ' + arguments,
                      command + ' _ _ _ ' + arguments,
                      command_implicit + ' _ _ _ ' + arguments,
                      command + ' _ _ _ _ ' + arguments,
                      command_implicit + ' _ _ _ _ ' + arguments
                      ]
        possible_codes.extend(more_codes)

    return format_orelse(possible_codes)
