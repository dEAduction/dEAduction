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

import deaduction.pylib.config.vars as cvars
from deaduction.pylib.mathobj.math_object   import MathObject

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

    def action_from_premise_and_operator(self, other: MathObject):
        """
        Return possible actions for premise = self and operator = other. This is
        used e.g. to determine which action could be triggered by a drag&drop
        operation.
        """
        operator = self
        premise = other
        action = None

        implicit = cvars.get("functionality.allow_implicit_use_of_definitions")

        if premise.math_type.is_prop():
            if operator.can_be_used_for_implication(implicit=implicit):
                action = "implies"
            else:
                yes, subs = operator.can_be_used_for_substitution()
                if yes:
                    action = "equal"
        else:
            if operator.is_for_all(implicit=implicit):
                action = "forall"

        return action

    def help_target_msg(self, format_="html") -> (str, str):
        """
        Return three help msgs about self:
        - a general msg that describes self,
        - a msgs that explains how to use self in deaduction,
        - a (maybe empty) hint msg.
        Help msgs should depend on the main symbol of self, using implicit
        definition if they are allowed by the current settings.
        """

        implicit = cvars.get("functionality.allow_implicit_use_of_definitions")
        implicit = False  # Fixme

        raw_msgs = None
        params = tuple()
        children = self.math_type.children
        if self.is_for_all(implicit=implicit):
            params = (children[0].to_display(format_="html"))
            raw_msgs = prove_forall

        if raw_msgs:
            msgs = (_(msg).format(params) if msg else "" for msg in raw_msgs)
            return msgs
        else:
            return "", "", ""

    def help_context_msg(self, format_="html") -> (str, str, str):
        """
        Return three help msgs about self:
        - a general msg that describes self,
        - a msgs that explains how to use self in deaduction,
        - a (maybe empty) hint msg.
        Help msgs should depend on the main symbol of self, using implicit
        definition if they are allowed by the current settings.
        """

        implicit = cvars.get("functionality.allow_implicit_use_of_definitions")
        implicit = False  # Fixme

        raw_msgs = None
        params = tuple()
        children = self.math_type.children
        if self.is_for_all(implicit=implicit):
            params = (children[0].to_display(format_="html"))
            raw_msgs = use_forall

        if raw_msgs:
            msgs = (_(msg).format(params) for msg in raw_msgs)
            return msgs
        else:
            return "", "", ""


use_forall = (_("This is a universal property, which tells something about "
                "every element of {}."),
              _("To use this property, press the ∀ button after selecting "
                "an element of {}."),
              _("To use this property, you need some element of {}. Is there "
                "any in the context? If not, can you create some?"))


prove_forall = (_("This is a universal property, which tells something about "
                  "every element of {}."),
                _("To start a proof of this property, press the ∀ button."),
                "")

use_exists = (_("This is an existential property, which asserts the "
                "existence of an element of {} satisfying a precise "
                "property."),
              _("To use this property, just press the ∃ button."),
              "")

prove_exists = (_("This is an existential property, which asserts the "
                  "existence of an element of {} satisfying a precise "
                  "property."),
                _("To prove this property, press the ∃ button after selecting"
                  "the element of {} that satisfies the wanted property."),
                _("Is there some element of {} in the context? If this is "
                  "so, does it suits your needs? If not, can you create "
                  "some?"))

use_or = (_("This property is a disjunction."),
          _("Press the ∨ (OR) button to engage in a proof by cases; you will "
            "successively examine the case when {} holds and the case when {}"
            "holds."),
          _("Would it help you to know which one of the two properties hold?"
            "If so, then you could consider engaging in a proof by cases."))


prove_or = (use_or[0],
            _("Press the ∨ (OR) button to simplify the goal by deciding which "
              "one of the two properties you will prove. You may forget about"
              "the other one!"),
            _("Do you have enough information in the context to prove one of "
              "these two properties? \\If this is so, then choose this "
              "property with the ∨ (OR) button. \\If not, you should first "
              "get more information (maybe by engaging in a proof by cases)."))

#  ¬
use_and = (_("∧"),
           _(""),
           _(""))


prove_and = (_(""),
             _(""),
             _(""))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


