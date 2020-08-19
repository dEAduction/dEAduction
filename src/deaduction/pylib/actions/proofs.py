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
from deaduction.pylib.actions   import (    InputType,
                                            MissingParametersError,
                                            WrongUserInput,
                                            action)
from deaduction.pylib.mathobj   import (    PropObj,
                                            Goal)

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
            return "cases (classical.em ({0})) with {1} {2}, ".format(user_input[0], h1, h2)
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


@action(_("If a hypothesis of form ∀ a ∈ A, ∃ b ∈ B, P(a,b) has been previously selected, introduce a new function f : A → B and add ∀ a ∈ A, P(a, f(a)) to the properties"), _("CREATE FUN"))
def action_choice(goal : Goal, l : [PropObj]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(l) == 1:
        h = l[0].lean_data["name"]
        hf = utils.get_new_hyp()
        f = utils.get_new_fun()
        return f'cases classical.axiom_of_choice {h} with {f} {hf}, dsimp at {hf}, dsimp at {f}, '
        # TODO : demander à FLR une façon plus jolie avec tactic choice par exemple plutôt que faire dsimp après
    else:
        raise WrongUserInput
        
        
@action(_("Introduce new object\nIntroduce new subgoal: transform the current target into the input target and add this to the properties of the future goal."), "+")
def action_new_object(goal : Goal, l : [PropObj], user_input : [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of PropObj arguments preselected by the user
    :return: string of lean code
    """
    if len(user_input) == 0:
        raise MissingParametersError(InputType.Choice, [_("new object"), _("subgoal")], title = "+", output = _("Choose what you want to introduce:"))
    if user_input[0] == _("new object"):
        if len(user_input) == 1:
            raise MissingParametersError(InputType.Text, title = "+", output = _("Introduce new object:"))
        else:
            x = utils.get_new_var()
            h = utils.get_new_hyp()
            return "let {0} := {1}, have {2} : {0} = {1}, refl, ".format(x, user_input[1], h)
    if user_input[0] == _("subgoal"):
        if len(user_input) == 1:
            raise MissingParametersError(InputType.Text, title = "+", output = _("Introduce new subgoal:"))
        else:
            h = utils.get_new_hyp()
            return "have {0} : ({1}), ".format(h, user_input[1])




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

