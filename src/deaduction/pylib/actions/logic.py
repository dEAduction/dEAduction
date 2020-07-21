"""
############################################################
# logic.py : functions to call in order to                 #
# translate actions into lean code                         #
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

from deaduction.pylib.actions.actiondef import action

from dataclasses import dataclass

import gettext
_ = gettext.gettext

import deaduction.pylib.logger as logger
import logging


##
# Squelette actions logiques
##

@action(_("Negation"))
def action_negate(goal,):
    return ""

@action(_("Implication"))
def action_implicate(a):
    return ""

@action(_("And"))
def action_and(a):
    return ""

@action(_("Or"))
def action_or(a):
    return ""

@action(_("If and only if"))
def action_iff(a):
    return ""

@action(_("For all"))
def action_forall(a):
    return ""

@action(_("Exists"))
def action_exists(a):
    return ""

if __name__ == "__main__":
    logger.configure()
