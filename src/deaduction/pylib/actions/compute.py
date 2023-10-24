"""
########################################
# compute.py : Actions for computation #
########################################

Author(s)     : - Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
Maintainer(s) : - Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
Created       : October 2023 (creation)
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

from deaduction.pylib.actions     import (action,
                                          InputType,
                                          MissingParametersError,
                                          WrongUserInput,
                                          WrongProveModeInput,
                                          WrongUseModeInput,
                                          test_selection,
                                          test_prove_use,
                                          CodeForLean)

from deaduction.pylib.give_name import get_new_hyp

log = logging.getLogger(__name__)

global _


@action()
def action_sum(proof_step) -> CodeForLean:
    """
    Try several adding lemmas, by calling the custom tactics smart_add:
    - add two selected equalities/inequalities (strict or not),
    - add some number to an equality/inequality,
    - add two numbers to create a third one.
    """
    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected

    test_selection(selected_objects, target_selected)

    # TODO: if len(selected_objects) == 1:
    #  MissingParam --> user rentre un nb à ajouter.
    #   e.g.
    #     let a := 2,
    #     have Haux0: a = 2, refl,
    #     smart_add H1_lt a with H, rw Haux0 at H, clear Haux0, clear a,

    if len(selected_objects) == 2:

        H0 = selected_objects[0]
        H1 = selected_objects[1]
        # TODO: accept H0=nb, H1=ineq to add H0 on the left instead of the right
        if not H0.math_type.is_prop() and H1.math_type.is_prop():
            # smart_add accept an inequality (first pos) and a number
            H0, H1 = H1, H0
        new_hypo_name = get_new_hyp(proof_step)
        code = CodeForLean.from_string(
            f"smart_add {H0} {H1} with {new_hypo_name}")
        code.add_success_msg(_(f"Adding {H0} and {H1} to get {new_hypo_name}"))
        code.add_error_msg(f"I cannot add {H0} and {H1}")
        # code.add_error_msg(f"Use the + button for inequalities")
        return code

    # TODO: add one ine to a number


# TODO: select pertinent mul lemmas ??
#   This is more subtil, since we have to check signs
# @action()
# def action_mul(proof_step) -> CodeForLean:
#     """
#     Try several adding lemmas, by calling the custom tactics smart_add:
#     - add two selected equalities/inequalities (strict or not),
#     - add some number to an equality/inequality,
#     - add two numbers to create a third one.
#     """
#     selected_objects = proof_step.selection
#     target_selected = proof_step.target_selected
#
#     test_selection(selected_objects, target_selected)
#
#     # TODO: if len(selected_objects) == 1:
#     #  MissingParam --> user rentre un nb à ajouter.
#
#     if len(selected_objects) == 2:
#
#         H0 = selected_objects[0]
#         H1 = selected_objects[1]
#         # TODO: accept H0=nb, H1=ineq to add H0 on the left instead of the right
#         if not H0.math_type.is_prop() and H1.math_type.is_prop():
#             # smart_add accept an inequality (first pos) and a number
#             H0, H1 = H1, H0
#         new_hypo_name = get_new_hyp(proof_step)
#         code = CodeForLean.from_string(
#             f"smart_mul {H0} {H1} with {new_hypo_name}")
#         code.add_success_msg(_(f"Multiplying {H0} and {H1} to get"
#                                f" {new_hypo_name}"))
#         code.add_error_msg(f"I cannot multiply {H0} and {H1}")
#         # code.add_error_msg(f"Use the + button for inequalities")
#         return code
#
#     # TODO: add one ineg to a number

@action()
def action_simplify(proof_step) -> CodeForLean:
    """
    Try norm_num, and various simp lemmas, on selection. Only one selected
    prop at a time.
    TODO: this should be customizable in lean super-user file.
    """
    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected

    test_selection(selected_objects, target_selected, exclusive=True)

    selected_name = ""
    if len(selected_objects) == 1:  # no selection : simplify everything??
        selected_name = selected_objects[0].name
    elif len(selected_objects) > 1:
        raise WrongUseModeInput("Select only one object at a time")

    location = "" if target_selected else " at " + selected_name

    code1 = CodeForLean("norm_num")
    simp2 = f"simp only [] with simp_arith {location}"
    code2 = CodeForLean(simp2)
    code = ((code1.and_then(code2)).or_else(code2)).or_else(code1)

    msg = ("Target simplified" if target_selected
           else f"Property {selected_name} simplified")
    code.add_success_msg(msg)
    code.add_error_msg(_("Unable to simplify"))
    return code


