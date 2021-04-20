"""
# __init__.py : Provide the Journal class
    
The Journal class is designed
(1) to keep track of all events occurring in the soft, and
(2) to serve as a filter towards the status bar.

It is instantiated exactly once.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 12 2020 (creation)
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
import                  logging
from dataclasses import dataclass
import                  pickle
import os
from typing import Any, Dict, Callable
import trio

from deaduction.pylib.config.i18n import _

import deaduction.pylib.config.vars as cvars
import deaduction.pylib.config.dirs as cdirs

from deaduction.pylib.mathobj import    ProofStep
from deaduction.pylib.coursedata import AutoStep

log = logging.getLogger(__name__)


class EventNature(str):
    """Class clarifying the nature of journal's events."""
    button =               'button'
    statement =            'statement'
    context_selection =    'context selection'
    user_input =           'user input'
    effective_code =       'effective code'
    lean_code =            'Lean code'
    code_from_editor =     'code from editor'
    wrong_user_input =     'WrongUserInput'
    failed_request_error = 'FailedRequestError'
    success_message =      'success message'
    new_proof_state =      'new proof state'
    other =                'other'


class Journal:
    """
    A class to record events in the memory attribute. The events occuring
    during a given proof step are temporary stored in the new_events attribute,
    and stored in memory only by the update_events() method. This allow
    global information process, e.g. to call the display in a StatusBar. The
    display is handled by the display_message attribute.
    """

    memory:     [ProofStep]

    __save_journal = cvars.get('journal.save')
    __journal_file_name = cdirs.local / 'journal.pkl'

    def __init__(self, display_message=None):
        self.memory = []

    def store(self, proof_step: ProofStep, emw):
        # TODO: add time
        self.memory.append(proof_step)
        display = AutoStep.from_proof_step(proof_step, emw)
        log.debug(f"Storing proof_step {display}")

    def save(self):
        # TODO: add time in the filename
        with open(self.__journal_file_name, mode='w') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    # def write_last_entry(self):
    #     with open(self.__journal_file_name, mode='ab') as output:
    #         pickle.dump(self.memory[-1], output, pickle.HIGHEST_PROTOCOL)