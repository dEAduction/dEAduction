"""
############################################################
# special_actions.py                                       #
############################################################

Author(s)     : - Frédéric Le Roux
Maintainer(s) : - Frédéric Le Roux <frederic.le-rxou@imj-prg.fr>
Created       : August 2022 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2022 the dEAduction team

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

import logging
from typing import Union, Optional

from deaduction.pylib.math_display.display_data import new_objects

from deaduction.pylib.actions     import (action,
                                          WrongUserInput,
                                          CodeForLean)

from deaduction.pylib.mathobj     import (ContextMathObject)

log = logging.getLogger("logic")

global _


def drag_n_drop(premise: ContextMathObject, operator: ContextMathObject,
                button_names: [str] = None) -> str:
    """
    Compute an action to be triggered from a drag and drop operation.
    @param premise: the dragged property or object.
    @param operator: the receiver property or object.
    @return: nams of the action to be triggered.
    """
    if not operator:  #
        raise WrongUserInput(_("Drop on some object or property!"))
    elif not premise:  # This should not happen...
        raise WrongUserInput(_("Drag and drop failed, please try again."))
    # log.debug(f"Selection len: {len(selection)}")
    # log.debug(f"Operator: {operator.math_type_to_display(format_='utf8')}")

    # The main premise determines the action. It is the last selected
    # property if any, else the last selected object.
    # # FIXME: beware that selection maybe not ordered by time of selection?
    # if not selection:
    #     raise WrongUserInput(_("I don't know what to do!"))
    #
    # premise = selection[-1]
    # for math_obj in selection:
    #     if math_obj.is_prop():
    #         premise = math_obj
    # log.debug(f"Premise: {premise}")
    names = operator.action_from_premise_and_operator(premise, button_names)
    log.debug(f"Name: {names}")

    if not names:
        raise WrongUserInput(_("I don't know what to do!"))

    return names
