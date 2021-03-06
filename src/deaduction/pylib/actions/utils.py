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

_VAR_NB = 0

def get_new_var():
    global _VAR_NB
    _VAR_NB += 1
    return "x{0}".format(_VAR_NB)

def get_new_hyp():
    global _VAR_NB
    _VAR_NB += 1
    return "h{0}".format(_VAR_NB)

