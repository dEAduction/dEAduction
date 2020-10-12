"""
############################################################
# utils.py : utilitarian functions used in files in        #
# the actions directory                                    #
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

from deaduction.pylib.actions import WrongUserInput

_VAR_NB = 0
_FUN_NB = 0
_CODE_NB = 0


def get_new_var():
    global _VAR_NB
    _VAR_NB += 1
    return "x{0}".format(_VAR_NB)


def get_new_fun():
    global _FUN_NB
    _FUN_NB += 1
    return "f{0}".format(_FUN_NB)


# OBSOLETE : see mathobj.give_name.get_new_hyp()
def get_new_hyp():
    global _VAR_NB
    _VAR_NB += 1
    return "h{0}".format(_VAR_NB)


def format_orelse(list_of_choices):
    global _CODE_NB
    if len(list_of_choices) == 0:
        raise WrongUserInput
    _CODE_NB += 1
    if len(list_of_choices) == 1:
        return list_of_choices[0]
    else:
        list_of_choices = map(lambda string : f'`[ {string}, trace \"EFFECTIVE CODE {_CODE_NB} : {string}\"]', list_of_choices)
        return " <|> ".join(list_of_choices) + ", "

