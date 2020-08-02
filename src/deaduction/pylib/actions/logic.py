"""
############################################################
# logic.py : functions to call in order to                 #
# translate actions into lean code                         #
############################################################
    
Every function action_* takes 2 arguments,
- goal (of class Goal)
- a list of ProofStatePO precedently selected by the user
and returns lean code as a string

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


from dataclasses import dataclass
from gettext import gettext as _
import logging
import deaduction.pylib.actions.utils as utils
from deaduction.pylib.actions import (  action,
                                        InputType,
                                        MissingParametersError,
                                        WrongUserInput) 
from deaduction.pylib.mathobj import (  PropObj,
                                        Goal)

## AND ##

def construct_and(goal):
    if goal.target.math_type.node != "PROP_AND":
        raise WrongUserInput
    return "split, "

def apply_and(l):
    if l[0].math_type.node != "PROP_AND":
        raise WrongUserInput
    h_selected = l[0].lean_data["name"]
    h1 = utils.get_new_hyp()
    h2 = utils.get_new_hyp()
    return "cases {0} with {1} {2}, ".format(h_selected, h1, h2)

def construct_and_hyp(selected_objects : [PropObj]):
    h1 = selected_objects[0].lean_data["name"]
    h2 = selected_objects[1].lean_data["name"]
    h = utils.get_new_hyp()
    #TODO : comprendre pourquoi c'est pas bien parsé pcq metavariable
    raise WrongUserInput
    #return "have {0}, from and.intro {1} {2}, ".format(h, h1, h2)

@action(_("And"), _('AND'))
def action_and(goal : Goal, selected_objects: [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(selected_objects) == 0:
        return construct_and(goal)
    elif len(selected_objects) == 1:
        return apply_and(selected_objects)
    elif len(selected_objects) == 2:
        return construct_and_hyp(selected_objects)
    else:
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
    h1 = utils.get_new_hyp()
    h2 = utils.get_new_hyp()
    return "cases {0} with {1} {2}, ".format(h_selected, h1, h2)

@action(_("Or"), _("OR"))
def action_or(goal : Goal, l : [PropObj], user_input = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_or(goal, user_input)
    elif len(l) == 1:
        return apply_or(l)
    else :
        raise WrongUserInput

## NOT ##

@action(_("Negation"), _("NOT"))
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
    elif len(l) == 1:
        if l[0].math_type.node != "PROP_NOT":
            raise WrongUserInput
        return "push_neg at {0}, ".format(l[0].lean_data["name"])
    else:
        raise WrongUserInput

## IMPLICATION ##

def construct_implicate(goal : Goal):
    if goal.target.math_type.node != "PROP_IMPLIES":
        raise WrongUserInput
    h = utils.get_new_hyp()
    return "intro {0}, ".format(h)

def apply_implicate(goal : Goal, l : [PropObj]):
    if l[0].math_type.node != "PROP_IMPLIES":
        raise WrongUserInput
    if not l[0].math_type.children[1].__eq__(goal.target.math_type):
        raise WrongUserInput
    return "apply {0},".format(l[0].lean_data["name"])

def apply_implicate_to_hyp(goal : Goal, l : [PropObj]):
    #if l[0].math_type.node != "QUANT_∀":
    #    if not (l[0].math_type.node == "PROP_IMPLIES" and l[0].math_type.children[0] == l[1].math_type):
    #        raise WrongUserInput
    h_selected = l[0].lean_data["name"]
    x_selected = l[1].lean_data["name"]
    h = utils.get_new_hyp()
    return "have {0} := {1} {2}, ".format(h, h_selected, x_selected)

# TODO: see if we can put bigger arrows, same for iff
@action(_("Implication"), "⇒")
def action_implicate(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_implicate(goal)
    elif len(l) == 1:
        return apply_implicate(goal, l)
    elif len(l) == 2:
        return apply_implicate_to_hyp(goal,l)
    raise WrongUserInput


## IFF ##

def construct_iff(goal : Goal):
    if goal.target.math_type.node != "PROP_IFF":
        raise WrongUserInput
    return "split, "

@action(_("If and only if"), "⇔")
def action_iff(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_iff(goal)
    else:
        raise WrongUserInput

## FOR ALL ##

def construct_forall(goal):
    if goal.target.math_type.node != "QUANT_∀":
        raise WrongUserInput 
    x = utils.get_new_var()
    return "intro {0}, ".format(x)

@action(_("For all"), "∀")
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

def construct_exists(goal, x : str):
    if goal.target.math_type.node != "QUANT_∃":
        raise WrongUserInput
    if len(user_input) != 1:
        raise MissingParametersError(InputType.Text, title = _("Exist"), output = _("Enter element you want to use:"))
    return "use {0},".format(x)

def apply_exists(l : [PropObj]) -> str:
    if l[0].math_type.node != "QUANT_∃":
        raise WrongUserInput
    h_selected = l[0].lean_data["name"]
    x = utils.get_new_var()
    hx = utils.get_new_hyp()
    if l[0].math_type.children[2].node == "PROP_∃":
        return "rcases {0} with ⟨ {1}, ⟨ {2}, {0} ⟩ ⟩, ".format(h_selected, x, hx)
    else :
        return "cases {0} with {1} {2}, ".format(h_selected, x, hx)

@action(_("Exists"), "∃")
def action_exists(goal : Goal, l : [PropObj], user_input : [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 1 and user_input == []:
        if l[0].math_type.is_prop():
            return apply_exists(l)
        else:
            return construct_exists(goal, l[0].lean_data["name"])
    if len(l) == 0:
        return construct_exists(goal, user_input[0])
    raise WrongUserInput

## SUBSTITUTION

@action(_("Substitution"), "t[x:=u]") #TODO : symbole à changer
def action_substitution(goal : Goal, l : [PropObj]):
    """
    Translate into string of lean code corresponding to the action
    
    :param l:   list of PropObj arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 1:
        return "rw {0} <|> rw <- {0}, ".format(l[0].lean_data["name"])
    elif len(l) == 2:
        return "rw <- {0} at {1} <|> rw {0} at {1} <|> rw <- {1} at {0} <|> rw {1} at {0}, ".format(l[1].lean_data["name"],l[0].lean_data["name"])
    else:
        raise WrongUserInput    

