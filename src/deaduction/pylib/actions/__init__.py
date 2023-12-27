"""
# __init__.py #
    
    https://en.meming.world/images/en/8/8e/All_Right_Then%2C_Keep_Your_Secrets.jpg

Author(s)     : Marguerite Bin bin.marguerite@gmail.com
Maintainer(s) : Marguerite Bin bin.marguerite@gmail.com
Created       : 07 2020 (creation)
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

from .actiondef import (    Action,
                            action)

from .exceptions import (InputType,
                         MissingParametersError,
                         CalculatorRequest,
                         MissingCalculatorOutput,
                         WrongUserInput,
                         WrongProveModeInput,
                         WrongUseModeInput,
                         SelectDefaultTarget,
                         test_selection,
                         test_prove_use)

from .synthetic_proof_step import SyntheticProofStepType, SyntheticProofStep

from .code_for_lean import (LeanCombinator,
                            CodeForLean,
                            get_effective_code_numbers)

from .generic import action_definition

from .logic import (action_forall,
                    action_exists,
                    action_implies,
                    action_and,
                    action_or,
                    action_not,
                    action_equal,
                    action_map)

from .proofs import action_proof_methods, introduce_new_subgoal, ProofMethods
from .magic import action_assumption, context_obj_solving_target
from .compute import action_sum
from .special_actions import drag_n_drop


