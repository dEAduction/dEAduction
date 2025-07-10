"""
##################
# __init__.py :  #
##################

Author(s)      : - Florian Dupeyron <florian.dupeyron@mugcat.fr>

Maintainers(s) : - Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : July 2020

Copyright (c) 2020 the dEAduction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    d∃∀duction is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with d∃∀duction. If not, see <https://www.gnu.org/licenses/>.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from diff_match_patch import diff_match_patch
from pickle import ( dump, HIGHEST_PROTOCOL )
import logging

import deaduction.pylib.config.dirs as        cdirs
import deaduction.pylib.config.vars as        cvars
from deaduction.pylib.utils.filesystem import check_dir

from deaduction.pylib.proof_step import    ProofStep

dmp = diff_match_patch()

log = logging.getLogger(__name__)


@dataclass
class HistoryEntry:
    """
    Represents an entry in the editing history
    of a LeanFile.
    """

    label: str
    patch_backward: List[str]
    patch_forward: List[str]
    cursor_pos: int

    misc_info: Dict[str, any]

    @property
    def proof_step(self):
        return self.misc_info.get("proof_step")


class VirtualFile:
    """
    Class used to store a virtual, editable lean file, with editing
    history managment.
    """

    def __init__(self,
                 file_name="memory", init_txt="",
                 preamble=""       , afterword=""):

        self.file_name    = file_name
        self.history      = [
            HistoryEntry( label="init",
                          patch_backward=None,
                          patch_forward=None,
                          cursor_pos=0,
                          misc_info=dict() )
                            ]         # List[HistoryEntry]

        self.idx          = 0         # Current position in history
        self.target_idx   = 0         # Targeted position in history

        self.__txt        = init_txt  # Text at current position in history

        self.preamble     = preamble   # Text inserted before content
        self.afterword    = afterword  # Text inserted after content

        # Virtual cursor management
        # /!\ IMPORTANT NOTE /!\
        # if you want to use the current_pos attribute in one of the class
        # functions, please do not refer to it directly, but retrieve it
        # in a variable first :
        #     current_pos = self.current_pos
        #     ...
        # in fact, retrieving current_pos calls a property function that
        # updates the cache state according to position in history.
        self.current_pos = 0

    ################################
    # Apply history modifications
    ################################
    def __update(self):
        """
        Updates text cache and cursor position to
        corresponding state in history
        """

        ddir = int(self.target_idx > self.idx) - \
               int(self.target_idx < self.idx)

        # Update cursor position
        if self.target_idx != self.idx:
            self.__current_pos = self.history[self.target_idx].cursor_pos

        # Apply patches to text
        while self.target_idx != self.idx:
            hist_entry = self.history[self.idx]
            patch = hist_entry.patch_backward if ddir < 0 \
                else hist_entry.patch_forward

            # Apply patch
            self.__txt, _ = dmp.patch_apply(patch, self.__txt)

            # Update index and cursor position
            self.idx += ddir

    @property
    def history_length(self):
        return len(self.history)

    def has_history(self):
        return self.history_length > 1

    ################################
    # Virtual cursor managment
    ################################
    @property
    def current_pos(self):
        """
        Gets current cursor position in buffer string
        """
        self.__update()
        return self.__current_pos

    @current_pos.setter
    def current_pos(self, x: int):
        """
        Sets current cursor position in buffer string

        :param x: wanted new position.
        """

        self.__update()
        self.__current_pos = max(min(x, len(self.__txt)), 0)

    def cursor_move_up(self, nlines: int):
        """
        Moves the cursor nlines up, at the beginning of the line

        :param nlines: number of lines to move up
        """

        idx = self.current_pos
        while (idx > 0) and nlines >= 0:
            idx -= 1
            if self.__txt[idx] == "\n":
                nlines -= 1

        if idx > 0:
            idx += 1  # Not at beginning of document, put the cursor
            # after the newline character

    def cursor_move_down(self, nlines: int):
        """
        Moves the cursor nlines down, at the beginning of the line

        :param nlines: number of lines to move down
        """

        idx    = self.current_pos
        leng   = len(self.__txt)
        while (idx < leng) and nlines >= 0:
            idx += 1
            if self.__txt[idx] == "\n":
                nlines -= 1

        self.current_pos = idx

    def cursor_move_to(self, lineno: int):
        """
        Move the cursor to the line lineto

        :param lineno: Line number (starting from 0)
        """

        txt = self.contents
        pos = 0

        for i in range(lineno - 1):
            pos_add = txt[pos:].find("\n")

            if pos_add < 0:  # No more newlines
                pos = len(txt) - 1
                break
            else:
                pos += pos_add + 1
        self.current_pos = pos

    def cursor_save(self):
        """
        Saves the current cursor position into the last
        history entry.
        """

        self.history[-1].cursor_pos = self.current_pos

    def find_first_insertion_of(self, text):
        """
        Find the first time that text was contained in inserted text,
        and return the inserted text (or "" if not found).
        """

        inserted_text = ""
        for idx in range(self.idx):
            entry_dict = self.history[idx].misc_info
            inserted_text = entry_dict.get('inserted_text', '')
            if inserted_text.find(text) != -1:
                break

        return inserted_text

    ################################
    # Actions
    ################################
    def replace(self, old, new) -> bool:
        """
        In the current text, replace first occurence of old with new.
        Return False if old is not found.
        """
        success = (self.__txt.find(old) != -1)
        if not success:
            return False

        current_pos = self.current_pos
        next_txt = self.__txt.replace(old, new, 1)
        # Improve: this assume that cursor is after old in the text.
        current_pos += (len(new) - len(old))
        self.state_add('code_replace', next_txt, current_pos)
        self.state_info_attach(replaced_text=(old, new))
        return True

    def replace_entry_containing(self, old_piece_of_code, new_code):
        old_code = self.find_first_insertion_of(old_piece_of_code)
        self.replace(old_code, new_code)

    def insert(self, label, add_txt, move_cursor=True):
        """
        Inserts text at cursor position, and update cursor position.

        :param label:         Label of the history entry of this modification
        :param add_txt:     The text to insert at the given cursor position
        :param move_cursor: Move cursor after inserted text.
        """

        current_pos = self.current_pos
        next_txt = self.__txt[:current_pos] + add_txt

        if move_cursor:
            current_pos += len(add_txt)

        self.state_add(label, next_txt, current_pos)
        self.state_info_attach(inserted_text=add_txt)

    def set_code(self, code):
        """
        Set code from scratch (independently of previous content)
        and put cursor to end.
        """
        label = 'code_set'
        current_pos = len(code)
        self.state_add(label, code, current_pos=current_pos)

    def state_add(self,
                  label: str, next_txt: str,
                  current_pos: Optional[int] = None):
        """
        Adds a new state/entry in the history for the text.

        :param label: a label for the history entry
        :param next_txt: the new text state
        :param current_pos: Cursor position. None => Current cursor position
        """

        # Compute forward diff
        forward_diff = dmp.patch_make(self.__txt, next_txt)
        backward_diff = dmp.patch_make(next_txt, self.__txt)

        # Compute cursor position
        current_pos = self.current_pos if current_pos is None else current_pos

        # Remove elements of history after index
        if self.target_idx < len(self.history):
            del self.history[self.target_idx + 1:]

        # Get current element of history and modify forward patch
        hist_entry = self.history[self.target_idx]
        hist_entry.patch_forward = forward_diff

        # Add new state element in history
        self.history.append(HistoryEntry(label=label,
                                         patch_backward=backward_diff,
                                         patch_forward=None,
                                         cursor_pos=current_pos,
                                         misc_info=dict()))

        line_number = first_distinct_line(self.__txt, next_txt)

        # Modify history indexes, text buffer, and cursor position
        self.target_idx  = len(self.history) - 1
        self.idx         = self.target_idx
        self.__txt       = next_txt

        self.current_pos = current_pos

        # Keep the number of the first line of last change in misc_info
        self.state_info_attach(first_line_of_last_change=line_number)

    def state_info_attach(self, **kwargs):
        """
        Attach info to the last history entry.

        Example usage:
            lean_file.state_info_attach( my_info = "This is info",
                                         second_info = "Another info")

            lean_file.state_info_attach( another = "You can also attach this")
        """

        self.__update()
        entry = self.history[self.idx]
        entry.misc_info.update(kwargs)

    def get_info(self, info_name: str):
        """
        return info in misc_info of current history_entry (or None)
        """
        self.__update()
        entry_dict = self.history[self.idx].misc_info
        if info_name in entry_dict:
            return entry_dict[info_name]
        else:
            return None

    ################################
    # History control
    ################################
    def undo(self):
        """
        Moves the history cursor one step backwards.
        """
        self.target_idx -= 1
        if self.target_idx < 0:
            self.target_idx = 0

    def history_replace(self, code_string):
        """
        Replace the last entry by code_string, by performing an undo followed
        by insert.
        """
        label = self.history[self.target_idx].label
        self.undo()
        self.insert(label=label, add_txt=code_string)

    def redo(self):
        """
        Moves the history cursor one step forward.
        """
        self.target_idx += 1
        if self.target_idx >= len(self.history):
            self.target_idx = len(self.history) - 1

    def rewind(self):
        """
        Moves the history cursor at the beginning.
        """
        self.target_idx = 0

    def go_to_end(self):
        """
        Moves the history cursor at the end.
        """
        self.target_idx = len(self.history) - 1

    def goto(self, history_nb):
        """
        Move the history cursor at step_nb.
        """
        self.target_idx = history_nb

    def delete(self):
        """
        Delete last step of history.
        """
        self.undo()
        self.__update()
        del self.history[self.target_idx + 1:]

    def history_lbl(self):
        """
        Generator to retrieve the list of history labels.
        """

        # FIXME(florian): Find another generator to explore history ?
        return map(lambda x: x.label, self.history)

    @property
    def history_at_beginning(self):
        return self.target_idx == 0

    @property
    def history_at_end(self):
        return self.target_idx == (len(self.history) - 1)

    ################################
    # Get file contents
    ################################

    @property
    def contents(self):
        """
        Retrieve the complete file contents.
        """
        self.__update()

        return self.preamble + self.__txt + self.afterword

    @property
    def inner_contents(self):
        """
        Retrieve the inner text.
        """
        self.__update()
        return self.__txt

    ################################
    # Other properties
    ################################
    @property
    def linecol(self):
        """
        Retrieve the current position as (line,col)

        :return: a tuple containing the line and the column position of
                 the cursor
        """
        current_pos = self.current_pos

        line = 0
        col  = 0
        idx  = 0

        while (idx <= current_pos) and (idx < len(self.__txt)):
            if self.__txt[idx] == "\n":
                col   = 0
                line += 1
            else:
                col += 1
            idx += 1

        return (line, col,)

    @property
    def first_line_of_inner_content(self):
        """
        return number of the line where proof begins (just after "begin")
        """
        text = self.preamble
        line_number = text.count("\n") + 1
        return line_number

    @property
    def last_line_of_inner_content(self):
        """
        return the number of the last line of inner content
        """
        text = self.preamble + self.inner_contents
        line_number = text.count("\n")
        return line_number

    @property
    def current_line_of_file(self):
        """
        return the line number where code has been inserted in the whole
        file (with preamble)
        """
        text = self.preamble
        line_in_vf, _ = self.linecol
        line_number = text.count("\n") + line_in_vf
        return line_number

    @property
    def first_line_of_last_change(self):
        """
        Return the number of the first line at which the current content
        differs from the previous one (taking into account the preamble)
        """
        line_number = self.get_info("first_line_of_last_change")
        if line_number is None:
            return self.first_line_of_inner_content
        else:
            return self.first_line_of_inner_content + (line_number - 1)


def first_distinct_line(txt1: str, txt2: str) -> int:
    """
    Compute the first line at which the two given strings are distinct
    (first line = 1)
    """
    txt1 = txt1.splitlines()
    txt2 = txt2.splitlines()
    counter = 0
    while counter < min(len(txt1), len(txt2)) \
            and txt1[counter] == txt2[counter]:
        counter += 1
    return counter + 1  # first line = 1, not 0


class LeanFile(VirtualFile):

    def proof_step_from_history_nb(self, history_nb) -> Optional[ProofStep]:
        if 0 <= history_nb < len(self.history):
            return self.history[history_nb].misc_info.get('proof_step')
        else:
            return None

    @property
    def previous_proof_step(self) -> Optional[ProofStep]:
        return self.proof_step_from_history_nb(self.target_idx-1)

    @property
    def current_proof_step(self) -> ProofStep:
        return self.proof_step_from_history_nb(self.target_idx)

    @property
    def next_proof_step(self) -> Optional[ProofStep]:
        if self.target_idx < len(self.history)-1:
            return self.history[self.target_idx+1].misc_info.get('proof_step')
        else:
            return None

    @property
    def button(self):
        proof_step = self.current_proof_step
        if proof_step:
            return proof_step.button

    @property
    def statement(self):
        proof_step = self.current_proof_step
        if proof_step:
            return proof_step.statement_item

    @property
    def selection(self):
        proof_step = self.current_proof_step
        if proof_step:
            return proof_step.selection

    @property
    def current_number_of_goals(self):
        return len(self.current_proof_step.proof_state.goals)

    @property
    def previous_number_of_goals(self):
        if self.previous_proof_step:
            return len(self.previous_proof_step.proof_state.goals)
        else:
            return 1

    @property
    def delta_goals_count(self):
        return self.current_number_of_goals - self.previous_number_of_goals

    def add_seq_num(self, seq_num: int):
        """
        Add seq_num in a comment at the beginning of the preamble.
        """
        seq_num_str = f"-- Seq num {seq_num}\n"
        if self.preamble:
            old_seq_num_str, _, raw_preamble = self.preamble.partition("\n")
            if old_seq_num_str.startswith('-- Seq num'):
                self.preamble = seq_num_str + raw_preamble
            else:
                self.preamble = seq_num_str + self.preamble

