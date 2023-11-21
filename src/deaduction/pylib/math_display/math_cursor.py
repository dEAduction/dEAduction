"""
# math_cursor.py : class MathCursor #

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 12 2021 (creation)
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


from typing import Union
import logging
from PySide2.QtGui import QTextDocument

from .new_display import MathString, MathList

log = logging.getLogger(__name__)


class MathCursor:
    """
    A class to encode a position in a tree of MathStrings.
    The cursor is considered as a virtual additional element in one of the
    list of the tree. Its position may be any valid address in the tree,
    but the last int of the address may correspond to an additional element
    (thus being equal to the length of the current list).

    Parameter cursor_address is the address of the current position of the
    cursor in the tree of string. (Beware, this is NOT the address of the
    current marked descendant of the root math object).
    e.g. if the tree is
    [['f''], '\circ, ['g']]
    then cursor_address
        () corresponds to the main list,
        (0, ) corresponds to the MathList ['f'],
        (0, 0) corresponds to the MathString 'f'
        (1) corresponds to the MathString '\circ'
    """

    deaduction_cursor = MathString.cursor

    def __init__(self, root_math_object, cursor_math_object):
        self.math_list = MathList.complete_latex_shape(math_object=root_math_object)
        self.target_math_object = root_math_object

        self.cursor_address = tuple()
        self.cursor_is_after = True

        self.go_to(cursor_math_object if cursor_math_object
                   else root_math_object)
        self.__cursor_is_shown = False

    @property
    def cursor_is_before(self):
        return not self.cursor_is_after

    def set_cursor_before(self):
        self.cursor_is_after = False

    def set_cursor_after(self):
        self.cursor_is_after = True

    def go_up(self):
        ca = self.cursor_address
        if len(ca) > 0:
            self.cursor_address = ca[:-1]
            return True
        else:
            return False

    def go_down(self):
        if isinstance(self.current_item, MathList):
            if self.cursor_is_before:  # Go to beginning of current_item
                self.cursor_address += (0,)
            else:  # Go to end of current item
                self.cursor_address += (len(self.current_item)-1,)
            return True
        else:
            return False

    def go_right(self):
        parent = self.parent_of_current_item
        if parent:
            idx = self.current_idx
            if idx < len(parent) - 1:
                self.cursor_address = (self.cursor_address[:-1] +
                                       (idx + 1,))
                return True
        return False

    def go_left(self):
        idx = self.current_idx
        if idx and idx > 0:
            self.cursor_address = (self.cursor_address[:-1] +
                                   (idx - 1,))
            return True
        else:
            return False

    @property
    def root_math_object(self):
        return self.math_list.root_math_object

    @property
    def current_math_object(self):
        line = self.current_item.line_of_descent
        cmo = self.root_math_object.descendant(line)
        return cmo

    #######################
    # Pure cursor methods #
    #######################
    @property
    def current_idx(self):
        ca = self.cursor_address
        if len(ca) > 0:
            return ca[-1]

    def item_for_address(self, address: tuple) -> Union[MathString,
                                                        MathList]:
        return self.math_list.item_for_address(address)

    @property
    def current_item(self) -> Union[MathString, MathList]:
        """
        Return item pointed by self.cursor_address, except that single-term
        lists are (recursively) replaced by their lonely term.
        """
        cs = self.item_for_address(self.cursor_address)
        while isinstance(cs, MathList) and len(cs) == 1:
            cs = cs[0]
        return cs

    @property
    def parent_of_current_item(self) -> MathList:
        ca = self.cursor_address
        if len(ca) > 0:
            math_list = self.item_for_address(self.cursor_address[:-1])
            return math_list

    def parent_and_idx_of_cursor(self):
        """
        Return parent and idx of cursor in self.math_list: this is where the
        'cursor' string is to be found (unless cursor is hidden).
        """
        parent = self.parent_of_current_item
        if parent:
            idx = (self.current_idx if not self.cursor_is_after else
                   self.current_idx + 1)
        else:  # No parent : self is root_math_object
            parent = self.math_list
            if not self.cursor_is_after:
                idx = 0
            elif not self.__cursor_is_shown:
                idx = (len(self.math_list))
            else:
                idx = len(self.math_list) - 1

        if self.__cursor_is_shown:
            assert parent[idx] == self.deaduction_cursor

        return parent, idx

    def show_cursor(self):
        """
        Insert a special "cursor" MathString at cursor_address, pushing
        elements by 1 to the right.
        """

        if self.__cursor_is_shown:
            return

        parent, idx = self.parent_and_idx_of_cursor()
        parent.insert(idx, self.deaduction_cursor)

        self.__cursor_is_shown = True

    def hide_cursor(self):
        """
        Remove the cursor at cursor_address.
        """

        if not self.__cursor_is_shown:
            return

        parent, idx = self.parent_and_idx_of_cursor()
        cursor = parent.pop(idx)
        assert cursor == self.deaduction_cursor

        self.__cursor_is_shown = False

    def linear_cursor_position(self):
        """
        Return the position at which the cursor should be seen, in a text
        document.
        """
        # doc = QTextDocument()
        # MathDisplay.mark_cursor = True
        # MathDisplay.cursor_pos = self.target.marked_descendant().cursor_pos
        # doc.setHtml(self.math_list.to_string())
        # text = doc.toPlainText()
        # print(f"VIRTUAL CURSOR POS: {text}")
        # position = text.find(MathDisplay.cursor_tag)
        # print(f"vcp in: {text} --> {position}")
        # print("Marked latex shape:")
        # print(self.target.latex_shape())
        # MathDisplay.mark_cursor = False
        # MathDisplay.cursor_pos = None
        doc = QTextDocument()
        self.show_cursor()
        doc.setHtml(self.math_list.to_string())
        text = doc.toPlainText()
        position = text.find(self.deaduction_cursor)
        self.hide_cursor()
        return position

    def debug(self):
        log.debug(f"Math cursor: {self.math_list}")
        log.debug(f"Cursor address: "
                  f"{'after' if self.cursor_is_after else 'before'}"
                  f" {self.cursor_address}")
        log.debug(f"Current item: "
                  f" {self.current_item}")
        log.debug(f"Marked descendant: "
                  f"{self.root_math_object.marked_descendant()}")

    def set_marked_element(self, yes=True):
        math_object = self.current_math_object
        if hasattr(math_object, "set_marked"):
            self.root_math_object.unmark()
            math_object.set_marked(yes)

    def go_to(self, math_object, after=True, set_marked=True) -> bool:
        """
        Set the cursor to the last position whose string correspond to the
        given math_object. Return True in case of success.
        """

        # self.set_marked_element(False)
        address = self.math_list.last_address_of(math_object)
        if address:
            self.cursor_address = address
            self.cursor_is_after = after
            if set_marked:
                self.set_marked_element(True)
            self.debug()
            return True
        else:
            return False

    def is_at_end(self):
        # test = ((len(self.cursor_address) == 1) and
        #         (self.current_idx == len(self.math_list)))
        test = self.cursor_address == tuple() and self.cursor_is_after
        return test

    def is_at_beginning(self):
        # test = ((len(self.cursor_address) == 1) and
        #         (self.current_idx == 0))
        test = self.cursor_address == tuple() and self.cursor_is_before
        return test

    def go_to_end(self, set_marked=True):
        # self.set_marked_element(False)
        self.cursor_address = tuple()
        self.set_cursor_after()

        if set_marked:
            self.set_marked_element(True)

    def go_to_beginning(self, set_marked=True):
        # self.set_marked_element(False)
        self.cursor_address = tuple()
        self.set_cursor_before()

        if set_marked:
            self.set_marked_element(True)

    def adjust_position(self, set_marked=True):
        """
        If cursor is before a single-term list, go down to the term.
        Do so inductively. Symmetrically if cursor is after.
        """

        while (isinstance(self.current_item, MathList) and
               len(self.current_item) == 1):
            self.go_down()

        if set_marked:
            self.set_marked_element()

    def increase_pos(self, set_marked=True):
        """
        Increase cursor position by one.
        """

        # self.set_marked_element(False)
        self.hide_cursor()

        if self.is_at_end():
            return

        # (1) Cursor is before:
        if self.cursor_is_before:
            # (1.1) Try to go down:
            go_down = self.go_down()

            # (1.2) Otherwise, put cursor after current item:
            if not go_down:  # or isinstance(self.current_item, MathString):
                self.set_cursor_after()

        # (2) Cursor is after
        else:
            # (2.1) Try to go right:
            go_right = self.go_right()

            # (2.2) Otherwise, try to go up:
            if not go_right:
                self.go_up()

        # self.adjust_position(set_marked=set_marked)

        # if set_marked:
        #     self.set_marked_element(True)

        self.debug()

    def decrease_pos(self, set_marked=True):
        """
        Decrease cursor position by one. Symmetric to the increase() method.
        """

        self.hide_cursor()
        # self.set_marked_element(False)

        if self.is_at_beginning():
            return

        # (1) Cursor is after:
        if self.cursor_is_after:
            # (1.1) Try to go down:
            go_down = self.go_down()

            # (1.2) Otherwise, put cursor after current item:
            if not go_down:
                self.set_cursor_before()

        # (2) Cursor is before
        else:
            # (2.1) Try to go left:
            go_left = self.go_left()

            # (2.2) Otherwise, try to go up:
            if not go_left:
                self.go_up()

        if set_marked:
            self.set_marked_element(True)

        self.debug()

    def fast_increase(self):
        """
        Increase pos until cursor pos in the linear order has actually
        changed (and not only pos in the tree).
        """

        # TODO
        pass

    def fast_decrease(self):
        """
        Increase pos until cursor pos in the linear order has actually
        changed (and not only pos in the tree).
        """

        # TODO
        pass



