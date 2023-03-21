"""
############################################################
# logic.py : functions to call in order to                 #
# translate actions into lean code                         #
############################################################
    
Every function action_* takes the following arguments:
- proof_step: the current proof_step, of class ProofStep, that contains
various informations about the current proof state
- selected_objects: a list of MathObject previously selected by the user
- target_selected: a boolean that indicates if target is selected.
If target_selected is False, (and the setting target_selected_by_default is
not on) then selected_objects must be non-empty.

Some of these functions take an optional argument:
- user_input, an object reflecting a choice made by the user inside a
previous call of the same function.

Most of these functions are just switches that call other more
specialised functions, according to the number and nature of
selected_objects. All these auxiliary functions occurs immediately before the
function action_* in the present file.

Author(s)     : - Marguerite Bin <bin.marguerite@gmail.com>
Maintainer(s) : - Marguerite Bin <bin.marguerite@gmail.com>
                - Frédéric Le Roux <frederic.le-rxou@imj-prg.fr>
Created       : July 2020 (creation)
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
from typing import Union, Optional

import deaduction.pylib.config.vars as cvars
from deaduction.pylib.math_display.display_data import new_objects

from deaduction.pylib.actions.utils import (add_type_indication,
                                            pre_process_lean_code)

from deaduction.pylib.actions.commun_actions import introduce_new_subgoal
from deaduction.pylib.actions     import (action,
                                          InputType,
                                          MissingParametersError,
                                          WrongUserInput,
                                          test_selection,
                                          CodeForLean)

from deaduction.pylib.mathobj     import  MathObject

from deaduction.pylib.give_name import    get_new_hyp

log = logging.getLogger("logic")
global _


def rw_with_defi(definition, object=None):
    defi = definition.lean_name
    if object:
        name = object.info['name']
        code = CodeForLean.from_string(f"rw {defi} at {name}")
    else:
        code = CodeForLean.from_string(f"rw {defi}")
    return code


#######
# AND #
#######

def construct_and(proof_step, user_input: [str]) -> CodeForLean:
    """
    Split the target 'P AND Q' into two sub-goals.
    Handle the case of an implicit "and", and the case of IFF.
    """
    target = proof_step.goal.target.math_type
    if target.is_iff(is_math_type=True):
        return construct_iff(proof_step, user_input)

    implicit_definition = None
    if not target.is_and(is_math_type=True, implicit=True):
        raise WrongUserInput(error=_("Target is not a conjunction 'P AND Q'"))

    if not target.is_and(is_math_type=True):
        # Implicit "and"
        implicit_definition = MathObject.last_used_implicit_definition
        target              = MathObject.last_rw_object

    children = target.children

    left = children[0]
    right = children[1]
    if not user_input:
        # User choice
        choices = [(_("Left"), left.to_display(format_="utf8")),
                   (_("Right"), right.to_display(format_="utf8"))]
        raise MissingParametersError(
            InputType.Choice,
            choices,
            title=_("Choose sub-goal"),
            output=_("Which property to prove first?"))
    else:
        if implicit_definition:
            code = rw_with_defi(implicit_definition)
        else:
            code = CodeForLean.empty_code()
        if user_input[0] == 1:
            # Prove second property first
            if target.node == "PROP_∃":
                # In this case, first rw target as a conjunction
                code = code.and_then("rw exists_prop")
            code = code.and_then("rw and.comm")
            left, right = right, left

        code = code.and_then("split")
        code.add_success_msg(_('Target split'))
        code.add_conjunction(target, left, right)
    return code


def apply_and(proof_step, selected_objects) -> CodeForLean:
    """
    Destruct a property 'P and Q'.
    Here selected_objects is assumed to contain exactly one conjunction
    property.
    """

    selected_hypo = selected_objects[0].info["name"]
    h1 = get_new_hyp(proof_step)
    h2 = get_new_hyp(proof_step)
    code = CodeForLean.from_string(f'cases {selected_hypo} with {h1} {h2}')
    code.add_success_msg(_("Split property {} into {} and {}").
                         format(selected_hypo, h1, h2))
    return code


def construct_and_hyp(proof_step, selected_objects: [MathObject]) \
                      -> CodeForLean:
    """
    Construct 'P AND Q' from properties P and Q.
    Here selected_objects is assumed to contain exactly two properties.
    """

    h1 = selected_objects[0].info["name"]
    h2 = selected_objects[1].info["name"]
    new_hypo_name = get_new_hyp(proof_step)
    code = f'have {new_hypo_name} := and.intro {h1} {h2}'
    code = CodeForLean.from_string(code)
    code = code.and_then(f"clear {h1}")
    code = code.and_then(f"clear {h2}")
    code.add_success_msg(_("Conjunction {} added to the context").
                         format(new_hypo_name))
    return code


@action()
def action_and(proof_step) -> CodeForLean:
    """
    Translate into string of lean code corresponding to the action

If the target is of the form P AND Q:
    transform the current goal into two subgoals, P, then Q.
If a hypothesis of the form P AND Q has been previously selected:
    creates two new hypothesis P, and Q.
