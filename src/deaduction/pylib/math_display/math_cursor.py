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
from .new_display import MathString, MathList


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
    """

    deaduction_cursor = r'\DeadCursor'

    def __init__(self, math_list: MathList):
        self.math_list = math_list

        self.cursor_address = (len(math_list),)
        self.cursor_is_after = True
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
            self.cursor_address += (1,)
            return True
        else:
            return False

    def go_right(self):
        parent = self.parent_of_current_item
        if parent:
            idx = self.current_idx
            if idx < len(parent):
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
        cs = self.item_for_address(self.cursor_address)
        return cs

    @property
    def parent_of_current_item(self) -> MathList:
        ca = self.cursor_address
        if len(ca) > 0:
            math_list = self.item_for_address(self.cursor_address[:-1])
            return math_list

    def show_cursor(self):
        """
        Insert a special "cursor" MathString at cursor_address, pushing
        elements by 1 to the right.
        """

        if self.__cursor_is_shown:
            return

        parent = self.parent_of_current_item
        idx = self.current_idx
        if not self.cursor_is_after:
            parent.insert(idx, self.deaduction_cursor)
        else:
            parent.insert(idx+1, self.deaduction_cursor)

        self.__cursor_is_shown = True

    def hide_cursor(self):
        """
        Insert a special "cursor" MathString at cursor_address, pushing
        elements by 1 to the right.
        """

        if not self.__cursor_is_shown:
            return

        parent = self.parent_of_current_item
        idx = self.current_idx
        if not self.cursor_is_after:
            cursor = parent.pop(idx)
        else:
            cursor = parent.pop(idx + 1)
        assert cursor == self.deaduction_cursor

        self.__cursor_is_shown = False

    def go_to(self, math_object) -> bool:
        """
        Set the cursor to the last position whose string correspond to the
        given math_object. Return True in case of success.
        """

        address = self.math_list.last_address_of(math_object)
        if address:
            self.cursor_address = address
            return True
        else:
            return False

    @property
    def is_cursor_at_end(self):
        # test = ((len(self.cursor_address) == 1) and
        #         (self.current_idx == len(self.math_list)))
        test = self.cursor_address == tuple() and self.cursor_is_after
        return test

    def increase_pos(self):
        """
        Increase cursor position by one.
        """

        self.hide_cursor()

        if self.is_cursor_at_end:
            return

        # (1) Cursor is before:
        if self.cursor_is_before:
            # (1.1) Try to go down:
            go_down = self.go_down()

            # (1.2) Otherwise, put cursor after current item:
            if not go_down:
                self.set_cursor_after()

        # (2) Cursor is after
        else:
            # (2.1) Try to go right:
            go_right = self.go_right()

            # (2.2) Otherwise, try to go up:
            if not go_right:
                self.go_up()

    @property
    def is_cursor_at_beginning(self):
        # test = ((len(self.cursor_address) == 1) and
        #         (self.current_idx == 0))
        test = self.cursor_address == tuple() and self.cursor_is_before
        return test

    def decrease_pos(self):
        """
        Decrease cursor position by one. Symmetric to the increase() method.
        """

        self.hide_cursor()

        if self.is_cursor_at_beginning:
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




