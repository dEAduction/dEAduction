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
from deaduction.pylib.actions.actiondef import action
from deaduction.pylib.mathobj.PropObj import PropObj
import deaduction.pylib.mathobj.PropObj as PO # useless for now
from deaduction.pylib.mathobj.proof_state import Goal


log = logging.getLogger("logic")

@action(_("Negation"))
def action_negate(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0:
        if goal.target.math_type.node != "PROP_NOT":
            return "" #TODO : gestion erreur raise usererror
        return "push_neg, "
    elif len(l) == 1:
        if l[0].math_type.node != "PROP_NOT":
            return "" #TODO : gestion erreur raise usererror
        return "push_neg at {0}, ".format(l[0].lean_data["name"])
    else:
        return ""

## IMPLICATION ##

def construct_implicate(goal : Goal):
    if goal.target.math_type.node != "PROP_IMPLIES":
        return "" #TODO : gestion erreur raise usererror
    h = utils.get_new_hyp()
    return "intro {0}, ".format(h)

def apply_implicate(goal : Goal, l : [PropObj]):
    if l[0].math_type.node != "PROP_IMPLIES":
        return "" #TODO : gestion erreur raise usererror
    if not l[0].math_type.children[1].__eq__(goal.target.math_type):
        return "" #TODO : gestion erreur raise usererror
    return "apply {0},".format(l[0].lean_data["name"])

def apply_implicate_to_hyp(goal : Goal, l : [PropObj]):
    if l[0].math_type.node != "PROP_IMPLIES":
        return "" #TODO : gestion erreur raise usererror
    if not l[0].math_type.children[0].__eq__(l[1].math_type):
        return "" #TODO : gestion erreur raise usererror
    h_selected = l[0].lean_data["name"]
    x_selected = l[1].lean_data["name"]
    h = utils.get_new_hyp()
    return "have {0} := {1} {2}, ".format(h, h_selected, x_selected)

@action(_("Implication"))
def action_implicate(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0:
        return construct_implicate(goal)
    elif len(l) == 1:
        return apply_implicate(goal, l)
    elif len(l) == 2:
        return apply_implicate_to_hyp(goal,l)
    return ""

## AND ##

def construct_and(goal):
    log.debug(goal.target.math_type.node)
    if goal.target.math_type.node != "PROP_AND":        
        log.debug("noeud de goal pas and")
        return "" #TODO : gestion erreur raise usererror
    return "split, "

def apply_and(l):
    if l[0].math_type.node != "PROP_AND":
        return "" #TODO : gestion erreur raise usererror
    h_selected = l[0].lean_data["name"]
    h1 = utils.get_new_hyp()
    h2 = utils.get_new_hyp()
    return "cases {0} with {1} {2}, ".format(h_selected, h1, h2)

@action(_("And"))
def action_and(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0:
        return construct_and(goal)
    elif len(l) == 1:
        return apply_and(l)
    else :
        return "" # TODO : gestion erreur raise usererror

## OR ##

def construct_or(goal : Goal) -> str:
    if goal.target.math_type.node != "PROP_OR":
        return "" # TODO : gestion erreur ex raise user_error 
    return "left, " # TODO : coder tactic lean permettant de
                    # trouver le bon left / right et remplacer dans ce code

def apply_or(l : [PropObj]) -> str:
    if l[0].math_type.node != "PROP_OR":
        return "" #TODO : gestion erreur raise usererror
    h_selected = l[0].lean_data["name"]
    h1 = utils.get_new_hyp()
    h2 = utils.get_new_hyp()
    return "cases {0} with {1} {2}, ".format(h_selected, h1, h2)

@action(_("Or"))
def action_or(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0:
        return construct_or(goal)
    elif len(l) == 1:
        return apply_or(l)
    else :
        return "" # TODO : gestion erreur ex raise user_error

## IFF ##

@action(_("If and only if"))
def action_iff(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    return ""

## FOR ALL ##

def construct_forall(goal):
    if goal.target.math_type.node != "QUANT_∀":
        return "" # TODO : gestion erreur ex raise user_error 
    x = utils.get_new_var()
    return "intro {0}, ".format(x)

@action(_("For all"))
def action_forall(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0:
        return construct_forall(goal)
    else :
        return "" # TODO : gestion erreur ex raise user_error

## EXISTS ##

def construct_exists(goal, x : str):
    if goal.target.math_type.node != "QUANT_∃":
        return "" # TODO : gestion erreur ex raise user_error
    return "use {0},".format(x)

def apply_exists(l : [PropObj]) -> str:
    if l[0].math_type.node != "QUANT_∃":
        return "" # TODO : gestion erreur ex raise user_error
    h_selected = l[0].lean_data["name"]
    x = utils.get_new_var()
    hx = utils.get_new_hyp()
    if l[0].math_type.children[2].node == "PROP_∃":
        return "rcases {0} with ⟨ {1}, ⟨ {2}, {0} ⟩ ⟩, ".format(h_selected, x, hx)
    else :
        return "cases {0} with {1} {2}, ".format(h, x, hx)

@action(_("Exists"))
def action_exists(goal : Goal, l : [PropObj], user_input : str = None) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 1 and user_input is None:
        if l[0].math_type.is_prop():
            return apply_exists(l)
        else:
            return construct_exists(goal, l[0].lean_data["name"])
    if len(l) == 0:
        if user_input is None:
            x = "0"
            return construct_exists(goal, x) # raise MissingStrInput ?
        else:
            return construct_exists(goal, user_input)
    return ""