If two hypothesis P, then Q, have been previously selected:
    add the new hypothesis P AND Q to the properties.
    """

    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected
    user_input = proof_step.user_input

    test_selection(selected_objects, target_selected)
    # goal = proof_step.goal

    if len(selected_objects) == 0:
        return construct_and(proof_step, user_input)
    if len(selected_objects) == 1:
        if not selected_objects[0].is_and(implicit=True):
            raise WrongUserInput(error=_("Selected property is not "
                                         "a conjunction 'P AND Q'"))
        else:
            return apply_and(proof_step, selected_objects)
    if len(selected_objects) == 2:
        if not (selected_objects[0].math_type.is_prop and
                selected_objects[1].math_type.is_prop):
            raise WrongUserInput(error=_("Selected items are not properties"))
        else:
            return construct_and_hyp(proof_step, selected_objects)
    raise WrongUserInput(error=_("Does not apply to more than two properties"))


######
# OR #
######

def construct_or(proof_step, user_input: [str]) -> CodeForLean:
    """
    Assuming target is a disjunction 'P OR Q', choose to prove either P or Q.
    Handle the case of an implicit "or".
    """
    target = proof_step.goal.target.math_type

    # Implicit definition ?
    if not target.is_or(is_math_type=True):
        # Implicit "or"
        # implicit_definition = MathObject.last_used_implicit_definition
        target = MathObject.last_rw_object

    children = target.children

    left = children[0].to_display(format_="utf8")
    right = children[1].to_display(format_="utf8")
    choices = [(_("Left"), left), (_("Right"), right)]

    if not user_input:
        raise MissingParametersError(InputType.Choice,
                                     choices,
                                     title=_("Choose new goal"),
                                     output=_("Which property will you "
                                              "prove?"))
    code = None
    if len(user_input) == 1:
        i = user_input[0]
        if i == 0:
            code = CodeForLean.from_string("left")
            code.add_success_msg(_("Target replaced by the left alternative"))
        else:
            code = CodeForLean.from_string("right")
            code.add_success_msg(_("Target replaced by the right alternative"))

    return code


def apply_or(proof_step,
             selected_objects: [MathObject],
             user_input: [str]) -> CodeForLean:
    """
    Assuming selected_objects is one disjunction 'P OR Q',
    engage in a proof by cases.
    Handle the case of an implicit "or".
    """

    selected_hypo = selected_objects[0]
    math_type = selected_hypo.math_type
    code = CodeForLean.empty_code()

    # Implicit definition ?
    implicit_definition = None
    if not selected_hypo.is_or(is_math_type=False):
        # Implicit "or"
        implicit_definition = MathObject.last_used_implicit_definition
        math_type = MathObject.last_rw_object

    children = math_type.children

    left = children[0]
    right = children[1]
    if not user_input:
        choices = [(_("Left"), left.to_display(format_="utf8")),
                   (_("Right"), right.to_display(format_="utf8"))]
        raise MissingParametersError(InputType.Choice,
                                     choices=choices,
                                     title=_("Choose case"),
                                     output=_("Which case to assume first?"))
    else:  # len(user_input) == 1
        if user_input[0] == 1:
            # If user wants the second property first, then first permute
            code_str = f'rw or.comm at {selected_hypo.info["name"]}'
            if implicit_definition:
                code = rw_with_defi(implicit_definition, selected_hypo)
                code = code.and_then(code_str)
            else:
                code = CodeForLean.from_string(code_str)
            left, right = right, left

    h1 = get_new_hyp(proof_step)
    h2 = get_new_hyp(proof_step)
    # Destruct the disjunction
    code = code.and_then(f'cases {selected_hypo.info["name"]} with {h1} {h2}')
    code.add_success_msg(_("Proof by cases"))
    code.add_disjunction(selected_hypo, left, right)

    return code


def construct_or_on_hyp(proof_step,
                        selected_property: [MathObject],
                        user_input: [str] = None) -> CodeForLean:
    """
    Construct a property 'P or Q' from property 'P' or property 'Q'.
    Here we assume selected_object contains 1 or 2 items.
    """
    if not user_input:
        user_input = []
    possible_codes = []
    first_hypo_name = selected_property[0].info["name"]
    # hypo = selected_property[0].math_type.to_display()

    if len(selected_property) == 2:
        if not (selected_property[0].math_type.is_prop()
                and selected_property[1].math_type.is_prop()):
            error = _("Selected items are not properties")
            raise WrongUserInput(error)
        else:
            second_selected_property = selected_property[1]
            second_name = second_selected_property.info["name"]
            second_lean_code = \
                second_selected_property.math_type.to_display(format_='lean')
    elif len(selected_property) == 1:
        if not selected_property[0].math_type.is_prop():
            error = _("Selected item is not a property")
            raise WrongUserInput(error)
        if not user_input:  # User has to choose 2nd property
            raise MissingParametersError(
                InputType.Text,
                title=_("Obtain 'P OR Q'"),
                output=_("Enter the property you want to use:"))
        else:
            second_name = user_input[0]
            second_lean_code = second_name
            user_input = user_input[1:]
        
    if not user_input:  # Usr still has to choose side
        raise MissingParametersError(
            InputType.Choice,
            [(_("Left"),
              f'({first_hypo_name}) OR ({second_name})'),
             (_('Right'),
              f'({second_name}) OR ({first_hypo_name})')],
            title=_("Choose side"),
            output=_(f'On which side do you want') + f' {first_hypo_name} ?')
    
    new_hypo_name = get_new_hyp(proof_step)
    # Mind Lean syntax: @or.inl P Q HP ; @or.inr P Q HQ
    if user_input[0] == 0:
        possible_codes.append(f'have {new_hypo_name} := '
                              f'@or.inl _ ({second_lean_code}) '
                              f'({first_hypo_name})')
    elif user_input[0] == 1:
        possible_codes.append(f'have {new_hypo_name} := '
                              f'@or.inr ({second_lean_code}) _ '
                              f'({first_hypo_name})')
    else:
        raise WrongUserInput("Unexpected error")
    code = CodeForLean.or_else_from_list(possible_codes)
    code.add_success_msg(_('Property {} added to the context').
                         format(new_hypo_name))
    return code
            

@action()
def action_or(proof_step) -> CodeForLean:
    """
    If the target is of the form P OR Q:
        transform the target in P (or Q) according to the user's choice.
    If a hypothesis of the form P OR Q has been previously selected:
        transform the current goal into two subgoals,
            one with P as a hypothesis,
            and another with Q as a hypothesis.
    """

    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected
    user_input = proof_step.user_input

    test_selection(selected_objects, target_selected)
    goal = proof_step.goal

    if len(selected_objects) == 0:
        if not goal.target.is_or(implicit=True):
            raise WrongUserInput(
                error=_("Target is not a disjunction 'P OR Q'"))
        else:
            return construct_or(proof_step, user_input)
    elif len(selected_objects) == 1:
        if selected_objects[0].is_or(implicit=True):
            return apply_or(proof_step, selected_objects, user_input)
        else:
            return construct_or_on_hyp(proof_step, selected_objects, user_input)
    elif len(selected_objects) == 2:
        return construct_or_on_hyp(proof_step, selected_objects, user_input)
    else:  # More than 2 selected objects
        raise WrongUserInput(error=_("Does not apply to more than two "
                                     "properties"))


#######
# NOT #
#######
@action()
def action_not(proof_step) -> CodeForLean:
    """
    Translate into string of lean code corresponding to the action
    
    If no hypothesis has been previously selected:
        transform the target in an equivalent one with its negations 'pushed'.
    If a hypothesis has been previously selected:
        do the same to the hypothesis.
    """

    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected
    # user_input = proof_step.user_input

    test_selection(selected_objects, target_selected)
    goal = proof_step.goal

    # (1) Push neg once on target
    if len(selected_objects) == 0:
        if not goal.target.first_pushable_body_of_neg():
            raise WrongUserInput(error=_("Negation cannot be pushed in target"))
        code = CodeForLean.from_string('push_neg_once')
        code.add_success_msg(_("Negation pushed on target"))
        # Add try_norm_num. This changes A≠B into ¬ (A=B)
        # which makes it possible, e.g., to unfold 'double inclusion'
        code = code.and_try_simp_only(lemmas='ne.def')

    # (2) Push neg once on one hypo
    elif len(selected_objects) == 1:
        if not selected_objects[0].first_pushable_body_of_neg():
            error = _("Negation cannot be pushed in selected property")
            raise WrongUserInput(error)
        selected_hypo = selected_objects[0].info["name"]
        code = CodeForLean.from_string(f'push_neg_once at {selected_hypo}')
        code.add_success_msg(_("Negation pushed on property {}").format(
            selected_hypo))
        code = code.and_try_simp_only(lemmas='ne.def',
                                      location=selected_hypo)

    else:
        raise WrongUserInput(error=_('Only one property at a time'))
    return code


###############
# IMPLICATION #
###############
def construct_implies(proof_step) -> CodeForLean:
    """
    Here the target is assumed to be an implication P ⇒ Q, P is added to the
    context, and the target becomes Q.
    """
    if not proof_step.goal.target.is_implication(implicit=True):
        raise WrongUserInput(error=_("Target is not an implication 'P ⇒ Q'"))
    else:
        new_hypo_name = get_new_hyp(proof_step)
        code = CodeForLean.from_string(f'intro {new_hypo_name}')
        code.add_success_msg(_("Property {} added to the context").
                             format(new_hypo_name))
        return code


def apply_implies(implication: [MathObject]) -> CodeForLean:
    """
    Here selected_object contains a single property which is an implication
    P ⇒ Q; if the target is Q then it will be replaced by P.
    """

    selected_name = implication.info["name"]
    code = CodeForLean.from_string(f'apply_with {selected_name} '
                                   '{md:=reducible}')
    code.add_success_msg(_("Target modified using implication {}").
                         format(selected_name))

    code.add_used_properties(implication)
    code.outcome_operator = implication

    return code


def have_new_property(arrow: MathObject,
                      variable_names: [str],
                      new_hypo_name: str,
                      success_msg=None) -> CodeForLean:
    """
    Compute Lean code to apply an implication or a universal property to a
    property or a variable.

    :param arrow:           a MathObject which is either an implication or a
                            universal property
    :param variable_names:  a list of names of variables (or properties) to
                            which "arrow" will be applied
    :param new_hypo_name:   a fresh name for the new property

    :param success_msg:     A success msg, if None then the standard one will be
                            used.

    return:                 Lean Code to produce the wanted new property,
                            taking into account implicit parameters
    """

    # TODO: add smart guess for placeholders, by matching math types
    #  May even try to guess parameters from the context
    #  (e.g. if we need a function and there is only one in the context)
    selected_hypo = arrow.info["name"]

    command = f'have {new_hypo_name} := {selected_hypo}'
    command_explicit = f'have {new_hypo_name} := @{selected_hypo}'

    arguments = ' '.join(variable_names)

    # try with up to 4 implicit parameters
    implicit_codes = [command + ' ' + arguments,
                      command + ' _ ' + arguments,
                      command + ' _ _ ' + arguments,
                      command + ' _ _ _ ' + arguments,
                      command + ' _ _ _ _ ' + arguments]

    explicit_codes = [command_explicit + ' ' + arguments,
                      command_explicit + ' _ ' + arguments,
                      command_explicit + ' _ _ ' + arguments,
                      command_explicit + ' _ _ _ ' + arguments,
                      command_explicit + ' _ _ _ _ ' + arguments]

    possible_codes = implicit_codes + explicit_codes

    code = CodeForLean.or_else_from_list(possible_codes)
    if success_msg is None:
        success_msg = _("Property {} added to the context").format(new_hypo_name)
    if success_msg:
        code.add_success_msg(success_msg)

    code.operator = arrow
    # code.add_used_properties(arrow)

    return code


def apply_implies_to_hyp(proof_step,
                         selected_objects: [MathObject]) -> CodeForLean:
    """
    Try to apply last selected property on the other ones.
    The last property should be an implication
    (or equivalent to such after unfolding definitions)
    """

    implication = selected_objects[-1]
    new_hypo_name = get_new_hyp(proof_step)
    variable_names = [variable.info['name'] for variable in
                      selected_objects[:-1]]

    code = have_new_property(implication, variable_names, new_hypo_name)
    code.add_used_properties(selected_objects)

    return code


def implies_hyp(proof_step):
    """
    This method is called when user press implies with exactly one selected
    hypothesis, which is an implication or a universal implication.
    """

    implication = proof_step.selection[0]
    # (0) Determine is implication is a universal implication, or a True
    #     implication (maybe implicit)
    universal_implication = False
    if not implication.is_implication(is_math_type=False, implicit=True):
        universal_implication = True
    else:
        # Implicit definition ?
        if not implication.is_implication(is_math_type=False):
            # Implicit implication
            implication = MathObject.last_rw_object

    target_selected = proof_step.target_selected
    user_input = proof_step.user_input
    goal = proof_step.goal

    # (1) 'It suffices to prove'?
    if target_selected:
        return apply_implies(implication)

    premise = implication.premise()
    # (2) Premise in context (but not selected)?
    #  or inaccessible premise (e.g. universal implication)
    if universal_implication \
            or not isinstance(premise, MathObject) \
            or premise in ([p.math_type for p in goal.context_props]
                           + [goal.target.math_type]):
        raise WrongUserInput(error=_("You need to select another property"
                                     "in order to apply this implication"))
    # (3) Ask to add premise as a new sub_goal
    elif not user_input:
        assert isinstance(premise, MathObject)
        raw_msg = _('To apply this property, you need the premise \"{}\". '
                    'Do you want to prove it?')
        msg = _(raw_msg).format(premise.to_display(format_='utf8'))
        raise MissingParametersError(
            InputType.YesNo,
            choices=[],
            title=_("Introduce new sub-goal?"),
            output=msg)
    # (4) Add premise as a new sub-goal
    elif user_input[0] == 0:  # Should always be the case here
        if premise and isinstance(premise, MathObject):
            return introduce_new_subgoal(proof_step, premise)
        else:
            error_msg = _("I do not know what to do")
            raise WrongUserInput(error_msg)


@action()
def action_implies(proof_step) -> CodeForLean:
    """
    Three cases:
    (1) No property selected:
        If the target is of the form P ⇒ Q: introduce the hypothesis P in
        the properties and transform the target into Q.
    (2) A single selected property, of the form P ⇒ Q, and the target is
    selected: if the target was Q, it is replaced by P. If the target is not
    selected, then usr is asked to prove the premise (new sub-goal).
    (3) Exactly two selected property, on of which is an implication P ⇒ Q
    and the other is P: Add Q to the context
    """

    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected
    user_input = proof_step.user_input

    test_selection(selected_objects, target_selected)
    goal = proof_step.goal

    if len(selected_objects) == 0:
        # Try to prove an implication
        if not goal.target.is_implication(implicit=True):
            raise WrongUserInput(
                error=_("Target is not an implication 'P ⇒ Q'"))
        else:
            return construct_implies(proof_step)
    elif len(selected_objects) == 1:
        # Try to apply an implication, but no other prop selected
        if not selected_objects[0].can_be_used_for_implication(implicit=True):
            raise WrongUserInput(
                error=_("Selected property is not an implication 'P ⇒ Q'"))
        else:
            return implies_hyp(proof_step)

    elif len(selected_objects) == 2:
        # Try to apply P ⇒ Q on P
        if not selected_objects[1].can_be_used_for_implication(implicit=True):
            if not selected_objects[0].can_be_used_for_implication(
                                                               implicit=True):
                raise WrongUserInput(error=_(
                    "Selected properties are not implications 'P ⇒ Q'"
                                            ))
            else:  # l[0] is an implication but not l[1]: permute
                selected_objects.reverse()
        return apply_implies_to_hyp(proof_step, selected_objects)
    # TODO: treat the case of more properties, including the possibility of
    #  P, Q and 'P and Q ⇒ R'
    else:
        raise WrongUserInput(error=_("Does not apply to more than two "
                                     "properties"))


#######
# IFF #
#######

def choose_substitution(equality0: MathObject, equality1: MathObject):
    """
    Ask usr to choose between using equality0 to substitute in equality1 or
    the converse. equality0, equality1 are assumed to be (universal)
    equalities or iff.
    """
    eq0 = equality0.to_display(format_="utf8")
    eq1 = equality1.to_display(format_="utf8")
    choice = _("Use for substitution in {}")
    choices = [(eq0, choice.format(eq1)),
               (eq1, choice.format(eq0))]
    raise MissingParametersError(
        InputType.Choice,
        choices,
        title=_("Precision of substitution"),
        output=_("Choose which equality to use for substitution"))


def construct_iff(proof_step, user_input: [str]) -> CodeForLean:
    """
    Assuming target is an iff, split into two implications.
    """

    target = proof_step.goal.target.math_type
    code = CodeForLean.empty_code()

    left = target.children[0]
    right = target.children[1]
    left_display = left.to_display(format_="utf8")
    right_display = right.to_display(format_="utf8")
    if not user_input:
        choices = [("⇒", f'({left_display}) ⇒ ({right_display})'),
                   ("⇐", f'({right_display}) ⇒ ({left_display})')]
        raise MissingParametersError(
            InputType.Choice,
            choices,
            title=_("Choose sub-goal"),
            output=_("Which implication to prove first?"))

    elif len(user_input) == 1:
        if user_input[0] == 1:
            code = CodeForLean.from_string("rw iff.comm")
            left, right = right, left
        code = code.and_then("split")
    else:
        raise WrongUserInput(error=_("Undocumented error"))
    code.add_success_msg(_("Iff split in two implications"))
    impl1 = MathObject(info={},
                       node="PROP_IMPLIES",
                       children = [left, right],
                       math_type=MathObject.PROP)
    impl2 = MathObject(info={},
                       node="PROP_IMPLIES",
                       children = [right, left],
                       math_type=MathObject.PROP)
    code.add_conjunction(target, impl1, impl2)
    return code


def destruct_iff(proof_step) -> CodeForLean:
    """
    Check if target is a conjunction of two implications (but not if these
    implications are logical inverses). If so, return code that builds the
    equivalent iff statement. If not, return None.
    """

    goal = proof_step.goal
    # code = None
    target = goal.target
    if target.is_and():
        left = target.math_type.children[0]
        right = target.math_type.children[1]
        if left.is_implication(is_math_type=True) \
                and right.is_implication(is_math_type=True):
            code = CodeForLean.from_string("apply iff_def.mp")
            code.add_success_msg(_("Target replaced by iff property"))
            error_msg = _("The first implication is not the converse of the "
                          "second one")
            code.add_error_msg(error_msg)
            return code
        else:
            error_msg = _("I do not know what to do")
            raise WrongUserInput(error_msg)


def destruct_iff_on_hyp(proof_step,
                        selected_objects: [MathObject]) -> CodeForLean:
    """
    Split a property 'P iff Q' into two implications.
    len(selected_objects) should be 1.
    """
    possible_codes = []
    hypo_name = selected_objects[0].info["name"]
    h1 = get_new_hyp(proof_step)
    h2 = get_new_hyp(proof_step)
    possible_codes.append(f'cases (iff_def.mp {hypo_name}) with {h1} {h2}')
    code = CodeForLean.or_else_from_list(possible_codes)
    code.add_success_msg(_("Property {} split into {} and {}").
                             format(hypo_name, h1, h2))
    return code


def construct_iff_on_hyp(proof_step,
                         selected_objects: [MathObject]) -> CodeForLean:
    """
    Construct property 'P iff Q' from both implications.
    len(selected_objects) should be 2.
    """

    new_hypo_name = get_new_hyp(proof_step)
    h1 = selected_objects[0].info["name"]
    h2 = selected_objects[1].info["name"]
    code_string = f'have {new_hypo_name} := iff.intro {h1} {h2}'
    code = CodeForLean.from_string(code_string)
    code.add_success_msg(_("Logical equivalence {} added to the context").
                             format(new_hypo_name))
    error_msg = _("The first implication is not the converse of the "
                  "second one")
    code.add_error_msg(error_msg)
    code.add_used_properties(selected_objects)
    return code


def rw_with_iff(rw_hyp: MathObject,
                on_hyp: Optional[MathObject] = None) -> CodeForLean:
    """
    Try to use rw_hyp, assumed to be a (universal) iff,
    to rewrite either on_hyp if any, or target.
    """

    # FIXME: rw target should appear on ProofTree when on_hyp is None.
    code1 = code_for_substitution(rw_hyp, old_term=None, new_term=None,
                                  on_hyp=on_hyp)
    code2 = code_for_substitution(rw_hyp, old_term=None, new_term=None,
                                  on_hyp=on_hyp, reverse=True)

    code = code1.or_else(code2)
    code.add_used_properties(rw_hyp)
    code.rw_item = rw_hyp
    return code


@action()
def action_iff(proof_step) -> CodeForLean:
    """
    Three cases:
    (1) No selected property:
        If the target is of the form P ⇔ Q:
            introduce two subgoals, P⇒Q, and Q⇒P.
        If target is of the form (P → Q) ∧ (Q → P):
            replace by P ↔ Q
    (2) 1 selected property
        - if an iff, and target not selected, split it
        - elif a universal iff, try to rw target,
    (3) 2 properties:
        - if one is a universal iff, try to rw the other,
        - if none is an iff but both are implications, try to obtain P ⇔ Q.
    """
    # TODO: a good part could be merged with action_equal,
    #  in particular add testing of direction of substitution for a
    #  non-universal iff.

    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected
    user_input = proof_step.user_input

    if user_input is None:
        user_input = []

    test_selection(selected_objects, target_selected)
    goal = proof_step.goal
    code = CodeForLean.empty_code()
    test_subst = [item.can_be_used_for_substitution()
                  for item in selected_objects]

    if len(selected_objects) == 0:
        if goal.target.math_type.node == "PROP_IFF":
            return construct_iff(proof_step, user_input)
        else:
            code = destruct_iff(proof_step)
            if code:
                return code
            else:
                error_msg = _("Target is not an iff property 'P ⇔ Q'")
                raise WrongUserInput(error=error_msg)

    if len(selected_objects) == 1:
        if selected_objects[0].is_iff() and not target_selected:
            more_code = destruct_iff_on_hyp(proof_step, selected_objects)
            code = code.or_else(more_code)
        else:
            [(test, eq)] = test_subst
            if test:  # 1st selected object can be used for substitution
                code = rw_with_iff(selected_objects[0])
            elif not selected_objects[0].is_iff():
                error = _("Selected property is not an iff property 'P ⇔ Q'")
                raise WrongUserInput(error)
        return code

    if len(selected_objects) == 2:
        [(test0, equality0), (test1, equality1)] = test_subst
        if test0 and test1:
            # Two iff: which one to use?
            if not user_input:
                choose_substitution(equality0, equality1)
            elif user_input[0] == 0:
                return rw_with_iff(selected_objects[0],
                                   on_hyp=selected_objects[1])
            else:
                return rw_with_iff(selected_objects[1],
                                   on_hyp=selected_objects[0])
        elif test0:
            return rw_with_iff(selected_objects[0],
                               on_hyp= selected_objects[1])
        elif test1:
            return rw_with_iff(selected_objects[1],
                               on_hyp= selected_objects[0])

        elif not (selected_objects[0].is_implication()
                  and selected_objects[1].is_implication()):
            error = _("Selected items should both be implications")
            raise WrongUserInput(error)
        else:
            return construct_iff_on_hyp(proof_step, selected_objects)

    raise WrongUserInput(error=_("Does not apply to more than two properties"))


###########
# FOR ALL #
###########

def construct_forall(proof_step) -> CodeForLean:
    """
    Here goal.target is assumed to be a universal property "∀ x:X, ...",
    and variable x is introduced.
    """

    goal = proof_step.goal
    math_object = goal.target.math_type

    possible_codes = CodeForLean.empty_code()
    implicit = not math_object.is_for_all(is_math_type=True, implicit=False)
    if implicit:
        # Implicit "for_all"
        implicit_definition = MathObject.last_used_implicit_definition
        math_object         = MathObject.last_rw_object
        possible_codes = rw_with_defi(implicit_definition)

    math_type: MathObject = math_object.bound_var_type
    bound_var = math_object.bound_var
    body = math_object.body
    # hints = []
    # strong_hint = None
    # if not implicit:  # or math_type.is_R():  # FIXME: experimental
    #     # hint = (variable.info.get('lean_name') if variable.is_unnamed() else
    #     #         variable.display_name)
    #     hint = bound_var.display_name
    #     if hint:  # and len(hint) == 1:
    #         hints = [hint]
    #         strong_hint = hint
    if math_type.node == "PRODUCT":
        # [math_type_1, math_type_2] = math_type.children
        # [x, y] = names_for_types(math_type.children, proof_step)
        # x = give_global_name(proof_step=proof_step, math_type=math_type_1)
        # y = give_global_name(proof_step=proof_step, math_type=math_type_2)
        # Find two DISTINCT good names!
        name_0 = proof_step.goal.provide_good_name(math_type.children[0])
        name_1 = proof_step.goal.provide_good_name(math_type.children[1],
                                                   local_names=[name_0])
        code = f'rintro ⟨ {name_0}, {name_1} ⟩'
        possible_codes = possible_codes.and_then(code)
        name = f"({name_0},{name_1})"
    else:
        name = proof_step.goal.provide_good_name(math_type,
                                                 bound_var.preferred_letter())
        # x = give_global_name(proof_step=proof_step,
        #                      math_type=math_type,
        #                      hints=hints,
        #                      strong_hint=strong_hint)
        possible_codes = possible_codes.and_then(f'intro {name}')
    possible_codes.add_success_msg(_("Object {} added to the context").
                                   format(name))

    if body.is_implication(is_math_type=True):
        # If math_object has the form
        # ∀ x:X, (x R ... ==> ...)
        # where R is some inequality relation
        # then introduce the inequality on top of x
        premise = body.children[0]  # children (2,0)
        if premise.is_inequality(is_math_type=True):
            # FIXME: rather use automatic actions
            h = get_new_hyp(proof_step)
            # Add and_then intro h
            possible_codes = possible_codes.and_then(f'intro {h}')

    return possible_codes


def inequality_from_pattern_matching(math_object: MathObject,
                                     variable: MathObject) -> MathObject:
    """
    Check if math_object.math_type has the form
    ∀ x:X, (x R ... ==> ...)
    where R is some inequality relation, and if this statement may be
    applied to variable. If so, return inequality with x replaced by variable
    """
    inequality = None
    if not math_object.is_for_all(implicit=True):
        return

    if not math_object.is_for_all(is_math_type=False):
        # Implicit "for all"
        math_object = MathObject.last_rw_object
    else:
        math_object = math_object.math_type

    math_type, var, body = math_object.children
    # NB: following line does not work because of coercions
    # if var.math_type == variable.math_type:
    if body.is_implication(is_math_type=True):
        premise = body.children[0]  # children (2,0)
        if (premise.is_inequality(is_math_type=True) and
                var == premise.children[0]):
            children = [variable, premise.children[1]]
            inequality = MathObject(node=premise.node,
                                    info={},
                                    children=children,
                                    math_type=premise.math_type)
    return inequality


# def simple_apply_forall(proof_step, selected_objects: [MathObject]) \
#                         -> CodeForLean:
#     """
#     Try to apply last selected property on the other ones.
#     The last property should be a universal property
#     (or equivalent to such after unfolding definitions)
#
#     selected_objects: list of MathObjects of length ≥ 2.
#     """
#     # FIXME: return error msg if user try to apply "forall x:X, P(x)"
#     #  to some object of wrong type (e.g. implication)
#     #  For the moment "forall x, P->Q" works with "P->Q" and button forall
#
#     universal_property = selected_objects[-1]  # The property to be applied
#     new_hypo_name = get_new_hyp(proof_step)
#     var_names = [var.info['name'] for var in selected_objects[:-1]]
#     code = have_new_property(universal_property, var_names, new_hypo_name)
#     code.add_success_msg(_("Property {} added to the context").
#                          format(new_hypo_name))
#     code.add_used_properties(selected_objects)
#
#     return code


