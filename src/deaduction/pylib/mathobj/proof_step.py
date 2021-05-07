"""
# proof_step.py : <#ShortDescription> #
    
    <#optionalLongDescription>

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
from typing import Optional
from copy import copy
import logging

import deaduction.pylib.logger as logger
from deaduction.pylib.config.i18n import _

from deaduction.pylib.mathobj import MathObject

log = logging.getLogger(__name__)


@dataclass()
class NewGoal:
    node_type:  str  # 'or', 'and'
    counter:    int  # 1st or 2nd case / target
    old_hypo:   Optional[MathObject]  # e.g. 'P or Q'
    old_target: Optional[MathObject]  # e.g. 'P and Q'
    new_hypo:   Optional[MathObject]  # e.g. 'P'
    new_target: Optional[MathObject]  # e.g. 'P'


class ProofStep:
    """
    Class to store data associated to a step in proof.
    The step starts with user inputs, and ends with Lean's responses.
    Note that the proof_state attribute is used both for storing the
    proof_state at the beginning of the step, which is used by logical
    action to compute the pertinent Lean Code,
    and for storing the proof_state at the end of the step, to be stored in
    Journal and lean_file's history.
    """

    # ──────────────── Proof memory ─────────────── #
    property_counter: int    = 0
    current_goal_number: int = 1  # Current number of goal in the proof history
    total_goals_counter: int = 1  # Total number of goals in the proof history
    new_goals: [NewGoal]  = None  # TODO e.g. "Second case: we assume x∈A".
    time                     = None

    # ──────────────── Input ─────────────── #
    selection      = None  # [MathObject]
    user_input     = None  # [str]
    button         = None  # ActionButton or str, e.g. "history_undo".
    statement_item = None  # StatementsTreeWidgetItem
    lean_code      = None  # CodeForLean

    # ──────────────── Output ─────────────── #
    effective_code            = None  # CodeForLean that proved effective
    error_type: Optional[int] = 0  # 1 = WUI, 2 = FRE
    error_msg: str            = ''
    proof_state               = None
    no_more_goal              = False

    def __init__(self,
                 goal_change_msgs=None,
                 property_counter=0,
                 current_goal_number=1,
                 total_goals_counter=1,
                 proof_state=None):
        self.property_counter    = property_counter
        self.current_goal_number = current_goal_number
        self.total_goals_counter = total_goals_counter
        if goal_change_msgs:
            self.goal_change_msgs = goal_change_msgs
        else:
            self.goal_change_msgs = []

        self.proof_state = proof_state
        self.selection = []
        self.user_input = []

    @classmethod
    def next(cls, proof_step):
        """
        Instantiate a copy of proof_step by duplicating attributes that
        should be pass to the next proof_step.
        """

        pf = proof_step
        npf = ProofStep(property_counter=pf.property_counter,
                        goal_change_msgs=copy(pf.goal_change_msgs),
                        current_goal_number=pf.current_goal_number,
                        total_goals_counter=pf.total_goals_counter,
                        proof_state=pf.proof_state
                        )
        return npf

    @property
    def success_msg(self):
        if self.is_error():
            return ''
        elif self.effective_code:
            return self.effective_code.success_msg
        elif self.lean_code:
            return self.lean_code.success_msg
        else:
            return ''

    @property
    def goal(self):
        if self.proof_state:
            return self.proof_state.goals[0]
        else:
            return None

    def is_undo(self):
        return self.button == 'history_undo'

    def is_redo(self):
        return self.button == 'history_redo'

    def is_rewind(self):
        return self.button == 'history_rewind'

    def is_history_move(self):
        return self.is_undo() or self.is_redo() or self.is_rewind()

    def is_error(self):
        return bool(self.error_type)

    def is_cqfd(self):
        return hasattr(self.button, 'symbol') and \
               self.button.symbol == _("goal!")
        # NB: this should be action_assumption.symbol,
        # but unable to import this here

    def compare(self, auto_test) -> (str, bool):
        """
        Compare self to an auto_test, and write a report if unexpected
        happened. This is used for auto_test.

        :return: a string containing a written report, and a bool which is
        True iff everything is OK.
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
                success = False
        # Success msg
        success_msg = self.success_msg
        if success_msg:
            find = success_msg.find(auto_test.success_msg)
            if find == -1:
                report += f'\nUnexpected success msg: {success_msg}, ' \
                          f'expected: {auto_test.success_msg}'
                success = False

        return report, success

    def display(self) -> str:
        """Construct a string representation of self."""

        selection = " ".join([item.display_name for item in self.selection])
        user_input = " ".join([str(item) for item in self.user_input])
        button = ""
        statement = ""
        history_move = ""
        if self.button:
            button = self.button.symbol
        elif self.statement_item:
            statement = self.statement_item.statement.pretty_name
        elif self.is_history_move():
            history_move = self.button.replace("_", " ")

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




@dataclass
class Proof:
    """
    This class encodes a whole proof history, maybe uncompleted (i.e. the
    goal is not solved) as a list of ProofStates and Actions.

    It provides a method that counts the number of goals during the proof,
    and tells if a goal has been solved, or if a new goal has emerged during
    the last step of the proof. This piece of info is displayed in the UI.
    """

    # TODO: implement a display_tree method

    steps: [ProofStep]  # A proof is a sequence of proof steps.
