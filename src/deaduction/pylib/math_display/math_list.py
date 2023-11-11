"""
# math_list.py : class MathCursor #

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

    def set_cursor_before(self):
        self.cursor_is_after = False

    def set_cursor_after(self):
        self.cursor_is_after = True

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
        return self.cursor_address[-1]

    def item_for_address(self, address: tuple) -> Union[MathString,
                                                          MathList]:
        return self.math_list.item_for_address(address)

    @property
    def current_item(self) -> Union[MathString, MathList]:
        cs = self.item_for_address(self.cursor_address)
        return cs

    @property
    def parent_of_current_item(self) -> MathList:
        ml = self.item_for_address(self.current_idx)
        return ml

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
        test = ((len(self.cursor_address) == 1) and
                (self.current_idx == len(self.math_list)))
        return test

    def increase_pos(self):
        """
        Increase cursor position by one.
        """

        # FIXME: cursor is NOT an element, it takes the place of an element.
        # FIXME: take into account before/after

        self.hide_cursor()

        if self.is_cursor_at_end:
            return

        # (1) Try to go down
        current_item = self.current_item
        if isinstance(current_item, MathList):
            self.cursor_address += (0,)
            return

        # (2) Try to go left
        parent = self.parent_of_current_item
        if self.current_idx < len(parent):
            # Case 1: not at the end of the current (parent) list
            self.cursor_address = (self.cursor_address[:-1] +
                                   (self.current_idx + 1,))
            return

        # (3) Try to go up and increase idx
        if len(self.cursor_address) > 1:

            new_idx = self.cursor_address[-2] + 1
            head = self.cursor_address[:-2] + (new_idx,)
            item = self.item_for_address(head)
            tail = item.address_of_first_leaf_descendant
            self.cursor_address = head + tail




    @property
    def is_cursor_at_beginning(self):
        test = ((len(self.cursor_address) == 1) and
                (self.current_idx == 0))
        return test

    def decrease_pos(self):
        """
        Decrease cursor position by one.
        Note that is NOT the symetric of the previous method, because the
        cursor take the place of an item, shifting items to the right.
        """

        # FIXME

        if self.is_cursor_at_beginning:
            return




