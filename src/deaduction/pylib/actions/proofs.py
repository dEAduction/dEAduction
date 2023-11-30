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
from enum import IntEnum

from deaduction.pylib.text        import tooltips
# from deaduction.pylib.config.i18n import _
import deaduction.pylib.config.vars as cvars

from deaduction.pylib.actions.utils import pre_process_lean_code
from deaduction.pylib.actions.commun_actions import introduce_new_subgoal
from deaduction.pylib.actions import (InputType,
                                      MissingParametersError,
                                      WrongUserInput,
                                      action,
                                      CodeForLean)
from deaduction.pylib.actions.logic import use_or

from deaduction.pylib.mathobj import MathObject
from deaduction.pylib.give_name import get_new_hyp

from deaduction.pylib.math_display import new_objects, new_properties

log = logging.getLogger(__name__)
global _

# # Turn proof_button_texts into a dictionary
# proof_list = ['action_apply', 'proof_methods', 'new_object']
# lbt = tooltips.get('proof_button_texts').split(', ')
# proof_button_texts = {}
# for key, value in zip(proof_list, lbt):
#     proof_button_texts[key] = value


class ProofMethods:
    """
    A class for recording user input for the proof_methods action.
    The nb stored in user_input must refer to the complete list, not to the
    local list of available proof methods, so that it is not dependent on
    current settings.

    To add the new proof method blabla:
    add the function method_blabla() at the right place below with the
    @add_to_proof_methods decorator,
    update the pretty_names dict,
    (update the functionality.proof_methods list in config.toml).
    .
    """

    # Items may be added here, but order changes should be avoided
    # (or propagated). Order should not affect UI.
    # Nbs in user_input refer to index in this reference_list.
    # Name of callable must be 'method_' + <name in list>
    reference_list = ["case_based", "contraposition", "contradiction",
                      "sorry", "induction"]
    ordered_list = []
    callables = []

    @staticmethod
    def pretty_names(name):
        proof_methods_dic = {'case_based': _("Case-based reasoning"),
                             'contraposition': _("Proof by contraposition"),
                             'contradiction': _("Proof by contradiction"),
                             'induction': _("Proof by induction"),
                             'sorry': _("Admit current sub-goal!")}
        return proof_methods_dic[name]

    @classmethod
    def local_list(cls):
        """
        List of available proof methods in the current settings context.
        """
        proof_methods = cvars.get('functionality.proof_methods',
                                  default_value=cls.ordered_list)
        local_methods = [m for m in proof_methods
                         if cvars.get('functionality.allow_' + m)]

        return local_methods

    @classmethod
    def choices(cls):
        """
        Return the list of possible choices, as a parameter for the
        MissingParametersError exception.
        e.g.
                choices = [('1', _("Case-based reasoning")),
                   ('2', _("Proof by contraposition")),
                   ('3', _("Proof by contradiction"))]
        """

        l = cls.local_list()
        choices = [(str(idx), cls.pretty_names(l[idx]))
                   for idx in range(len(l))]
        return choices

    @classmethod
    def local_to_absolute_nb(cls, nb):
        """
        Convert the index in the local list to the index of the same item in
        the reference list, that should be stored in user_input.
        """
        name = cls.local_list()[nb]
        idx = cls.reference_list.index(name)
        return idx

    @classmethod
    def callable_method_from_name(cls, name):
        for cal in cls.callables:
            if cal.__name__.endswith(name):
                return cal

    @classmethod
    def callable_from_abs_nb(cls, nb):
        name = cls.reference_list[nb]
        return cls.callable_method_from_name(name)


def add_to_proof_methods() -> callable:
    """
    Decorator that add function to the ProofMethods lists.
    """
    
    def proof_method(func):
        if func not in ProofMethods.callables:
            name = func.__name__[len('method_'):]
            ProofMethods.ordered_list.append(name)
            ProofMethods.callables.append(func)
        return func

    return proof_method


