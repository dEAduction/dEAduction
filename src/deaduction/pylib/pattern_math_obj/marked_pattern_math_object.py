"""
marked_pattern_math_objects.py : provide the MarkedPatternMathObject class.

The trickiest thing here is an insertion algorithm in an expression tree.
In such a tree, every node has an ordered list of left and right children.
Here this list is induced by the latex_shape, with a choice of a main symbol.

Two cases:
(1) insertion at a non assigned metavar.
(2) insertion after a matched metavar.
 In any case, after a successful insertion, the marked node should
    - move to the first non assigned metavar of the inserted object,
    if any,
    - otherwise, stay in place. The cursor will indicate the place just after
    the (main symbol of) the inserted object.

Case (1) is easy: just check that types match.

Case (2) splits into the following sub-cases. Let (MO) denotes the matched
object after which the insertion takes place.

    (2a) The new node (NN) has a metavar left of its main symbol. Let (MVL)
    be the first metavar left of (NN). If (MVL) matches (MO), then (NN) be
    inserted at (MO)'s place, with (MO) becoming (MVL)'s matched object.
    Precedence rule, involving MO's father, should also be checked here (?).
    If the insertion fails, then it should be tried on the next place in the
    tree path from the mvar to the next node in the infix order (?).

    (2b) If (NN) has no left child, or if (2a) fails, then automatic insertion
    are tried: operators in the automatic list are tried one by one, until one
    matches (MO) as its left child and (NN) as its right child.
    Automatic operators includes
    f, x --> f(x)
    f, A --> f(A)
    f, g --> f circ g ?
    1, 2 --> INT (1, 2)
    ...

    (2c) If (2a) and (2b) fails, then the symmetric right insertion trials
    should be performed.

Then precedence rules must be checked: if the edge between (NN) and its
parent do not bind dy the rule, then a precedence move must be performed.
This operation is repeated until the precedence rules are satisfied.


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
import logging

if __name__ == '__main__':
    from deaduction.dui.__main__ import language_check
    language_check()

from deaduction.pylib.mathobj import MathObject
from deaduction.pylib.pattern_math_obj import PatternMathObject, MetaVar
from deaduction.pylib.math_display import MathDisplay

log = logging.getLogger(__name__)


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

    # def parent_of_marked_descendant(self):
    #     """
    #     Return the immediate parent of self.marked_descendant, if any.
    #     """
    #     for child in self.children:
    #         if child.is_marked:
    #             return self
    #         elif child.parent_of_marked_descendant():
    #             return child.parent_of_marked_descendant()

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

    def left_descendants(self, only_unmatched=False):
        """
        Return the list of descendants of self.left_children, in infix order.
        """
        l_list = []
        for child in self.left_children:
            l_list.extend(child.infix_list(only_unmatched=only_unmatched))
        return l_list

    def right_descendants(self, only_unmatched=False):
        """
        Return the list of descendants of self.right_children, in infix
        order.
        """
        r_list = []
        for child in self.right_children:
            r_list.extend(child.infix_list(only_unmatched=only_unmatched))
        return r_list

    def infix_list(self, only_unmatched=False):
        """
        Return the list of all nodes in self's tree in the infix order.
        """

        maybe_self = [] if self.is_matched and only_unmatched else [self]

        i_list = (self.left_descendants(only_unmatched=only_unmatched)
                  + maybe_self
                  + self.right_descendants(only_unmatched=only_unmatched))

        return list(i_list)

    def left_mvar(self, only_unmatched=False):
        # TODO
        pass


    # def marked_infix_idx(self):
    #     if self.marked_descendant():
    #         return self.infix_list().index(self.marked_descendant())

    def right_of_marked_element(self, other):
        """
        True iff other is right of marked element in self.infix list.
        """
        l = self.infix_list()
        if self.marked_descendant():
            m_idx = l.index(self.marked_descendant())
            o_idx = l.index(other)
            return m_idx < o_idx

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

    def next_from_marked(self, unmatched=False):
        """
        Return the next node from marked descendant in the infix order.
        """
        i_list = self.infix_list()
        marked_mvar = self.marked_descendant()
        if not marked_mvar:
            return None

        idx = i_list.index(marked_mvar)
        next_mvar = None
        if not unmatched:
            if idx < len(i_list) - 1:
                next_mvar = i_list[idx + 1]
        else:
            while idx < len(i_list) - 1 and i_list[idx].is_matched:
                idx += 1
            if not i_list[idx].is_matched:
                next_mvar = i_list[idx]

        return next_mvar

    def move_right(self, unmatched=False):
        """
        Move the marked node to the next metavar in self if any. Return the 
        new marked metavar, or None.
        """

        next_mvar = self.next_from_marked(unmatched=unmatched)
        marked_mvar = self.marked_descendant()
        if marked_mvar and next_mvar:
            marked_mvar.unmark()
            next_mvar.mark()
            return next_mvar

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

    def lineage_from(self, descendant) -> []:
        if self is descendant:
            return [self]
        else:
            for child in self.children:
                child_lineage = child.lineage_from(descendant)
                if child_lineage:
                    return child_lineage + [self]

    def marked_lineage_from(self) -> []:
        if self.is_marked:
            return [self]
        else:
            for child in self.children:
                child_lineage = child.marked_lineage_from()
                if child_lineage:
                    return child_lineage + [self]

    def path_from_marked_to_next(self) -> ():
        """
        Return the two components of the path from the unique marked
        descendant to the next node in the infix order, more precisely both
        upward paths from node to the common ancestor. The common ancestor is
        included in both paths.
        """
        marked_l = self.marked_lineage_from()
        if not marked_l:
            return [], []
        next_ = self.next_from_marked()
        if not next_:
            path = marked_l, [marked_l[-1]]
        else:
            next_l = self.lineage_from(next_)
            common_ancestor = self  # Useless
            while next_l and marked_l and next_l[-1] is marked_l[-1]:
                common_ancestor = marked_l.pop()
                next_l.pop()
            # next_l.reverse()
            path = marked_l + [common_ancestor],  next_l + [common_ancestor]

        return path


