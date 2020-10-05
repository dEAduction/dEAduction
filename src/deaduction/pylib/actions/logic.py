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
from dataclasses                import      dataclass
from gettext                    import      gettext as _
from deaduction.pylib.actions   import (    action,
                                            InputType,
                                            MissingParametersError,
                                            WrongUserInput,
                                            get_new_hyp,
                                            get_new_var,
                                            format_orelse) 
from deaduction.pylib.mathobj   import (    MathObject,
                                            Goal,
                                            give_global_name)

log = logging.getLogger("logic") # uncomment to use

## AND ##

def construct_and(goal : Goal, user_input : [str]):
    possible_codes = []
    
    if goal.target.math_type.node != "PROP_AND":
        raise WrongUserInput
    left = goal.target.math_type.children[0].format_as_utf8()
    right = goal.target.math_type.children[1].format_as_utf8()
    choices = [("Left", left), ("Right", right)]

    if user_input == []:
        raise MissingParametersError(
            InputType.Choice,
            choices,
            title="Choose sub-goal",
            output="Which property to prove first?")

    if len(user_input) == 1:
        if user_input[0] == 1:
            code = "rw and.comm, "
        else:
            code = ""
        possible_codes.append(f'{code}split')
            
    return format_orelse(possible_codes)

def apply_and(l):
    possible_codes = []
    
    if l[0].math_type.node != "PROP_AND":
        raise WrongUserInput
        
    h_selected = l[0].info["name"]
    h1 = get_new_hyp()
    h2 = get_new_hyp()
    possible_codes.append(f'cases {h_selected} with {h1} {h2}')
    return format_orelse(possible_codes)

def construct_and_hyp(selected_objects : [MathObject]):
    possible_codes = []
    h1 = selected_objects[0].info["name"]
    h2 = selected_objects[1].info["name"]
    new_h = get_new_hyp()
    possible_codes.append(f'have {new_h} := and.intro {h1} {h2}')
    return format_orelse(possible_codes)

@action(_("If the target is of the form P AND Q: transform the current goal into two subgoals, P, then Q.\nIf a hypothesis of the form P AND Q has been previously selected: creates two new hypothesis P, and Q.\n If two hypothesis P, then Q, have been previously selected: add the new hypothesis P AND Q to the properties."), _('AND'))
def action_and(goal : Goal, selected_objects: [MathObject], user_input : [str] = [] ) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(selected_objects) == 0:
        return construct_and(goal, user_input)
    if len(selected_objects) == 1:
        return apply_and(selected_objects)
    if len(selected_objects) == 2:
        return construct_and_hyp(selected_objects)
    raise WrongUserInput

## OR ##

def construct_or(goal : Goal, user_input : [str]) -> str:
    possible_codes = []
    
    if goal.target.math_type.node != "PROP_OR":
        raise WrongUserInput
    
    left = goal.target.math_type.children[0].format_as_utf8()
    right = goal.target.math_type.children[1].format_as_utf8()
    choices = [("Left", left), ("Right", right)]
    
    if len(user_input) == 0:
        
        raise MissingParametersError(InputType.Choice,
                                     choices,
                                     title="Choose new goal",
                                     output="Which property will you prove?")
        
    if len(user_input) == 1:
        i = user_input[0]
        code = ["left", "right"][i]
        possible_codes.append(code)
            
    return format_orelse(possible_codes)

def apply_or(l : [MathObject], user_input : [str]) -> str:
    possible_codes = []
    if l[0].math_type.node != "PROP_OR":
        raise WrongUserInput
    
    h_selected = l[0].info["name"]
    
    left = l[0].math_type.children[0].format_as_utf8()
    right = l[0].math_type.children[1].format_as_utf8()
    choices = [("Left", left), ("Right", right)]
    
    if len(user_input) == 0:
        raise MissingParametersError(InputType.Choice,
                                     choices=choices,
                                     title="Choose case",
                                     output="Which case to assume first?")
        
    if len(user_input) == 1:
        if user_input[0] == 1:
            possible_codes.append(f'rw or.comm at {h_selected}, ')
        else:
            possible_codes.append("")
    
    h1 = get_new_hyp()
    h2 = get_new_hyp()
    possible_codes[0] += (f'cases {h_selected} with {h1} {h2}')
    return format_orelse(possible_codes)

