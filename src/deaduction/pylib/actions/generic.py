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

from deaduction.pylib.actions import CodeForLean
from deaduction.pylib.mathobj import (MathObject,
                                      get_new_hyp)

from deaduction.pylib.proof_state import Goal

global _


def rw_using_statement(goal: Goal, selected_objects: [MathObject],
                       statement) -> CodeForLean:
    """
    Return codes trying to use statement for rewriting. This should be
    reserved to iff or equalities. This function is called by
    action_definition, and by action_theorem in case the theorem is an iff
    statement.
    """
    codes = CodeForLean.empty_code()
    defi = statement.lean_name
    # statement_type = statement.type.capitalize()
    if statement.is_definition():
        target_msg = _('Definition applied to target')
        context_msg = _('Definition applied to')
    elif statement.is_theorem():
        target_msg = _('Theorem applied to target')
        context_msg = _('Theorem applied to')
    else:
        target_msg = _('Exercise applied to target')
        context_msg = _('Exercise applied to')

    if len(selected_objects) == 0:
        codes = codes.or_else(f'rw {defi}')
        codes = codes.or_else(f'simp_rw {defi}')
        codes = codes.or_else(f'rw <- {defi}')
        codes = codes.or_else(f'simp_rw <- {defi}')
        codes.add_success_msg(target_msg)

    else:
        names = [item.info['name'] for item in selected_objects]
        arguments = ' '.join(names)

        context_msg += ' ' + arguments
        codes = codes.or_else(f'rw {defi} at {arguments}')
        codes = codes.or_else(f'simp_rw {defi} at {arguments}')
        codes = codes.or_else(f'rw <- {defi} at {arguments}')
        codes = codes.or_else(f'simp_rw <- {defi} at {arguments}')
        codes.add_success_msg(context_msg)

    codes.rw_item = statement # (statement.type_, statement.pretty_name)
    return codes


def add_statement_to_context(proof_step, statement) -> CodeForLean:
    # TODO: store statement name in the ContextMO as a synthetic name
    h = get_new_hyp(proof_step)
    name = statement.lean_name

    if statement.is_definition():
        success_msg = _('Definition added to the context')
    elif statement.is_theorem():
        success_msg = _('Theorem added to the context')
    else:
        success_msg = _('Exercise added to the context')

    code = CodeForLean(f'have {h} := @{name}', success_msg=success_msg)
    return code


def action_definition(proof_step) -> CodeForLean:
    """
    Apply definition to rewrite selected object or target.
    If nothing is selected, add definition to the context.
    """
    target_selected = proof_step.target_selected
    definition = proof_step.statement
    selected_objects = proof_step.selection
    # test_selection(selected_objects, target_selected)
    if not target_selected and not selected_objects:
        codes = add_statement_to_context(proof_step, definition)
        return codes

    else:
        codes = rw_using_statement(proof_step.goal, selected_objects,
                                   definition)
        codes.add_error_msg(_("Unable to apply definition"))
    return codes


def action_theorem(proof_step) -> CodeForLean:
    """
    Apply theorem on selected objects.
    - If nothing is selected, add theorem to the context.
    - If target is selected, try to apply theorem, with selected objects if
    any, to modify the target.
    - Else try to apply theorem to selected objects to get a new property.
    """

    # test_selection(selected_objects, target_selected)
    target_selected = proof_step.target_selected
    theorem = proof_step.statement
    selected_objects = proof_step.selection

    goal = proof_step.goal
    codes = CodeForLean()
    theorem_goal: Goal = theorem.initial_proof_state.goals[0]

    if not target_selected and not selected_objects:
        codes = add_statement_to_context(proof_step, theorem)
        return codes

    substitution, equality = theorem_goal.target.can_be_used_for_substitution()
    if substitution:
        codes = rw_using_statement(goal, selected_objects, theorem)

    h = get_new_hyp(proof_step)
    th = theorem.lean_name
    if len(selected_objects) == 0:
        code = CodeForLean(f'apply_with {th} {{md:=reducible}}',
                           success_msg=_('Target replaced by applying theorem'))
        code.outcome_operator = theorem
        codes = codes.or_else(code)

    else:
        command = f'have {h} := {th}' + ' '
        command_implicit = f'have {h} := @{th}' + ' '
        names = [item.info['name'] for item in selected_objects]
        arguments = ' '.join(names)
        if target_selected:
            more_codes = [f'apply_with ({th} {arguments})  {{md:=reducible}}',
                          f'apply_with (@{th} {arguments})  {{md:=reducible}}']
            success_msg = (_("Target replaced by applying theorem to ")
                           + arguments)
            more_codes = CodeForLean.or_else_from_list(more_codes)
            more_codes.outcome_operator = theorem

        else:
            # Up to 4 implicit arguments
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
            success_msg = (_('Theorem') + ' ' + _('applied to') + ' '
                           + arguments)
            more_codes = CodeForLean.or_else_from_list(more_codes)

        more_codes.add_success_msg(success_msg)
        more_codes.add_used_properties(selected_objects)

        codes = codes.or_else(more_codes)
        codes.add_error_msg(_("Unable to apply theorem"))
        codes.operator = theorem

    return codes
