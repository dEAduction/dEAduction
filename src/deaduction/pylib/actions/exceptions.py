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
import deaduction.pylib.config.vars as cvars

global _


class InputType(IntEnum):
    """
    Class clarifying second argument of output of functions action_*
    """
    Text = 0
    Choice = 1
    YesNo = 2
    Calculator = 3


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


class WrongProveModeInput(WrongUserInput):
    def __init__(self, error="", prop=None):
        super().__init__(f"Wrong 'prove' user input with error: {error}")
        if not prop:
            prop = _("a property")
        if not error:
            if cvars.get("logic.button_use_or_prove_mode") == "display_switch":
                error = _("Go into 'use mode' to make use of {} of "
                          "the context").format(prop)
            else:
                error = _("Press the 'use' button to make use of {} of "
                          "the context").format(prop)
        self.message = error


class WrongUseModeInput(WrongUserInput):
    def __init__(self, error="", prop=None):
        super().__init__(f"Wrong 'use' user input with error: {error}")
        if not prop:
            prop = _("the goal")
        if not error:
            if cvars.get("logic.button_use_or_prove_mode") == "display_switch":
                error = _("Go into 'prove mode' to prove {}").format(prop)
            else:
                error = _("Press the 'prove' button to prove {}").format(prop)
        self.message = error


def test_selection(items_selected: [],
                   selected_target: bool,
                   exclusive=False):
    """
    Test that at least one of items_selected or selected_target is not empty.
    If exclusive is True, then also test that both are not simultaneously
    nonempty.
    """
    implicit_target = cvars.get("functionality.target_selected_by_default")

    if not (items_selected or selected_target or implicit_target):
        error = _("Select at least one object, one property or the target")
        raise WrongUserInput(error)

    if exclusive and items_selected and selected_target:
        error = _("I do not know what to do with this selection")
        raise WrongUserInput(error)


def test_prove_use(selected_objects, demo, use, prop):
    """
    Raise an exception if nb of selected_objects does not fit use/demo mode.
    @param selected_objects:
    @param demo: True iff demo mode is on
    @param use: True iff use mode is on
    @param prop: the type of property
    """
    if not selected_objects and not demo:
        raise WrongUseModeInput(prop=prop)
    elif selected_objects and not use:
        raise WrongProveModeInput(prop=prop)


