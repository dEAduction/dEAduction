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
from typing import Union

from deaduction.pylib.text        import tooltips
from deaduction.pylib.config.i18n import _
from deaduction.pylib.actions     import (action,
                                          InputType,
                                          MissingParametersError,
                                          WrongUserInput,
                                          LeanCombinator,
                                          CodeForLean
                                          )

from deaduction.pylib.mathobj     import (MathObject,
                                          Goal,
                                          give_global_name,
                                          get_new_hyp,
                                          NUMBER_SETS_LIST)

import deaduction.pylib.config.vars as cvars

log = logging.getLogger("logic")  # uncomment to use


# Get buttons symbols from config file
action_list = ['action_and', 'action_or', 'action_negate',
               'action_implicate', 'action_iff', 'action_forall',
               'action_exists']

if cvars.get('display.use_logic_button_symbols'):
    logic_button_texts = cvars.get('display.logic_button_symbols')
else:
    logic_button_texts = tooltips.get('logic_button_texts')
# turn logic_button_texts into a dictionary
lbt = logic_button_texts.split(', ')
logic_button_texts = {}
for key, value in zip(action_list, lbt):
    logic_button_texts[key] = value


#######
# AND #
#######

def construct_and(goal: Goal, user_input: [str]):
    """
Split the target 'P AND Q' into two sub-goals
    """
    possible_codes = []

    if not goal.target.is_and():
        raise WrongUserInput(error=_("target is not a conjunction 'P AND Q'"))
    left = goal.target.math_type.children[0].to_display()
    right = goal.target.math_type.children[1].to_display()
    choices = [(_("Left"), left), (_("Right"), right)]

    if not user_input:
        raise MissingParametersError(
            InputType.Choice,
            choices,
            title=_("Choose sub-goal"),
            output=_("Which property to prove first?"))

    if len(user_input) == 1:
        if user_input[0] == 1:
            if goal.target.math_type.node == "PROP_∃":
                # In this case, first rw target as a conjunction
                code = "rw exists_prop, rw and.comm, "
            else:
                code = "rw and.comm, "
        else:
            code = ""
        possible_codes.append(f'{code}split')

    return CodeForLean.or_else_from_list(possible_codes)


def apply_and(goal, l):
    """
Destruct a property 'P and Q'
Here l contains exactly one conjunction property
    """
    possible_codes = []
    h_selected = l[0].info["name"]
    h1 = get_new_hyp(goal)
    h2 = get_new_hyp(goal)
    possible_codes.append(f'cases {h_selected} with {h1} {h2}')
    return CodeForLean.or_else_from_list(possible_codes)


def construct_and_hyp(goal, selected_objects: [MathObject]):
    """
Construct 'P AND Q' from properties P and Q
Here l contains exactly two properties
    """
    possible_codes = []
    h1 = selected_objects[0].info["name"]
    h2 = selected_objects[1].info["name"]
    new_h = get_new_hyp(goal)
    possible_codes.append(f'have {new_h} := and.intro {h1} {h2}')
    return CodeForLean.or_else_from_list(possible_codes)


@action(tooltips.get('tooltip_and'),
        logic_button_texts['action_and'])
def action_and(goal: Goal,
               selected_objects: [MathObject],
               user_input: [str] = []
               ) -> str:
    """
    Translate into string of lean code corresponding to the action

If the target is of the form P AND Q:
    transform the current goal into two subgoals, P, then Q.
If a hypothesis of the form P AND Q has been previously selected:
    creates two new hypothesis P, and Q.
If two hypothesis P, then Q, have been previously selected:
    add the new hypothesis P AND Q to the properties.

    :param selected_objects:   list of MathObject preselected by user
    :return:    string of lean code
    """
    if len(selected_objects) == 0:
        return construct_and(goal, user_input)
    if len(selected_objects) == 1:
        if not selected_objects[0].is_and():
            raise WrongUserInput(error=_("selected property is not "
                                         "a conjunction 'P AND Q'"))
        else:
            return apply_and(goal, selected_objects)
    if len(selected_objects) == 2:
        if not (selected_objects[0].math_type.is_prop and
                selected_objects[1].math_type.is_prop):
            raise WrongUserInput(error=_("selected items are not properties"))
        else:
            return construct_and_hyp(goal, selected_objects)
    raise WrongUserInput(error=_("does not apply to more than two properties"))