# def apply_forall_with_ineq(proof_step, selected_objects: [MathObject]) -> \
#         CodeForLean:
#     """
#     Try to apply last selected property on the other ones.
#     The last property should be a universal property
#     (or equivalent to such after unfolding definitions)
#
#     selected_objects: list of MathObjects of length ≥ 2
#     """
#     # FIXME: return error msg if user try to apply "forall x:X, P(x)"
#     #  to some object of wrong type (e.g. implication)
#     #  For the moment "forall x, P->Q" works with "P->Q" and button forall
#
#     goal = proof_step.goal
#     universal_property = selected_objects[-1]  # The property to be applied
#     unsolved_inequality_counter = 0
#     # Variable_names will contain the list of variables and proofs of
#     # inequalities that will be passed to universal_property
#     variable_names = []
#     code = CodeForLean.empty_code()
#     used_inequalities = []
#     # for potential_var in selected_objects[:-1]:
#     # We consider only the first variable
#     potential_var = selected_objects[0]
#     # TODO: replace by pattern matching
#     # Check for "∀x>0" (and variations)
#     inequality = inequality_from_pattern_matching(universal_property,
#                                                   potential_var)
#     variable_names.append(potential_var.info['name'])
#     if inequality:
#         math_types = [p.math_type for p in goal.context]
#         if inequality in math_types:
#             # Check if inequality is in context:
#             index = math_types.index(inequality)
#             context_inequality = goal.context[index]
#             used_inequalities.append(context_inequality)
#             inequality_name = context_inequality.display_name
#             variable_names.append(inequality_name)
#         else:
#             # If not, assert inequality as a new goal:
#             inequality_name = get_new_hyp(proof_step)
#             variable_names.append(inequality_name)
#             unsolved_inequality_counter += 1
#             # Add type indication to the variable in inequality
#             math_type = inequality.children[1].math_type
#             # Variable is not used explicitly, but this affects inequality:
#             variable = inequality.children[0]
#             variable = add_type_indication(variable, math_type)
#             ineq_with_type = MathObject(node=inequality.node,
#                                         info=inequality.info,
#                                         children=[variable,
#                                                   inequality.children[1]],
#                                         math_type=inequality.math_type)
#             display_inequality = ineq_with_type.to_display(format_='lean')
#             # Code I: state corresponding inequality #
#             code = code.and_then(f"have {inequality_name}: "
#                                  f"{display_inequality}")
#             code = code.and_then("rotate")  # Back to main goal
#             used_inequalities.append(inequality_name)
#
#     # Code II: Apply universal_property, with no success_msg #
#     new_hypo_name = get_new_hyp(proof_step)
#     code = code.and_then(have_new_property(universal_property,
#                                            variable_names,
#                                            new_hypo_name,
#                                            success_msg=""))
#     if used_inequalities:
#         code.add_used_properties(used_inequalities)
#
#     # Code III: try to solve inequalities # e.g.:
#     #   iterate 2 { solve1 {try {norm_num at *}, try {compute_n 10}} <|>
#     #               rotate},   rotate,
#     if unsolved_inequality_counter:
#         assert unsolved_inequality_counter == 1
#         # Fixme: (1) no rotate if compute fails
#         #   (2) "Proof of intermediate subgoal" not appropriate...
#         # Back to first inequality:
#         more_code0 = CodeForLean.from_string(f"rotate {proof_step.nb_of_goals}")
#         more_code1 = CodeForLean.from_string("norm_num at *")
#         more_code1 = more_code1.try_()
#         more_code2 = CodeForLean.from_string("compute_n 10")
#         more_code2 = more_code2.try_()
#         # Try to solve1 inequality by norm_num, maybe followed by compute:
#         more_code = more_code0.and_then(
#             (more_code1.and_then(more_code2)).solve1())
#         more_code.add_success_msg(_("Property {} added to the context").
#                              format(new_hypo_name))
#         # # If it fails, rotate to next inequality
#         # # This has been suppressed!
#         # failing_code = CodeForLean.from_string(f"rotate "
#         #                                        f"{proof_step.nb_of_goals}")
#         # failing_code.add_success_msg(_("You have to check the inequality to "
#         #                                "get the desired property"))
#         # more_code = more_code.or_else(failing_code)
#         code = code.and_then(more_code)
#         # # Do this for all inequalities
#         # #   more_code = more_code.single_combinator(f"iterate
#         # #   {unsolved_inequality_counter}") --> replaced by explicit iteration
#         # code_list = [more_code] * unsolved_inequality_counter
#         # more_code = CodeForLean.and_then_from_list(code_list)
#         # Finally come back to first inequality??
#     if not unsolved_inequality_counter:
#         # Success msg when there is no inequality to solve:
#         code.add_success_msg(_("Property {} added to the context").
#                              format(new_hypo_name))
#     # In any case:
#     code.add_used_properties(selected_objects)
#
#     return code


