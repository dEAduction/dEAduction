"""
#################################################################
# proof_tree.py: a class for storing a proof tree and its nodes #
#################################################################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 04 2022 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the d∃∀duction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    d∃∀duction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

from copy import deepcopy
from typing import Optional

from deaduction.pylib.proof_state import Goal, ProofState
from deaduction.pylib.mathobj import ProofStep, MathObject


class GoalNode:
    """
    A class for storing a node of the proof tree corresponding to one
    ProofState's goal. It may have as a child a ProofStep instance,
    which itself has children GoalNode instances.
    """

    def __init__(self, parent: Optional[ProofStep] = None, goal: Goal = None,
                 child_proof_step=None, is_solved=False):
        self.parent = parent
        self.goal = goal
        self.child_proof_step = child_proof_step
        self._is_solved = is_solved

    @property
    def children_goal_nodes(self):
        if self.child_proof_step:
            return self.child_proof_step.children_goal_nodes
        else:
            return []

    @property
    def parent_node(self):
        if self.parent and hasattr(self.parent, "parent_goal_node"):
            return self.parent.parent_goal_node
        else:
            return None

    def set_goal(self, goal):
        self.goal = goal

    def set_child_proof_step(self, proof_step):
        self.child_proof_step = proof_step

    def is_solved(self):
        """self is solved if it is explicitly solved, or it has children and
        they are all solved."""

        if self._is_solved:
            return True
        elif self.children_goal_nodes():
            return all([child.is_solved() for child in self.children_goal_nodes()])
        else:
            return False

    @classmethod
    def goal_solved(cls, proof_step):
        """
        Return a copy of goal_node where target is a msg that goal is solved.
        """
        goal_node = proof_step.parent_goal_node
        goal = deepcopy(goal_node.goal)
        goal.target.math_type = MathObject.CURRENT_GOAL_SOLVED
        return cls(proof_step, goal, is_solved=True)

    def is_bifurcation_node(self):
        return len(self.children_goal_nodes)>1

    def ramification_degree(self):
        """
        Number of bifurcations from root node to self in ProofTree.
        """
        if not self.parent_node:
            return 0
        parent = self.parent_node
        degree = self.parent_node.ramification_degree()
        if parent.is_bifurcation_node():
            degree += 1
        return degree

    def __str__(self):
        indent = " |" * self.ramification_degree()
        separator = indent + " |___" + "\n" if self.is_bifurcation_node() \
            else ""
        main_str = indent + self.goal.target.math_type.to_display(
            format_="utf8") + "\n"
        for child in self.children_goal_nodes:
            main_str += str(child) + separator
        return main_str

# class GoalRoot(GoalNode):
#     def __init__(self, initial_proof_state: Optional[ProofState]):
#         super().__init__(parent=None)
#         self.proof_state = initial_proof_state


class ProofTree:
    """
    This class stores the main goal node, and the current goal node. It also
    keeps track of the list of unsolved goals, with the same order as Lean's
    internal list. The term of this list should be exactly the GoalNodes that
    have no children and for which self.is_solved is False.
    First unsolved_goal_node is the current goal.
    """

    def __init__(self, initial_goal=None):
        """
        Note that if initial goal is not provided, then root_node has to be
        set by the first call to process_new_proof_step.
        """
        self.root_node = GoalNode(parent=None, goal=initial_goal) \
            if initial_goal else None
        self.unsolved_goal_nodes = [self.root_node] if self.root_node else []

    @property
    def current_goal_node(self):
        return self.unsolved_goal_nodes[0]

    # ─────── Handling unsolved_goal_nodes ─────── #
    def set_current_goal_solved(self):
        self.unsolved_goal_nodes.pop(0)

    def move_next_node(self):
        self.unsolved_goal_nodes[0] = \
            self.unsolved_goal_nodes[0].children_goal_nodes[0]

    def set_bifurcation(self, new_goal_node):
        self.unsolved_goal_nodes.insert(1, new_goal_node)

    def process_new_proof_step(self, new_proof_step: ProofStep):
        """
        Create new GoalNodes and add them into the tree according to the data.
        First call creates the main_goal. The next proof_step should be created
        after this is called, with current_goal_node as a parent.
        """

        new_proof_state = new_proof_step.proof_state
        assert new_proof_state is not None

        # ─────── Very first step ─────── #
        if not self.root_node:
            self.root_node = GoalNode(parent=new_proof_step,
                                      goal=new_proof_state.goals[0])
            self.unsolved_goal_nodes.append(self.root_node)
            new_proof_step.set_children_goal_nodes([self.root_node])
            return

        # ─────── Connect new_proof_step to ProofTree ─────── #
        self.current_goal_node.set_child_proof_step(new_proof_step)

        # ─────── Create new GoalNodes ─────── #
        new_goal = new_proof_state.goals[0]
        delta_goal = (len(new_proof_state.goals) -
                      len(self.unsolved_goal_nodes))
        if delta_goal == -1:  # current goal solved
            children = [GoalNode.goal_solved(new_proof_step)]
            new_proof_step.set_children_goal_nodes(children)
            self.set_current_goal_solved()
            self.current_goal_node.set_goal(new_goal)
        elif delta_goal == 0:  # Generic case
            next_goal_node = GoalNode(parent=new_proof_step, goal=new_goal)
            children = [next_goal_node]
            new_proof_step.set_children_goal_nodes(children)
            self.move_next_node()
        else:  # Bifurcation
            assert delta_goal == 1
            next_goal_node = GoalNode(parent=new_proof_step, goal=new_goal)
            other_goal = new_proof_state.goals[1]
            other_goal_node = GoalNode(parent=new_proof_step, goal=other_goal)
            children = [next_goal_node, other_goal_node]
            new_proof_step.set_children_goal_nodes(children)
            self.set_bifurcation(other_goal_node)
            self.move_next_node()

        # ─────── Compare with previous state and tag properties ─────── #
        previous_goal = self.current_goal_node.parent_node.goal
        Goal.compare(new_goal, previous_goal)
        # FIXME: serious treatment of used props
        # used_properties = new_proof_step.used_properties()
        # new_goal.mark_used_properties(used_properties)

        # DEBUG
        print("ProofTree:")
        print(str(self))

    def __str__(self):
        return str(self.root_node)