# OR #
def construct_or(goal: Goal, user_input: [str]) -> str:
    """
When target is a disjunction 'P OR Q', choose to prove either P or Q
    """
    possible_codes = []

    if not goal.target.is_or():
        raise WrongUserInput(error=_("target is not a disjunction 'P OR Q'"))

    left = goal.target.math_type.children[0].to_display()
    right = goal.target.math_type.children[1].to_display()
    choices = [(_("Left"), left), (_("Right"), right)]

    if len(user_input) == 0:
        raise MissingParametersError(InputType.Choice,
                                     choices,
                                     title=_("Choose new goal"),
                                     output=_("Which property will you "
                                              "prove?"))

    if len(user_input) == 1:
        i = user_input[0]
        code = ["left", "right"][i]
        possible_codes.append(code)

    return CodeForLean.or_else_from_list(possible_codes)


def apply_or(goal, l: [MathObject], user_input: [str]) -> str:
    """
Engage in a proof by cases by applying a property 'P OR Q'
    """
    possible_codes = []
    if not l[0].is_or():
        raise WrongUserInput(error=_("Selected property is not "
                                     "a disjunction 'P OR Q'"))

    h_selected = l[0].info["name"]

    left = l[0].math_type.children[0].to_display()
    right = l[0].math_type.children[1].to_display()
    choices = [(_("Left"), left), (_("Right"), right)]

    if len(user_input) == 0:
        raise MissingParametersError(InputType.Choice,
                                     choices=choices,
                                     title=_("Choose case"),
                                     output=_("Which case to assume first?"))

    if len(user_input) == 1:
        if user_input[0] == 1:
            possible_codes.append(f'rw or.comm at {h_selected}, ')
        else:
            possible_codes.append("")

    h1 = get_new_hyp(goal)
    h2 = get_new_hyp(goal)
    possible_codes[0] += f'cases {h_selected} with {h1} {h2}'
    return CodeForLean.or_else_from_list(possible_codes)


def construct_or_on_hyp(goal: Goal, l: [MathObject], user_input: [str] = []):
    """
Construct a property 'P or Q' from property 'P' or property 'Q'
    """

    possible_codes = []
    if len(l) > 2:
        error = _("does not apply to more than two properties")
        raise WrongUserInput(error)
    hP = l[0].info["name"]
    P = l[0].math_type.to_display()

    if len(l) == 2:
        if not (l[0].math_type.is_prop() and l[1].math_type.is_prop()):
            error = _("selected items are not properties")
            raise WrongUserInput(error)
        else:
            Q = l[1].info["name"]
    elif len(l) == 1:
        if not l[0].math_type.is_prop():
            error = _("selected item is not a property")
            raise WrongUserInput(error)
        if len(user_input) == 0:
            raise MissingParametersError(InputType.Text,
                        title=_("Obtain 'P OR Q'"),
                        output=_("Enter the proposition you want to use:"))
        Q = user_input[0]
        user_input = user_input[1:]
        
    if len(user_input) == 0:
        raise MissingParametersError(
            InputType.Choice,
            [(_("Left"), f'({P}) OR ({Q})'), (_('Right'), f'({Q}) OR ({P})')],
            title=_("Choose side"),
            output=_(f'On which side do you want') + f' {P} ?')
    
    new_h = get_new_hyp(goal)
    if user_input[0] == 0:
        possible_codes.append(f'have {new_h} := @or.inl _ ({Q}) ({hP})')
    elif user_input[0] == 1:
        possible_codes.append(f'have {new_h} := @or.inr ({Q}) _ ({hP})')
    else:
        raise WrongUserInput("unexpected error")
    return CodeForLean.or_else_from_list(possible_codes)
            

@action(tooltips.get('tooltip_or'),
        logic_button_texts['action_or'])
def action_or(goal: Goal, l: [MathObject], user_input=[]) -> str:
    """
Translate into string of lean code corresponding to the action

If the target is of the form P OR Q:
    tranform the target in P (or Q) accordingly to the user's choice.
If a hypothesis of the form P OR Q has been previously selected:
    transform the current goal into two subgoals,
        one with P as a hypothesis,
        and another with Q as a hypothesis.

    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """

    if len(l) == 0:
        return construct_or(goal, user_input)
    if len(l) == 1:
        if l[0].is_or():
            return apply_or(goal, l, user_input)
        else:
            return construct_or_on_hyp(goal, l, user_input)
    if len(l) == 2:
        return construct_or_on_hyp(goal, l, user_input)
    raise WrongUserInput(error=_("does not apply to more than two properties"))