def apply_forall_with_ineq(proof_step, selected_objects, inequality,
                           new_hypo_name=None) -> CodeForLean:
    """
    Try to apply last selected property, assumed to be a universal prop matching
    forall x, (some inex on x) ==> ...

    The inequality on x is the MathObject inequality.
    - If inequality belongs to the context, we apply the universal property
    to x and inequality
    - if not, we claim inequality, apply the universal property to it,
    and ask Lean to try to solve the inequality.
    """

    if not new_hypo_name:
        new_hypo_name = get_new_hyp()

    goal = proof_step.goal
    universal_property = selected_objects[-1]
    unsolved_inequality_counter = 0
    # Variable_names will contain the list of variables and proofs of
    # inequalities that will be passed to universal_property
    variable_names = []
    used_inequalities = []
    # Check for "∀x>0" (and variations)
    variable = inequality.children[0]
    variable_names.append(variable.name)
    math_types = [p.math_type for p in goal.context]
    code = CodeForLean.empty_code()

    # (1) Try to prove inequality
    if inequality in math_types:  # Check if inequality is in context
        ineq_in_ctxt = True
        index = math_types.index(inequality)
        context_inequality = goal.context[index]
        used_inequalities.append(context_inequality)
        inequality_name = context_inequality.display_name
        variable_names.append(inequality_name)
    else:
        ineq_in_ctxt = False
        # If not, assert inequality as a new goal:
        inequality_name = new_hypo_name
        variable_names.append(inequality_name)
        unsolved_inequality_counter += 1
        # Add type indication to the variable in inequality
        math_type = inequality.children[1].math_type
        # Variable is not used explicitly, but this affects inequality:
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
    variable_names.extend([var.name for var in selected_objects[1:-1]])
    if not ineq_in_ctxt:  # Hypo_name has been used
        new_hypo_name = get_new_hyp(proof_step)
    code = code.and_then(have_new_property(universal_property,
                                           variable_names,
                                           new_hypo_name,
                                           success_msg=""))
    if used_inequalities:
        code.add_used_properties(used_inequalities)

    # (3) try to solve inequalities # e.g.:
    #   iterate 2 { solve1 {try {norm_num at *}, try {compute_n 10}} <|>
    #               rotate},   rotate,
    if unsolved_inequality_counter:
        assert unsolved_inequality_counter == 1
        # Fixme: (1) no rotate if compute fails
        #   (2) "Proof of intermediate subgoal" not appropriate...
        # Back to first inequality:
        more_code0 = CodeForLean.from_string(f"rotate {proof_step.nb_of_goals}")
        more_code1 = CodeForLean.from_string("norm_num at *")
        more_code1 = more_code1.try_()
        more_code2 = CodeForLean.from_string("compute_n 10")
        more_code2 = more_code2.try_()
        # Try to solve1 inequality by norm_num, maybe followed by compute:
        more_code = more_code0.and_then(
            (more_code1.and_then(more_code2)).solve1())
        more_code.add_success_msg(_("Property {} added to the context").
                                  format(new_hypo_name))
        # # If it fails, rotate to next inequality
        # # This has been suppressed!
        # failing_code = CodeForLean.from_string(f"rotate "
        #                                        f"{proof_step.nb_of_goals}")
        # failing_code.add_success_msg(_("You have to check the inequality to "
        #                                "get the desired property"))
        # more_code = more_code.or_else(failing_code)
        code = code.and_then(more_code)
        # # Do this for all inequalities
        # #   more_code = more_code.single_combinator(f"iterate
        # #   {unsolved_inequality_counter}") --> replaced by explicit iteration
        # code_list = [more_code] * unsolved_inequality_counter
        # more_code = CodeForLean.and_then_from_list(code_list)
        # Finally come back to first inequality??
    if not unsolved_inequality_counter:
        # Success msg when there is no inequality to solve:
        code.add_success_msg(_("Property {} added to the context").
                             format(new_hypo_name))
    # In any case:
    code.add_used_properties(selected_objects)

    return code


