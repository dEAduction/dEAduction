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
     ContextWidget, PureContextWGB, EmptyWGB, GoalSolvedWGB,
     TargetSubstitutionWGB, IntroWGB, IntroImpliesWGB)

from deaduction.pylib.actions import SyntheticProofStepType
from deaduction.pylib.proof_tree import ProofTree

global _

if __name__ != "__main__":
    from deaduction.pylib.proof_tree import GoalNode, VirtualBrotherAuxGoalNode
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
    created by calling this function. A WGB corresponding to goal_node is
    created, with parent_widget as its logical parent. This function is
    crucial for the good appearance of the ProofTreeWindow ; the kind of WGB
    created should reflect the logic of the corresponding ProofStep.
    """

    new_context = goal_node.new_context
    target = goal_node.goal.target.math_type
    log.debug(f"Goal nb {goal_node.goal_nb}")

    if not parent_widget:
        log.debug("First generic WGB created")
        # Ensure wgb has a children_layout!!
        return WidgetGoalBlock(logical_parent=parent_widget,
                               goal_node=goal_node,
                               target=target, context1=new_context)

    pure_context = goal_node.is_pure_context
    context_rw = goal_node.is_context_substitution
    target_rw = goal_node.is_target_substitution
    sps = goal_node.parent.synthetic_proof_step

    # TODO: replace all tests using SyntheticProofStepType
    if sps:
        if sps.type_ in (SyntheticProofStepType.ApplyUnivStatement,
                         SyntheticProofStepType.ApplyUnivProp):
            premises = sps.premises
            operator = sps.operator
            wgb = PureContextWGB(parent_widget, goal_node,
                                 premises, operator, conclusions=new_context)
            log.debug("Pure context WGB created")

    elif pure_context:
        premises, operator, conclusions = pure_context
        # assert conclusions
        wgb = PureContextWGB(parent_widget, goal_node,
                             premises, operator, conclusions)
        log.debug("Pure context WGB created")
    elif context_rw:
        premises, rw_item, conclusions = context_rw
        # assert conclusions
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

    elif goal_node.is_no_more_goals():  # or goal_node.is_goals_solved():
        wgb = GoalSolvedWGB(parent_widget, goal_node)
        log.debug("End WGB created")

    elif goal_node.is_context_and:
        wgb = EmptyWGB(logical_parent=parent_widget, goal_node=goal_node)
        log.debug("Empty WGB created")

    elif goal_node.is_auxiliary_goal_brother:
        premises, operator, conclusions = None, None, new_context
        # assert conclusions
        wgb = PureContextWGB(parent_widget, goal_node,
                             premises, operator, conclusions)
        log.debug("Pure context WGB created for auxiliary goal brother")

    elif not goal_node.target_has_changed:
        premises = goal_node.parent.selection
        operator = None
        conclusions = (goal_node.goal.modified_context
                       + goal_node.goal.new_context)
        # assert conclusions
        wgb = PureContextWGB(parent_widget, goal_node,
                             premises, operator, conclusions)

    else:
        wgb = WidgetGoalBlock(logical_parent=parent_widget,
                              goal_node=goal_node,
                              target=target, context2=new_context)
        log.debug("Generic WGB created")

    return wgb


def update_from_node(wgb: WidgetGoalBlock, gn: GoalNode):
    """
    Recursively update the WidgetProofTree from (under) the given node,
    so that its structure will reflect that of the ProofTree.
    We have the following alternative:
    - either there is a new child goal_node for which we will create a
    child wgb;
    - or some child_wgb does not match the corresponding child goal_node:
    in this case all children_wgb should be deleted and new ones will be
    created.
    - or all children wgb match corresponding children goal_nodes.

    Noe that this is NOT redundant with the update_display method of the
    proof_tree_window, which ensures that the WidgetProofTree is correctly
    displayed on screen, and should be called later on.

    This function is a bit of an overkiller, since it probably re-creates many
    WGB unnecessarily.
    """
    pairs = list(zip(wgb.logical_children, gn.children_goal_nodes))

    # (1) If some child_wgb is obsolete, replace it
    if (len(wgb.logical_children) > len(gn.children_goal_nodes)
        or any([child_gn.goal_has_changed for child_gn in
                gn.children_goal_nodes])
        or any([child_wgb.goal_node is not child_gn
                for child_wgb, child_gn in pairs])):
        new_logical_children = []
        for i in range(len(pairs)):
            child_wgb = wgb.logical_children[i]
            child_gn = gn.children_goal_nodes[i]
            if child_gn.goal_has_changed or child_wgb.goal_node is not child_gn:
                # Reset child_wgb
                child_gn.goal_has_changed = False
                child_wgb = widget_goal_block(wgb, child_gn)
            new_logical_children.append(child_wgb)
        # Beware that now wgb.logical_children is meaningless: replace it!!
        wgb.logical_children = new_logical_children

        pairs = zip(wgb.logical_children, gn.children_goal_nodes)

    # (2) Case of new children goal nodes
    if len(wgb.logical_children) < len(gn.children_goal_nodes):
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
    The model is given by the ProofTree, the view is provided by the
    ProofTreeWindow, and the ProofTreeController makes sure that the view
    reflects the model.

    The main method is update(), which proceeds as follows:
    (1) Call the update_from_node() function, which recursively build
    WidgetGoalBlock (WGB) instances that reflect the structure of the
    ProofTree: to each GoalNode instance corresponds a WidgetGoalBlock
    instance. Each WidgetGoalBlock instance is created by this function,
    when it detects a defect some part of the ProofTree which is not
    displayed correctly. Note that this stage alone has no effect on what is
    displayed; the display is updated only at stage (3).
    (2) The WGB are recursively enabled/disabled to reflect history moves: if
    history is not at end, then all WGB corresponding to GoalNode whose
    goal_nb is > to the current goal_nb are disabled.
    (3) The WGB are recursively displayed correctly, via the
    WGB.update_display_recursively() method.
    (4) The current target is set, after which the WGB corresponding to the
    current GoalNode should indicate user that this is where the
    building of the ProofTree will continue.
    """
    def __init__(self):
        self.disabled = False
        self.proof_tree: Optional[ProofTree] = None
        self.proof_tree_window = ProofTreeWindow()

    def set_enabled(self, yes=True):
        self.disabled = not yes

    def set_proof_tree(self, proof_tree: ProofTree):
        self.proof_tree = proof_tree
        # proof_tree.set_truncate_mode(True)

    def __enable(self, till_step_nb):
        """
        Enable all WGB until a given goal_nb, disabled the others.
        Disabled WGB will be displayed in light grey. This is used when usr
        moves in the history.
        """
        main_block = self.proof_tree_window.main_block
        main_block.enable_recursively(till_step_nb=till_step_nb)

    def __is_at_end(self):
        return self.proof_tree.is_at_end()

    def update(self):
        """
        Update self.proof_tree_widget according to self.proof_tree.
        The update_from_node method creates the pertinent WidgetGoalBlocks
        that reflects the GoalNodes of the proof tree. Then these new widgets
        are inserted by the update_display method.
        """

        if self.disabled:
            return

        ptw = self.proof_tree_window
        if not self.proof_tree.root_node:
            return
        elif not ptw.main_block:
            main_block = widget_goal_block(None,
                                           self.proof_tree.root_node)
            ptw.set_main_block(main_block)

        current_goal_node = self.proof_tree.current_goal_node
        # (1) Adapt ProofTreeWindow to ProofTree.
        update_from_node(ptw.main_block, self.proof_tree.root_node)

        # (2) Enable / disable to adapt to history move:
        # proof_tree.next_proof_step_nb is the first proof_step that will be
        # deleted if usr starts a new branch from here
        proof_step_nb = self.proof_tree.next_proof_step_nb
        # log.debug(f"Enabling till {proof_step_nb-1}")
        self.__enable(till_step_nb=(proof_step_nb-1 if proof_step_nb is not None
                                  else 10000000))
        # log.info("Updating display")

        # (3) Update display of ProofTreeWindow subwidgets:
        log.info(f"Updating...")
        ptw.unset_current_target()
        ptw.update_display()

        # (4) Set current target:
        goal_nb = current_goal_node.goal_nb
        # log.info(f"Setting current target, current goal nb {goal_nb}...")
        wdg = ptw.set_current_target(goal_nb, blinking=self.__is_at_end())
        if wdg:
            # print("Ensuring visible")
            ptw.make_visible(wdg)

        # wgb = self.wgb_from_goal_nb(1)
        # if wgb and wgb.target_widget:
        #     log.debug(f"Current status_msg for gn1 is "
        #               f"{wgb.status_msg()}")

    def __wgb_from_goal_nb(self, goal_nb: int, from_wgb=None) -> \
            WidgetGoalBlock:
        """
        For debugging.
        """

        if not from_wgb:
            from_wgb = self.proof_tree_window.main_block
        if from_wgb.goal_nb == goal_nb:
            return from_wgb
        for child in from_wgb.logical_children:
            wgb = self.__wgb_from_goal_nb(goal_nb, from_wgb=child)
            if wgb:
                return wgb

