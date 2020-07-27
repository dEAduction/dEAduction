"""
# proofs.py : #ShortDescription #
    
    (#optionalLongDescription)

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
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

from dataclasses import dataclass
from gettext import gettext as _
import logging
import deaduction.pylib.actions.utils as utils
from deaduction.pylib.actions.actiondef import action
from deaduction.pylib.mathobj.PropObj import PropObj
import deaduction.pylib.mathobj.PropObj as PO # useless for now
from deaduction.pylib.mathobj.proof_state import Goal

@action(_("Assumption"))
def action_assumption(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0:
        return "assumption, "
    else:
        return "" # TODO : gestion erreur ex raise user_error

@action(_("Reductio ad absurdum"))
def action_absurdum(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0:
        return "by_contradiction {0}, ".format(utils.get_new_hyp()) 
    else:
        return "" # TODO : gestion erreur ex raise user_error

@action(_("Case-based reasoning"))
def action_cbr(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0:
        h1 = utils.get_new_hyp()
        h2 = utils.get_new_hyp()
        case = "0 = 0" # TODO : pop-up qui demande sur quelle propriété on veut faire une disjonction de cas
        return "cases (em ({0})) with {1} {2}".format(case, h1, h2)
    else:
        return "" # TODO : gestion erreur ex raise user_error

@action(_("Proof by contrapositive"))
def action_contrapose(goal : Goal, l : [PropObj]):
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0:
        if goal.target.math_type.node == "PROP_IMPLIES":
            return "contrapose, "
    return "" # TODO : gestion erreur ex raise user_error

@action(_("Use axiom of choice"))
def action_choice(goal):
    return ""