def apply_forall(proof_step, selected_objects: [MathObject]) \
                        -> CodeForLean:
    """
    Try to apply last selected property on the other ones.
    The last property should be a universal property
    (or equivalent to such after unfolding definitions)

    selected_objects: list of MathObjects of length ≥ 2.
    """
    # FIXME: return error msg if user try to apply "forall x:X, P(x)"
    #  to some object of wrong type (e.g. implication)
    #  For the moment "forall x, P->Q" works with "P->Q" and button forall

    universal_property = selected_objects[-1]  # The property to be applied
    potential_var = selected_objects[0]

    new_hypo_name = get_new_hyp(proof_step)
    var_names = [var.info['name'] for var in selected_objects[:-1]]
    simple_code = have_new_property(universal_property, var_names,
                                    new_hypo_name)
    simple_code.add_success_msg(_("Property {} added to the context").
                         format(new_hypo_name))
    simple_code.add_used_properties(selected_objects)

    inequality = inequality_from_pattern_matching(universal_property,
                                                  potential_var)

    # (Case 1) No inequality to solve
    if not inequality or not cvars.get(
        "functionality.auto_solve_inequalities_in_bounded_quantification",
            False):
        return simple_code

    # (Cas 2) Inequality: try to solve it, turn to simple code if it fails
    else:
        complex_code = apply_forall_with_ineq(proof_step, selected_objects,
                                              inequality, new_hypo_name)
        code = complex_code.or_else(simple_code)
        return code