# NOT #

@action(tooltips.get('tooltip_not'),
        logic_button_texts['action_negate'])
def action_negate(goal: Goal, l: [MathObject]) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    If no hypothesis has been previously selected:
transform the target in an equivalent one which has its negations 'pushed'.
    If a hypothesis has been previously selected:
do the same to the hypothesis.

    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    possible_codes = []

    if len(l) == 0:
        if goal.target.math_type.node != "PROP_NOT":
            raise WrongUserInput(error=_("target is not a negation 'NOT P'"))
        possible_codes.append('push_neg')
    if len(l) == 1:
        if l[0].math_type.node != "PROP_NOT":
            error = _("selected property is not a negation 'NOT P'")
            raise WrongUserInput(error)
        h_selected = l[0].info["name"]
        possible_codes.append(f'push_neg at {h_selected}')
    return CodeForLean.or_else_from_list(possible_codes)


###############
# IMPLICATION #
###############
def construct_implicate(goal: Goal) -> CodeForLean:
    """
    Here the target is assumed to be an implication P ⇒ Q, P is added to the
    context, and the target becomes Q.
    """
    if not goal.target.is_implication():
        raise WrongUserInput(error=_("target is not an implication 'P ⇒ Q'"))
    else:
        h = get_new_hyp(goal)
        return CodeForLean.from_string(f'intro {h}')


def apply_implicate(goal: Goal, l: [MathObject]) -> CodeForLean:
    """
    Here l contains a single property which is an implication P ⇒ Q; if the
    target is Q then it will be replaced by P.
    """
    h_selected = l[0].info["name"]
    return CodeForLean.from_string(f'apply {h_selected}')


def have(arrow: MathObject, variable_names: [str], hypo_name) -> CodeForLean:
    """

    :param arrow:           a MathObject which is either an implication or a
                            universal property
    :param variable_names:  a list of names of variables (or properties) to
                            which "arrow" will be applied
    :param hypo_name:       a fresh name for the new property

    return:                 Lean Code to produce the wanted new property,
                            taking into account implicit parameters
    """

    h = hypo_name
    h_selected = arrow.info["name"]

    command = f'have {h} := {h_selected}'
    command_explicit = f'have {h} := @{h_selected}'

    arguments = ' '.join(variable_names)

    # try with up to 4 implicit parameters
    implicit_codes = [command + ' ' + arguments,
                      command + ' _ ' + arguments,
                      command + ' _ _ ' + arguments,
                      command + ' _ _ _ ' + arguments,
                      command + ' _ _ _ _ ' + arguments]

    explicit_codes = [command_explicit + ' ' + arguments,
                      command_explicit + ' _ ' + arguments,
                      command_explicit + ' _ _ ' + arguments,
                      command_explicit + ' _ _ _ ' + arguments,
                      command_explicit + ' _ _ _ _ ' + arguments]

    possible_codes = implicit_codes + explicit_codes

    return CodeForLean.or_else_from_list(possible_codes)


def apply_implicate_to_hyp(goal: Goal, l: [MathObject]) -> CodeForLean:
    """
    Try to apply last selected property on the other ones.
    The last property should be an implication
    (or equivalent to such after unfolding definitions)

    :param l: list of MathObjects
    :return:
    """

    implication = l[-1]
    hypo_name = get_new_hyp(goal)
    variable_names = [variable.info['name'] for variable in l[:-1]]

    return have(implication, variable_names, hypo_name)


@action(tooltips.get('tooltip_implies'),
        logic_button_texts['action_implicate'])
