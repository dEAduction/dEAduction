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
    lean_code: CodeForLean = None
    effective_code: CodeForLean = None  # CodeForLean that proved effective
    # no_more_goals = False
    previous_proof_state = None
    analysis = None
    new_proof_state = None
    # 1 = WUI, 2 = FRE, 3 = TIMEOUT, 4 = UNICODE, 5 = No proof state:
    error_type: int = 0
    error_list: Optional[List]
    _error_msg: str = ''
    _success_msg: str = ''

    def __init__(self, lean_code, effective_code=None,  # no_more_goals=False,
                 previous_proof_state: ProofState = None,
                 analysis: tuple = None,
                 error_type=0, error_list=None):
        self.lean_code = lean_code
        self.effective_code = effective_code
        # self.no_more_goals = no_more_goals
        self.previous_proof_state = previous_proof_state
        self.analysis = analysis
        if analysis:
            hypo_analysis, targets_analysis = analysis
            proof_state = ProofState.from_lean_data(hypo_analysis,
                                                    targets_analysis,
                                                    to_prove=True,
                                                    previous_proof_state=
                                                    previous_proof_state)
            self.new_proof_state = proof_state
        self.error_type = error_type
        self.error_list = error_list if error_list else []

    @property
    def success_msg(self):
        if self.no_more_goals:
            msg = _("Proof complete")
        elif self.effective_code:
            msg = self.effective_code.success_msg
        else:
            msg = self.lean_code.success_msg
        return msg

    @property
    def goals(self):
        if self.new_proof_state:
            return self.new_proof_state.goals

    @property
    def no_more_goals(self):
        return self.new_proof_state and not self.goals

