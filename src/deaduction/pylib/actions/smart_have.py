"""
############################################################
# smart_have.py : smart version of have_new_property       #
############################################################

Author(s)     : - Frédéric Le Roux <frederic.le-rxou@imj-prg.fr>
Maintainer(s) : - Frédéric Le Roux <frederic.le-rxou@imj-prg.fr>
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

import logging
from typing import Union, Optional

from deaduction.pylib.math_display.display_data import new_objects

from deaduction.pylib.actions import (action,
                                      InputType,
                                      MissingParametersError,
                                      WrongUserInput,
                                      test_selection,
                                      CodeForLean,
                                      action_definition
                                      )

from deaduction.pylib.mathobj import (MathObject,
                                      PatternMathObject,
                                      mvars_assign,
                                      mvars_assign_some,
                                      first_unassigned_mvar,
                                      give_global_name,
                                      names_for_types,
                                      get_new_hyp)

log = logging.getLogger("logic")
global _


def to_code_names(assigned_mvars):
    """
    Return list of code names for mvars:
    the display_name of those mvars that have been explicitly assigned,
    and "_" for the other ones.
    """

    # Check all mvars assigned
    assert first_unassigned_mvar(assigned_mvars) is None

    code_names = [mvar.children[0].display_name if mvar.is_explicitly_assigned()
                  else "_" for mvar in assigned_mvars]
    return code_names


def smart_have(arrow: MathObject,
               selected_objects,
               context,
               new_hypo_name: str,
               explicit=False) -> CodeForLean:
    """
    Compute Lean code to apply an implication or a universal property to a
    property and/or some local constant. But contrary to the function
    have_new_property, which is quite dumb, here we try to guess the position of
    each selected object, and even to add other context objects if needed.
    """

    selected_hypo = "@" + arrow.info['name'] if explicit else arrow.info['name']

    codes = []
    command = f'have {new_hypo_name} := {selected_hypo}'

    mvars = []
    pattern = PatternMathObject.from_universal_prop(arrow, mvars)

    # DEBUG:
    print("Pattern:")
    print("    ", pattern.to_display(format_="utf8"))
    print("mvars:", [mvar.to_display(format_="utf8") for mvar in mvars])
    print("mvars types:", [mvar.math_type.to_display(format_="utf8") for mvar
                           in mvars])

    assigned_mvars_list = mvars_assign(mvars, selected_objects)

    for mvars in assigned_mvars_list:
        # Remove last unassigned:
        while not mvars[-1].is_explicitly_assigned():
            mvars.pop()
        code_names = ""
        mvar = first_unassigned_mvar(mvars)
        if not mvar:  # All mvars assigned!
            code_names = to_code_names(mvars, selected_objects)
        else:
            # TODO: Remove selected_obj?
            success = mvars_assign_some(mvars, context)
            if success:
                code_names = to_code_names(mvars)
        if code_names:
            code = command + " " + " ".join(code_names)
            codes.append(code)
    if codes:
        return CodeForLean.or_else_from_list(codes)
    else:
        return None

