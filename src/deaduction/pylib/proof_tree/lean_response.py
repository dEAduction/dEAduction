"""
# lean_response.py : a class encoding Lean's response #

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
import logging
from typing import Optional, List

from deaduction.pylib.actions import CodeForLean
from deaduction.pylib.proof_state import ProofState

log = logging.getLogger(__name__)

global _


class LeanResponse:
    """
    A class encoding Lean's response to the usr action.
    """
    # no_more_goals = False
    analysis = None
    new_proof_state = None
    # 1 = WUI, 2 = FRE, 3 = TIMEOUT, 4 = UNICODE, 5 = No proof state:
    error_type: int = 0
    error_list: Optional[List]
    _error_msg: str = ''
    _success_msg: str = ''

    def __init__(self, proof_step=None, analyses: tuple = None,
                 error_type=0, error_list=None,
                 from_previous_state=False):
        self.proof_step = proof_step
        self.analyses = analyses
        self.from_previous_state = from_previous_state
        self.error_type = error_type
        self.error_list = error_list if error_list else []

        if analyses:
            hypo_analyses, targets_analyses = analyses
            proof_state = ProofState.from_lean_data(hypo_analyses,
                                                    targets_analyses,
                                                    to_prove=True,
                                                    previous_proof_state=
                                                    self.previous_proof_state)
            self.new_proof_state = proof_state

        # self.debug()

    def debug(self):
        nb = len(self.new_proof_state.goals)
        print(f"Lean response: {nb} goals")
        for g in self.new_proof_state.goals:
            print("   " + g.target.math_type_to_display(format_='utf8'))

    @property
    def lean_code(self):
        if self.proof_step:
            return self.proof_step.lean_code
        else:
            return CodeForLean.empty_code()

    @property
    def effective_code(self):
        if self.proof_step:
            return self.proof_step.effective_code

    @property
    def previous_proof_state(self):
        """
        Return previous_proof_state if info is available, but only when using
        the method from previous state, since otherwise the pertinent
        previous proof states are included in the new proof state
        (see ProofState.from_lean_data() ).
        """
        if self.proof_step and self.from_previous_state:
            return self.proof_step.proof_state

    @property
    def goals(self):
        if self.new_proof_state:
            return self.new_proof_state.goals

    @property
    def no_more_goals(self):
        return self.new_proof_state and not self.goals

    @property
    def success_msg(self):
        if self.no_more_goals:
            msg = _("Proof complete")
        elif self.effective_code:
            msg = self.effective_code.success_msg
        elif self.lean_code:
            msg = self.lean_code.success_msg
        else:
            msg = ""
        return msg