@action(_("If the target is of the form P OR Q: tranform the target in P (or Q) accordingly to the user's choice.\nIf a hypothesis of the form P OR Q has been previously selected: transform the current goal into two subgoals, one with P as a hypothesis, and another with Q as a hypothesis."), _("OR"))
def action_or(goal : Goal, l : [MathObject], user_input = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_or(goal, user_input)
    if len(l) == 1:
        return apply_or(l, user_input)
    raise WrongUserInput

## NOT ##

@action(_("If no hypothesis has been previously selected: transform the target in an equivalent one which has its negations 'pushed'.\nIf a hypothesis has been previously selected: do the same to the hypothesis."), _("NOT"))
def action_negate(goal : Goal, l : [MathObject]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
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

def construct_implicate(goal : Goal):
    possible_codes = []
    
    if goal.target.math_type.node != "PROP_IMPLIES":
        raise WrongUserInput
        
    h = get_new_hyp()
    possible_codes.append(f'intro {h}')
    return format_orelse(possible_codes)
    
def apply_implicate(goal : Goal, l : [MathObject]):
    possible_codes = []
    h_selected = l[0].info["name"]
    possible_codes.append(f'apply {h_selected}')
    return possible_codes

def apply_implicate_to_hyp(goal : Goal, l : [MathObject]):
    possible_codes = []
    h_selected = l[1].info["name"]
    x_selected = l[0].info["name"]
    h = get_new_hyp()
    
    possible_codes.append(f'have {h} := {h_selected} {x_selected}')
    possible_codes.append(f'have {h} := {h_selected} _ {x_selected}')
    possible_codes.append(f'have {h} := {h_selected} _ _ {x_selected}')
    possible_codes.append(f'have {h} := {h_selected} _ _ _ {x_selected}')
    possible_codes.append(f'have {h} := {h_selected} _ _ _ _ {x_selected}')
    
    possible_codes.append(f'have {h} := @{h_selected} {x_selected}')
    possible_codes.append(f'have {h} := @{h_selected} _ {x_selected}')
    possible_codes.append(f'have {h} := @{h_selected} _ _ {x_selected}')
    possible_codes.append(f'have {h} := @{h_selected} _ _ _ {x_selected}')
    possible_codes.append(f'have {h} := @{h_selected} _ _ _ _ {x_selected}')
    
    return possible_codes
    
@action(_("If the target is of the form P ⇒ Q: introduce the hypothesis P in the properties and transform the target into Q."), "⇒")
def action_implicate(goal : Goal, l : [MathObject]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_implicate(goal)
    if len(l) == 1:
        return format_orelse(apply_implicate(goal, l))
    if len(l) == 2:
        return format_orelse(apply_implicate_to_hyp(goal,l))
    raise WrongUserInput


## IFF ##

def construct_iff(goal : Goal, user_input : [str]):
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

def construct_iff_on_hyp(goal : Goal, l : MathObject):
    possible_codes = []
    
    if not (l[0].math_type.is_prop() and l[1].math_type.is_prop()):
        raise WrongUserInput
        
    new_h = get_new_hyp()
    h1 = l[0].info["name"]
    h2 = l[1].info["name"]
    possible_codes.append(f'have {new_h} := iff.intro {h1} {h2}')
    return format_orelse(possible_codes)

@action(_("If the target is of the form P ⇔ Q: introduce two subgoals, P⇒Q, and Q⇒P."), "⇔")
def action_iff(goal : Goal, l : [MathObject], user_input : [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_iff(goal, user_input)
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
                  hints=[goal.target.math_type.children[1].format_as_utf8(),
                    goal.target.math_type.children[0].format_as_utf8().lower()])
    possible_codes.append(f'intro {x}')
    return format_orelse(possible_codes)
    
@action(_("If the target is of the form ∀ x, P(x): introduce x and transform the target into P(x)"), "∀")
def action_forall(goal : Goal, l : [MathObject]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_forall(goal)
    else :
        raise WrongUserInput

## EXISTS ##

def construct_exists(goal, user_input : [str]):

    possible_codes = []
    
    if goal.target.math_type.node != "QUANT_∃":
        raise WrongUserInput
    if len(user_input) != 1:
        raise MissingParametersError(InputType.Text,
            title = _("Exist"),
            output = _("Enter element you want to use:"))
    # TODO : demander à FLR différence entre use et existsi. Un prend en compte le type et pas l'autre ?... la doc dit :
    # "Similar to existsi, use l will use entries in l to instantiate existential obligations at the beginning of a target. Unlike existsi, the pexprs in l are elaborated with respect to the expected type."
    x = user_input[0]
    possible_codes.append(f'existsi {x}')
    return format_orelse(possible_codes)
    
def apply_exists(goal : Goal, l : [MathObject]) -> str:
    possible_codes = []
    
    h_selected = l[0].math_type
    if h_selected.node != "QUANT_∃":
        raise WrongUserInput
    h_name = l[0].info["name"]
    x = give_global_name(goal=goal, math_type=h_selected.children[0],
                  hints=[h_selected.children[1].format_as_utf8()])
    hx = get_new_hyp()
    if h_selected.children[2].node == "PROP_∃":
        possible_codes.append(f'rcases {h_name} with ⟨ {x}, ⟨ {hx}, {h_name} ⟩ ⟩')
    else:
        possible_codes.append(f'cases {h_name} with {x} {hx}')
    return format_orelse(possible_codes)
    
def construct_exists_on_hyp(goal : Goal, l : [MathObject]):
    possible_codes = []
    
    x = l[0].info["name"]
    hx = l[1].info["name"]
    new_h = get_new_hyp()
    possible_codes.append(f'have {new_h} := exists.intro {hx} {x}')
    x, hx = hx, x
    possible_codes.append(f'have {new_h} := exists.intro {hx} {x}')
    return format_orelse(possible_codes)
    
@action(_("If target is of form ∃ x, P(x): ask the user to enter a specific x and transform the target into P(x). \nIf a hypothesis of form ∃ x, P(x) has been previously selected: introduce a new x and add P(x) to the properties"), "∃")
def action_exists(goal : Goal, l : [MathObject], user_input : [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 1 and user_input == []:
        if l[0].math_type.is_prop():
            return apply_exists(goal, l)
        else:
            return construct_exists(goal, [l[0].info["name"]])
    if len(l) == 0:
        return construct_exists(goal, user_input)
    if len(l) == 2:
        return construct_exists_on_hyp(goal, l)
    raise WrongUserInput

## APPLY

def apply_substitute(goal : Goal, l: [MathObject]):
    possible_codes = []
    
    if len(l) == 1:
        h = l[0].info["name"]
        possible_codes.append(f'rw {h}')
        possible_codes.append(f'rw <- {h}')
        
    if len(l) == 2:
        h = l[1].info["name"]
        heq = l[0].info["name"]
        possible_codes.append(f'rw <- {heq} at {h}')
        possible_codes.append(f'rw {heq} at {h}')
        
        h, heq = heq, h
        possible_codes.append(f'rw <- {heq} at {h}')
        possible_codes.append(f'rw {heq} at {h}')
        
    return possible_codes

def apply_function(goal : Goal, l : [MathObject]):
    possible_codes = []
    
    if len(l) == 1:
        raise WrongUserInput
    function = l[-1]  # let us check the input is indeed a function
    if function.math_type.node != "FUNCTION":
        raise WrongUserInput
    f = function.info["name"]
    Y = l[-1].math_type.children[1]
    while (len(l) != 1):
        new_h = get_new_hyp()
        # if function applied to equality
        if l[0].math_type.is_prop():
            h = l[0].info["name"]
            possible_codes.append(f'have {new_h} := congr_arg {f} {h}')
        # if function applied to element x
        else:
            x = l[0].info["name"]
            y = give_global_name(goal=goal, math_type=Y, hints=[Y.info[
                "name"].lower()])
            possible_codes.append(f'set {y} := {f} {x} with {new_h}')
        del l[0]
    return format_orelse(possible_codes)
    
@action(_("Apply last selected item on previous ones"), _("APPLY"))
def action_apply(goal : Goal, l : [MathObject]):
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    possible_codes = []
    
    if len(l) == 0:
        raise WrongUserInput # n'apparaîtra plus quand ce sera un double-clic
    
    # if user wants to apply a function
    if not l[-1].math_type.is_prop():
        return apply_function(goal, l)
    
    # determines which kind of property the user wants to apply
    quantifier = l[-1].math_type.node
    log.info(quantifier)
    if quantifier == "PROP_EQUAL" or quantifier == "PROP_IFF" or \
            quantifier == "QUANT_∀":
        possible_codes.extend(apply_substitute(goal, l))
    
    if quantifier == "PROP_IMPLIES" or quantifier == "QUANT_∀":
        if len(l) == 1:
            possible_codes.extend(apply_implicate(goal, l))
        if len(l) == 2:
            possible_codes.extend(apply_implicate_to_hyp(goal,l))
    
    return format_orelse(possible_codes)  

