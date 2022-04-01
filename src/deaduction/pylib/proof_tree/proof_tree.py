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

from deaduction.pylib.proof_state import Goal


class GoalNode:
    """
    A class for storing a node of the proof tree corresponding to one
    ProofState's goal. It may have as a child a ProofStep instance,
    which itself has children GoalNode instances.
    """

    def __init__(self, goal: Goal, child_proof_step=None, is_solved=False):
        self.goal = goal

        self.child_proof_step = child_proof_step
        self._is_solved = is_solved

    def children_nodes(self):
        if self.child_proof_step:
            return self.child_proof_step.children_goal_nodes
        else:
            return []

    def is_solved(self):
        """self is solved if it is explicitly solved, or it has children and
        they are all solved."""

        if self._is_solved:
            return True
        elif self.children_nodes():
            return all([child.is_solved() for child in self.children_nodes()])
        else:
            return False


class ProofTree:
    """
    This class stores the main goal node, and the current goal node.
    """

    def __init__(self, main_goal: GoalNode):
        self.main_goal = main_goal
        self.current_goal = main_goal



