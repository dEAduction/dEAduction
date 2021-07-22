"""
# pickle_utils.py : load and save python objects

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
import logging
import pickle5 as pickle

log = logging.getLogger(__name__)


####################
# pickle utilities #
####################
def load_object(filename):
    """
    Load pickled object obj from file with name filename
    (file is assumed to contain exactly one object).
    """
    log.debug(f"Trying to load object from {filename}...")
    if not filename.exists():
        log.debug("...no file found")
        return None
    else:
        with filename.open(mode="rb") as input_file:
            log.debug("...loaded")
            return pickle.load(input_file)


def save_object(obj, filename):
    """
    Save pickled object obj in a file with name filename.
    """
    log.debug(f"Saving pickled object in {filename}")
    with filename.open(mode='wb') as output:  # Overwrites any existing file
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

