"""
marked_pattern_math_objects.py : provide the MarkedPatternMathObject class.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 06 2023 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2023 the d∃∀duction team

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

from copy import copy

if __name__ == '__main__':
    from deaduction.dui.__main__ import language_check
    language_check()

from deaduction.pylib.mathobj import MathObject
from deaduction.pylib.pattern_math_obj import PatternMathObject, MetaVar
from deaduction.pylib.math_display import MathDisplay


class MarkedTree:
    """
    A tree with zero or one marked node. This is a mixin to build MathObjects
    with a marked node, which may be thought of as some sort of cursor.
    mark_first_mvar() should be called on creation of the tree (but not of
    every node, obviously).

    Every node in the tree is assumed to have a list of left and right
    children, which induces an infix order.
    """

    # Fixme: we need children as an attribute, but whose value is set by the
    # main class
    _children = []
    matched_math_object = None
    is_marked = False
    _has_marked_descendant = False
    # @classmethod
    # def from_pattern_math_object(cls, pmo):
    #     marked_children = [cls.from_pattern_math_object(child)
    #                        for child in pmo.children]
    #     marked_pmo = cls(pmo.node, pmo.info, marked_children,
    #                      copy(pmo.math_type), pmo.imperative_matching)
    #     return marked_pmo

    def __init__(self, children=None, is_marked=False):
        # Fixme: useless?
        if children:
            self._children = children
        self.is_marked = is_marked

    # FIXME
    @property
    def children(self):
        """
        Fake children, this should be overriden by all subclasses.
        """
        return []
    # @property
    # def children(self):
    #     if self.is_metavar() and self.matched_math_object:
    #         return self.matched_math_object.children
    #     else:
    #         return self._children

    @property
    def left_children(self):
        return []

    @property
    def right_children(self):
        return []

    def is_metavar(self):
        pass

    @property
    def is_matched(self):
        return bool(self.matched_math_object)

    def parent_of_marked_descendant(self):
        """
        Return the immediate parent of self.marked_descendant, if any.
        """
        for child in self.children:
            if child.is_marked:
                return self
            elif child.parent_of_marked_descendant():
                return child.parent_of_marked_descendant()

    def marked_descendant(self):
        """
        Return the marked descendant of self, if any.        
        """
        if self.is_marked:
            return self

        for child in self.children:
            marked_descendant = child.marked_descendant()
            if marked_descendant:
                self._has_marked_descendant = True
                return marked_descendant

    @property
    def has_marked_descendant(self) -> bool:
        if not self._has_marked_descendant:
            self._has_marked_descendant = bool(self.marked_descendant())

        return self._has_marked_descendant

    def index_child_with_marked_descendant(self):
        i = 0
        for child in self.children:
            if child.has_marked_descendant:
                return i
            i += 1

    def child_with_marked_descendant(self):
        i = self.index_child_with_marked_descendant()
        if i:
            return self.children[i]

    def mark(self):
        self.is_marked = True

    def unmark(self):
        """
        Unmark self's marked node.
        """
        if self.is_marked:
            self.is_marked = False
        else:
            child = self.child_with_marked_descendant()
            if child:
                child.unmark()

    # def first_infix_mvar(self, unmatched=True):
    #     """
    #     Return first (unmatched) mvar in the tree whose root is self, if any.
    #     """
    #
    #     # (1) Try left children:
    #     if self.left_children:
    #         child = self.left_children[0]
    #         mvar = child.first_infix_mvar(self, unmatched=unmatched)
    #         if mvar:
    #             return mvar
    #
    #     # (2) Try self:
    #     elif self.is_metavar() and not self.is_matched or not unmatched:
    #         return self
    #
    #     # (3) Try right children
    #     else:
    #         for child in self.right_children:
    #             mvar = child.first_infix_mvar(unmatched=unmatched)
    #             if mvar:
    #                 return mvar

    def infix_list(self):
        """
        Return the list of all nodes in self's tree in the infix order.
        """

        i_list = []
        for child in self.left_children:
            i_list.extend(child.infix_list())

        i_list.append(self)

        for child in self.right_children:
            i_list.extend(child.infix_list())

        return list(i_list)

    # def next_infix_mvar(self, unmatched=False):
    #     """
    #     Return first mvar in the tree under self and after self, if any. This
    #     uses the right children.
    #     """
    #
    #     # l_children = self.left_children
    #     r_children = self.right_children
    #     if not r_children:
    #         return None
    #     else:
    #         return r_children[0].first_infix_mvar(unmatched=unmatched)

    def move_right(self, unmatched=False):
        """
        Move the marked node to the next metavar in self if any. Return the 
        new marked metavar, or None.
        """

        i_list = self.infix_list()
        marked_mvar = self.marked_descendant()
        idx = i_list.index(marked_mvar)
        new_mvar = None

        if not unmatched:
            if idx < len(i_list) - 1:
                new_mvar = i_list[idx+1]
        else:
            while idx < len(i_list) - 1 and i_list[idx].is_matched:
                idx += 1
            if not i_list[idx].is_matched:
                new_mvar = i_list[idx]

        if new_mvar:
            marked_mvar.unmark()
            new_mvar.mark()
            return new_mvar

        # new_marked_mvar = None
        # if not self.has_marked_descendant or not self.children:
        #     return None
        #
        # # (1) Search new mvar in child with marked descendant
        # elif self.is_marked:
        #     gmarked_child = self
        #     marked_index = -1  # FIXME: only right children
        # else:
        #     marked_index = self.index_child_with_marked_descendant()
        #     gmarked_child = self.children[marked_index]
        #     new_marked_mvar = gmarked_child.move_right()
        #
        # # (2) If failed, search new mvar in next children
        # if not new_marked_mvar:
        #     for child in self.children[marked_index+1:]:
        #         new_marked_mvar = child.first_infix_mvar(unmatched=False)
        #         if new_marked_mvar:
        #             break
        #
        # # (3) Success?
        # if new_marked_mvar:
        #     gmarked_child.unmark()
        #     new_marked_mvar.mark()
        #     return new_marked_mvar

    def move_left(self):
        """
        Move the marked node to the previous metavar.
        """

        i_list = self.infix_list()
        marked_mvar = self.marked_descendant()
        idx = i_list.index(marked_mvar)

        if idx > 0:
            new_mvar = i_list[idx - 1]
            marked_mvar.unmark()
            new_mvar.mark()
            return new_mvar

        # # Case 1: self has a marked child?
        # # 1.1: in left_children? Return previous child, if any.
        # previous_child = None
        # for child in self.left_children:
        #     if child.is_marked:
        #         if isinstance(previous_child, MarkedTree):
        #             previous_child.mark()
        #             child.unmark()
        #             return previous_child
        #         else:
        #             return None
        #     previous_child = child
        # # 1.1: in right_children? Return previous child, or self.
        # previous_child = None
        # for child in self.right_children:
        #     if child.is_marked:
        #         child.unmark()
        #         if isinstance(previous_child, MarkedTree):
        #             previous_child.mark()
        #             return previous_child
        #         else:  # First right child ! return self
        #             self.mark()
        #             return self
        #     previous_child = child

        # 2: not among children: try down.

    def move_up(self):
        if self.is_marked:
            return None
        elif self.has_marked_descendant:
            marked_child = self.child_with_marked_descendant()
            if marked_child:
                if marked_child.is_marked:
                    marked_child.unmark()
                    self.mark()
                    return self
                else:
                    return marked_child.move_up()

    def move_right_to_next_unmatched(self):
        """
        Move the marked node to the next unmatched mvar, if any.
        """

        return self.move_right(unmatched=True)
        # mvar = self
        # while mvar and mvar.is_matched:
        #     mvar = self.move_right()
        # return mvar

    def move_after_insert(self):
        """
        This method is supposed to be called just after an insertion involving
        the marked node. It tries to move the marked node down to the first
        unmatched mvar, or else to the next unmatched mvar. It returns the
        new marked mvar if any.
        """

        # (1) Try marked_mvar:
        marked_mvar = self.marked_descendant()
        if marked_mvar and not marked_mvar.is_matched:
            return marked_mvar

        # (2) Try ALL children of marked mvar:
        for child in marked_mvar.children:
            if child.is_metavar and not child.is_matched:
                marked_mvar.unmark()
                child.mark()
                return child

        # (3) Move right
        return self.move_right_to_next_unmatched()


