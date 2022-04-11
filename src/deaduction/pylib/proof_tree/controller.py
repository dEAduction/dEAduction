"""
###############################################################################
# controller.py: a class to control the proof_tree_widget from the proof_tree #
###############################################################################

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

from deaduction.dui.elements import (ProofTreeWindow, WidgetGoalBlock, IntroWGB,
                                     ByCasesBlock, PureContextBlock)
from .proof_tree import ProofTree


class Controller:
    """
    A class to create and update a ProofTreeWindow that reflects a ProofTree.
    """

    def __init__(self, proof_tree):
        self.proof_tree = proof_tree
        self.proof_tree_window = ProofTreeWindow()
        self.update()

    def update(self):
        pass


