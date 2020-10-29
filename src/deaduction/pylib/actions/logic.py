"""
############################################################
# logic.py : functions to call in order to                 #
# translate actions into lean code                         #
############################################################
    
Every function action_* takes 2 arguments,
- goal (of class Goal)
- a list of ProofStatePO precedently selected by the user
and returns lean code as a string

Some take an optional argument:
- user_input, a list of 

Author(s)     : - Marguerite Bin <bin.marguerite@gmail.com>
Maintainer(s) : - Marguerite Bin <bin.marguerite@gmail.com>
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

from deaduction.config        import user_config, _
from deaduction.pylib.actions import (action,
                                      InputType,
                                      MissingParametersError,
                                      WrongUserInput,
                                      format_orelse)
from deaduction.pylib.mathobj import (MathObject,
                                      Goal,
                                      give_global_name,
                                      get_new_hyp)

log = logging.getLogger("logic")  # uncomment to use


# Get buttons symbols from config file
action_list = ['action_and', 'action_or', 'action_negate',
               'action_implicate', 'action_iff', 'action_forall',
               'action_exists']
if user_config.getboolean('use_logic_button_symbols'):
    logic_button_texts = user_config.get('logic_button_symbols')
else:
    logic_button_texts = user_config.get('logic_button_texts')
# turn logic_button_texts into a dictionary
lbt = logic_button_texts.split(', ')
logic_button_texts = {}
for key, value in zip(action_list, lbt):
    logic_button_texts[key] = value


#######
# AND #
#######

def construct_and(goal: Goal, user_input: [str]):
    possible_codes = []

    if goal.target.math_type.node != "PROP_AND":
        raise WrongUserInput
    left = goal.target.math_type.children[0].format_as_utf8()
    right = goal.target.math_type.children[1].format_as_utf8()
    choices = [(_("Left"), left), (_("Right"), right)]

    if user_input == []:
        raise MissingParametersError(
            InputType.Choice,
            choices,
            title=_("Choose sub-goal"),
            output=_("Which property to prove first?"))

    if len(user_input) == 1:
        if user_input[0] == 1:
            code = "rw and.comm, "
        else:
            code = ""
        possible_codes.append(f'{code}split')

    return format_orelse(possible_codes)


def apply_and(goal, l):
    possible_codes = []
    h_selected = l[0].info["name"]
    h1 = get_new_hyp(goal)
    h2 = get_new_hyp(goal)
    possible_codes.append(f'cases {h_selected} with {h1} {h2}')
    return format_orelse(possible_codes)


def construct_and_hyp(goal, selected_objects: [MathObject]):
    possible_codes = []
    h1 = selected_objects[0].info["name"]
    h2 = selected_objects[1].info["name"]
    new_h = get_new_hyp(goal)
    possible_codes.append(f'have {new_h} := and.intro {h1} {h2}')
    return format_orelse(possible_codes)


@action(user_config.get('tooltip_and'),
        logic_button_texts['action_and'])
def action_and(goal: Goal, selected_objects: [MathObject],
               user_input: [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action

If the target is of the form P AND Q:
    transform the current goal into two subgoals, P, then Q.
If a hypothesis of the form P AND Q has been previously selected:
    creates two new hypothesis P, and Q.
If two hypothesis P, then Q, have been previously selected:
    add the new hypothesis P AND Q to the properties.

    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(selected_objects) == 0:
        return construct_and(goal, user_input)
    if len(selected_objects) == 1:
        if selected_objects[0].math_type.node != "PROP_AND":
            raise WrongUserInput
        else:
            return apply_and(goal, selected_objects)
    if len(selected_objects) == 2:
        if not (selected_objects[0].math_type.is_prop and
                selected_objects[1].math_type.is_prop):
            raise WrongUserInput
        else:
            return construct_and_hyp(goal, selected_objects)
    raise WrongUserInput


## OR ##

def construct_or(goal: Goal, user_input: [str]) -> str:
    possible_codes = []

    if goal.target.math_type.node != "PROP_OR":
        raise WrongUserInput

    left = goal.target.math_type.children[0].format_as_utf8()
    right = goal.target.math_type.children[1].format_as_utf8()
    choices = [(_("Left"), left), (_("Right"), right)]

    if len(user_input) == 0:
        raise MissingParametersError(InputType.Choice,
                                     choices,
                                     title=_("Choose new goal"),
                                     output=_("Which property will you "
                                              "prove?"))

    if len(user_input) == 1:
        i = user_input[0]
        code = ["left", "right"][i]
        possible_codes.append(code)

    return format_orelse(possible_codes)


def apply_or(goal, l: [MathObject], user_input: [str]) -> str:
    possible_codes = []
    if l[0].math_type.node != "PROP_OR":
        raise WrongUserInput

    h_selected = l[0].info["name"]

    left = l[0].math_type.children[0].format_as_utf8()
    right = l[0].math_type.children[1].format_as_utf8()
    choices = [(_("Left"), left), (_("Right"), right)]

    if len(user_input) == 0:
        raise MissingParametersError(InputType.Choice,
                                     choices=choices,
                                     title=_("Choose case"),
                                     output=_("Which case to assume first?"))

    if len(user_input) == 1:
        if user_input[0] == 1:
            possible_codes.append(f'rw or.comm at {h_selected}, ')
        else:
            possible_codes.append("")

    h1 = get_new_hyp(goal)
    h2 = get_new_hyp(goal)
    possible_codes[0] += (f'cases {h_selected} with {h1} {h2}')
    return format_orelse(possible_codes)

def construct_or_on_hyp(goal: Goal, l: [MathObject], user_input: [str] = []):
    possible_codes = []
    if not l[0].math_type.is_prop():
        raise WrongUserInput
    hP = l[0].info["name"]
    P = l[0].math_type.format_as_utf8()
    if len(l) == 2:
        Q = l[1].info["name"]
    
    elif len(l) == 1:
        if len(user_input) == 0:
            raise MissingParametersError(InputType.Text,
                    title=_("Obtain 'P OR Q'"),
                    output=_("Enter the proposition you want to use:"))
        Q = user_input[0]
        user_input = user_input[1:]
        
    if len(user_input) == 0:
        raise MissingParametersError(
            InputType.Choice,
            [(_("Left"), f'({P}) OR ({Q})'), (_('Right'), f'({Q}) OR ({P})')],
            title=_("Choose side"),
            output=_(f'On which side do you want') + f' {P} ?')
    
    new_h = get_new_hyp(goal)
    if user_input[0] == 0:
        possible_codes.append(f'have {new_h} := @or.inl _ ({Q}) ({hP})')
    elif user_input[0] == 1:
        possible_codes.append(f'have {new_h} := @or.inr ({Q}) _ ({hP})')
    else:
        raise WrongUserInput
    return format_orelse(possible_codes)
            
            
            
            
@action(user_config.get('tooltip_or'),
        logic_button_texts['action_or'])
        
def action_or(goal: Goal, l: [MathObject], user_input=[]) -> str:
    """
    Translate into string of lean code corresponding to the action

    If the target is of the form P OR Q:
