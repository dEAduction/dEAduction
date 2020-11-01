"""
# test_mathobj.py : test mathobj files #
    
    <#optionalLongDescription>

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

import pytest
from pathlib import Path
import os

from deaduction.pylib.coursedata import Course
from deaduction.pylib.mathobj import MathObject


@pytest.fixture
def course():
    from tests.mathobj.process_for_testing import pickled_items
    dir = os.path.join(os.path.dirname(__file__))
    pkl_path = dir / Path('lean_files/exercises_theorie_des_ensembles.pkl')
    [stored_course] = pickled_items(pkl_path)
    return stored_course


@pytest.fixture
def statements(course):
    return course.statements


@pytest.fixture
def goals(statements):
    goals = [st.initial_proof_state.goals[0] for st in statements]
    return goals


@pytest.fixture
def contexts(goals):
    contexts = [goal.context for goal in goals]
    return contexts


@pytest.fixture
def context_displays(goals):
    displays = [goal.display_context for goal in goals]
    return displays


@pytest.fixture
def targets(goals):
    targets = [goal.target for goal in goals]
    return targets


@pytest.fixture
def target_displays(goals):
    displays = [goal.display_target for goal in goals]
    return displays


########################
# test course creation #
########################


############################
# test MathObject creation #
############################


###########################
# test MathObject display #
###########################


def test_display_contexts(contexts, context_displays):
    for (context, displays) in zip(contexts, context_displays):
        for (math_object, display) in zip(context, displays):
            (display_object, display_type) = display
            assert display_object == math_object.format_as_utf8()
            math_type = math_object.math_type
            assert display_type == math_type.format_as_utf8(is_math_type=True)


def test_display_targets(targets, target_displays):
    for (target, display) in zip(targets, target_displays):
        assert display == target.math_type.format_as_utf8(is_math_type=True)


########################
# test course creation #
########################