@action()
def action_forall(proof_step) -> CodeForLean:
    """
    (1) If no selection and target is of the form ∀ x, P(x):
        introduce x and transform the target into P(x)
    (2) If a single universal property is selected, ask user for an object
        to which the property will be applied
    (3) If 2 or more items are selected, one of which is a universal
        property, try to apply it to the other selected items

    """

    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected
    user_input = proof_step.user_input

    test_selection(selected_objects, target_selected)
    goal = proof_step.goal

    # selection_object_added = False

    if len(selected_objects) == 0:
        if not goal.target.is_for_all(implicit=True):
            error = _("Target is not a universal property '∀x, P(x)'")
            raise WrongUserInput(error)
        else:
            return construct_forall(proof_step)

    elif len(selected_objects) == 1:  # Ask user for item
        if not selected_objects[0].is_for_all(implicit=True):
            error = _("Selected property is not a universal property '∀x, "
                      "P(x)'")
            raise WrongUserInput(error)
        elif not user_input:
            raise MissingParametersError(InputType.Text,
                                         title=_("Apply a universal property"),
                                         output=_(
                                             "Enter element on which you "
                                             "want to apply:"))
        else:
            item = pre_process_lean_code(user_input[0])
            item = add_type_indication(item)  # e.g. (0:ℝ)
            if item[0] != '(':
                item = '(' + item + ')'
            potential_var = MathObject(node="LOCAL_CONSTANT",
                                       info={'name': item, 'user_input': True},
                                       children=[],
                                       math_type=None)
            selected_objects.insert(0, potential_var)
            # selection_object_added = True
            # Now len(l) == 2

    # From now on len(l) ≥ 2
    # Search for a universal property among l, beginning with last item
    selected_objects.reverse()
    for item in selected_objects:
        if item.is_for_all(implicit=True):
            # Put universal property in last position
            selected_objects.remove(item)
            selected_objects.reverse()
            selected_objects.append(item)
            code = apply_forall(proof_step, selected_objects)
            # if selection_object_added:  # Remove it (for auto-test)
            #     selected_objects.pop(0)
            return code
    raise WrongUserInput(error=_("No universal property among selected"))


##########
# EXISTS #
##########

def construct_exists(proof_step, user_input: [str]) -> CodeForLean:
    """
    Assuming the target is an existential property '∃ x, P(x)', prove it by
    providing a witness x and proving P(x).
    """

    if not user_input:
        output = _("Enter element you want to use:") + "\n \n \n" + new_objects
        raise MissingParametersError(InputType.Text,
                                     title=_("Exist"),
                                     output=output)
    x = pre_process_lean_code(str(user_input[0]))
    code = CodeForLean.from_string(f'use {x}')  # (f'use {x}, dsimp')
    # code = code.or_else(f'use {x}')
    code.add_success_msg(_("Now prove {} suits our needs").format(x))
    return code


