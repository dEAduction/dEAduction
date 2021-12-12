"""
# proof_tree.py : provide the ProofTreeItem class for storing proofs #

This class is the abstract data moedl to be displayed by
the proof_outline_window.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 12 2021 (creation)
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

from typing import Optional

from deaduction.pylib.mathobj import ContextMathObject
from deaduction.pylib.actions.code_for_lean import CodeForLean

class ProofTreeItem:
    """
    A class for storing steps of a proof in dEAduction.
    Each step but the first one has a single parent step, and 0, 1 or 2
    children. A step is a node iff it has 2 children, and in this case (and
    only in this case) its children are SubGoal instances; all other steps
    are ProofStep instances. The two children of a proof node must be
    created simultaneously.
    """

    def __init__(self, parent, children, history_nb, msg):
        self.parent: Optional[ProofTreeItem] = parent
        assert len(children) <= 2
        self.children: [ProofTreeItem]       = children
        self.history_nb: int                 = history_nb
        self.msg: str                        = msg

    @property
    def is_node(self) -> bool:
        """
        True if self has more than one children.
        """
        return len(self.children) > 1

    @property
    def is_last_child_of_parent(self) -> bool:
        """
        True if self is the last child of its parent.
        """
        return self is self.parent.children[-1]

    @property
    def current_sub_goal(self):
        """
        Return the SubGoal instance relevant to this ProofTreeItem,
        i.e. the first SubGoal ancestor.
        """
        item = self.parent
        while not isinstance(item, SubGoal):
            item = self.parent
        return item

    @property
    def next_sub_goal(self):
        """
        Return the next SubGoal instance in the linearized tree,
        which corresponds to the next sub-goal to be solved.
        """

        # Find pertinent node
        sub_goal = self.current_sub_goal
        while sub_goal.is_last_child_of_parent:
            sub_goal = self.current_sub_goal

        node = sub_goal.parent
        assert len(node.children) == 2
        next_sub_goal = node.children[-1]
        return next_sub_goal


class SubGoal(ProofTreeItem):
    def __init__(self):
        super().__init__()

    @classmethod
    def from_lean_code(self, lean_code: CodeForLean):
        pass


class ProofStep(ProofTreeItem):
    pass