"""
############################################################
# exceptions.py : functions to call in order to            #
# translate actions into lean code                         #
############################################################
    
Every function action_* takes 2 arguments,
- goal (of class Goal)
- a list of ProofStatePO precedently selected by the user
and returns lean code as a string

Author(s)     : - Marguerite Bin <bin.marguerite@gmail.com>
Maintainer(s) : - Marguerite Bin <bin.marguerite@gmail.com>
Created       : July 2020 (creation)
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

from enum                         import IntEnum

# from deaduction.pylib.config.i18n import _


class InputType(IntEnum):
    """
    Class clarifying second argument of output of functions action_*
    """
    Text = 0
    Choice = 1


class MissingParametersError(Exception):
    def __init__(self, input_type, choices=None, title="", output=""):
        self.input_type         = input_type
        self.choices            = choices
        self.title              = title
        self.output             = output


class WrongUserInput(Exception):
    def __init__(self, error=""):
        super().__init__(f"Wrong user input with error: {error}")
        self.message = error


def test_selection(items_selected,
                   selected_target):
    """
    Test that at least one of items_selected or selected_target is not empty.
    """
    if not (items_selected or selected_target):
        error = _("select at least one object, one property or the target")
        raise WrongUserInput(error)