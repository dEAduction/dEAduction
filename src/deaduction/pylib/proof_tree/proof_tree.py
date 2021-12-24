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

from deaduction.pylib.actions.code_for_lean import CodeForLean
from deaduction.pylib.proof_state import ProofState
from deaduction.pylib.mathobj import MathObject
from .user_action import UserProofAction
from .lean_response import LeanResponse

global _


class ProofTreeItem:
    """
    A class for storing steps of a proof in dEAduction.
    Each step but the first one has a single parent step, and 0, 1 or 2
    children. A step is a node iff it has 2 children, and in this case (and
    only in this case) its children are SubGoal instances; all other steps
    (including nodes) are ProofStep instances. The two children of a proof
    node must be created simultaneously.
    """
    proof_state_after = None  # Each derived class must implement this.

    def __init__(self, parent=None):
        self.parent: Optional[ProofTreeItem] = parent
        self.children = []
        self.time = None  # FIXME

    def add_child(self, child):
        if self.children:
            assert isinstance(child, SubGoal)
        self.children.append(child)

    def set_children(self, children):
        self.children = children
        if len(children) > 1:
            for child in children:
                assert  isinstance(child, SubGoal)

    @property
    def is_node(self) -> bool:
        """
        True if self has more than one children.
        """
        return len(self.children) > 1

    def is_last_child_of_parent(self) -> bool:
        """
        True if self is the last child of its parent.
        """
        return self is self.parent.children[-1]

    @property
    def sub_goal(self):
        """
        Return the SubGoal instance relevant to this ProofTreeItem,
        i.e. the first SubGoal ancestor.
        NB: return self if self is a SubGoal instance.
        """

        if isinstance(self, SubGoal):
            return self
        else:
            return self.parent.sub_goal

    @property
    def next_sub_goal_to_be_solved(self):
        """
        Assuming self.sub_goal has been solved, return the next SubGoal to be
        solved instance in the linearized tree,
        which is a brother of a sub-goal ancestor.
        """

        if not isinstance(self, SubGoal):
            return self.sub_goal.next_sub_goal_to_be_solved

        # Now self is a SubGoal
        next_brother = self.next_brother
        if next_brother:
            return next_brother
        elif self.parent:
            return self.parent.sub_goal.next_sub_goal_to_be_solved

    @property
    def previous_proof_step(self):
        """
        Return previous proof_step, which is self.parent except if it is a
        SubGoal instance.
        """
        parent = self.parent
        if not parent:
            return None
        elif isinstance(parent, SubGoal):
            return parent.previous_proof_step
        else:
            return parent

    @property
    def solved(self) -> bool:
        """
        True if the task corresponding to self has been solved in the proof
        tree.
        """

        if isinstance(self, NewProofStep) and self.current_goal_solved:
            return True
        elif not self.children:
            return False
        else:
            return all((child.solved for child in self.children))


class SubGoal(ProofTreeItem):
    """
    A ProofTreeItem representing a new sub-goal, e.g. splitting a
    conjunction target will yield two new sub-goals as children of the
    corresponding ProofTreeItem.
    """
    def __init__(self, parent, msg="", proof_state_after=None):
        super().__init__(parent)
        self.proof_state_after = proof_state_after
        self.msg = msg
        # Automatic numbering of sub-goals  FIXME!!
        if not parent:
            self.sub_goal_nb = 1
        else:
            # The first child has the same sub-goal number as its parent.
            self.sub_goal_nb = (parent.sub_goal.sub_goal_number
                                + len(parent.children))
            self.parent.children.append(self)

    def set_proof_state(self, proof_state):
        self.proof_state_after = proof_state

    @classmethod
    def from_lean_code(cls, lean_code: CodeForLean, parent, nb_new_goals=2):
        """
        Create 2 SubGoal instances from lean_code. This happens when usr
        split the goal (P and Q), or engage in a proof by cases, or
        add a new sub-goal. The main task is to compute the msgs
        corresponding to the new sub-goals.

        :return: as many SubGoal instances as nb_new_goals, which should
        always 2.
        """

        msgs = ["", ""]
        p = [None, None]
        if lean_code.conjunction:
            p_and_q, p[0], p[1] = lean_code.conjunction
            target = ["", ""]
            if isinstance(p_and_q, MathObject) and p_and_q.is_iff(
                    is_math_type=True):
                msg = _("Proof of {} implication: {}")
            else:
                msg = _("Proof of {} property: {}")
            for nb, i in ("first", 0), ("second", 1):
                target[i] = (p[i] if isinstance(p[i], str)
                             else p[i].to_display(format_="utf8")
                                 if isinstance(p[i], MathObject)
                             else None)
                msgs[i] = msg.format(nb, target[i])

        elif lean_code.disjunction:
            p_or_q, p[0], p[1] = lean_code.disjunction
            msgs[0] = _("First case:")
            msgs[1]=_("Second case:")
            new_hypo = ["", ""]
            for i in [0,1]:
                new_hypo[i] = (p[i] if isinstance(p[i], str)
                               else p[i].to_display(format_="utf8")
                                   if isinstance(p[i], MathObject)
                               else None)
            msgs[0] += " " + _("assuming {}").format(new_hypo[0])
            msgs[1] += " " + _("assuming {}").format(new_hypo[1])

        elif lean_code.subgoal:
            subgoal = lean_code.subgoal
            msgs[0] = _("Proof of new sub-goal: {}").format(subgoal)
        else:  # Generic case
            msgs[0] = _("Proof of new sub-goal")
            msgs[1] = _("Proof of new sub-goal")

        if nb_new_goals > 2:
            msgs.extend([_("Proof of new sub-goal")]*(nb_new_goals - 2))

        sub_goals = list(cls(parent, msg) for msg in msgs)
        return sub_goals

    @property
    def next_brother(self):
        """
        Return the next brother if it exists.

        :return: Optional[SubGoal]
        """
        parent = self.parent
        if not parent:
            return None

        children = parent.children
        index = children.index(self)
        if index < len(children)-1:
            return children[index+1]
        else:
            return None