# decreasing precedence
priorities = [
              {'MULT', 'DIV'},
              {'SUM', 'DIFFERENCE'},
              {'PROP_EQUAL', 'PROP_<', 'PROP_>', 'PROP_≤', 'PROP_≥'},
              {'PARENTHESES'}
              ]


def priority(self: str, other: str) -> str:
    """
    Return '=' if self and other have the same priority level,
    '>' or '<' if they have distinct comparable priority levels,
    None otherwise.
    """
    self_found = False
    other_found = False
    for nodes in priorities:
        if self in nodes:
            if other_found:
                return '<'
            if other in nodes:
                return '='
            else:
                self_found = True
        elif other in nodes:
            if self_found:
                return '>'
            else:
                other_found = True


class MarkedPatternMathObject(PatternMathObject, MarkedTree):
    """
    A PatternMathObject with a marked node.
    """

    @classmethod
    def from_pattern_math_object(cls, pmo: PatternMathObject):
        """
        Create a MarkedPatternMathObject from a PatternMathObject,
        or a MarkedMetavar if pmo is a metavar.
        """

        if isinstance(pmo, MetaVar):
            return MarkedMetavar.from_mvar(pmo)

        children = [MarkedMetavar.from_mvar(child, parent=pmo)
                    if isinstance(child, MetaVar)
                    else cls.from_pattern_math_object(child)
                    for child in pmo.children]
        # NO_MATH_TYPE should be kept identical
        marked_type = (pmo.math_type if pmo.math_type.is_no_math_type()
                       else copy(pmo.math_type))
        marked_pmo = cls(pmo.node, pmo.info, children,
                         marked_type, pmo.imperative_matching)
        return marked_pmo

    @classmethod
    def from_string(cls, s: str, metavars=None):
        pmo = super().from_string(s, metavars)
        mpmo = cls.from_pattern_math_object(pmo)
        return mpmo

    def insert_at_marked_mvar(self, pmo: PatternMathObject) -> bool:
        """
        Try to insert math_object in self's marked mvar. Return True in case
        of success, False otherwise. If the marked mvar has a new unmatched
        mvar, mark it.
        """
        marked_mvar: MarkedMetavar = self.marked_descendant()
        if not marked_mvar:
            return False

        parent = self.parent_of_marked_descendant()
        return marked_mvar.insert(pmo, parent)

    def delete(self):
        """
        'Delete' current marked metavar, i.e. remove matched_math_object.
        """
        return self.marked_descendant().delete()


