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
                                        CodeForLean)
from deaduction.pylib.coursedata import Statement
from deaduction.pylib.mathobj import (  Goal,
                                        MathObject,
                                        get_new_hyp)


def rw_using_statement(goal: Goal, selected_objects: [MathObject],
                      statement: Statement):
    """
    Return codes trying to use statement for rewriting. This should be
    reserved to iff or equalities. This function is called by
    action_definition, and by action_theorem in case the theorem is an iff
    statement.
    """
    possible_codes = []
    defi = statement.lean_name
    if len(selected_objects) == 0:
        possible_codes.append(f'rw {defi}')
        possible_codes.append(f'simp_rw {defi}')
        possible_codes.append(f'rw <- {defi}')
        possible_codes.append(f'simp_rw <- {defi}')

    else:
        names = [item.info['name'] for item in selected_objects]
        arguments = ' '.join(names)
        possible_codes.append(f'rw {defi} at {arguments}')
        possible_codes.append(f'simp_rw {defi} at {arguments}')
        possible_codes.append(f'rw <- {defi} at {arguments}')
        possible_codes.append(f'simp_rw <- {defi} at {arguments}')

    return possible_codes


def action_definition(goal : Goal,
                      selected_objects : [MathObject],
                      definition : Statement):
    possible_codes = rw_using_statement(goal, selected_objects, definition)
    return CodeForLean.or_else_from_list(possible_codes)


def action_theorem(goal : Goal, selected_objects : [MathObject], theorem : Statement):
    possible_codes = []
    # For an iff statement, use rewriting
    # fixme: test for iff or equality is removed since it works only with
    #  pkl files
    proof_state = theorem.initial_proof_state
    # if proof_state and ( proof_state.goals[0].target.is_iff()
    #                      or proof_state.goals[0].target.is_equality() ):
    possible_codes = rw_using_statement(goal,
                                        selected_objects,
                                        theorem)
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

    return CodeForLean.or_else_from_list(possible_codes)