tranform the target in P (or Q) accordingly to the user's choice.
    If a hypothesis of the form P OR Q has been previously selected:
transform the current goal into two subgoals,
    one with P as a hypothesis,
    and another with Q as a hypothesis.

    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_or(goal, user_input)
    if len(l) == 1:
        if l[0].math_type.node == "PROP_OR":
            return apply_or(goal, l, user_input)
        elif l[0].math_type.is_prop():
            return construct_or_on_hyp(goal, l, user_input)
    if len(l) == 2 and l[0].math_type.is_prop() and l[1].math_type.is_prop():
        return construct_or_on_hyp(goal, l, user_input)
    raise WrongUserInput


## NOT ##

@action(user_config.get('tooltip_not'),
        logic_button_texts['action_negate'])
def action_negate(goal: Goal, l: [MathObject]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    If no hypothesis has been previously selected:
transform the target in an equivalent one which has its negations 'pushed'.
    If a hypothesis has been previously selected:
do the same to the hypothesis.

    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    possible_codes = []

    if len(l) == 0:
        if goal.target.math_type.node != "PROP_NOT":
            raise WrongUserInput
        possible_codes.append('push_neg')
    if len(l) == 1:
        if l[0].math_type.node != "PROP_NOT":
            raise WrongUserInput
        h_selected = l[0].info["name"]
        possible_codes.append(f'push_neg at {h_selected}')
    return format_orelse(possible_codes)


## IMPLICATION ##

def construct_implicate(goal: Goal):
    possible_codes = []

    if goal.target.math_type.node != "PROP_IMPLIES":
        raise WrongUserInput

    h = get_new_hyp(goal)
    possible_codes.append(f'intro {h}')
    return format_orelse(possible_codes)


def apply_implicate(goal: Goal, l: [MathObject]):
    possible_codes = []
    h_selected = l[0].info["name"]
    possible_codes.append(f'apply {h_selected}')
    return possible_codes


def apply_implicate_to_hyp(goal: Goal, l: [MathObject]):
    """
    Try to apply last selected property on the other ones.
    :param l: list of 2 or 3 MathObjects
    :return:
    """
    possible_codes = []
    h_selected = l[-1].info["name"]
    x_selected = l[0].info["name"]
    h = get_new_hyp(goal)

    if len(l) == 2:
        # try with up to 4 implicit parameters
        possible_codes.append(f'have {h} := {h_selected} {x_selected}')
        possible_codes.append(f'have {h} := {h_selected} _ {x_selected}')
        possible_codes.append(f'have {h} := {h_selected} _ _ {x_selected}')
        possible_codes.append(f'have {h} := {h_selected} _ _ _ {x_selected}')
        possible_codes.append(f'have {h} := {h_selected} _ _ _ _ {x_selected}')

        possible_codes.append(f'have {h} := @{h_selected} {x_selected}')
        possible_codes.append(f'have {h} := @{h_selected} _ {x_selected}')
        possible_codes.append(f'have {h} := @{h_selected} _ _ {x_selected}')
        possible_codes.append(f'have {h} := @{h_selected} _ _ _ {x_selected}')
        possible_codes.append(
            f'have {h} := @{h_selected} _ _ _ _ {x_selected}')

    elif len(l) == 3:
        y_selected = l[1].info["name"]
        # try to apply "forall x,y , P(x,y)" to x and y
        possible_codes.append(
            f'have {h} := {h_selected} {x_selected} {y_selected}')
        possible_codes.append(
            f'have {h} := {h_selected} _ {x_selected} {y_selected}')
        possible_codes.append(
            f'have {h} := {h_selected} _ _ {x_selected} {y_selected}')
        possible_codes.append(
            f'have {h} := {h_selected} _ _ _ {x_selected} {y_selected}')
        possible_codes.append(
            f'have {h} := {h_selected} _ _ _ _ {x_selected} {y_selected}')

    return possible_codes


@action(user_config.get('tooltip_implies'),
        logic_button_texts['action_implicate'])
def action_implicate(goal: Goal, l: [MathObject]) -> str:
    """
    Translate into string of lean code corresponding to the action

    If the target is of the form P ⇒ Q:
introduce the hypothesis P in the properties and transform the target into Q.

    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_implicate(goal)
    if len(l) == 1:
        return format_orelse(apply_implicate(goal, l))
    if len(l) == 2:
        return format_orelse(apply_implicate_to_hyp(goal, l))
    raise WrongUserInput


## IFF ##

def construct_iff(goal: Goal, user_input: [str]):
    possible_codes = []
    if goal.target.math_type.node != "PROP_IFF":
        raise WrongUserInput

    left = goal.target.math_type.children[0].format_as_utf8()
    right = goal.target.math_type.children[1].format_as_utf8()
    choices = [("⇒", f'({left}) ⇒ ({right})'), ("⇐", f'({right}) ⇒ ({left})')]

    if user_input == []:
        raise MissingParametersError(
            InputType.Choice,
            choices,
            title=_("Choose sub-goal"),
            output=_("Which implication to prove first?"))

    elif len(user_input) == 1:
        if user_input[0] == 1:
            code = "rw iff.comm, "
        else:
            code = ""
        possible_codes.append(f'{code}split')
    else:
        raise WrongUserInput
    return format_orelse(possible_codes)

def destruct_iff_on_hyp(goal: Goal, l: [MathObject]):
    possible_codes = []
    if l[0].math_type.node != "PROP_IFF":
        raise WrongUserInput
    h = l[0].info["name"]
    h1 = get_new_hyp(goal)
    h2 = get_new_hyp(goal)
    possible_codes.append(f'cases (iff_def.mp {h}) with {h1} {h2}')
    return format_orelse(possible_codes)
    
def construct_iff_on_hyp(goal: Goal, l: [MathObject]):
    possible_codes = []

    if not (l[0].math_type.is_prop() and l[1].math_type.is_prop()):
        raise WrongUserInput

    new_h = get_new_hyp(goal)
    h1 = l[0].info["name"]
    h2 = l[1].info["name"]
    possible_codes.append(f'have {new_h} := iff.intro {h1} {h2}')
    return format_orelse(possible_codes)


@action(user_config.get('tooltip_iff'),
        logic_button_texts['action_iff'])
def action_iff(goal: Goal, l: [MathObject], user_input: [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    If the target is of the form P ⇔ Q:
introduce two subgoals, P⇒Q, and Q⇒P.

    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_iff(goal, user_input)
    if len(l) == 1:
        return destruct_iff_on_hyp(goal, l)
    if len(l) == 2:
        return construct_iff_on_hyp(goal, l)
    raise WrongUserInput


## FOR ALL ##

def construct_forall(goal):
    possible_codes = []
    if goal.target.math_type.node != "QUANT_∀":
        raise WrongUserInput
    x = give_global_name(goal=goal,
                         math_type=goal.target.math_type.children[0],
                         hints=[goal.target.math_type.children[
                                    1].format_as_utf8(),
                                goal.target.math_type.children[
                                    0].format_as_utf8().lower()])
    possible_codes.append(f'intro {x}')
    return format_orelse(possible_codes)


@action(user_config.get('tooltip_forall'),
        logic_button_texts['action_forall'])
def action_forall(goal: Goal, l: [MathObject]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    If the target is of the form ∀ x, P(x):
introduce x and transform the target into P(x)

    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_forall(goal)
    else:
        raise WrongUserInput


## EXISTS ##

def construct_exists(goal, user_input: [str]):
    possible_codes = []

    if goal.target.math_type.node != "QUANT_∃":
        raise WrongUserInput
    if len(user_input) != 1:
        raise MissingParametersError(InputType.Text,
                                     title=_("Exist"),
                                     output=_(
                                         "Enter element you want to use:"))
    # TODO : demander à FLR différence entre use et existsi. Un prend en compte le type et pas l'autre ?... la doc dit :
    # "Similar to existsi, use l will use entries in l to instantiate existential obligations at the beginning of a target. Unlike existsi, the pexprs in l are elaborated with respect to the expected type."
    x = user_input[0]
    possible_codes.append(f'existsi {x}')
    return format_orelse(possible_codes)


def apply_exists(goal: Goal, l: [MathObject]) -> str:
    possible_codes = []

    h_selected = l[0].math_type
    if h_selected.node != "QUANT_∃":
        raise WrongUserInput
    h_name = l[0].info["name"]
    x = give_global_name(goal=goal, math_type=h_selected.children[0],
                         hints=[h_selected.children[1].format_as_utf8()])
    hx = get_new_hyp(goal)
    if h_selected.children[2].node == "PROP_∃":
        possible_codes.append(
            f'rcases {h_name} with ⟨ {x}, ⟨ {hx}, {h_name} ⟩ ⟩')
    else:
        possible_codes.append(f'cases {h_name} with {x} {hx}')
    return format_orelse(possible_codes)


def construct_exists_on_hyp(goal: Goal, l: [MathObject]):
    """
    Try to construct an existence property from some object and some property
    :param goal:
    :param l:
    :return:
    """
    possible_codes = []
    x = l[0].info["name"]
    hx = l[1].info["name"]
    if not l[0].math_type.is_prop() and l[1].math_type.is_prop():
        new_h = get_new_hyp(goal)
        possible_codes.append(f'have {new_h} := exists.intro {x} {hx}')
    elif not l[1].math_type.is_prop() and l[0].math_type.is_prop():
        x, hx = hx, x
        new_h = get_new_hyp(goal)
        possible_codes.append(f'have {new_h} := exists.intro {x} {hx}')
    else:
        raise WrongUserInput
    return format_orelse(possible_codes)


@action(user_config.get('tooltip_exists'),
        logic_button_texts['action_exists'])
def action_exists(goal: Goal, l: [MathObject], user_input: [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    If target is of form ∃ x, P(x):
ask the user to enter a specific x and transform the target into P(x).
    If a hypothesis of form ∃ x, P(x) has been previously selected:
introduce a new x and add P(x) to the properties

    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 1 and user_input == []:
        h_selected = l[0].math_type
        if h_selected.is_prop():
            # try to apply property "exists x, P(x)" to get a new MathObject x
            if h_selected.node != "QUANT_∃":
                raise WrongUserInput
            else:
                return apply_exists(goal, l)
        else:
            return construct_exists(goal, [l[0].info["name"]])
    elif len(l) == 0:
        return construct_exists(goal, user_input)
    elif len(l) == 2:
        return construct_exists_on_hyp(goal, l)
    raise WrongUserInput

