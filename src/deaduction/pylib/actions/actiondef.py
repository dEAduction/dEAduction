"""
############################################################
# actiondef.py : defines class Action                      #
############################################################


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


import deaduction.pylib.logger as logger
import logging
import inspect
from dataclasses import dataclass

@dataclass
class Action:
    """
    Associates data to a specific action function.
    """
    caption:str
    run:any

def action(caption: str):
    """
    Decorator used to reference the function as an available action,
    plus creating the Action object containing the metadata.
    """
    # Get caller module object.
    # See https://stackoverflow.com/questions/1095543/get-name-of-calling-functions-module-in-python
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])

    def wrap_action(func):
        act = Action(caption,func)
        
        # Init the __actions__ object in the corresponding module if not
        # existing, then add the function object. Identifier is taken from
        # the function name.
        if not "__actions__" in mod.__dict__: mod.__actions__ = dict()
        mod.__actions__[func.__name__] = act

        return func

    return wrap_action 
