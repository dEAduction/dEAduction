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


class MarkedTree:
    """
    A tree with zero or one marked node. This is a mixin to build MathObjects
    with a marked node, which may be thought of as some sort of cursor.
    mark_first_mvar() should be called on creation of the tree (but not of
    every node, obviously).
    """
    
    _children = []
    matched_math_object = None
    is_marked = False
    
    # @classmethod
    # def from_pattern_math_object(cls, pmo):
    #     marked_children = [cls.from_pattern_math_object(child)
    #                        for child in pmo.children]
    #     marked_pmo = cls(pmo.node, pmo.info, marked_children,
    #                      copy(pmo.math_type), pmo.imperative_matching)
    #     return marked_pmo

    def __init__(self, children=None, is_marked=False):
        if children:
            self._children = children
        self.is_marked = is_marked
        self._has_marked_descendant = False

    # FIXME
    # @property
    # def children(self):
    #     if self.is_metavar() and self.matched_math_object:
    #         return self.matched_math_object.children
    #     else:
    #         return self._children

    def is_metavar(self):
        pass

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
                return child

    @property
    def has_marked_descendant(self) -> bool:
        if not self._has_marked_descendant:
            self._has_marked_descendant = bool(self.marked_descendant())

        return self._has_marked_descendant

    def mark_first_mvar(self, unmatched=True):
        """
        Mark first (unmatched) mvar and return it. If self already has a marked
        descendant, just return it.
        """

        marked_descendant = self.marked_descendant()
        if marked_descendant:
            return marked_descendant

        elif self.is_metavar() and (not unmatched or
                                    not self.matched_math_object):
            self.is_marked = True
            return self
        
        else:
            for child in self.children:
                marked = child.mark_first_mvar(unmatched=unmatched)
                if marked:
                    return marked

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

    def has_mvar(self, unmatched=True):
        if self.is_metavar():
            return bool(self.matched_math_object)
        else:
            return any([child.has_mvar(unmatched) for child in self.children])
    
    def move_right(self, to_unmatched_mvar=True):
        """
        Move the marked node to the next metavar in self if any. Return the 
        new marked metavar, or None. If to_unmatched_mvar then the new marked
        mvar must be unmatched.
        """
        
        if not self.has_marked_descendant or not self.children:
            return None
        
        # (1) Search new mvar in child with marked descendant
        marked_index = self.index_child_with_marked_descendant()
        marked_child = self.children[marked_index]
        new_marked_mvar = marked_child.move_right()
        
        # (2) If failed, search new mvar in next children
        if not new_marked_mvar:
            for child in self.children[marked_index:]:
                new_marked_mvar = child.mark_first_mvar(unmatched=to_unmatched_mvar)
                if new_marked_mvar:
                    break

        # (3) Success?
        if new_marked_mvar:
            marked_child.unmark()
            new_marked_mvar.mark()
            return new_marked_mvar

    def move_left(self):
        pass

    def move_up(self):
        pass

    def move_down(self):
        pass

    # def insert(self, pmo):
    #     """
    #     Try to insert pmo as matched_math_object for the current marked node.
    #     """


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

        children = [MarkedMetavar.from_mvar(child) if isinstance(child, MetaVar)
                    else cls.from_pattern_math_object(child)
                    for child in pmo.children]
        marked_pmo = cls(pmo.node, pmo.info, children,
                         copy(pmo.math_type), pmo.imperative_matching)
        return marked_pmo

    @classmethod
    def from_string(cls, s: str, metavars=None):
        pmo = super().from_string(s, metavars)
        mpmo = cls.from_pattern_math_object(pmo)
        return mpmo

    def insert(self, pmo: PatternMathObject) -> bool:
        """
        Try to insert math_object in self's marked mvar. Return True in case
        of success, False otherwise. If the marked mvar has a new unmatched
        mvar, mark it.
        """
        marked_mvar = self.marked_descendant()
        if not marked_mvar:
            return False

        success = marked_mvar.insert(pmo)
        if not success:
            return False

        new_mvar = marked_mvar.first_mvar(unmatched=True)
        if new_mvar:
            self.unmark()
            new_mvar.mark()

        return True


class MarkedMetavar(MetaVar, MarkedTree):
    """
    A Metavar which can be marked.
    """

    @property
    def children(self):
        """
        Override super().children in case self has a matched_math_object.
        """
        children = (self.matched_math_object._children
                    if self.matched_math_object else self._children)
        return children

    @classmethod
    def from_mvar(cls, mvar: MetaVar):
        marked_mvar = cls(math_type=mvar.math_type)
        marked_mvar.matched_math_object = mvar.matched_math_object
        return marked_mvar

    def insert_over_matched_math_object(self, pmo: PatternMathObject) -> bool:
        """
        See next method's doc.
        """
        mvar = pmo.first_mvar()
        if not mvar:
            return False
        else:
            match = mvar.match(self.matched_math_object)
            if match:
                mvar.matched_math_object = self.matched_math_object
                self.matched_math_object = pmo
                return True
            else:
                return False

    def insert(self, math_object: PatternMathObject) -> bool:
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

        if not self.matched_math_object:
            match = self.match(math_object)
            if match:
                self.matched_math_object = math_object
                return True
            else:
                return False

        else:
            return self.insert_over_matched_math_object(math_object)

    def to_display(self, format_="html", text=False,
                   use_color=True, bf=False, is_type=False,
                   used_in_proof=False):
        display = MathObject.to_display(self, format_=format_, text=text,
                                        use_color=use_color, bf=bf,
                                        is_type=is_type)
        mmo = self.matched_math_object
        if mmo:
            display = mmo.to_display(self, format_=format_, text=text,
                                        use_color=use_color, bf=bf,
                                        is_type=is_type)
        if not self.is_marked:
            return '?=' + display
        else:
            return '??=' + display


if __name__ == "__main__":
    s1 = "SUM(?1 , NUMBER/value=1)"
    # pmo = PatternMathObject.from_string(s1)
    # mpmo1 = MarkedPatternMathObject.from_pattern_math_object(pmo)
    mpmo = MarkedPatternMathObject.from_string(s1)
    mpmo.mark_first_mvar()
    child_ = mpmo.children[1]
    print(mpmo.to_display(format_='utf8'))
