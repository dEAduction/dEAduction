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
from deaduction.pylib.config.i18n import _

import deaduction.pylib.config.vars as cvars
import deaduction.pylib.config.dirs as cdirs

log = logging.getLogger(__name__)


class Journal:
    """
    A very simple journal, designed to keep track of every event that occurs
    in dEAduction. It has a single attribute, memory, which is a list of
    events that are triples (nature, content, detail). The main method is
    "add_event", but methods are also provided to retrieve the last events
    of a given nature,
    """
    memory: [tuple]

    event_natures = ('button',
                     'code_sent',
                     'effective_code'
                     'error',
                     'lean_error',
                     'success',
                     'user_input',
                     'various')
    __save_journal = cvars.get('journal.save')
    __journal_file_name = cdirs.local / 'journal.pkl'

    def __init__(self):
        self.memory = []

    def add_event(self, event: tuple, emw=None):
        """
        Add an event entry in the Journal.

        :param event:   (nature, content, details)
        :param emw:     ExerciseMainWindow instance, in which the event
                        will be displayed
        """
        log.debug(f"New event: {event}")
        if event[0] not in self.event_natures:
            log.warning(f"Unexpected event: {event[0]}")
        self.memory.append(event)

        # Display event in the status bar
        if emw:
            nature, content, details = event
            if nature == 'lean_error':
                event = (nature, content, _("request failed"))

            if nature == 'code_sent':
                event = (nature, '...', '')
            # Display event in the status bar
            emw.statusBar.display_status_bar_message(event=event)

        if self.__save_journal:  # fixme: should not be done each time!
            self.write_last_entry()

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
                return None, None, None

        # Search for the last event whose nature is "nature".
        for anti_idx in range(len(self.memory)):
            idx = len(self.memory) - anti_idx -1
            event = self.memory[idx]
            if event[0] == nature:
                return event[1], event[2]  # content, details

        return None, None, None

    def write_file(self):
        with open(self.__journal_file_name, mode='ab') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def write_last_entry(self):
        with open(self.__journal_file_name, mode='ab') as output:
            pickle.dump(self.memory[-1], output, pickle.HIGHEST_PROTOCOL)