@action()
def action_proof_methods(proof_step) -> CodeForLean:

    selected_objects = proof_step.selection
    # target_selected = proof_step.target_selected
    user_input = proof_step.user_input

    # proof_methods = cvars.get('functionality.proof_methods',
    #                           default_value=UserInput.default)

    # 1st call, choose proof method
    if not user_input:
        # choices = [('1', _("Case-based reasoning")),
        #            ('2', _("Proof by contraposition")),
        #            ('3', _("Proof by contradiction"))]
        # allow_proof_by_sorry = cvars.get('functionality.allow_proof_by_sorry')
        # if allow_proof_by_sorry:
        #     choices.append(('4', _("Admit current sub-goal!")))
        choices = ProofMethods.choices()
        raise MissingParametersError(InputType.Choice,
                                     choices,
                                     title=_("Choose proof method"),
                                     output=_("Which proof method?"),
                                     converter=ProofMethods.local_to_absolute_nb
                                     )
    # 2nd call, call the adequate proof method. len(user_input) = 1.
    else:
        method = ProofMethods.callable_from_abs_nb(user_input[0])
        return method(proof_step, selected_objects, user_input)
        # method = int(user_input[0]) + 1
        # if method == 1:
        #     return method_case_based(proof_step, selected_objects, user_input)
        # if method == 2:
        #     return method_contraposition(proof_step, selected_objects)
        # if method == 3:
        #     return method_contradiction(proof_step, selected_objects)
        # if method == 4:
        #     return method_sorry(proof_step, selected_objects)


@add_to_proof_methods()
def method_case_based(proof_step,
                      selected_objects: [MathObject],
                      user_input=[]) -> CodeForLean:
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
            # raise MissingParametersError(
            #      InputType.Text,
            #      title=_("cases"),
            #      output=_("Enter the property you want to discriminate on:")
            #                             )
            raise MissingParametersError(InputType.Calculator,
                                         title=_("Enter the property you want to discriminate on:"),
                                         target=MathObject.PROP)

        else:
            # h0 = pre_process_lean_code(user_input[1])
            prop = user_input[1]
            h0 = (prop.to_display(format_='lean')
                  if isinstance(prop, MathObject) else prop)

            h1 = get_new_hyp(proof_step)
            h2 = get_new_hyp(proof_step)
            code = CodeForLean.from_string(f"cases (classical.em ({h0})) "
                                           f"with {h1} {h2}")
            code.add_success_msg(_("Proof by cases"))
            code.add_disjunction(prop, h1, h2)  # Strings, not MathObject
    else:
        prop = selected_objects[0]
        if not prop.is_or():
            error = _("Selected property is not a disjunction")
            raise WrongUserInput(error)
        else:
            code = use_or(proof_step, selected_objects, user_input)

    return code


@add_to_proof_methods()
def method_contraposition(proof_step,
                          selected_objects: [MathObject],
                          user_input=None) -> CodeForLean:
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


@add_to_proof_methods()
def method_contradiction(proof_step,
                         selected_objects: [MathObject],
                         user_input=None) -> CodeForLean:
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


@add_to_proof_methods()
def method_induction(proof_step,
                     selected_objects: [MathObject],
                     user_input=None) -> CodeForLean:
    """
    Try to do a proof by induction.
    """

    implicit = False
    target = proof_step.goal.target
    if not target.is_for_all(implicit=True):
        error = _("Proof by induction only applies to prove "
                  "a universal property '∀n∈ℕ, P(n)'")
        raise WrongUserInput(error)

    if not target.is_for_all(is_math_type=False):
        # Implicit "for all"
        implicit = True
        math_object = MathObject.last_rw_object
    else:
        math_object = target.math_type

    math_type, var, body = math_object.children
    if not var.is_nat():
        if not implicit:
            error = _(f"{var} is not a natural number") + ", " + \
                    _("proof by induction does not apply")
        raise WrongUserInput(error)

    var_name = proof_step.goal.provide_good_name(math_type,
                                                 var.preferred_letter())
    # h = get_new_hyp(proof_step)
    # code_s = f"intro {name}, induction {name} with {name} {h}"

    # code_s = "apply induction.simple_induction"
    # code = CodeForLean.from_string(code_s)
    # code.add_success_msg(f"Proof by induction on {name}")

    code = CodeForLean.empty_code()
    if len(user_input) < 2:
        choices = [('1', _('Base case')), ('2', _('Induction step'))]
        raise MissingParametersError(
            InputType.Choice,
            choices,
            title=_("Choose sub-goal"),
            output=_("Which property to prove first?"))
    elif user_input[1] == 0:
        code = CodeForLean.induction(var_name)
    elif user_input[1] == 1:
        code = CodeForLean.induction(var_name).and_then('rotate')

    return code


