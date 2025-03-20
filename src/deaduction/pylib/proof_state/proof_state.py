"""
###########################################################
# proof_state.py : provides the class ProofState and Goal #
###########################################################

The goal and proof_state classes are designed to reflect Lean's goals and
proof states. A goal is essentially made of a context and a target. The
context is a list of MathObjects, and the target is a MathObject.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 07 2020 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

This file is part of dEAduction.

    dEAduction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    dEAduction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

from dataclasses import dataclass
import logging
from typing import List, Tuple, Union
from copy import copy

import deaduction.pylib.logger as logger
import deaduction.pylib.config.vars as cvars

from deaduction.pylib.mathobj.math_object import MathObject, BoundVar
from deaduction.pylib.mathobj.context_math_object import ContextMathObject
from deaduction.pylib.mathobj.lean_analysis import (lean_expr_with_type_grammar,
                                                    LeanEntryVisitor)
# from deaduction.pylib.math_display import plurals, numbers
from deaduction.pylib.utils import inj_list
from deaduction.pylib.give_name.name_hint import NameHint

from deaduction.pylib.math_display import MathDisplay

log = logging.getLogger(__name__)

global _

DEBUG = False


# plurals = MathDisplay.plurals
# plural_types = MathDisplay.plural_types
# numbers = MathDisplay.numbers


##################
# The Goal class #
##################
class Goal:
    """
    A goal is made of a context and a target, and reflects Lean's goal.
    The future_tags attribute is used to store the result of the comparison
    with the previous goal during a proof; it essentially tags each object of
    the context as new, modified or unchanged.

    Note that the order in the context is important, since it will be
    displayed as such in the UI. We do not keep Lean's order, which put
    modified objects at the end: for a better user experience we rather try to
    keep the order of the previous step. More precisely,
    - instantiation from_lean_data keeps Lean's order,
    - application of the compare(self, previous_goal) method modify the
    order so that unchanged and modified objects are kept in the order they
    had in the previous_goal, and new objects are kept at the end.

    The class provides methods for
    - comparing goals,
    - splitting goals into objects and properties,
    - "smartly" naming variables, in particular all bound variables,
    - printing goals.

    unmodified_context reflects the order the context is recorded by Lean.
    This order may be modified in self._context, typically when a
    substitution occurs within a property H, the new property H' is put at
    the place where H was, thus resulting in a property where a term x
    occurs before it is declared. In summary,
        _context is used in the gui,
        unmodified_context is used for Lean communication.
    """

    def __init__(self, context: [ContextMathObject], target: ContextMathObject):
        self._context = context
        self.unmodified_context = context
        self.target = target
        self.name_hints = []
        # self.smart_name_bound_vars()

    @classmethod
    def from_lean_data(cls, hypo_analysis: str, target_analysis: str,
                       to_prove=False):
        """
        Construct a goal Python object from Lean's data, i.e. the two
        strings resulting from the tactics hypo_analysis and targets_analysis.

        :param hypo_analysis:   string from the lean tactic hypo_analysis
        :param target_analysis: first string from the lean tactic
                                targets_analysis (only the main target)
        :param to_prove: True if this is the main goal of an exercise.

        :return: a goal
        """

        log.info("creating new Goal from lean strings")
        # log.debug(hypo_analysis)
        # log.debug(target_analysis)
        lines = hypo_analysis.split("¿¿¿")
        # Put back "¿¿¿" and remove '\n', getting rid of the title line
        # ("context:")
        lines = ['¿¿¿' + item.replace('\n', '') for item in lines[1:]]
        context: [ContextMathObject] = []
        for math_obj_string in lines:
            if math_obj_string.startswith("context:"):
                continue
            else:
                # Applying the parser
                tree = lean_expr_with_type_grammar.parse(math_obj_string)
                math_object: ContextMathObject = LeanEntryVisitor().visit(tree)
                context.append(math_object)

        tree = lean_expr_with_type_grammar.parse(target_analysis)
        target = LeanEntryVisitor().visit(tree)
        new_goal = cls(context, target)
        ####################################################################
        # Name bound vars, except for current exercise because we wait for #
        # name_hints transferred from previous goal                        #
        ####################################################################
        if not to_prove:
            new_goal.smart_name_bound_vars()
        return new_goal

    @property
    def context(self):
        """
        Return only non-hidden ContextMathObjects, except if include_hidden.
        Remove double properties.
        """

        return [obj for obj in self._context if not obj.is_hidden]

    @context.setter
    def context(self, context):
        self._context = context

    def context_included_hidden(self):
        return self._context

    def context_objects_included_hidden(self) -> [ContextMathObject]:
        """
        Return the list of objects of the context that are not proposition.
        Note that instance witnesses are excluded
        (i.e. variables whose name starts with "_inst_" )
        """
        if self.context is None:
            return
        objects = [cmo for cmo in self.context_included_hidden()
                   if not cmo.math_type.is_prop()]
        return objects

    def context_props_included_hidden(self) -> [ContextMathObject]:
        if self.context is not None:
            props = [cmo for cmo in self.context_included_hidden()
                     if cmo.math_type.is_prop()]
            return props

    @property
    def context_objects(self) -> [ContextMathObject]:
        """
        Return the list of objects of the context that are not proposition.
        Note that instance witnesses are excluded
        (i.e. variables whose name starts with "_inst_" )
        """
        if self.context is None:
            return
        objects = [cmo for cmo in self.context if not cmo.math_type.is_prop()
                   and not cmo.is_instance()]
        return objects

    @property
    def context_props(self) -> [ContextMathObject]:
        if self.context is None:
            return

        props = []
        prop_types = []
        for obj in self._context:
            if ((not obj.math_type.is_prop()) or obj.is_hidden
                    or obj.math_type in prop_types):
                pass
            else:
                props.append(obj)
                prop_types.append(obj.math_type)

        return props

    @property
    def new_context(self):
        """
        Return objects and props of the context that are new, i.e. they have
        no parent.
        """
        if self.context is not None:
            return [cmo for cmo in self.context if cmo.is_new]

    @property
    def new_props(self):
        """
        Return objects and props of the context that are new, i.e. they have
        no parent.
        """
        if self.context_props is not None:
            return [cmo for cmo in self.context_props if cmo.is_new]

    @property
    def new_objects(self):
        """
        Return objects and props of the context that are new, i.e. they have
        no parent.
        """
        if self.context_objects is not None:
            return [cmo for cmo in self.context_objects if cmo.is_new]

    @property
    def modified_context(self):
        """
        Return objects and props of the context that are new, i.e. they have
        no parent.
        """
        if self.context is not None:
            return [cmo for cmo in self.context if cmo.is_modified]

    @property
    def all_is_new(self) -> bool:
        return all(obj.is_new for obj in self.context)

    @property
    def contains_new_or_modified_context(self) -> bool:
        """True if the context contains new or modified object, but not all
        of them are."""
        return (bool(self.new_context + self.modified_context) and not
                self.all_is_new)

    @property
    def contains_used_in_proof(self) -> bool:
        return any(obj.has_been_used_in_proof for obj in self.context)

    def defining_equalities(self):
        """
        Return the list of defining equalities in self.context. A prop is a
        defining equality iff its name starts with "Def" and it is an
        equality whose left term is a local constant of self.context.
        """
        eq = []
        for p in self.context_props:
            if p.is_equality():
                name = p.name
                lc = p.math_type.children[0]
                if name.startswith('Def') and lc in self.context_objects:
                    eq.append(p)

        return eq

    def remove_future_info(self):
        for obj in self.context:
            obj.remove_future_info()

    def math_object_from_name(self, name: str) -> MathObject:
        """
        Return the MathObject whose name is name.
        """
        if name == "target":
            return self.target
        else:
            math_objects = [math_object for math_object in self.context if
                            math_object.has_name(name)]
            if math_objects:
                return math_objects[0]

    def mark_used_properties(self,
                             used_properties: Union[ContextMathObject, str]):
        """
        Mark all properties of self that appear in used_properties as used.
        """

        context_used_prop = [prop for prop in used_properties
                             if isinstance(prop, ContextMathObject)]
        str_used_prop = [prop for prop in used_properties
                         if isinstance(prop, str)]
        for prop in self.context_props:
            if prop in context_used_prop:
                prop.has_been_used_in_proof = True
                context_used_prop.remove(prop)
            elif prop.name in str_used_prop:
                prop.has_been_used_in_proof = True
                str_used_prop.remove(prop.name)

        unused_prop = context_used_prop + str_used_prop
        if unused_prop:
            log.debug(f"Used properties not found in goal: "
                        f"{unused_prop}")

##################
# Compare method #
##################
    def compare(self, old_goal):
        """
        Compare the new goal to the old one, and tag the target and the
        elements of the new context accordingly. tag is one of the following:
        "+" means present in the new goal, absent in the old goal
        "=" means present in both and identical
        "≠" means present in both and different

        In the tests, two math_objects are equal if they have the same name
        and the same math_type, and they are modified versions of each other if
        they have the same name and different math_types.

        Note that this method relies heavily on __eq__ MathObject's method,
        which is redefined in the corresponding file as a rather strict
        notion of equality.

        :param self:        new goal
        :param old_goal:    old goal

        :return: no direct return, but
            - the context is permuted (see the Goal class documentation)
            - objects of the context are linked to objects of the previous
            context via the parent/child attribute.
        """

        old_goal: Goal
        new_goal = self
        new_context = new_goal.context.copy()
        old_context = old_goal.context.copy()
        # Permuted_new_context will contain the new_context in the order
        # reflecting that of the old_context
        # Each new item that is found in the old_context will be affected at
        # its old index, items that are new will be appended, and then
        # None objects (corresponding to object that have disappeared) will be
        # removed from the list
        permuted_new_context = [None] * len(old_context)

        log.info("Comparing and tagging old goal and new goal")
        # log.debug(old_context)
        # log.debug(new_context)
        old_names = [math_object_old.info["name"]
                     for math_object_old in old_context]
        for math_object in new_context:
            name = math_object.info["name"]

            # (1) Search old_context for an object with the same name
            try:
                old_index = old_names.index(name)
            except ValueError:
                # (2) If no such object then object is new
                old_index = None
                # New objects at the end
                permuted_new_context.append(math_object)
            else:
                # Put new object at old index, copy tags for ui,
                #  and link to parent object
                old_object = old_context[old_index]
                permuted_new_context[old_index] = math_object
                math_object.copy_tags(old_object)
                math_object.parent_context_math_object = old_object
                old_object.child_context_math_object = math_object
                # (3) Reveal if modified(?)
                if old_object.math_type != math_object.math_type:
                    math_object.is_hidden = False

            if old_index is not None:
                # Will not be considered anymore:
                old_names[old_index]   = None
                old_context[old_index] = None

        # (5) Remove 'None' entries
        clean_permuted_new_context = [item for item in permuted_new_context
                                      if item is not None]

        # (6) Finally, modify order and set tags
        self.context = clean_permuted_new_context

        # (7) Compare targets:
        old_target = old_goal.target.math_type
        new_target = new_goal.target.math_type
        if new_target == old_target:
            new_goal.target.parent_context_math_object = old_goal.target

#############################
# Bound vars naming methods #
#############################
    def free_variables(self, math_type=None):
        """
        Return all free variable, i.e. elements of the context.
        """
        if math_type:
            return [var for var in self.context_objects
                    if var.math_type == math_type]
        else:
            return self.context_objects

    def bound_variables(self, math_type=None):
        """
        Return all bound variables of context and target of a given type.
        Each variable should appear exactly once.
        """
        c_vars = sum([mo.math_type.bound_vars(math_type=math_type)
                      for mo in self.context_props], [])
        t_vars = self.target.math_type.bound_vars(math_type=math_type)
        return c_vars + t_vars

    def variables(self, math_type=None) -> [MathObject]:
        """
        Provide the list of all variables (free and bound) of a given
        math_type.
        """
        return self.free_variables(math_type) + self.bound_variables(math_type)

    def free_var_types(self):
        return inj_list([var.math_type for var in self.free_variables()])

    def bound_var_types(self):
        return inj_list([var.math_type for var in self.bound_variables()])

    def variable_types(self):
        return inj_list([var.math_type for var in self.variables()])

    def free_var_names(self, math_type=None):
        """
        Return all context var names of given math_type.
        """
        return [cmo.display_name for cmo in self.free_variables(math_type)]

    def potential_math_types(self):
        """
        Return the elements of context that can serve as types.
        For the moment, just sets (universes).
        FIXME: Could include subsets, and sets/subsets among bound vars.
        """
        return inj_list([mo for mo in self.variables() if mo.is_type()])

###################
# Build NameHints #
###################
    def transfer_name_hints_from(self, old_goal):
        new_goal = self
        new_goal.name_hints = copy(old_goal.name_hints)

    def clear_hints(self):
        """
        Remove the hints that do not correspond anymore to any pertinent
        math_type of the context.
        """

        # (1) Collect all pertinent math types
        types = self.variable_types() + self.potential_math_types()

        # (2) Remove hints for non-existing types
        for hint in self.name_hints:
            if hint.math_type not in types:
                self.name_hints.remove(hint)

    def update_context_hints(self):
        """
        Create NameHints for all math_types of context vars.
        """
        for var in self.free_variables():
            math_type = var.math_type
            if math_type.is_number():
                preferred_letter = var.display_name
                friendly_names = []
            else:
                preferred_letter = ''
                friendly_names = self.free_var_names(math_type)
            # Add new name hint if none match:
            NameHint.from_math_type(math_type, preferred_letter,
                                    self.name_hints, friendly_names)

    def update_bound_var_hints(self):
        """
        Create NameHints for all bound vars to be named.
        """
        for var in self.bound_variables():
            if not var.keep_lean_name():  # (Var needs a name)
                math_type = var.math_type
                # Add new name hint if none match:
                NameHint.from_math_type(math_type, var.preferred_letter(),
                                        self.name_hints)

    def update_potential_hints(self):
        """
        Add hints for some math_type even if no MathObject of that type
        already exists, just in case. This 'book' the corresponding
        hints.letter, which will not be used by other hints.
        """
        # TODO: add set X for every universe X?
        # TODO: take into account implicit defs in target
        for math_type in self.potential_math_types():
            NameHint.from_math_type(math_type, existing_hints=self.name_hints)

    def __update_all_name_hints(self):
        """
        Ensure that each math_type of appearing in self has an associated
        NameHint.
        """
        self.clear_hints()
        self.update_context_hints()
        self.update_bound_var_hints()
        self.update_potential_hints()
        if DEBUG:
            self.print_hints()

    def print_hints(self):
        """For debugging."""
        print("Name hints:")
        for name_hint in self.name_hints:
            print(name_hint)
            # print(f"Name hint for {name_hint.math_type}: {name_hint.letter}")
            # if name_hint.names:
            #     print(f"   names: {name_hint.names}")

########################
# Build Naming Schemes #
########################
    def _recursive_bound_vars_length(self, math_obj: MathObject,
                                     include_sequences=True, 
                                     hint: NameHint = None):
        """
        Compute the maximal length of a chain of bound vars of the given
        types. On other words, this is the maximal nb of distinct bound vars
        of this type that live in the same local context.
        The principle of the computation is that if self has bound var then
        this bound var occurs in the local context of all self's children.
        This algo follows MathObject.bound_vars().
        This method is crucial, overestimating or underestimating the number
        of vars to be named with a given NameHint.names() method would lead to
        bad naming!
        """

        math_type = hint.math_type
        # preferred_letter = hint.preferred_letter
        preferred_letters = hint.current_preferred_letters()
        local_length = 0

        # (0) Special case: if u_n then do not count u's bound var used for
        # display in (u_n)_{n in N}
        if math_obj.is_app_of_local_constant():
            return 0

        # (1) Self's has direct bound var?
        if math_obj.has_bound_var():
            var = math_obj.bound_var
            typ = math_obj.bound_var_type
            letter = var.preferred_letter()
            if include_sequences or \
                    not (math_obj.is_sequence(is_math_type=True)
                         or math_obj.is_set_family(is_math_type=True)):
                if (not math_type) or \
                    (typ == math_type and
                        (not letter or letter in preferred_letters)):
                    local_length = 1

        # (2) Children's vars:
        child_length = [self._recursive_bound_vars_length(child,
                                                          include_sequences,
                                                          hint)
                        for child in math_obj.children]
        return local_length + max(child_length + [0])

    def max_local_length(self, hint):
        """
        Compute the nb of distinct vars which fits the given hint that may occur
        simultaneously in a local context. Fitting hint means having the same
        math_type and same preferred_letter if any.
        """
        # context_length = len(self.free_variables(math_type))

        props = ([prop.math_type for prop in self.context_props]
                 + [self.target.math_type])
        local_context_length = []
        for prop in props:
            local_context_length.append(self._recursive_bound_vars_length(
                                        math_obj=prop,
                                        include_sequences=True,
                                        hint=hint))

        if DEBUG:
            # print(f"BVs: {[p.bound_vars() for p in props]}")
            print(f"Local context length for hint {hint.math_type}, "
                  f"pref letter = {hint.preferred_letter}:"
                  f" {local_context_length}")

        length = max(local_context_length + [0])

        if length > 0:
            log.debug(f"Bound vars length of {hint.math_type, hint.letter}:"
                      f" {length}")

        return length

    def update_name_schemes(self, supp_math_type=None,
                            supp_nb=0):
        """
        Compute lists of names for naming all bound vars appearing in self,
        one scheme associated to each math type, via its NameHint.
        Supplementary vars can be asked for, in case we need to name new var
        for the next context (e.g. "intro x").
        At least one name is provided for each type, even if no var is
        required at present time.
        """

        all_names = set(self.free_var_names())
        hint_letters = {hint.letter for hint in self.name_hints}
        for hint in self.name_hints:
            math_type = hint.math_type
            length = self.max_local_length(hint)
            if math_type == supp_math_type:
                length += supp_nb
            if length == 0:
                length = 1
            friend_names = set(self.free_var_names(math_type=math_type))
            # Experimental: exclude other hint letters
            bad_letters = hint_letters.difference({hint.letter})
            bad_names = all_names.union(bad_letters)
            excluded_names = bad_names.difference(friend_names)

            # Ensure that hint's naming scheme is compatible with data:
            if DEBUG:
                print(f"Updating name list for hint, old = {hint.names}")
                print(f"length = {length}, friend names = {friend_names}, "
                      f"excluded names = {excluded_names}")

            hint.update_names_list(length, friend_names, excluded_names)

            if DEBUG:
                print(f"   ... new = {hint.names}")

##################
# Name variables #
##################
    def provide_good_name(self, math_type, preferred_letter='',
                          local_names=None, isolated=False):
        """
        Try its best to get a good name of given math_type with
        preferred_letter, taken into account given names.
        """

        # Names to be excluded:
        if not local_names:
            local_names = []
        global_names = self.free_var_names() if not isolated else []
        given_names = local_names + global_names

        name_hint = NameHint.from_math_type(math_type, preferred_letter,
                                            existing_hints=self.name_hints)

        new_name, success = name_hint.provide_name(given_names=given_names)

        if DEBUG:
            print(f"Naming var, preferred_letter = {preferred_letter}, context ="
                  f" {given_names}, self.name_hints= {self.name_hints}")
            print(f"Names hint = {name_hint.names}, new_name = {new_name}")
            print(f"---> new_name = {new_name}")
        if not success:
            # Update all name schemes with requiring one more name for this
            # type:
            self.update_name_schemes(supp_math_type=math_type, supp_nb=1)
            new_name, success = name_hint.provide_name(given_names=given_names)

            print(f"Renaming var, context = {given_names}")
            print(f"Names hint = {name_hint.names}, new_name = {new_name}")
            print(f"---> new_name = {new_name}")

            if not success:
                log.warning(f"Bad name {new_name} given to var of type "
                            f"{math_type}")

        return new_name

    def provide_good_names(self, math_types, preferred_letters=None):
        """
        Provide new names for a list of math_types.
        """

        # Fill preferred_letters with None to get equal length with math_types
        if not preferred_letters:
            preferred_letters = [None]*len(math_types)
        elif len(preferred_letters) < len(math_types):
            preferred_letters.extend([None] *
                                     (len(math_types)-len(preferred_letters)))
        new_names = []
        for math_type, letter in zip(math_types, preferred_letters):
            new_name = self.provide_good_name(math_type,
                                              preferred_letter=letter,
                                              local_names=new_names)
            new_names.append(new_name)
        return new_names

    def name_one_bound_var(self, var: BoundVar, isolated=False):
        """
        Name the given bound var according to its type and the
        name scheme found in self.name_hints.
        isolated bool may be used to name sequences' indices without bothering
        about conflicting with global vars names.
        """

        # if DEBUG:
        #     print(f"Naming var, local_context = {var.local_context}")

        if not var.is_unnamed:
            return
        elif var.keep_lean_name():
            name = var.lean_name
        else:
            if not isolated:
                local_names = [other_var.name for other_var in var.local_context]
            else:
                local_names = []

            name = self.provide_good_name(var.math_type, var.preferred_letter(),
                                          local_names=local_names,
                                          isolated=isolated)

        var.name_bound_var(name)

    def __name_context_object_bound_var(self, math_object, isolated=False):
        """
        Provide a name for bound vars of context objects like sequences and
        set families, used only to display these objects. Here local context
        is useless.
        """

        for child in math_object.children:
            if child.is_bound_var:
                name = self.provide_good_name(child.math_type,
                                              child.preferred_letter(),
                                              local_names=[],
                                              isolated=isolated)
                child.name_bound_var(name)

    def recursive_name_all_bound_vars(self, p: MathObject,
                                      include_sequences=True):
        """
        Recursively name all bound vars in p. Each bound var should be
        named only once (!). Beware that local context should have been set.
        """

        # (1) Name self's direct bound var, if any
        if p.has_bound_var():
            if (not include_sequences) \
                    and (p.is_sequence(is_math_type=True)
                         or p.is_set_family(is_math_type=True)):
                isolated = True
            else:
                isolated = False

            self.name_one_bound_var(p.bound_var, isolated=isolated)

        # (2) Name children's vars:
        for child in p.children:
            self.recursive_name_all_bound_vars(child, include_sequences)

    def debug(self):
        print('Context props:')
        print([obj.math_type for obj in self.context_props])
        print(f'Target: {self.target.math_type}')
        self.print_hints()

    def smart_name_bound_vars(self):
        """
        This method should be called each time a new goal is instantiated,
        but after name_hints have been set.
        It provides names for all bound vars in self's context and target.

        The local context for prop is also set here, it is crucial so that
        names are given appropriately.
        """

        # (1) Update name lists for each math_type
        self.__update_all_name_hints()
        self.update_name_schemes()

        # (2) Name bound vars in context objects (e.g. sequences):
        if DEBUG:
            print(f"Naming BV in context objs...")
        for math_object in self.context_objects:
            self.__name_context_object_bound_var(math_object)

        # (3) Name bound vars in target
        if DEBUG:
            print(f"Naming BV in target...")
        self.target.math_type.set_local_context()
        self.recursive_name_all_bound_vars(self.target.math_type)
                
        # (4) Name bound vars in context props:
        for p in self.context_props:
            if DEBUG:
                print(f"Naming BV in {p}...")
            p.math_type.set_local_context()
            self.recursive_name_all_bound_vars(p.math_type)

        # (5) Debug
        # self.debug()

    def extract_vars_names(self) -> List[str]:
        """
        Provides the list of names of all variables in the context,
        including names of hypotheses (but NOT bound variables).
        """
        names = [math_object.info['name'] for math_object in
                 self.context]
        return names

    ###################
    # Display methods #
    ###################
    def to_math_object(self) -> MathObject:
        """
        Return a math_object obtained by integrating all the context in the
        target, using universal quantifiers and implications. e.g. if
        self.context contains objects x, y and properties P, Q, the new goal
        will be
                        ∀x, ∀y, (P and Q ) ==> target.
        This is not a recursive method since we do not want to create new goals
        (to avoid creating new ContextMathObjects).
        """

        # (1) Compute body of universal prop:
        props = [prop.math_type for prop in self.context_props_included_hidden()]
        target = self.target.math_type
        if props:
            conjunction = MathObject.conjunction(props)
            body = MathObject.implication(conjunction, target)
        else:
            body = target

        # (2) Compute the "∀x, ∀y, ..." part (list shadow copy):
        objs = [obj for obj in self.context_objects_included_hidden()]
        while objs:
            obj = objs.pop()
            body = MathObject.forall(obj, body)

        self.recursive_name_all_bound_vars(body)
        return body

    def negate(self) -> MathObject:
        """
        Return a math_object obtained by negating self. e.g. if self.context
        contains objects x, y and properties P, Q, the new goal will be
             NOT  ( ∀x, ∀y, (P and Q ) ==> target ).
        """

        # # (1) Compute body of universal prop:
        # props = [prop.math_type for prop in self.context_props]
        # target = self.target.math_type
        # if props:
        #     conjunction = MathObject.conjunction(props)
        #     body = MathObject.implication(conjunction, target)
        # else:
        #     body = target
        #
        # # (2) Compute the "∀x, ∀y, ..." part:
        # objs = [obj for obj in self.context_objects]  # List shadow copy
        # while objs:
        #     obj = objs.pop()
        #     body = MathObject.forall(obj, body)

        # (3) Negate!
        new_prop = MathObject.negate(self.to_math_object())

        return new_prop

    @classmethod
    def negated_goal(cls, old_goal):
        """
        Return a new goal which is the negation of old_goal.
        """
        new_prop = old_goal.negate()
        new_target = ContextMathObject(node="LOCAL_CONSTANT",
                                       info={'name': "target"},
                                       children=[],
                                       math_type=new_prop)
        negated_goal = cls(context=[], target=new_target)
        # Bound vars are named like the old context vars they stand for,
        # but for dummy var for sequences.
        negated_goal.smart_name_bound_vars()
        return negated_goal

    def context_to_lean(self):
        """
        Return  self's context in Lean format, e.g.
        (x: X) (A: set X) (H1: x ∈ A)
        """
        lean_context = ""
        for co in self.unmodified_context:
            lean_context += f"({co.to_lean_with_type()}) "

        return lean_context

    def target_to_lean(self):
        """
        Return  self's target in Lean format, e.g.
        x ∈ B
        """
        return self.target.math_type.to_display(format_='lean')

    def to_lean_statement(self, title="deaduction"):
        """
        Return self's content as a Lean exercise, e.g.
        'lemma exercise.blabla
        (x: X) (A: set X) (H1: x ∈ A) :
        x ∈ B :='
        """
        context = self.context_to_lean()
        target = self.target_to_lean()
        lean_statement = f"lemma exercise.{title}\n {context} :\n {target}"
        # lean_proof = "begin\n\nend\n"
        # debug:
        # print(lean_statement)
        return lean_statement + " :=\n"  # + lean_proof

    def goal_to_text(self,
                     format_="utf8",
                     to_prove=True,
                     text_mode=True,
                     open_problem=False,
                     apply_statement=False) -> str:
        """
        Compute a displayable version of the goal as the statement of an
        exercise.

        :param format_:     "utf8" or "html".
        :param to_prove:    boolean.
            If True, the goal will be formulated as "Prove that..."
            If False, the goal will be formulated as "Then..." (useful if
            the goal comes from a Theorem or Definition)
        :param text_mode:  boolean.
        :param open_problem: if True, then display as "True or False?"
        @param apply_statement: if True, the (non-implicit) hypotheses are
        separated by a CR.

        :return: a text version of the goal
        """

        # TODO: if by_type, group successive context objects by math_type.
        text_cr = "<br>" if format_ == "html" else "\n"

        # Name bound vars if needed!
        self.smart_name_bound_vars()

        context = self.context
        target = self.target
        text = ""
        #######################
        # (1) Display context #
        #######################
        previous_object_is_prop = None
        counter = 0
        while counter < len(context):
            math_object = context[counter]
            math_type = math_object.math_type

            if math_type.is_prop():  # Display hypotheses
                object_is_prop = True
                prop = math_object.math_type_to_display(format_=format_,
                                                        text=text_mode)
                prop_utf8 = math_object.math_type_to_display(format_='utf8',
                                                        text=True)
                assume_that = _("Assume that") + " "
                if prop_utf8.startswith(_('the negation')):
                    assume_that = _("Assume") + " "

                if cvars.get('i18n.select_language') == 'fr_FR':
                    # "Supposons que il" --> "Supposons qu'il"
                    if (prop_utf8.startswith("un")
                            or prop_utf8.startswith("il")):
                        assume_that = "Supposons qu'"

                new_sentence = assume_that + prop + "."
            else:  # Display objects
                object_is_prop = False
                new_sentence = ""
                # Try to gather objects of the same type:
                grouped_objects = [math_object]
                while (counter < len(context) - 1
                       and context[counter+1].math_type == math_type):
                    counter += 1
                    grouped_objects.append(context[counter])
                new_sentence = introduce_several_object(grouped_objects,
                                                        format_=format_)

            # Add a separator, either a new line or a space
            if text:
                if object_is_prop != previous_object_is_prop:
                    # New line only to separate objects and propositions.
                    text += text_cr
                elif apply_statement and (not object_is_prop):
                    text += text_cr
                else:
                    # New sentence
                    text += " "

            previous_object_is_prop = object_is_prop
            text += new_sentence

            counter += 1

        if text:
            text += text_cr

        ######################
        # (2) Display target #
        ######################
        target_text = target.math_type_to_display(text=text_mode,
                                                  format_=format_)
        # Helper for syntactic rules:
        target_utf8 = target.math_type_to_display(text=text_mode,
                                                  format_='utf8')
        if to_prove and not open_problem:
            prove_that = _("Prove that") + " "
            # "Prove that the negation" --> "Prove the negation"
            if target_utf8.startswith(_('the negation')):
                prove_that = _("Prove") + " "
            elif cvars.get('i18n.select_language') == 'fr_FR':
                # "Démontrer que il" --> "Démontrer qu'il"
                if target_utf8:
                    words = target_utf8.split()
                    if words[0] in ("il", "un"):
                        prove_that = "Démontrer qu'"
            target_text = prove_that + target_text
        elif text:
            target_text = _("Then") + " " + target_text
        else:  # Capitalise but inside html formatters...
            # Little issue: if sentence starts with a lower case
            # variable. This should never happen though...
            first_word = target_utf8.split()[0]
            target_text = target_text.replace(first_word,
                                              first_word.capitalize(),
                                              1)
        if open_problem:
            text = _("True or False:") + text_cr + text
        text += target_text + "."
        return text

    def print_goal(self, open_problem=False, to_prove=True) -> str:
        """
        Return context and target in a raw (text) form.
        """

        # Name bound vars if needed
        # self.name_bound_vars(to_prove=to_prove)

        context = self.context
        target = self.target
        text = ""
        if open_problem:
            text += _("True or False?") + "\n"
        if len(context) == 1:
            text += _("Hypothesis:") + "\n"
        elif len(context) > 1:
            text += _("Hypotheses:") + "\n"

        for math_object in context:
            # math_type = math_object.math_type
            name = math_object.to_display(format_="utf8")
            name_type = math_object.math_type_to_display(format_="utf8")
            text_object = name + _(": ") + name_type
            text += "  " + text_object + "\n"
        if to_prove and not open_problem:
            text += _("Prove that") + "\n"
        elif context:
            text += _("Then") + "\n"
        text += target.math_type_to_display(format_="utf8")
        return text

    def to_tooltip(self, type_='exercise', format_='html') -> str:
        """
        Return context and target in a raw form as a tooltip for a goal.
        """

        # Name bound vars if needed
        # self.name_bound_vars(to_prove=(type_ == 'exercise'))

        context: [ContextMathObject] = self.context
        target = self.target
        text = ""
        cr = "<br>" if format_ == 'html' else "\n"

        # Context
        if context:
            if type_ == "exercise":
                hypo_text = _("Context:")
            else:
                hypo_text = _("Hypothesis:") if len(context) == 1 else \
                    _("Hypotheses:")
            if format_ == 'html':
                hypo_text = "<b>" + hypo_text + "</b>"
            text = hypo_text + cr
        else:
            # text = _("Empty context") + "\n"
            text = ""

        for math_object in context:
            # math_type = math_object.math_type
            name = math_object.to_display(format_=format_)
            # name_type = math_type.old_to_display(is_math_type=True)
            name_type = math_object.math_type_to_display(format_=format_)
            text_object = name + _(": ") + name_type
            text += "  " + text_object + cr

        # Goal
        if type_ == "exercise":
            goal_text = _("Goal:")
        elif context:
            goal_text = _("Conclusion:")
        else:
            goal_text = ""
        if format_ == 'html' and goal_text:
            goal_text = "<b>" + goal_text + "</b>"
        if goal_text:
            text += (goal_text + cr)
        text += " " + target.math_type_to_display(format_=format_)
        # except:
        #     print(target.math_type)
        return text


########################
# The ProofState class #
########################
@dataclass
class ProofState:
    """
    This class reflects Lean's proofstates, and is essentially made of a
    list of goals. The lean_data attributes stores the strings from
    hypo_analysis and targets_analysis from which the ProofState has been
    built.
    This class has a single method, a class method used for building
    ProofStates from the Lean data.

    Note that only the first goal has a non empty context, since
    hypo_analysis only provide context of the main goal.
    """
    goals: List[Goal]
    lean_data: Tuple[str, str] = None

    @property
    def main_goal(self):
        return self.goals[0]

    @classmethod
    def from_lean_data(cls, hypo_analysis: [str], targets_analysis: [str],
                       to_prove=False, previous_proof_state=None):
        """
        :param hypo_analysis:    list of strings from the lean tactic
        hypo_analysis, one string for each goal
        :param targets_analysis: list of string from the lean tactic
        targets_analysis
        :param to_prove: True iff the main goal is the current exercise's goal
        (this affect bound vars naming).
        :param previous_proof_state: previous Proof State. If not know,
        the new proof state is used as an update to the previous proof state:
        - the previous main goal is deleted,
        - the new goals are inserted at index 0 in ProofState.goals

        :return: a ProofState
        """

        log.info("Creating new ProofState from lean strings")
        # targets = targets_analysis.split("¿¿¿")
        # # Put back "¿¿¿" and remove '\n' :
        # targets = ['¿¿¿' + item.replace('\n', '') for item in targets]
        # targets.pop(0)  # Removing title line ("targets:")
        targets = targets_analysis
        # if not targets:
        #     log.warning(f"No target, targets_analysis={targets_analysis}")
        if len(hypo_analysis) != len(targets):
            log.warning("Nb of hypo analysis does not match nb of targets")

        else:
            # main_goal = None
            # # Create main goal:
            # main_goal = Goal.from_lean_data(hypo_analysis, targets[0],
            #                                             to_prove=to_prove)
            # goals = [main_goal]
            # for other_string_goal in targets[1:]:
            #     other_goal = Goal.from_lean_data(hypo_analysis="",
            #                                      target_analysis=other_string_goal,
            #                                      to_prove=False)
            #     goals.append(other_goal)
            new_goals = [Goal.from_lean_data(hypo, target, to_prove=to_prove)
                         for hypo, target in zip(hypo_analysis, targets)]

            if previous_proof_state:
                goals = new_goals + previous_proof_state.goals[1:]
            else:
                goals = new_goals
            new_proof_state = cls(goals, (hypo_analysis, targets_analysis))

            return new_proof_state


def print_proof_state(goal: Goal):
    print("Context:")
    for mt, mt_list in goal.math_types:
        print(f"{[PO.to_display() for PO in mt_list]} :"
              f" {mt.to_display()}")
    print("Target:")
    print(goal.target.math_type.to_display())


if __name__ == '__main__':
    logger.configure()
    from pprint import pprint

    hypo_analysis_new = """"""
    hypo_analysis_old = """"""
    goal_analysis = """"""

    goal = Goal.from_lean_data(hypo_analysis_old, goal_analysis)
    print("context:")
    pprint(goal.context)
    print(("target:"))
    pprint(goal.target.math_type)

    print("variables: ")
    pprint(goal.extract_var_names())

    hypo_essai = """"""

    essai_set_family_hypo = """"""
    essai_set_family_target = """"""


    def print_proof_state(goal):
        print("Context:")
        for mt, mt_list in goal.math_types:
            print(f"{[PO.to_display() for PO in mt_list]} :"
                  f" {mt.to_display()}")
        print("Target:")
        print(goal.target.math_type.to_display())


    goal = Goal.from_lean_data(essai_set_family_hypo, essai_set_family_target)
    print_proof_state(goal)

    print(f"variable names {goal.extract_var_names()}")


def introduce_several_object(objects: [MathObject], format_) -> str:
    """
    Given two or more MathObject having the same math_type, try to construct a
    sentence that introduces them together. e.g.
    "Let A, B be two subsets of X".
    The construction succeed if a plural version of the type is found in
    the "plurals" dictionary.
    """

    # Fixme: changing i18n does not update the following dic,
    #  even if module is reloaded (see config_window)
    # from deaduction.pylib.math_display import plural_types, numbers, plurals
    # update_plurals() FIXME: done in settings?
    new_sentence = ""
    if not objects:
        return new_sentence

    if len(objects) == 1:  # One object
        math_object = objects[0]
        names = math_object.to_display(format_)
        type_ = math_object.math_type_to_display(format_=format_,
                                                 text=True)
        new_sentence = _("Let {} be {}").format(names, type_) + "."

    else:  # More than one object
        names = ", ".join([obj.to_display(format_) for obj in objects])
        number = len(objects)
        if len(objects) <= len(MathDisplay.numbers):
            number = MathDisplay.numbers[number]  # text version of the number
        utf8_type = objects[0].math_type_to_display(format_='utf8',
                                                    text=True)
        type_ = objects[0].math_type_to_display(format_=format_,
                                                text=True)
        plural_type = MathDisplay.plural_types(type_, utf8_type)

        if plural_type:
            shape = MathDisplay.plurals[_("Let {} be {}")]
            new_sentence = shape.format(names, number, plural_type) + "."

    if not new_sentence:  # No plural found: introduce one by one.
        sentences = [introduce_several_object([obj],
                                              format_) for obj in objects]
        new_sentence = " ".join(sentences)

    return new_sentence
