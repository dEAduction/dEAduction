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

import logging
from typing import Union

from deaduction.config       import (user_config,
                                     tooltips_config,
                                     _)

import deaduction.pylib.actions.utils as utils
from deaduction.pylib.actions import (InputType,
                                      MissingParametersError,
                                      WrongUserInput,
                                      action,
                                      format_orelse,
                                      get_new_var,
                                      solve1_wrap,
                                      apply_exists,
                                      apply_and,
                                      apply_or)
from deaduction.pylib.mathobj import (MathObject,
                                      Goal,
                                      get_new_hyp,
                                      give_global_name,
                                      NO_MATH_TYPE,
                                      NUMBER_SETS_LIST)

log = logging.getLogger(__name__)


# Turn proof_button_texts into a dictionary
proof_list = ['action_apply', 'proof_methods', 'new_object']
lbt = tooltips_config.get('proof_button_texts').split(', ')
proof_button_texts = {}
for key, value in zip(proof_list, lbt):
    proof_button_texts[key] = value


@action(tooltips_config.get('tooltip_proof_methods'),
        proof_button_texts['proof_methods'])
def action_use_proof_methods(goal: Goal, l: [MathObject],
                            user_input: [str] = []) -> str:
    # parameters
    allow_proof_by_sorry = user_config.getboolean('allow_proof_by_sorry')

    # 1st call, choose proof method
    if not user_input:
        choices = [('1', _("Case-based reasoning")),
                   ('2', _("Proof by contrapositive")),
                   ('3', _("Proof by contradiction"))]
        if allow_proof_by_sorry:
            choices.append(('4', _("Admit current sub-goal!")))
        raise MissingParametersError(InputType.Choice,
                                     choices,
                                     title=_("Choose proof method"),
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


def introduce_fun(goal: Goal, l: [MathObject]) -> str:
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
        # finding expected math_type for the new function
        universal_property = l[0]
        if universal_property.is_for_all():
            source_type = universal_property.math_type.children[0]
            exist_property = universal_property.math_type.children[2]
            if exist_property.is_exists(is_math_type=True):
                target_type = exist_property.children[0]
                math_type = MathObject(node="FUNCTION",
                                       info={},
                                       children=[source_type, target_type],
                                       math_type=NO_MATH_TYPE)

                hf = get_new_hyp(goal)
                f = give_global_name(math_type, goal)
                possible_codes.append(f'cases classical.axiom_of_choice {h} '
                                      f'with {f} {hf}, dsimp at {hf}, '
                                      f'dsimp at {f}')
                return format_orelse(possible_codes)
    raise WrongUserInput


@action(tooltips_config.get('tooltip_new_object'),
        proof_button_texts['new_object'])
def action_new_object(goal: Goal, l: [MathObject],
                      user_input: [str] = []) -> str:
    """
    Introduce new object / sub-goal / function

    :param l: list of MathObject arguments preselected by the user
    :return: string of lean code
    """
    possible_codes = []
    # Choose between object/sub-goal/function
    if len(user_input) == 0:
        raise MissingParametersError(InputType.Choice,
                             [(_("Object"), _("Introduce a new object")),
                              (_("Goal"), _("Introduce a new "
                                                "intermediate sub-goal")),
                              (_("Function"), _("Introduce a new "
                                                "function"))],
                             title=_("New object"),
                             output=_("Choose what to introduce:"))
    # Choice = new object
    if user_input[0] == 0:
        if len(user_input) == 1:  # ask for new object
            raise MissingParametersError(InputType.Text,
                                         title="+",
                                         output=_("Introduce new object:"))
        else:  # send code
            x = get_new_var()  # fixme: ask the user for a name
            h = get_new_hyp(goal)
            possible_codes.append(
                f"let {x} := {user_input[1]}, "
                f"have {h} : {x} = {user_input[1]}, refl, ")

    # Choice = new sub-goal
    elif user_input[0] == 1:
        if len(user_input) == 1:
            raise MissingParametersError(InputType.Text,
                                         title="+",
                                         output=_("Introduce new subgoal:"))
        else:
            h = get_new_hyp(goal)
            possible_codes.append(f"have {h} : ({user_input[1]}),")

    # Choice = new function
    elif user_input[0] == 2:
        return introduce_fun(goal, l)
    return format_orelse(possible_codes)


#########
# APPLY #
#########

def apply_implicate(goal: Goal, l: [MathObject]):
    possible_codes = []
    h_selected = l[0].info["name"]
    possible_codes.append(f'apply {h_selected}')
    return possible_codes


def have(for_all: MathObject,
         variable_name: str,
         hypo_name) -> [str]:
    # TODO: adapt for more than 1 variable
    h_selected = for_all.info["name"]
    x_selected = variable_name
    h = hypo_name
    possible_codes = []
    # try with up to 4 implicit parameters
    possible_codes.append(f'have {h} := {h_selected} {x_selected}')
    possible_codes.append(f'have {h} := {h_selected} _ {x_selected}')
    possible_codes.append(f'have {h} := {h_selected} _ _ {x_selected}')
    possible_codes.append(f'have {h} := {h_selected} _ _ _ {x_selected}')
    possible_codes.append(f'have {h} := {h_selected} _ _ _ _ {x_selected}')

    possible_codes.append(f'have {h} := @{h_selected} {x_selected}')
    possible_codes.append(f'have {h} := @{h_selected} _ {x_selected}')
    possible_codes.append(f'have {h} := @{h_selected} _ _ {x_selected}')
    possible_codes.append(f'have {h} := @{h_selected} _ _ _ {x_selected}')
    possible_codes.append(
        f'have {h} := @{h_selected} _ _ _ _ {x_selected}')

    return possible_codes


def inequality_from_pattern_matching(math_object: MathObject,
                                     variable: MathObject):
    """
    Check if math_object.math_type has the form
    ∀ x:X, (x R ... ==> ...)
    where R is some inequality relation, and if this statement may be
    applied to variable. If so, return inequality with x replaced by variable
    """
    inequality = None
    if math_object.is_for_all():
        math_type, var, body = math_object.math_type.children
        # NB: following line does not work because of coercions
        # if var.math_type == variable.math_type:
        if body.is_implication(is_math_type=True):
            premise = body.children[0]  # children (2,0)
            if (premise.is_inequality(is_math_type=True) and
                    var == premise.children[0]):
                children = [variable, premise.children[1]]
                inequality = MathObject(node=premise.node,
                                        info={},
                                        children=children,
                                        math_type=premise.math_type)
    return inequality


def apply_implicate_to_hyp(goal: Goal, l: [MathObject], user_input=None):
    """
    Try to apply last selected property on the other ones.
    :param l: list of 1-3 MathObjects
    :param user_input: in case of 1 MathObject, list of 1 str
    :return:
    """
    possible_codes = []
    if len(l) == 1 and user_input:
        item = user_input[0]
        item = add_type_indication(item)  # e.g. (0:ℝ)
        potential_var = MathObject(node="LOCAL_CONSTANT",
                                   info={'name': item},
                                   children=[],
                                   math_type=None)
        l.insert(0,potential_var)
        # Now len(l) == 2 so next test will be positive
    if len(l) == 2:
        math_object = l[-1]
        potential_var = l[0]
        # TODO: replace by pattern matching
        # Check for "∀x>0" (and variations)
        inequality = inequality_from_pattern_matching(math_object,
                                                      potential_var)
        h1 = get_new_hyp(goal)
        # TODO: structure this into:
        #  (1) try { have <INEQ>, by <compute> , and_then (have.. or_else ...)
        #  (2) or_else {(have.. or_else ...)}
        #  For the moment, the first have is tried many time by Lean,
        #  which is highly inefficient
        if inequality:
            # Add type indication
            math_type = inequality.children[1].math_type
            variable = inequality.children[0]
            variable = add_type_indication(variable, math_type)
            h2 = get_new_hyp(goal)
            display_inequality = inequality.to_display(
                is_math_type=False,
                format_='lean')
            code = f"have {h1} : {display_inequality}, "
            code += "by { try {norm_num at *}, try {compute_n 10}}"
            code = "try { " + code + "}, "
            # Then apply to h2 instead of x
            new_codes = have(math_object, h1, h2)
            possible_codes = [code + other_code
                              for other_code in new_codes]
            # And try this combination before standard "have"
        possible_codes.extend(have(math_object,
                                   potential_var.info['name'],
                                   h1))

    elif len(l) == 3:
        h = get_new_hyp(goal)
        h_selected = l[-1].info["name"]
        x_selected = l[0].info["name"]
        y_selected = l[1].info["name"]
        # try to apply "forall x,y , P(x,y)" to x and y
        possible_codes.append(
            f'have {h} := {h_selected} {x_selected} {y_selected}')
        possible_codes.append(
            f'have {h} := {h_selected} _ {x_selected} {y_selected}')
        possible_codes.append(
            f'have {h} := {h_selected} _ _ {x_selected} {y_selected}')
        possible_codes.append(
            f'have {h} := {h_selected} _ _ _ {x_selected} {y_selected}')
        possible_codes.append(
            f'have {h} := {h_selected} _ _ _ _ {x_selected} {y_selected}')

    return possible_codes


def apply_substitute(goal: Goal, l: [MathObject], user_input: [int]):
    """
    Try to rewrite the goal or the first selected property using the last
    selected property
    """
    possible_codes = []
    if len(l) == 1:
        heq = l[0]
    else:
        heq = l[-1]
    left_term = heq.math_type.children[0]
    right_term = heq.math_type.children[1]
    choices = [(left_term.to_display(),
                f'Replace by {right_term.to_display()}'),
               (right_term.to_display(),
                f'Replace by {left_term.to_display()}')]
            
    if len(l) == 1:
        h = l[0].info["name"]
        if len(user_input) > 0 and user_input[0] <= 1:
            if user_input[0] == 1:
                possible_codes.append(f'rw <- {h}')
            else:
                possible_codes.append(f'rw {h}')
        else:
            if goal.target.math_type.contains(left_term) and \
                    goal.target.math_type.contains(right_term):
                
                raise MissingParametersError(
                    InputType.Choice,
                    choices, 
                    title=_("Precision of substitution"),
                    output=_("Choose which expression you want to replace"))
                 
            possible_codes.append(f'rw {h}')
            possible_codes.append(f'rw <- {h}')
    
    if len(l) == 2:
        h = l[0].info["name"]
        heq = l[-1].info["name"]
        if len(user_input) > 0 and user_input[0] <= 1:
            if user_input[0] == 1:
                possible_codes.append(f'rw <- {heq} at {h}')
            else:
                possible_codes.append(f'rw {heq} at {h}')
        else:     
            if l[0].math_type.contains(left_term) and \
                    l[0].math_type.contains(right_term):
                    
                raise MissingParametersError(
                    InputType.Choice,
                    choices, 
                    title=_("Precision of substitution"),
                    output=_("Choose which expression you want to replace"))
                
        possible_codes.append(f'rw <- {heq} at {h}')
        possible_codes.append(f'rw {heq} at {h}')

        h, heq = heq, h
        possible_codes.append(f'rw <- {heq} at {h}')
        possible_codes.append(f'rw {heq} at {h}')

    return possible_codes


def apply_function(goal: Goal, l: [MathObject]):
    """
    Apply l[-1], which is assumed to be a function f, to previous elements of
    l, which can be:
    - an equality
    - an object x (then create the new object f(x) )
    """
    log.debug('Applying function')
    possible_codes = []

    if len(l) == 1:
        raise WrongUserInput
    
    # let us check the input is indeed a function
    function = l[-1]
    # if function.math_type.node != "FUNCTION":
    #    raise WrongUserInput
    
    f = function.info["name"]
    Y = l[-1].math_type.children[1]
    
    while (len(l) != 1):
        new_h = get_new_hyp(goal)
        
        # if function applied to equality
        if l[0].math_type.is_prop():
            h = l[0].info["name"]
            possible_codes.append(f'have {new_h} := congr_arg {f} {h}')
            
        # if function applied to element x:
        # create new element y and new equality y=f(x)
        else:
            x = l[0].info["name"]
            y = give_global_name(goal=goal,
                    math_type=Y,
                    hints=[Y.info["name"].lower()])
            possible_codes.append(f'set {y} := {f} {x} with {new_h}')
        l = l[1:]
    return format_orelse(possible_codes)


@action(tooltips_config.get('tooltip_apply'),
        proof_button_texts['action_apply'])
def action_apply(goal: Goal, l: [MathObject], user_input: [str] = []):
    """
    Translate into string of lean code corresponding to the action
    Function explain_how_to_apply should reflect the actions

    Apply last selected item on the other selected

    test for last selected item l[-1], and call functions accordingly:
    - apply_function, if item is a function
    - apply_susbtitute, if item can_be_used_for_substitution
    - apply_implicate, if item is an implication or a universal property
    - apply_exists, if item is an existential property

    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """

    # fixme: rewrite to provide meaningful error messages
    possible_codes = []
    error = ""

    if not l:
        raise WrongUserInput(error=_("no property selected"))

    # Now len(l) > 0
    prop = l[-1]  # property to be applied
    # If user wants to apply a function
    if prop.is_function():
        return apply_function(goal, l)

    # Determines which kind of property the user wants to apply
    if prop.can_be_used_for_substitution():
        if len(l) == 1 or (len(l) > 1 and l[0].math_type.is_prop()):
            possible_codes.extend(apply_substitute(goal, l, user_input))

    # todo: allow apply_implicate_hyp even when property is not explicitly
    #  an implication
    if prop.is_implication() and len(l) == 1:
        possible_codes.extend(apply_implicate(goal, l))
    if prop.is_for_all() and len(l) == 1:
        if len(user_input) != 1:
            raise MissingParametersError(InputType.Text,
                                         title=_("Apply"),
                                         output=_(
                                             "Enter element on which you "
                                             "want to apply:"))
        possible_codes.extend(apply_implicate_to_hyp(goal, l, user_input))
    elif prop.is_implication() or prop.is_for_all():
        if len(l) == 2 or len(l) == 3:
            possible_codes.extend(apply_implicate_to_hyp(goal, l))
            
    if len(l) == 1 and user_can_apply(l[0]):
        if prop.is_exists():
            possible_codes.append(apply_exists(goal, l))
        if prop.is_and():
            possible_codes.append(apply_and(goal, l))
        if prop.is_or():
            possible_codes.append(apply_or(goal, l, user_input))
    if possible_codes:
        return format_orelse(possible_codes)
    else:
        error = "I cannot apply this"  # fixme!!
        raise WrongUserInput(error)


################################
# Captions for 'APPLY' buttons #
################################

applicable_nodes = {'FUNCTION',  # to apply a function
                    'PROP_EQUAL', 'PROP_IFF', 'QUANT_∀',  # for substitution
                    'PROP_IMPLIES',
                    # for obvious action:
                    'QUANT_∃', 'QUANT_∃!', 'PROP_AND', 'PROP_OR'}


def user_can_apply(math_object) -> bool:
    """
    True if math_object may be applied
    (--> an 'APPLY' button may be created)
    """
    return math_object.math_type.node in applicable_nodes


def explain_how_to_apply(math_object: MathObject, dynamic=False, long=False) \
        -> str:
    """
    Provide explanations of how the math_object may be applied
    (--> to serve as tooltip or help)
    :param math_object:
    :param dynamic: if False, caption depends only on main node
    :param long: boolean
    TODO: implement dynamic and long tooltips
    """
    captions = []  # default value

    # the following 4 cases are mutually exclusive
    if math_object.is_function():
        captions.append(tooltips_config.get('tooltip_apply_function'))

    elif math_object.is_for_all():
        captions.append(tooltips_config.get('tooltip_apply_for_all'))

    elif math_object.is_exists():
        captions.append(tooltips_config.get('tooltip_apply_exists'))

    elif math_object.is_and():
        captions.append(tooltips_config.get('tooltip_apply_and'))

    # additional line
    if math_object.can_be_used_for_implication():
        captions.append(tooltips_config.get('tooltip_apply_implication'))

    elif math_object.can_be_used_for_substitution():
        captions.append(tooltips_config.get('tooltip_apply_substitute'))

    return captions


# @action(_("Proof by induction"))
# def action_induction(goal : Goal, l : [MathObject]):
#    raise WrongUserInput


#########
# UTILS #
#########

def which_number_set(string: str):
    """
    Return 'ℕ', 'ℤ', 'ℚ', 'ℝ' if string represents a number, else None
    """
    ind = -1
    if '.' in string or '/' in string:
        ind = 2  # at least Q
    string = string.replace('.', '')
    string = string.replace('/', '')
    if not string.isdigit():
        return None
    else:
        return NUMBER_SETS_LIST[ind]


def add_type_indication(item: Union[str, MathObject],
                        math_type: MathObject=None) -> Union[str, MathObject]:
    """
    Add type indication for Lean. e.g.
    '0' -> (0:ℝ)
    'x' -> (x:ℝ)
    :param item:        either a string (provided by user in TextDialog) or
    MathObject
    :param math_type:   math_type indication to add. If None, largest number
    set used in current context will be indicated
    :return: either     string or MathObject, with type indication in name
    """
    if math_type:
        number_type = math_type.which_number_set(is_math_type=True)
    if isinstance(item, str):
        number_set = which_number_set(item)
        if number_set and ':' not in item:
            if not math_type:
                MathObject.add_numbers_set(number_set)
                # Add type indication = largest set of numbers among used
                number_type = MathObject.number_sets[-1]
            item = f"({item}:{number_type})"  # e.g. (0:ℝ)
        return item
    else:
        if not math_type:
            number_type = MathObject.number_sets[-1]
        if hasattr(item, 'info'):
            name = item.display_name
            # Do not put 2 type indications!!
            if (':' not in name
                    and hasattr(item, 'info')):
                item.info['name'] = f"({name}:{number_type})"
        return item
