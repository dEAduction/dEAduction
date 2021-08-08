"""
###########################################################
# actiondef.py : define class Action                      #
###########################################################

Thanks to the action decorator, a dictionary of all action functions is
build. Then a button is created for each function.

To add a new action function:
    - create the function in action/logic or magic or proofs
    - add a tooltip in pylib/text/tooltips, and (for a logic button)
    the name in the logic_buttons list, and a default symbol in config.toml

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

import inspect
from deaduction.pylib.text import button_symbol


class Action:
    """
    A class to store action functions.
    self.run is the function.
    """
    run: any

    def __init__(self, func):
        self.run       = func

    @property
    def symbol(self):
        """
        "Symbol" of the action, to be put on the button
        (e.g. action_forall --> ∀)
        This is the basic symbol, the actual symbol may be changed by user
        (cf config.toml).
        """
        return button_symbol(self.name)

    @property
    def name(self):
        """
        e.g. function action_and --> name = "and"
        """
        func_name = self.run.__name__
        # Remove the "action_" part
        name = func_name[len("action_"):]
        return name


def action():
    """
    Decorator used to reference the function as an available action
    plus creating the Action object containing the metadata
    and storing it in the dict mod.__actions__ as a value.
    """
    # Get caller module object.
    # Allows to have access / create to the dict __actions__ of the
    # current module.
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])

    def wrap_action(func):
        act = Action(func)

        # Init the __actions__ object in the corresponding module if not
        # existing, then add the Action object.
        # Identifier is taken from the function name.
        if "__actions__" not in mod.__dict__:
            mod.__actions__ = dict()
        mod.__actions__[func.__name__] = act

        return func

    return wrap_action
