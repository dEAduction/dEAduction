"""
# essai_server.py : #ShortDescription #
    
    (#optionalLongDescription)

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
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

import trio
import logging
import sys

from pathlib import Path

#from snippets.server.ServerInterface import *
import deaduction.pylib.logger as logger
from deaduction.pylib.coursedata.course import Course
from deaduction.pylib.coursedata.exercise_classes import Exercise
from deaduction.pylib.mathobj.PropObj import ProofStatePO

from deaduction.pylib.server import ServerInterface


def  print_goal_by_type(goal):
    i = 0
    print("Current context:")
    for mt in goal.math_types:
        print(f"{[PO.format_as_utf8() for PO in goal.math_types_instances[i]]} : {mt.format_as_utf8()}")
        i += 1
    print("Current goal:")
    print(goal.target.math_type.format_as_utf8())

def print_objects_and_proposition(objects, propositions):
    """
    :param objects: list of tuples (pfPO, tag)
    :param propositions: list of tuples (pfPO, tag)
    where tag = "=", "≠", "+"
    """
    print("Current context")
    print("  Objects:")
    for (pfPO, tag) in objects:
        print(f"{tag} {pfPO.format_as_utf8()} : "
              f"{pfPO.math_type.format_as_utf8()}")
    print("  Propositions:")
    for (pfPO, tag) in propositions:
        print(f"{tag} {pfPO.format_as_utf8()} : "
              f"{pfPO.math_type.format_as_utf8()}")

async def main():
#    logger.configure()
    async with trio.open_nursery() as nursery:
        my_server = ServerInterface(nursery)
        my_server.log = logging.getLogger("ServerInterface")

        await my_server.start()

        ##########
        # course #
        ##########
        course_file_path = Path(
            '../../tests/lean_files/short_course'
            '/exercises.lean')
        my_course = Course.from_file(course_file_path)
        counter = 0
        for statement in my_course.statements:
            print(f"Statement n°{counter:2d}: "
                  f"(exercise: {isinstance(statement, Exercise)}) "
                  f"{statement.lean_name}"
                  f" ({statement.pretty_name})")
            counter += 1

        ############
        # exercise #
        ############
        num_ex = int(input("exercise n° ?"))
        #num_ex = 10
        my_exercise = my_course.statements[num_ex]
        begin_line  = my_exercise.lean_begin_line_number
        end_line    =  my_exercise.lean_end_line_number

        print(f"begin_line={begin_line} ; end_line={end_line}")
        #file_content = my_course.file_content
        #lines = file_content.splitlines()

        #virtual_file_preamble = "\n".join(lines[:begin_line]) + "\n"
#       # virtual_file_afterword = "  hypo_analysis,\n" \
#       #                          + "  targets_analysis,\n" \
#       #                          + "end"
        #virtual_file_afterword = "  hypo_analysis,\n" \
        #                         + "  targets_analysis,\n" \
        #                         + "\n".join(lines[end_line-1:])
        #txt = virtual_file_preamble + virtual_file_afterword
        #my_server.log.debug("Sending file:" + txt)
        #line = begin_line + 1
        #my_server.lean_file = LeanFile(file_name='lean file', init_txt=txt)
        #my_server.lean_file.cursor_move_to(line)
        #my_server.lean_file.cursor_save()

        #await my_server.__update()

        await my_server.exercise_set(my_exercise)

        #####################
        # print proof state #
        #####################
        print("Proof State:")
<<<<<<< HEAD
        #ins = ""
        #while ins not in ["stop", "quit", "exit"]:
        #    ins = input("waiting for Lean, hit ENTER")
        #    try:
        #        goal = my_server.proof_state.goals[0]
        #        break
        #    except AttributeError:
        #        my_server.log.warning("AttributeError")

        goal = my_server.proof_state.goals[0]
        print_goal(goal)
=======
        ins = ""
        while ins not in ["stop", "quit", "exit"]:
            ins = input("waiting for Lean, hit ENTER")
            try:
                new_goal = my_server.proof_state.goals[0]
                break
            except AttributeError:
                my_server.log.warning("AttributeError")
        print_goal_by_type(new_goal)
>>>>>>> 418ab4428cbc3483a5cc7da2bc3a69d46e9076e6

        ####################
        # next instruction #
        ####################
        code = ""
<<<<<<< HEAD
        while code != "sorry\n":
            code = input("Lean next instruction ?")
            if code == "undo":
=======
        while code != "sorry,\n":
            code = input("Lean next instruction?")
            if code.startswith("undo"):
>>>>>>> 418ab4428cbc3483a5cc7da2bc3a69d46e9076e6
                await my_server.history_undo()
            elif code.startswith("redo"):
                await my_server.history_redo()
            elif code == "contents":
                print(my_server.lean_file.contents)
            else:
                if not code.endswith(','):
                    code += ','
                code += f"\n"
                print(f"Sending code {code} to Lean server")
                await my_server.code_insert(label=f"step n°{counter}", code=code)
            ins = ""
            # while ins not in ["stop", "quit", "exit"]:
            #     ins = input("waiting for Lean, hit ENTER")
            #     try:
            #         goal = my_server.proof_state.goals[0]
            #         break
            #     except AttributeError:
            #         my_server.log.warning("AttributeError")
            old_goal = new_goal
            print("New Proof State:")
            new_goal = my_server.proof_state.goals[0]
            new_goal.compare(old_goal, goal_is_new=False)
            objects, propositions = new_goal.tag_and_split_propositions_objects()
            print_objects_and_proposition(objects,propositions)
            print("Current target:")
            print(new_goal.target.math_type.format_as_utf8())
        my_server.stop()
        await my_server.lean_server.exited.wait()

trio.run(main)
