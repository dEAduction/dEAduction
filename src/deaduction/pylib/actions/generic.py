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

from deaduction.pylib.actions.actiondef import action

from dataclasses import dataclass
import gettext
_ = gettext.gettext

import deaduction.pylib.logger as logger
import logging


##
# Squelette actions type de preuves
##

@action(_("Apply Definition"))
def action_apply_definition(goal : Goal, selected_objects : [PropObj]):
    defi = selected_objects[1].lean_data["name"]
    if len(selected_objects) == 1:
        return "defi {0}".format(defi)
    elif len(selected_objects) == 2:
        return "defi {0} at {1}".format(selected_objects[1].lean_data["name"], defi)
    else:
        return "" #TODO : gestion erreur raise usererror

