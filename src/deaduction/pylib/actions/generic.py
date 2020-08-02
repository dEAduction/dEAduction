"""
# generic.py : # Contain actions the graphic interface has to call #
# when the user selects a definition or a theorem                  #
    
    (#optionalLongDescription)

Author(s)     : Marguerite Bin bin.marguerite@gmail.com
Maintainer(s) : Marguerite Bin bin.marguerite@gmail.com
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

from dataclasses import dataclass
from gettext import gettext as _
import logging
from deaduction.pylib.actions import (  WrongUserInput,
                                        get_new_hyp)
from deaduction.pylib.coursedata import Statement
from deaduction.pylib.mathobj import (  Goal,
                                        PropObj)

def action_definition(goal : Goal, selected_objects : [PropObj], definition : Statement):
    if len(selected_objects) == 0:
        defi = definition.lean_name
        return "defi {0} <|> simp_rw {0} <|> simp_rw <- {0}".format(defi)
    elif len(selected_objects) == 1:
        defi = definition.lean_name
        return "defi {0} at {1} <|> simp_rw {0} at {1} <|> simp_rw <- {0} at {1}".format(defi,
                                        selected_objects[0].lean_data["name"])
    else:
        raise WrongUserInput

def action_theorem(goal : Goal, selected_objects : [PropObj], theorem : Statement):
    th = theorem.lean_name
    if len(selected_objects) == 0:
        h = get_new_hyp()
        return "apply {1} <|> have {0} := @{1},".format(h, th)
    else:
        arguments = " ".join([selected_objects[0].lean_data["name"]])
        arguments_type = " "
        h = get_new_hyp()
        return "apply {1} {2} <|> apply @{1} {2} <|> have {0} := {1} {2} <|> have {0} := @{1} {2},".format(h, th, arguments)
