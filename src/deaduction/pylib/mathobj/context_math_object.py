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
from copy import copy

# from deaduction.pylib.math_display import TO_BE_EXPANDED
from deaduction.pylib.mathobj.math_object   import MathObject
from deaduction.pylib.mathobj.give_name import name_single_bound_var

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
        # log.debug(f"Creating ContextMathPObject {self.to_display()},")
                  # f"dummy vars = "
                  # f"{[var.to_display() for var in self.bound_vars]}")

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

    def expanded_latex_shape(self, text_depth=0):
        display = super().expanded_latex_shape(text_depth)
        # FIXME: settle applied properties attribute
        # if self.has_been_applied_in_the_proof:
        #     display = ['@applied_property', display]
        return display

    @property
    def identifier(self):
        return self.info.get("id")

    # @property
    # def expanded_version(self):
    #     """
    #     Return an expanded version if it exists, or None.
    #     """
    #     if not self._expanded_version:
    #         if self.is_sequence():
    #             self._expanded_version = self.__expanded_sequence()
    #         elif self.is_set_family():
    #             self._expanded_version = self.__expanded_set_family()
    #
    #     return self._expanded_version
    #
    # def __raw_version(self):
    #     """
    #     Return a new MathObject which is a copy of self except that the
    #     math_type's node is prefixed by "RAW_".
    #     """
    #     math_type = self.math_type
    #     raw_node = "RAW_" + math_type.node
    #     raw_math_type = MathObject(node=raw_node,
    #                                info=copy(math_type.info),
    #                                children=math_type.children,
    #                                math_type=math_type.math_type)
    #     raw_self = MathObject(node="LOCAL_CONSTANT",
    #                           info=copy(self.info),
    #                           children=self.children,
    #                           math_type=raw_math_type)
    #     return raw_self
    #
    # def __expanded_sequence(self):
    #     """
    #     Take a ContextMathObject of type "SEQUENCE",
    #     (whose display would be, say , "u")
    #     and return a new MathObject whose display will be
    #     "(u_n)_{n in N}".
    #     NB: display of EXPANDED_SEQUENCE will be as
    #     (r"(", 0, ('_', 1), ')', ('_', 1, r"\in_symbol", 2))
    #     """
    #
    #     # We have to change math_type in raw_sequence,
    #     # otherwise we will get infinite recursion, i.e.
    #     # the 'u' in '(u_n)_{n in N}' will be replaced by '(u_n)_{n in N}'...
    #     math_type = self.math_type
    #     raw_sequence = self.__raw_version()
    #     bound_var_type = math_type.children[0]
    #     bound_var = MathObject.new_bound_var(bound_var_type)
    #     name_single_bound_var(bound_var)
    #     # type first, like for quantifiers
    #     children = [bound_var_type, bound_var, raw_sequence]
    #
    #     expanded_sequence = ContextMathObject(node="EXPANDED_SEQUENCE",
    #                                           info=copy(self.info),
    #                                           children=children,
    #                                           math_type=math_type,
    #                                           bound_vars=[])
    #     # NB: "bound_vars=[]" is a trick to hide the bound var from above
    #     # so that it will not be part of the naming game. Its name is
    #     # independent of the context.
    #
    #     return expanded_sequence
    #
    # def __expanded_set_family(self):
    #     """
    #     Take a ContextMathObject of type "SEQUENCE",
    #     (whose display would be, say , "E")
    #     and return a new MathObject whose display will be like
    #     "{E_i, i in I}". See __expand_sequence for more details.
    #     """
    #
    #     math_type = self.math_type
    #     raw_set_family = self.__raw_version()
    #
    #     bound_var_type = math_type.children[0]
    #     bound_var = MathObject.new_bound_var(bound_var_type)
    #     name_single_bound_var(bound_var)
    #     # type first, like for quantifiers
    #     children = [bound_var_type, bound_var, raw_set_family]
    #
    #     expanded_family = ContextMathObject(node="EXPANDED_SET_FAMILY",
    #                                         info=copy(self.info),
    #                                         children=children,
    #                                         math_type=math_type,
    #                                         bound_vars=[])
    #
    #     return expanded_family

