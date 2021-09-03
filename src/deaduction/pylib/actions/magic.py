"""
# magic.py : #ShortDescription #
    
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

from typing import Optional
import logging

from deaduction.pylib.utils.nice_display_tree import display_tree
from deaduction.pylib.actions.actiondef import action
from deaduction.pylib.actions import (CodeForLean,
                                      WrongUserInput)
from deaduction.pylib.mathobj import  MathObject


log = logging.getLogger("magic")
global _


@action()
def action_compute(proof_step,
                   selected_objects,
                   user_input,
                   target_selected: bool = True):
    """
    If the target is an equality, an inequality (or 'False'), then send
    tactics trying to prove the goal by (mainly linearly) computing.
    """

    goal = proof_step.goal

    target = goal.target
    if not (target.is_equality()
            or target.is_inequality()
            or target.is_false()):
        error = _("Target is not an equality, an inequality, "
                  "nor a contradiction")
        raise WrongUserInput(error)
    # try_before = "try {apply div_pos}, " \
    #            + "try { all_goals {norm_num at *}}" \
    #             + ", "
    # simplify_1 = "simp only " \
    #             + "[*, ne.symm, ne.def, not_false_iff, lt_of_le_of_ne]"
    # possible_code = [try_before + "linarith",
    #                 try_before + simplify_1]
    # "finish" "norm_num *"
    # if user_config.getboolean('use_library_search_for_computations'):
    #     possible_code.append('library_search')
    code1 = CodeForLean.from_string("norm_num at *").solve1()
    code2 = CodeForLean.from_string("compute_n 10")
    code3 = CodeForLean.from_string("norm_num at *").try_().and_then(code2)
    code4 = code3.solve1()
    possible_code = code1.or_else(code4)
    #possible_code = [solve1_wrap("norm_num at *"),
    #                 solve1_wrap("try {norm_num at *}, compute_n 10")]
    return possible_code


def solve_equality(target: MathObject) -> CodeForLean:
    """
    Assuming prop is an equality or an iff, return a list of tactics trying to 
    solve prop as a target.
    """

    code = CodeForLean.empty_code()

    if target.math_type.children[0] == target.math_type.children[1]:
        code = code.or_else('refl')
    # try to use associativity and commutativity
    code = code.or_else('ac_reflexivity')
    # try to permute members of the goal equality
    code = code.or_else('apply eq.symm, assumption')
    # congruence closure, solves e.g. (a=b, b=c : f a = f c)
    code = code.or_else('cc')
    return code


def solve_target(prop):
    """
    Try to solve 'prop' as a target, without splitting conjunctions.    
    """
    
    code = CodeForLean.empty_code()
    code = code.or_else('assumption')
    code = code.or_else('contradiction')

    # (1) Equality, inequality, iff
    if prop.is_equality() or prop.is_iff():
        code = code.or_else(solve_equality(prop))
    elif prop.is_inequality():
        # try to permute members of the goal equality
        code = code.or_else('apply ne.symm, assumption')

    # (2) Try some symmetry rules
    if prop.is_iff():
        code = code.or_else('apply iff.symm, assumption')
    elif prop.is_and():  # todo: change to "id_and_like"
        code = code.or_else('apply and.symm, assumption')
    # The following will be tried only after context splitting:
    #     code = code.or_else('split, assumption, assumption')
    elif prop.is_or():
        code = code.or_else('apply or.symm, assumption')
        # The following is too much?
        code = code.or_else('left, assumption')
        code = code.or_else('right, assumption')

    return code


def search_specific_prop(proof_step):
    """Search context for some specific properties to conclude the proof."""
    # Fixme: "exfalso, assumption" works.
    goal = proof_step.goal

    more_code = CodeForLean.empty_code()
    for prop in goal.context:
        math_type = prop.math_type
        # Conclude from "x in empty set"
        if (math_type.node == "PROP_BELONGS"
                and math_type.children[1].node == "SET_EMPTY"):
            hypo = prop.info['name']
            if goal.target.node != "PROP_FALSE":
                more_code = CodeForLean.from_string("exfalso")
            else:
                more_code = CodeForLean.empty_code()
            more_code = more_code.and_then(f"exact set.not_mem_empty _ {hypo}")

    return more_code


@action()
def action_assumption_old(proof_step,
                      selected_objects: [MathObject],
                      user_input,
                      target_selected: bool = True) -> CodeForLean:
    """
    Translate into string of lean code corresponding to the action.
    """

    goal = proof_step.goal

    # (1) First trials
    target = goal.target
    improved_assumption = solve_target(target)
    codes = [improved_assumption]

    # (2) Use user selection
    if len(selected_objects) == 1:
        string = f'apply {selected_objects[0].info["name"]}'
        codes.append(CodeForLean.from_string(string).solve1())

    # (3) Conjunctions: try to split hypotheses once
    # TODO: recursive splitting in hypo
    # And then retry many things (in improved_assumption_2).
    split_conj = split_conjunctions_in_context(proof_step.goal.context)

    improved_assumption_2 = solve_target(target)
    # Split target
    if target.is_and():
        # TODO: recursive splitting in target, and_then for each subgoal
        #  apply improved_assumption
        split_code = CodeForLean.from_string('split, assumption, assumption')
        improved_assumption_2 = improved_assumption_2.or_else(split_code)

    # Try norm_num
    if (goal.target.is_equality()
            or goal.target.is_inequality()
            or goal.target.is_false()):
        # Do not remove above test, since norm_num may solve some
        # not-so-trivial goal, e.g. implications
        norm_num_code = CodeForLean.from_string('norm_num at *').solve1()
        improved_assumption_2 = improved_assumption_2.or_else(norm_num_code)

    # Try specific properties
    more_assumptions = search_specific_prop(proof_step)
    if not more_assumptions.is_empty():
        improved_assumption_2 = improved_assumption_2.or_else(more_assumptions)
    more_code = split_conj.and_then(improved_assumption_2)
    codes.append(more_code)
    code = CodeForLean.or_else_from_list(codes)
    code = code.solve1()
    code.add_error_msg(_("I don't know how to conclude"))
    return code


############
# REFACTOR #
############

#############
# Raw codes #
#############

def compute(target) -> CodeForLean:
    """
    Try to use tactics to solve numerical target, mainly by linear computing.
    """
    code1 = CodeForLean.from_string("norm_num at *").solve1()
    code2a = CodeForLean.from_string("compute_n 10")
    code2b = CodeForLean.from_string("norm_num at *").try_().and_then(code2a)
    code2c = code2b.solve1()
    possible_code = code1.or_else(code2c)
    return possible_code


def raw_solve_equality(target: MathObject) -> CodeForLean:
    """
    Assuming prop is an equality or an iff, return a list of tactics trying to
    solve prop as a target. These tactics are pertinent whatever the type of
    the terms.
    """

    code = CodeForLean.empty_code()

    if target.children[0] == target.children[1]:
        code = code.or_else('refl')
    # Try to use associativity and commutativity
    code = code.or_else('ac_reflexivity')
    # Congruence closure, solves e.g. (a=b, b=c : f a = f c)
    code = code.or_else('cc')
    return code


def raw_solve_target(target, proof_step, selected_objects) -> CodeForLean:
    """
    Try to solve target without splitting conjunctions, disjunctions,
    nor using symmetry properties. Tactics should be ordered from the
    simplest to the most CPU time consuming ones.
    """

    # (1) General tactics
    code = CodeForLean.empty_code()
    code = code.or_else('assumption')
    code = code.or_else('contradiction')

    # (2) Use user selection
    if len(selected_objects) == 1:
        string = f'apply {selected_objects[0].info["name"]}'
        more_code = CodeForLean.from_string(string).solve1()
        code = code.or_else(more_code)

    # (2) Equality/iff tactics
    if (target.is_equality(is_math_type=True)
            or target.is_iff(is_math_type=True)):
        more_code = raw_solve_equality(target)
        code = code.or_else(more_code)

    # (3) Computing tactics (beware, this may take a long time!)
    numbers_involved = False
    if target.is_false(is_math_type=True):
        # Check if numbers are involved somewhere in context
        context = proof_step.goal.context
        for math_object in context:
            if math_object.math_type.concerns_numbers():
                numbers_involved = True
    elif target.concerns_numbers():
        numbers_involved = True
    if numbers_involved:
        more_code = compute(target)
        code = code.or_else(more_code)
        log.debug(f"Compute: {code}")

    return code


##################
# Modifying code #
##################

def exfalso(target) -> (CodeForLean, MathObject):

    exfalso_code = CodeForLean.from_string("exfalso")
    new_target = MathObject.FALSE()

    return exfalso_code, new_target


def symmetrize(target) -> (Optional[CodeForLean], Optional[MathObject]):
    """
    Try to apply a symmetry rule to target.
    """

    code = None
    new_target = None
    if target.is_equality(is_math_type=True):
        code = CodeForLean.from_string("apply eq.symm")
    elif target.is_non_equality(is_math_type=True):
        code = CodeForLean.from_string("apply ne.symm")
    elif target.is_iff(is_math_type=True):
        code = CodeForLean.from_string('apply iff.symm')
    elif target.is_and(is_math_type=True):
        code = CodeForLean.from_string("apply and.symm")
    elif target.is_or(is_math_type=True):
        code = CodeForLean.from_string("apply or.symm")

    if code:
        new_children = [target.children[1], target.children[0]]
        new_target = MathObject(node=target.node,
                                info=target.info,
                                children=new_children,
                                bound_vars=target.bound_vars,
                                math_type=target.math_type)

    return code, new_target


def modulate(target, variations: [callable]):
    """
    Try to modify target by using variations, e.g. methods symmetrize() and
    exfalso().

    :return: A tree whose leaves are either
        - CodeForLean,
        - the CodeForLean method or_else"
        - MathObject
    """
    tree = [target]
    for variation in variations:
        more_code, new_target = variation(target)
        if more_code:
            tree += [CodeForLean.or_else, [more_code, new_target]]
    return tree


def modulate_tree(tree, variations: [callable]):
    """Recursively apply modulate function to each MathObject leaf of the
    tree.

    :return: modulated tree.
    """

    if not tree:
        return None
    elif isinstance(tree, list): # Non empty list
        # Replace child by modulated children
        modulated_tree = []
        for child in tree:
            modulated_tree.append(modulate_tree(child, variations))
        return modulated_tree
    elif isinstance(tree, MathObject):
        return modulate(tree, variations)
    else:  # String or "or_else"
        return tree


##################
# Splitting code #
##################

def split_conjunctions_in_context(context):
    """
    Return a Lean code that will split all conjunctions in context (non
    recursively, only first level is split). Implicit definitions are also
    split.
    """

    code = CodeForLean.empty_code()
    counter = 0
    split_context = False
    for prop in context:
        if prop.is_and(implicit=True):
            split_context = True
            name = prop.info['name']
            h0 = f"H_aux_{counter}"  # these hypotheses will disappear
            h1 = f"H_aux_{counter + 1}"  # so names are unimportant
            code = code.and_then(f"cases {name} with {h0} {h1}")
            counter += 2
    if split_context:
        return code


def rec_split_conj(target):
    """
    Recursively split target until there is no conjunction left in sub-goals.
    e.g.
    - if target is "(P AND Q) AND R" ->
        ["split", ["split" P, Q], R]
    - if target is "P AND (Q AND R)" ->
        ["split", P, ["split", Q, R] ]

    In the returned list, each  MathObject must be replaced by CodeForLean
    to solve it, and resulting list must be chained with "and_then".
    """

    if not target.is_and(is_math_type=True, implicit=True):
        return target
    elif not target.is_and(is_math_type=True, implicit=False):
        # Implicit and
        target = MathObject.last_rw_object

    left = rec_split_conj(target.children[0])
    right = rec_split_conj(target.children[1])
    return ["split", left, right]


def rec_split_disj(target):
    """
    Recursively split target until there is no disjunction left in sub-goals.
    e.g. if target is "(P OR Q) OR R" ->
        [ ["left", [ ["left", P], or_else, ["right", Q ]],
        or_else, ["right", R]]
    :return: A tree whose leaves are either
        - CodeForLean,
        - the CodeForLean method or_else()
        - MathObject
    """

    if not target.is_or(is_math_type=True, implicit=True):
        return target
    elif not target.is_or(is_math_type=True, implicit=False):
        # Implicit or
        target = MathObject.last_rw_object

    left = rec_split_disj(target.children[0])
    right = rec_split_disj(target.children[1])
    return [["left", left], CodeForLean.or_else, ["right", right]]


def code_from_tree(tree, selected_objects, proof_step, preamble=None) \
        -> CodeForLean:
    """
    Compute CodeForLean corresponding to a tree as returned by the functions
    rec_split_disj and rec_split_conj. The leaves that are MathObject
    instances are replaced by appropriate CodeForLean by calling solve_target.
    """

    # TODO: make it a CodeForLean class method?
    # log.debug(f"CFT(TREE={tree}, PREAMBLE={preamble})")
    if not preamble:
        preamble = CodeForLean.empty_code()
    if not tree:
        # log.debug(f"--> PREAMBLE")
        return preamble

    if isinstance(tree, CodeForLean):
        # log.debug(f"--> PREAMBLE and_then TREE")
        return preamble.and_then(tree)
    elif isinstance(tree, str):
        more_code = CodeForLean.from_string(tree)
        # log.debug(f"--> PREAMBLE and_then Lean(tree)")
        return preamble.and_then(more_code)
    elif isinstance(tree, MathObject):
        more_code = raw_solve_target(tree, proof_step, selected_objects)
        # log.debug(f"--> PREAMBLE and_then {more_code}")
        return preamble.and_then(more_code)
    elif isinstance(tree, list):  # NB: non empty list
        combinator = CodeForLean.and_then
        msg_combi = " and_then "
        msg = "PREAMBLE"
        for child in tree:
            if child is CodeForLean.or_else:
                combinator = CodeForLean.or_else
                msg_combi = " or_else "
            else:
                child_code = code_from_tree(child,
                                            selected_objects,
                                            proof_step)
                preamble = combinator(preamble, child_code)
                msg += msg_combi + str(child_code)
                combinator = CodeForLean.and_then
                msg_combi = " and_then "
        # log.debug(f"--> {msg}")
        return preamble


@action()
def action_assumption(proof_step,
                      selected_objects: [MathObject],
                      user_input,
                      target_selected: bool = True) -> CodeForLean:
    """
    New action assumption.
    The idea is to apply a series of transformation of the target, and then
    to apply raw_solve_target to each resulting target. Transformations
    includes:
    - splitting conjunctions and disjunctions
    - trying exfalso, trying to symmetrize the target


    """

    goal = proof_step.goal
    target = goal.target.math_type
    context = goal.context

    # (0) Raw target
    code_tree = [target]

    # (1a) Split conjunctions
    split_conj_target = rec_split_conj(target)
    split_conj_context = split_conjunctions_in_context(context)
    if isinstance(split_conj_target, list):
        # If target is a conjunction then we split context and rec split
        # target simultaneously
        split_conj = [split_conj_context, split_conj_target]
        code_tree += [CodeForLean.or_else, split_conj]
    elif split_conj_context:
        split_conj = [split_conj_context, target]
        code_tree += [CodeForLean.or_else, split_conj]

    # (1b) Split disjunctions in target
    split_disj = rec_split_disj(target)
    if isinstance(split_disj, list):
        code_tree += [CodeForLean.or_else, split_disj]

    # (2) Add the variations: exfalso, symmetrize
    modulated_tree = modulate_tree(code_tree, variations=[exfalso, symmetrize])
    print("Code tree :")
    display_tree(code_tree)
    print("Modulated tree :")
    display_tree(modulated_tree)

    # (3) Turn code_tree into CodeForLean
    code = code_from_tree(modulated_tree, selected_objects, proof_step)
    print("Code :")
    print(code)

    # (4) Add global msg
    code.add_error_msg(_("I don't know how to conclude"))

    # TODO:
    #   - add implicit definitions, for and / or only ? And only once ?
    #   (inter, union, borné, ...)
    #   - Add error, success msgs
    return code  # .solve1()

