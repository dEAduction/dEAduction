"""
# implicit_definitions.py : <#ShortDescription> #
    
    <#optionalLongDescription>

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

from copy import copy, deepcopy

import logging
if __name__ == "__main__":
    import deaduction.pylib.config.i18n

from deaduction.pylib.math_display        import HAVE_BOUND_VARS
from deaduction.pylib.mathobj.math_object import MathObject

log = logging.getLogger(__name__)


class PatternMathObject(MathObject):
    """
    A class for MathObject that may contain metavariables. Metavariables
    are represented by PatternMathObject whose node is 'METAVAR".
    e.g. The PatternMathObject representing the definition of injectivity
    looks like:
        metavar_28 is injective ⇔ ( ∀x ∈ metavar_26, ∀x' ∈ metavar_26,
                                  (metavar_28(x) = metavar_28(x') ⇒ x = x') )
    Note that here metavar_28 would have type '(metavar_26) → (metavar_27)'
    and metavar_26 has type 'ensemble'.

    The match() method tests if a given MathObject match a PatternMathObject,
    e.g. if left is the PatternMathObject 'metavar_28 is injective', and
         math_object = 'g∘f is injective'
    then
        left.match(math_object)
    will be True. Note that the math_types should also match.

    TODO: modify this:
    After a successful matching test, the matching values of the metavars are
    stored
    FIXME: obsolete:
        in the metavar_objects class attribute as a list of MathObject
        instances.
    FIXME: New version:
    as children of each assigned metavar.
    Then the apply_matching() method will substitute metavars in
    some MathObject. For instance after the previous example, if right is the
    PatternMathObject
        (∀x ∈ metavar_26, ∀x' ∈ metavar_26,
        (metavar_28(x) = metavar_28(x') ⇒ x = x'))
    then right.apply_matching() will produce the MathObject
        ∀x ∈ X, ∀x' ∈ X, (g∘f(x) = g∘f(x') ⇒ x = x')
    """
    metavar_nb = 0
    metavars_csts               = []  # List of all metavars in all patterns
    loc_csts_for_metavars       = []  # and corresponding local constants
    __tmp_metavars_csts         = None
    __tmp_loc_csts_for_metavars = None
    metavars        = None
    metavar_objects = None  # Objects matching metavars (see self.match)

    def __init__(self, node, info, children, bound_vars, math_type):
        super().__init__(node=node,
                         info=info,
                         children=children,
                         bound_vars=bound_vars,
                         math_type=math_type)

    @property
    def nb(self):
        if self.node == 'METAVAR':
            return self.info['nb']
        else:
            return None

    @classmethod
    def new_metavar(cls, math_type):
        cls.metavar_nb += 1
        return cls(node='METAVAR',
                   info={'nb': cls.metavar_nb},
                   children=[],
                   bound_vars=[],
                   math_type=math_type)

    @classmethod
    def from_math_object(cls, math_object: MathObject):
        cls.__tmp_loc_csts_for_metavars = []
        cls.__tmp_metavars_csts         = []
        return cls.__from_math_object(math_object)

    @classmethod
    def __from_math_object(cls, math_object: MathObject):
        """
        Produce a PatterMathObject from math_object by replacing all local
        constants which are not bound variables by fresh metavars.
        Of course all occurrences of a given local constant must be replaced
        by the same metavar.
        This is obviously a recursive method. The lists loc_csts, metavars
        allow keeping track of the correspondence between the local
        constants that have been previously replaced and the metavars.

        :param loc_csts: list of local constants
        :param metavars: corresponding list of metavars
        :return:         new PatternMathObject
        """
        # log.debug(f"Patterning mo {math_object.to_display()}")
        metavars = cls.__tmp_metavars_csts
        loc_csts = cls.__tmp_loc_csts_for_metavars

        if math_object in loc_csts:
            metavar = metavars[loc_csts.index(math_object)]
            # log.debug(f"   Mo is metavar n°{metavar.info['nb']}")
            return metavar

        elif math_object.node == 'LOCAL_CONSTANT' and \
                not math_object.is_bound_var():
            # Turn math_type into a PatternMathObject,
            # then create a new metavar.
            if math_object.math_type is MathObject.NO_MATH_TYPE:
                math_type = PatternMathObject.NO_MATH_TYPE
            else:
                math_type   = cls.__from_math_object(math_object.math_type)
            new_metavar = cls.new_metavar(math_type)
            metavars.append(new_metavar)
            cls.metavars_csts.append(new_metavar)
            loc_csts.append(math_object)
            cls.loc_csts_for_metavars.append(math_object)
            # metavar_list[math_object] = new_metavar
            # log.debug(f"   Creating metavar n°{new_metavar.info['nb']}")
            return new_metavar

        else:
            node = math_object.node

            info = math_object.info  # Useless??
            # log.debug("   ->Children:")
            children = []
            for child in math_object.children:
                new_child = cls.__from_math_object(child)
                children.append(new_child)
            if math_object.math_type is MathObject.NO_MATH_TYPE:
                math_type = PatternMathObject.NO_MATH_TYPE
            else:
                # log.debug("   ->Math type:")
                math_type   = cls.__from_math_object(math_object.math_type)

            pattern_math_object = cls(node=node,
                                      info=info,
                                      children=children,
                                      bound_vars=math_object.bound_vars,
                                      math_type=math_type)
            # log.debug(f"   ->pmo: {pmo.to_display()}")
            return pattern_math_object

    def __eq__(self, other):
        """
        Redefine __eq__, otherwise all METAVARS are equals!?
        """
        return self is other

    def is_metavar(self):
        return self.node == "METAVAR"

    def is_unassigned_mvar(self, selected_objects=None) -> bool:
        """
        Return True if self has been assigned. If selected_objects is not None,
        then the assignment must belong to selected_objects.
        """
        if selected_objects is None:
            return self.is_metavar() and not self.children
        else:
            return (self.is_metavar()
                    and (not self.children
                         or self.children[0] not in selected_objects))

    def set_explicitly_assigned(self, OK=True):
        assert self.is_metavar()
        if OK:
            self.info["assigned"] = "explicit"
        else:
            self.info["assigned"] = None

    def is_explicitly_assigned(self):
        return self.is_metavar() and self.info.get("assigned") == "explicit"

    def match(self, math_object: MathObject, assign=False) -> bool:
        """
        Test if math_object match self. This is a recursive test.
        The list PatternMathObject.metavars contains the metavars that have
        already been matched against a math_object, which is stored with the
        same index in the list PatternMathObject.metavar_objects.
        e.g. 'g∘f is injective' matches 'metavar_28 is injective'
        (note that math_types of metavars should also match).
        If assign=True then all metavars that match are "assigned", i.e.
        the corresponding math_object is stored as their child. This option
        should be used only after having checked that self and math_object do
        match.
        """
        PatternMathObject.metavars = []
        PatternMathObject.metavar_objects = []
        match = self.recursive_match(math_object, assign)
        # log.debug(f"Matching...")
        list_ = [(PatternMathObject.metavars[idx].to_display(),
                  PatternMathObject.metavar_objects[idx].to_display())
                 for idx in range(len(PatternMathObject.metavars))]
        # log.debug(f"    Metavars, objects: {list_}")
        return match

    def recursive_match(self, math_object: MathObject, assign=False,
                        is_math_type=False) -> bool:
        """
        Test if math_object match self. This is a recursive test.
        The list metavars contains the metavars that have already been
        matched against a math_object, and this object is stored with the same
        index in the metavar_objects list.
        """
        # FIXME: take assigned mvars into account.

        metavars = PatternMathObject.metavars
        metavar_objects = PatternMathObject.metavar_objects
        match = True    # Self and math_object are presumed to match
        marked = False  # Will be True if bound variables should be unmarked

        node = self.node
        # Case of NO_MATH_TYPE (avoid infinite recursion!)
        if node == "not provided" or math_object.node == "not provided":
            return True

        # METAVAR
        elif node == 'METAVAR':
            # If self has already been identified, math_object matches self
            #   iff it is equal to the corresponding item in metavar_objects
            # If not, then self matches with math_object providing their
            #   math_types match. In this case, identify metavar.
            if self in metavars:
                corresponding_object = self.math_object_from_metavar()
                match = (math_object == corresponding_object)
            elif self.children:  # Another way to assign the mvar
                match = (math_object == self.children[0])
            else:
                mvar_type = self.math_type
                math_type = math_object.math_type
                match = mvar_type.recursive_match(math_type, assign,
                                                  is_math_type=True)
                if match:
                    metavars.append(self)
                    metavar_objects.append(math_object)
                    # Assign self to math_object:
                    if assign:
                        self.children = [math_object]
                # match = True
            return match
        # Node
        elif node != math_object.node:
            # log.debug(f"distinct nodes {self.node, math_object.node}")
            return False

        # Mark bound vars in quantified expressions to distinguish them
        elif node in HAVE_BOUND_VARS:
            # Here self and math_object are assumed to be a quantified
            # proposition and children[1] is the bound variable.
            # We mark the bound variables in self and math_object with same
            # number so that we know that, say, 'x' in self and 'y' in
            # math_object are linked and should represent the same variable
            # everywhere
            bound_var_1 = self.children[1]
            bound_var_2 = math_object.children[1]
            self.mark_bound_vars(bound_var_1, bound_var_2)
            marked = True

        # Names
        if 'name' in self.info.keys():
            # For bound variables, do not use names, use numbers
            if self.is_bound_var():
                if not math_object.is_bound_var():
                    match = False
                # Here both are bound variables
                elif 'bound_var_number' not in self.info:
                    if 'bound_var_number' in math_object.info:
                        # Already appeared in math_object but not in self
                        match = False
                    else:
                        # Here both variable are unmarked. This means
                        # we are comparing two subexpressions with respect
                        # to which the variables are not local:
                        # names have a meaning
                        match = (self.info['name'] == math_object.info['name'])
                # From now on self.info['bound_var_number'] exists
                elif 'bound_var_number' not in math_object.info:
                    match = False
                # From now on both variables have a number
                elif (self.info['bound_var_number'] !=
                      math_object.info['bound_var_number']):
                    match = False
            else:  # Self is not bound var
                if math_object.is_bound_var():
                    match = False
                elif self.info['name'] != math_object.info['name']:
                    # None is a bound var
                    match = False
                    # log.debug(f"distinct names "
                    #        f"{self.info['name'], math_object.info['name']}")

        # Recursively test for math_types (but not math_types of math_type)
        #  (added: also when names)
        # FIXME: Remove to activate the fact that type of
        #  type is considered irrelevant:
        is_math_type = False
        if not is_math_type and not self.math_type.recursive_match(
                math_object.math_type, assign, is_math_type=True):
            # log.debug(f"distinct types {self.math_type}")
            # log.debug(f"math_object type     "
            #           f"{math_object.math_type.to_display()}")
            match = False

        # Recursively test matching for children
        elif len(self.children) != len(math_object.children):
            match = False
        else:
            for child0, child1 in zip(self.children, math_object.children):
                if not child0.recursive_match(child1, assign):
                    match = False

        # Unmark bound_vars, in prevision of future tests
        if marked:
            self.unmark_bound_vars(bound_var_1, bound_var_2)

        return match

    def math_object_from_metavar(self):
        if self not in PatternMathObject.metavars:
            return MathObject.NO_MATH_TYPE
        else:
            index = PatternMathObject.metavars.index(self)
            math_object = PatternMathObject.metavar_objects[index]
            return math_object

    def apply_matching(self):
        """
        Substitute metavars in self according to PatternMathObject.metavars and
        PatternMathObject.metavar_objects. Returns a MathObject if all
        metavars of self are in PatternMathObject.metavars,
        else a MathObject with some metavars.
        """

        if self.is_metavar():
            return self.math_object_from_metavar()
        elif self is PatternMathObject.NO_MATH_TYPE:
            return MathObject.NO_MATH_TYPE

        found_math_type = self.math_type.apply_matching()
        found_children = []
        for pattern_child in self.children:
            child = pattern_child.apply_matching()
            found_children.append(child)

        math_object = MathObject(node=self.node,
                                 info=self.info,
                                 children=found_children,
                                 bound_vars=self.bound_vars,
                                 math_type=found_math_type)
        return math_object

    @classmethod
    def set_definitions_for_implicit_use(cls, definitions):
        """
        Set definitions for implicit use.
        """
        MathObject.implicit_definitions = []
        MathObject.definition_patterns = []
        for definition in definitions:
            log.debug(f"Adding implicit use of "
                      f"{definition.pretty_name}")
            iff = definition.extract_iff()
            if iff:
                pattern = cls.from_math_object(iff)
                # log.debug(f"  Pattern: {pattern.to_display(format_='utf8')}")
                MathObject.implicit_definitions.append(definition)
                MathObject.definition_patterns.append(pattern)
                definition.implicit_use_activated = True

    @classmethod
    def from_universal_prop(cls, math_object: MathObject, mvars=None,
                            mvar_objects=None, insert_mvar=True):
        """
        Create a PatternMathObject by changing each universally quantified
        dummy var, and also each premise at the beginning of prop into ah
        metavar. e.g. if math_object corresponds to
                ∀ f: X→Y, ∀{A: set X}, ∀{x: X}, (x ∈ A → f x ∈ f '' A)
            then the fct will return
             ∀?₃ : (?₁)→(?₂), ∀?₄ ⊂ (?₁), ∀?₅ ∈ ?₁, ((?₆) ⇒ ?₃(?₅) ∈ ?₃(?₄))
        Note that all local constants are also turned into mvars. This fct
        will be called with initial_proof_state of some theorem, and the
        idea is that local constant that are not dummy var are implicit
        parameters of the theorem, and shoud be treated as dummy vars.

        The metavars in mvars should be substituted by the
        corresponding mvar_objects. insert_mvar will be set to FALSE for
        recursion when we are running through the part of prop where dummy
        var should NOT be replaced by mvars anymore. Namely, dummy var should be
        further replaced only in the body of a universal property in which
        dummy var has been replaced.

        Note that this function has side effect on mvars and mvar_objects:
        if lists are provided then they are updated with the new mvars.
        Except for recursion, the function should be called with an empty
        list, which will be filled by the mvars.
        """

        if mvars is None:
            mvars = []
        if mvar_objects is None:
            mvar_objects = []

        node = math_object.node
        info = copy(math_object.info)
        children = math_object.children
        math_type = math_object.math_type

        if math_object.is_local_constant():  # Search if replaced by mvar
            for mvar, mobj in zip(mvars, mvar_objects):
                if mobj.info["identifier"] == math_object.info["identifier"]:
                    return mvar

        # Recursively compute new math_type:
        new_math_type = PatternMathObject.NO_MATH_TYPE \
            if math_type is MathObject.NO_MATH_TYPE \
            else cls.from_universal_prop(math_type, mvars, mvar_objects, False)

        if math_object.is_local_constant():  # Make it a metavar!
            mvar = PatternMathObject.new_metavar(new_math_type)
            mvars.append(mvar)
            mvar_objects.append(math_object)
            return mvar

        # It remains to compute new children, by cases:
        if insert_mvar and math_object.is_for_all(is_math_type=True):
            # Replace var by mvar, and recursively in body
            typ = children[0]
            var = children[1]
            body = children[2]
            new_type = cls.from_universal_prop(typ, mvars, mvar_objects, False)
            mvar = PatternMathObject.new_metavar(new_type)
            mvars.append(mvar)
            mvar_objects.append(var)
            new_body = cls.from_universal_prop(body, mvars, mvar_objects, True)
            new_children = [new_type, mvar, new_body]

        elif insert_mvar and math_object.is_implication(is_math_type=True):
            # Replace premise by mvar:
            new_premise = cls.from_universal_prop(children[0], mvars,
                                                  mvar_objects, False)
            mvar = PatternMathObject.new_metavar(new_premise)
            mvars.append(mvar)
            mvar_objects.append(new_premise)
            new_conclusion = cls.from_universal_prop(children[1], mvars,
                                                     mvar_objects, False)
            new_children = [mvar, new_conclusion]

        else:
            new_children = [cls.from_universal_prop(child, mvars,
                                                    mvar_objects, False)
                            for child in children]

        return cls(node=node, info=info, children=new_children,
                   math_type=new_math_type, bound_vars=None)


def mvars_assign(mvars: [PatternMathObject],
                 math_objects: [MathObject],
                 start_idx=0) -> [[PatternMathObject]]:
    """
    Try to assign all math_objects to mvars, and return all possible lists of
    mvars where all objects have been successfully assigned. Assignation is
    done preferentially preserving the order of math_objects, and the order
    of the resulting list reflects that preference. For that the
    search in mvars starts at index start_idx.

    param mvars: a list of metavars, some of them assigned (i.e. have a child
    MathObject).
    """
    if not math_objects:  # All objects are assigned, success!
        return [mvars]

    success_list = []
    math_object = math_objects[0]
    # log.debug(f"Affecting {math_object.to_display(format_='utf8')}...")
    idx = start_idx  # Idx of mvar in mvars with ORIGINAL order.
    for mvar in mvars[start_idx:] + mvars[:start_idx]:  # Start at start_idx.
        if not mvar.children:  # Do not try to match assigned mvars
            match = mvar.match(math_object)
            if match:  # Replace mvar by its assigned version to get a new list.
                assigned_mvars = deepcopy(mvars)
                assigned_mvar = assigned_mvars[idx]
                assigned_mvar.match(math_object, assign=True)
                assigned_mvar.set_explicitly_assigned()
                success_list.append((assigned_mvars, idx))
        idx = idx + 1 if idx < len(mvars) else 0

    # Now the recursion: for each success, try to match the remaining obj.
    new_math_objects = math_objects[1:]
    assigned_mvars_list = []
    for assigned_mvars, idx in success_list:
        new_assigned_mvars = mvars_assign(assigned_mvars, new_math_objects,
                                          start_idx=idx + 1)
        assigned_mvars_list.extend(new_assigned_mvars)
    return assigned_mvars_list


def first_unassigned_mvar(mvars: [PatternMathObject]):
    """
    Return first unassigned mvar in mvars, if any.
    """
    for mvar in mvars:
        if mvar.is_unassigned_mvar():
            return mvar
    return None


def mvars_assign_some(mvars: [PatternMathObject],
                      math_objects: [MathObject]) -> [[PatternMathObject]]:
    """
    Try to assign some math_objects to mvars, and return ONE possible list of
    mvars where all mvars have been successfully assigned.

    Note that the mvars_assign() function tries to assign all objects to some
    mvars, whereas mvars_assign_some() tries to assign all mvars to some object.

    param mvars: a list of metavars, some of them assigned (i.e. have a child
    MathObject).
    """

    mvar = first_unassigned_mvar(mvars)
    if not mvar:  # ALl mvars assigned!
        return mvars

    # Try to assign mvar
    success_object = None
    for math_object in math_objects:
        match = mvar.match(math_object)
        if match:
            success_object = math_object
            mvar.match(math_object, assign=True)
            mvar.set_explicitly_assigned()
            break

    if not success_object:  # No way to assign all mvars
        return None

    # Now the recursion: assign mvars to remaining objects
    new_math_objects = math_objects[:]  # No side effect on math_objects!
    new_math_objects.remove(success_object)

    return mvars_assign_some(mvars, new_math_objects)

# class Mvars(list):
#     """
#     A class for storing lists of assigned metavars and info about their
#     assignments. Attribute _assignments is a list of the same length as self,
#     and entries that are not None contain math_objects the corresponding mvar
#     has been assigned to.
#     """
#     def __init__(self, arg):
#         super().__init__(arg)
#         self._assignments = [None] * len(self)
#
#     def append(self, object_) -> None:
#         super().append(self)
#         self._assignments.append(None)
#
#     def remove_last_unassigned(self, objects):
#         while not self._assignments[-1]:
#             self.pop()
#             self._assignments.pop()
#
#     def assign(self, math_objects, start_idx=0):
#         """
#         Try to assign all math_objects to mvars, and return all possible lists of
#         mvars where all objects have been successfully assigned. Assignation is
#         done preferentially preserving the order of math_objects, and the order
#         of the resulting list reflects that preference. For that the
#         search in mvars starts at index start_idx.
#
#         param mvars: a list of metavars, some of them assigned (i.e. have a child
#         MathObject)g.
#         """
#         mvars = self
#         if not math_objects:  # All objects are assigned, success!
#             return [mvars]
#
#         success_list = []
#         math_object = math_objects[0]
#         # log.debug(f"Affecting {math_object.to_display(format_='utf8')}...")
#         idx = start_idx  # Idx of mvar in mvars with ORIGINAL order.
#         for mvar in mvars[start_idx:] + mvars[
#                                         :start_idx]:  # Start at start_idx.
#             if not mvar.children:  # Do not try to match assigned mvars
#                 match = mvar.match(math_object)
#                 if match:
#                     # Replace mvar by its assigned version to get a new list.
#                     assigned_mvars = deepcopy(mvars)
#                     assigned_mvars._assignments[idx] = math_object
#                     assigned_mvar = assigned_mvars[idx]
#                     assigned_mvar.match(math_object, assign=True)
#                     success_list.append((assigned_mvars, idx))
#             idx = idx + 1 if idx < len(mvars) else 0
#
#         # Now the recursion: for each success, try to match the remaining obj.
#         new_math_objects = math_objects[1:]
#         assigned_mvars_list = []
#         for assigned_mvars, idx in success_list:
#             new_assigned_mvars = assigned_mvars.assign(new_math_objects,
#                                                        start_idx=idx + 1)
#             assigned_mvars_list.extend(new_assigned_mvars)
#         return assigned_mvars_list


PatternMathObject.NO_MATH_TYPE = PatternMathObject(node="not provided",
                                                   info={},
                                                   children=[],
                                                   bound_vars=[],
                                                   math_type=None)


#########
# TESTS #
#########

if __name__ == '__main__':
    from deaduction.pylib.mathobj.lean_analysis import (
                                            lean_expr_with_type_grammar,
                                            LeanEntryVisitor)
    import deaduction.pylib.config.i18n
    import logging
    from deaduction.pylib import logger
    logger.configure(domains='__main__', display_level='debug')

    targets_analysis = []
    targets_analysis.append("""¿¿¿property¿[pp_type: x ∈ A ∩ B ↔ x ∈ A ∧ x ∈ B¿]: METAVAR¿[name: _mlocal._fresh.231.31595¿]¿= PROP_IFF¿[type: PROP¿]¿(PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.230.21962¿]¿, SET_INTER¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.230.21950¿]¿)¿]¿(LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.230.21954¿]¿, LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.230.21959¿]¿)¿)¿, PROP_AND¿[type: PROP¿]¿(PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.230.21962¿]¿, LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.230.21954¿]¿)¿, PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.230.21962¿]¿, LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.230.21959¿]¿)¿)¿)""")
    targets_analysis.append("""¿¿¿property¿[pp_type: x ∈ A ∪ B ↔ x ∈ A ∨ x ∈ B¿]: METAVAR¿[name: _mlocal._fresh.326.17524¿]¿= PROP_IFF¿[type: PROP¿]¿(PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.325.14324¿]¿, SET_UNION¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.325.14312¿]¿)¿]¿(LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.325.14316¿]¿, LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.325.14321¿]¿)¿)¿, PROP_OR¿[type: PROP¿]¿(PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.325.14324¿]¿, LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.325.14316¿]¿)¿, PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.325.14324¿]¿, LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.325.14321¿]¿)¿)¿)""")
    targets_analysis.append("""¿¿¿property¿[pp_type: injective f ↔ ∀ (x y : X), f x = f y → x = y¿]: METAVAR¿[name: _mlocal._fresh.307.5511¿]¿= PROP_IFF¿[type: PROP¿]¿(APPLICATION¿[type: PROP¿]¿(APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.307.5242¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.307.5244¿]¿)¿, PROP¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.307.5869¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.307.5242¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.307.5869¿]¿)¿, PROP¿)¿)¿]¿(CONSTANT¿[name: injective¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.307.5896¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.307.5908¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.307.5896¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.307.5908¿]¿)¿, PROP¿)¿)¿)¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.307.5242¿]¿)¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.307.5244¿]¿)¿, LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.307.5247¿]¿)¿, QUANT_∀¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.307.5242¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.307.5927¿]¿, QUANT_∀¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.307.5242¿]¿, LOCAL_CONSTANT¿[name: y¿/ identifier: _fresh.307.5937¿]¿, PROP_IMPLIES¿[type: PROP¿]¿(PROP_EQUAL¿[type: PROP¿]¿(APPLICATION¿[type: LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.307.5244¿]¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.307.5247¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.307.5927¿]¿)¿, APPLICATION¿[type: LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.307.5244¿]¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.307.5247¿]¿, LOCAL_CONSTANT¿[name: y¿/ identifier: _fresh.307.5937¿]¿)¿)¿, PROP_EQUAL¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.307.5927¿]¿, LOCAL_CONSTANT¿[name: y¿/ identifier: _fresh.307.5937¿]¿)¿)¿)¿)¿)""")
    hypo = """¿¿¿property¿[pp_type: x ∈ A ∩ (B ∪ C)¿]: LOCAL_CONSTANT¿[name: H¿/ identifier: 0._fresh.340.35755¿]¿= PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.340.35743¿]¿, SET_INTER¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.338.29051¿]¿)¿]¿(LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.338.29052¿]¿, SET_UNION¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.338.29051¿]¿)¿]¿(LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.338.29054¿]¿, LOCAL_CONSTANT¿[name: C¿/ identifier: 0._fresh.338.29056¿]¿)¿)¿)"""
    # Statement of theorem_image_directe
    targets_analysis.append("""¿¿¿property¿[pp_type: ∀ (f : X → Y) {A : set X} {x : X}, x ∈ A → f x ∈ f '' A¿]: METAVAR¿[name: _mlocal._fresh.512.3669¿]¿= QUANT_∀¿[type: PROP¿]¿(FUNCTION¿[type: TYPE¿]¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.508.4189¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.508.4191¿]¿)¿, LOCAL_CONSTANT¿[name: f¿/ identifier: _fresh.512.4028¿]¿, QUANT_∀¿[type: PROP¿]¿(SET¿[type: TYPE¿]¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.508.4189¿]¿)¿, LOCAL_CONSTANT¿[name: A¿/ identifier: _fresh.512.4040¿]¿, QUANT_∀¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.508.4189¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.512.4050¿]¿, PROP_IMPLIES¿[type: PROP¿]¿(PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.512.4050¿]¿, LOCAL_CONSTANT¿[name: A¿/ identifier: _fresh.512.4040¿]¿)¿, PROP_BELONGS¿[type: PROP¿]¿(APPLICATION¿[type: LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.508.4191¿]¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: _fresh.512.4028¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.512.4050¿]¿)¿, SET_IMAGE¿[type: SET¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.508.4191¿]¿)¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: _fresh.512.4028¿]¿, LOCAL_CONSTANT¿[name: A¿/ identifier: _fresh.512.4040¿]¿)¿)¿)¿)¿)¿)""")
    # The same but with implicit vars
    targets_analysis.append("""¿¿¿property¿[pp_type: ∀ {X Y : Type} (f : X → Y) {A : set X} {x : X}, x ∈ A → f x ∈ f '' A¿]: LOCAL_CONSTANT¿[name: H¿/ identifier: 0._fresh.616.13669¿]¿= QUANT_∀¿[type: PROP¿]¿(TYPE¿[type: TYPE¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.616.13727¿]¿, QUANT_∀¿[type: PROP¿]¿(TYPE¿[type: TYPE¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.616.13743¿]¿, QUANT_∀¿[type: PROP¿]¿(FUNCTION¿[type: TYPE¿]¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.616.13727¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.616.13743¿]¿)¿, LOCAL_CONSTANT¿[name: f¿/ identifier: _fresh.616.13763¿]¿, QUANT_∀¿[type: PROP¿]¿(SET¿[type: TYPE¿]¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.616.13727¿]¿)¿, LOCAL_CONSTANT¿[name: A¿/ identifier: _fresh.616.13780¿]¿, QUANT_∀¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.616.13727¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.616.13790¿]¿, PROP_IMPLIES¿[type: PROP¿]¿(PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.616.13790¿]¿, LOCAL_CONSTANT¿[name: A¿/ identifier: _fresh.616.13780¿]¿)¿, PROP_BELONGS¿[type: PROP¿]¿(APPLICATION¿[type: LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.616.13743¿]¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: _fresh.616.13763¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.616.13790¿]¿)¿, SET_IMAGE¿[type: SET¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.616.13743¿]¿)¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: _fresh.616.13763¿]¿, LOCAL_CONSTANT¿[name: A¿/ identifier: _fresh.616.13780¿]¿)¿)¿)¿)¿)¿)¿)¿)""")
    # Test is_and
    math_types = []
    for target in targets_analysis:
        tree = lean_expr_with_type_grammar.parse(target)
        mo = LeanEntryVisitor().visit(tree)
        mt = mo.math_type
        math_types.append(mt)

    # pattern = PatternMathObject.from_math_object(mt)
    mt = math_types[4]
    mvars = []
    pattern = PatternMathObject.from_universal_prop(mt, mvars)
    print("Pattern:")
    print("    ", pattern.to_display(format_="utf8"))
    print("mvars:", [mvar.to_display(format_="utf8") for mvar in mvars])
    print("mvars types:", [mvar.math_type.to_display(format_="utf8") for mvar
                           in mvars])
    # print("Pattern matches left?")
    # print(pattern.match(left))

    hypo_analysis = []
    # hypo_analysis.append("""¿¿¿object: LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.670.22324¿]¿= TYPE""")
    # hypo_analysis.append("""¿¿¿object: LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.670.22326¿]¿= TYPE""")
    hypo_analysis.append("""¿¿¿object: LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.669.20887¿]¿= FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.670.22324¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.670.22326¿]¿)""")
    hypo_analysis.append("""¿¿¿property¿[pp_type: x ∈ A¿]: LOCAL_CONSTANT¿[name: H¿/ identifier: 0._fresh.669.20893¿]¿= PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.669.20891¿]¿, LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.669.20889¿]¿)""")
    hypos = []
    for hypo in hypo_analysis:
        tree = lean_expr_with_type_grammar.parse(hypo)
        mo = LeanEntryVisitor().visit(tree)
        # mt = mo.math_type
        hypos.append(mo)

    hypo0 = hypos[0]
    hypo1 = hypos[1]
    print("hypos:", [hypo.to_display(format_="utf8") for hypo in hypos])
    hypos0 = [hypo0]
    hypos1 = [hypo1]
    ass_mvars = mvars_assign(mvars, hypos0)
    ass_mvars2 = mvars_assign(ass_mvars[0], hypos1)

    print("Assigned lists:")
    print("     ", [[mvar.children[0].to_display(format_="utf8") if
                     mvar.children else mvar.to_display(format_="utf8")
                     for mvar in mvars]
                    for mvars in ass_mvars])
    print("     ", [[mvar.children[0].to_display(format_="utf8") if
                     mvar.children else mvar.to_display(format_="utf8")
                     for mvar in mvars]
                    for mvars in ass_mvars2])


    MathObject.definition_patterns.append(pattern)
    tree = lean_expr_with_type_grammar.parse(hypo)
    mo = LeanEntryVisitor().visit(tree)
    mt = mo.math_type
    print(f"{mt.to_display()} matches {pattern.to_display()} ?")
    print(pattern.children[0].match(mt))
    print(pattern.children[1].apply_matching().to_display())



