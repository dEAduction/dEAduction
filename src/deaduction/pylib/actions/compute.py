"""
########################################
# compute.py : Actions for computation #
########################################

Author(s)     : - Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
Maintainer(s) : - Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
Created       : October 2023 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

This file is part of dEAduction.

    dEAduction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    dEAduction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging

from deaduction.pylib.actions     import (action,
                                          InputType,
                                          MissingParametersError,
                                          WrongUserInput,
                                          WrongProveModeInput,
                                          WrongUseModeInput,
                                          test_selection,
                                          test_prove_use,
                                          CodeForLean)

log = logging.getLogger(__name__)


@action()
def action_sum(proof_step) -> CodeForLean:
    pass


@action()
def action_simplify(proof_step) -> CodeForLean:
    pass


@action()
def action_factorize(proof_step) -> CodeForLean:
    pass


@action()
def action_expand(proof_step) -> CodeForLean:
    pass


@action()
def action_transitivity(proof_step) -> CodeForLean:
    pass


@action()
def action_commute(proof_step) -> CodeForLean:
    pass


@action()
def action_triangular_inequality(proof_step) -> CodeForLean:
    pass