# @action()
# def action_factorize(proof_step) -> CodeForLean:
#     pass
#
#
# @action()
# def action_expand(proof_step) -> CodeForLean:
#     pass
#
#


@action()
def action_transitivity(proof_step) -> CodeForLean:
    """
    Try several transitivity lemma (the 'smart_trans' tactic), in particular
    chaining inequalities. This is a symmetric tactic.
    """
    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected

    test_selection(selected_objects, target_selected)

    if len(selected_objects) != 2:
        raise WrongUseModeInput("Transitivity needs exactly two properties")

    H0 = selected_objects[0]
    H1 = selected_objects[1]
    new_hypo_name = get_new_hyp(proof_step)
    code = CodeForLean.from_string(
        f"smart_trans {H0} {H1} with {new_hypo_name}")
    code.add_success_msg(_(f"Chaining {H0} and {H1} to get {new_hypo_name}"))
    code.add_error_msg(f"I cannot chain {H0} and {H1}")
    # code.add_error_msg(f"Use the + button for inequalities")
    return code


@action()
def action_commute(proof_step) -> CodeForLean:
    """
    Try to apply commutativity rules on a single selected property.
    """
    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected

    test_selection(selected_objects, target_selected, exclusive=True)

    if target_selected and not selected_objects:
        code = CodeForLean(f"smart_comm_on_target")
        msg = _("Apply commutation on target")
        code.add_success_msg(msg)
        code.add_error_msg(f"I don't know how to apply commutation.")
        return code

    elif len(selected_objects) == 1:  # no selection : simplify everything??
        selected_name = selected_objects[0].name
        code = CodeForLean(f"smart_comm {selected_name}")
        msg = _("Apply commutation on {}").format(selected_name)
        code.add_success_msg(msg)
        code.add_error_msg(f"I don't know how to apply commutation.")
        return code

    else:
        raise WrongUseModeInput("Select one object at a time")


@action()
def action_associativity(proof_step) -> CodeForLean:
    """
    Try to apply associativity rules on a single selected property.
    """
    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected

    test_selection(selected_objects, target_selected, exclusive=True)

    if target_selected and not selected_objects:
        code = CodeForLean(f"smart_assoc_on_target")
        msg = _(f"Apply associativity on target")
        code.add_success_msg(msg)
        code.add_error_msg(f"I don't know how to apply associativity.")
        return code

    elif len(selected_objects) == 1:  # no selection : simplify everything??
        selected_name = selected_objects[0].name
        code = CodeForLean(f"smart_assoc {selected_name}")
        msg = _("Apply associativity on {}").format(selected_name)
        code.add_success_msg(msg)
        code.add_error_msg(f"I don't know how to apply associativity.")
        return code

    else:
        raise WrongUseModeInput("Select one object at a time")


@action()
def action_triangular_inequality(proof_step) -> CodeForLean:
    """
    Try to apply a triangular inequality which is pertinent with respect
    to a given expression.
    """
    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected

    test_selection(selected_objects, target_selected, exclusive=True)

    if len(selected_objects) == 1:  # no selection : simplify everything??
        selected_name = selected_objects[0].name
    elif len(selected_objects) > 1:
        raise WrongUseModeInput("Select only one object")

    new_hyp = get_new_hyp(proof_step)
    code1 = CodeForLean("norm_num").try_()  # To normalise inequalities
    if target_selected:
        location = "target"
        simp2 = f"smart_triang_ineq_on_target with {new_hyp}"
    else:
        location = selected_name
        simp2 = f"smart_triang_ineq {location} with {new_hyp}"
    code2 = CodeForLean(simp2)
    code = code1.and_then(code2)

    msg = f"Triangular inequality {new_hyp} added to the context"
    code.add_success_msg(msg)
    code.add_error_msg(_("No absolute value found in {}").format(location))
    return code




