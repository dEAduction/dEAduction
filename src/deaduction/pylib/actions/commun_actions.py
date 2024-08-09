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
from typing import Optional, Union

import deaduction.pylib.config.vars as cvars
from deaduction.pylib.actions.utils import pre_process_lean_code

from deaduction.pylib.actions import (CalculatorRequest,
                                      MissingCalculatorOutput,
                                      InputType,
                                      MissingParametersError,
                                      CodeForLean,
                                      SyntheticProofStep,
                                      SyntheticProofStepType)

from deaduction.pylib.config.request_method import from_previous_state_method

from deaduction.pylib.give_name import get_new_hyp
from deaduction.pylib.actions.utils import (add_type_indication,
                                            extract_var)
from deaduction.pylib.actions.magic import compute

from deaduction.pylib.mathobj import MathObject
# from deaduction.pylib.coursedata import Statement


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
        msg = _("Action not available")
        raise MissingCalculatorOutput(CalculatorRequest.StateSubGoal,
                                      proof_step=proof_step,
                                      msg_if_no_calculator=msg)
        # raise MissingParametersError(InputType.Calculator,
        #                              title=_("Introduce a new subgoal"),
        #                              target=MathObject.PROP)  # FIXME
        # raise MissingParametersError(InputType.Text,
        #                                  title=_("Introduce a new object"),
        #                                  output=output)
        # else:  # Send code
        #     name = pre_process_lean_code(user_input[1])
        #     new_hypo_name = get_new_hyp(proof_step, name='Def')
        #     new_object = user_input[2].to_display(format_='lean')
    elif len(user_input) == 2:
        sub_goal = user_input[1][0]
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


# FIXME: obsolete
def inequality_from_pattern_matching(math_object: MathObject,
                                     variable: MathObject) -> Optional[MathObject]:
    """
    Check if math_object.math_type has the form
    ∀ x:X, (x R ... ==> ...)
    where R is some inequality relation, and if this statement may be
    applied to variable. If so, return inequality with x replaced by variable
    """

    # inequality = None
    # if not math_object.is_for_all(implicit=True):
    #     return None
    #
    # if not math_object.is_for_all(is_math_type=False):
    #     # Implicit "for all"
    #     math_object = MathObject.last_rw_object
    # else:
    #     math_object = math_object.math_type
    #
    # math_type, var, body = math_object.children
    # # NB: following line does not work because of coercions
    # # if var.math_type == variable.math_type:
    # if body.is_implication(is_math_type=True):
    #     premise = body.children[0]  # children (2,0)
    #     if (premise.is_inequality(is_math_type=True) and
    #             var == premise.children[0]):
    #         children = [variable, premise.children[1]]
    #         inequality = MathObject(node=premise.node,
    #                                 info={},
    #                                 children=children,
    #                                 math_type=premise.math_type)
    math_object = math_object.math_type
    p_n_b = math_object.bound_prop_n_actual_body_of_bounded_quant()
    if p_n_b:
        inequality, body = p_n_b
        if inequality.is_inequality(is_math_type=True):
            children = [variable, inequality.children[1]]
            new_inequality = MathObject(node=inequality.node,
                                        info={},
                                        children=children,
                                        math_type=inequality.math_type)

            return new_inequality


