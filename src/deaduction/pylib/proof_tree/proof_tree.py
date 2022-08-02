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
    which itself has 1 or 2 children which are GoalNode instances.

    Methods include test to know if GoalNode was obtained as a result of a
    proof by case, or proof of conjunction, and so on. Ideally These tests 
    should not be based on user actions, since this would forbid to use them
    in case of direct Lean code.

    Note that goal_nb's follow the order of creation, and brothers are always
    created immediately one after another.

    :param parent: the proof_step that resulted into self. None only for
    root node.
    :param goal: the Lean goal corresponding to self.
    :param child_proof_step: the next proof_step, if any.
    :param _is_solved: set to True when a goal is directly solved. In
        particular, a solved node has no child.

    :param goal_has_changed: flag to indicate that the goal has changed,
    and display chould be updated with the new goal.
    :param _temporary_new_context: set when deaduction guess the context of a
    node whose goal has not been provided by Lean, typically the second child
    of a fork proof_step.
    :param outcomes: Outcomes that should be displayed after the node
    display, typically when target Q is replaced by P by applying P=>Q
    (see ProofTree.add_outcomes).
    :param truncate_at_proof_step_nb: Class parameter, the attribute
    child_proof_step will be set to None if the proof_step nb is > than this
    nb. Thus the ProofTree will be truncated, this is used when usr is moving in
     the history.
    """
    goal_nb = 0  # Counter
    _truncate_at_proof_step_nb = None

    def __init__(self, parent: Optional[ProofStep] = None, goal: Goal = None,
                 child_proof_step=None, is_solved=False):
        self.goal_nb = GoalNode.goal_nb
        GoalNode.goal_nb += 1
        self.parent = parent
        self.goal = goal
        self._child_proof_step = child_proof_step
        # self._is_solved = is_solved
        self.goal_has_changed = False
        self._temporary_new_context = None
        self.outcomes = []

        self._msg = None
        self._html_msg = None
        self._is_by_cases = None
        self._is_conjunction = None  # Beware that this refers to parent_node!!
        self._is_double_implication = None
        self._is_intro = None
        self._is_implies = None
        self._is_pure_context = None
        self._is_auxiliary_goal = None
        self._is_auxiliary_goal_brother = None

    @classmethod
    def set_truncation_nb(cls, proof_step_nb=None):
        cls._truncate_at_proof_step_nb = proof_step_nb

    @property
    def child_proof_step(self):
        if not self._child_proof_step:
            return None

        if (self._truncate_at_proof_step_nb is not None and
                self._child_proof_step.pf_nb > self._truncate_at_proof_step_nb):
            return None

        return self._child_proof_step

    @child_proof_step.setter
    def child_proof_step(self, proof_step):
        self._child_proof_step = proof_step

    @classmethod
    def no_more_goals(cls, proof_step):
        """
        Return a copy of goal_node where target is a msg that goal is solved.
        """
        goal_node = proof_step.parent_goal_node
        goal = deepcopy(goal_node.goal)
        goal.target.math_type = MathObject.NO_MORE_GOALS
        goal_node = cls(proof_step, goal, is_solved=True)
        goal_node._msg = goal.target.math_type.to_display(format_="utf8")
        goal_node._html_msg = _("No more goal!")
        return goal_node

    @property
    def new_context(self):
        """
        Return the goal.new_context, except if goal has not been provided yet by
        Lean, in which case a temporary new_context may be stored in
        self._temporary_new_context.
        """
        if self.goal.new_context:
            return self.goal.new_context
        elif self._temporary_new_context is not None:
            return self._temporary_new_context
        else:
            return []

    def set_temporary_new_context(self, new_context: [MathObject]):
        self._temporary_new_context = new_context

    @property
    def next_goal_node(self):  # Optional[GoalNode]
        """
        Return next goal node in the proof tree.
        """
        if self.child_proof_step and self.child_proof_step.children_goal_nodes:
            return self.child_proof_step.children_goal_nodes[0]

    @property
    def children_goal_nodes(self):  # -> [GoalNode]
        if self.is_immediately_solved:
            return []
        elif self.child_proof_step:
            return self.child_proof_step.children_goal_nodes
        else:
            return []

    @property
    def parent_node(self):  # -> Optional[GoalNode]
        """
        The parent GoalNode, if any. Technically, parent of the parent
        ProofStep.
        """
        if self.parent and hasattr(self.parent, "parent_goal_node"):
            return self.parent.parent_goal_node
        else:
            return None

    @property
    def proof_step_nb(self) -> int:
        if self.parent:
            return self.parent.pf_nb

    @property
    def is_fork_node(self) -> bool:
        """
        True if self has more than one child.
        """
        return len(self.children_goal_nodes) > 1

    @property
    def is_child_fork_node(self) -> bool:
        """
        True if self has one or more brother nodes.
        """
        return self.parent_node and self.parent_node.is_fork_node

    @property
    def last_child_fork_node(self):  # -> Optional[GoalNode]
        """
        Recursively climb the tree until it finds the child of a fork node.
        """

        if self.is_child_fork_node:
            return self
        elif self.parent_node:
            return self.parent_node.last_child_fork_node
        else:
            return None

    @property
    def brother_number(self) -> Optional[int]:
        """
        Number in the brotherhood.
        """
        if self.parent_node:
            if self in self.parent_node.children_goal_nodes:
                return self.parent_node.children_goal_nodes.index(self)

    @property
    def brother(self):  #Optional[GoalNode]
        """
        Brother GoalNode, if any.
        """
        if (self.brother_number is not None
                and len(self.parent_node.children_goal_nodes) == 2):
            return self.parent_node.children_goal_nodes[1-self.brother_number]

    @property
    def target_has_changed(self) -> bool:
        """
        True if self's target differs from parent_node's target.
        """
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
        if not self.is_child_fork_node:
            self._is_conjunction = False
            return False
        # Now self has a brother
        parent_target = self.parent_node.goal.target.math_type
        conjunction = parent_target.implicit(MathObject.is_and)
        if not conjunction:
            self._is_conjunction = False
        else:
            target = self.goal.target.math_type
            brother_target = self.brother.goal.target.math_type
            tests = [target in conjunction.children,
                     brother_target in conjunction.children]
            self._is_conjunction = all(tests)
        # test_and = parent_target.is_and(is_math_type=True, implicit=True)
        # if test_and and not parent_target.is_and(is_math_type=True):
        #     parent_target = MathObject.last_rw_object  # "Implicit and" case
        # tests = [parent_target.is_and(is_math_type=True),
        #          target in parent_target.children]
        # self._is_conjunction = all(tests)
        return self._is_conjunction

    @property
    def is_double_implication(self):
        """
        Self is the node of a double implication proof iff its parent's target
        is a double implication whose children contain self's target.
        """

        # if self._is_double_implication is not None:
        #     return self._is_double_implication
        parent_node = self.parent_node
        if not parent_node or not parent_node.is_fork_node:
            self._is_double_implication = False
            return False

        # Now self has a brother
        iff = parent_node.goal.target.math_type
        target = self.goal.target.math_type
        brother_target = self.brother.goal.target.math_type
        tests = [iff.is_iff(is_math_type=True),
                 target.is_implication(is_math_type=True),
                 brother_target.is_implication(is_math_type=True),
                 target.children[0] == brother_target.children[1],
                 target.children[1] == brother_target.children[0]]
        self._is_double_implication = all(tests)
        return self._is_double_implication

    @property
    def is_intro(self):
        """
        True if self corresponds to introduction of objects in order to
        prove a universal property (but NOT an implication). This is
        characterised
        by
        - parent is not a fork node,
        - new context objects
        - and new target which is contained in the previous target.
        """
        if self._is_intro is not None:
            return self._is_intro
        else:
            return self.parent.is_intro_forall()

    @property
    def is_implies(self):
        """
        True if self corresponds to introduction of objects to prove an
        implication.
        """

        if self._is_implies is not None:
            return self._is_implies
        else:
            return self.parent.is_intro_implies()

    @property
    def is_target_substitution(self):
        """
        If self is a substitution occurring on the target, return the prop
        or statement used for substitution.
        """

        rw_item = None
        proof_step = self.parent
        if proof_step.is_statement() and proof_step.is_on_target():
            rw_item = proof_step.rw_item
        elif proof_step.button_name == "equal" \
                and len(proof_step.selection) == 1:
            rw_item = proof_step.rw_item
        elif proof_step.is_push_neg() and proof_step.is_on_target():
            rw_item = _("Pushing negation")
        elif proof_step.is_by_contraposition():
            rw_item = _("Contraposition")
        return rw_item

    @property
    def is_context_substitution(self):
        """
        If self is a substitution occurring on the context, return the prop
        or statement used for substitution, as well as premises and conclusions.
        """

        rw_item = None
        proof_step = self.parent
        if proof_step.is_statement() and not proof_step.is_on_target():
            rw_item = proof_step.rw_item
        elif (proof_step.is_equal() or proof_step.is_iff()) and \
                len(proof_step.selection) >= 2:
            rw_item = proof_step.rw_item
        elif proof_step.is_push_neg() and not proof_step.is_on_target():
            rw_item = _("Pushing negation")

        if rw_item:
            selection = proof_step.selection
            premises = [obj for obj in selection if rw_item != obj]
            conclusions = (proof_step.goal.new_context
                           + proof_step.goal.modified_context)

            return premises, rw_item, conclusions

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
        selected_objects = self.parent.selection
        tests = [not parent_node.is_fork_node,
                 self.goal.new_context,
                 not self.target_has_changed,
                 selected_objects]
        if all(tests):
            conclusions = self.goal.new_context
            operator = self.parent.operator
            premises = [obj for obj in selected_objects if obj != operator]
            return premises, operator, conclusions
        else:
            return False

    @property
    def is_context_and(self):
        if not (self.parent.is_and() or self.parent.is_iff()):
            return False
        if self.parent.is_on_target():
            return False
        selection = self.parent.selection
        if self.parent.is_iff() and len(selection) == 2 and \
                (selection[0].is_iff() or selection[1].is_iff()):
            # This is a substitution
            return False
        return True

    @property
    def is_auxiliary_goal(self):
        """
        True if self.target is new and brother.target is not new.
        """
        if self._is_auxiliary_goal is not None:
            return self._is_auxiliary_goal
        parent_node = self.parent_node
        if not parent_node or not parent_node.is_fork_node:
            self._is_auxiliary_goal = False
            return False
        tests = self.target_has_changed and not self.brother.target_has_changed
        self._is_auxiliary_goal = tests
        self.brother._is_auxiliary_goal_brother = tests
        # if tests:
        #     """
        #     Add temporary new_context for brother node.
        #     """
        #     self.brother.set_temporary_new_context([self.goal.target.math_type])
        return tests

    @property
    def is_auxiliary_goal_brother(self):
        if self._is_auxiliary_goal_brother is not None:
            return self._is_auxiliary_goal_brother
        tests = self.brother and self.brother.is_auxiliary_goal
        return tests

    @property
    def is_suffices_to(self):
        """
        True if node is obtained by applying a theorem or property "P => Q" on
        target Q, replacing it with target P.
        For the moment, this is detected (and useful only) if
        CodeForLean.outcome_operator is not None.
        """
        proof_step = self.parent
        return proof_step and proof_step.outcome_operator

    def __msg(self, format_, use_color=True, bf=False):
        """
        Compute a msg to be displayed as the header of the proof below this
        node. Generic msg is "Proof of <target>", but a different msg is
        displayed e.g. for proof by cases.

        html_msg is displayed in the proof tree widget,
        msg is displayed in the status bar, exclusively in case of a fork node.

        msg is supposed to be a synthetic version of html_msg
            e.g. "Proof of first property" vs "Proof of <first property>".

        :param format_ : "html" or "utf8"
        :param use_color: enable or disable colors (used for variables in
            case of html format)
        :param bf: use boldface fonts.
        """

        msg = ""
        html_msg = ""

        if self._msg:
            return self._msg
        elif self.is_by_cases:
            case_nb = self.brother_number
            case_txt_nb = _("First case") if case_nb == 0 else _("Second case")
            html_msg = case_txt_nb
            # For second case we may not have the context...
            hypo = None
            if self.goal.new_context:
                hypo = self.goal.new_context[0].math_type
            if hypo:
                hypo_txt = hypo.to_display(format_="utf8")
                msg = (case_txt_nb + _(":") + " " +
                      _("assuming {}").format(hypo_txt))
            else:  # Do not assign self._msg since we may get hypo next time
                msg = case_txt_nb

        elif self.is_double_implication:
            target = self.goal.target.math_type
            target_nb = self.brother_number
            msg = (_("Proof of first implication") if target_nb == 0
                   else _("Proof of second implication"))
            html_target = target.to_display(format_="html",
                                            use_color=use_color,
                                            bf=bf)
            html_msg = _("Proof of {}").format(html_target)

        # NB: test double implication BEFORE conjunction, since iff is more
        #  specific than and.
        elif self.is_conjunction:
            target = self.goal.target.math_type
            target_nb = self.brother_number
            msg = (_("Proof of first property") if target_nb == 0
                   else _("Proof of second property"))
            html_target = target.to_display(format_="html",
                                            use_color=use_color,
                                            bf=bf)
            html_msg = _("Proof of {}").format(html_target)

        elif self.parent.is_by_contradiction():
            html_msg = _("Proof by contradiction")

        elif self.goal.target.math_type is MathObject.NO_MORE_GOALS:
            msg = self.goal.target.math_type.to_display(format_="utf8")
            html_msg = self.goal.target.math_type.to_display(format_="html")

        else:  # TODO: refine this, taking into account auxiliary goal
            target = self.goal.target.math_type
            utf8_target = target.to_display(format_="utf8")
            html_target = target.to_display(format_="html",
                                            use_color=use_color,
                                            bf=bf)
            if self.is_auxiliary_goal_brother:
                msg = _("Back to proof of {}").format(utf8_target)
                html_msg = _("Back to proof of {}").format(html_target)
            elif self.is_child_fork_node:
                msg = _("Proof of sub-goal: {}").format(utf8_target)
                html_msg = _("Proof of sub-goal: {}").format(html_target)
            else:
                msg = _("Proof of {}").format(utf8_target)
                html_msg = _("Proof of {}").format(html_target)

        return msg if format_ == "utf8" else html_msg

    def msg(self):
        return self.__msg(format_="utf8")

    def html_msg(self, use_color=True, bf=False):
        return self.__msg(format_="html", use_color=use_color, bf=bf)

    def set_goal(self, goal):
        self.goal = goal

    def is_no_more_goals(self):
        return self.goal.target.math_type == MathObject.NO_MORE_GOALS

    @property
    def is_immediately_solved(self):
        """
        True iff self is solved (NOT sorry) by its child_proof_step.
        """
        return (self.child_proof_step and
                self.child_proof_step.has_solved_one_goal)

    def is_recursively_solved(self):
        """
        Self is recursively solved if it is explicitly solved, or it has
        children and they are all (recursively) solved. Here we consider only
        strictly solved goals, that is, not "solved by sorry".
        """

        if self.is_immediately_solved or self.is_no_more_goals():
            return True
        elif self.children_goal_nodes:
            return all([child.is_recursively_solved()
                        for child in self.children_goal_nodes])
        else:
            return False

    def is_immediately_sorry(self):
        """
        True if self is obtained by applying "proof by sorry" method.
        """
        if self.child_proof_step:
            return self.child_proof_step.is_sorry()

    def is_recursively_sorry(self):
        """
        Self is recursively sorry all of its children are solved or sorry,
        and at least one is sorry.
        """
        if self.is_immediately_sorry():
            return True
        # elif not self.is_recursively_solved():
        #     return False
        else:
            sorry = [child.is_recursively_sorry() for child in
                     self.children_goal_nodes]
            solved = [child.is_recursively_solved() for child in
                      self.children_goal_nodes]
            solved_or_sorry = [sos[0] or sos[1] for sos in zip(solved, sorry)]
            return any(sorry) and all(solved_or_sorry)

    def is_recursively_solved_or_sorry(self):
        return self.is_recursively_solved() or self.is_recursively_sorry()

    @property
    def unsolved_leaves(self):
        """
        Return the list of unsolved leaves of self. This is used to determine
        the list of goals that remain to be solved. Here the goals solved by
        sorry are considered to be solved.
        """

        if self.is_recursively_solved_or_sorry():
            return []
        elif not self.children_goal_nodes:
            return [self]
        else:
            unsolved_leaves = []
            for child in self.children_goal_nodes:
                unsolved_leaves.extend(child.unsolved_leaves)
            return unsolved_leaves

    # def truncated_unsolved_leaves(self, till_proof_step_nb=None) -> []:
    #     """
    #     Return the list of unsolved leaves of self (truncating all proof steps
    #     after till_proof_step_nb). Admitted is considered as solved.
    #     """
    #     if till_proof_step_nb is None:
    #         return self.unsolved_leaves
    #
    #     if (not self.child_proof_step or self.child_proof_step.pf_nb >
    #             till_proof_step_nb):
    #         # Unsolved leaf of the truncated ProofTree
    #         return [self]
    #     elif self.is_immediately_solved or self.is_immediately_sorry():
    #         # Leaf is solved NOT AFTER till_proof_step_nb
    #         return []
    #
    #     # Add unsolved leaves of children
    #     unsolved_leaves = []
    #     for child in self.children_goal_nodes:
    #         child_leaves = child.truncated_unsolved_leaves(till_proof_step_nb)
    #         unsolved_leaves.extend(child_leaves)
    #     return unsolved_leaves

    def total_degree(self):
        """
        Number of bifurcations from root node to self in ProofTree. Used only
        for debugging (__str__ method).
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
        main_str = indent + self.msg() + "\n"
        for child in self.children_goal_nodes:
            main_str += str(child) + separator
        return main_str

    def clear_descendance(self):
        self.child_proof_step = None
        self.goal.remove_future_info()

    def prune_from(self, proof_step_nb):
        """
        Prune the ProofTree of all ProofSteps occurring after self.
        All these ProofSteps should have nb >= to the given nb (so this
        information is used only for debugging). Note that this includes the
        subtree under self, but also any other part of the tree that has been
        constructed after self, as these are linked by the special ProofSteps
        from solved GoalNodes.
        Used when user starts a new tree after some undoing.
        """

        # proof_step = self.child_proof_step
        # if not proof_step:
        #     return
        # if proof_step.pf_nb <= proof_step_nb:
        #     # Keep this one, prune children
        #     for child in proof_step.children_goal_nodes:
        #         child.prune_from(proof_step_nb)
        # else:
        #     # Remove!
        #     self.set_solved(False)  # VERY important!
        #     self.child_proof_step = None
        #     self.goal.remove_future_info()

        child_proof_step = self.child_proof_step
        if not child_proof_step:
            return

        assert child_proof_step.pf_nb >= proof_step_nb

        # Prune_from children
        for child in child_proof_step.children_goal_nodes:
            child.prune_from(proof_step_nb)

        # Disconnect child_proof_step and clear future info
        self.clear_descendance()


class RootGoalNode(GoalNode):
    """
    This class should be used for the first node of a ProofTree. Its only
    purpose is to distinguish the root node.
    """
    def __init__(self, parent_proof_step, initial_goal):
        super().__init__(parent_proof_step, initial_goal)
        self._is_intro = False
        self._is_conjunction = False
        self._is_double_implication = False
        self._is_by_cases = False


class VirtualBrotherAuxGoalNode(GoalNode):
    """
    This is a special type of node, that does not correspond to some Lean state.
    In case user applies a theorem saying "P => Q" on a target Q, then Lean
    replaces the target by P, and this will correspond to some GoalNode G.
    Then an instance of the present class may be added in the ProofTree as a
    brother node for G. This GoalNode may be used to make explicit  the
    implicit logics after G is solved, displaying
    P
    P --> P => Q --> Q.

    Note that P is the target of self.brother, Q is the target of
    self.parent_node, and P => Q should have been stored in the CodeForLean,
    and is accessed via self.outcome_operator.
    """
    def __init__(self, parent: ProofStep, type_: str):
        super().__init__(parent, goal=None, is_solved=(type_ is "operator"))
        self.type_ = type_  # 'premise' or 'operator'

    @property
    def outcome_operator(self):
        if self.type_ is 'operator' and self.parent:
            return self.parent.outcome_operator

    @property
    def main_premise(self):
        """
        Return 'P'.
        """
        brother = self.parent.children_goal_nodes[0]
        return brother.goal.target

    @property
    def premises(self):
        if self.type_ is not 'operator':
            return

        selection = self.parent.selection
        if selection:
            premises = [obj for obj in selection
                        if obj != self.outcome_operator]
        else:
            premises = []
        premises.append(self.main_premise)
        return premises

    @property
    def conclusions(self):
        """
        Return 'Q'.
        """
        if self.type_ is 'operator':
            return [self.parent_node.goal.target]


class ProofTree:
    """
    This class stores the root goal node, and the current goal node. It also
    keeps track of the list of unsolved goals, with the same order as Lean's
    internal list. The term of this list should be exactly the GoalNodes that
    have no children and for which self.is_solved is False.
    First unsolved_goal_node is the current goal.

    The tree is made of two kind of items:
    - GoalNode instances are the tree nodes,
    - ProofStep instances represent edges.
    A ProofStep that solves a goal is directed towards the next GoalNode in
    history (the first unsolved goal node at that time); thus it is not a
    real edge of the ProofTree, but it allows to keep track of history.
    More precisely, the chronological order of the ProofTree's GoalNode can
    be recovered by following the ProofSteps's first child:
    Root node -> child_proof_step -> children_goal_node[0] -> child_proof_step
    ... and so on.
    """

    # TODO: add a permutation to reflect Lean's own list of unsolved goals.
    def __init__(self, initial_goal=None):
        """
        Note that if initial goal is not provided, then root_node has to be
        set by the first call to process_new_proof_step.

        - self.last_proof_step is the last ProofStep instance received by
        the ProofTree, responsible for the present state.
        """
        self.root_node = RootGoalNode(parent_proof_step=None,
                                      initial_goal=initial_goal) \
            if initial_goal else None
        self.current_goal_node = self.root_node
        self.previous_goal_node = None
        self._last_proof_step: Optional[ProofStep] = None

    @property
    def last_proof_step(self):
        """
        Return the nb of the last proof step. Note that in case of a history
        move this is not the current_goal_node.parent but the nb of the
        ProofStep that was the aim of the move.
        """
        if self._last_proof_step is not None:
            return self._last_proof_step
        elif self.current_goal_node:
            return self.current_goal_node.parent

    @last_proof_step.setter
    def last_proof_step(self, proof_step: ProofStep):
        self._last_proof_step = proof_step

    @property
    def last_proof_step_nb(self):
        """
        Return the nb of the last proof step. Note that in case of a history
        move this is not the current_goal_node.parent but the nb of the
        ProofStep that was the aim of the move.
        """
        if self.last_proof_step:
            return self.last_proof_step.pf_nb
        else:
            return None

    def set_truncate_mode(self, yes=True):
        """
        Set the ProofTree into truncate mode: the part of the tree below
        self.last_proof_step becomes invisible. This is useful to compute
        unsolved goals, ... during history moves.
        """
        if yes:
            GoalNode.set_truncation_nb(self.last_proof_step_nb)
        else:
            GoalNode.set_truncation_nb(None)

    def last_child_fork_node(self) -> Optional[GoalNode]:
        """
        Return the last ancestor of current_goal_node which is the child of a
        fork node. This is the pertinent goal_node for the proof msg to be
        displayed in the status bar.
        """
        return self.current_goal_node.last_child_fork_node

    def current_proof_msg(self) -> Optional[str]:
        """
        Return the msg of the last child fork node. This msg should be
        displayed in the status bar.
        """
        if self.last_child_fork_node():
            return self.last_child_fork_node().msg()

    def is_at_end(self):
        """
        True if self has no child_proof_step, e.g. if self is at end of history.
        """
        return self.current_goal_node.child_proof_step is None

    @property
    def next_proof_step_nb(self) -> Optional[int]:
        proof_step = self.current_goal_node.child_proof_step
        if proof_step:
            return proof_step.pf_nb
        else:
            return None

    # def unsolved_goal_nodes(self, till_proof_step_nb=None) -> [GoalNode]:
    #     """
    #     Compute from the proof tree (truncated at "till_goal_nb") the list of
    #     unsolved goal_nodes. This is the ordered list of unsolved leaves of
    #     the tree.
    #     """
    #     if till_proof_step_nb is not None:
    #         return self.root_node.truncated_unsolved_leaves(till_proof_step_nb)
    #     else:
    #         return self.root_node.unsolved_leaves

    def unsolved_goal_nodes(self, truncated=True) -> [GoalNode]:
        """
        Compute from the proof tree (truncated at "till_goal_nb") the list of
        unsolved goal_nodes. This is the ordered list of unsolved leaves of
        the tree. In truncated mode, only the part of the ProofTree before
        last_proof_step_nb is taken into account.
        """
        self.set_truncate_mode(truncated)
        leaves = self.root_node.unsolved_leaves
        self.set_truncate_mode(False)
        return leaves

    # def pending_goal_nodes(self, till_proof_step_nb=None) -> [GoalNode]:
    #     """
    #     The list of unsolved oal nodes, except current_goal_node.
    #     """
    #     pgn = [gn for gn in self.unsolved_goal_nodes(till_proof_step_nb)
    #            if gn is not self.current_goal_node]
    #     return pgn
    #

    def pending_goal_nodes(self, truncated=True) -> [GoalNode]:
        """
        The list of unsolved oal nodes, except current_goal_node.
        """
        pgn = [gn for gn in self.unsolved_goal_nodes(truncated)
               if gn is not self.current_goal_node]
        return pgn

    def go_to_first_unsolved_node(self):
        """
        Set current_goal_node to the next unsolved goal node. This is called
        when current_goal_node is solved.
        """

        # TODO: modify to allow permutation of unsolved nodes.
        unsolved_goal_nodes = self.unsolved_goal_nodes(truncated=False)
        if unsolved_goal_nodes:
            self.current_goal_node = unsolved_goal_nodes[0]

    def set_no_more_goals(self):
        """
        Artificially set current_goal_nodes to display "no more goals".
        """
        proof_step = self.current_goal_node.child_proof_step
        no_more_goals = GoalNode.no_more_goals(proof_step)
        self.current_goal_node = no_more_goals

    def add_outcomes(self):
        """
        Artificially add outcomes in brother node (if exists), or even create a
        virtual brother node to display "it suffices" proof step in proof tree.
        """
        if self.current_goal_node.is_auxiliary_goal:
            brother = self.current_goal_node.brother
            target = self.current_goal_node.goal.target.math_type
            brother.set_temporary_new_context([target])
        elif self.current_goal_node.is_suffices_to:
            proof_step = self.current_goal_node.parent
            # goal = proof_step.proof_state.goals[0]
            brothers = [VirtualBrotherAuxGoalNode(parent=proof_step,
                                                  # goal=goal,
                                                  type_='premise'),
                        VirtualBrotherAuxGoalNode(parent=proof_step,
                                                  # goal=goal,
                                                  type_='operator')]
            self.current_goal_node.outcomes = brothers

    def process_new_proof_step(self, new_proof_step: ProofStep):
        """
        Create new GoalNodes and add them into the tree according to the
        provided new_proof_step. First call creates the root_node if there is
        none. The next proof_step should be created after this is called,
        with current_goal_node as a parent.

        The new_proof_step is set as the child_proof_step of
        self.current_goal_node, and it turns it receives one or two GoalNodes as
         its children. Note that this happens even if the new_proof_step
         solves the current goal; this is crucial to be able to correctly
         prune the ProofTree when user start a new step after some undoing.

         Note that the ProofSteps corresponding to history moves are NOT
         processed, thue they do not appear in the ProofTree. They should
         rather be sees as acting on the current_goal_node of the ProofTree.
        """

        self.previous_goal_node = self.current_goal_node
        new_proof_state = new_proof_step.proof_state
        assert new_proof_state is not None

        # ─────── Very first step ─────── #
        if not self.root_node:
            self.root_node = RootGoalNode(new_proof_step,
                                          new_proof_state.goals[0])
            new_proof_step.children_goal_nodes = [self.root_node]
            self.current_goal_node = self.root_node
            return

        # ─────── Case of new step after history move ─────── #
        # self.set_truncate_mode(False)
        child_proof_step = self.current_goal_node.child_proof_step
        if child_proof_step:
            # Remove everything beyond parent_proof_step before proceeding
            self.current_goal_node.prune_from(child_proof_step.pf_nb)

        # self.set_truncate_mode(True)

        # ─────── Compute delta goal ─────── #
        # NB; this must be done BEFORE connecting new_proof_step, since we
        # want the nb of unsolved goals BEFORE new_proof_step (which might
        # solved (maybe by sorry) the current_goal_node).
        new_goal = new_proof_state.goals[0]
        unsolved_gn = self.unsolved_goal_nodes()
        delta_goal = (len(new_proof_state.goals)
                      - len(unsolved_gn))
        log.info("Current unsolved goal nb:")
        log.debug([g.goal_nb for g in unsolved_gn])
        log.info(f"Delta goals: {delta_goal}")

        # ─────── Connect new_proof_step to ProofTree ─────── #
        self.current_goal_node.child_proof_step = new_proof_step

        # ─────── Create new GoalNodes ─────── #
        if delta_goal == -1:  # current goal solved
            new_proof_step.has_solved_one_goal = True
            if unsolved_gn:
                # FIXME: this won't work if current_node was not 1st unsolved.
                self.go_to_first_unsolved_node()
            else:  # No more goals!
                self.set_no_more_goals()
            children_gn = [self.current_goal_node]
            #  Refresh goal and set tag:
            self.current_goal_node.set_goal(new_goal)
            self.current_goal_node.goal_has_changed = True
        else:
            next_goal_node = GoalNode(parent=new_proof_step,
                                      goal=new_goal)
            self.current_goal_node = next_goal_node
            if delta_goal == 0:  # Generic case
                children_gn = [next_goal_node]
            else:  # Fork node: two sub-goals
                assert delta_goal == 1
                # Provisionally create other goal node
                other_goal = new_proof_state.goals[1]
                other_goal.name_bound_vars()
                other_goal_node = GoalNode(parent=new_proof_step,
                                           goal=other_goal)
                children_gn = [next_goal_node, other_goal_node]

            self.add_outcomes()

        new_proof_step.children_goal_nodes = children_gn
        self.last_proof_step = new_proof_step

        # ─────── Compare with previous state and tag properties ─────── #
        previous_goal = self.current_goal_node.parent_node.goal
        Goal.compare(new_goal, previous_goal)
        # print("ProofTree:")
        # print(str(self))

    # def prune(self, proof_step_nb):
    #     """
    #     Remove from self all information posterior to the given proof_step.
    #     This includes info on ContextMathObjects, so that self should be as
    #     it was before.
    #     Value proof_step_nb = 0 corresponds to initial goal (as this is the
    #     step number of self.root_node.parent).
    #     """
    #     self.root_node.prune_from(proof_step_nb)

    def __str__(self):
        return str(self.root_node)