# decreasing precedence
priorities = [
              {'MULT', 'DIV'},
              {'SUM', 'DIFFERENCE'},
              {'PROP_EQUAL', 'PROP_<', 'PROP_>', 'PROP_≤', 'PROP_≥'},
              {'CLOSE_PARENTHESIS', 'OPEN_PARENTHESIS'}
              ]


def priority(self: str, other: str) -> str:
    """
    Return '=' if self and other have the same priority level,
    '>' or '<' if they have distinct comparable priority levels,
    None otherwise.
    """

    if not self or not other:
        return None
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


def in_this_order(self, other, list_):
    """
    Return True if self and other are in this order in list_, False if they
    are in the reverse order.
    """
    yes = None
    both_in = False
    for item in list_:
        if item is self:
            if yes is None:  # self is first
                yes = True
            elif yes is False:  # self is second
                both_in = True
        elif item is other:
            if yes:  # other is second
                both_in = True
            else:  # other is first
                yes = False

    if both_in:
        return yes


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

    # def insert_at_marked_mvar(self, pmo: PatternMathObject) -> bool:
    #     """
    #     Try to insert math_object in self's marked mvar. Return True in case
    #     of success, False otherwise. If the marked mvar has a new unmatched
    #     mvar, mark it.
    #     """
    #     marked_mvar: MarkedMetavar = self.marked_descendant()
    #     if not marked_mvar:
    #         return False
    #
    #     # parent = self.parent_of_marked_descendant()
    #     # return marked_mvar.insert(pmo, parent)
    #
    #     # todo: send lineage
    #     marked_lineage = self.marked_lineage_from()
    #     marked_mvar: MarkedMetavar = marked_lineage.pop()
    #     return marked_mvar.insert(pmo, marked_lineage)

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

    def clear_all_matchings(self):
        for mvar in self.left_descendants() + self.right_descendants():
            mvar.clear_matching()

    def can_be_inserted_at(self, mvar, new_pmo, left_path, right_path,
                           left=True, do_insert=True):
        """
        Try to insert pmo at mvar.
        mvar is either a term of left_path or a term of right_path.
        In the first case it is not the last term, in the second not the first.
        """

        # Beware that match() method do assign the matched object.
        # do_insert=False not implemented

        log.debug(f"Trying to insert {new_pmo} at {mvar}")

        # First test: if mvar.is_matched, its matched object must match
        #  a descendant of new_pmo, on the adequate side.
        if left:
            idx = left_path.index(mvar)
            parent_mvar = left_path[idx+1] if idx < len(left_path) - 1 else None
        else:
            idx = right_path.index(mvar)  # idx always >0
            parent_mvar = left_path[idx-1]

        # Priority test (no priority test for common ancestor)
        if parent_mvar:
            priority_test = (priority(parent_mvar.node, new_pmo.node)
                             not in ('=', '>'))
            log.debug(f"Priority test: {parent_mvar} {priority_test} {new_pmo}")
            if not priority_test:
                return False

        if mvar.is_matched:
            log.debug(f"Trying to match {mvar.matched_math_object}")
            match_child_test = False
            if left:
                for child_new_pmo in new_pmo.left_descendants(
                        only_unmatched=True):
                    log.debug(f"{child_new_pmo} match?")
                    if child_new_pmo.match(mvar.matched_math_object):
                        # NB: matched_math_object now assigned to child_new_pmo
                        match_child_test = True
                        break
            else:
                for child_new_pmo in new_pmo.right_descendants(
                        only_unmatched=True):
                    log.debug(f"{child_new_pmo} match?")
                    if child_new_pmo.match(mvar.matched_math_object):
                        match_child_test = True
                        break
            if not match_child_test:
                return False

        # Additional refactoring for common ancestor:
        # Some of its children may be at the wrong side of new_pmo in the
        # infix order
        if not parent_mvar and mvar.is_matched:  # (mvar is the common ancestor)
            dubious_children = mvar.matched_math_object.children

            if left:
                # mvar.matched_mo has been inserted on the left of new_pmo
                # move bad children of this to the right mvar of new_pmo,
                # trying successively all right descendant of new_pmo
                mvars = new_pmo.right_descendants(only_unmatched=True)
                bad_children = [child for child in dubious_children
                                if self.right_of_marked_element(child)]
                while bad_children:
                    child = bad_children.pop(0)
                    while mvars:
                        mvar = mvars.pop(0)
                        if mvar.match(child):  # Success for this child!
                            break
                    if not mvar.is_matched:  # last mvar did not match
                        return False
            else:
                mvars = new_pmo.left_descendants(only_unmatched=True)
                bad_children = [child for child in dubious_children
                                if not self.right_of_marked_element(child)]
                while bad_children:
                    child = bad_children.pop(0)
                    while mvars:
                        mvar = mvars.pop(0)
                        if mvar.match(child):  # Success for this child!
                            break
                    if not mvar.is_matched:  # last mvar did not match
                        return False

        # Last test: new_pmo match mvar?
        log.debug(f"Last test: {new_pmo} match {mvar}?")
        match_mvar_test = mvar.match(new_pmo)
        if not match_mvar_test:
            return False

        return True

    def insert(self, new_pmo: PatternMathObject) -> bool:
        """
        Try to insert pmo in self's tree, so that pmo is just after the
        marked node in the infix order.
        """

        left_path, right_path = self.path_from_marked_to_next()
        right_path.reverse()
        # tree = self.deep_copy(self)

        # TODO: successively call can_be_inserted(mvar, pmo)
        #  with mvar in left_path, then in right_path.reverse.
        # success = False
        # if len(left_path) == 1:
        # left_path.append(None)  # Artificially add a parent
        for left in (True, False):
            # Crucial: deepcopy pmo!!
            new_pmo_copy = MarkedPatternMathObject.deep_copy(new_pmo)
            for mvar in (left_path if left else right_path[1:]):
                success = self.can_be_inserted_at(mvar, new_pmo_copy,
                                                  left_path, right_path,
                                                  left)
                if success:
                    return True
                else:
                    new_pmo_copy.clear_all_matchings()

        # TODO: try at common ancestor (but we need its parent)

        # TODO: try automatic patterns

        # TODO: handle multiple patterns

    def delete(self):
        """
        'Delete' current marked metavar, i.e. remove matched_math_object.
        """
        return self.marked_descendant().delete()

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


