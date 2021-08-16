"""
# conftest.py : <#ShortDescription> #
    
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
import logging

import ctypes
import logging
import qtrio
import threading
import trio
import pytest

from PySide2.QtCore import ( QObject,
                             Signal,
                             Slot  )

from deaduction.dui.stages.exercise              import ExerciseMainWindow
from deaduction.dui.stages.start_coex            import StartCoExStartup

from deaduction.dui.stages.missing_dependencies  import (InstallingMissingDependencies,
                                                         WantInstallMissingDependencies )

from deaduction.pylib.coursedata                 import Exercise
from deaduction.pylib                            import logger
from deaduction.pylib.server                     import ServerInterface

import deaduction.pylib.config.dirs              as     cdirs
import deaduction.pylib.config.environ           as     cenv
import deaduction.pylib.config.site_installation as     inst
import deaduction.pylib.config.vars              as     cvars

from deaduction.pylib.coursedata import Exercise
from deaduction.dui.__main__ import WindowManager
log = logging.getLogger(__name__)



async def essai():
    pass


@pytest.fixture
async def container(nursery, exercise):  # NB: nursery is pytest-trio fixture
    cenv.init()
    cdirs.init()
    inst.init()
    container = WindowManager(nursery, exercise)
    return container


@pytest.fixture()
async def exercise_main_window(qbot, container: WindowManager):
    container.start_exercise(container.exercise)
    container.nursery.start_soon(container.solve_exercise)
    return container.exercise_window


@pytest.fixture
def exercises(course):
    exercises = (statement for statement in course.statements if isinstance(
        statement, Exercise))
    return exercises


@pytest.fixture
def course():
    from tests.lean_files_for_tests.process_for_testing import pickled_items
    dir = os.path.join(os.path.dirname(__file__))
    pkl_path = dir / Path(
        'lean_files_for_tests/exercises_for_tests.pkl')
    [stored_course] = pickled_items(pkl_path)
    return stored_course


@pytest.fixture
def course_path(course):
    return course.course_path

@pytest.fixture
def file_content(course):
    return course.file_content


@pytest.fixture
def statements(course):
    return course.statements


@pytest.fixture
def lean_data_list(course):
    statements = course.statements
    lean_data_list = [st.initial_proof_state.lean_data for st in statements]
    return lean_data_list


@pytest.fixture
def proof_states(statements):
    proof_states = [st.initial_proof_state for st in statements]
    return proof_states


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