def action_implicate(goal: Goal, l: [MathObject]) -> CodeForLean:
    """
    Three cases:
    (1) No property selected:
        If the target is of the form P ⇒ Q: introduce the hypothesis P in
        the properties and transform the target into Q.
    (2) A single selected property, of the form P ⇒ Q: If the target was Q,
    it is replaced by P
    (3) Exactly two selected property, on of which is an implication P ⇒ Q
    and the other is P: Add Q to the context

    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        if not goal.target.is_implication():
            raise WrongUserInput(
                error=_("target is not an implication 'P ⇒ Q'"))
        else:
            return construct_implicate(goal)
    if len(l) == 1:
        if not l[0].can_be_used_for_implication():
            raise WrongUserInput(
                error=_("selected property is not an implication 'P ⇒ Q'"))
        else:
            return apply_implicate(goal, l)
    elif len(l) == 2:
        if not l[-1].can_be_used_for_implication():
            if not l[0].is_implication():
                raise WrongUserInput(error=_(
                    "selected properties are not implications 'P ⇒ Q'"
                                            ))
            else:  # l[0] is an implication but not l[1]: permute
                l.reverse()
        return apply_implicate_to_hyp(goal, l)
    # TODO: treat the case of more properties, including the possibility of
    #  P, Q and 'P and Q ⇒ R'
    raise WrongUserInput(error=_("does not apply to more than two properties"))


#######
# IFF #
#######

def construct_iff(goal: Goal, user_input: [str]):
    possible_codes = []
    if goal.target.math_type.node != "PROP_IFF":
        raise WrongUserInput(error=_("target is not an iff property 'P ⇔ Q'"))

    left = goal.target.math_type.children[0].to_display()
    right = goal.target.math_type.children[1].to_display()
    choices = [("⇒", f'({left}) ⇒ ({right})'), ("⇐", f'({right}) ⇒ ({left})')]

    if not user_input:
        raise MissingParametersError(
            InputType.Choice,
            choices,
            title=_("Choose sub-goal"),
            output=_("Which implication to prove first?"))

    elif len(user_input) == 1:
        if user_input[0] == 1:
            code = "rw iff.comm, "
        else:
            code = ""
        possible_codes.append(f'{code}split')
    else:
        raise WrongUserInput(error=_("undocumented error"))
    return CodeForLean.or_else_from_list(possible_codes)


def destruct_iff_on_hyp(goal: Goal, l: [MathObject]):
    """
    Split a property 'P iff Q' into two implications.
    len(l) should be 1.
    """
    possible_codes = []
    if l[0].math_type.node != "PROP_IFF":
        error = _("selected property is not an iff property 'P ⇔ Q'")
        raise WrongUserInput(error)
    h = l[0].info["name"]
    h1 = get_new_hyp(goal)
    h2 = get_new_hyp(goal)
    possible_codes.append(f'cases (iff_def.mp {h}) with {h1} {h2}')
    return CodeForLean.or_else_from_list(possible_codes)


def construct_iff_on_hyp(goal: Goal, l: [MathObject]):
    """
    Construct property 'P iff Q' from both implications.
    len(l) should be 2.
    """
    possible_codes = []

    if not (l[0].math_type.is_prop() and l[1].math_type.is_prop()):
        error = _("selected items should both be implications")
        raise WrongUserInput(error)

    new_h = get_new_hyp(goal)
    h1 = l[0].info["name"]
    h2 = l[1].info["name"]
    possible_codes.append(f'have {new_h} := iff.intro {h1} {h2}')
    return CodeForLean.or_else_from_list(possible_codes)


@action(tooltips.get('tooltip_iff'),
        logic_button_texts['action_iff'])
def action_iff(goal: Goal, l: [MathObject], user_input: [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    If the target is of the form P ⇔ Q:
introduce two subgoals, P⇒Q, and Q⇒P.

    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_iff(goal, user_input)
    if len(l) == 1:
        return destruct_iff_on_hyp(goal, l)
    if len(l) == 2:
        return construct_iff_on_hyp(goal, l)
    raise WrongUserInput(error=_("does not apply to more than two properties"))


###########
# FOR ALL #
###########

def construct_forall(goal) -> CodeForLean:
    """
    Here goal.target is assumed to be a universal property "∀ x:X, ...",
    and variable x is introduced.
    """

    math_object = goal.target.math_type
    body = math_object.children[2]
    math_type = math_object.children[0]
    if math_type.node == "PRODUCT":
        [math_type_1, math_type_2] = math_type.children
        x = give_global_name(goal=goal, math_type=math_type_1)
        y = give_global_name(goal=goal, math_type=math_type_2)
        possible_codes = CodeForLean.from_string(f'rintro ⟨ {x}, {y} ⟩')
        name = f"({x},{y})"
    else:
        x = give_global_name(goal=goal,
                             math_type=math_type,
                             )
        possible_codes = CodeForLean.from_string(f'intro {x}')
        name = f"{x}"
    possible_codes.add_success_message(_("Object") + " " + name + " "
                                       + _("added to the context"))

    if body.is_implication(is_math_type=True):
        # If math_object has the form
        # ∀ x:X, (x R ... ==> ...)
        # where R is some inequality relation
        # then introduce the inequality on top of x
        premise = body.children[0]  # children (2,0)
        if premise.is_inequality(is_math_type=True):
            h = get_new_hyp(goal)
            # Add and_then intro h
            possible_codes = possible_codes.and_then(f'intro {h}')

    return possible_codes


def inequality_from_pattern_matching(math_object: MathObject,
                                     variable: MathObject) -> MathObject:
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


def apply_forall(goal: Goal, l: [MathObject]) -> CodeForLean:
    """
    Try to apply last selected property on the other ones.
    The last property should be a universal property
    (or equivalent to such after unfolding definitions)

    :param l: list of MathObjects
    :return:
    """

    universal_property = l[-1]  # The property to be applied
    inequality_counter = 0
    # Variable_names will contain the list of variables and proofs of
    # inequalities that will be passed to universal_property
    variable_names = []
    code = CodeForLean.empty_code()
    for potential_var in l[:-1]:
        # TODO: replace by pattern matching
        # Check for "∀x>0" (and variations)
        inequality = inequality_from_pattern_matching(universal_property,
                                                      potential_var)
        variable_names.append(potential_var.info['name'])
        if inequality:
            inequality_counter += 1
            inequality_name = get_new_hyp(goal)
            variable_names.append(inequality_name)
            # TODO: search if inequality is not already in context, and if so,
            #  use it instead of re-proving (which leads to duplication)
            # Add type indication to the variable in inequality
            math_type = inequality.children[1].math_type
            # Even if variable is not used explicitly, this affects inequality:
            variable = inequality.children[0]
            variable = add_type_indication(variable, math_type)
            display_inequality = inequality.to_display(
                is_math_type=False,
                format_='lean')
            # Code I: state corresponding inequality #
            code = code.and_then(f"have {inequality_name}: "
                                 f"{display_inequality}")
            code = code.and_then("rotate")


    # Code II: Apply universal_property #
    hypo_name = get_new_hyp(goal)
    code = code.and_then(have(universal_property,
                              hypo_name=hypo_name,
                              variable_names=variable_names)
                         )
    code = code.and_then("rotate")  # back to first inequality

    # Code III: try to solve inequalities # e.g.
    #   iterate 2 { solve1 {try {norm_num at *}, try {compute_n 10}} <|>
    #               rotate},   rotate,
    more_code = CodeForLean.empty_code()
    if inequality_counter:
        more_code1 = CodeForLean.from_string("norm_num at *")
        more_code1 = more_code1.single_combinator("try")
        more_code2 = CodeForLean.from_string("compute_n 1")
        more_code2 = more_code2.single_combinator("try")
        # Try to solve1 inequality by norm_num, maybe followed by compute:
        more_code = more_code1.and_then(more_code2)
        more_code = more_code.single_combinator("solve1")
        # If it fails, rotate to next inequality
        more_code = more_code.or_else("rotate")
        # Do this for all inequalities
        more_code = more_code.single_combinator(f"iterate {inequality_counter}")
        # Finally come back to first inequality
        more_code = more_code.and_then("rotate")

    return code.and_then(more_code)


@action(tooltips.get('tooltip_forall'),
        logic_button_texts['action_forall'])
def action_forall(goal: Goal, l: [MathObject], user_input: [str] = []) \
                                                            -> CodeForLean:
    """
    (1) If no selection and target is of the form ∀ x, P(x):
        introduce x and transform the target into P(x)
    (2) If a single universal property is selected, ask user for an object
        to which the property will be applied
    (3) If 2 or more items are selected, one of which is a universal
        property, try to apply it to the other selected items

    """

    if len(l) == 0:
        if not goal.target.is_for_all():
            error = _("target is not a universal property '∀x, P(x)'")
            raise WrongUserInput(error)
        else:
            return construct_forall(goal)

    elif len(l) == 1:  # Ask user for item
        if not l[0].is_for_all():
            error = _("selected property is not a universal property '∀x, "
                      "P(x)'")
            raise WrongUserInput(error)
        elif len(user_input) == 0:
            raise MissingParametersError(InputType.Text,
                                         title=_("Apply a universal property"),
                                         output=_(
                                             "Enter element on which you "
                                             "want to apply:"))
        else:
            item = user_input[0]
            item = add_type_indication(item)  # e.g. (0:ℝ)
            potential_var = MathObject(node="LOCAL_CONSTANT",
                                       info={'name': item},
                                       children=[],
                                       math_type=None)
            l.insert(0, potential_var)
            # Now len(l) == 2
    # From now on len(l) ≥ 2
    # Search for a universal property among l, beginning with last item
    l.reverse()
    for item in l:
        if item.is_for_all():
            # Put item on last position
            l.remove(item)
            l.reverse()
            l.append(item)
            return apply_forall(goal, l)
    raise WrongUserInput(error=_("no universal property among selected"))


##########
# EXISTS #
##########

def construct_exists(goal, user_input: [str]) -> str:
    possible_codes = []

    if not goal.target.is_exists():
        error = _("target is not existential property '∃x, P(x)'")
        raise WrongUserInput(error)
    if len(user_input) != 1:
        raise MissingParametersError(InputType.Text,
                                     title=_("Exist"),
                                     output=_(
                                         "Enter element you want to use:"))
    x = user_input[0]
    possible_codes.append(f'use {x}, dsimp')
    possible_codes.append(f'use {x}')
    return CodeForLean.or_else_from_list(possible_codes)


def apply_exists(goal: Goal, l: [MathObject]) -> str:
    possible_codes = []

    h_selected = l[0].math_type
    h_name = l[0].info["name"]
    x = give_global_name(goal=goal, math_type=h_selected.children[0],
                         hints=[h_selected.children[1].to_display()])
    hx = get_new_hyp(goal)
    if h_selected.node == 'QUANT_∃!':
        # we have to add the "simp" tactic to avoid appearance of lambda expr
        possible_codes.append(f'cases {h_name} with {x} {hx}, simp at {hx}')

    if h_selected.children[2].node == "PROP_∃":
        possible_codes.append(
            f'rcases {h_name} with ⟨ {x}, ⟨ {hx}, {h_name} ⟩ ⟩')
    else:
        possible_codes.append(f'cases {h_name} with {x} {hx}')
    return CodeForLean.or_else_from_list(possible_codes)


def construct_exists_on_hyp(goal: Goal, l: [MathObject]):
    """
    Try to construct an existence property from some object and some property
    Here len(l) = 2
    """

    possible_codes = []
    x = l[0].info["name"]
    hx = l[1].info["name"]
    if (not l[0].math_type.is_prop()) and l[1].math_type.is_prop():
        new_h = get_new_hyp(goal)
        possible_codes.append(f'have {new_h} := exists.intro {x} {hx}')
    elif (not l[1].math_type.is_prop()) and l[0].math_type.is_prop():
        x, hx = hx, x
        new_h = get_new_hyp(goal)
        possible_codes.append(f'have {new_h} := exists.intro {x} {hx}')
    else:
        error = _("I cannot build an existential property with this")
        raise WrongUserInput(error)
    return CodeForLean.or_else_from_list(possible_codes)


@action(tooltips.get('tooltip_exists'),
        logic_button_texts['action_exists'])
def action_exists(goal: Goal, l: [MathObject], user_input: [str] = []) -> str:
    """
    Translate into string of lean code corresponding to the action
    
    If target is of form ∃ x, P(x):
ask the user to enter a specific x and transform the target into P(x).
    If a hypothesis of form ∃ x, P(x) has been previously selected:
introduce a new x and add P(x) to the properties

    :param l:   list of MathObject arguments preselected by the user
    :return:    string of lean code
    """
    if len(l) == 0:
        return construct_exists(goal, user_input)
    elif len(l) == 1 and user_input == []:
        h_selected = l[0]
        if h_selected.math_type.is_prop():
            # try to apply property "exists x, P(x)" to get a new MathObject x
            if not h_selected.is_exists():
                error = _("selection is not existential property '∃x, P(x)'")
                raise WrongUserInput(error)
            else:
                return apply_exists(goal, l)
        else:  # h_selected is not a property : get an existence property
            return construct_exists(goal, [l[0].info["name"]])
    elif len(l) == 2:
        return construct_exists_on_hyp(goal, l)
    raise WrongUserInput(error=_("does not apply to more than two properties"))


#########
# utils #
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
