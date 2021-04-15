"""
#################################
# __main__.py : Test deaduction #
#################################

Launch deaduction, and an auto_test on one or several exercises from a given
course. This module may be launched with the following arguments:
* choice of a directory, with  one of the two equivalent syntaxes:
    -d <directory path>
    --directory=<directory path>
In this first case, all lean files whose name starts with "test" are
collected, and all exercises with AutoStep metadata in one of these files are
tested. in this case, other arguments have no effect.
* choice of a course file with either:
    -c <path to a lean or pkl file>
or  --course=<path to a lean or pkl file>
* choice of an exercise inside the given course, with either
    -e <lean name or index of the exercise in course.exercises>
or  --exercise=<lean name or index>
* '++', either alone or immediately following the name or number of exercise,
indicate that all exercises following the given one will be tested.

If no file or directory are indicated in arguments, then a box will ask user
to select a file.

The test simulates user acting on the interface with the metadata found in
the field "AutoTest" of the selected exercises. Only exercises with metadata
in this field will be tested.

Author(s)      : Frédéric Le Roux <frederic.le-roux@imj-prg.fr>

Maintainers(s) : Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
Date           : April 2021

Copyright (c) 2021 the dEAduction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    d∃∀duction is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with d∃∀duction. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import qtrio
import trio
from sys import argv
from functools import partial
from typing import Optional
from pathlib import Path

from deaduction.pylib.coursedata                 import Course, Exercise
from deaduction.pylib                            import logger

import deaduction.pylib.config.dirs              as     cdirs
import deaduction.pylib.config.environ           as     cenv
import deaduction.pylib.config.site_installation as     inst
import deaduction.pylib.config.vars              as     cvars

from deaduction.dui.__main__ import Container

from deaduction.pylib.autotest import ( select_course,
                                        select_exercise)

# (non-exhaustive) list of logger domains:
# ['lean', 'ServerInterface', 'Course', 'deaduction.dui',
#  'deaduction.pylib.coursedata', 'deaduction.pylib.mathobj', 'LeanServer']

###################
# Configuring log #
###################
# Change your own settings in .deaduction-dev/config.toml
# log_domains = cvars.get("logs.domains", [""])
# log_level = cvars.get("logs.display_level", "info")
# logger.configure(domains=log_domains,
#                  display_level=log_level)

log = logging.getLogger(__name__)


def coex_from_argv() -> (Optional[Path], Course, Exercise, bool):
    """
    Try to build Course and Exercise object from arguments.
    """
    dir_path = None
    course_path = None
    exercise_like = None
    course = None
    exercise = None
    all_from_this_one = False

    for arg in argv[1:]:
        if arg.startswith('--directory='):
            dir_path = arg[len("--directory="):]
        elif arg == '-d':
            dir_path = argv[argv.index(arg)+1]
        elif arg.startswith("--course="):
            course_path = arg[len("--course="):]
        elif arg == "-c":
            course_path = argv[argv.index(arg)+1]
        elif arg.startswith("--exercise="):
            exercise_like = arg[len("--exercise="):]
        elif arg == "-e":
            exercise_like = argv[argv.index(arg)+1]

    if dir_path:
        dir_path = Path(dir_path)
        return dir_path, None, None, None

    if course_path and exercise_like:
        if exercise_like.endswith('++'):
            all_from_this_one = True
            exercise_like = exercise_like[:-2]
        elif  argv[-1] in ("--from", '++'):
            all_from_this_one = True
        log.debug('Searching course and exercise...')
        course, exercise = select_exercise(course_path, exercise_like)
    elif course_path:
        course = select_course(course_path)

    return None, course, exercise, all_from_this_one


def get_exercises_from_dir(dir_path: Path):
    test_files = [file for file in dir_path.iterdir()
                  if (file.suffix == '.lean' or file.suffix == '.pkl')
                  and file.name.startswith('test')]
    log.info(f"looking for deaduction test files in {dir_path.name}")
    log.info(f" found {len(test_files)} files")
    log.info(f"Files names must start with 'test'")

    exercises = []
    for course_file in test_files:
        course = select_course(course_file)
        exo_for_this_course = []
        for exo in course.exercises:
            if exo.auto_test:
                exo_for_this_course.append(exo)
        print(f"{len(exo_for_this_course)} exercises found for test in this "
              f"course")
        exercises.extend(exo_for_this_course)
    return exercises


def get_exercises(course: Optional[Course],
                  exercise: Optional[Exercise],
                  all_from_this_one: bool) -> [Exercise]:
    """
    Build exercises list from data: just one exercise (if not
    all_from_this_one), or all from the given one.
    """

    # Case 1: no course --> choose a course (but no exercise)
    if not course:
        course = select_course()

    # Case 2: course, no exercise --> test all exercises with AutoTest
    if course and not exercise:
        exercises = [exo for exo in course.exercises if exo.auto_test]
        if not exercises:
            log.debug(f"No AutoTest found in course {course.title}")
            quit()
        else:
            exercises = exercises

    # Case 3: course and exercise --> test just this one, or all from
    # this one, according to all_from_this_one
    else:
        if not isinstance(exercise, Exercise):
            log.debug(f"Not an Exercise instance: {exercise}")
            quit()
        if all_from_this_one:
            exo_nb = course.exercises.index(exercise)
            exercises = [exo for exo in course.exercises[exo_nb:]
                         if exo.auto_test]

        else:
            exercises = [exercise]
    return exercises


async def auto_test(container: Container):
    """
    Test the Exercise's instance container.exercise by listening to
    deaduction signals and simulating user pressing buttons according to
    the instructions found in exercise.auto_test.

    Note that just one exercise is tested, this function is not in charge of
    processing to the next exercise to be tested.
    """

    # Auto-steps loop
    exercise = container.exercise
    log.info(f"Testing exercise {exercise.pretty_name}")
    auto_steps = exercise.refined_auto_steps
    emw = container.exercise_window

    async with qtrio.enter_emissions_channel(signals=[emw.ui_updated]) as \
            emissions:
        async for emission in emissions.channel:
            log.debug("ui_updated received")
            step = auto_steps[0]
            log.debug(f"auto_step found: {step}")
            if not step:
                log.debug("Found 'None' step, giving up")
                emw.close()
                break

            # Collect selection from e.g. 'H1', 'x', '@p2', '@O3'
            auto_selection = []
            properties = [item.mathobject for item in emw.ecw.props_wgt.items]
            objects = [item.mathobject for item in emw.ecw.objects_wgt.items]
            goal = emw.servint.proof_state.goals[0]
            for name in step.selection:
                selection = None
                with trio.move_on_after(5):
                    # Not clear to me why deaduction may not have
                    # finished constructing goal, but this happens.
                    # So we give it 1 more second to complete the
                    # construction.
                    while not selection:
                        if name.startswith('@O'):
                            selection = objects[int(name[2:])-1]
                        elif name.startswith('@P'):
                            selection = properties[int(name[2:])-1]
                        else:
                            if name.startswith('@'):  # @ should not be here but...
                                name = name[1:]
                            selection = goal.math_object_from_name(name)
                        if not selection:
                            properties = [item.mathobject for item in
                                          emw.ecw.props_wgt.items]
                            objects = [item.mathobject for item in
                                       emw.ecw.objects_wgt.items]
                            goal = emw.servint.proof_state.goals[0]

                if selection:
                    auto_selection.append(selection)
                else:
                    log.debug("Bad selection in auto_step")
                    quit()

            selection_names = [item.display_name for item in auto_selection]
            log.debug(f"Selection: {selection_names}")
            auto_user_input = [int(item) if item.isdecimal() else item
                               for item in step.user_input]

            if step.button:  # Auto step is a button step
                action_btn = emw.ecw.action_button(step.button)
                log.debug(f"Button: {action_btn}")
                await emw.process_async_signal(partial(
                    emw.__server_call_action,
                    action_btn, auto_selection,
                    auto_user_input))

            elif step.statement:  # Auto step is a statement step
                statement_widget = emw.ecw.statements_tree.from_name(
                    step.statement)
                log.debug(f"Statement: {statement_widget}")
                await emw.process_async_signal(partial(
                    emw.__server_call_statement,
                    statement_widget,
                    auto_selection))
            else:
                log.warning("Auto-step loop: empty step")

            auto_steps = auto_steps[1:]
            if not auto_steps:
                break


async def main():
    """
    """

    #############################
    # Choose course and exercise #
    #############################
    dir_, course, exercise, all_from_this_one = coex_from_argv()
    if dir_:
        exercises = get_exercises_from_dir(dir_)
    else:
        exercises = get_exercises(course, exercise, all_from_this_one)

    if not exercises:
        quit()
    else:
        log.debug(f"Found {len(exercises)} with AutoTest metadata")

    async with trio.open_nursery() as nursery:
        # Create container and enter test mode
        container = Container(nursery)
        container.exercises = exercises

        # Main loop: quit if window is closed by user or if there is no more
        # exercise.
        signals = [container.test_complete,
                   container.close_exercise_window]
        try:
            async with qtrio.enter_emissions_channel(signals=signals) as \
                    emissions:
                log.info("Entering main test loop")

                # Test first exercise
                container.exercise = container.exercises[0]
                container.exercises = container.exercises[1:]
                await container.test_exercise()
                container.nursery.start_soon(auto_test, container)

                async for emission in emissions.channel:
                    if emission.is_from(container.test_complete) \
                            and container.exercises:  # Test next exercise
                        log.debug("Test complete -> next exercise")
                        log.debug(f"{len(Container.exercises)} exercises "
                                  f"remaining to test")
                        # Close window
                        container.exercise_window.window_closed.disconnect()
                        container.exercise_window.close()
                        if container.exercises:
                            container.exercise = container.exercises[0]
                            container.exercises = container.exercises[1:]
                            await container.test_exercise()
                            container.nursery.start_soon(auto_test, container)
                        else:
                            log.debug("No more exercises to test!")
                            break

                    elif emission.is_from(container.close_exercise_window):
                        log.info("Exercise window closed")
                        break

        finally:
            # Finally closing d∃∀duction
            if container.servint:
                await container.servint.file_invalidated.wait()
                container.servint.stop()  # Good job, buddy
                log.info("Lean server stopped!")
            if container.nursery:
                container.nursery.cancel_scope.cancel()


if __name__ == '__main__':
    log.info("Starting autotest...")
    log.info("Run with '-d ../../../tests/autotest_exercises/' to test all "
             "exercises")

    cenv.init()
    cdirs.init()
    inst.init()

    qtrio.run(main)
    log.debug("qtrio finished")

