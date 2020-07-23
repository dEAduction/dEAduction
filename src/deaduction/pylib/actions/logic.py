"""
############################################################
# logic.py : functions to call in order to                 #
# translate actions into lean code                         #
############################################################
    
Every function


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
import deaduction.pylib.logger as logger
import deaduction.pylib.actions.utils as utils
from deaduction.pylib.actions.actiondef import action
from mathobj.PropObj import PropObj # ne marche que si on rajoute snippets dans pythonpath, une fois que FLR aura rajouté les bons fichiers dans src ça marchera
import mathobj.PropObj as PO # useless for now
from mathobj.proof_state import Goal


log = logging.getLogger("logic")

@action(_("Negation"))
def action_negate(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    return ""

@action(_("Implication"))
def action_implicate(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    return ""

## AND ##

def construct_and(goal):
    log.debug(goal.target.math_type.node)
    if goal.target.math_type.node != "PROP_AND":        
        log.debug("noeud de goal pas and")
        return "" #TODO : gestion erreur raise usererror
    return "split, "

def apply_and(l):
    if l[0].node != "PROP_AND":
        return "" #TODO : gestion erreur raise usererror
    h = l[0].lean_data["name"]
    h1 = utils.get_new_hyp()
    h2 = utils.get_new_hyp()
    return "cases {0} with {1} {2}, ".format(h, h1, h2)
    
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
    if l[0].node != "PROP_OR":
        return "" #TODO : gestion erreur raise usererror
    h = l[0].lean_data["name"]
    h1 = utils.get_new_hyp()
    h2 = utils.get_new_hyp()
    return "cases {0} with {1} {2}, ".format(h, h1, h2)

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

def construct_forall(goal):
    log.debug(goal.target.math_type.node)
    if goal.target.math_type.node != "QUANT_∀":
        return "" # TODO : gestion erreur ex raise user_error 
    h = utils.get_new_hyp()
    return "intro {0}, ".format(h)

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

def construct_exists(): # compliqué, à Antoine de faire le taff
    return ""

def apply_exists(l : [PropObj]) -> str:
    if l[0].node != "QUANT_∃":
        return "" # TODO : gestion erreur ex raise user_error
    h2 = get_new_hyp()
    h = l[0].leandata["name"]
    x = get_new_var()
    hx = get_new_hyp()
    return "have {0} := {1}, cases {1} with {2} {3}, ".format(h2, h, x, hx) 

@action(_("Exists"))
def action_exists(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 1:
        return apply_exists()
    if len(l) == 2: # TODO : ???? demander à Antoine de faire un truc
                    # pour que je puisse faire la différence,
                    # peut-être 3e argument "pop-up" ?
        return construct_exists()
    return ""

## ASSUMPTION ##

@action(_("Assumption"))
def action_assumption(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0: # TODO : ptet verifier si on a bien une hypothèse pareil que le goal ?
        return "assumption, "
    else:
        return "" # TODO : gestion erreur ex raise user_error


if __name__ == "__main__":
    logger.configure()
    
    
