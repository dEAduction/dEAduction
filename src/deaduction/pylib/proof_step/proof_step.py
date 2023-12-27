"""
###############################################
# proof_step.py : provide the ProofStep class #
###############################################

The ProofStep class is used to store all pieces of information concerning
one step of a proof. This includes context selection and action, Lean Code,
success or error msg, resulting proofstate, and so on.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 05 2021 (creation)
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

from dataclasses import dataclass
from typing import Optional, Union
from copy import copy
import logging

from deaduction.pylib.text.tooltips import button_symbol
from deaduction.pylib.mathobj import MathObject
from deaduction.pylib.coursedata.auto_steps import UserAction
from deaduction.pylib.actions import ProofMethods
# from deaduction.pylib.proof_state import LeanResponse

log = logging.getLogger(__name__)
global _


@dataclass()
class NewGoal:
    """
    This class allows to store the creation of a new goal. In particular,
    the msg property provides a msg that can be displayed and gives
    information about the resulting branching of the proof,
    e.g. First case/ second case, proof of first implication, ...

    An instance is created from CodeForLean, by looking at special attributes
    (conjunction, disjunction, subgoal). The old/new hypos, or new target
    are stored. Using these attributes, the msg property computes msgs for
    the user indicating the kind of new goal that has appeared.
    """
    node_type:  str  # 'or', 'and', 'iff', 'subgoal'
    counter:    int  # 1st or 2nd case / target
    old_hypo:   Optional[Union[MathObject, str]]    # e.g. 'P or Q'
    old_target: Optional[Union[MathObject, str]]  # e.g. 'P and Q'
    new_hypo:   Optional[Union[MathObject, str]]  # e.g. 'P'
    new_target: Optional[Union[MathObject, str]]  # e.g. 'P'

    @classmethod
    def from_lean_code(cls, lean_code, delta=1):  # Type: [NewGoal, NewGoal]
        """
        If lean_code will create new goals, return them.
        """
        more_goals = []
        if lean_code.conjunction:
            p_and_q, p, q = lean_code.conjunction
            type_ = 'and'
            if isinstance(p_and_q, MathObject) and p_and_q.is_iff(
                    is_math_type=True):
                type_ = 'iff'
            new_goal1 = NewGoal(type_, 1, old_hypo=None, old_target=p_and_q,
                                new_hypo=None, new_target=p)
            new_goal2 = NewGoal(type_, 2, old_hypo=None, old_target=p_and_q,
                                new_hypo=None, new_target=q)
            more_goals = [new_goal2, new_goal1]  # Mind the order: pile!
        elif lean_code.disjunction:
            p_or_q, p, q = lean_code.disjunction
            new_goal1 = NewGoal('or', 1, old_hypo=p_or_q, old_target=None,
                                new_hypo=p, new_target=None)
            new_goal2 = NewGoal('or', 2, old_hypo=p_or_q, old_target=None,
                                new_hypo=q, new_target=None)
            more_goals = [new_goal2, new_goal1]
        elif lean_code.subgoal:
            subgoal = lean_code.subgoal
            new_goal = NewGoal('subgoal', 1, old_hypo=None, old_target=None,
                               new_hypo=None, new_target=subgoal)
            more_goals = [new_goal]
        if len(more_goals) < delta:
            # Add generic NewGoals to complete the list
            generic_new_goal = cls.generic()
            more_goals.extend([generic_new_goal] * (delta - len(more_goals)))
        return more_goals

    @classmethod
    def generic(cls):
        return NewGoal('generic', 1, old_hypo=None, old_target=None,
                       new_hypo=None, new_target=None)

    @property
    def msg(self):
        msg = ""
        if self.node_type == 'and':
            if self.counter == 1:
                msg = _("Proof of first property: {}")
            else:
                msg = _("Proof of second property: {}")
            if isinstance(self.new_target, str):
                target = self.new_target
            else:
                target = self.new_target.to_display(format_="utf8")
            msg = msg.format(target)
        elif self.node_type == 'iff':
            if self.counter == 1:
                msg = _("Proof of first implication: {}")
            else:
                msg = _("Proof of second implication: {}")
            if isinstance(self.new_target, str):
                target = self.new_target
            else:
                target = self.new_target.to_display(format_="utf8")
            msg = msg.format(target)
        elif self.node_type == 'or':
            if self.counter == 1:
                msg = _("Fist case:")
            elif self.counter == 2:
                msg=_("Second case:")
            if isinstance(self.new_hypo, str):
                hypo = self.new_hypo
            else:
                hypo = self.new_hypo.to_display(format_="utf8")
            msg += " " + _("assuming {}").format(hypo)
        elif self.node_type == 'subgoal':
            msg = _("Proof of new subgoal: {}").format(self.new_target)
        else:  # Generic case
            msg = _("Proof of new subgoal")
        # msg += " ..."
        return msg


class ProofNode:
    """
    This class encodes a node in the proof, e.g. a point where the proof
    divides into two or more sub-proofs, as happens for a proof by cases,
    or a proof of a conjunction.

    The 'txt" attribute store the NewGoal.msg to be displayed for user
    as a node of the proof outline.
    """
    def __init__(self, parent, txt, history_nb, sub_proof: [] = None):
        super().__init__()
        self.parent: ProofNode = parent
        self.txt = txt
        self.history_nb = history_nb
        self.children = sub_proof if sub_proof else []


class ProofStep:
    """
    Class to store data associated to one step in the proof.
    The step starts with user inputs, and ends with Lean's responses.
    Note that the proof_state attribute is used both for storing the
    proof_state at the beginning of the step, which is used by logical
    action to compute the pertinent Lean Code,
    and for storing the proof_state at the end of the step, to be stored in
    Journal and lean_file's history (and passed to the next proof_step).

    proof_nodes is a class attribute,
    a pile of ProofNode, initialised with an empty ProofNode
    that stands for the whole proof.
    """
    # Fixme: proof_nodes should not be class attributes, for history moves

    # ──────────────── Proof memory ─────────────── #
    pf_nb                    = 0
    initial_proof_node       = ProofNode(parent=None,
                                         txt="Proof",
                                         history_nb=-1,
                                         sub_proof=[])
    proof_nodes: [ProofNode] = None
    property_counter: int    = 1
    current_goal_number: int = 1  # Current number of goal in the proof history
    total_goals_counter: int = 1  # Total number of goals in the proof history
    parent                   = None  # Parent ProofNode
    new_goals: [NewGoal]     = None
    time                     = None
    delta_goals_count        = 0
    children                 = None
    imminent_new_node: Optional[ProofNode]      = None
    history_nb: int          = None

    # ──────────────── Input ─────────────── #
    # selection      = None  # [MathObject]
    # target_selected= False
    # user_input     = None  # [str]
    # button_name    = None  # str, e.g. "exists" or "history_undo".
    # statement      = None  # Statement
    user_action: UserAction = None
    action = None
    is_automatic   = False
    drag_n_drop    = None  # DragNDrop

    lean_code      = None  # CodeForLean

    # ──────────────── Output ─────────────── #
    effective_code            = None  # CodeForLean that proved effective
    # 1 = WUI, 2 = FRE, 3 = TIMEOUT, 4 = UNICODE, 5 = No proof state:
    error_type: Optional[int] = 0
    error_msg: str            = ''
    proof_state               = None
    no_more_goal              = False
    _success_msg: str         = ''
    # AutoStep version, computed in Coordinator.update_proof_step():
    auto_step                 = None
    unsolved_goal_nodes_after = None  # Copy of the proof_tree, for history move

    def __init__(self,
                 proof_nodes=None,
                 new_goals=None,
                 parent=None,
                 property_counter=1,
                 current_goal_number=1,
                 total_goals_counter=1,
                 proof_state=None,
                 history_nb=-1):
        self._children_goal_nodes = []
        self._parent_goal_node = None
        self.property_counter    = property_counter
        self.current_goal_number = current_goal_number
        self.total_goals_counter = total_goals_counter
        if new_goals:
            self.new_goals = new_goals
        else:
            self.new_goals = []
        if parent:
            self.parent = parent
        else:
            self.parent = self.initial_proof_node

        self.user_action = UserAction()

        self.proof_state = proof_state
        # self.selection = []
        # self.target_selected = False
        # self.user_input = []

        self.imminent_new_node = None
        self.history_nb = history_nb
        # Creation of first proof node if none is provided
        self.proof_nodes = proof_nodes if proof_nodes \
            else [self.initial_proof_node]

        # Flags
        self._has_solved_one_goal = None
        self.is_cqfd = False
        self.pf_nb = ProofStep.pf_nb
        ProofStep.pf_nb += 1

    @classmethod
    def next_(cls, proof_step, history_nb):
        """
        Instantiate a copy of proof_step by duplicating attributes that
        should be passed to the next proof_step.
        """

        if proof_step:
            next_parent = proof_step.proof_nodes[-1]
            # log.debug(f"Proof nodes: "
            #           f"{[(pf.txt, pf.parent.txt if pf.parent else None)
            #           for pf in proof_step.proof_nodes]}")
            nps = ProofStep(property_counter=proof_step.property_counter,
                            new_goals=copy(proof_step.new_goals),
                            parent=next_parent,
                            current_goal_number=proof_step.current_goal_number,
                            total_goals_counter=proof_step.total_goals_counter,
                            proof_state=proof_step.proof_state,
                            history_nb=history_nb,
                            proof_nodes=copy(proof_step.proof_nodes)
                            )
            log.debug(f"New proof step, n°{nps.pf_nb}")
            if not proof_step.is_history_move()\
                    and not proof_step.is_error()\
                    and next_parent:
                next_parent.children.append(nps)

        else:
            nps = cls()

        return nps

    def add_new_goals(self, delta):
        if not self.lean_code:
            self.new_goals.append(None)
        else:
            old_proof_node = self.proof_nodes[-1]
            if self.new_goals and (self.lean_code.conjunction
                                   or self.lean_code.disjunction):
                # Last goal will be replaced by first new goal
                self.new_goals.pop()
                self.proof_nodes.pop()
            more_goals = NewGoal.from_lean_code(self.lean_code, delta)
            more_proof_nodes = [ProofNode(parent=old_proof_node,
                                          txt=new_goal.msg,
                                          history_nb = self.history_nb,
                                          sub_proof=[])
                                for new_goal in more_goals]
            # The new ProofNode is a child of the old one
            old_proof_node.children.append(more_proof_nodes[-1])
            self.proof_nodes.extend(more_proof_nodes)
            if more_proof_nodes[-1] is not ProofStep.initial_proof_node:
                self.imminent_new_node = more_proof_nodes[-1]

            self.new_goals.extend(more_goals)

    def update_goals(self):
        """
        Manage the goals pile of self. That is,
        - if self.delta_goals_count > 0, i.e. new goals have been created
        during this step, add NewGoal instances to self.new_goals
        - if self.delta_goals_count < 0, i.e. new goals have been solved,
        then pop items from self.new_goals and self.proof_nodes.
        :return:
        """
        if self.is_error():  # Wrong delta if error (and no need)
            return

        delta = self.delta_goals_count
        if delta > 0:  # A new goal has appeared
            self.total_goals_counter += delta
            self.add_new_goals(delta)  # Manage goal msgs from LeanCode
        elif delta < 0:  # A goal has been solved
            # THe following assume delta is -1
            self.is_cqfd = True
            self.current_goal_number -= delta
            if self.new_goals:
                self.new_goals.pop()  # Remove last goal msg
                self.proof_nodes.pop()
                imminent_new_node = self.proof_nodes[-1]
                if imminent_new_node is not ProofStep.initial_proof_node:
                    self.imminent_new_node = imminent_new_node

    ##############
    # Properties #
    ##############

    @property
    def selection(self):
        return self.user_action.selection

    @selection.setter
    def selection(self, selection):
        self.user_action.selection = selection

    @property
    def target_selected(self):
        return self.user_action.target_selected

    @target_selected.setter
    def target_selected(self, target_selected):
        self.user_action.target_selected = target_selected

    @property
    def button_name(self):
        return self.user_action.button_name

    @button_name.setter
    def button_name(self, button_name):
        self.user_action.button_name = button_name
        if self.statement:
            log.warning("Both statement AND button_name for this "
                        "proof_step.user_action")

    @property
    def statement(self):
        return self.user_action.statement

    @statement.setter
    def statement(self, statement):
        self.user_action.statement = statement
        if self.button_name:
            log.warning("Both button_name AND statement for this "
                        "proof_step.user_action")

    @property
    def user_input(self):
        return self.user_action.user_input

    @user_input.setter
    def user_input(self, user_input):
        self.user_action.user_input = user_input

    @property
    def prove_or_use(self):
        return self.user_action.prove_or_use

    @prove_or_use.setter
    def prove_or_use(self, prove_or_use):
        self.user_action.prove_or_use = prove_or_use

    @property
    def has_solved_one_goal(self):
        return self._has_solved_one_goal

    @has_solved_one_goal.setter
    def has_solved_one_goal(self, yes: bool):
        self._has_solved_one_goal = yes

    @property
    def children_goal_nodes(self):
        return self._children_goal_nodes

    @children_goal_nodes.setter
    def children_goal_nodes(self, goal_nodes):
        self._children_goal_nodes = goal_nodes

    @property
    def parent_goal_node(self):
        return self._parent_goal_node

    @parent_goal_node.setter
    def parent_goal_node(self, goal_node):
        self._parent_goal_node = goal_node

    @property
    def button_symbol(self):
        return button_symbol(self.button_name)

    @property
    def statement_lean_name(self):
        if self.statement:
            return self.statement.lean_name

    @property
    def success_msg(self) -> str:
        if self._success_msg:
            return self._success_msg
        elif self.history_nb == -1:
            return self.beginning_of_proof_msg
        elif self.is_error():
            return ''
        elif self.is_cqfd:
            return self.current_goal_solved_msg
        elif self.is_sorry():
            return self.sorry_msg
        elif self.effective_code:
            return self.effective_code.success_msg
        elif self.lean_code:
            return self.lean_code.success_msg
        else:
            return ''

    @success_msg.setter
    def success_msg(self, msg: str):
        self._success_msg = msg

    @property
    def txt(self):
        if self.success_msg:
            return str(self.history_nb+1) + _(": ") + self.success_msg
        else:
            return str(self.history_nb+1) + _(": ") + _("no message")

    @property
    def txt_debug(self):
        msg = self.success_msg if self.success_msg else ""
        nb = str(self.history_nb+1) if self.history_nb else ""
        txt = "STEP " + nb \
              + " (" + self.short_display() + ")" + _(": ") + msg
        return txt

    @property
    def goal(self):
        if self.proof_state:
            return self.proof_state.goals[0]

    @property
    def nb_of_goals(self):
        """
        Return the number of unsolved goals in self.proof_state
        """
        if self.proof_state:
            return len(self.proof_state.goals)

    @property
    def current_new_goal(self):
        if self.new_goals:
            return self.new_goals[-1]

    @property
    def main_hypo(self):
        if self.selection:
            return self.selection[0]

    @property
    def synthetic_proof_step(self):
        code = self.effective_code if self.effective_code else self.lean_code
        return code.synthetic_proof_step

    @property
    def operator(self):
        code = self.effective_code if self.effective_code else self.lean_code
        return code.operator

    @property
    def rw_item(self):
        code = self.effective_code if self.effective_code else self.lean_code
        return code.rw_item

    @property
    def outcome_operator(self):
        code = self.effective_code if self.effective_code else self.lean_code
        return code.outcome_operator

    @property
    def context_obj_solving(self):
        from deaduction.pylib.actions import context_obj_solving_target
        return context_obj_solving_target(self)

    def is_node(self):  
        """
        True if self is a proof node (a new goal has appeared).
        """
        return self.delta_goals_count and self.delta_goals_count > 0

    def is_undo(self):
        return self.button_name == 'history_undo'

    def is_redo(self):
        return self.button_name == 'history_redo'

    def is_rewind(self):
        return self.button_name == 'history_rewind'

    def is_goto(self):
        return self.button_name == 'history_goto'

    def is_go_to_end(self):
        return self.button_name == 'history_go_to_end'

    def is_history_move(self):
        return self.is_undo() or self.is_redo() \
               or self.is_rewind() or self.is_goto() or self.is_go_to_end()

    def is_error(self):
        return bool(self.error_type)

    def is_action_button(self):
        return self.button_name is not None

    def is_statement(self):
        return self.statement is not None

    def is_definition(self):
        return self.statement and self.statement.is_definition()

    def is_theorem(self):
        return self.statement and self.statement.is_theorem()

    def is_intro_implies(self):
        if not self.parent_goal_node or not self.button_name:
            return False
        target = self.parent_goal_node.goal.target
        tests = [self.button_name.endswith("implies"),
                 not self.selection,
                 target.is_implication(implicit=True),
                 not self.is_error()]
        return all(tests)

    def is_intro_forall(self):
        if not self.parent_goal_node or not self.button_name:
            return False
        tests = [self.button_name.endswith("forall"),
                 not self.selection,
                 self.parent_goal_node.goal.target.is_for_all(implicit=True),
                 not self.is_error()]
        return all(tests)

    def is_push_neg(self):
        return self.button_name == "not" and not self.is_error()

    def is_on_target(self):
        return not self.selection

    def is_and(self):
        if not self.button_name:
            return False
        else:
            return self.button_name.endswith("and")

    def is_iff(self):
        return self.button_name == "iff"

    def is_destruct_iff(self):
        """
        True if an iff context prop has been destroyed.
        """

        if not self.is_iff():
            return False
        if len(self.selection) != 1:
            return False
        return self.selection[0].is_iff()

    def is_equal(self):
        return self.button_name == "equal"

    def is_prove_and_from_ctxt(self):
        """
        True if step has proved 'P AND Q' from P,Q in the context
        """

        if (self.button_name and self.button_name.endswith('and') and
                self.prove_or_use == "prove" and len(self.selection) == 2):
            return True

    def is_prove_exists_from_ctxt(self):
        """
        True if step has proved 'Exists z, P(z)'
        from some x and P(x) in the context.
        """

        if (self.button_name and self.button_name.endswith('exists') and
                self.prove_or_use == "prove" and len(self.selection) == 2):
            return True

    # def rw_item(self):
    #     if self.is_definition():
    #         return _("Definition"), self.statement.pretty_name
    #     elif self.is_statement():
    #         target = self.statement.target
    #         if target.can_be_used_for_substitution():
    #             return _("Theorem"), self.statement.pretty_name
    #         else:
    #             return None

    def is_by_contraposition(self):
        if self.button_name == "proof_methods" and self.user_input:
            idx = ProofMethods.reference_list.index('contraposition')
            return self.user_input[0] == idx

    def is_by_contradiction(self):
        if self.button_name == "proof_methods" and self.user_input:
            idx = ProofMethods.reference_list.index('contradiction')
            return self.user_input[0] == idx

    def is_by_induction(self):
        if self.button_name == "proof_methods" and self.user_input:
            idx = ProofMethods.reference_list.index('induction')
            return self.user_input[0] == idx

    def is_sorry(self):
        if self.button_name == "proof_methods" and self.user_input:
            idx = ProofMethods.reference_list.index('sorry')
            return self.user_input[0] == idx

    def compare(self, auto_test) -> (str, bool):
        """
        Compare self to an auto_test, and write a report if unexpected
        events happened. This is used for auto_test.

        :return: a string containing a written report, and a bool which is
        True iff everything is OK, None if the error or success msg differs,
        and False if there is a more serious difference.
        """
        report = ''
        success = True
        # Case of error
        if self.is_error():
            error_nb = self.error_type
            error_type = auto_test.error_dic[error_nb]
            if not auto_test.error_type:
                report = f"unexpected {error_type}"
                report += f", error msg: {self.error_msg}"
                success = False
            elif auto_test.error_type != error_nb:
                expected_error = auto_test.error_dic[auto_test.error_type]
                report = f"unexpected {error_type}, expected {expected_error}"
                report += f", error msg: {self.error_msg}"
                success = False

        # Error msg
        error_msg = self.error_msg
        if error_msg:
            find = error_msg.find(auto_test.error_msg)
            if find == -1:
                report += f'\nUnexpected error msg: {error_msg}, ' \
                          f'expected: {auto_test.error_msg}'
                success = None
        # Success msg
        success_msg = self.success_msg
        if success_msg:
            find = success_msg.find(auto_test.success_msg)
            if find == -1:
                report += f'\nUnexpected success msg: {success_msg}, ' \
                          f'expected: {auto_test.success_msg}'
                success = None

        return report, success

    def display(self) -> str:
        """Construct a string representation of the proof step, including
        action, context and target."""

        selection = " ".join([item.display_name for item in self.selection])
        user_input = " ".join([str(item) for item in self.user_input])
        button = ""
        statement = ""
        history_move = ""
        if self.is_history_move():
            history_move = self.button_name.replace("_", " ")
        elif self.button_name:
            button = self.button_name  # FIXME: should be symbol?
        elif self.statement:
            statement = self.statement.pretty_name

        if self.is_error():
            error_msg = _("ERROR:") + " " + self.error_msg
            success_msg = ""
        else:
            error_msg = ""
            success_msg = _("Success:") + " " + self.success_msg

        goal = self.proof_state.goals[0]
        goal_txt = goal.print_goal(to_prove=False)

        action_txt =  button + statement + history_move
        selection_txt = ""
        if selection:
            selection_txt = selection + " "
        user_input_txt = ""
        if user_input:
            user_input_txt = " " + user_input

        txt = selection_txt + action_txt + user_input_txt + "\n" \
            + error_msg + success_msg + "\n" \
            + goal_txt + "\n"

        return txt

    def short_display(self) -> str:
        statement = self.statement
        statement_name = statement.pretty_name if statement else ""
        button_name = self.button_name if self.button_name else ""
        txt = button_name + statement_name
        return txt

    def used_properties(self):
        code = self.effective_code if self.effective_code else self.lean_code
        if code and not self.is_error():
            return code.used_properties()
        else:
            return []

    # ──────────────── msgs ─────────────── #
    @property
    def current_goal_solved_msg(self):
        return _("Current goal solved")

    @property
    def sorry_msg(self):
        return _("(Current goal admitted)")

    @property
    def beginning_of_proof_msg(self):
        return _("Beginning of Proof")

    def descendant_proof_steps(self) -> []:
        """
        Return list of descendant proof steps in a depth first search. The
        list does not include self.
        """

        proof_steps = sum([child.descendant_proof_steps()
                          for child in self.children_goal_nodes], [])
        return proof_steps

    def tree_display(self, msg="", level=0):
        """
        Compute a TREE representation of self and children GoalNode /
        ProofSteps, including GoalNode msgs ( "Proof of...") and success msgs.
        """

        indent = " |"
        separator = "__"
        ret = (indent * level) + msg + " --> " + self.txt_debug
        if self.has_solved_one_goal:
            ret += ' //GOAL SOLVED//\n'
            # ret += (indent * level) + (separator * 10) + '\n'
        else:
            ret += '\n'
            children = self.children_goal_nodes
            if len(children) == 1:
                child = children[0]
                child_ps = child.child_proof_step
                if child_ps:
                    ret += child_ps.tree_display(children[0].msg(), level)
                else:
                    ret += indent * level + child.msg() + "/...\n"
            else:  # Indent
                for child_gn in self.children_goal_nodes:
                    child_ps = child_gn.child_proof_step
                    if child_ps:
                        ret += child_ps.tree_display(child_gn.msg(), level+1)
                    else:
                        ret += indent*(level+1) + child_gn.msg() + "/...\n"
                    # Add a separator between children
                    if child_gn != self.children_goal_nodes[-1]:
                        ret += (indent * (level+1)) + (separator * 5) + '\n'
        return ret

    def __str__(self):
        return self.tree_display()