class MarkedMetavar(MetaVar, MarkedPatternMathObject):
    """
    A Metavar which can be marked.
    """

    def __repr__(self):
        rep = super().__repr__()
        if self.is_marked:
            rep = '--> ' + rep
        return rep

    @classmethod
    def deep_copy(cls, self):
        new_mvar: MarkedMetavar = super().deep_copy(self)
        if self.is_marked:
            new_mvar.mark()
        return new_mvar

    @property
    def node(self):
        """
        Override super().node.
        """
        node = (self.matched_math_object._node
                if self.matched_math_object else self._node)
        return node

    @property
    def info(self):
        """
        Override super().children in case self has a matched_math_object.
        """
        info = (self.matched_math_object._info
                if self.matched_math_object else self._info)
        return info

    @property
    def children(self):
        """
        Override super().children in case self has a matched_math_object.
        """
        children = (self.matched_math_object._children
                    if self.matched_math_object else self._children)
        return children

    @property
    def left_children(self):
        node = self.node
        l_nb, r_nb = MathDisplay.left_right_children(node)
        l_children = [self.children[i] for i in l_nb]
        # r_children = [self.children[i] for i in r_nb]
        return l_children

    @property
    def right_children(self):
        node = self.node
        l_nb, r_nb = MathDisplay.left_right_children(node)
        # l_children = [self.children[i] for i in l_nb]
        r_children = [self.children[i] for i in r_nb]
        return r_children

    @classmethod
    def from_mvar(cls, mvar: MetaVar, parent=None):
        marked_mvar = cls(math_type=mvar.math_type)
        marked_mvar.parent = parent
        marked_mvar.matched_math_object = mvar.matched_math_object
        return marked_mvar

    def insert_over_matched_math_object(self, pmo: PatternMathObject,
                                        parent=None) -> bool:
        """
        See next method's doc.
        """

        # (1) Special cases
        self_object = self.matched_math_object
        if self_object.math_type.is_number() or self_object.node == 'NUMBER':
            value = str(self_object.value)
            if pmo.math_type.is_number() or pmo.node == 'NUMBER':
                units = str(pmo.value)
                self_object.value = value + units
                return True
            elif pmo.node == 'POINT':
                if '.' not in value:
                    self_object.value = value + '.'
                    return True
                else:
                    return False

        # (2) If self_object and pmo both have children and have the same
        #  nb of children, try to replace.
        # if self_object.children and \
        #         len(self_object.children) == len(pmo.children):
        #     tests = [self.match(pmo)]
        #     for child, child_mvar in zip(self_object.children, pmo.children):
        #         if isinstance(child_mvar, MetaVar):
        #             tests.append(child_mvar.match(child))
        #     if all(tests):
        #         self.matched_math_object = pmo
        #         for child, child_mvar in zip(self_object.children,
        #                                      pmo.children):
        #             child_mvar.matched_math_object = child
        #         return True

        # (3) Try to insert
        mvar = pmo.first_mvar()
        if not mvar:
            return False

        # (3a) Check parent priority, and maybe insert at parent
        elif parent and hasattr(parent, "insert_over_matched_math_object"):
            # Compare priority of pmo and parent
            self_node = parent.node
            other_node = pmo.node
            prior = priority(self_node, other_node)
            if prior in ('=', '>'):
                success = parent.insert_over_matched_math_object(pmo)
                if success:
                    return True

        # (3b) Insert at self
        match = mvar.match(self.matched_math_object)
        if match:
            mvar.matched_math_object = self.matched_math_object
            self.matched_math_object = pmo
            return True
        else:
            return False

    def insert(self, math_object: PatternMathObject, parent=None) -> bool:
        """
        Try to insert math_object in self. Return True in case of success,
        False otherwise.
        - If self does not have matched_math_object, just check that
        math_types match (to be improved: try automatic matching, e.g.
            f --> f(.) );
        - Otherwise, try to substitute matched_math_object with math_object
        by matching the matched_math_obj with the first mvar of math_object
        (to be improved: try automatic matching?)
        """

        # Crucial: deepcopy math_object!!
        math_object = math_object.deep_copy(math_object)

        if not self.matched_math_object:
            match = self.match(math_object)
            if match:
                self.matched_math_object = math_object
                return True
            else:
                # FIXME: insert an MVAR with math_object as first child?
                return False

        else:
            return self.insert_over_matched_math_object(math_object,
                                                        parent=parent)

    def delete(self):
        """
        FIXME: what is the desired behavior?
        """
        if self.matched_math_object:
            self.matched_math_object = None
            if isinstance(self.math_type, MetaVar):
                self.math_type.matched_math_object = None
            return True

    def to_display(self, format_="html", text=False,
                   use_color=True, bf=False, is_type=False,
                   used_in_proof=False):
        mmo = self.matched_math_object
        if mmo:
            display = mmo.to_display(format_=format_, text=text,
                                     use_color=use_color, bf=bf,
                                     is_type=is_type)
        else:
            display = MathObject.to_display(self, format_=format_, text=text,
                                            use_color=use_color, bf=bf,
                                            is_type=is_type)

        return display

    @classmethod
    def mark_cursor(cls, yes=True):
        MathDisplay.mark_cursor = yes

    def latex_shape(self, is_type=False, text=False, lean_format=False):
        """
        Modify the latex shape to mark the main symbol, if self.is_marked.
        """
        shape = super().latex_shape(is_type=False,
                                    text=False,
                                    lean_format=False)
        if not self.is_marked:
            return shape

        marked_shape = MathDisplay.marked_latex_shape(self.node, shape)
        return marked_shape


# def marked(item):
#     """
#     This method add a tag to the main symbol of a tuple representing a latex
#     shape.
#     FIXME: criterium and marking to be modified.
#     """
#     marked_item = ('*' + item if isinstance(item, str)
#                    else item)
#     return marked_item


if __name__ == "__main__":
    s1 = "SUM(?1 , NUMBER/value=1)"
    # pmo = PatternMathObject.from_string(s1)
    # mpmo1 = MarkedPatternMathObject.from_pattern_math_object(pmo)
    mpmo = MarkedPatternMathObject.from_string(s1)
    mpmo.mark_first_mvar()
    child_ = mpmo.children[1]
    print(mpmo.to_display(format_='utf8'))