def apply_exists(proof_step, selected_object: [MathObject]) -> CodeForLean:
    """
    Apply a property '∃ x, P(x)' to get an x with property P(x).
    Assume selected_object[0] is an existence property.
    """
    selected_hypo = selected_object[0].math_type
    hypo_name = selected_object[0].info["name"]

    if not selected_hypo.is_exists(is_math_type=True):
        # Implicit "exists"
        # implicit_definition = MathObject.last_used_implicit_definition
        selected_hypo       = MathObject.last_rw_object

    # hint = selected_hypo.children[1].display_name
    math_type = selected_hypo.bound_var_type
    bound_var = selected_hypo.bound_var    # "NOT(APP(CST?,...))": ((0, -1), r'\text_is_not', (0, 0)),

    name = proof_step.goal.provide_good_name(math_type,
                                             bound_var.preferred_letter())

    # x = give_global_name(proof_step=proof_step,
    #                      math_type=selected_hypo.children[0],
    #                      hints=[hint],
    #                      strong_hint=hint)
    new_hypo_name1 = get_new_hyp(proof_step)
    new_hypo_name2 = get_new_hyp(proof_step)

    if selected_hypo.children[2].node == "PROP_∃":
        code = f'rcases {hypo_name} with ' \
                f'⟨ {name}, ⟨ {new_hypo_name1}, {new_hypo_name2} ⟩ ⟩'
    else:
        code = f'cases {hypo_name} with {name} {new_hypo_name1}'
    code = CodeForLean.from_string(code)
    if selected_hypo.node == 'QUANT_∃!':
        # We have to add the "simp" tactic to avoid appearance of lambda expr
        code = code.and_then(f'simp at {new_hypo_name1}')
    code.add_success_msg(_("New object {} with property {}").
                         format(name, new_hypo_name1))
    code.operator = selected_object[0]
    return code


def construct_exists_on_hyp(proof_step,
                            selected_objects: [MathObject]) -> CodeForLean:
    """
    Try to construct an existence property from some object and some property
    Here len(l) = 2
    """

    x = selected_objects[0].info["name"]
    hx = selected_objects[1].info["name"]
    if (not selected_objects[0].math_type.is_prop()) \
            and selected_objects[1].math_type.is_prop():
        new_hypo = get_new_hyp(proof_step)
        code_string = f'have {new_hypo} := exists.intro {x} {hx}'
    elif (not selected_objects[1].math_type.is_prop()) \
            and selected_objects[0].math_type.is_prop():
        x, hx = hx, x
        new_hypo = get_new_hyp(proof_step)
        code_string = f'have {new_hypo} := exists.intro {x} {hx}'
    else:
        error = _("I cannot build an existential property with this")
        raise WrongUserInput(error)
    code = CodeForLean.from_string(code_string)
    code.add_success_msg(_("Get new existential property {}").format(
                           new_hypo))

    code.add_used_properties(selected_objects)

    return code


@action()
def action_exists(proof_step) -> CodeForLean:
    """
    Three cases:
    (1) If target is of form ∃ x, P(x):
        - if no selection, ask the user to enter a witness x and transform
        the target into P(x).
        - if some selection, use it as a witness for existence.
    (2) If a hypothesis of form ∃ x, P(x) has been previously selected:
        introduce a new x and add P(x) to the properties.
    (3) If some 'x' and a property P(x) have been selected:
        get property '∃ x, P(x)'
    """

    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected
    user_input = proof_step.user_input

    test_selection(selected_objects, target_selected)
    goal = proof_step.goal

    if len(selected_objects) == 0:
        if not goal.target.is_exists(implicit=True):
            error = _("Target is not existential property '∃x, P(x)'")
            raise WrongUserInput(error)
        else:
            return construct_exists(proof_step, user_input)
    elif len(selected_objects) == 1 and not user_input:
        selected_hypo = selected_objects[0]
        if selected_hypo.math_type.is_prop():
            # Try to apply property "exists x, P(x)" to get a new MathObject x
            if not selected_hypo.is_exists(implicit=True):
                error = _("Selection is not existential property '∃x, P(x)'")
                raise WrongUserInput(error)
            else:
                return apply_exists(proof_step, selected_objects)
        else:  # h_selected is not a property : get an existence property
            if not goal.target.is_exists(implicit=True):
                error = _("Target is not existential property '∃x, P(x)'")
                raise WrongUserInput(error)
            else:
                object_name = selected_objects[0].info["name"]
                return construct_exists(proof_step, [object_name])
    elif len(selected_objects) == 2:
        return construct_exists_on_hyp(proof_step, selected_objects)
    raise WrongUserInput(error=_("Does not apply to more than two properties"))


#########
# EQUAL #
#########
def code_for_substitution(rw_hyp: MathObject,
                          old_term: str = None, new_term: str = None,
                          on_hyp: Optional[MathObject] = None,
                          reverse=False) -> CodeForLean:
    """
    Return code for using rw_hyp to substitute in on_hyp
    (or in target if on_hyp=None),
    in reverse direction if reverse=True.
    Success msg will display "old_term" replaced by "new_term".
    """
    rw_hyp_name = rw_hyp.info['name']
    on_hyp_name = on_hyp.info['name'] if on_hyp else _("the target")

    success_msg = _("{} replaced by {}").format(old_term, new_term) \
        if old_term and new_term else \
        _("Substitution using {}").format(rw_hyp_name)
    success_msg += " " + _("in {}").format(on_hyp_name)
    error_msg = _("Unable to substitute {} by {}").format(old_term, new_term) \
    if old_term and new_term else _("Unable to use {} to substitute in {}"
                                    ).format(rw_hyp_name, on_hyp_name)

    reverse_code = " <- " if reverse else " "
    rw_code = "rw" + reverse_code + "{}"
    used_hyp = [rw_hyp]
    if on_hyp:
        used_hyp.append(on_hyp)
        rw_code += " at {}"

    simp_rw_code = "simp_" + rw_code
    # Replace hyp by their names:
    used_hyp = [hyp.info["name"] for hyp in used_hyp]
    code_strings = [rw_code.format(*used_hyp), simp_rw_code.format(*used_hyp)]
    code = CodeForLean.or_else_from_list(code_strings)
    code.add_success_msg(success_msg)
    code.add_error_msg(error_msg)

    code.add_used_properties(rw_hyp)
    code.rw_item = rw_hyp
    return code


def apply_substitute(proof_step,
                     selected_objects: [MathObject],
                     user_input: [int],
                     equality: MathObject,
                     equality_nb=-1,
                     direction_nb=0) -> CodeForLean:
    """
    Try to use the selected property indicated by equality_nb to rewrite the
    goal or the other selected property:
    - if there is exactly 1 selected property, rewrite the goal,
    - if there are exactly 2 selected properties, rewrite the 1st one with
    the equality contained in the second one.

    In both cases, ask for the direction of rewriting if there is an ambiguity.
    If no ambiguity is detected, successively try both directions.
    """

    goal = proof_step.goal

    codes = CodeForLean.empty_code()
    heq = selected_objects[equality_nb]  # Property to be used for substitution

    left: MathObject = equality.children[0]
    right: MathObject = equality.children[1]
    left_display = left.to_display(format_="utf8")
    right_display = right.to_display(format_="utf8")
    choices = [(left_display, f'Replace by {right_display}'),
               (right_display, f'Replace by {left_display}')]

    if len(selected_objects) == 1:  # Substitution on target
        if len(user_input) > 0:  # Choice of direction has been made
            if user_input[0] == 0:  # Direct substitution
                more_code = code_for_substitution(heq,
                                                  left_display, right_display)
            elif user_input[0] == 1:  # Reverse substitution
                more_code = code_for_substitution(heq,
                                                  right_display, left_display,
                                                  reverse=True)
            codes = codes.or_else(more_code)
        else:  # Choice of substitution direction has not been made
            if goal.target.math_type.contains(left) and \
                    goal.target.math_type.contains(right):
                # Choice needed
                raise MissingParametersError(
                    InputType.Choice,
                    choices,
                    title=_("Precision of substitution"),
                    output=_("Choose which expression you want to replace"))
            else:  # Try both direction
                more_code1 = code_for_substitution(heq,
                                                   left_display, right_display)
                more_code2 = code_for_substitution(heq,
                                                   right_display, left_display,
                                                   reverse=True)
                codes = more_code1.or_else(more_code2)

    if len(selected_objects) == 2:  # Substitution on context
        prop_nb = 0 if equality_nb != 0 else 1
        prop = selected_objects[prop_nb]  # Substitute in prop
        if len(user_input) > direction_nb:  # Choice of direction has been made
            if user_input[direction_nb] == 0:  # Direct substitution
                more_code = code_for_substitution(heq,
                                                  left_display, right_display,
                                                  on_hyp=prop)
                codes = codes.or_else(more_code)
            elif user_input[direction_nb] == 1:  # Reverse substitution
                more_code = code_for_substitution(heq,
                                                  right_display, left_display,
                                                  on_hyp=prop,
                                                  reverse=True)
                codes = codes.or_else(more_code)
        else:
            if prop.math_type.contains(left) and \
                    prop.math_type.contains(right):  # Both directions work
                raise MissingParametersError(
                    InputType.Choice,
                    choices,
                    title=_("Precision of substitution"),
                    output=_("Choose which expression you want to replace"))

            else:
                more_code1 = code_for_substitution(heq,
                                                   left_display, right_display,
                                                   on_hyp=prop)
                more_code2 = code_for_substitution(heq,
                                                   right_display, left_display,
                                                   on_hyp=prop,
                                                   reverse=True)
                codes = codes.or_else(more_code1)
                codes = codes.or_else(more_code2)

    if heq.is_for_all():
        # if property is, e.g. "∀n, u n = c"
        # there is a risk of meta vars if Lean does not know to which n
        # apply the equality
        codes = codes.and_then('no_meta_vars')

    return codes


