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
import logging

from deaduction.pylib.proof_state import Goal, ProofState
from deaduction.pylib.mathobj import ProofStep, MathObject
log = logging.getLogger(__name__)
global _


class GoalNode:
    """
    A class for storing a node of the proof tree corresponding to one
    ProofState's goal. It may have as a child a ProofStep instance,
    which itself has children GoalNode instances.

    Methods include test to know if GoalNode was obtained as a result of a
    proof by case, or proof of conjunction, and so on. These tests should not
    be based on user actions, since this would forbid to use them in case of
    direct Lean code.
    """

    def __init__(self, parent: Optional[ProofStep] = None, goal: Goal = None,
                 child_proof_step=None, is_solved=False):
        self.parent = parent
        self.goal = goal
        self.child_proof_step = child_proof_step
        self._is_solved = is_solved
        self._msg = None
        self._html_msg = None
        self._is_by_cases = None
        self._is_conjunction = None  # Beware that this refers to parent_node!!
        self._is_double_implication = None
        self._is_intro = None
        self._is_pure_context = None

    @classmethod
    def root_node(cls, parent_proof_step, initial_goal):
        root_node = cls(parent_proof_step, initial_goal)
        root_node._is_intro = False
        root_node._is_conjunction = False
        root_node._is_double_implication = False
        root_node._is_by_cases = False
        return root_node

    @classmethod
    def goal_solved(cls, proof_step):
        """
        Return a copy of goal_node where target is a msg that goal is solved.
        """
        goal_node = proof_step.parent_goal_node
        goal = deepcopy(goal_node.goal)
        goal.target.math_type = MathObject.CURRENT_GOAL_SOLVED
        goal_node = cls(proof_step, goal, is_solved=True)
        goal_node._msg = goal.target.math_type.to_display(format_="utf8")
        goal_node._html_msg = _("Goal!")
        return goal_node

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

    @property
    def is_fork_node(self):
        return len(self.children_goal_nodes) > 1

    @property
    def brother_number(self):
        if self.parent_node:
            if self in self.parent_node.children_goal_nodes:
                return self.parent_node.children_goal_nodes.index(self)

    @property
    def brother(self):
        if self.brother_number is not None:
            return self.parent_node.children_goal_nodes[1-self.brother_number]

    @property
    def target_has_changed(self):
        if self.parent_node:
            return (self.parent_node.goal.target.math_type !=
                    self.goal.target.math_type)

    @property
    def is_by_cases(self):
        """
        True iff this node is one of the brother nodes of a proof by cases.
        Return self._is_by_cases if this has been set explicitly, else try
        to guess by comparing targets and contexts with previous goal.
        Precisely, self is by cases if targets equal parent's target,
        and new_context has exactly one more element, and this is also true
        for the brother.
        """
        if self._is_by_cases is not None:
            return self._is_by_cases
        parent_node = self.parent_node
        if not parent_node or not parent_node.is_fork_node:
            return False
        # Now self has a brother
        tests = [not self.target_has_changed,
                 (not self.goal.context) or len(self.goal.new_context) == 1,
                 not self.brother.target_has_changed,
                 (not self.brother.goal.context) or
                 len(self.brother.goal.new_context) == 1,
                 ]
        self._is_by_cases = all(tests)
        return self._is_by_cases

    @property
    def is_conjunction(self):
        """
        Self is the node of a conjunction proof iff its parent's target is a
        conjunction whose children contain self's target.
        """
        if self._is_conjunction is not None:
            return self._is_conjunction
        parent_node = self.parent_node
        if not parent_node or not parent_node.is_fork_node:
            return False
        target = self.goal.target.math_type
        parent_target = parent_node.goal.target.math_type
        test_and = parent_target.is_and(is_math_type=True, implicit=True)
        if test_and and not parent_target.is_and(is_math_type=True):
            parent_target = MathObject.last_rw_object  # "Implicit and" case
        tests = [parent_target.is_and(is_math_type=True),
                 target in parent_target.children]
        self._is_conjunction = all(tests)
        return self._is_conjunction

    @property
    def is_double_implication(self):
        """
        Self is the node of a conjunction proof iff its parent's target is a
        conjunction whose children contain self's target.
        """
        if self._is_double_implication is not None:
            return self._is_double_implication
        parent_node = self.parent_node
        if not parent_node or not parent_node.is_fork_node:
            return False
        target = self.goal.target.math_type
        parent_target = parent_node.goal.target.math_type
        tests = [parent_target.is_iff(is_math_type=True),
                 target in parent_target.children]
        self._is_double_implication = all(tests)
        return self._is_double_implication

    @property
    def is_intro(self):
        """
        True if self corresponds to introduction of objects (in order to
        prove a universal property or an implication). This is characterised
        by
        - parent is not a fork node,
        - new context objects
        - and new target which is contained in the previous target.
        """
        if self._is_intro is not None:
            return self._is_intro
        parent_node = self.parent_node
        if not parent_node:
            return False
        tests = [not parent_node.is_fork_node,
                 self.goal.new_context,
                 self.goal.target in parent_node.goal.target]
        return all(tests)

    @property
    def is_pure_context(self):
        """
        True if parent is not a fork node and target has not changed.
        """
        if self._is_pure_context is not None:
            return self._is_pure_context
        parent_node = self.parent_node
        if not parent_node:
            return False
        tests = [not parent_node.is_fork_node,
                 self.goal.new_context,
                 not self.target_has_changed
                 ]
        return all(tests)

    @property
    def msg(self):
        """
        Compute a msg to be displayed as the header of the proof below this
        node. Generic msg is "Proof of <target>", but a different msg is
        displayed e.g. for proof by cases.
        """
        if self._msg:
            return self._msg
        elif self.is_by_cases:
            case_nb = self.brother_number
            case_txt_nb = _("First case") if case_nb == 0 else _("Second case")
            self._html_msg = case_nb
            # For second case we may not have the context...
            hypo = None
            if self.goal.new_context:
                hypo = self.goal.new_context[0].math_type
            if hypo:
                hypo_txt = hypo.to_display(format_="utf8")
                self._msg = (case_txt_nb + _(":") + " " +
                             _("assuming {}").format(hypo_txt))
            else:  # Do not assign self._msg since we may get hypo next time
                return case_txt_nb
            return self._msg
        elif self.is_conjunction:
            target_nb = self.brother_number
            self._msg = (_("Proof of first property") if target_nb == 0
                         else _("Proof of second property"))
            html_target = self.goal.target.math_type.to_display(format_="html")
            self._html_msg = _("Proof of {}").format(html_target)
            return self._msg
        elif self.is_double_implication:
            target_nb = self.brother_number
            self._msg = (_("Proof of first implication") if target_nb == 0
                         else _("Proof of second implication"))
            html_target = self.goal.target.math_type.to_display(format_="html")
            self._html_msg = _("Proof of {}").format(html_target)
            return self._msg

        elif self.goal.target is MathObject.NO_MORE_GOALS:
            self._msg = self.goal.target.math_type.to_display(format_="utf8")
            self._html_msg = _("Goal!")
            return self._msg

        else:  # TODO: refine this, taking into account auxiliary goal
            utf8_target = self.goal.target.math_type.to_display(format_="utf8")
            html_target = self.goal.target.math_type.to_display(format_="html")
            self._msg = _("Proof of {}").format(utf8_target)
            self._html_msg = _("Proof of {}").format(html_target)
            return self._msg

    def html_msg(self):
        if self._html_msg:
            return self._html_msg
        else: # Compute msg since this also compute html_msg, and try again...
            txt = self.msg
            if self._html_msg:
                return self._html_msg

        return self.msg

    def set_goal(self, goal):
        self.goal = goal

    def set_child_proof_step(self, proof_step):
        self.child_proof_step = proof_step

    def is_solved(self):
        """self is solved if it is explicitly solved, or it has children and
        they are all solved."""

        if self._is_solved:
            return True
        elif self.children_goal_nodes:
            return all([child.is_solved()
                        for child in self.children_goal_nodes])
        else:
            return False

    def total_degree(self):
        """
        Number of bifurcations from root node to self in ProofTree.
        """
        if not self.parent_node:
            return 0
        parent = self.parent_node
        parent_degree = self.parent_node.total_degree()
        if parent.is_fork_node:
            parent_degree += 1
        return parent_degree

    def __str__(self):
        indent = " |" * self.total_degree()
        separator = indent + " |___" + "\n" if self.is_fork_node \
            else ""
        main_str = indent + self.msg + "\n"
        for child in self.children_goal_nodes:
            main_str += str(child) + separator
        return main_str

    def prune(self, proof_step_nb):
        """
        Remove all info posterior to proof_step_number in the subtree under
        self.
        """
        proof_step = self.child_proof_step
        if not proof_step:
            return
        if proof_step.pf_nb <= proof_step_nb:
            # Keep this one, prune children
            for child in proof_step.children_goal_nodes:
                child.prune(proof_step_nb)
        else:
            # Remove!
            self.child_proof_step = None
            self.goal.remove_future_info()


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

    def set_unsolved_goals(self, goal_nodes):
        self.unsolved_goal_nodes = goal_nodes

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
            self.root_node = GoalNode.root_node(parent=new_proof_step,
                                                goal=new_proof_state.goals[0])
            self.unsolved_goal_nodes.append(self.root_node)
            new_proof_step.set_children_goal_nodes([self.root_node])
            return

        # ─────── Case of history move ─────── #
        if self.current_goal_node.child_proof_step:
            # Remove everything beyond parent_proof_step before proceeding
            self.prune(self.current_goal_node.parent.pf_nb)

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
        else:  # Fork node: two sub-goals
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

    def prune(self, proof_step_nb):
        """
        Remove from self all information posterior to the given proof_step.
        This includes info on ContextMathObjects, so that self should be as
        it was before.
        Value proof_step_nb = 0 corresponds to initial goal (as this is the
        step number of self.root_node.parent).
        """
        self.root_node.prune(proof_step_nb)

    def __str__(self):
        return str(self.root_node)
