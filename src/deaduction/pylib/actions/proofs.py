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
from deaduction.pylib.actions.exceptions import InputType, MissingParametersError, WrongUserInput
from deaduction.pylib.actions.actiondef import action
from deaduction.pylib.mathobj.PropObj import PropObj
from deaduction.pylib.mathobj.proof_state import Goal

@action(_("Case-based reasoning"), _("CASES")) # TODO : dire à Florian de rajouter open classical et local attribute [instance] classical.prop_decidable dans le fichier lean
def action_cbr(goal : Goal, l : [PropObj], user_input : [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0:
        if user_input == []:
            raise MissingParametersError(InputType.Text, title = _("cases"), output = _("Enter the case you want to discriminate on:")) #TODO : apprendre l'anglais
        else:
            h1 = utils.get_new_hyp()
            h2 = utils.get_new_hyp()
        return "cases (em ({0})) with {1} {2}".format(user_input[0], h1, h2)
    else:
        raise WrongUserInput

@action(_("Proof by contrapositive"), "¬Q ⇒ ¬P")
def action_contrapose(goal : Goal, l : [PropObj]):
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0:
        if goal.target.math_type.node == "PROP_IMPLIES":
            return "contrapose, "
    raise WrongUserInput

@action(_("Reductio ad absurdum"), _('0=1'))
def action_absurdum(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0:
        return "contradiction <|> by_contradiction {0}, ".format(utils.get_new_hyp()) 
    else:
        return "contradiction, "


@action(_("Introduce new object"), "+")
def action_new_object(goal : Goal, l : [PropObj], user_input : [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(user_input) == 0:
        raise MissingParametersError(InputType.Text, title = "+", output = _("Introduce new object:"))
    else:
        x = utils.get_new_var()
        return "let {0} := {1}, ".format(x, user_input[0])

@action(_("Assumption"), "¯\_(ツ)_/¯")
def action_assumption(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 0:
        return "assumption <|> refl, "
    else:
        raise WrongUserInput

        
#@action(_("Proof by induction"))
#def action_induction(goal : Goal, l : [PropObj]):
#    raise WrongUserInput

#@action(_("Use axiom of choice"))
#def action_choice(goal):
#    raise WrongUserInput

