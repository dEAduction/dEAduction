"""
##################################################################
# __main__.py : pre-process all statements of a lean course file #
##################################################################

Allow the user to choose a lean file, and pre-process all statements,
sending them to Lean one by one to get their initial proof_state.
The resulting course is stored in a '.pkl' file in the same directory
If the corresponding '.pkl' file already exists, then
- if the file_content was different, just erase the '.pkl' file
- if not, read the stored course and keep the initial proof_states
that are already stored there.

Every 5 processed statements, Lean server is stopped and started again.
This prevents the Lean serve from crashing because of messages of length
> 65535. The resulting course with partial pre-processing is also stored,
to take into account the possibility of a crash.

TODO: change the data to avoid saving the whole contents every 5 statements.

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

import logging
import qtrio
import trio
import gettext
import pickle
from pathlib import Path

from deaduction.dui.launcher import select_course
from deaduction.pylib.coursedata import Exercise
from deaduction.pylib import logger
from deaduction.pylib.server import ServerInterface

log = logging.getLogger(__name__)


async def main():
    """
    See file doc
    """
    # Choose course and parse it
    course = select_course()
    # check for pkl file and, if it exists, find all unprocessed statements
    course, unprocessed_statements, course_pkl_path = check_statements(course)

    if not unprocessed_statements:
        log.info("pkl fle is up_to_date with all initial_proof_states")
        # Checking
        read_data(course_pkl_path)
        return
    else:
        log.info(f"Still {len(unprocessed_statements)} statements to process")

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
        finally:
            servint.stop()  # Good job, buddy
            save_objects([course], course_pkl_path)

        # Checking
        read_data(course_pkl_path)


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
    course_path = course.course_path
    directory_name = course_path.parent
    course_hash = hash(course.file_content)

    # search for pkl file, and compare contents
    # so that only unprocessed statements will be processed
    unprocessed_statements = []
    filename = course_path.stem + '.pkl'
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
        await servint.exercise_set(statement)
        # proof_state is now stored as servint.proof_state
        log.info(f"Got proof state of statement "
                 f"{statement.pretty_name}, n"
                 f"°{counter}")
        statement.initial_proof_state = servint.proof_state

        # stop and restart server every 5 exercises to avoid
        # too long messages that entail crashing
        if counter % 5 == 0:
            servint.stop()
            log.info("Saving temporary file...")
            save_objects([course], course_pkl_path)
            await servint.start()


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

    print("Text version ? (t)")
    answer = input()
    if answer == 't':
        print_text_version(stored_course)
    else:
        print_goal(stored_course)


def print_text_version(course):
    counter = 0
    for st in course.statements:
        print("-------------------------")
        if isinstance(st, Exercise):
            counter += 1
            print(_("Exercise") + f" n°{counter}: {st.pretty_name}")
            goal = st.initial_proof_state.goals[0]
            print(goal.goal_to_text(text_depth=1))
            # print("     More verbose:")
            # print(goal.goal_to_text(text_depth=2))
        else:
            print(_("Definition:") + f" {st.pretty_name}")
            goal = st.initial_proof_state.goals[0]
            print(goal.goal_to_text(to_prove=False, text_depth=1))


def print_goal(course):
    counter = 0
    for st in course.statements:
        print("-------------------------")
        if isinstance(st, Exercise):
            counter += 1
            print(_("Exercise") + f" n°{counter}: {st.pretty_name}")
        else:
            print(_("Definition:") + f" {st.pretty_name}")

        goal = st.initial_proof_state.goals[0]
        print(goal.print_goal())


if __name__ == '__main__':
    logger.configure(debug=True,
                     domains="pre_processing",
                     suppress=False)
    _ = gettext.gettext
    log.debug("starting pre-processing...")
    qtrio.run(main)

