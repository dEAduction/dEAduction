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

from deaduction.config.config import user_config, _

import deaduction.pylib.actions.utils as utils
from deaduction.pylib.actions import (InputType,
                                      MissingParametersError,
                                      WrongUserInput,
                                      action,
                                      format_orelse)
from deaduction.pylib.mathobj import (MathObject,
                                      Goal,
                                      get_new_hyp)

# turn logic_button_texts into a dictionary
proof_list= ['proof_methods', 'choice', 'new_object', 'assumption']
lbt = user_config.get('proof_button_texts').split(', ')
proof_button_texts = {}
for key, value in zip(proof_list, lbt):
    proof_button_texts[key] = value


@action(user_config.get('tooltip_proof_methods'),
        proof_button_texts['proof_methods'])
def action_use_proof_methods(goal: Goal, l: [MathObject],
                            user_input: [str] = []) -> str:
    # parameters
    allow_proof_by_sorry = user_config.getboolean('allow_proof_by_sorry')

    # 1st call, choose proof method
    if not user_input:
        choices = [('1', _("Case-based reasoning")),
                   ('2', _("Proof by contrapositive")),
                   ('3', _("Reductio ad absurdum"))]
        if allow_proof_by_sorry:
            choices.append(('4', _("Admit current sub-goal!")))
        raise MissingParametersError(InputType.Choice,
                                     choices,
                                     title="Choose proof method",
                                     output=_("Which proof method?")
                                     )
    # 2nd call, call the adequate proof method. len(user_input) = 1.
    else:
        method = user_input[0] + 1
        if method == 1:
            # if len(user_input) > 1:
            #     del user_input[0]   # we do not need this user_input anymore
            #     # but we need the next choice
            return method_cbr(goal, l, user_input)
        if method == 2:
            return method_contrapose(goal, l)
        if method == 3:
            return method_absurdum(goal, l)
        if method == 4:
            return method_sorry(goal, l)
    raise WrongUserInput


def method_cbr(goal: Goal, l: [MathObject], user_input: [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of MathObject arguments preselected by the user
    :return: string of lean code
    """
    possible_codes = []
    if len(l) == 0:
        # NB: user_input[1] contains the needed property
        if len(user_input) == 1:
            raise MissingParametersError(
                 InputType.Text,
                 title=_("cases"),
                 output=_("Enter the property you want to discriminate on:")
                                        )
        else:
            h0 = user_input[1]
            h1 = get_new_hyp(goal)
            h2 = get_new_hyp(goal)
            possible_codes.append(
                f"cases (classical.em ({h0})) with {h1} {h2}")
    else:
        h0 = l[0].info['name']
        h1 = get_new_hyp(goal)
        h2 = get_new_hyp(goal)
        possible_codes.append(
            f"cases (classical.em ({h0})) with {h1} {h2}")

    return format_orelse(possible_codes)


def method_contrapose(goal: Goal, l: [MathObject]) -> str:
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


def method_absurdum(goal: Goal, l: [MathObject]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    :param l: list of MathObject arguments preselected by the user
    :return: string of lean code
    """
    possible_codes = []
    if len(l) == 0:
        new_h = get_new_hyp(goal)
        possible_codes.append(f'by_contradiction {new_h}')
    return format_orelse(possible_codes)


def method_sorry(goal: Goal, l: [MathObject]) -> str:
    """
    Close the current sub-goal by sending the 'sorry' code
    """
    possible_codes = ['sorry']
    return format_orelse(possible_codes)


@action(user_config.get('tooltip_choice'),
        proof_button_texts['choice'])
def action_choice(goal: Goal, l: [MathObject]) -> str:
    """
    Translate into string of lean code corresponding to the action

If a hypothesis of form ∀ a ∈ A, ∃ b ∈ B, P(a,b) has been previously selected:
use the axiom of choice to introduce a new function f : A → B
and add ∀ a ∈ A, P(a, f(a)) to the properties

    :param l: list of MathObject arguments preselected by the user
    :return: string of lean code
    """
    possible_codes = []
    if len(l) == 1:
        h = l[0].info["name"]
        hf = get_new_hyp(goal)
        f = utils.get_new_fun()
        possible_codes.append(
            f'cases classical.axiom_of_choice {h} with {f} {hf}, dsimp at {hf}, dsimp at {f}')
    return format_orelse(possible_codes)


@action(user_config.get('tooltip_new_object'),
        proof_button_texts['new_object'])
def action_new_object(goal: Goal, l: [MathObject],
                      user_input: [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action

    Introduce new object\nIntroduce new subgoal:
transform the current target into the input target
and add this to the properties of the future goal.

    :param l: list of MathObject arguments preselected by the user
    :return: string of lean code
    """
    possible_codes = []
    if len(user_input) == 0:
        raise MissingParametersError(InputType.Choice,
                             [(_("Object"), _("Introduce a new object")),
                              (_("Sub-goal"), _("Introduce a new "
                                                "intermediate sub-goal"))],
                             title="+",
                             output=_("Choose what to introduce:"))
    if user_input[0] == 0:  # choice = new object
        if len(user_input) == 1:  # ask for new object
            raise MissingParametersError(InputType.Text,
                                         title="+",
                                         output=_("Introduce new object:"))
        else:  # send code
            x = utils.get_new_var()
            h = get_new_hyp(goal)
            possible_codes.append(
                f"let {x} := {user_input[1]}, "
                f"have {h} : {x} = {user_input[1]}, refl, ")
    if user_input[0] == 1:  # new sub-goal
        if len(user_input) == 1:
            raise MissingParametersError(InputType.Text,
                                         title="+",
                                         output=_("Introduce new subgoal:"))
        else:
            h = get_new_hyp(goal)
            possible_codes.append(f"have {h} : ({user_input[1]}),")
    return format_orelse(possible_codes)


@action(user_config.get('tooltip_assumption'),
        proof_button_texts['assumption'])
def action_assumption(goal: Goal, l: [MathObject]) -> str:
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
            if goal.target.math_type.children[0] == \
                    goal.target.math_type.children[1]:
                possible_codes.append('refl')
        possible_codes.append('ac_reflexivity')
        possible_codes.append('apply eq.symm, assumption')
        possible_codes.append('apply iff.symm, assumption')
    if len(l) == 1:
        possible_codes.append(f'apply {l[0].info["name"]}')
    return format_orelse(possible_codes)

# @action(_("Proof by induction"))
# def action_induction(goal : Goal, l : [MathObject]):
#    raise WrongUserInput
