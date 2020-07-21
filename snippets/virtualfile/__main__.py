from diff_match_patch import diff_match_patch
dmp = diff_match_patch()
import sys

from deaduction.pylib.utils import ansiterm as aterm

class LeanFile:
    def __init__( self, file_name="memory" ):

        self.file_name    = file_name
        self.history      = []

        self.idx          = 0  # Current position in history
        self.target_idx   = 0  # Targeted position in history

        self.txt          = "" # Text at current position in history

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

        ddir = int(self.target_idx > self.idx) - int(self.target_idx < self.idx)

        # Update cursor position
        if self.target_idx != self.idx:
            self.__current_pos = self.history[self.target_idx][3]

        # Apply patches to text
        while self.target_idx != self.idx:
            lbl, patch_backward, patch_forward, cursor_pos, misc_info = self.history[self.idx]
            patch = patch_backward if ddir < 0 else patch_forward

            # Apply patch
            self.txt,_ = dmp.patch_apply(patch, self.txt)

            # Update index and cursor position
            self.idx += ddir

    ################################
    # Virtual cursor managment
    ################################
    @property
    def current_pos(self):
        self.__update()
        return self.__current_pos

    @current_pos.setter
    def current_pos(self,x):
        self.__update()
        self.__current_pos = max(min(x,len(self.txt)-1), 0)

    def cursor_move_up(self, nlines):
        """
        Moves the cursor nlines up, at the beginning of the line
        """

        idx    = self.current_pos
        while (idx > 0) and nlines >= 0:
            idx -= 1
            if self.txt[idx] == "\n":
                nlines -= 1

        if idx > 0 : idx += 1 # Not at beginning of document, put the cursor
                              # after the newline character

        self.current_pos = idx

    ################################
    # Actions
    ################################
    def insert( self, lbl, add_txt, misc_info=dict(), move_cursor=True ):
        """
        Inserts text at cursor position, and update cursor position.

        :param lbl:         Label of the history entry of this modification
        :param add_txt:     The text to insert at the given cursor position
        :param misc_info:   Misc. info to store with history entry
        :param move_cursor: Move cursor after inserted text.
        """
        current_pos = self.current_pos
        next_txt = self.txt[:current_pos+1]   \
                   + add_txt                  \
                   + self.txt[current_pos+1:]

        if move_cursor: current_pos += len(add_txt)

        self.state_add(lbl, next_txt, current_pos, misc_info)

    def state_add(self, lbl, next_txt, current_pos=None, misc_info=dict()):
        # Compute forward diff
        forward_diff  = dmp.patch_make(self.txt, next_txt)
        backward_diff = dmp.patch_make(next_txt, self.txt)

        # Compute cursor position
        current_pos = self.current_pos if current_pos is None else current_pos

        # Remove elements of history after index
        if self.target_idx < len(self.history):
            del self.history[self.target_idx+1:]

        elif self.target_idx == len(self.history):
            self.history.append(("init",None,None,0,dict(),)) # Init element

        # Get current element of history
        cur_lbl,cur_bdiff,cur_fwdiff,cur_pos,cur_misc = self.history[self.target_idx]

        # Modify current element of history
        self.history[self.target_idx] = (cur_lbl, cur_bdiff, forward_diff,
                                         cur_pos,cur_misc)

        # Add new state element in history
        self.history.append( (lbl, backward_diff, None, current_pos, misc_info) )

        # Modify history indexes, text buffer, and cursor position
        self.target_idx  = len(self.history)-1
        self.idx         = self.target_idx
        self.txt         = next_txt

        self.current_pos = current_pos

    ################################
    # History control
    ################################
    def undo(self):
        self.target_idx -= 1
        if self.target_idx < 0:
            self.target_idx = 0

    def redo(self):
        self.target_idx += 1
        if self.target_idx >= len(self.history):
            self.target_idx = len(self.history)-1

    def history_lbl(self):
        return map(lambda x:x[0], self.history)

    ################################
    # Get file contents
    ################################
    @property
    def contents(self):
        self.__update()

        return self.txt

    ################################
    # Other properties
    ################################
    @property
    def linecol(self):
        current_pos = self.current_pos

        line = 0
        col  = 0
        idx  = 0

        while (idx <= current_pos) and (idx < len(self.txt)):
            if self.txt[idx] == "\n":
                col   = 0
                line += 1
            else:
                col += 1
            idx += 1
        
        return (line,col,)

if __name__=="__main__":
    def print_contents(ff):
        ct  = ff.contents
        pos = ff.current_pos

        if pos >= len(ct):
            ct = ct + "┊"
        else:
            ct = ct[:pos] + "┊" + ct[pos:]
        print(ct)

    txt_a = """
    goals_analysis,
    hypo_analysis,
    """

    ff = LeanFile()
    ff.insert("First line" , txt_a, move_cursor=True)

    print("First state\n----------------")
    print_contents(ff)

    ff.insert("Second line", "This is second line\n")

    print("Second state\n----------------")
    print_contents(ff)

    ff.insert("Third line", "This is third line\n", move_cursor=False)

    print("Third state\n----------------")
    print_contents(ff)

    ff.undo()
    ff.undo()

    print("After 2 undo\n----------------")
    print_contents(ff)

    ff.redo()
    print("After 1 redo\n----------------")
    print_contents(ff)

    ff.redo()
    print("After 1 redo\n----------------")
    print_contents(ff)

    print("History\n----------------")
    for x in ff.history_lbl():
        print(f" * {x}")
