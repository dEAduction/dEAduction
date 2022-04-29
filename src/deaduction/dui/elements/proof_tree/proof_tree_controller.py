"""
# Classes for controlling the proof tree widget. #

Author(s)     : F Le Roux
Maintainer(s) : F. Le Roux
Created       : 03 2022 (creation)
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
from typing import Union, Optional

from deaduction.dui.elements.proof_tree.proof_tree_widget import \
    (ProofTreeWindow, WidgetGoalBlock, ByCasesWGB, SubstitutionWGB,
        PureContextWGB, EmptyWGB, GoalSolvedWGB, TargetSubstitutionWGB,
        IntroWGB, IntroImpliesWGB)

global _

if __name__ != "__main__":
    from deaduction.pylib.proof_tree import GoalNode
else:
    def _(x):
        return x

    class MathObject:
        pass

    class GoalNode:
        pass


log = logging.getLogger(__name__)


def widget_goal_block(parent_widget: Optional[WidgetGoalBlock],
                      goal_node: GoalNode) -> WidgetGoalBlock:
    """
    All WidgetGoalBlock to be inserted in the ProofTreeWidget should be
    created by calling this method.
    """

    # TODO:
    #  - target_substitution (including proof by contraposition, push_neg)
    #  - apply
    #  - Auxiliary sub-goal
    #  - EmptyWidget when adding a statement content to context
    #  - action_theorem
    #  - ...

    new_context = goal_node.goal.new_context
    target = goal_node.goal.target.math_type

    pure_context = goal_node.is_pure_context
    context_rw = goal_node.is_context_substitution
    target_rw = goal_node.is_target_substitution

    if pure_context:
        premises, operator, conclusions = pure_context
        wgb = PureContextWGB(parent_widget, goal_node,
                             premises, operator, conclusions)
        log.debug("Pure context WGB created")
    elif context_rw:
        premises, rw_item, conclusions = context_rw
        wgb = SubstitutionWGB(parent_widget, goal_node,
                              premises, rw_item, conclusions)
        log.debug("Substitution Context WGB created")

    elif target_rw:
        wgb = TargetSubstitutionWGB(logical_parent=parent_widget,
                                    goal_node=goal_node,
                                    rw_item=target_rw)
        log.debug("Target Substitution WGB created")

    elif goal_node.is_intro:
        wgb = IntroWGB(logical_parent=parent_widget, goal_node=goal_node,
                       context=new_context, target=target)
        log.debug("Intro WGB created")

    elif goal_node.is_implies:
        wgb = IntroImpliesWGB(logical_parent=parent_widget,
                              goal_node=goal_node,
                              context=new_context, target=target)
        log.debug("Implies WGB created")

    elif goal_node.is_by_cases:
        wgb = ByCasesWGB(logical_parent=parent_widget,
                         goal_node=goal_node,
                         context=new_context, target=target)
        log.debug("By Cases WGB created")

    elif goal_node.is_all_goals_solved():  # or goal_node.is_goals_solved():
        wgb = GoalSolvedWGB(parent_widget, goal_node)
        log.debug("End WGB created")

    elif goal_node.is_context_and:
        wgb = EmptyWGB(logical_parent=parent_widget, goal_node=goal_node)
        log.debug("Empty WGB created")

    else:
        wgb = WidgetGoalBlock(logical_parent=parent_widget,
                              goal_node=goal_node,
                              target=target, context2=new_context)
        log.debug("Generic WGB created")

    return wgb


def update_from_node(wgb: WidgetGoalBlock, gn: GoalNode):
    """
    Recursively update the WidgetProofTree from (under) the given node.
    We have the following alternative:
    - either there is a new child goal_node for which we will create a
    child wgb;
    - or some child_wgb does not match the corresponding child goal_node:
    in this case all children_wgb should be deleted and new ones will be
    created.
    - or all children wgb match corresponding children goal_nodes.
    """
    pairs = list(zip(wgb.logical_children, gn.children_goal_nodes))
    if (len(wgb.logical_children) > len(gn.children_goal_nodes)
        or any([child_wgb.goal_node is not child_gn
                for child_wgb, child_gn in pairs])):
        # Case 1: Some child_wgb is obsolete: reset all children
        wgb.logical_children = []
        wgb.set_layout_without_children()
        for child_gn in gn.children_goal_nodes:
            child_wgb = widget_goal_block(wgb, child_gn)
        pairs = zip(wgb.logical_children, gn.children_goal_nodes)

    elif len(wgb.logical_children) < len(gn.children_goal_nodes):
        # Case 2: new children
        new_index = len(wgb.logical_children)
        new_children_gn = gn.children_goal_nodes[new_index:]
        for child_gn in new_children_gn:
            child_wgb = widget_goal_block(wgb, child_gn)
        pairs = zip(wgb.logical_children, gn.children_goal_nodes)

    # In any case, recursively update children
    for child_wgb, child_gn in pairs:
        update_from_node(child_wgb, child_gn)


class ProofTreeController:
    """
    A class to create and update a ProofTreeWindow that reflects a ProofTree.
    """
    def __init__(self):
        self.proof_tree = None
        self.proof_tree_window = ProofTreeWindow()

    def set_proof_tree(self, proof_tree):
        self.proof_tree = proof_tree

    def enable(self, till_step_nb):
        """
        Enable all WGB until a given goal_nb, disabled the others.
        Disabled WGB will be displayed in light grey. This is used when usr
        moves in the history.
        """
        main_block = self.proof_tree_window.main_block
        main_block.enable_recursively(till_step_nb=till_step_nb)

    def is_at_end(self):
        return self.proof_tree.is_at_end()

    def update(self):
        if not self.proof_tree.root_node:
            return
        elif not self.proof_tree_window.main_block:
            main_block = widget_goal_block(None,
                                           self.proof_tree.root_node)
            self.proof_tree_window.set_main_block(main_block)

        current_goal_node = self.proof_tree.current_goal_node
        # Adapt display of ProofTreeWindow to ProofTree:
        log.info("Updating proof tree widget from proof tree.")
        update_from_node(self.proof_tree_window.main_block,
                         self.proof_tree.root_node)

        # Enable / disable to adapt to history move:
        # proof_tree.next_proof_step_nb is the first proof_step that will be
        # deleted if usr starts a new branch from here
        proof_step_nb = self.proof_tree.next_proof_step_nb
        if proof_step_nb is not None:
            log.debug(f"Enabling till {proof_step_nb-1}")
            self.enable(till_step_nb=proof_step_nb-1)
        else:
            self.enable(till_step_nb=1000000)
        log.info("Updating display")

        # Update display:
        self.proof_tree_window.update_display()

        # Set current target:
        log.info("Setting current target")
        goal_nb = current_goal_node.goal_nb
        self.proof_tree_window.set_current_target(goal_nb,
                                                  blinking=self.is_at_end())

    def wgb_from_goal_nb(self, goal_nb: int, from_wgb=None) -> \
            WidgetGoalBlock:
        """ For debugging only."""
        if not from_wgb:
            from_wgb = self.proof_tree_window.main_block
        if from_wgb.goal_nb == goal_nb:
            return from_wgb
        for child in from_wgb.logical_children:
            wgb = self.wgb_from_goal_nb(goal_nb, from_wgb=child)
            if wgb:
                return wgb

