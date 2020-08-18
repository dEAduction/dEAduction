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
                                            get_new_var) 
from deaduction.pylib.mathobj   import (    PropObj,
                                            Goal,
                                            give_name)

# log = logging.getLogger("logic") # uncomment to use

## AND ##

def construct_and(goal):
    if goal.target.math_type.node != "PROP_AND":
        raise WrongUserInput
    return "split, "

def apply_and(l):
    if l[0].math_type.node != "PROP_AND":
        raise WrongUserInput
    h_selected = l[0].lean_data["name"]
    h1 = get_new_hyp()
    h2 = get_new_hyp()
    return "cases {0} with {1} {2}, ".format(h_selected, h1, h2)

def construct_and_hyp(selected_objects : [PropObj]):
    h1 = selected_objects[0].lean_data["name"]
    h2 = selected_objects[1].lean_data["name"]
    h = get_new_hyp()
    return "have {0} := and.intro {1} {2}, ".format(h, h1, h2)

@action(_("If the target is of the form P AND Q: transform the current goal into two subgoals, P, then Q.\nIf a hypothesis of the form P AND Q has been previously selected: creates two new hypothesis P, and Q.\n If two hypothesis P, then Q, have been previously selected: add the new hypothesis P AND Q to the properties."), _('AND'))
def action_and(goal : Goal, selected_objects: [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(selected_objects) == 0:
        return construct_and(goal)
    if len(selected_objects) == 1:
        return apply_and(selected_objects)
    if len(selected_objects) == 2:
        return construct_and_hyp(selected_objects)
    raise WrongUserInput

## OR ##

def construct_or(goal : Goal, user_input : [str]) -> str:
    if goal.target.math_type.node != "PROP_OR":
        raise WrongUserInput
    if len(user_input) == 1:
        left = goal.target.math_type.children[0].format_as_utf8()
        right = goal.target.math_type.children[1].format_as_utf8()
        if user_input[0] in [left, right]:
            i = [left, right].index(user_input[0])
            code = ["left","right"][i]
            return "{0}, ".format(code)
        else:
            raise WrongUserInput
    else:
        left = goal.target.math_type.children[0].format_as_utf8()
        right = goal.target.math_type.children[1].format_as_utf8()
        raise MissingParametersError(InputType.Choice, [left,right])

def apply_or(l : [PropObj]) -> str:
    if l[0].math_type.node != "PROP_OR":
        raise WrongUserInput
    h_selected = l[0].lean_data["name"]
    h1 = get_new_hyp()
    h2 = get_new_hyp()
    return "cases {0} with {1} {2}, ".format(h_selected, h1, h2)

@action(_("If the target is of the form P OR Q: tranform the target in P (or Q) accordingly to the user's choice.\nIf a hypothesis of the form P OR Q has been previously selected: transform the current goal into two subgoals, one with P as a hypothesis, and another with Q as a hypothesis."), _("OR"))
def action_or(goal : Goal, l : [PropObj], user_input = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_or(goal, user_input)
    if len(l) == 1:
        return apply_or(l)
    
    raise WrongUserInput

## NOT ##

@action(_("If no hypothesis has been previously selected: transform the target in an equivalent one which has its negations 'pushed'.\nIf a hypothesis has been previously selected: do the same to the hypothesis."), _("NOT"))
def action_negate(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        if goal.target.math_type.node != "PROP_NOT":
            raise WrongUserInput
        return "push_neg, "
    if len(l) == 1:
        if l[0].math_type.node != "PROP_NOT":
            raise WrongUserInput
        return "push_neg at {0}, ".format(l[0].lean_data["name"])
    raise WrongUserInput

## IMPLICATION ##

def construct_implicate(goal : Goal):
    if goal.target.math_type.node != "PROP_IMPLIES":
        raise WrongUserInput
    h = get_new_hyp()
    return "intro {0}, ".format(h)

def apply_implicate(goal : Goal, l : [PropObj]):
    if not l[0].math_type.children[1].__eq__(goal.target.math_type):
        raise WrongUserInput
    return "apply {0}, ".format(l[0].lean_data["name"])

def apply_implicate_to_hyp(goal : Goal, l : [PropObj]):
    h_selected = l[1].lean_data["name"]
    x_selected = l[0].lean_data["name"]
    h = get_new_hyp()
    return "have {0} := {1} {2} <|> have {0} := {1} _ {2} <|> have {0} := {1} _ _ {2} <|> have {0} := {1} _ _ _ {2} <|> have {0} := {1} _ _ _ _ {2} <|> have {0} := @{1} {2} <|> have {0} := @{1} _ {2} <|> have {0} := @{1} _ _ {2} <|> have {0} := @{1} _ _ _ {2} <|> have {0} := @{1} _ _ _ _ {2}, ".format(h, h_selected, x_selected)

@action(_("If the target is of the form P ⇒ Q: introduce the hypothesis P in the properties and transform the target into Q."), "⇒")
def action_implicate(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_implicate(goal)
    if len(l) == 1:
        return apply_implicate(goal, l)
    if len(l) == 2:
        return apply_implicate_to_hyp(goal,l)
    raise WrongUserInput


## IFF ##

def construct_iff(goal : Goal):
    if goal.target.math_type.node != "PROP_IFF":
        raise WrongUserInput
    return "split, "

@action(_("If the target is of the form P ⇔ Q: transform the target into (P =>Q AND Q =>P) by definition"), "⇔")
def action_iff(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_iff(goal)
    raise WrongUserInput

## FOR ALL ##

def construct_forall(goal):
    if goal.target.math_type.node != "QUANT_∀":
        raise WrongUserInput
    x = give_name(goal, goal.target.math_type.children[0], [goal.target.math_type.children[1].format_as_utf8(), goal.target.math_type.children[0].format_as_utf8().lower()])
    return "intro {0}, ".format(x)

@action(_("If the target is of the form ∀ x, P(x): introduce x and transform the target into P(x)"), "∀")
def action_forall(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_forall(goal)
    else :
        raise WrongUserInput

## EXISTS ##

def construct_exists(goal, user_input : [str]):
    if goal.target.math_type.node != "QUANT_∃":
        raise WrongUserInput
    if len(user_input) != 1:
        raise MissingParametersError(InputType.Text, title = _("Exist"), output = _("Enter element you want to use:"))
    return "use {0},".format(user_input[0])

def apply_exists(goal : Goal, l : [PropObj]) -> str:
    h_selected = l[0].math_type
    if h_selected.node != "QUANT_∃":
        raise WrongUserInput
    h_name = l[0].lean_data["name"]
    x = give_name(goal, math_type=h_selected.children[0],
                  authorized_names=h_selected.children[1].lean_data["name"],
                  hints=[h_selected.children[1].format_as_utf8()])
    hx = get_new_hyp()
    if h_selected.children[2].node == "PROP_∃":
        return "rcases {0} with ⟨ {1}, ⟨ {2}, {0} ⟩ ⟩, ".format(h_name, x, hx)
    else :
        return "cases {0} with {1} {2}, ".format(h_name, x, hx)

@action(_("If target is of form ∃ x, P(x): ask the user to enter a specific x and transform the target into P(x). \nIf a hypothesis of form ∃ x, P(x) has been previously selected: introduce a new x and add P(x) to the properties"), "∃")
def action_exists(goal : Goal, l : [PropObj], user_input : [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 1 and user_input == []:
        if l[0].math_type.is_prop():
            return apply_exists(goal, l)
        else:
            return construct_exists(goal, l[0].lean_data["name"])
    if len(l) == 0:
        return construct_exists(goal, user_input)
    raise WrongUserInput

## APPLY

def apply_substitute(goal : Goal, l: [PropObj]):
    #missing comma on purpose
    if len(l) == 1:
        return "rw {0} <|> rw <- {0}".format(l[0].lean_data["name"])
    if len(l) == 2:
        return "rw <- {0} at {1} <|> rw {0} at {1} <|> rw <- {1} at {0} <|> rw {1} at {0}".format(l[1].lean_data["name"], l[0].lean_data["name"])
    raise WrongUserInput

def apply_function(goal : Goal, l : [PropObj]):
    if len(l) == 1:
        raise WrongUserInput
    code = ""
    f = l[-1].lean_data["name"]
    Y = l[-1].math_type.children[1]
    while (len(l) != 1):
        new_h = get_new_hyp()
        # if function applied to equality
        if l[0].math_type.is_prop():
            h = l[0].lean_data["name"]
            code = code + f'have {new_h} := congr_arg {f} {h}, '
        # if function applied to element x
        else:
            x = l[0].lean_data["name"]
            y = give_name(goal, Y, [Y.lean_data["name"].lower()])
            code = code + f'set {y} := {f} {x} with {new_h}, '
        del l[0]
    return code    
    
@action(_("Apply last selected item on previous ones"), _("APPLY"))
def action_apply(goal : Goal, l : [PropObj]):
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        raise WrongUserInput # n'apparaîtra plus quand ce sera un double-clic
    
    # if user wants to apply a function
    if not l[-1].math_type.is_prop():
        return apply_function(goal, l)
    
    # determines which kind of property the user wants to apply
    quantifier = l[-1].math_type.node
    if quantifier == "PROP_EQUAL" or quantifier == "PROP_IFF":
        return apply_substitute(goal, l) + ", "
    
    if quantifier == "QUANT_∀":
        code = apply_substitute(goal, l) + " <|> "
    else:
        code = ""
    if quantifier == "PROP_IMPLIES" or quantifier == "QUANT_∀":
        if len(l) == 1:
            return code + apply_implicate(goal, l)
        if len(l) == 2:
            return code + apply_implicate_to_hyp(goal,l)
    
    raise WrongUserInput    

