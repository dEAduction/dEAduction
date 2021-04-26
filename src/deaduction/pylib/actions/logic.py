"""
############################################################
# logic.py : functions to call in order to                 #
# translate actions into lean code                         #
############################################################
    
Every function action_* takes the following arguments:
- goal: the current goal, of class Goal
- selected_objects: a list of MathObject previously selected by the user
- target_selected: a boolean that indicates if target is selected.
The following alternative is assumed:
either target_selected is True,
or selected_objects is non empty.

Some of these functions take an optional argument:
- user_input, an object reflecting a choice made by the user inside a
previous call of the same function.

Most of these functions are just switches that call other more
specialised functions, according to the number and nature of
selected_objects. All these auxiliary functions occurs immmediately before the
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
from typing import Union

from deaduction.pylib.text        import tooltips
from deaduction.pylib.config.i18n import _
from deaduction.pylib.actions     import (action,
                                          InputType,
                                          MissingParametersError,
                                          WrongUserInput,
                                          test_selection,
                                          CodeForLean
                                          )

from deaduction.pylib.mathobj     import (MathObject,
                                          Goal,
                                          give_global_name,
                                          get_new_hyp,
                                          NUMBER_SETS_LIST)

import deaduction.pylib.config.vars as cvars

log = logging.getLogger("logic")


# Get buttons symbols from config file
action_list = ['action_and', 'action_or', 'action_negate',
               'action_implicate', 'action_iff', 'action_forall',
               'action_exists']

if cvars.get('display.use_logic_button_symbols'):
    logic_button_texts = cvars.get('display.logic_button_symbols')
else:
    logic_button_texts = tooltips.get('logic_button_texts')
# Turn logic_button_texts into a dictionary
lbt = logic_button_texts.split(', ')
logic_button_texts = {}
for key, value in zip(action_list, lbt):
    logic_button_texts[key] = value


#######
# AND #
#######

def construct_and(proof_step, user_input: [str]) -> CodeForLean:
    """
    Split the target 'P AND Q' into two sub-goals.
    """
    goal = proof_step.goal

    if not goal.target.is_and():
        raise WrongUserInput(error=_("target is not a conjunction 'P AND Q'"))

    if not user_input:
        # User choice
        left = goal.target.math_type.children[0].to_display()
        right = goal.target.math_type.children[1].to_display()
        choices = [(_("Left"), left), (_("Right"), right)]
        raise MissingParametersError(
            InputType.Choice,
            choices,
            title=_("Choose sub-goal"),
            output=_("Which property to prove first?"))
    else:
        if user_input[0] == 1:
            # Prove second property first
            if goal.target.math_type.node == "PROP_∃":
                # In this case, first rw target as a conjunction
                code = CodeForLean.and_then_from_list(["rw exists_prop",
                                                       "rw and.comm"])
            else:
                code = CodeForLean.from_string("rw and.comm")
        else:
            code = CodeForLean.empty_code()
        code = code.and_then("split")
        code.add_success_msg(_('Let us prove the first property'))
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
    code.add_success_msg(_("split properties {} and {}").
                         format(h1, h2))
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
    code.add_success_msg(_("conjunction {} added to the context").
                         format(new_hypo_name))
    return code


@action(tooltips.get('tooltip_and'),
        logic_button_texts['action_and'])
def action_and(proof_step,
               selected_objects: [MathObject],
               user_input: [str] = None,
               target_selected: bool = True
               ) -> CodeForLean:
    """
    Translate into string of lean code corresponding to the action

If the target is of the form P AND Q:
    transform the current goal into two subgoals, P, then Q.
If a hypothesis of the form P AND Q has been previously selected:
    creates two new hypothesis P, and Q.
