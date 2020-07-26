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

from snippets.server.ServerInterface import *
import deaduction.pylib.logger as logger
from deaduction.pylib.coursedata.course import Course
from deaduction.pylib.mathobj.PropObj import ProofStatePO



def  print_goal(goal):
    i = 0
    print("Current context:")
    for mt in goal.math_types:
        print(f"{[PO.format_as_utf8() for PO in goal.math_types_instances[i]]} : {mt.format_as_utf8()}")
        i += 1
    print("Current goal:")
    print(goal.target.math_type.format_as_utf8())

async def main():
    logger.configure()
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
            print(f"Statement n°{counter}: "
                  f"({isinstance(statement, Exercise)}) "
                  f"{statement.pretty_name}")
            counter += 1

        ############
        # exercise #
        ############
        # num_ex = input("exercise n° ?")
        num_ex = 8
        my_exercise = my_course.statements[num_ex]
        begin_line = my_exercise.lean_begin_line_number
        end_line =  my_exercise.lean_end_line_number
        my_server.hypo_counter = 0
        my_server.goals_counter = 0

        file_content = my_course.file_content
        lines = file_content.splitlines()

        virtual_file_preamble = "\n".join(lines[:begin_line]) + "\n"
#        virtual_file_afterword = "  hypo_analysis,\n" \
#                                 + "  goals_analysis,\n" \
#                                 + "end"
        virtual_file_afterword = "  hypo_analysis,\n" \
                                 + "  goals_analysis,\n" \
                                 + "\n".join(lines[end_line-1:])
        txt = virtual_file_preamble + virtual_file_afterword
        my_server.log.debug("Sending file:" + txt)
        line = begin_line + 1
        my_server.lean_file = LeanFile(file_name='lean file', init_txt=txt)
        my_server.lean_file.cursor_move_to(line)
        my_server.lean_file.cursor_save()
        await my_server.__update()
        #####################
        # print proof state #
        #####################
        print("Proof State:")
        ins = ""
        while ins not in ["stop", "quit", "exit"]:
            ins = input("waiting for Lean, hit ENTER")
            try:
                goal = my_server.proof_state.goals[0]
                break
            except AttributeError:
                my_server.log.warning("AttributeError")
        print_goal(goal)

        ####################
        # next instruction #
        ####################
        code = ""
        while code != "sorry":
            code = input("Lean next instruction?")
            code += f"\n"
            print("Sending to Lean server")
            await my_server.code_insert(label=f"step n°{counter}", code=code)
            ins = ""
            while ins not in ["stop", "quit", "exit"]:
                ins = input("waiting for Lean, hit ENTER")
                try:
                    goal = my_server.proof_state.goals[0]
                    break
                except AttributeError:
                    my_server.log.warning("AttributeError")
            print_goal(goal)
            print("New Proof State:")
            goal = my_server.proof_state.goals[0]
            print_goal(goal)
        my_server.stop()
        await my_server.lean_server.exited.wait()


trio.run(main)
