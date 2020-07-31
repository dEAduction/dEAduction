
from dataclasses import dataclass
from typing import Dict, List, Optional
from diff_match_patch import diff_match_patch

dmp = diff_match_patch()


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


class LeanFile:
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
                          misc_info=dict )
        ]  # List[HistoryEntry]

        self.idx          = 0         # Current position in history
        self.target_idx   = 0         # Targeted position in history

        self.__txt          = init_txt  # Text at current position in history

        self.preamble     = preamble   # Text inserted before content
        self.afterword    = afterword  # Text inserted after content

        # Virtual cursor managment
        # /!\ IMPORTANT NOTE /!\
        # if you want to use the current_pos attribute in one of the class
        # functions, please do not refer to it directly, but retrieve it
        # in a variable first :
        #     current_pos = self.current_pos
        #     ...
        # in fact, retrieving current_pos calls a property function that
        # updates the cache state according to position in history.
        self.current_pos  = 0

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

        idx    = self.current_pos
        while (idx > 0) and nlines >= 0:
            idx -= 1
            if self.__txt[idx] == "\n":
                nlines -= 1

        if idx > 0 :
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

    ################################
    # Actions
    ################################
    def insert( self, label, add_txt, move_cursor=True ):
        """
        Inserts text at cursor position, and update cursor position.

        :param lbl:         Label of the history entry of this modification
        :param add_txt:     The text to insert at the given cursor position
        :param misc_info:   Misc. info to store with history entry
        :param move_cursor: Move cursor after inserted text.
        """

        current_pos = self.current_pos
        next_txt = self.__txt[:current_pos] \
            + add_txt              \

        if move_cursor:
            current_pos += len(add_txt)

        self.state_add(label, next_txt, current_pos)

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
        forward_diff  = dmp.patch_make(self.__txt, next_txt)
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
        self.history.append( HistoryEntry(label=label,
                                          patch_backward=backward_diff,
                                          patch_forward=None,
                                          cursor_pos=current_pos,
                                          misc_info=dict()))

        # Modify history indexes, text buffer, and cursor position
        self.target_idx  = len(self.history) - 1
        self.idx         = self.target_idx
        self.__txt       = next_txt

        self.current_pos = current_pos

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

    ################################
    # History control
    ################################
    def undo(self):
        """
        Moves the history cursor one step backwards
        """
        self.target_idx -= 1
        if self.target_idx < 0:
            self.target_idx = 0

    def redo(self):
        """
        Moves the history cursor one step forward
        """
        self.target_idx += 1
        if self.target_idx >= len(self.history):
            self.target_idx = len(self.history) - 1

    def history_lbl(self):
        """
        Generator to retrieve the list of history labels.
        """

        # FIXME(florian): Find another generator to explore history ?
        return map(lambda x: x.label, self.history)

    @property
    def history_at_beginning(self):
        return self.target_idx == 0

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
        Retrieve the inner text
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