If two hypothesis P, then Q, have been previously selected:
    add the new hypothesis P AND Q to the properties.
    """

    test_selection(selected_objects, target_selected)
    goal = proof_step.goal

    if len(selected_objects) == 0:
        return construct_and(proof_step, user_input)
    if len(selected_objects) == 1:
        if not selected_objects[0].is_and():
            raise WrongUserInput(error=_("selected property is not "
                                         "a conjunction 'P AND Q'"))
        else:
            return apply_and(proof_step, selected_objects)
    if len(selected_objects) == 2:
        if not (selected_objects[0].math_type.is_prop and
                selected_objects[1].math_type.is_prop):
            raise WrongUserInput(error=_("selected items are not properties"))
        else:
            return construct_and_hyp(proof_step, selected_objects)
    raise WrongUserInput(error=_("does not apply to more than two properties"))


######
# OR #
######

def construct_or(proof_step, user_input: [str]) -> CodeForLean:
    """
    Assuming target is a disjunction 'P OR Q', choose to prove either P or Q.
    """
    goal = proof_step.goal

    left = goal.target.math_type.children[0].to_display()
    right = goal.target.math_type.children[1].to_display()
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
        if i==0:
            code = CodeForLean.from_string("left")
            code.add_success_msg(_("target replaced by the left alternative"))
        else:
            code = CodeForLean.from_string("right")
            code.add_success_msg(_("target replaced by the right alternative"))

    return code


def apply_or(proof_step,
             selected_objects: [MathObject],
             user_input: [str]) -> CodeForLean:
    """
    Assuming selected_objects is one disjunction 'P OR Q',
    engage in a proof by cases.
    """

    # if not selected_objects[0].is_or():
    #     raise WrongUserInput(error=_("Selected property is not "
    #                                  "a disjunction 'P OR Q'"))

    selected_hypo = selected_objects[0].info["name"]
    code = CodeForLean.empty_code()

    if not user_input:
        left = selected_objects[0].math_type.children[0].to_display()
        right = selected_objects[0].math_type.children[1].to_display()
        choices = [(_("Left"), left), (_("Right"), right)]
        raise MissingParametersError(InputType.Choice,
                                     choices=choices,
                                     title=_("Choose case"),
                                     output=_("Which case to assume first?"))
    else:  # len(user_input) == 1
        if user_input[0] == 1:
            # If user wants the second property first, then first permute
            code = f'rw or.comm at {selected_hypo}'
            code = CodeForLean.from_string(code)

    h1 = get_new_hyp(proof_step)
    h2 = get_new_hyp(proof_step)
    # Destruct the disjunction
    code = code.and_then(f'cases {selected_hypo} with {h1} {h2}')
    code.add_success_msg(_("proof by cases: we first assume {}").
                             format(h1))
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
    hypo = selected_property[0].math_type.to_display()

    if len(selected_property) == 2:
        if not (selected_property[0].math_type.is_prop()
                and selected_property[1].math_type.is_prop()):
            error = _("selected items are not properties")
            raise WrongUserInput(error)
        else:
            second_selected_property = selected_property[1].info["name"]
    elif len(selected_property) == 1:
        if not selected_property[0].math_type.is_prop():
            error = _("selected item is not a property")
            raise WrongUserInput(error)
        if not user_input:
            raise MissingParametersError(
                InputType.Text,
                title=_("Obtain 'P OR Q'"),
                output=_("Enter the proposition you want to use:"))
        else:
            second_selected_property = user_input[0]
            user_input = user_input[1:]
        
    if not user_input:
        raise MissingParametersError(
            InputType.Choice,
            [(_("Left"),
              f'({hypo}) OR ({second_selected_property})'),
             (_('Right'),
              f'({second_selected_property}) OR ({hypo})')],
            title=_("Choose side"),
            output=_(f'On which side do you want') + f' {hypo} ?')
    
    new_hypo_name = get_new_hyp(proof_step)
    if user_input[0] == 0:
        possible_codes.append(f'have {new_hypo_name} := '
                              f'@or.inl _ ({second_selected_property}) '
                              f'({first_hypo_name})')
    elif user_input[0] == 1:
        possible_codes.append(f'have {new_hypo_name} := '
                              f'@or.inr ({second_selected_property}) _ '
                              f'({first_hypo_name})')
    else:
        raise WrongUserInput("unexpected error")
    code = CodeForLean.or_else_from_list(possible_codes)
    code.add_success_msg(_('property {} added to the context').
                         format(new_hypo_name))
    return code
            

@action(tooltips.get('tooltip_or'),
        logic_button_texts['action_or'])
def action_or(proof_step,
              selected_objects: [MathObject],
              user_input=None,
              target_selected: bool = True) -> CodeForLean:
    """
    If the target is of the form P OR Q:
        transform the target in P (or Q) according to the user's choice.
    If a hypothesis of the form P OR Q has been previously selected:
        transform the current goal into two subgoals,
            one with P as a hypothesis,
            and another with Q as a hypothesis.
    """

    test_selection(selected_objects, target_selected)
    goal = proof_step.goal

    if len(selected_objects) == 0:
        if not goal.target.is_or():
            raise WrongUserInput(
                error=_("target is not a disjunction 'P OR Q'"))
        else:
            return construct_or(proof_step, user_input)
    elif len(selected_objects) == 1:
        if selected_objects[0].is_or():
            return apply_or(proof_step, selected_objects, user_input)
        else:
            return construct_or_on_hyp(proof_step, selected_objects, user_input)
    elif len(selected_objects) == 2:
        return construct_or_on_hyp(proof_step, selected_objects, user_input)
    else:  # More than 2 selected objects
        raise WrongUserInput(error=_("does not apply to more than two "
                                     "properties"))


#######
# NOT #
#######
@action(tooltips.get('tooltip_not'),
        logic_button_texts['action_negate'])
def action_negate(proof_step,
                  selected_objects: [MathObject],
                  target_selected: bool = True) -> CodeForLean:
    """
    Translate into string of lean code corresponding to the action
    
    If no hypothesis has been previously selected:
        transform the target in an equivalent one with its negations 'pushed'.
    If a hypothesis has been previously selected:
        do the same to the hypothesis.
    """

    test_selection(selected_objects, target_selected)
    goal = proof_step.goal

    if len(selected_objects) == 0:
        if not goal.target.is_not():
            raise WrongUserInput(error=_("target is not a negation 'NOT P'"))
        code = CodeForLean.from_string('push_neg')
        code.add_success_msg(_("negation pushed on target"))
    elif len(selected_objects) == 1:
        if not selected_objects[0].is_not():
            error = _("selected property is not a negation 'NOT P'")
            raise WrongUserInput(error)
        selected_hypo = selected_objects[0].info["name"]
        code = CodeForLean.from_string(f'push_neg at {selected_hypo}')
        code.add_success_msg(_(f"negation pushed on property "
                                   f"{selected_hypo}"))
    else:
        raise WrongUserInput(error=_('negate only one property at a time'))
    return code


###############
# IMPLICATION #
###############
def construct_implicate(proof_step) -> CodeForLean:
    """
    Here the target is assumed to be an implication P ⇒ Q, P is added to the
    context, and the target becomes Q.
    """
    if not proof_step.goal.target.is_implication():
        raise WrongUserInput(error=_("target is not an implication 'P ⇒ Q'"))
    else:
        new_hypo_name = get_new_hyp(proof_step)
        code = CodeForLean.from_string(f'intro {new_hypo_name}')
        code.add_success_msg(_("property {} added to the context").
                             format(new_hypo_name))
        return code


def apply_implicate(proof_step, selected_object: [MathObject]) -> CodeForLean:
    """
    Here selected_object contains a single property which is an implication
    P ⇒ Q; if the target is Q then it will be replaced by P.
    """
    selected_hypo = selected_object[0].info["name"]
    code = CodeForLean.from_string(f'apply {selected_hypo}')
    code.add_success_msg(_("target modified using implication {}").
                         format(selected_hypo))
    return code


def have_new_property(arrow: MathObject,
                      variable_names: [str],
                      new_hypo_name: str) -> CodeForLean:
    """

    :param arrow:           a MathObject which is either an implication or a
                            universal property
    :param variable_names:  a list of names of variables (or properties) to
                            which "arrow" will be applied
    :param new_hypo_name:   a fresh name for the new property

    return:                 Lean Code to produce the wanted new property,
                            taking into account implicit parameters
    """

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
    code.add_success_msg(_("Property {} added to the context").
                         format(new_hypo_name))
    return code


def apply_implicate_to_hyp(proof_step,
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

    return have_new_property(implication, variable_names, new_hypo_name)


@action(tooltips.get('tooltip_implies'),
        logic_button_texts['action_implicate'])
def action_implicate(proof_step,
                     selected_objects: [MathObject],
                     target_selected: bool = True) -> CodeForLean:
    """
    Three cases:
    (1) No property selected:
        If the target is of the form P ⇒ Q: introduce the hypothesis P in
        the properties and transform the target into Q.
    (2) A single selected property, of the form P ⇒ Q: If the target was Q,
    it is replaced by P
    (3) Exactly two selected property, on of which is an implication P ⇒ Q
    and the other is P: Add Q to the context
    """

    test_selection(selected_objects, target_selected)
    goal = proof_step.goal

    if len(selected_objects) == 0:
        if not goal.target.is_implication():
            raise WrongUserInput(
                error=_("target is not an implication 'P ⇒ Q'"))
        else:
            return construct_implicate(proof_step)
    if len(selected_objects) == 1:
        if not selected_objects[0].can_be_used_for_implication():
            raise WrongUserInput(
                error=_("selected property is not an implication 'P ⇒ Q'"))
        else:
            return apply_implicate(proof_step, selected_objects)
    elif len(selected_objects) == 2:
        if not selected_objects[-1].can_be_used_for_implication():
            if not selected_objects[0].can_be_used_for_implication():
                raise WrongUserInput(error=_(
                    "selected properties are not implications 'P ⇒ Q'"
                                            ))
            else:  # l[0] is an implication but not l[1]: permute
                selected_objects.reverse()
        return apply_implicate_to_hyp(proof_step, selected_objects)
    # TODO: treat the case of more properties, including the possibility of
    #  P, Q and 'P and Q ⇒ R'
    raise WrongUserInput(error=_("does not apply to more than two properties"))


#######
# IFF #
#######

def construct_iff(proof_step, user_input: [str]) -> CodeForLean:
    """
    Assuming target is an iff, split into two implications.
    """

    goal = proof_step.goal
    code = CodeForLean.empty_code()

    if not user_input:
        left = goal.target.math_type.children[0].to_display()
        right = goal.target.math_type.children[1].to_display()
        choices = [("⇒", f'({left}) ⇒ ({right})'),
                   ("⇐", f'({right}) ⇒ ({left})')]
        raise MissingParametersError(
            InputType.Choice,
            choices,
            title=_("Choose sub-goal"),
            output=_("Which implication to prove first?"))

    elif len(user_input) == 1:
        if user_input[0] == 1:
            code = CodeForLean.from_string("rw iff.comm")
        code = code.and_then("split")
    else:
        raise WrongUserInput(error=_("undocumented error"))
    code.add_success_msg(_("begin proof of first implication"))
    return code


def destruct_iff(proof_step) -> CodeForLean:
    """
    Check if target is a conjunction of two implications (but not if these
    implications are logical inverses). If so, return code that builds the
    equivalent iff statement. If not, return None.
    """

    goal = proof_step.goal
    code = None
    target = goal.target
    if target.is_and():
        left = target.math_type.children[0]
        right = target.math_type.children[1]
        if left.is_implication(is_math_type=True) \
                and right.is_implication(is_math_type=True):
            code = CodeForLean.from_string("apply iff_def.mp")
            code.add_success_msg(_("target replaced by iff property"))
    return code


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
    code.add_success_msg(_("property {} split into {} and {}").
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
    return code


@action(tooltips.get('tooltip_iff'),
        logic_button_texts['action_iff'])
def action_iff(proof_step,
               selected_objects: [MathObject],
               user_input: [str] = [],
               target_selected: bool = True) -> CodeForLean:
    """
    Three cases:
    (1) No selected property:
        If the target is of the form P ⇔ Q:
            introduce two subgoals, P⇒Q, and Q⇒P.
        If target is of the form (P → Q) ∧ (Q → P):
            replace by P ↔ Q
    (2) 1 selected property, which is an iff P ⇔ Q:
        split it into two implications P⇒Q, and Q⇒P.
    (3) 2 properties:
        try to obtain P ⇔ Q.
    """

    test_selection(selected_objects, target_selected)
    goal = proof_step.goal

    if len(selected_objects) == 0:
        if goal.target.math_type.node != "PROP_IFF":
            code = destruct_iff(proof_step)
            if code:
                return code
            else:
                raise WrongUserInput(
                    error=_("target is not an iff property 'P ⇔ Q'"))
        else:
            return construct_iff(proof_step, user_input)
    if len(selected_objects) == 1:
        if selected_objects[0].math_type.node != "PROP_IFF":
            error = _("selected property is not an iff property 'P ⇔ Q'")
            raise WrongUserInput(error)
        else:
            return destruct_iff_on_hyp(proof_step, selected_objects)
    if len(selected_objects) == 2:
        if not (selected_objects[0].math_type.is_prop()
                and selected_objects[1].math_type.is_prop()):
            error = _("selected items should both be implications")
            raise WrongUserInput(error)
        else:
            return construct_iff_on_hyp(proof_step, selected_objects)
    raise WrongUserInput(error=_("does not apply to more than two properties"))


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
    math_type = math_object.children[0]
    variable = math_object.children[1]
    body = math_object.children[2]
    hint = variable.display_name  # not optimal
    if math_type.node == "PRODUCT":
        [math_type_1, math_type_2] = math_type.children
        x = give_global_name(proof_step=proof_step, math_type=math_type_1)
        y = give_global_name(proof_step=proof_step, math_type=math_type_2)
        possible_codes = CodeForLean.from_string(f'rintro ⟨ {x}, {y} ⟩')
        name = f"({x},{y})"
    else:
        x = give_global_name(proof_step=proof_step,
                             math_type=math_type,
                             hints=[hint]
                             )
        possible_codes = CodeForLean.from_string(f'intro {x}')
        name = f"{x}"
    possible_codes.add_success_msg(_("Object {} added to the context").
                                       format(name))

    if body.is_implication(is_math_type=True):
        # If math_object has the form
        # ∀ x:X, (x R ... ==> ...)
        # where R is some inequality relation
        # then introduce the inequality on top of x
        premise = body.children[0]  # children (2,0)
        if premise.is_inequality(is_math_type=True):
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
    if math_object.is_for_all():
        math_type, var, body = math_object.math_type.children
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


def apply_forall(proof_step, l: [MathObject]) -> CodeForLean:
    """
    Try to apply last selected property on the other ones.
    The last property should be a universal property
    (or equivalent to such after unfolding definitions)

    :param l: list of MathObjects of length ≥ 2
    :return:
    """

    goal = proof_step.goal
    universal_property = l[-1]  # The property to be applied
    unsolved_inequality_counter = 0
    # Variable_names will contain the list of variables and proofs of
    # inequalities that will be passed to universal_property
    variable_names = []
    code = CodeForLean.empty_code()
    for potential_var in l[:-1]:
        # TODO: replace by pattern matching
        # Check for "∀x>0" (and variations)
        inequality = inequality_from_pattern_matching(universal_property,
                                                      potential_var)
        variable_names.append(potential_var.info['name'])
        if inequality:
            math_types = [p.math_type for p in goal.context]
            if inequality in math_types:
                index = math_types.index(inequality)
                inequality_name = goal.context[index].display_name
                variable_names.append(inequality_name)
            else:
                inequality_name = get_new_hyp(proof_step)
                variable_names.append(inequality_name)
                unsolved_inequality_counter += 1
                # Add type indication to the variable in inequality
                math_type = inequality.children[1].math_type
                # Variable is not used explicitly, but this affects inequality:
                variable = inequality.children[0]
                variable = add_type_indication(variable, math_type)
                display_inequality = inequality.to_display(
                    is_math_type=False,
                    format_='lean')
                # Code I: state corresponding inequality #
                code = code.and_then(f"have {inequality_name}: "
                                     f"{display_inequality}")
                code = code.and_then("rotate")

    # Code II: Apply universal_property #
    new_hypo_name = get_new_hyp(proof_step)
    code = code.and_then(have_new_property(universal_property,
                                           variable_names,
                                           new_hypo_name)
                         )

    # Code III: try to solve inequalities #     e.g.:
    #   iterate 2 { solve1 {try {norm_num at *}, try {compute_n 10}} <|>
    #               rotate},   rotate,
    more_code = CodeForLean.empty_code()
    if unsolved_inequality_counter:
        code = code.and_then("rotate")  # back to first inequality
        more_code1 = CodeForLean.from_string("norm_num at *")
        more_code1 = more_code1.try_()
        more_code2 = CodeForLean.from_string("compute_n 1")
        more_code2 = more_code2.try_()
        # Try to solve1 inequality by norm_num, maybe followed by compute:
        more_code = more_code1.and_then(more_code2)
        more_code = more_code.single_combinator("solve1")
        # If it fails, rotate to next inequality
        more_code = more_code.or_else("rotate")
        # Do this for all inequalities
        #   more_code = more_code.single_combinator(f"iterate
        #   {unsolved_inequality_counter}") --> replaced by explicit iteration
        code_list = [more_code] * unsolved_inequality_counter
        more_code = CodeForLean.and_then_from_list(code_list)
        # Finally come back to first inequality
        more_code = more_code.and_then("rotate")

    code.add_success_msg(_("Property {} added to the context").
                             format(new_hypo_name))
    return code.and_then(more_code)


@action(tooltips.get('tooltip_forall'),
        logic_button_texts['action_forall'])
def action_forall(proof_step,
                  selected_objects: [MathObject],
                  user_input: [str] = [],
                  target_selected: bool = True) -> CodeForLean:
    """
    (1) If no selection and target is of the form ∀ x, P(x):
        introduce x and transform the target into P(x)
    (2) If a single universal property is selected, ask user for an object
        to which the property will be applied
    (3) If 2 or more items are selected, one of which is a universal
        property, try to apply it to the other selected items

    """

    test_selection(selected_objects, target_selected)
    goal = proof_step.goal

    if len(selected_objects) == 0:
        if not goal.target.is_for_all():
            error = _("target is not a universal property '∀x, P(x)'")
            raise WrongUserInput(error)
        else:
            return construct_forall(proof_step)

    elif len(selected_objects) == 1:  # Ask user for item
        if not selected_objects[0].is_for_all():
            error = _("selected property is not a universal property '∀x, "
                      "P(x)'")
            raise WrongUserInput(error)
        elif not user_input:
            raise MissingParametersError(InputType.Text,
                                         title=_("Apply a universal property"),
                                         output=_(
                                             "Enter element on which you "
                                             "want to apply:"))
        else:
            item = user_input[0]
            item = add_type_indication(item)  # e.g. (0:ℝ)
            if item[0] != '(':
                item = '(' + item + ')'
            potential_var = MathObject(node="LOCAL_CONSTANT",
                                       info={'name': item},
                                       children=[],
                                       math_type=None)
            selected_objects.insert(0, potential_var)
            # Now len(l) == 2
    # From now on len(l) ≥ 2
    # Search for a universal property among l, beginning with last item
    selected_objects.reverse()
    for item in selected_objects:
        if item.is_for_all():
            # Put item on last position
            selected_objects.remove(item)
            selected_objects.reverse()
            selected_objects.append(item)
            return apply_forall(proof_step, selected_objects)
    raise WrongUserInput(error=_("no universal property among selected"))


##########
# EXISTS #
##########

def construct_exists(proof_step, user_input: [str]) -> CodeForLean:
    """
    Assuming the target is an existential property '∃ x, P(x)', prove it by
    providing a witness x and proving P(x).
    """

    if not user_input:
        raise MissingParametersError(InputType.Text,
                                     title=_("Exist"),
                                     output=_(
                                         "Enter element you want to use:"))
    x = user_input[0]
    code = CodeForLean.from_string(f'use {x}, dsimp')
    code = code.or_else(f'use {x}')
    code.add_success_msg(_("now prove {} suits our needs").format(x))
    return code


def apply_exists(proof_step, selected_object: [MathObject]) -> CodeForLean:
    """
    Apply a property '∃ x, P(x)' to get an x with property P(x).
    """

    selected_hypo = selected_object[0].math_type
    hypo_name = selected_object[0].info["name"]
    x = give_global_name(proof_step=proof_step,
                         math_type=selected_hypo.children[0],
                         hints=[selected_hypo.children[1].to_display()])
    new_hypo_name = get_new_hyp(proof_step)

    if selected_hypo.children[2].node == "PROP_∃":
        code = f'rcases {hypo_name} with ' \
                f'⟨ {x}, ⟨ {new_hypo_name}, {hypo_name} ⟩ ⟩'
    else:
        code = f'cases {hypo_name} with {x} {new_hypo_name}'
    code = CodeForLean.from_string(code)
    if selected_hypo.node == 'QUANT_∃!':
        # We have to add the "simp" tactic to avoid appearance of lambda expr
        code = code.and_then(f'simp at {new_hypo_name}')
    code.add_success_msg(_("new object {} with property {}").
                         format(x, new_hypo_name))
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
    code.add_success_msg(_("get new existential property {}").
                             format(new_hypo))
    return code


@action(tooltips.get('tooltip_exists'),
        logic_button_texts['action_exists'])
def action_exists(proof_step,
                  selected_objects: [MathObject],
                  user_input: [str] = None,
                  target_selected: bool = True) -> CodeForLean:
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

    test_selection(selected_objects, target_selected)
    goal = proof_step.goal

    if len(selected_objects) == 0:
        if not goal.target.is_exists():
            error = _("target is not existential property '∃x, P(x)'")
            raise WrongUserInput(error)
        else:
            return construct_exists(proof_step, user_input)
    elif len(selected_objects) == 1 and not user_input:
        selected_hypo = selected_objects[0]
        if selected_hypo.math_type.is_prop():
            # Try to apply property "exists x, P(x)" to get a new MathObject x
            if not selected_hypo.is_exists():
                error = _("selection is not existential property '∃x, P(x)'")
                raise WrongUserInput(error)
            else:
                return apply_exists(proof_step, selected_objects)
        else:  # h_selected is not a property : get an existence property
            if not goal.target.is_exists():
                error = _("target is not existential property '∃x, P(x)'")
                raise WrongUserInput(error)
            else:
                object_name = selected_objects[0].info["name"]
                return construct_exists(proof_step, [object_name])
    elif len(selected_objects) == 2:
        return construct_exists_on_hyp(proof_step, selected_objects)
    raise WrongUserInput(error=_("does not apply to more than two properties"))


#########
# utils #
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
        return NUMBER_SETS_LIST[ind]


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