class NewProofStep(ProofTreeItem):
    """
    Property counter is used for naming new properties, i.e. H1, H2, ...
    We make the hypotheses that
     - at most one goal is solved at a time,
     - a given step never both create and solve goals.
    """
    counter: int = 0  # For debugging
    # property_counter: int = 1

    def __init__(self, parent,
                 user_action: UserProofAction,
                 lean_response: LeanResponse):
        """
        Create self as the UNIQUE child of parent. Destruct any previous
        child.
        """
        super().__init__(parent)
        self.user_action = user_action
        self.lean_response = lean_response

        self.counter = NewProofStep.counter
        NewProofStep.counter += 1
        # self.property_counter = self.previous_proof_step.property_counter
        if parent:  # A ProofStep has no sister!
            parent.children = [self]

    @property
    def proof_state_after(self):
        return self.lean_response.new_proof_state

    @property
    def msg(self):
        return self.lean_response.success_msg

    @property
    def sub_goal_number(self) -> int:
        """
        Current number of goal in the proof history.
        """
        return self.sub_goal.sub_goal_number

    @property
    def delta_goals_count(self) -> int:
        parent = self.parent
        previous_nb = (0 if not parent else 0 if not parent.proof_state_after
                       else len(parent.proof_state_after.goals))
        proof_state = self.proof_state_after
        if proof_state:
            return len(proof_state.goals) - previous_nb
        else:
            return 0

    @property
    def current_goal_solved(self):
        return self.delta_goals_count < 0

    @property
    def new_goal_created(self):
        return self.delta_goals_count > 0


class ProofTree:
    """
    A class for storing a proof tree whose items are ProofTreeItem instances.
    The key method here is new_item, which enlarge the proof tree according
    to the nature of the proof step, i.e. by creating new sub-goals if
    necessary.
    """

    def __init__(self, initial_proof_state: ProofState = None):
        """
        Init an empty proof tree.
        """
        self.root_goal = SubGoal(parent=None, msg="Proof",
                                 proof_state_after=initial_proof_state)
        self.current_item = self.root_goal
        self.total_goals_counter = 1
        self.property_counter = 1

    def new_item(self,
                 user_action: UserProofAction,
                 lean_response: LeanResponse,
                 parent=None):
        """
        This is where the Proof Tree is built.
        Create a new ProofStep, and new sub-goals if necessary.
        Update self.current_item
        """

        if not parent:
            parent = self.current_item

        # First deleted any existing step below parent:
        parent.children = []

        new_proof_step = NewProofStep(parent=parent,
                                      user_action=user_action,
                                      lean_response=lean_response)
        proof_state = new_proof_step.proof_state_after

        # Case of current goal solved:
        if new_proof_step.current_goal_solved:
            self.current_item: SubGoal = parent.next_sub_goal
            self.current_item.proof_state_after = proof_state

        # Case of new goals created: bifurcation in the ProofTree:
        elif new_proof_step.new_goal_created:
            nb_new_goals = new_proof_step.delta_goals_count
            new_sub_goals = SubGoal.from_lean_code(LeanResponse.lean_code,
                                                   parent=new_proof_step,
                                                   nb_new_goals=nb_new_goals)
            new_proof_step.set_children(new_sub_goals)

            # New sub-goals replace previous
            self.total_goals_counter += len(new_sub_goals) -1
            self.current_item = new_sub_goals[0]
            self.current_item.proof_state_after = proof_state

        # Generic step:
        else:
            self.current_item = new_proof_step

        return self.current_item  # FIXME: useless?

    @property
    def current_sub_goal(self):
        return self.current_item.sub_goal

    @property
    def next_sub_goal(self) -> SubGoal:
        return self.current_item.next_sub_goal

    @property
    def current_proof_state(self):
        return self.current_item.proof_state_after

    @property
    def sub_goal_number(self) -> int:
        """
        Number of goal for the current_item in the proof history.
        """
        return self.current_item.sub_goal.sub_goal_number

