from diff_match_patch import diff_match_patch
dmp = diff_match_patch()
import sys

class LeanFile:
    def __init__( self ):
        self.history     = []

        self.idx         = 0  # Current position in history
        self.target_idx  = 0  # Targeted position in history

        self.txt         = "" # Text at current position in history

    ################################
    # Add actions and stuff
    ################################
    def state_add(self, lbl, next_txt, misc_info=dict()):
        # Compute forward diff
        forward_diff  = dmp.patch_make(self.txt, next_txt)
        backward_diff = dmp.patch_make(next_txt, self.txt)

        # Remove elements of history after index
        if self.target_idx < len(self.history):
            del self.history[self.target_idx+1:]

        elif self.target_idx == len(self.history):
            self.history.append(("init",None,None,dict(),)) # Init element

        # Get current element of history
        cur_lbl,cur_bdiff,cur_fwdiff,cur_misc = self.history[self.target_idx]

        # Modify current element of history
        self.history[self.target_idx] = (cur_lbl, cur_bdiff, forward_diff, cur_misc)

        # Add new state element in history
        self.history.append( (lbl, backward_diff, None, misc_info) )

        # Modify history indexes and cache
        self.target_idx = len(self.history)-1
        self.idx        = self.target_idx
        self.txt        = next_txt

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
        # Increment or decrement direction
        ddir = int(self.target_idx > self.idx) - int(self.target_idx < self.idx)

        while self.target_idx != self.idx:
            lbl, patch_backward, patch_forward, misc_info = self.history[self.idx]
            patch = patch_backward if ddir < 0 else patch_forward

            # Apply patch
            self.txt,_ = dmp.patch_apply(patch, self.txt)

            # Update index
            self.idx += ddir

        return self.txt

if __name__=="__main__":
    txt_a = """This is first text
    """

    txt_b = """Thsi is first text,
    With second line !
    """

    ff = LeanFile()
    ff.state_add("First line" , txt_a)
    print("First state\n----------------")
    print(ff.contents)

    ff.state_add("Second line", txt_b)

    print("Second state\n----------------")
    print(ff.contents)

    ff.undo()
    print("After undo\n----------------")
    print(ff.contents)

    ff.redo()
    print("After redo\n----------------")
    print(ff.contents)

    print("History\n----------------")
    for x in ff.history_lbl():
        print(f" * {x}")