@add_to_proof_methods()
def method_sorry(proof_step,
                 selected_objects: [MathObject],
                 user_input=None) -> CodeForLean:
    """
    Close the current sub-goal by sending the 'sorry' code.
    """
    return CodeForLean.from_string('sorry')


# def introduce_new_subgoal(proof_step) -> CodeForLean:
#     selected_objects = proof_step.selection
#     user_input = proof_step.user_input
#     sub_goal = None
#     codes = CodeForLean()
#
#     # (A) Sub-goal from selection
#     if selected_objects:
#         premise = selected_objects[0].premise()
#         if premise:
#             # FIXME: make format_='lean' functional
#             sub_goal = premise.to_display(format_='lean')
#
#     # (B) User enter sub-goal
#     elif len(user_input) == 1:
#         output = new_properties
#         raise MissingParametersError(InputType.Text,
#                                      title=_("Introduce a new subgoal"),
#                                      output=output)
#     elif len(user_input) == 2:
#         sub_goal = pre_process_lean_code(user_input[1])
#
#     # (C) Code:
#     if sub_goal:
#         new_hypo_name = get_new_hyp(proof_step)
#         codes = CodeForLean.from_string(f"have {new_hypo_name}:"
#                                         f" ({sub_goal})")
#         codes.add_success_msg(_("New target will be added to the context "
#                                 "after being proved"))
#         codes.add_subgoal(sub_goal)
#
#     return codes


def introduce_fun(proof_step, selected_objects: [MathObject]) -> CodeForLean:
    """
    If a hypothesis of form ∀ a ∈ A, ∃ b ∈ B, P(a,b) has been previously
    selected: use the axiom of choice to introduce a new function f : A → B
    and add ∀ a ∈ A, P(a, f(a)) to the properties.
    """

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
                                       math_type=MathObject.NO_MATH_TYPE)

                hf = get_new_hyp(proof_step)
                name = proof_step.goal.provide_good_name(math_type)

                # f = give_global_name(math_type=math_type,
                #                      proof_step=proof_step)
                code = CodeForLean.from_string(f'cases '
                                               f'classical.axiom_of_choice '
                                               f'{h} with {name} {hf}, '
                                               f'dsimp at {hf}, '
                                               f'dsimp at {name}')
                code.add_error_msg(error)
                success = success.format(name, hf)
                code.add_success_msg(success)
                return code
    raise WrongUserInput(error)


@action()
def action_new_object(proof_step) -> CodeForLean:
    """
    Introduce new object / sub-goal / function
    """

    selected_objects = proof_step.selection
    # target_selected = proof_step.target_selected
    user_input = proof_step.user_input

    goal = proof_step.goal

    codes = CodeForLean()
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
    # (1) Choice = new object
    if user_input[0] == 0:
        if len(user_input) == 1:  # Ask for name
            raise MissingParametersError(InputType.Text,
                                         title="+",
                                         output=_("Give a name for your "
                                                  "new object:"))
        elif len(user_input) == 2:
            # Check name does not already exists
            name = pre_process_lean_code(user_input[1])
            names = [obj.display_name for obj in goal.context]
            if name in names:
                user_input.pop()
                output = _("This name already exists, please give a new name:")
                raise MissingParametersError(InputType.Text,
                                             title="+",
                                             output=output)
            else:  # Ask for new object
                # output = new_objects
                raise MissingParametersError(InputType.Calculator,
                                             title=_("Introduce a new object"),
                                             target=None)
                # raise MissingParametersError(InputType.Text,
                #                                  title=_("Introduce a new object"),
                #                                  output=output)
        else:  # Send code
            name = pre_process_lean_code(user_input[1])
            new_hypo_name = get_new_hyp(proof_step, name='Def')

            # Process object from auto_step or from Calculator:
            math_object = user_input[2]
            if isinstance(math_object, str):
                math_object = MathObject(node="RAW_LEAN_CODE",
                                         info={'name': '(' + math_object + ')'},
                                         children=[],
                                         math_type=None)

            new_object = math_object.to_display(format_='lean')
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

    # (2) Choice = new sub-goal
    elif user_input[0] == 1:
        codes = introduce_new_subgoal(proof_step)

    # (3) Choice = new function
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
