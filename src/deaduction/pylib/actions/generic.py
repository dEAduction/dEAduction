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
    if len(selected_objects) == 0:
        defi = definition.lean_name
        possible_codes.append(f'rw {defi}')
        possible_codes.append(f'rw <- {defi}')
        possible_codes.append(f'simp_rw {defi}')
        possible_codes.append(f'simp_rw <- {defi}')
        
    elif len(selected_objects) == 1:
        defi = definition.lean_name
        h = selected_objects[0].info["name"]
        
        possible_codes.append(f'rw {defi} at {h}')
        possible_codes.append(f'rw <- {defi} at {h}')
        possible_codes.append(f'simp_rw {defi} at {h}')
        possible_codes.append(f'simp_rw <- {defi} at {h}')
        
    return format_orelse(possible_codes)

def action_theorem(goal : Goal, selected_objects : [MathObject], theorem : Statement):
    possible_codes = []
    th = theorem.lean_name
    if len(selected_objects) == 0:
        h = get_new_hyp(goal)
        possible_codes.append(f'apply {th}')
        possible_codes.append(f'have {h} := @{th}')
    else:
        arguments = " ".join([selected_objects[0].info["name"]])
        h = get_new_hyp(goal)
        possible_codes.append(f'apply {th} {arguments}')
        possible_codes.append(f'apply @{th} {arguments}')
        possible_codes.append(f'have {h} := {th} {arguments}')
        possible_codes.append(f'have {h} := @{th} {arguments}')
    
    return format_orelse(possible_codes)
