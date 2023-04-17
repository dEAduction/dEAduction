"""
request_method.py : define the current method for request to Lean server.

    Contains the CourseData class, which pre-processes some data for the
    ServerInterface class to process a list of statements of a given course.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 07 2021 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the d∃∀duction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    d∃∀duction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

import deaduction.pylib.config.vars as cvars


def from_previous_state_method():
    fpps = cvars.get('others.Lean_request_method', 'automatic')
    if fpps == 'normal':
        return False
    elif fpps == 'from_previous_proof_state':
        return True

    return cvars.get('others.currently_using_from_previous_proof_state_method')


