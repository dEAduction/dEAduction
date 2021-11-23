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
    """

    goal = proof_step.goal

    if len(selected_objects) == 0:
        if goal.target.math_type.node == "PROP_IMPLIES":
            code = CodeForLean.from_string("contrapose")
            code.add_success_msg(_("Target replaced by contrapositive"))
            return code
        else:
            error = _('Proof by contraposition only applies when target is '
                      'an implication')
    else:
        error = _('Proof by contraposition only applies to target')
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
                                         title=_("Introduce a new subgoal") ,
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
# APPLY #
#########

# def apply_function(proof_step, selected_objects: [MathObject]):
#     """
#     Apply l[-1], which is assumed to be a function f, to previous elements of
#     l, which can be:
#     - an equality
#     - an object x (then create the new object f(x) )
#
#     l should have length at least 2
#     """
#
#     log.debug('Applying function')
#     codes = CodeForLean.empty_code()
#
#     # let us check the input is indeed a function
#     function = selected_objects[-1]
#     # if function.math_type.node != "FUNCTION":
#     #    raise WrongUserInput
#
#     f = function.info["name"]
#     Y = selected_objects[-1].math_type.children[1]
#
#     while len(selected_objects) != 1:
#         new_h = get_new_hyp(proof_step)
#
#         # if function applied to a property, presumed to be an equality
#         if selected_objects[0].math_type.is_prop():
#             h = selected_objects[0].info["name"]
#             codes = codes.or_else(f'have {new_h} := congr_arg {f} {h}')
#             codes.add_success_msg(_("Function {} applied to {}").format(f, h))
#         # if function applied to element x:
#         # create new element y and new equality y=f(x)
#         else:
#             x = selected_objects[0].info["name"]
#             y = give_global_name(proof_step =proof_step,
#                                  math_type=Y,
#                                  hints=[Y.info["name"].lower()])
#             msg = _("New objet {} added to the context").format(y)
#             codes = codes.or_else(f'set {y} := {f} {x} with {new_h}',
#                                   success_msg=msg)
#         selected_objects = selected_objects[1:]
#
#     return codes
#
#
# @action()
# def action_apply(proof_step,
#                  selected_objects: [MathObject],
#                  user_input: [str],
#                  target_selected: bool = True):
#     """
#     Translate into string of lean code corresponding to the action
#     Function explain_how_to_apply should reflect the actions
#
#     Apply last selected item on the other selected
#
#     test for last selected item l[-1], and call functions accordingly:
#     - apply_function, if item is a function
#     - apply_susbtitute, if item can_be_used_for_substitution
#     ONLY if the option expanded_apply_button is set:
#     - apply_implicate, if item is an implication or a universal property
#         (or call action_forall if l[-1] is a universal property and none of
#         the other actions apply)
#     - apply_exists, if item is an existential property
#     - apply_and
#     - apply_or
#     ...
#     """
#
#     # fixme: rewrite to provide meaningful error msgs
#
#     if not selected_objects:
#         raise WrongUserInput(error=_("No property selected"))
#
#     # Now len(l) > 0
#
#     # (1)   If user wants to apply a function
#     #       (note this is exclusive of other types of applications)
#     # We successively try all selected objects
#     for i in range(len(selected_objects)-1):
#         prop = selected_objects[-1]  # property to be applied
#         if prop.is_function():
#             if len(selected_objects) == 1:
#                 # TODO: ask user for element on which to apply the function
#                 #   (plus new name, cf apply_forall)
#                 error = _("Select an element or an equality on which to "
#                           "apply the function")
#                 raise WrongUserInput(error=error)
#             else:
#                 return apply_function(proof_step, selected_objects)
#         # Put prop at index 0 and try again
#         prop = selected_objects.pop()
#         selected_objects.insert(0, prop)
#
#     codes = CodeForLean.empty_code()
#     error = ""
#     # Tha following has been replaced by the equal button
#     # (2) If rewriting is possible
#     # test, equality = prop.can_be_used_for_substitution()
#     # if test:
#     #     codes = codes.or_else(apply_substitute(proof_step,
#     #                                            selected_objects,
#     #                                            user_input,
#     #                                            equality))
#
#     expanded_apply_button = cvars.get('expanded_apply_button', False)
#     if expanded_apply_button:
#         # What follows applies only if expanded_apply_button
#         # (4) Other easy applications
#         if len(selected_objects) == 1 and user_can_apply(selected_objects[0]):
#             if prop.is_exists():
#                 codes = codes.or_else(apply_exists(proof_step,
#                                                    selected_objects))
#             if prop.is_and():
#                 codes = codes.or_else(apply_and(proof_step, selected_objects))
#             if prop.is_or():
#                 codes = codes.or_else(apply_or(proof_step,
#                                                selected_objects,
#                                                user_input))
#
#     if not codes.is_empty():
#         return codes
#     else:
#         error = _("I cannot apply this")  # fixme: be more precise
#         raise WrongUserInput(error)
#
#     # The following would allow to use the apply button instead of for_all
#     # or implicate
#     # # (3) If property is an implication (or a universal implication)
#     # if prop.can_be_used_for_implication() and len(l) == 1:
#     #     # Apply to the target
#     #     codes = codes.or_else(apply_implicate(proof_step, l))
#     # elif prop.is_implication() or prop.is_for_all():
#     #     if len(l) > 1:
#     #         # In this case implication and 'forall' are applied the same way
#     #         codes = codes.or_else(apply_implicate_to_hyp(proof_step, l))
#
#     # # Lastly, if nothing else but forall may be applied we do not know on what
#     # # to apply: ask user (as treated in action_forall)
#     # elif prop.is_for_all() and len(l) == 1:
#     #     return action_forall(proof_step, l, user_input)
#
#
# ################################
# # Captions for 'APPLY' buttons #
# ################################
#
# applicable_nodes = {'FUNCTION',  # to apply a function
#                     'PROP_EQUAL', 'PROP_IFF', 'QUANT_∀',  # for substitution
#                     'PROP_IMPLIES',
#                     # for obvious action:
#                     'QUANT_∃', 'QUANT_∃!', 'PROP_AND', 'PROP_OR'}


