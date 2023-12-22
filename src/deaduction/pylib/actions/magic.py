"""
 magic.py : magic actions

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

import deaduction.pylib.config.vars as cvars

from deaduction.pylib.actions.actiondef import action
from deaduction.pylib.actions import (CodeForLean,
                                      WrongUserInput)
from deaduction.pylib.mathobj import MathObject

from deaduction.pylib.actions.compute_utils import unify_by_ring


log = logging.getLogger("magic")
global _

########################################
# Helper: target obviously in context? #
########################################


def find_target_in_props(target: MathObject, props: [(MathObject, MathObject)]):
    """
    Direct search for a prop that matches target.
    each element of props is a couple (original_prop, sub_prop)
    where sub_prop is a property implied by original_prop (either by applying
    implicit def, or one term of a conjunction, ...).
    Return a couple that matches, or None.
    """
    for original_prop, sub_prop in props:
        if sub_prop == target:
            return original_prop, sub_prop


def rec_find_target_in_props(target: MathObject,
                             props: [MathObject, MathObject],
                             depth=3):
    """
    Recursively search props for a prop that matches target, taking into
    account implicit defs and conjunctions/ disjunctions.

    depth enables to limit recursive search, to mimick the (in)efficiency of the
    Goal! button (and of our brains...).
    """

    # TODO: add target conjunctions (solved by Goal!)

    use_implicit = cvars.get("functionality.allow_implicit_use_of_definitions")

    if not props:
        return

    # Direct search
    direct = find_target_in_props(target, props)
    if direct:
        return direct

    if depth == 0:
        return

    # Conjunctions search
    for original_prop, prop in props:
        if prop.is_and(is_math_type=True):
            and_props = [(original_prop, pr) for pr in prop.children]
            conj = rec_find_target_in_props(target, and_props,
                                            depth=0)
            if conj:
                return conj

    # Implicit defs search
    if use_implicit:
        for original_prop, prop in props:
            implicit_props = [(original_prop, pr)
                              for pr in prop.unfold_implicit_definition()]
            implicit = rec_find_target_in_props(target, implicit_props,
                                                depth=min(1, depth-1))
            if implicit:
                return implicit

    # Target disjunction search
    if target.is_or(is_math_type=True):
        for sub_target in target.children:
            disj = rec_find_target_in_props(sub_target, props,
                                            depth=0)
            if disj:
                return disj

    # Target implicit defs search
    if use_implicit:
        implicit_targets = target.unfold_implicit_definition()
        for sub_target in implicit_targets:
            # Here rec_find_... would be too powerful...
            implicit = rec_find_target_in_props(sub_target, props,
                                                depth=min(1, depth-1))
            if implicit:
                return implicit


def context_obj_solving_target(proof_step):
    """
    Search context for an object that matches the target.
    If search is successful return a couple (main_prop, sub_prop)
    where main_prop is a ContextMathObject which implies sub_prop,
    and sub_prop matches target (or one of target children if target is a
    disjunction).
    """
    goal = proof_step.goal
    target = goal.target.math_type
    props = [(prop, prop.math_type) for prop in goal.context
             if prop.math_type.is_prop()]
    return rec_find_target_in_props(target, props)


def rw_let_expr(goal) -> CodeForLean:
    """
    try {rw H} successively for all defining equalities H of let expr.
    """
    defining_eq = goal.defining_equalities()
    code = CodeForLean.empty_code()
    for eq in defining_eq:
        more_code = CodeForLean.from_string(f"rw {eq} at *")
        code = code.and_then(more_code.try_())
    return code


def norm_num_with_let_expr(goal) -> CodeForLean:
    code1 = rw_let_expr(goal)
    code2 = CodeForLean.from_string("norm_num at *").try_()
    return code1.and_then(code2)


#############
# Raw codes #
#############

def compute(proof_step) -> CodeForLean:
    """
    Try to use tactics to solve 1 numerical target, mainly by linear computing.
    This is the expensive code. If this is modified, consider adapting the
    SererInterface.__desirable_lean_rqst_fpps_method() method.
    """

    # selected_objects = proof_step.selection
    goal = proof_step.goal
    target = goal.target.math_type
    # (1) just ring
    code0 = CodeForLean.from_string("ring").solve1()
    # code1 = CodeForLean.from_string("norm_num at *").solve1()

    # (2) Just norm_num
    code1 = norm_num_with_let_expr(goal).solve1()

    possible_code = code0.or_else(code1)

    # (3) Pre_unification with ring
    # if len(selected_objects) == 1:
    #     H = selected_objects[0].math_type
    #     if H.is_prop():
    #         target = goal.target.math_type
    #         code2 = unify_by_ring(H, target)
    #         if code2:
    #             possible_code = possible_code.or_else(code2)
    for hyp in goal.context_props:
        code2 = unify_by_ring(hyp.math_type, target)
        if code2:
            possible_code = possible_code.or_else(code2.solve1())

    # (4) Linear arithmetic
    code10a = CodeForLean.from_string("compute_n 10")
    # code2b = CodeForLean.from_string("norm_num at *").try_().and_then(code2a)
    code10b = norm_num_with_let_expr(goal).and_then(code10a)
    code10c = code10b.solve1()

    possible_code = possible_code.or_else(code10c)

    return possible_code


def raw_solve_equality(target: MathObject) -> CodeForLean:
    """
    Assuming prop is an equality or an iff, return a list of tactics trying to
    solve prop as a target. These tactics are pertinent whatever the type of
    the terms.
    """

    code = CodeForLean.empty_code()
    if target.is_equality(is_math_type=True):
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

    context = proof_step.goal.context

    # (1) General tactics
    code = CodeForLean.empty_code()
    code = code.or_else('assumption')
    code = code.or_else('contradiction')

    # (2) Use user selection
    if len(selected_objects) == 1:
        string = f'apply {selected_objects[0].info["name"]}'
        more_code = CodeForLean.from_string(string).solve1()
        code = code.or_else(more_code)

    # (2) Equality/iff tactics if pertinent, cf target and context
    if (target.is_equality(is_math_type=True)
            or target.is_iff(is_math_type=True)):
        goal_contains_equalities = True
    else:
        goal_contains_equalities = False
    for math_object in context:
        if math_object.is_equality():
            goal_contains_equalities = True

    if goal_contains_equalities:
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
        # goal = proof_step.goal
        more_code = compute(proof_step)
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
def action_assumption(proof_step) -> CodeForLean:
    """
    New action assumption.
    The idea is to apply a series of transformation of the target, and then
    to apply raw_solve_target to each resulting target. Transformations
    include:
    - splitting conjunctions and disjunctions
    - trying exfalso, trying to symmetrize the target
    """

    selected_objects = proof_step.selection
    # target_selected = proof_step.target_selected
    # user_input = proof_step.user_input

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
    # print("Code tree :")
    # display_tree(code_tree)
    # print("Modulated tree :")
    # display_tree(modulated_tree)

    # (3) Turn code_tree into CodeForLean
    code = code_from_tree(modulated_tree, selected_objects, proof_step)
    # print("Code :")
    # print(code)

    # (4) Add global msg
    code.add_error_msg(_("I don't know how to conclude"))

    # (5) User can select objects to indicate used properties(?)
    if selected_objects:
        code.add_used_properties(selected_objects)
    # TODO:
    #   - add implicit definitions, for and / or only ? And only once ?
    #   (inter, union, borné, ...)
    #   - Add error, success msgs
    return code  # .solve1()