class MarkedMetavar(MetaVar, MarkedPatternMathObject):
    """
    A Metavar which can be marked.
    """

    def __repr__(self):
        rep = super().__repr__()
        if self.is_marked:
            rep = '--> ' + rep
        return rep

    @property
    def matched_math_object(self):
        return self._matched_math_object

    @matched_math_object.setter
    def matched_math_object(self, math_object):
        self._matched_math_object = math_object

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

    @classmethod
    def from_mvar(cls, mvar: MetaVar, parent=None):
        marked_mvar = cls(math_type=mvar.math_type)
        marked_mvar.parent = parent
        marked_mvar.matched_math_object = mvar.matched_math_object
        return marked_mvar

    # def insert_over_matched_math_object(self, pmo: PatternMathObject,
    #                                     lineage=None) -> bool:
    #     """
    #     See next method's doc.
    #     """
    #
    #     # (1) Special cases
    #     self_object = self.matched_math_object
    #     if self_object.math_type.is_number() or self_object.node == 'NUMBER':
    #         value = str(self_object.value)
    #         if pmo.math_type.is_number() or pmo.node == 'NUMBER':
    #             units = str(pmo.value)
    #             self_object.value = value + units
    #             return True
    #         elif pmo.node == 'POINT':
    #             if '.' not in value:
    #                 self_object.value = value + '.'
    #                 return True
    #             else:
    #                 return False

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

        # # (3) Try to insert
        # mvar = pmo.first_mvar()
        # if not mvar:
        #     return False
        #
        # # (3a) Check parent priority, and maybe insert at parent
        # else:
        #     # FIXME: left or right children????
        #     if lineage:
        #         parent = lineage.pop()
        #         if hasattr(parent, "insert_over_matched_math_object"):
        #             # TODO: if not, try parent's parent
        #             # Compare priority of pmo and parent
        #             self_node = parent.node
        #             other_node = pmo.node
        #             prior = priority(self_node, other_node)
        #             if prior in ('=', '>'):
        #                 success = parent.insert_over_matched_math_object(pmo,
        #                                                                  lineage)
        #                 if success:
        #                     return True
        #
        # # (3b) Insert at self
        # match = mvar.match(self.matched_math_object)
        # if match:
        #     mvar.matched_math_object = self.matched_math_object
        #     self.matched_math_object = pmo
        #     return True
        # else:
        #     return False

    # def insert(self, math_object: PatternMathObject, lineage=None) -> bool:
    #     """
    #     Try to insert math_object in self. Return True in case of success,
    #     False otherwise.
    #     - If self does not have matched_math_object, just check that
    #     math_types match (to be improved: try automatic matching, e.g.
    #         f --> f(.) );
    #     - Otherwise, try to substitute matched_math_object with math_object
    #     by matching the matched_math_obj with the first mvar of math_object
    #     (to be improved: try automatic matching?)
    #     """
    #
    #     # Crucial: deepcopy math_object!!
    #     math_object = math_object.deep_copy(math_object)
    #
    #     if not self.matched_math_object:
    #         match = self.match(math_object)
    #         if match:
    #             self.matched_math_object = math_object
    #             return True
    #         else:
    #             # FIXME: insert an MVAR with math_object as first child?
    #             return False
    #
    #     else:
    #         return self.insert_over_matched_math_object(math_object, lineage)

    def delete(self):
        """
        FIXME: what is the desired behavior?
        """
        if self.matched_math_object:
            self.matched_math_object = None
            if isinstance(self.math_type, MetaVar):
                self.math_type.matched_math_object = None
            return True

    # def to_display(self, format_="html", text=False,
    #                use_color=True, bf=False, is_type=False,
    #                used_in_proof=False):
    #     # mmo = self.matched_math_object
    #     unmark = False
    #     mmo = None
    #     if mmo:
    #         assert isinstance(mmo, MarkedPatternMathObject)
    #         if self.is_marked and not mmo.is_marked:
    #             mmo.mark()
    #             unmark = True
    #         display = mmo.to_display(format_=format_, text=text,
    #                                  use_color=use_color, bf=bf,
    #                                  is_type=is_type)
    #         if unmark:
    #             mmo.unmark()
    #     else:
    #         display = MathObject.to_display(self, format_=format_, text=text,
    #                                         use_color=use_color, bf=bf,
    #                                         is_type=is_type)
    #
    #     return display

    # @classmethod
    # def mark_cursor(cls, yes=True):
    #     MathDisplay.mark_cursor = yes

    # def latex_shape(self, is_type=False, text=False, lean_format=False):
    #     """
    #     Modify the latex shape to mark the main symbol, if self.is_marked.
    #     """
    #     shape = super().latex_shape(is_type=False,
    #                                 text=False,
    #                                 lean_format=False)
    #     if not self.is_marked:
    #         return shape
    #
    #     marked_shape = MathDisplay.marked_latex_shape(self.node, shape)
    #     return marked_shape
    #

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