# def user_can_apply(math_object) -> bool:
#     """
#     True if math_object may be applied
#     (--> an 'APPLY' button may be created)
#     """
#     return math_object.math_type.node in applicable_nodes
#
#
# def explain_how_to_apply(math_object: MathObject, dynamic=False, long=False) \
#         -> str:
#     """
#     Provide explanations of how the math_object may be applied
#     (--> to serve as tooltip or help)
#     :param math_object:
#     :param dynamic: if False, caption depends only on main node
#     :param long: boolean
#     TODO: implement dynamic and long tooltips
#     """
#     captions = []  # default value
#
#     if math_object.is_function():
#         captions.append(tooltips.apply_tool_tip('tooltip_apply_function'))
#     # Substitution transfered to 'equal' button
#     # elif math_object.can_be_used_for_substitution()[0]:
#     #    captions.append(tooltips.get('tooltip_apply_substitute'))
#
#     return captions
#
#     #TODO: include this when extended apply button
#     # the following 4 cases are mutually exclusive
#     if math_object.is_function():
#         captions.append(tooltips.apply_tool_tip('tooltip_apply_function'))
#
#     elif math_object.is_for_all():
#         captions.append(tooltips.apply_tool_tip('tooltip_apply_for_all'))
#
#     elif math_object.is_exists():
#         captions.append(tooltips.apply_tool_tip('tooltip_apply_exists'))
#
#     elif math_object.is_and():
#         captions.append(tooltips.apply_tool_tip('tooltip_apply_and'))
#
#     # Additional line
#     if math_object.can_be_used_for_implication():
#         captions.append(tooltips.apply_tool_tip('tooltip_apply_implication'))
#
#     elif math_object.can_be_used_for_substitution()[0]:
#         captions.append(tooltips.apply_tool_tip('tooltip_apply_substitute'))
#
#     return captions

# TODO:
#  @action(_("Proof by induction"))
# def action_induction(proof_step, l : [MathObject]):
#    raise WrongUserInput


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
