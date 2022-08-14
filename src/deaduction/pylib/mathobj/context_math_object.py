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
    is_new_: bool  # True if self was not present in previous context FIXME
    is_modified_: bool  # True if self is modified from previous context FIXME
    is_hidden: bool  # True if self should not be dispplayed in ui
    has_been_used_in_the_proof: bool

    def __init__(self, node, info, children, bound_vars, math_type):
        super().__init__(node, info, children, bound_vars, math_type)

        ContextMathObject.list_.append(self)

        # Ancestor in logically previous context
        self.parent_context_math_object = None
        self.child_context_math_object = None

        # Tags
        self.is_new_ = False  # FIXME: obsolete
        self.is_modified_ = False  # FIXME: obsolete
        self.has_been_used_in_proof = False  # TODO: implement
        self.is_hidden = False # TODO
        # log.debug(f"Creating ContextMathPObject {self.to_display()},")
                  # f"dummy vars = "
                  # f"{[var.to_display() for var in self.bound_vars]}")

    @property
    def is_new(self):
        return self.parent_context_math_object is None

    @property
    def is_modified(self):
        return (self.parent_context_math_object
                and self.parent_context_math_object.math_type != self.math_type)

    def is_descendant_of(self, other):
        """
        True is self is a (strict) descendant of other.
        """
        parent = self.parent_context_math_object
        if parent:
            return parent == other or parent.is_descendant_of(other)

    @classmethod
    def whose_math_type_is(cls, math_type: MathObject):
        """
        Return the list of current ContextMathObjects with given math_type.
        """
        math_objects = [mo for mo in cls.list_ if mo.math_type == math_type]
        return math_objects

    def copy_tags(self, other):
        self.has_been_used_in_proof = other.has_been_used_in_proof
        self.is_hidden = other.is_hidden

    def remove_future_info(self):
        self.child_context_math_object = None

    def raw_latex_shape(self, negate=False, text_depth=0):
        """
        Replace the raw_latex_shape method for MathObject.
        """
        shape = super().raw_latex_shape(negate, text_depth)
        if (hasattr(self, 'has_been_used_in_proof')
                and self.has_been_used_in_proof):
            shape = [r'\used_property'] + shape
        return shape

    def raw_latex_shape_of_math_type(self, text_depth=0):
        """
        Replace the raw_latex_shape_of_math_type method for MathObject.
        """
        shape = super().raw_latex_shape_of_math_type(text_depth)
        if (hasattr(self, 'has_been_used_in_proof')
                and self.has_been_used_in_proof):
            shape = [r'\used_property'] + shape
        if self.is_function():
            # Should be "a function from" in text mode,
            # and nothing in symbol mode.
            shape[0] = r"\context_function_from"
        return shape

    @property
    def identifier(self):
        return self.info.get("id")

    # def math_type_to_display(self, format_="html", text_depth=0) -> str:
    #     abstract_string = MathObject.to_abstract_string(self, text_depth)
    #     if self.has_been_used_in_the_proof:
    #         abstract_string = [r"\used_property"] + abstract_string

    def help_target_msg(self, format_="html") -> (str, str):
        """
        A help msg for a ContextMathObject as a target.

        Help msgs should depend on the main symbol of self, using implicit
        definition if they are allowed by the current settings.
        """

        gen_msg = ""
        pract_msg = ""
        hint = ""
        to_prove = _("In order to prove")
        if self.is_for_all():
            type_ = self.children[0].to_display(format_="html")
            var = self.children[1].to_display(format_="html")
            prop = self.children[2].to_display(format_="html")
            gen_msg = to_prove + " " + _("this universal property") + ", " +\
                _("take any element {} of {}").format(var, type_) + " " +\
                _("and prove that {}").format(prop) + "."

        return gen_msg, pract_msg, hint

    def help_context_msg(self, format_="html") -> (str, str, str):
        to_use = _("In order to use")
        gen_msg = ""
        pract_msg = ""
        hint = ""
        children = self.math_type.children
        if self.is_for_all():
            # TODO: in case of an implicit forall (and
            #  implicite_use_of_def is set), add a preambule saying
            #  "after unfolding the def, this is a universal prop".
            type_ = children[0].to_display(format_="html")
            var = children[1].to_display(format_="html")
            # prop = children[2].to_display(format_="html")
            gen_msg = _("You can apply") + " " + _("this universal property") +\
                " " + _("to any element {} of {}").format(var, type_) + "."
            pract_msg = _("If there is an element of {} in the context, "
                          "you may select it together with this property "
                          "before pressing the ∀ button.").format(type_)
            hint = to_use + "this universal property, " + \
                   _("you need some element of {}.").format(type_) + \
                + _("Is there any in the context? If not, can you create some?")

        return gen_msg, pract_msg, hint



