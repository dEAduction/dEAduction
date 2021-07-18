"""
##################################################################
# __main__.py : pre-process all statements of a lean course file #
##################################################################

Allow the user to choose a lean file, and pre-process all statements,
sending them to Lean one by one to get their initial proof_state.
Each initial proof state is stored in the statement.initial_proof_state
attribute.

The resulting course is stored in a '.pkl' file in the same directory

If the corresponding '.pkl' file already exists, then
- if the file_content was different, just erase the '.pkl' file
- if not, read the stored course and keep the initial proof_states
that are already stored there.

Every 5 processed statements, Lean server is stopped and started again.
This prevents the Lean server from crashing because of messages of length
> 65535. The resulting course with partial pre-processing is also stored,
to take into account the possibility of a crash.

In practice, the software seldom succeeds in processing the whole content.
As said before, however, the statements that have already been processed are
still accessible. So in case of a crash, just run the soft again, and be
patient...

Finally the programme prints all statements, so this can also be used to get
the list of all statements in a given Lean (or pkl) course file.

Author(s)      : - Frédéric Le Roux <frederic.le_roux@imj-prg.fr>

Maintainers(s) : - Frédéric Le Roux <frederic.le_roux@imj-prg.fr>

Date           : September 2020

Copyright (c) 2020 the dEAduction team

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
# TODO: change the data to avoid saving the whole contents every 5 statements.

from sys import argv
from typing import Optional
import logging
import qtrio
import trio
import pickle5 as pickle
import argparse
from pathlib import Path
from PySide2.QtWidgets import QFileDialog


import deaduction.pylib.config.dirs              as     cdirs
import deaduction.pylib.config.environ           as     cenv
import deaduction.pylib.config.site_installation as     inst
import deaduction.pylib.config.vars              as     cvars

# from deaduction.pylib.config.i18n import _
from deaduction.pylib.coursedata import (Course,
                                         Exercise,
                                         Definition,
                                         Theorem)
from deaduction.pylib import logger
from deaduction.pylib.server import ServerInterface
from deaduction.pylib.pre_processing import ServerInterfaceAllStatements


log = logging.getLogger(__name__)

arg_parser = argparse.ArgumentParser("Start deaduction pre-processing to "
                                     "turn '.lean' files into '.pkl'")
arg_parser.add_argument('--directory', '-d', help="Path for directory")
arg_parser.add_argument('--course', '-c', help="Course filename")

def check_statements(course):
    """
    Check every statement of course for initial_proof_state attribute

    :param course: Course

    :return:    1) a Course instance, with some preprocessed statement
            (if a pkl file have been found with the good file content)
                2) list of statements without initial_proof_state attribute
                3) path for pkl version of the course (whether the file exists
                or not)
    """
    # get course_path relative to cwd
    # (cwd is set be src/deaduction by config.py)
    relative_course_path = course.relative_course_path
    directory_name = relative_course_path.parent
    course_hash = hash(course.file_content)

    # search for pkl file, and compare contents
    # so that only unprocessed statements will be processed
    unprocessed_statements = []
    filename = relative_course_path.stem + '.pkl'
    course_pkl_path = directory_name.joinpath(Path(filename))
    log.debug(f"Checking for {course_pkl_path}")
    if course_pkl_path.exists():
        [stored_course] = pickled_items(course_pkl_path)
        stored_hash = hash(stored_course.file_content)
        log.debug(f"Found '.pkl' file, hash = {stored_hash} vs {course_hash}")
        if stored_hash == course_hash:
            # log.info("pkl content file is up to date")
            # we want the statements already processed to be conserved:
            course = stored_course
            for statement in course.statements:
                name = statement.pretty_name
                if hasattr(statement, 'initial_proof_state') \
                        and statement.initial_proof_state is not None:
                    log.info(f"found initial_proof_state for {name}")
                else:
                    unprocessed_statements.append(statement)
                    log.info(f"NO initial_proof_state for {name}")
        else:
            log.info(f"pkl content file is NOT up to date: "
                     f"course hash ={course_hash}")
            unprocessed_statements = course.statements
    else:
        log.debug("File '.pkl' does not exist")
        unprocessed_statements = course.statements
    return course, unprocessed_statements, course_pkl_path


async def get_all_proof_states(servint,
                               course,
                               statements_to_process,
                               course_pkl_path):
    """
    for each statement to process,
        initialize servint with the statement,
        get initial proof_state,
        store it as a statement attribute
    Save the course in the course_pkl_path every 5 statements
    """
    counter = 0
    for statement in statements_to_process:
        counter += 1
        await servint.set_exercise(statement)
        # proof_state is now stored as servint.proof_state
        log.info(f"Got proof state of statement "
                 f"{statement.pretty_name}, n"
                 f"°{counter}")
        statement.initial_proof_state = servint.proof_state

        # stop and restart server every 5 exercises to avoid
        # too long messages that entail crashing
        if (counter % 100) == 0:
            # servint.stop()
            log.info("Saving temporary file...")
            save_objects([course], course_pkl_path)
            # await servint.start()
            # await servint.exercise_set(statement)
            # # proof_state is now stored as servint.proof_state
            # log.info(f"Got proof state of statement "
            #          f"{statement.pretty_name}, n"
            #          f"°{counter}")
            # statement.initial_proof_state = servint.proof_state


def save_objects(objects: list, filename):
    with filename.open(mode='wb') as output:  # Overwrites any existing file
        for obj in objects:
            pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def pickled_items(filename):
    """ Unpickle a file of pickled data. """
    with filename.open(mode="rb") as input:
        while True:
            try:
                yield pickle.load(input)
            except EOFError:
                break


def read_data(filename):
    print("Reading file:")
    [stored_course] = pickled_items(filename)

    # print("Text version ? (t)")
    # answer = input()
    # if answer == 't':
    #     print_text_version(stored_course)
    # else:
    #     print_goal(stored_course)
    print_goal(stored_course)


def print_text_version(course):
    counter = 0
    for st in course.statements:
        print("-------------------------")
        if isinstance(st, Exercise):
            counter += 1
            print(_("Exercise") + f" n°{counter}: {st.pretty_name}")
            goal = st.initial_proof_state.goals[0]
            if 'open_question' in st.info:
                open_problem = True
            else:
                open_problem = False
            print(goal.goal_to_text(text_depth=1, open_problem=open_problem))
            # print("     More verbose:")
            # print(goal.goal_to_text(text_depth=2))
        else:
            print(_("Definition:") + f" {st.pretty_name}")
            goal = st.initial_proof_state.goals[0]
            print(goal.goal_to_text(to_prove=False, text_depth=1))


def print_goal(course):
    counter = 0
    to_prove = False
    for st in course.statements:
        print("-------------------------")
        if isinstance(st, Exercise):
            counter += 1
            print(_("Exercise") + f" n°{counter}: {st.pretty_name}")
            to_prove = True
        elif isinstance(st, Definition):
                print(_("Definition:") + f" {st.pretty_name}")
                to_prove = False
        elif isinstance(st, Theorem):
                print(_("Theorem:") + f" {st.pretty_name}")
                to_prove = False

        if 'open_question' in st.info:
            open_problem = True
        else:
            open_problem = False
        goal = st.initial_proof_state.goals[0]
        print(goal.goal_to_text(format_='utf8',
                                to_prove=to_prove,
                                text_depth=5,
                                open_problem=open_problem))


def get_courses_from_dir(dir_path: Path):
    lean_files = [file for file in dir_path.iterdir()
                  if file.suffix == '.lean']
    log.info(f"looking for deaduction-Lean files in {dir_path.name}")
    log.info(f" found {len(lean_files)} files")

    courses = [select_course(file) for file in lean_files]
    return courses


def select_course(course_path=None) -> Course:
    """
    Select a course from a Path, a path string, or by opening a QFileDialog.
    :param course_path: a Path, a string, or None.
    :return: a instance of Course.
    """

    course = None
    if not course_path:
        course_path, ok = QFileDialog.getOpenFileName()
        if not ok:
            quit()
    if isinstance(course_path, str):
        if not course_path.endswith('.lean') \
        and not course_path.endswith('.pkl'):
            course_path += '.lean'
        course_path = Path(course_path)

    course_path_str = str(course_path.resolve())
    log.info(f'Selected course: {course_path_str}')

    extension = course_path.suffix
    # case of a standard Lean file
    if extension == '.lean':
        course = Course.from_file(course_path)
    # case of a pre-processed .pkl file
    elif extension == '.pkl':
        [course] = pickled_items(course_path)
    else:
        log.error("Wrong file format")

    return course


def coex_from_argv() -> (Optional[Path], Course, Exercise, bool):
    """
    Try to build Course and Exercise object from arguments.
    """
    course = None

    args = arg_parser.parse_args(argv[1:])
    dir_path = args.directory
    course_path = args.course

    if dir_path:
        dir_path = Path(dir_path)
        return dir_path, None
    elif course_path:
        course = select_course(course_path)

    return None, course


async def main():
    """
    See file doc.
    """

    cenv.init()
    cdirs.init()
    inst.init()

    #############################################
    # Search course or directory from arguments #
    #############################################
    dir_, course = coex_from_argv()
    if dir_:
        courses = get_courses_from_dir(dir_)
    elif course:
        courses = [course]
    else:
        course = select_course()
        courses = [course]

    # Process each course
    for course in courses:
        # Check for pkl file and, if it exists, find all unprocessed statements
        course, unprocessed_statements, course_pkl_path \
            = check_statements(course)

        if not unprocessed_statements:
            log.info("pkl fle is up_to_date with all initial_proof_states")
            # Checking
            read_data(course_pkl_path)
            continue
        else:
            log.info(f"Still {len(unprocessed_statements)} "
                     f"statements to process")

        # confirm before processing file
        print("Processing? (y/n)")
        answer = input()
        if answer == 'y':
            pass
        else:
            print('Quitting')
            return

        #########################
        # Init and start server #
        #########################
        async with trio.open_nursery() as nursery:
            servint = ServerInterface(nursery)
            await servint.start()
            try:
                log.info("Pre-processing course...")
                await get_all_proof_states(servint,
                                           course,
                                           unprocessed_statements,
                                           course_pkl_path
                                           )
            except UnicodeDecodeError:
                log.error("UnicodeDecodeError")
            finally:
                servint.stop()  # Good job, buddy
                save_objects([course], course_pkl_path)

            # Checking
            read_data(course_pkl_path)


async def main_alt():
    """
    See file doc.
    """

    cenv.init()
    cdirs.init()
    inst.init()

    #############################################
    # Search course or directory from arguments #
    #############################################
    dir_, course = coex_from_argv()
    if dir_:
        courses = get_courses_from_dir(dir_)
    elif course:
        courses = [course]
    else:
        course = select_course()
        courses = [course]

    # Process each course
    for course in courses:
        async with trio.open_nursery() as nursery:
            servint = ServerInterfaceAllStatements(nursery)
            await servint.start()
            await servint.set_statements(course)
            servint.stop()

        log.debug("Got all proof states, saving")
        # Save pkl course file
        relative_course_path = course.relative_course_path
        directory_name = relative_course_path.parent
        course_hash = hash(course.file_content)

        # search for pkl file, and compare contents
        # so that only unprocessed statements will be processed
        unprocessed_statements = []
        filename = relative_course_path.stem + '.pkl'
        course_pkl_path = directory_name.joinpath(Path(filename))

        save_objects([course], course_pkl_path)

        print("===================================")
        print_goal(course)


if __name__ == '__main__':
    logger.configure(domains=['ServerInterface', '__main__'])
    log.debug("starting pre-processing...")
    qtrio.run(main_alt)

