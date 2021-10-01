"""
# context_math_object.py : subclass MathObject for objects in the context #

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 08 2021 (creation)
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


from typing import Any
import logging
import deaduction.pylib.logger as logger

from deaduction.pylib.mathobj.MathObject   import MathObject
from deaduction.pylib.mathobj.html_display import html_display
from deaduction.pylib.mathobj.utf8_display import utf8_display

from deaduction.pylib.mathobj.display_math import (recursive_display,
                                                   latex_to_utf8,
                                                   shallow_latex_to_text)

log = logging.getLogger(__name__)
global _

class ContextMathObject(MathObject):
    """
    This class subclasses MathObject for objects of the context.
    At a given moment of a proof, the list of instances, as recorded in
    self.list_, is exactly the list of MathObjects in the current context.
    This list is useful for naming dummy vars.

    Attributes allow to keep track of some additional information.
    """
    list_: [Any] = []  # List of all ContextMathObject in the current context
    is_new: bool  # True if self was not present in previous context
    is_modified: bool  # True if self is modified from previous context
    is_hidden: bool  # True if self should not be dispplayed in ui
    has_been_applied_in_the_proof: bool

    def __init__(self, node, info, children, bound_vars, math_type):
        super().__init__(node, info, children, bound_vars, math_type)
        ContextMathObject.list_.append(self)

        # Tags
        self.is_new = False
        self.is_modified = False
        self.has_been_applied_in_proof = False  # TODO: implement
        self.is_hidden = False

        log.debug(f"Creating ContextMathPObject {self.to_display()},"
                  f"dummy vars = "
                  f"{[var.to_display() for var in self.bound_vars]}")

    @classmethod
    def whose_math_type_is(cls, math_type: MathObject):
        """
        Return the list of current ContextMathObjects with given math_type.
        """
        math_objects = [mo for mo in cls.list_ if mo.math_type == math_type]
        return math_objects

    def copy_tags(self, other):
        self.has_been_applied_in_proof = other.has_been_applied_in_proof
        self.is_hidden = other.is_hidden

    def raw_latex_shape_of_math_type(self):
        ########################################################
        # Special math_types for which display is not the same #
        ########################################################
        math_type = self.math_type
        if hasattr(math_type, 'math_type') \
                and hasattr(math_type.math_type, 'node') \
                and math_type.math_type.node == "TYPE":
            name = math_type.info["name"]
            raw_shape = [_("an element of") + " ", name]
            # The "an" is to be removed fo short display
        elif hasattr(math_type, 'node') and math_type.node == "SET":
            raw_shape = [_("a subset of") + " ", 0]
            # Idem
        elif math_type.node == "SEQUENCE":
            raw_shape = [_("a sequence in") + " ", 1]
        elif math_type.node == "SET_FAMILY":
            raw_shape = [_("a family of subsets of") + " ", 1]
        else:  # Generic case: usual shape from math_object
            raw_shape = math_type.raw_latex_shape()

        return raw_shape

    def expanded_latex_shape(self):
        display = super().expanded_latex_shape()
        # FIXME: settle applied properties attribute
        # if self.has_been_applied_in_the_proof:
        #     display = ['@applied_property', display]
        return display

    def math_type_to_display(self, format_="html", text_depth=0) -> str:
        """
        cf MathObject.to_display
        """
        raw_shape = self.raw_latex_shape_of_math_type()
        abstract_string = recursive_display(self.math_type,
                                            raw_display=raw_shape)
        # Replace some symbol by plain text:
        display = shallow_latex_to_text(abstract_string, text_depth)
        # Replace latex macro by utf8:
        if format_ in ('utf8', 'html'):
            display = latex_to_utf8(display)
        if format_ == 'html':
            display = html_display(display)
        elif format_ == 'utf8':
            display = utf8_display(display)
        log.debug(f"{self.old_to_display()} -> {display}")

        return display

