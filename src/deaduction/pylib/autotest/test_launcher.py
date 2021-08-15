"""
#################################
# __main__.py : Test deaduction #
#################################

Launch deaduction, and a test on one or several exercises from a given
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
import time
import qtrio
import trio
from sys import argv
from functools import partial
from typing import Optional
from pathlib import Path
import pickle5 as pickle
import argparse

from deaduction.pylib                            import logger

import deaduction.pylib.config.dirs              as     cdirs
import deaduction.pylib.config.environ           as     cenv
import deaduction.pylib.config.site_installation as     inst
import deaduction.pylib.config.vars              as     cvars
import deaduction.pylib.config.i18n

from deaduction.dui.__main__ import Container
from deaduction.dui.stages.test import QTestWindow

from deaduction.pylib.coursedata import Course, Exercise
from deaduction.pylib.autotest import ( select_course,
                                        select_exercise)

# (non-exhaustive) list of logger domains:
# ['lean', 'ServerInterface', 'Course', 'deaduction.dui',
#  'deaduction.pylib.coursedata', 'deaduction.pylib.mathobj', 'LeanServer']

###################
# Configuring log #
###################
# Change your own settings in .deaduction-dev/config.toml
log_domains = cvars.get("logs.domains", [""])
# log_level = cvars.get("logs.display_level", "info")
# logger.configure(domains=log_domains)
log = logging.getLogger(__name__)

arg_parser = argparse.ArgumentParser("Start deaduction in test mode")
arg_parser.add_argument('--directory', '-d', help="Path for directory")
arg_parser.add_argument('--course', '-c', help="Course filename")
arg_parser.add_argument('--exercise', '-e', help="Exercise (piece of) name")
arg_parser.add_argument('--more', '-m',
                        action='store_true',
                        help="If some exercise is specified, test all "\
                             "exercise from this one",
                        )

#######################
# Choice of exercises #
#######################


def exercise_from_pkl(exercise_like, dir_path):
    """
    Get exercise from exercise_like which should be a pkl file in dir_path,
    or in cdirs.test_exercises if dir_path is None.