def have_new_property(operator,  #: Union[MathObject, Statement]
                      arguments: [Union[MathObject, str]],
                      new_hypo_name: str,
                      success_msg=None,
                      iff_direction='',
                      no_more_place_holder=False) -> CodeForLean:
    """
    Compute Lean code to apply an implication or a universal property to a
    property or a variable.
    Try implicit and explicit version of the statement 'arrow'.
    Try to place up to 6 place_holders ('_') at the beginning,
    except if variables already contains some, in which case only the
    explicit statement is sent to Lean.

    @param operator:           a MathObject or a Statement which is either an
                            implication or a universal property
    @param arguments:       a list of MathObjects to which "arrow" will be
                            applied
    @param new_hypo_name:   a fresh name for the new property

    @param success_msg:     A success msg, if None then the standard one will be
                            used.

    @param iff_direction:   = 'mp' if arrow is an iff that we want to use as an
                            implication, 'mpr' for reverse direction,
                            '' if arrow is an implication.
    @param no_more_place_holder:
                            if False, try to add 0 to 6  Lean place-holders
                            ( '_').

    return:                 Lean Code to produce the wanted new property,
                            taking into account implicit parameters
    """

    # TODO: add smart guess for placeholders, by matching math types
    #  May even try to guess parameters from the context
    #  (e.g. if we need a function and there is only one in the context)

    # Try several codes, e.g. "have H10 := (@H1 _ _ ).mp H2"
    # (new_hypo_name = "H10", arrow = "H1", arguments = ["H2"], iff_direction
    # = "mp")

    # variable_names = [variable.to_display(format_='lean')
    #                   if isinstance(variable, MathObject)
    #                   else variable for variable in arguments]
    #
    # # selected_hypo = arrow.info["name"]
    # selected_hypo = operator.lean_name  # Property of both MathObject and Statement

    if not no_more_place_holder:
        no_more_place_holder = (hasattr(arguments[0], 'is_place_holder')
                                and arguments[0].is_place_holder())
    # have = f'have {new_hypo_name} := '
    # args = ' '.join(variable_names)
    implicit_codes = []
    explicit_codes = []
    nbs = [0] if no_more_place_holder else range(6)  # Implicit args ('_')
    for nb in nbs:
        have = CodeForLean.have(new_hypo_name, operator, arguments,
                                iff_direction=iff_direction, explicit=False,
                                nb_place_holders=nb)
        # imp_code = f'{selected_hypo} ' + '_ '*nb
        # exp_code = f'@{selected_hypo} ' + '_ '*nb
        # if iff_direction:
        #     if nb > 0:
        #         imp_code = '(' + imp_code + ')'
        #         exp_code = '(' + exp_code + ')'
        #     imp_code = imp_code + '.' + iff_direction + ' '
        #     exp_code = exp_code + '.' + iff_direction + ' '
        implicit_codes.append(have)
        have = CodeForLean.have(new_hypo_name, operator, arguments,
                                iff_direction=iff_direction, explicit=True,
                                nb_place_holders=nb)
        explicit_codes.append(have)

    codes = (explicit_codes if no_more_place_holder
             else implicit_codes + explicit_codes)
    code = CodeForLean.or_else_from_list(codes)
    if success_msg is None:
        success_msg = _("Property {} added to the context").format(new_hypo_name)
    code.add_success_msg(success_msg)

    code.operator = operator
    return code


