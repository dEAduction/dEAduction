"""
###################################################
# proofs.py : provide lean code for proof buttons #
###################################################

Author(s)     : Marguerite Bin <bin.marguerite@gmail.com>
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
from typing import Union

from deaduction.pylib.text        import tooltips
# from deaduction.pylib.config.i18n import _
import deaduction.pylib.config.vars as cvars
from deaduction.pylib.actions import (InputType,
                                      MissingParametersError,
                                      WrongUserInput,
                                      action,
                                      CodeForLean,
                                      apply_or)

from deaduction.pylib.mathobj import (MathObject,
                                      get_new_hyp,
                                      give_global_name)

from deaduction.pylib.math_display import new_objects, new_properties

log = logging.getLogger(__name__)
global _

# # Turn proof_button_texts into a dictionary
# proof_list = ['action_apply', 'proof_methods', 'new_object']
# lbt = tooltips.get('proof_button_texts').split(', ')
# proof_button_texts = {}
# for key, value in zip(proof_list, lbt):
#     proof_button_texts[key] = value


@action()
def action_proof_methods(proof_step,
                         selected_objects: [MathObject],
                         user_input: [str],
                         target_selected: bool = True) -> CodeForLean:

    # 1st call, choose proof method
    if not user_input:
        choices = [('1', _("Case-based reasoning")),
                   ('2', _("Proof by contraposition")),
                   ('3', _("Proof by contradiction"))]
        allow_proof_by_sorry = cvars.get('functionality.allow_proof_by_sorry')
        if allow_proof_by_sorry:
            choices.append(('4', _("Admit current sub-goal!")))
        raise MissingParametersError(InputType.Choice,
                                     choices,
                                     title=_("Choose proof method"),
                                     output=_("Which proof method?")
                                     )
    # 2nd call, call the adequate proof method. len(user_input) = 1.
    else:
        method = user_input[0] + 1
        if method == 1:
            return method_cbr(proof_step, selected_objects, user_input)
        if method == 2:
            return method_contrapose(proof_step, selected_objects)
        if method == 3:
            return method_absurdum(proof_step, selected_objects)
        if method == 4:
            return method_sorry(proof_step, selected_objects)
    raise WrongUserInput


def method_cbr(proof_step,
               selected_objects: [MathObject],
               user_input: [str] = []) -> CodeForLean:
    """
    Engage in a proof by cases.
    - If selection is empty, then ask the user to choose a property
    - If a disjunction is selected, use this disjunction for the proof by cases
    _ If anything else is selected try to discuss on this property
    (useful only in propositional calculus?)
    In any case, ask the user which case she wants to prove first.
    """

    if len(selected_objects) == 0:
        # NB: user_input[1] contains the needed property
        if len(user_input) == 1:
            raise MissingParametersError(
                 InputType.Text,
                 title=_("cases"),
                 output=_("Enter the property you want to discriminate on:")
                                        )
        else:
            h0 = user_input[1]
            h1 = get_new_hyp(proof_step)
            h2 = get_new_hyp(proof_step)
            code = CodeForLean.from_string(f"cases (classical.em ({h0})) "
                                           f"with {h1} {h2}")
            code.add_success_msg(_("Proof by cases"))
            code.add_disjunction(h0, h1, h2)  # Strings, not MathObject
    else:
        prop = selected_objects[0]
        if not prop.is_or():
            error = _("Selected property is not a disjunction")
            raise WrongUserInput(error)
        else:
            code = apply_or(proof_step, selected_objects, user_input)

    return code


def method_contrapose(proof_step,
                      selected_objects: [MathObject]) -> CodeForLean:
    """
    If target is an implication, turn it to its contrapose.
    If a property P is selected, and target is Q, then assume (not Q) and
    change target to (not P).
    """

    target: MathObject = proof_step.goal.target

    if len(selected_objects) == 0:
        if target.is_implication():
            code = CodeForLean.from_string("contrapose")
            code.add_success_msg(_("Target replaced by contrapositive"))
            return code
        else:
            error = _('Proof by contraposition only applies when target is '
                      'an implication')
    elif len(selected_objects) == 1:
        prop: MathObject = selected_objects[0]
        if prop.math_type.is_prop():
            name = prop.info["name"]
            h = get_new_hyp(proof_step)
            code = CodeForLean.from_string(f"contrapose {name} with {h}")
            code.add_success_msg(_("Proof by contraposition with hypothesis "
                                   "{}").format(name))
            return code
        else:
            error = _("Selected object should be a property")
            raise WrongUserInput(error)
    else:
        error = _('There should be at most one selected property')
    raise WrongUserInput(error)


def method_absurdum(proof_step, selected_objects: [MathObject]) -> CodeForLean:
    """
    If no selection, engage in a proof by contradiction.
    """
    if len(selected_objects) == 0:
        new_hypo = get_new_hyp(proof_step)
        code = CodeForLean.from_string(f'by_contradiction {new_hypo}')
        code.add_success_msg(_("Negation of target added to the context"))
        return code
    else:
        error = _('Proof by contradiction only applies to target')
    raise WrongUserInput(error)


def method_sorry(proof_step, selected_objects: [MathObject]) -> CodeForLean:
    """
    Close the current sub-goal by sending the 'sorry' code.
    """
    return CodeForLean.from_string('sorry')


def introduce_fun(proof_step, selected_objects: [MathObject]) -> CodeForLean:
    """
    If a hypothesis of form ∀ a ∈ A, ∃ b ∈ B, P(a,b) has been previously
    selected: use the axiom of choice to introduce a new function f : A → B
    and add ∀ a ∈ A, P(a, f(a)) to the properties.
    """

    goal = proof_step.goal

    error = _('Select a property "∀ x, ∃ y, P(x,y)" to get a function')
    success = _("Function {} and property {} added to the context")
    if len(selected_objects) == 1:
        h = selected_objects[0].info["name"]
        # Finding expected math_type for the new function
        universal_property = selected_objects[0]
        if universal_property.is_for_all():
            source_type = universal_property.math_type.children[0]
            exist_property = universal_property.math_type.children[2]
            if exist_property.is_exists(is_math_type=True):
                target_type = exist_property.children[0]
                math_type = MathObject(node="FUNCTION",
                                       info={},
                                       children=[source_type, target_type],
                                       bound_vars=[],
                                       math_type=MathObject.NO_MATH_TYPE)

                hf = get_new_hyp(proof_step)
                f = give_global_name(math_type=math_type,
                                     proof_step=proof_step)
                code = CodeForLean.from_string(f'cases '
                                               f'classical.axiom_of_choice '
                                               f'{h} with {f} {hf}, '
                                               f'dsimp at {hf}, '
                                               f'dsimp at {f}')
                code.add_error_msg(error)
                success = success.format(f, hf)
                code.add_success_msg(success)
                return code
    raise WrongUserInput(error)


@action()
def action_new_object(proof_step,
                      selected_objects: [MathObject],
                      user_input: [str] = None,
                      target_selected: bool = True) -> CodeForLean:
    """
    Introduce new object / sub-goal / function
    """

    goal = proof_step.goal

    codes = []
    # Choose between object/sub-goal/function
    if not user_input:
        raise MissingParametersError(InputType.Choice,
                             [(_("Object"), _("Introduce a new object")),
                              (_("Goal"), _("Introduce a new "
                                            "intermediate sub-goal")),
                              (_("Function"), _("Introduce a new "
                                                "function"))],
                             title=_("New object"),
                             output=_("Choose what to introduce:"))
    # Choice = new object
    if user_input[0] == 0:
        if len(user_input) == 1:  # Ask for name
            raise MissingParametersError(InputType.Text,
                                         title="+",
                                         output=_("Name your object:"))
        elif len(user_input) == 2:
            # Check name does not already exists
            name = user_input[1]
            names = [obj.display_name for obj in goal.context]
            if name in names:
                user_input.pop()
                output = _("This name already exists, please give a new name:")
                raise MissingParametersError(InputType.Text,
                                             title="+",
                                             output=output)
            else:  # Ask for new object
                output = new_objects
                raise MissingParametersError(InputType.Text,
                                             title=_("Introduce a new object"),
                                             output=output)
        else:  # Send code
            name = user_input[1]
            new_hypo_name = get_new_hyp(proof_step)
            new_object = user_input[2]
            codes = CodeForLean.from_string(f"let {name} := {new_object}")
            codes = codes.and_then(f"have {new_hypo_name} : {name} = "
                                                     f"{new_object}")
            codes = codes.and_then("refl")
            codes.add_success_msg(_("New object {} added to the context").
                                  format(name))
            if goal.target.is_for_all():
                # User might want to prove a universal property "∀x..."
                # and mistake "new object" for introduction of the relevant x.
                codes.add_error_msg(_("You might try the ∀ button..."))

    # Choice = new sub-goal
    elif user_input[0] == 1:
        if len(user_input) == 1:
            output = new_properties
            raise MissingParametersError(InputType.Text,
                                         title=_("Introduce a new subgoal"),
                                         output=output)
        else:
            new_hypo_name = get_new_hyp(proof_step)
            codes = CodeForLean.from_string(f"have {new_hypo_name}:"
                                                     f" ({user_input[1]})")
            codes.add_success_msg(_("New target will be added to the context "
                                    "after being proved"))
            codes.add_subgoal(user_input[1])
    # Choice = new function
    elif user_input[0] == 2:
        return introduce_fun(proof_step, selected_objects)
    return codes


#########
# UTILS #
#########

def which_number_set(string: str):
    """
    Return 'ℕ', 'ℤ', 'ℚ', 'ℝ' if string represents a number, else None
    """
    ind = -1
    if '.' in string or '/' in string:
        ind = 2  # at least Q
    string = string.replace('.', '')
    string = string.replace('/', '')
    if not string.isdigit():
        return None
    else:
        return MathObject.NUMBER_SETS_LIST[ind]


def add_type_indication(item: Union[str, MathObject],
                        math_type: MathObject=None) -> Union[str, MathObject]:
    """
    Add type indication for Lean. e.g.
    '0' -> (0:ℝ)
    'x' -> (x:ℝ)
    :param item:        either a string (provided by user in TextDialog) or
    MathObject
    :param math_type:   math_type indication to add. If None, largest number
    set used in current context will be indicated
    :return: either     string or MathObject, with type indication in name
    """
    if math_type:
        number_type = math_type.which_number_set(is_math_type=True)
    if isinstance(item, str):
        number_set = which_number_set(item)
        if number_set and ':' not in item:
            if not math_type:
                MathObject.add_numbers_set(number_set)
                # Add type indication = largest set of numbers among used
                number_type = MathObject.number_sets[-1]
            item = f"({item}:{number_type})"  # e.g. (0:ℝ)
        return item
    else:
        if not math_type:
            number_type = MathObject.number_sets[-1]
        if hasattr(item, 'info'):
            name = item.display_name
            # Do not put 2 type indications!!
            if (':' not in name
                    and hasattr(item, 'info')):
                item.info['name'] = f"({name}:{number_type})"
        return item