.
    :param dir_path: a Path, or None
    :param exercise_like: str name of exercise, or file_path
    :return:
    """
    if isinstance(exercise_like, str):
        if not exercise_like.endswith('.pkl'):
            exercise_like += '.pkl'
        if not dir_path:
            file_path = cdirs.test_exercises / exercise_like
        else:
            file_path = dir_path / exercise_like
    else:
        file_path = exercise_like

    [exercise] = pickled_items(file_path)
    # log.debug(f"Pickled object {type(exercise)}")
    return exercise


def pickled_items(filename):
    """ Unpickle a file of pickled data. """
    with filename.open(mode="rb") as input:
        while True:
            try:
                yield pickle.load(input)
            except EOFError:
                break


def coex_from_argv() -> (Optional[Path], Course, Exercise, bool):
    """
    Try to build Course and Exercise object from arguments.
    """
    course = None
    exercise = None

    args = arg_parser.parse_args(argv[1:])
    dir_path = args.directory
    course_path = args.course
    exercise_like = args.exercise
    all_from_this_one = args.more
    # print(args)

    if dir_path:
        dir_path = Path(dir_path)

    if course_path and exercise_like:
        if exercise_like.endswith('++'):
            all_from_this_one = True
            exercise_like = exercise_like[:-2]
        elif  argv[-1] in ("--from", '++'):
            all_from_this_one = True
        log.debug('Searching course and exercise...')
        course, exercise = select_exercise(course_path, exercise_like)
    elif exercise_like:
        exercise = exercise_from_pkl(exercise_like, dir_path)
        dir_path = None
    elif course_path:
        course = select_course(course_path)

    return dir_path, course, exercise, all_from_this_one


def get_exercises_from_dir(dir_path: Path):
    test_course_files = [file for file in dir_path.iterdir()
                         if file.suffix == '.lean'
                         and file.name.startswith('test')]

    test_exercise_files = [file for file in dir_path.iterdir()
                           if file.suffix == '.pkl'
                           and file.name.startswith('test_exercise')]

    nb_files = len(test_course_files) + len(test_exercise_files)
    log.info(f"looking for deaduction test files in {dir_path.name}")
    log.info(f" found {nb_files} files")
    # log.debug(f"{test_course_files}{test_exercise_files}")
    if not nb_files:
        log.info(f"Files names must start with 'test'")

    exercises = []
    for course_file in test_course_files:
        course = select_course(course_file)
        exo_for_this_course = []
        for exo in course.exercises:
            if exo.auto_test:
                exo_for_this_course.append(exo)
        print(f"{len(exo_for_this_course)} exercises found for test in this "
              f"course")
        exercises.extend(exo_for_this_course)

    for exercise_file in test_exercise_files:
        exercise = exercise_from_pkl(exercise_file, None)
        if exercise.refined_auto_steps:
            log.debug(f"Adding {exercise.pretty_name}")
            exercises.append(exercise)
        else:
            log.warning(f"No auto_step found in {exercise.pretty_name}")

    return exercises


def get_exercises_from_course(course: Optional[Course],
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


############################
# Auto-testing an exercise #
############################

def find_selection(auto_step, emw):
    """
    Convert the data in auto_step.selection into MathObjects instances.
    This is used by the async auto_step function.
    """
    # TODO: deprecated

    auto_selection = []
    success = True
    # First trial
    # TODO: make emw properties
    #  and function find_selection(AutoStep, prop, obj)
    # properties = [item.mathobject
    #               for item in emw.ecw.props_wgt.items]
    # objects = [item.mathobject
    #            for item in emw.ecw.objects_wgt.items]
    # goal = emw.servint.proof_state.goals[0]
    for name in auto_step.selection:
        selection = None
        # Not clear to me why deaduction may not have
        # finished constructing goal, but this happens.
        # So we give it a few more seconds to complete the
        # construction.
        t = time.time() + 5
        while not selection and time.time() < t:
            if name.startswith('@O'):
                try:
                    selection = emw.objects[int(name[2:]) - 1]
                except IndexError:
                    pass
            elif name.startswith('@P'):
                try:
                    selection = emw.properties[int(name[2:]) - 1]
                except IndexError:
                    pass
            else:
                if name.startswith('@'):  # (unwanted @)
                    name = name[1:]
                selection = emw.current_goal.math_object_from_name(name)
            # if not selection:
            #     # Next trial
            #     properties = [item.mathobject for item in
            #                   emw.ecw.props_wgt.items]
            #     objects = [item.mathobject for item in
            #                emw.ecw.objects_wgt.items]
            #     goal = emw.servint.proof_state.goals[0]

        if selection:
            auto_selection.append(selection)
        else:
            log.debug("Bad selection in auto_step")
            success = False
            break

    return auto_selection, success


async def auto_test(container: Container):
    """
    Test the Exercise's instance container.exercise by listening to
    deaduction signals and simulating user pressing buttons according to
    the instructions found in exercise.auto_test. The function assumes that
    the ExerciseMainWindow has been launched.

    Note that just one exercise is tested, this function is not in charge of
    processing to the next exercise to be tested.
    """

    # Auto-steps loop
    exercise = container.exercise
    emw = container.exercise_window
    test_window = container.test_window
    auto_steps = exercise.refined_auto_steps

    log.info(f"Testing exercise {exercise.pretty_name}")

    test_window.display(f"Testing exercise {exercise.pretty_name}",
                        color='red')
    test_window.display('auto_steps:')
    total_string = 'AutoTest\n'
    for step in auto_steps:
        total_string += '    ' + step.raw_string + ',\n'
    test_window.display(total_string)

    signals = [emw.proof_step_updated,
               emw.ui_updated,
               test_window.process_next_step]
    test_success = True
    steps_counter = 0
    async with qtrio.enter_emissions_channel(signals=signals) as \
            emissions:
        reports = [f'Exercise {exercise.pretty_name}']
        container.report.append(reports)
        async for emission in emissions.channel:
            # Check result of previous proof step #
            if emission.is_from(emw.proof_step_updated) and steps_counter:
                step = auto_steps[steps_counter-1]
                report, step_success = emw.displayed_proof_step.compare(step)
                test_success = test_success and step_success
                if not report:
                    report = f'Success with {step.raw_string}'
                else:
                    report = f'{step.raw_string}' + report

                report = f"Step {steps_counter}: " + report
                if not emw.displayed_proof_step.success_msg \
                        and emw.displayed_proof_step.button \
                        and not emw.displayed_proof_step.button.is_cqfd() \
                        and not emw.displayed_proof_step.is_error():
                    report += "(no success msg)"
                reports.append(report)

            elif emission.is_from(emw.ui_updated):
                test_window.display("ui_updated received")

                step = auto_steps[steps_counter]
                steps_counter += 1
                test_window.display(f"Auto_step found: "
                                               f"{step.raw_string}")
                if not step:
                    test_window.display("    Found 'None' step, giving up")
                    emw.close()
                    break

                # selection_names = [item.display_name
                #                    for item in step.selection]
                # log.debug(f"    Selection: {selection_names}")
                step.user_input = [int(item) if item.isdecimal() else item
                                   for item in step.user_input]

                # For first step:
                await container.coordinator.server_task_running.wait()

                if not test_window.step_by_step:
                    test_window.process_next_step.emit()
                else:
                    test_window.next_step_button.setEnabled(True)

            elif emission.is_from(test_window.process_next_step):

                test_window.next_step_button.setEnabled(False)

                ################
                # Process step #
                ################

                success, msg = emw.simulate_user_action(step)

                if not success:
                    test_window.display("    Failing action:")
                test_window.display(msg)

                if steps_counter == len(auto_steps):
                    break
    test_window.display(f"Auto_test successfull: {test_success}")
    reports.insert(0, test_success)


#############
# Main loop #
#############

async def main():
    """
    Select exercises to be tested, launch ExerciseMainWindow and Lean
    server, and then call auto_test successively on each exercise. The
    exercise in initialized by the Container.test_exercise method.

    The loop first collect a collection of exercises from arguments.
    Arguments may include
    1) a directory,
    2) a file path to a course, maybe with with the name of some exercise,
    3) or a file path to an individual exercise in a pkl file.

    - In the first case, it will collect all exercises with autotest data in
    all courses in the directory, as well as all individual pkl
    test_exercises.
    - In the second case it will collect the individual exercise if
    specified, or all the exercises from this one, or all exercises in the
    specified course if no exercise is specified.
    - In the last case it will collect the specified exercise.
    """

    # ─────────────── Choose exercises ─────────────── #
    exercises = None
    dir_, course, exercise, all_from_this_one = coex_from_argv()
    # dir: Path
    # course : Course
    # exercise: Exercise
    # all_from_this_one: bool
    if dir_:
        exercises = get_exercises_from_dir(dir_)
    elif course:
        exercises = get_exercises_from_course(course, exercise,
                                              all_from_this_one)
    elif exercise:
        exercises = [exercise]

    if not exercises:
        quit()
    else:
        log.debug(f"Found {len(exercises)} with AutoTest metadata")

    # ─────────────── Testing exercises ─────────────── #
    async with trio.open_nursery() as nursery:
        # Create container and enter test mode
        container = Container(nursery)
        await container.check_lean_server()

        container.exercises = exercises

        # Start console
        test_window = QTestWindow()


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
                container.test_exercise(test_window)
                container.nursery.start_soon(auto_test, container)

                async for emission in emissions.channel:
                    if emission.is_from(container.test_complete) \
                            and container.exercises:  # Test next exercise
                        test_window.display("Test complete -> next exercise",
                                            color='red')
                        test_window.display(f"{len(container.exercises)} "
                                            f"exercises remaining to test")
                        # Close window
                        container.exercise_window.window_closed.disconnect()
                        container.exercise_window.close()
                        if container.exercises:
                            # Test next exercise
                            container.exercise = container.exercises[0]
                            container.exercises = container.exercises[1:]
                            container.test_exercise(test_window)
                            container.nursery.start_soon(auto_test, container)

                        else:
                            test_window.display("No more exercises to test!")
                            break

                    elif emission.is_from(container.close_exercise_window):
                        log.info("Exercise window closed")
                        break

        finally:
            test_window.display("============================================")
            global_success = False not in [exo_report[0] for
                                           exo_report in container.report]
            test_window.display(f"Global success : {global_success}")
            for exo_report in container.report:
                success = "success" if exo_report[0] else "FAILURE"
                if len(exo_report) > 1:
                    test_window.display(exo_report[1] + ": " + success)
                    for step_report in exo_report[2:]:
                        test_window.display(step_report)

            print(test_window.txt)

            # Finally closing d∃∀duction
            if container.servint:
                await container.servint.file_invalidated.wait()
                container.servint.stop()  # Good job, buddy
                log.info("Lean server stopped!")
            if container.nursery:
                container.nursery.cancel_scope.cancel()

if __name__ == '__main__':
    log.info("Starting autotest...")

    cenv.init()
    cdirs.init()
    inst.init()

    qtrio.run(main)
    log.debug("qtrio finished")