def use_forall_with_ineq(proof_step, arguments,
                         universal_property_or_statement, inequality,
                         new_hypo_name=None,
                         no_place_holder=False) -> CodeForLean:
    """
    Try to use last selected property, assumed to be a universal prop matching
    forall x, (some inex on x) ==> ...

    The inequality on x is the MathObject inequality.
    - If inequality belongs to the context, we use the universal property
    to x and inequality
    - if not, we claim inequality, apply the universal property to it,
    and ask Lean to try to solve the inequality.

    Note that universal_property_or_statement is either a MathObject or a
    Statement, and will be passed to the have_new_property() method.
    """

    proof_step.prove_or_use = "use"

    if not new_hypo_name:
        new_hypo_name = get_new_hyp(proof_step)

    goal = proof_step.goal
    # if isinstance(universal_property_or_statement, MathObject):
    #     universal_property = universal_property_or_statement
    # else:
    #     universal_property = universal_property_or_statement.contextless()

    unsolved_inequality_counter = 0
    # Variable_names will contain the list of variables and proofs of
    # inequalities that will be passed to universal_property
    variables = []
    used_inequalities = []
    # Check for "∀x>0" (and variations)
    variable = inequality.children[0]
    variables.append(variable)
    math_types = [p.math_type for p in goal.context]
    code = CodeForLean.empty_code()

    # (1) Try to prove inequality
    idx = inequality.is_in(math_types,
                           remove_generic_paren=True,
                           use_assigned_math_obj=True)
    if idx is not False:
        # Check if inequality is in context
        ineq_in_ctxt = True
        # index = math_types.index(inequality)
        context_inequality = goal.context[idx]
        used_inequalities.append(context_inequality)
        # inequality will be passed to the "have" tactics:
        variables.append(context_inequality)
    else:
        # If not, assert inequality as a new goal:
        ineq_in_ctxt = False
        inequality_name = new_hypo_name
        variables.append(inequality_name)
        unsolved_inequality_counter += 1
        # Add type indication to the variable in inequality
        math_type = inequality.children[1].math_type
        # Variable is not used explicitly, but this affects inequality:
        # FIXME: now useless, this is included in Lean display?
        variable = add_type_indication(variable, math_type)
        ineq_with_type = MathObject(node=inequality.node,
                                    info=inequality.info,
                                    children=[variable,
                                              inequality.children[1]],
                                    math_type=inequality.math_type)
        display_inequality = ineq_with_type.to_display(format_='lean')
        # Code I: state corresponding inequality #
        code = CodeForLean.from_string(f"have {inequality_name}: "
                                       f"{display_inequality}")
        code = code.and_then("rotate")  # Back to main goal
        used_inequalities.append(inequality_name)

    # (2) Apply universal_property, with no success_msg #
    # Add remaining variables:
    variables.extend(arguments[1:])
    if not ineq_in_ctxt:  # Hypo_name has been used
        new_hypo_name = get_new_hyp(proof_step)
    have = have_new_property(universal_property_or_statement, variables,
                             new_hypo_name, success_msg="",
                             no_more_place_holder=no_place_holder)
    code = code.and_then(have)

    if used_inequalities:
        code.add_used_properties(used_inequalities)

    # (3) try to solve inequalities # e.g.:
    #   iterate 2 { solve1 {try {norm_num at *}, try {compute_n 10}} <|>
    #               rotate},   rotate,
    if unsolved_inequality_counter:
        assert unsolved_inequality_counter == 1
        # Back to first inequality anyway:
        if from_previous_state_method():
            # In this case no memory of previous goals
            more_code0 = CodeForLean.from_string("rotate")
        else:
            nbg = proof_step.nb_of_goals
            more_code0 = CodeForLean.from_string(f"rotate {nbg}")
        code = code.and_then(more_code0)
        # var = inequality.children[0].to_display(format='utf8')
        ineq_display = inequality.to_display(format_='utf8')
        msg = (_("Property {} will be added to the context").
               format(new_hypo_name))
        msg += _(" after we check {}").format(ineq_display)

        if inequality.is_inequality(is_math_type=True):
            # Try to solve1 inequality by norm_num, maybe followed by compute:
            try_succeed_msg = (_("Property {} added to the context").
                               format(new_hypo_name))
            more_code1 = compute(proof_step).try_(
                try_succeed_msg=try_succeed_msg,
                try_fail_msg=msg)
            # more_code1.add_success_msg()
            code = code.and_then(more_code1)
        else:
            code.add_success_msg(msg)

    if not unsolved_inequality_counter:
        # Success msg when there is no inequality to solve:
        code.add_success_msg(_("Property {} added to the context").
                             format(new_hypo_name))
    # In any case:
    code.add_used_properties(proof_step.selection)
    code.operator = universal_property_or_statement
    return code


def use_forall(proof_step, arguments: [MathObject],
               universal_property_or_statement,
               no_more_place_holder=False) -> CodeForLean:
    """
    Try to apply universal_property on arguments.
    universal_property should be a universal property,
    or equivalent to such after unfolding definitions.

    param universal_property: either a ContextMathObject, or a Statement.
    """
    # FIXME: return error msg if user try to apply "forall x:X, P(x)"
    #  to some object of wrong type (e.g. implication)
    #  For the moment "forall x, P->Q" works with "P->Q" and button forall

    # selected_objects = proof_step.user_input + proof_step.selection
    selected_objects = proof_step.selection
    proof_step.prove_or_use = "use"

    # universal_property = selected_objects[-1]  # The property to be applied
    new_hypo_name = get_new_hyp(proof_step)
    # variables = selected_objects[:-1]

    # If first arg is an equality, replace by left term:
    arguments[0] = extract_var(arguments[0])
    simple_code = have_new_property(universal_property_or_statement, arguments,
                                    new_hypo_name,
                                    no_more_place_holder=no_more_place_holder)

    # Add SyntheticProofStep data:
    if isinstance(universal_property_or_statement, MathObject):
        sps_type = SyntheticProofStepType.ApplyUnivProp
    else:
        sps_type = SyntheticProofStepType.ApplyUnivStatement
    sps = SyntheticProofStep(type_=sps_type,
                             operator=universal_property_or_statement,
                             premises=arguments)
    simple_code.synthetic_proof_step = sps

    universal_property = universal_property_or_statement.to_math_object()

    # Bounded quantification?
    # inequality = inequality_from_pattern_matching(universal_property,
    #                                               arguments[0])

    inequality = universal_property.bounded_quant(arguments[0])
    # (Case 1) No inequality to solve
    auto_solve = cvars.get("functionality.auto_solve_inequalities_"
                           "in_bounded_quantification", False)
    if not inequality or not auto_solve:
        code = simple_code
        # return simple_code

    # (Cas 2) Inequality: try to solve it, turn to simple code if it fails
    else:
        complex_code = use_forall_with_ineq(proof_step, arguments,
                                            universal_property_or_statement,
                                            inequality, new_hypo_name,
                                            no_place_holder=no_more_place_holder)
        sps2 = SyntheticProofStep(type_=sps_type,
                                  operator=universal_property_or_statement,
                                  premises=arguments + [inequality])
        complex_code.synthetic_proof_step = sps2
        code = complex_code.or_else(simple_code)

    code.add_used_properties(selected_objects)
    return code


