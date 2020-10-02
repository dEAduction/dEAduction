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
                                            action,
                                            format_orelse)
from deaduction.pylib.mathobj   import (    MathObject,
                                            Goal)

@action(_("Let the user choose a proof method"), _("Use proof method"))
def action_use_proof_method(goal : Goal, l : [MathObject], user_input : [str] = []) -> str:
    if user_input == []:
        raise MissingParametersError(InputType.Choice,
            [_("Case-based reasoning"),
            _("Proof by contrapositive"),
            _("Reductio ad absurdum")],
            title = "Proof method",
            output = _("Choose which proof method you want to use:"))
    else:
        method = user_input[0]
        del user_input[0]
        if method == _("Case-based reasoning"):
            return method_cbr(goal, l, user_input)
        if method == _("Proof by contrapositive"):
            return method_contrapose(goal, l)
        if method == _("Reductio ad absurdum"):
            return method_absurdum(goal, l)
    raise WrongUserInput
    
def method_cbr(goal : Goal, l : [MathObject], user_input : [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of MathObject arguments preselected by the user
    :return: string of lean code
    """
    possible_codes = []
    if len(l) == 0:
        if user_input == []:
            raise MissingParametersError(InputType.Text, title = _("cases"), output = _("Enter the case you want to discriminate on:"))
        else:
            h1 = utils.get_new_hyp()
            h2 = utils.get_new_hyp()
            possible_codes.append("cases (classical.em ({0})) with {1} {2}".format(user_input[0], h1, h2))
    return format_orelse(possible_codes)

def method_contrapose(goal : Goal, l : [MathObject]):
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of MathObject arguments preselected by the user
    :return: string of lean code
    """
    possible_codes = []
    if len(l) == 0:
        if goal.target.math_type.node == "PROP_IMPLIES":
            possible_codes.append("contrapose")
    return format_orelse(possible_codes)

def method_absurdum(goal : Goal, l : [MathObject]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of MathObject arguments preselected by the user
    :return: string of lean code
    """
    possible_codes = []
    if len(l) == 0:
        new_h = utils.get_new_hyp()
        possible_codes.append(f'by_contradiction {new_h}')
    return format_orelse(possible_codes)
    


@action(_("If a hypothesis of form ∀ a ∈ A, ∃ b ∈ B, P(a,b) has been previously selected: use the axiom of choice to introduce a new function f : A → B and add ∀ a ∈ A, P(a, f(a)) to the properties"), _("CREATE FUN"))
def action_choice(goal : Goal, l : [MathObject]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of MathObject arguments preselected by the user
    :return: string of lean code
    """
    possible_codes = []
    if len(l) == 1:
        h = l[0].info["name"]
        hf = utils.get_new_hyp()
        f = utils.get_new_fun()
        possible_codes.append(f'cases classical.axiom_of_choice {h} with {f} {hf}, dsimp at {hf}, dsimp at {f}')
    return format_orelse(possible_codes)        
        
@action(_("Introduce new object\nIntroduce new subgoal: transform the current target into the input target and add this to the properties of the future goal."), "+")
def action_new_object(goal : Goal, l : [MathObject], user_input : [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of MathObject arguments preselected by the user
    :return: string of lean code
    """
    possible_codes = []
    if len(user_input) == 0:
        raise MissingParametersError(InputType.Choice,
            [_("new object"),_("subgoal")],
            title = "+",
            output = _("Choose what you want to introduce:"))
    if user_input[0] == _("new object"):
        if len(user_input) == 1:
            raise MissingParametersError(InputType.Text,
                title = "+",
                output = _("Introduce new object:"))
        else:
            x = utils.get_new_var()
            h = utils.get_new_hyp()
            possible_codes.append("let {0} := {1}, have {2} : {0} = {1}, refl, ".format(x, user_input[1], h))
    if user_input[0] == _("subgoal"):
        if len(user_input) == 1:
            raise MissingParametersError(InputType.Text,
                title = "+",
                output = _("Introduce new subgoal:"))
        else:
            h = utils.get_new_hyp()
            possible_codes.append("have {0} : ({1}), ".format(h, user_input[1]))
    return format_orelse(possible_codes)

@action(_("Assumption"), "¯\_(ツ)_/¯")
def action_assumption(goal : Goal, l : [MathObject]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of MathObject arguments preselected by the user
    :return: string of lean code
    """

    possible_codes = []
    if len(l) == 0:
        possible_codes.append('assumption')
        possible_codes.append('contradiction')
        if goal.target.math_type.node == "PROP_EQUAL":
            if goal.target.math_type.children[0] == goal.target.math_type.children[1]: #TODO : tester si il y a assez d'enfants
                possible_codes.append('refl')
    if len(l) == 1:
        possible_codes.append(f'apply {l[0].info["name"]}')
    return format_orelse(possible_codes)

        
#@action(_("Proof by induction"))
#def action_induction(goal : Goal, l : [MathObject]):
#    raise WrongUserInput

