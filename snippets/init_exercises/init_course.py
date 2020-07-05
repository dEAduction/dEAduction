"""
# init_course.py : #ShortDescription #
    
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

import dataclasses
from pathlib import Path


@dataclasses
class Exercise:
    title: str
    text_description: str
    line_in_lean_file: int
    lean_statement: str
    latex_statement: str  # complete statement using text and latex expressions TODO
    logic_buttons_list: list
    statement_buttons_list: list
    magic_buttons_list: list
    expected_number_var: dict # expected number of variables of each mathematical type





@dataclasses
class Course:
    exercises_list: list[Exercise]
    definitions_list: list
    # logic_buttons_list
    # definition_buttons_list




    @classmethod
    def course_from_lean_file(clsself, exercises_path, files_list, definitions_path, definitions_files_list):
        exercises_list = []
        definitions_list = []
        path = exercises_path / file
        with open(path, mode = 'r') as lean_course_file:


        # TODO : extraire les listes
        Exercise = False
        line = "" ##
        # lire ligne par ligne
        if line.startwith("@dEAductionExercise"):
            exercise = True
            title = None
            text_description = None
            line_in_lean_file = None
            lean_statement = None
            latex_statement = None
            logic_buttons_list = None
            statement_buttons_list = None
            magic_buttons_list = None
            expected_number_var = None

        if exercise and line.startwith("@TextDescription"):
            pass

        if exercise and line.startwith("@LogicButtons"):
            pass

        if exercise and line.startwith("@DefiButtons"):
            pass
        if exercise and line.startwith("@ThmButtons"):
            pass

        if exercise and line.startwith("@ExpectedVars"):
            pass



        exercise = Exercise()

        return clsself(exercises_list, definitions_list)





if __name__ == '__main__':
    exercises_path = Path('.')
    file = 'exercises_theorie_des_ensembles.lean'
    my_course = Course.course_from_lean_file(exercises_path, file)








