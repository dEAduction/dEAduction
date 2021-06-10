"""
# __init__.py : Provide the Journal class
    
The Journal class is designed to keep track of all events occurring in the
current proof. It is instantiated exactly once for a given proof. If the
journal.save parameter in the config file is True, then the journal content
is saved when the exercise window is closed.

The content is saved under two format:
(1) a 'pkl' file containing an instance of the Exercise class, with the
proof_steps saved in the refined_auto_step attribute. This file can be used
fo autotests.
(2) a 'txt' file which contains the logs of the proof, in which the successive
proof steps are presented, with context, target, and actions.

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
import logging
import pickle5 as pickle
import time

from deaduction.pylib.config.i18n import _

import deaduction.pylib.config.vars as        cvars
import deaduction.pylib.config.dirs as        cdirs
from deaduction.pylib.utils.filesystem import check_dir

from deaduction.pylib.mathobj import          ProofStep

log = logging.getLogger(__name__)


class Journal:
    """
    A class to record events in the memory attribute. The events occurring
    during a proof step are stored in the proof_step attribute of
    ExerciseMainWindow, and then stored in Journal.memory.
    """

    memory:     [ProofStep]

    __save_journal = cvars.get('journal.save')
    __journal_file_name = cdirs.local / 'journal.pkl'

    def __init__(self, display_message=None):
        self.memory = []

    def store(self, proof_step: ProofStep, emw):
        proof_step.time = time.localtime(time.time())
        self.memory.append(proof_step)
        # display = AutoStep.from_proof_step(proof_step, emw)
        # log.debug(f"Storing proof_step {display}")

    def save_exercise_with_proof_steps(self, emw):
        """
        (1) Incorporate journal as auto_steps attribute to emw.exercise,
        and save this to cdirs.journal as a 'pkl' file.
        (2) Compute a text version of each proof step, and save the result
        in a 'txt' file.

        :param emw: ExerciseMainWindow instance
        """

        save = cvars.get('journal.save', False)
        if not save:
            return

        # Building auto_steps
        auto_steps = [proof_step.auto_step for proof_step in self.memory
                      if proof_step.auto_step is not None]

        # Saving
        date = time.strftime("%d%b%Hh%M")
        exercise = emw.exercise
        exercise.refined_auto_steps = auto_steps
        filename = 'journal_' \
                   + exercise.lean_short_name.replace('.', '_') \
                   + date \
                   + '.pkl'
        check_dir(cdirs.journal, create=True)
        file_path = cdirs.journal / filename

        total_string = 'ProofSteps\n'
        for step in auto_steps:
            total_string += '    ' + step.raw_string + ',\n'
        print(total_string)

        log.debug(f"Saving auto_steps in {file_path}")
        with open(file_path, mode='xb') as output:
            pickle.dump(exercise, output, pickle.HIGHEST_PROTOCOL)

        file_path = file_path.with_suffix('.txt')
        log.debug(f"Saving journal in {file_path}")
        txt = self.display()
        print(txt)
        with open(file_path, mode='xt') as output:
            output.write(txt)

    def display(self):
        """
        Compute a txt version of the proof stored in journal.memory.
        :return:
        """
        display_txt = ""
        step_counter = 0
        time_deltas = [0]
        for counter in range(len(self.memory)):
            if counter < len(self.memory) -1 :
                t2 = self.memory[counter+1].time
                t1 = self.memory[counter].time
                # Time diff in seconds
                delta = (t2.tm_min - t1.tm_min)*60 + t2.tm_sec - t1.tm_sec
                time_deltas.append(delta)
        time_deltas.append(0)
        for step, time_delta in zip(self.memory, time_deltas):
            # Compute display of the proof step:
            step_txt = step.display()  # ProofStep.display()
            time_display = "#" * int(time_delta/10)
            time_display2 = str(step.time.tm_min) + "'" + str(step.time.tm_sec)
            step_counter += 1
            more_txt = "------------------------------------\n"
            more_txt += time_display + "\n"
            more_txt += _("Step n°{} ").format(step_counter) \
                + "(" + time_display2 + ")" + "\n"
            more_txt += step_txt
            display_txt += more_txt
        return display_txt

