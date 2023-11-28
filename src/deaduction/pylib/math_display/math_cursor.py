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

    def __init__(self, root_math_object, cursor_math_object, go_to_end=True):
        self.math_list = MathList.complete_latex_shape(
            math_object=root_math_object,
            format_='html')
        self.math_list = self.math_list.remove_formatters()
        self.target_math_object = root_math_object

        self.cursor_address = tuple()
        self.cursor_is_after = True
        self.__cursor_is_shown = False

        if cursor_math_object:
            self.go_to(cursor_math_object)
        elif go_to_end:
            self.go_to_end()

    def __repr__(self):
        rmo = self.target_math_object.__repr__()
        repr = f"MathCursor(target_math_object={rmo})"
        self.show_cursor()
        ml = f"MathList: {self.math_list}"
        self.hide_cursor()
        address = (f"Cursor address: "
                   f"{'after' if self.cursor_is_after else 'before'} "
                   f"{self.cursor_address}")
        item = f"Current item:  {self.current_item}"
        mo = f"Current math object:  {self.current_math_object}"
        md = f"Marked descendant: {self.root_math_object.marked_descendant()}"
        repr = '\n'.join([repr, ml, address, item, mo, md])
        return repr

    @property
    def cursor_is_before(self):
        return not self.cursor_is_after

    def set_cursor_before(self, yes=True):
        self.cursor_is_after = not yes

    def set_cursor_after(self, yes=True):
        self.cursor_is_after = yes

    def set_cursor_at_the_same_position_as(self, other):
        assert isinstance(other, MathCursor)
        # self.go_to_address(other.cursor_address,
        #                    set_cursor_after=other.cursor_is_after,
        #                    set_marked=False)
        self.cursor_address = other.cursor_address
        self.cursor_is_after = other.cursor_is_after

    @property
    def root_math_object(self):
        return self.math_list.root_math_object

    @property
    def current_math_object(self):
        # return self.current_item.descendant
        # line = self.current_item.line_of_descent
        # cmo = self.root_math_object.descendant(line)
        cmo = self.current_item.descendant
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

    def current_item_linear_idx(self):
        """
        Return idx of the current item in the linear math_list.
        """

        linear_list: list = self.math_list.linear_list()

        idx = 0
        for item in linear_list:
            if item is self.current_item:
                break
            idx += 1
        if idx < len(linear_list):
            return idx

    def linear_text_cursor_position(self):
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
        log.debug(str(self))
        # pass
        # self.show_cursor()
        # log.debug(f"Math cursor: {self.math_list}")
        # self.hide_cursor()
        # log.debug(f"Cursor address: "
        #           f"{'after' if self.cursor_is_after else 'before'}"
        #           f" {self.cursor_address}")
        # log.debug(f"Current item: "
        #           f" {self.current_item}")
        # log.debug(f"Current math object: "
        #           f" {self.current_math_object}")
        # log.debug(f"Marked descendant: "
        #           f"{self.root_math_object.marked_descendant()}")
        #
        # log.debug("")

    def set_marked_element(self, yes=True):
        math_object = self.current_math_object
        if hasattr(math_object, "set_marked"):
            self.root_math_object.unmark()
            math_object.set_marked(yes)

    def go_up(self):
        ca = self.cursor_address
        if len(ca) > 0:
            self.cursor_address = ca[:-1]
            return True
        else:
            return False

    def go_down(self):
        """
        Go either to first child if cursor_is_before, or to last child if
        not.
        """
        if isinstance(self.current_item, MathList):
            if self.cursor_is_before:  # Go to beginning of current_item
                self.cursor_address += (0,)
            else:  # Go to end of current item
                self.cursor_address += (len(self.current_item)-1,)
            return True
        else:
            return False

    def go_right(self):
        """
        Move from before current item to after,
        or from after current item to before next item at the same level.
        """
        if self.cursor_is_before:
            self.set_cursor_after()
            return

        parent = self.parent_of_current_item
        if parent:
            idx = self.current_idx
            if idx < len(parent) - 1:
                self.cursor_address = (self.cursor_address[:-1] +
                                       (idx + 1,))
                self.set_cursor_before()
                return True

        return False

    def go_left(self):

        if self.cursor_is_after:
            self.set_cursor_before()
            return

        idx = self.current_idx
        if idx and idx > 0:
            self.cursor_address = (self.cursor_address[:-1] +
                                   (idx - 1,))
            self.set_cursor_after()
            return True

        return False

    # def decrease_through_identical_positions(self):
    #     """
    #     Change position from before an item to after the previous item at the
    #     same level, unless the current item is first at its level.
    #     """
    #
    #     # if self.cursor_is_after or self.current_idx == 0:  # Nothing to do
    #     #     return
    #
    #     # if self.current_item.is_formatter() or self.cursor_is_before:
    #     #     success = self.go_left()
    #     #     if success:
    #     #         self.decrease_through_identical_positions()
    #
    #     if self.cursor_is_after and not self.current_item.is_formatter():
    #         return
    #     if self.is_at_beginning():
    #         return
    #
    #     parent = self.parent_of_current_item
    #     if not parent:
    #         return
    #
    #     first_children = parent[:self.current_idx]
    #     if not all(child.is_formatter() for child in first_children):
    #         success = self.go_left()
    #         if success:
    #             self.decrease_through_identical_positions()

    # def increase_through_identical_positions(self):
    #     """
    #     Change position from before an item to after the previous item at the
    #     same level, unless the current item is first at its level.
    #     """
    #
    #     if self.current_item.is_formatter() or self.cursor_is_after:
    #         success = self.go_right()
    #         if success:
    #             self.increase_through_identical_positions()

    # def go_to_address(self, address: tuple, set_cursor_after=None,
    #                   set_marked=True):
    #     self.cursor_address = address
    #     if set_cursor_after is not None:
    #         self.set_cursor_after(set_cursor_after)
    #     if set_marked:
    #         self.set_marked_element(True)

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

        self.debug()

    def go_to_beginning(self, set_marked=True):
        # self.set_marked_element(False)
        self.cursor_address = tuple()
        self.set_cursor_before()

        if set_marked:
            self.set_marked_element(True)

        self.debug()

    def dont_wanna_park_at_current_item(self):
        """
        True if current_item is a reasonable position to stand at.
        """

        item = self.current_item
        test1 = any((item.is_formatter(), item.is_format_parenthesis(),
                    item.is_marker()))
        type_ = type(self.current_math_object)
        test2 = str(type_).endswith(".MarkedMetavar'>")
        return test1 or not test2

    def minimal_increase_pos(self):
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

    # @staticmethod
    # def equal_up_to_single_list(item1, item2):
    #     """
    #     Return True if item1 == [item2], or vice versa; or more generally if
    #     item 2 is the only non formatter term of the list.
    #     """
    #
    #     # if isinstance(item1, list):
    #     #     if len(item1) == 1 and item1[0] == item2:
    #     #         return True
    #     # elif isinstance(item2, list):
    #     #     if len(item2) == 1 and item2[0] == item1:
    #     #         return True
    #
    #     test1 = item1.significant_items() == [item2]
    #     test2 = item2.significant_items() == [item1]
    #     return test1 or test2

    def increase_pos(self, set_marked=True):

        # Adjust position (free move, both positions are considered identical)
        # self.increase_through_identical_positions()

        # FIXME: replace current_math_object by current_item?
        # current_mo, before = self.current_math_object, self.cursor_is_before
        current_mo, before = self.current_math_object, self.cursor_is_before
        new_mo, new_before = current_mo, before
        # new_item = self.current_item
        while ((not self.is_at_end()) and
               (self.dont_wanna_park_at_current_item()
                or (current_mo, before) == (new_mo, new_before))):
            self.minimal_increase_pos()
            new_mo = self.current_math_object
            # new_item = self.current_item
            new_before = self.cursor_is_before

        if set_marked:
            self.set_marked_element(True)

        self.debug()

    def minimal_decrease_pos(self):
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

    def decrease_pos(self, set_marked=True):

        # current_mo, before = self.current_math_object, self.cursor_is_before
        current_mo, before = self.current_math_object, self.cursor_is_before
        new_mo, new_before = current_mo, before
        # new_item = self.current_item
        # while ((not self.is_at_beginning()) and
        #        (new_item.is_formatter() or new_item.is_format_parenthesis()
        #        or new_item.is_marker()
        #         or (current_mo, before) == (new_mo, new_before)
        #        )):
        while ((not self.is_at_beginning()) and
               (self.dont_wanna_park_at_current_item()
                or (current_mo, before) == (new_mo, new_before))):
            self.minimal_decrease_pos()
            new_mo = self.current_math_object
            # new_item = self.current_item
            new_before = self.cursor_is_before

        # Adjust position (free move)
        # self.decrease_through_identical_positions()

        if set_marked:
            self.set_marked_element(True)

        self.debug()

    def fast_increase(self, set_marked=True):
        """
        Increase pos until cursor pos in the linear order has actually
        changed (and not only pos in the tree).
        """

        current_item = self.current_item
        while self.current_item == current_item and not self.is_at_end():
            self.minimal_increase_pos()

        if set_marked:
            self.set_marked_element(True)

        self.debug()

    def fast_decrease(self, set_marked=True):
        """
        Decrease pos until cursor pos in the linear order has actually
        changed (and not only pos in the tree).
        """

        current_item = self.current_item
        while self.current_item == current_item and not self.is_at_beginning():
            self.minimal_decrease_pos()

        if set_marked:
            self.set_marked_element(True)

        self.debug()




