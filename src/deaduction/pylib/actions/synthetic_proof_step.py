"""
##################################################################
# synthetic_proof_step.py : provide the SyntheticProofStep class #
##################################################################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 12 2023 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2023 the d∃∀duction team

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

from enum import IntEnum


class SyntheticProofStepType(IntEnum):
    """
    An enum class that tells proof_tree how to display a ProofStep instance.
    """

    PureContext = 0
    ApplyUnivStatement = 1
    ApplyUnivProp = 2

    ContextRewrite = 20
    TargetRewrite = 30
    Intro = 40
    IntroImplies = 50
    ByCases = 60

    # TODO add conjunction, disjunction


class SyntheticProofStep:
    """
    A class to store the data needed in ProofTree to display a specific
    ProofStep instance.
    """

    def __init__(self, type_: SyntheticProofStepType,
                 premises=None, operator=None, conclusions=None,
                 rw_operator=None):
        self.type_ = type_
        self.premises = premises if isinstance(premises, list) else [premises]
        self.operator = operator
        self.rw_operator = rw_operator
        self.conclusions = conclusions

    def add_premises(self, premises):
        self.premises.extend(premises)
