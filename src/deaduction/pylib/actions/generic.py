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

from deaduction.pylib.actions import MissingCalculatorOutput, CalculatorRequest
from deaduction.pylib.actions import CodeForLean, test_selection
from deaduction.pylib.give_name.get_new_hyp import get_new_hyp
from deaduction.pylib.actions.commun_actions import use_forall

# from deaduction.pylib.proof_state import Goal

global _


def rw_using_statement(goal,  # Goal,
                       selected_objects,
                       statement) -> CodeForLean:
    """
    Return codes trying to use statement for rewriting. This should be
    reserved to iff or equalities. This function is called by
    action_definition, and by action_theorem in case the theorem is an iff
    statement.
    """

    # defi = statement.lean_name
    defi_names = [statement.lean_name] + statement.auxiliary_definitions
    arguments = ''
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

    raw_codes = []
    if len(selected_objects) == 0:
        for defi in defi_names:
            raw_codes.extend([f'rw {defi}',
                              f'simp_rw {defi}',
                              f'rw <- {defi}',
                              f'simp_rw <- {defi}'])
        codes = CodeForLean.or_else_from_list(raw_codes)
        codes.add_success_msg(target_msg)

    else:
        names = [item.info['name'] for item in selected_objects]
        arguments = ' '.join(names)
        for defi in defi_names:
            raw_codes.extend([f'rw {defi} at {arguments}',
                              f'simp_rw {defi} at {arguments}',
                              f'rw <- {defi} at {arguments}',
                              f'simp_rw <- {defi} at {arguments}'])
        codes = CodeForLean.or_else_from_list(raw_codes)
        context_msg += ' ' + arguments
        codes.add_success_msg(context_msg)

    codes.rw_item = statement  # (statement.type_, statement.pretty_name)

    # Add try_norm_num; this removes lambda that can occur e.g. when applying
    # def of injectivity backwards
    # Fixme: simp_only tends to suppress vars
    #  e.g. Exists l, limit u l --> Exists limit u
    #  lambda n, (-1)^n --> pow (-1) and then Lean error!
    codes = codes.and_try_simp_only(location=arguments)

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

    # FIXME!!!!
    return action_theorem(proof_step)
    
    target_selected = proof_step.target_selected
    definition = proof_step.statement
    selected_objects = proof_step.selection
    test_selection(selected_objects, target_selected,
                   exclusive=True,
                   force_default_target=True)
    if not target_selected and not selected_objects:
        # FIXME: open Calculator instead?
        codes = add_statement_to_context(proof_step, definition)
        return codes

    else:
        codes = rw_using_statement(proof_step.goal, selected_objects,
                                   definition)
        codes.add_error_msg(_("Unable to apply definition"))
    return codes


def apply_theorem(proof_step) -> CodeForLean:
    """
    Apply theorem on selected objects (assumed to be non empty).
    """

    target_selected = proof_step.target_selected
    theorem = proof_step.statement
    selected_objects = proof_step.selection

    goal = proof_step.goal
    codes = CodeForLean()

    # if not target_selected and not selected_objects:
    #     codes = add_statement_to_context(proof_step, theorem)
    #     return codes

    # Add to context in case of drag n drop FIXME?
    if proof_step.drag_n_drop and proof_step.drag_n_drop.statement:
        codes = add_statement_to_context(proof_step, theorem)
        return codes

    ips = theorem.initial_proof_state
    theorem_goal = ips.goals[0] if ips else None  # Goal
    substitution, equality = (theorem_goal.target.can_be_used_for_substitution()
                              if theorem_goal else True, None)
    # If no ips available, then try anyway!
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


def action_theorem(proof_step) -> CodeForLean:
    """
    If an object or the target is (explicitly) selected, then call the
    theorem on it. If the theorem can be used for substitution,
    and all selected objects are properties,
    then a rewriting will be called.

    If nothing is selected, and the theorem is a universal
    property (which happens almost everytime), call Calculator so that usr
    enter the object on which the theorem will be applied (no rewriting in
    this case).
    """

    target_selected = proof_step.target_selected
    theorem = proof_step.statement
    selected_objects = proof_step.selection

    if selected_objects or target_selected:
        # TODO: use common actions (use_forall, etc.)
        return apply_theorem(proof_step)

    if proof_step.drag_n_drop and proof_step.drag_n_drop.statement:
        codes = add_statement_to_context(proof_step, theorem)
        return codes

    theorem_as_math_object = theorem.goal().to_math_object()

    # If all vars are implicit, do not call Calculator!
    if not theorem_as_math_object.is_for_all(is_math_type=True):
        # or not theorem_as_math_object.types_n_vars_of_univ_prop()):
        # proof_step.target_selected = True  # Cheating a little bit
        # TODO: consider other operators
        # TODO: implicit defs
        return apply_theorem(proof_step)

    # Apply universal statement
    if not proof_step.user_input:
        msg = _("Select at least one property")
        raise MissingCalculatorOutput(CalculatorRequest.ApplyStatement,
                                      proof_step=proof_step,
                                      statement=theorem,
                                      msg_if_no_calculator=msg)

    arguments = [arg if arg.is_place_holder()
                 else arg.between_parentheses(arg)
                 for arg in proof_step.user_input[0]]
    code = use_forall(proof_step, arguments,
                      universal_property_or_statement=theorem,
                      no_more_place_holder=True)
    
    # Apply auxiliary statements    
    # aux_codes = [use_forall(proof_step, arguments,
    #                         universal_property_or_statement=aux_theorem,
    #                         no_more_place_holder=True)
    #              for aux_theorem in theorem.auxiliary_statements]
    # code = code.or_else_from_list([code] + aux_codes)
    return code