def provide_name_for_new_vars(proof_step, math_types: [],
                              text="", user_input_nb=0):
    """
    Provide names for new vars of types math_types, either by asking usr or
    by calling proof_step.goal.provide_good_name.
    @param proof_step:
    @param math_types: list of math_types to be named.
    @param text: text to be displayed.
    @param user_input_nb: Nb of entries in user_input prior to naming.
    """

    usr_name_vars = cvars.get('logic.usr_name_new_vars')
    user_input = proof_step.user_input
    goal = proof_step.goal
    if usr_name_vars:
        if len(user_input) > user_input_nb:
            # Check last given name
            name = pre_process_lean_code(user_input[-1])
            names = [obj.display_name for obj in goal.context]
            if name in names:
                user_input.pop()
                math_type = math_types[len(user_input) - user_input_nb -1]
                type_str = math_type.to_display(format_="utf8", text=True,
                                                is_type=True)
                output = _("This name already exists in the context, please "
                           "give a new name for ") + type_str
                raise MissingParametersError(InputType.Text,
                                             title=_("New object"),
                                             output=output)
        if len(user_input) < user_input_nb + len(math_types):
            # Some names are missing
            math_type = math_types[len(user_input) - user_input_nb]
            type_str = math_type.to_display(format_="utf8", text=True,
                                            is_type=True)

            text = text + _("choose a name for") + " " + type_str
            raise MissingParametersError(InputType.Text,
                                         title=_("New object"),
                                         output=text)
        # Here all math_types have been provided good names by usr
        new_names = [pre_process_lean_code(name) for name in user_input[
                     user_input_nb:]]
    else:
        new_names = proof_step.goal.provide_good_names(math_types)

    return new_names


# def get_arguments_to_use_forall(proof_step, universal_property) -> [MathObject]:
#     """
#     This method assume that universal_property is a universal property
#     (up to unfolding implicit definitions?)
#     and that no other object has been selected. It calls the Calculator
#     to get the argument(s) to which the universal property should be applied.
#     Universal property and arguments should be sent to the use_forall() method.
#     """
#
#     # TODO: adapt to get several arguments from Calculator
#     #  --> several user_inputs
#
#     user_input = proof_step.user_input
#     # selected_objects = proof_step.selection
#
#     if not user_input:
#         # quant = selected_objects[-1].math_type
#         # input_target = universal_property.type_of_explicit_quant()
#         raise MissingCalculatorOutput(CalculatorRequest.ApplyProperty,
#                                       proof_step, prop=universal_property)
#     else:
#         arguments = [arg if arg.is_place_holder()
#                      else arg.between_parentheses(arg)
#                      for arg in user_input[0]]
#
#         # This will be a str either from Calculator in "Lean mode",
#         #   or from history file.
#         #  In this case we artificially change this to a "MathObject".
#         # In any case we add parentheses, e.g. in
#         #  have H2 := H (ε/2)
#         #  the parentheses are mandatory
#         # if isinstance(math_object, str):
#         #     math_object = MathObject(node="RAW_LEAN_CODE",
#         #                              info={'name': '(' + math_object + ')'},
#         #                              children=[],
#         #                              math_type=None)
#         # else:
#         #     math_object = MathObject(node='GENERIC_PARENTHESES',
#         #                              info={},
#         #                              children=[math_object],
#         #                              math_type=math_object.math_type)
#         # user_input[0] = math_object
#         # arguments = [user_input[0]]
#         # code = use_forall(proof_step, arguments, universal_property)
#         # return code
#         return arguments

