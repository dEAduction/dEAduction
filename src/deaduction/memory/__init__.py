"""
# __init__.py : <#ShortDescription> #
    
    <#optionalLongDescription>

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
from deaduction.config import user_config

log = logging.getLogger(__name__)



@dataclass
class Journal:
    """
    A very simple journal, designed to keep track of every event that occurs
    in dEAduction. It has a single attribute, memory, which is a list of
    events that are triples (nature, content, detail)
    """
    memory: [tuple]

    event_natures = ('button',
                     'code',
                     'error',
                     'lean_error'
                     'message',
                     'user_input',
                     'various')
    __save_journal = user_config.getboolean('save_journal')
    __journal_file_name = os.path.join(
        os.path.dirname(__file__)) + '/journal.pkl'

    def add_event(self, event: tuple, emw=None):
        """
        Add an entry in the Journal.

        :param event:   (nature, content, details)
        :param emw:      ExerciseMainWindow instance, in which the event
        will be displayed
        """
        log.debug(f"New event: {event}")
        if event[0] not in self.event_natures:
            log.warning(f"Unexpected event: {event[0]}")
        self.memory.append(event)

        if emw:
            nature, content, details = event
            if nature == 'lean_error':
                event = (nature, content, "request failed")

            # display event
            emw.display_status_bar_message(event=event)

        if self.__save_journal:  # fixme: should not be done each time!
            self.write_last_entry()

    def get_last(self, nature='any'):
        """
        Return content and detail for last event of a given nature
        :param nature:
        :return:
        """
        if nature == 'any':
            if self.memory:
                return self.memory[-1]
            else:
                return None

        for anti_idx in range(len(self.memory)):
            idx = len(self.memory) - anti_idx -1
            event = self.memory[idx]
            if event[0] == nature:
                return event[1], event[2]  # content, details

        return None

    def write_file(self):
        with open(self.__journal_file_name, mode='ab') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def write_last_entry(self):
        with open(self.__journal_file_name, mode='ab') as output:
            pickle.dump(self.memory[-1], output, pickle.HIGHEST_PROTOCOL)


# init
JOURNAL = Journal([])
