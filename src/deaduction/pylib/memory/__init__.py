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

from deaduction.pylib.mathobj import ProofStep

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


class JournalEvent:
    """
    A class for events that are to be recorded in a Journal instance.
    """
    nature: EventNature
    content: Any
    info: Dict[str, Any]

    def __init__(self, nature, content, info=None):
        self.nature  = nature
        self.content = content
        self.info    = info if info is not None else {}

    def is_error(self):
        return self.nature == EventNature.failed_request_error \
            or self.nature == EventNature.wrong_user_input

    def is_success(self):
        return self.nature == EventNature.success_message

    def is_proof_state(self):
        return self.nature == EventNature.new_proof_state


class Journal:
    """
    A class to record events in the memory attribute. The events occuring
    during a given proof step are temporary stored in the new_events attribute,
    and stored in memory only by the update_events() method. This allow
    global information process, e.g. to call the display in a StatusBar. The
    display is handled by the display_message attribute.
    """

    memory:     [JournalEvent]
    new_events: [JournalEvent]
    display_message: Callable

    __save_journal = cvars.get('journal.save')
    __journal_file_name = cdirs.local / 'journal.pkl'

    def __init__(self, display_message=None):
        self.memory = []
        self.new_events = []
        self.display_message = display_message

        # Events memory channel
        self.events_send, self.events_receive = \
            trio.open_memory_channel(max_buffer_size=1024)

    def add_event(self, event: JournalEvent):
        """
        Store event in self.new_events
        :param event:
        :param display_message:
        """
        self.new_events.append(event)
        if event.is_error() or event.is_proof_state():
            self.update_events()

    def update_events(self):
        """
        Add new_events to memory, and process information for that step.
        """
        # TODO : process info
        log.debug(f"Events: {[event.nature for event in self.new_events]}")

        for event in self.new_events:
            if event.is_error() or event.is_success():
                if self.display_message:
                    self.display_message(event)

            # Adjust goal number, and goals msg list TODO: put it here!!

            # Create ProofStep, and store in lean_file.history
            # button (and selection), PS, success_msg
            # sense of rw if statement
        proof_step = ProofStep

        self.memory.extend(self.new_events)
        self.new_events = []

    def store_lean_code(self, lean_code):
        nature  = EventNature.lean_code
        content = lean_code
        event   = JournalEvent(nature, content)
        self.add_event(event)
        message = lean_code.extract_success_message()
        if message:
            nature = EventNature.success_message
            event = JournalEvent(nature, message)
            self.add_event(event)

    def store_effective_code(self, code):
        nature  = EventNature.effective_code
        content = code
        event   = JournalEvent(nature, content)
        self.add_event(event)
        message = code.extract_success_message()
        if message:
            nature = EventNature.success_message
            event = JournalEvent(nature, message)
            self.add_event(event)

    def store_button(self, button_type):
        nature  = EventNature.button
        content = button_type
        event   = JournalEvent(nature, content)
        self.add_event(event)

    def store_proof_state(self, proof_state):
        nature  = EventNature.new_proof_state
        content = proof_state
        event   = JournalEvent(nature, content)
        self.add_event(event)

    def store_statement(self, statement_name):
        nature  = EventNature.statement
        content = statement_name
        event   = JournalEvent(nature, content)
        self.add_event(event)

    def store_failed_request_error(self, error):
        nature  = EventNature.failed_request_error
        content = error.message
        info    = error.info
        event   = JournalEvent(nature, content, info)
        self.add_event(event)

    def store_wrong_user_input(self, error):
        nature  = EventNature.wrong_user_input
        content = error.message
        event   = JournalEvent(nature, content)
        self.add_event(event)

    def store_selection(self, selection):
        nature  = EventNature.context_selection
        content = selection
        event   = JournalEvent(nature, content)
        self.add_event(event)

    def store_user_input(self, user_input):
        nature  = EventNature.user_input
        content = user_input
        event   = JournalEvent(nature, content)
        self.add_event(event)

    def store_lean_editor(self):
        nature  = EventNature.code_from_editor
        content = ''
        event   = JournalEvent(nature, content)
        self.add_event(event)

    def get_last_event(self, nature='any'):
        """
        Return content and detail for last event of a given nature
        :param nature:  an element of the event_natures list
        :return:        triplet
        """
        if nature == 'any':
            if self.memory:
                return self.memory[-1]
            else:
                return None

        # Search for the last event whose nature is "nature".
        for anti_idx in range(len(self.memory)):
            idx = len(self.memory) - anti_idx -1
            event = self.memory[idx]
            if event.nature == nature:
                return event  # content, details

        return None

    def write_file(self):
        with open(self.__journal_file_name, mode='ab') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def write_last_entry(self):
        with open(self.__journal_file_name, mode='ab') as output:
            pickle.dump(self.memory[-1], output, pickle.HIGHEST_PROTOCOL)