@action()
def action_equal(proof_step) -> CodeForLean:
    """
    Try to use one of the selected properties for substitution in the goal
    (in case only one property has been selected) or in the second one.
    As of now, work also with iff.
    TODO: implement iff substitution with iff button rather than equal
        button
    """

    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected
    target = proof_step.goal.target
    user_input = proof_step.user_input

    if user_input is None:
        user_input = []

    equality_nb = -1  # Default nb of property to be used for substitution
    direction_nb = 0  # Default user_input index for direction (no choice of eq)

    if proof_step.drag_n_drop:
        # Replace selected_objects so that operator is at end
        d_n_d = proof_step.drag_n_drop
        selected_objects = [d_n_d.premise, d_n_d.operator]
        equality = d_n_d.operator.math_type
    elif not selected_objects:
        if not target_selected:
            msg = _("Select an equality to perform a substitution")
        else:
            if target.is_set_equality():
                msg = _("To prove an equality between sets, use the relevant "
                        "definitions, not the = button")
            else:
                msg = _("Select an equality from the context to perform a "
                        "substitution")
        raise WrongUserInput(error=msg)

    # Now len(l) > 0
    elif len(selected_objects) > 2:
        raise WrongUserInput(error=_("Too many selected objects"))

    # Try all properties for substitution
    elif len(selected_objects) == 2:
        prop0, prop1 = selected_objects[0], selected_objects[1]
        test0, equality0 = prop0.can_be_used_for_substitution()
        test1, equality1 = prop1.can_be_used_for_substitution()
        if test0 and test1:
            # Two equalities: which one to use?
            if not user_input:
                choose_substitution(equality0, equality1)
            else:
                direction_nb = 1
                if user_input[0] == 0:
                    equality = equality0
                    equality_nb = 0
                else:
                    equality = equality1
        elif test0:
            equality = equality0
            selected_objects.reverse()
            # if not user_input:
            #     user_input.append(0)  # Make place for a potential second input
            # else:
            #     user_input[0] = 0
        elif test1:
            equality = equality1
            # if not user_input:
            #     user_input.append(1)
            # else:
            #     user_input[0] = 1
        else:  # No equality found
            error = _("This cannot be used for substitution")
            raise WrongUserInput(error)

    elif len(selected_objects) == 1:
        prop = selected_objects[0]
        test, equality = prop.can_be_used_for_substitution()
        if not test:
            error = _("This cannot be used for substitution")
            raise WrongUserInput(error)

    codes = apply_substitute(proof_step, selected_objects, user_input,
                             equality, equality_nb, direction_nb)
    return codes


def apply_map_to_element(proof_step,
                         map_: MathObject,
                         var_name: str,
                         other_names=None):
    """
    Return Lean code to apply map_ to element.
    Element may be a MathObject (selected by user)
    or a string (as a result of a WrongUserInput exception).

    other_names is a list of names that are not available, the name of the
    new element will be added.
    """

    if other_names is None:
        other_names = []
    map_name = map_.info["name"]
    # if isinstance(element, MathObject):
    #     x = element.info["name"]
    # elif isinstance(element, str):
    image_set = map_.math_type.children[1]
    name = proof_step.goal.provide_good_name(image_set,
                                             local_names=other_names)
    other_names.extend(name)
    # y = give_global_name(proof_step=proof_step,
    #                      math_type=image_set,
    #                      hints=[image_set.info["name"]])

    new_h = get_new_hyp(proof_step)
    msg = _("New objet {} added to the context").format(name)
    # code = CodeForLean.from_string(f"set {name} := {f} {x} with {new_h}",
    #                                success_msg=msg)
    codes = CodeForLean.from_string(f"let {name} := {map_name} {var_name}")
    codes = codes.and_then(f"have {new_h} : {name} = {map_name} {var_name}")
    codes = codes.and_then("refl")
    codes.operator = map_
    codes.success_msg = msg
    return codes


def apply_function(proof_step, map_, arguments: [MathObject]):
    """
    Apply map_, which is assumed to be a map f,
    to arguments, which can be:
        - equalities
        - objects x (then create the new object f(x) )

    arguments MUST have length at least 1.
    """

    codes = CodeForLean.empty_code()
    f = map_.info["name"]

    other_names = []
    while arguments:

        if arguments[0].math_type.is_prop():
            # Function applied to a property, presumed to be an equality
            h = arguments[0].info["name"]
            new_h = get_new_hyp(proof_step)
            other_names.extend(new_h)
            codes = codes.and_then(f'have {new_h} := congr_arg {f} {h}')
            codes.add_success_msg(_("Map {} applied to {}").format(f, h))
            codes.add_used_properties(arguments[0])
        else:
            # Function applied to element x:
            #   create new element y and new equality y=f(x)
            x = arguments[0].info["name"]
            codes = codes.and_then(apply_map_to_element(proof_step,
                                                        map_,
                                                        x,
                                                        other_names))
        arguments = arguments[1:]
    msg = (_("The map {} cannot be applied to this object").format(f)
           if len(arguments) == 1 else
           _("The map {} cannot be applied to these objects").format(f))
    codes.add_error_msg(msg)
    codes.operator = map_
    return codes


@action()
def action_map(proof_step) -> CodeForLean:
    """
    Apply a function, which must be one of the selected object,
    to an element or an equality.
    - If no function is selected, rise a WrongUserInput exception
    - If a function but no other object is selected, rise a
    MissingParameterError exception.

    (Previously action_apply).
    """

    selected_objects = proof_step.selection
    # target_selected = proof_step.target_selected
    user_input = proof_step.user_input

    # We successively try all selected objects
    for i in range(len(selected_objects)):
        math_object = selected_objects[i]
        if math_object.is_function():
            if len(selected_objects) == 1:
                # A function, but no other object:
                if not user_input:
                    name = math_object.display_name
                    output = _("Enter element on which you want to apply "
                               "the map {}:").format(name)
                    raise MissingParametersError(InputType.Text,
                                                 title=_("Map"),
                                                 output=output)
                else:
                    # Apply function to user input:
                    x = user_input[0]
                    code = apply_map_to_element(proof_step,
                                                map_=math_object,
                                                var_name=x)

                    return code
            else:
                arguments = selected_objects[:i] + selected_objects[i+1:]
                return apply_function(proof_step,
                                      map_=math_object,
                                      arguments=arguments)

    error = _("Select an application and an element or an equality")
    raise WrongUserInput(error=error)


