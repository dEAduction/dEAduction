"""
# test_mathobj.py : test mathobj files #

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 11 2020 (creation)
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

from deaduction.pylib.mathobj import ProofState



########################
# test course creation #
########################


############################
# test MathObject creation #
############################
def test_math_objects_creation(proof_states, lean_data_list):
    """
    Test ProofState.from_lean_data,
    i.e. creation of a ProofState from the lean_data strings
    hypo_analysis, targets_analysis
    which include
        - lean_analysis_with_type  (which parses the lean data)
        - MathObject.from_info_and_children (which creates the MathObject)
    """
    for (proof_state, lean_data) in zip (proof_states, lean_data_list):
        hypo_analysis, target_analysis = lean_data
        computed = ProofState.from_lean_data(hypo_analysis, target_analysis)
        assert proof_state == computed


###########################
# test MathObject display #
###########################
def test_display_contexts(contexts, context_displays):
    """
    test MathObject.format_as_utf8()
    which creates a displayable version of MathObjects
    this tests all the content of display_math.py
    """
    for (context, displays) in zip(contexts, context_displays):
        for (math_object, display) in zip(context, displays):
            (display_object, display_type) = display
            assert display_object == math_object.format_as_utf8()
            math_type = math_object.math_type
            assert display_type == math_type.format_as_utf8(is_math_type=True)


def test_display_targets(targets, target_displays):
    """
    like test_display_contexts, but with another set of data (targets)
    """
    for (target, display) in zip(targets, target_displays):
        assert display == target.math_type.format_as_utf8(is_math_type=True)


########################
# test course creation #
########################
