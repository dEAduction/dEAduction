"""
pattern_math_objects.py : provide the PatternMathObject class.

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

import logging
if __name__ == "__main__":
    import deaduction.pylib.config.i18n

from typing import Optional, Union
from copy import copy

from deaduction.pylib.utils import tree_list
from .pattern_parser import tree_from_str
from deaduction.pylib.math_display.nodes import Node
# from deaduction.pylib.mathobj import MathObject, BoundVar

from deaduction.pylib.math_display import PatternInit
from deaduction.pylib.mathobj.math_object import MathObject, BoundVar
from deaduction.pylib.math_display import metanodes

log = logging.getLogger(__name__)
global _


class PatternMathObject(MathObject):
    """
    A class for MathObject that may contain metavariables. Metavariables
    are represented by PatternMathObject whose node is 'METAVAR".
    e.g. the PatternMathObject representing the definition of injectivity
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

    After a successful matching test, the matching values of the metavars are
    stored in the metavar_objects class attribute as a list of MathObject
    instances. Then the apply_matching() method will substitute metavars in
    some MathObject. For instance after the previous example, if right is the
    PatternMathObject
        (∀x ∈ metavar_26, ∀x' ∈ metavar_26,
        (metavar_28(x) = metavar_28(x') ⇒ x = x'))
    then right.apply_matching() will produce the MathObject
        ∀x ∈ X, ∀x' ∈ X, (g∘f(x) = g∘f(x') ⇒ x = x')
    """
    metavar_nb = 0
    metavars_csts           = []  # List of all metavars in all patterns
    loc_csts_for_metavars   = []  # and corresponding local constants
    __tmp_metavars_csts         = None
    __tmp_loc_csts_for_metavars = None
    __metavars        = None  # Temporary list of mvars
    __metavar_objects = None  # Objects matching metavars (see self.match)

    __original_bound_vars = None
    __copied_bound_vars = None

    def __init__(self, node, info, children,
                 math_type=None,
                 imperative_matching=False):
        """
        Init self as a MathObject, plus metavars list.
        imperative_matching = True means self will not match a MathObject
        with unknown math_type.
        """
        self.metavars = []
        self.metavar_objects = []
        super().__init__(node=node,
                         info=info,
                         children=children,
                         math_type=math_type)
        self.imperative_matching = imperative_matching

    def __repr__(self):
        return self.debug_repr('PMO')

    # @property
    # def metavars(self):
    #     return self._metavars
    #
    # @property
    # def metavar_objects(self):
    #     return self._metavar_objects

    @classmethod
    def new_metavar(cls, math_type):
        return MetaVar(math_type=math_type)

    @classmethod
    def from_tree(cls, tree, metavars):
        """
        Recursive method to create a PMO from a Tree instance,
        with attributes node, children and type_. A list of the metavars used in
        self is furnished to which new metavars are appended; the index of
        the metavars in the list corresponds to the numbers in the pattern
        string, e.g. "?0" --> metavar at index 0 in metavars.
        """

        # if tree.node == '*INEQUALITY':
        #     pass  # debug

        # (1) Math_type
        math_type = (cls.from_tree(tree.type_, metavars=metavars) if tree.type_
                     else PatternMathObject.NO_MATH_TYPE)

        # (2) Children
        children_pmo = [cls.from_tree(child, metavars=metavars)
                        for child in tree.children]

        # (3) Node
        node = tree.node
        if node.startswith('!'):
            # Imperative type node
            imperative = True
            node = node[1:]
        else:
            imperative = False

        # -----> (3a) Children joker
        if node == "...":  # Joker for any number of children
            pmo = POMPOMPOM

        # -----> (3b) Case of a metavar, e.g. ?7
        elif node.startswith('?'):
            nb_str = node[1:]
            # If no nb then take first available
            metavar_nb = int(nb_str) if nb_str else len(metavars)
            assert metavar_nb >= 0
            metavars.extend([None] * (metavar_nb + 1 - len(metavars)))
            pmo = metavars[metavar_nb]
            if not pmo:  # Create new metavar and store it in metavars
                pmo = PatternMathObject.new_metavar(math_type)
                metavars[metavar_nb] = pmo

        # -----> (3c) Info
        elif "/" in node:
            node, info = node.split('/')
            key, value = info.split('=')
            info = {key: value}
            name = info.get('name')
            if name and name.endswith('.BoundVar'):
                # if name == 'u.BoundVar':
                #     print("debug")
                # Remove suffix and create a BoundVar
                # info['name'] = info['name'][:-len('.BoundVar')]
                pmo = BoundVar(node=node,
                               info=info,
                               math_type=math_type,
                               children=children_pmo,
                               parent=None)
            else:
                pmo = cls(node=node, children=children_pmo, math_type=math_type,
                          info=info, imperative_matching=imperative)

        # -----> (3d) Generic case
        else:
            pmo = cls(node=node, children=children_pmo, math_type=math_type,
                      info={}, imperative_matching=imperative)

        return pmo

    @classmethod
    def from_string(cls, s: str, metavars=None):
        if metavars is None:
            metavars = []
        tree = tree_from_str(s)
        pmo = cls.from_tree(tree, metavars)
        return pmo

    @classmethod
    def from_math_object(cls, math_object: MathObject,
                         turn_lc_into_mvar=True):
        cls.__tmp_loc_csts_for_metavars = []
        cls.__tmp_metavars_csts         = []
        cls.__original_bound_vars       = []
        cls.__copied_bound_vars         = []

        pattern = cls.__from_math_object(math_object,
                                         turn_lc_into_mvar=turn_lc_into_mvar)
        pattern.metavars = cls.__tmp_metavars_csts
        return pattern

    @classmethod
    def metavar_from_loc_constant(cls, loc_constant: MathObject):
        """
        Return a metavar that replaces loc_constant.
        """

        assert loc_constant.is_local_constant()
        metavars = cls.__tmp_metavars_csts
        loc_csts = cls.__tmp_loc_csts_for_metavars

        if loc_constant in loc_csts:
            metavar = metavars[loc_csts.index(loc_constant)]
            # log.debug(f"   Mo is metavar n°{metavar.info['nb']}")
            return metavar

        else:
            # Turn math_type into a PatternMathObject,
            # then create a new metavar.
            if loc_constant.math_type is MathObject.NO_MATH_TYPE:
                math_type = PatternMathObject.NO_MATH_TYPE
            else:
                math_type = cls.__from_math_object(loc_constant.math_type,
                                                   turn_lc_into_mvar=True)
            new_metavar = cls.new_metavar(math_type)
            metavars.append(new_metavar)
            cls.metavars_csts.append(new_metavar)
            loc_csts.append(loc_constant)
            cls.loc_csts_for_metavars.append(loc_constant)
            return new_metavar

    @classmethod
    def __from_math_object(cls, math_object: MathObject,
                           turn_lc_into_mvar):
        """
        Produce a PatterMathObject from math_object by replacing all local
        constants which are not bound variables by fresh metavars.
        Of course all occurrences of a given local constant must be replaced
        by the same metavar.
        This is obviously a recursive method. The lists loc_csts, metavars
        allow to keep track of the correspondence between the local
        constants that have been previously replaced and the metavars.
        """
        # log.debug(f"Patterning mo {math_object.to_display()}")
        # metavars = cls.__tmp_metavars_csts
        # loc_csts = cls.__tmp_loc_csts_for_metavars

        if math_object.is_bound_var:
            # Copy bound var ONCE, and then always refer to the same duplicate.
            return math_object.smart_duplicate(cls.__original_bound_vars,
                                               cls.__copied_bound_vars,
                                               keep_name=True)

        elif math_object.is_local_constant() and turn_lc_into_mvar:
            return cls.metavar_from_loc_constant(math_object)

        else:
            node = math_object.node

            info = math_object.info  # Useless??
            # log.debug("   ->Children:")
            children = []
            for child in math_object.children:
                new_child = cls.__from_math_object(child,
                                                   turn_lc_into_mvar=turn_lc_into_mvar)
                children.append(new_child)
            if math_object.math_type is math_object.NO_MATH_TYPE:
                math_type = cls.NO_MATH_TYPE
            else:
                # log.debug("   ->Math type:")
                math_type = cls.__from_math_object(math_object.math_type,
                                                   turn_lc_into_mvar=turn_lc_into_mvar)

            pattern_math_object = cls(node=node,
                                      info=info,
                                      children=children,
                                      math_type=math_type)
            # log.debug(f"   ->pmo: {pmo.to_display()}")
            return pattern_math_object

    def __eq__(self, other):
        """
        Redefine __eq__, otherwise all METAVARS are equals!?
        """
        return self is other

    @property
    def is_metavar(self):
        return isinstance(self, MetaVar)

    def is_no_math_type(self):
        return self is self.NO_MATH_TYPE

    def assign_matched_metavars(self):
        """
        Assign all metavars in self.metavars to the corresponding MathObject in
        self.metavar_objects.
        """
        for mvar, math_object in zip(self.metavars, self.metavar_objects):
            mvar.assigned_math_object = math_object

    @classmethod
    def clear_cls_metavars(cls):
        cls.__metavars = []
        cls.__metavar_objects = []

    def match(self,
              math_object: MathObject,
              successive_matching=False,
              first_of_successive=False,
              symmetric_match=False,
              debug=False,
              return_msg=False):
        """
        Test if math_object match self. This is a recursive test.
        The cls.__metavars list contains the metavars that have
        already been matched against a math_object, which is stored with the
        same index in the cls.__.metavar_objects list.
        e.g. 'g∘f is injective' matches 'metavar_28 is injective'
        (note that math_types of metavars should also match).
        In case of successful matching, the metavars and metavar_objects
        lists are stored as self's attributes. The corresponding MathObject
        may be obtained by applying the math_object_from_matching() method.

        To perform multiple simultaneous matching,
        use successive_matchings=True. Then the cumulative
        metavars/metavars_objects are stored in self.metavars.
        The matchings can be assigned by using the assigned_matched_metavars()
        method.

        Return either a bool, or (bool, str) if return_msg is True.
        """

        if not successive_matching or first_of_successive:
            self.__metavars = []
            self.__metavar_objects = []

        # Swallow copy of cls private metavars will be used for matching
        metavars = [mvar for mvar in self.__metavars]
        metavar_objects = [mvar for mvar in self.__metavar_objects]

        match, msg = self.recursive_match(math_object, metavars,
                                          metavar_objects,
                                          symmetric_match, debug,
                                          return_msg)
        if match:
            self.metavars = metavars
            self.metavar_objects = metavar_objects
            if successive_matching or first_of_successive:
                # Add new metavars matching to private
                length = len(self.__metavars)
                self.__metavars.extend(metavars[length:])
                self.__metavar_objects.extend(metavar_objects[length:])
        # log.debug(f"Matching {self.node} and {math_object.node}...")
        # list_ = [(PatternMathObject.__metavars[idx].to_display(),
        #           PatternMathObject.__metavar_objects[idx].to_display())
        #          for idx in range(len(PatternMathObject.__metavars))]
        # log.debug(f"    Metavars, objects: {list_}")
        if not return_msg:
            return match
        else:
            return match, msg

    def recursive_match(self, math_object: MathObject,
                        metavars, metavar_objects, symmetric_match=False,
                        debug=False, return_msg=False) -> (bool, str):
        """
        Test if math_object match self. This is a recursive test.
        The list metavars contains the metavars that have already been
        matched against a math_object, and this object is stored with the same
        index in the metavar_objects list.
        """

        # debug = True
        self_ = self  # Can be substituted, e.g. case of assigned_math_object
        children = self.children
        node = self.node
        self_type = self.math_type
        # DEBUG
        if not isinstance(self_type, PatternMathObject):
            print(f"{self_type} is not a PatternMathObject!!!")

        if return_msg:
            error_msg = self.try_to_display() + " ≠match "
            mo_display = math_object.try_to_display()
        else:
            error_msg = ""
            mo_display = ""

        # -----------------------------------------------
        # Case of NO_MATH_TYPE (avoid infinite recursion!)
        # Maybe this is too liberal??
        if self.is_no_math_type():
            return True, "No math type"
        elif math_object.is_no_math_type():
            if self.imperative_matching:
                if debug:
                    log.debug(f"Types mismatch: imperative matching")

                return False, error_msg + "no math type"
            else:
                return True, "Other is no math type"

        # --------------------- METAVARS --------------------------
        elif isinstance(self, MetaVar):
            # If self has already been identified, math_object matches self
            #   iff it is equal to the corresponding item in metavar_objects
            # If not, then self matches with math_object providing their
            #   math_types match. In this case, identify metavar.
            if self.assigned_math_object:
                # self is replaced by self_, and we go on testing for matching
                self_ = self.assigned_math_object
                children = self_.children
                node = self_.node
                self_type = self_.math_type

            # In all other cases we will decide (and return) HERE:
            elif self in metavars:
                corresponding_object = self.matched_math_object(metavars,
                                                                metavar_objects)
                match = MathObject.__eq__(math_object, corresponding_object)

                if not match:
                    if debug:
                        log.debug(f"Mismatch: matched mvar {self} vs"
                                  f" {math_object}")
                    return False, error_msg + mo_display + "(mvar)"
                else:
                    return True, ""
            else:
                mvar_type = self.math_type
                math_type = math_object.math_type
                match, type_msg = mvar_type.recursive_match(math_type,
                                                            metavars,
                                                            metavar_objects,
                                                            return_msg=return_msg)
                if match:
                    metavars.append(self)
                    metavar_objects.append(math_object)
                    # FIXME: make a PMO deep_copy?
                    # self.assigned_math_object = math_object
                    return True, ""
                elif debug:
                    log.debug(f"Types mismatch: type of mvar {self} vs"
                              f" {math_object}")
                    return (False, error_msg + mo_display
                            + "(types of mvars)")

        #############
        # Test node #
        #############
        if node != math_object.node:
            if node in metanodes and metanodes[node](math_object):
                # e.g. metanodes[*INEQUALITIES] is a callable
                #  that tests if object is an inequality
                return True, ""
            # elif (math_object.node in metanodes
            #         and metanodes[math_object.node](self_)):
            #     # (NB: math_object could be a PatternMathObject)
            #     return True, ""
            else:
                if debug:
                    log.debug(f"Nodes mismatch: {node} vs {math_object.node}")
                return False, error_msg + mo_display + "(nodes)"

        ###############################
        # Test bound var, name, value #
        ###############################
        # Testing is_bound_var does not seem to be relevant, since this is
        # determined by the node of self's parent. Furthermore, self could be
        # a local constant with name RealSubGroup which is a bound var,
        # but self.is_bound_var fails.
        # NB: '?' is a joker (match any name, any value)
        if (self_.name and self_.name != '?' and self_.name !=
              math_object.name):
            if debug:
                log.debug(f"Names mismatch: {self_} vs {math_object}")
            return False, error_msg + mo_display + "(names)"
        if self_.value and self_.value != '?' \
                and self_.value != math_object.value:
            if debug:
                log.debug(f"Values mismatch: {self_} vs {math_object}")
            return False, error_msg + mo_display + "(value)"
        if self_.binder_info and self_.binder_info != '?' \
                and self_.binder_info != math_object.binder_info:
            if debug:
                log.debug(f"Binder mismatch: {self_} vs {math_object}")
            return False, error_msg + mo_display + "(binder)"

        ##################################
        # Recursively test for math_type #
        ##################################
        match_type, msg = self_.math_type.recursive_match(math_object.math_type,
                                                          metavars,
                                                          metavar_objects,
                                                          return_msg=return_msg)
        if not match_type:
            if debug:
                log.debug(f"Types mismatch: {self_} vs {math_object}")
            return False, msg

        #################################
        # Recursively test for children #
        #################################
        elif len(children) >= len(math_object.children) + 2:
            if debug:
                log.debug(f"Children nb mismatch: {self_} vs {math_object}")
            return False, error_msg + "(#children)"
        elif len(children) < len(math_object.children) + 2:
            nb_c = len(children)
            nb_c_mo = len(math_object.children)
            # Case of undetermined nb of children: insert new mvars
            if POMPOMPOM in children:
                more_children = [PatternMathObject.new_metavar(
                    PatternMathObject.NO_MATH_TYPE)
                    for i in range(nb_c_mo + 1 - nb_c)]
                index = children.index(POMPOMPOM)
                children = children.copy()  # DO NOT modify self.children!!
                children = (children[:index]
                            + more_children
                            + children[index+1:])
            elif nb_c != nb_c_mo:
                if debug:
                    log.debug(f"Children nb mismatch: {self_} vs {math_object}")
                return False, error_msg + "(#children)"

        match = True
        bound_var_1 = None
        bound_var_2 = None
        ##############
        # Bound vars #
        ##############
        # Mark bound vars in quantified expressions to distinguish them
        # if self.node in self.HAVE_BOUND_VARS:
        if self_.has_bound_var():
            # Here self and other are assumed to be a quantified proposition
            # and children[1] is the bound variable.
            # We mark the bound variables in self and other with same number
            # so that we know that, say, 'x' in self and 'y' in other are
            # linked and should represent the same variable everywhere
            bound_var_1 = children[1]
            if isinstance(bound_var_1, BoundVar):
                bound_var_2 = math_object.children[1]
                bound_var_1.mark_identical_bound_vars(bound_var_2)

        ############
        # Children #
        ############
        child_msg = ""
        for child0, child1 in zip(children, math_object.children):
            child_match, child_msg = child0.recursive_match(child1, metavars,
                                                            metavar_objects,
                                                            return_msg=return_msg)
            if not child_match:
                if debug:
                    log.debug(f"Children mismatch: {self_} vs {math_object}")
                match = False

        # Unmark bound_vars
        if bound_var_1 and not isinstance(bound_var_1, MetaVar):
            bound_var_1.unmark_bound_var()
            bound_var_2.unmark_bound_var()

        # log.debug(f"... {match}")
        if not match:
            return False, child_msg
        else:
            return True, ""

    def math_object_from_matching(self, metavars=None, metavars_objects=None,
                                  original_bound_vars=None,
                                  copied_bound_vars=None):
        """
        Substitute metavars in self according to self.metavars and
        self.metavar_objects. Returns a MathObject if all
        metavars of self are in self.metavars,
        else a MathObject with some metavars.
        """

        if original_bound_vars is None:
            original_bound_vars = []
        if copied_bound_vars is None:
            copied_bound_vars = []

        # (1) Metavars:
        if metavars is None:
            metavars = self.metavars
            metavars_objects = self.metavar_objects

        if isinstance(self, MetaVar):
            return self.matched_math_object(metavars, metavars_objects)
        elif self is PatternMathObject.NO_MATH_TYPE:
            return MathObject.NO_MATH_TYPE

        # (2) Generic objects (NOT including BoundVar)
        matched_math_type = self.math_type.math_object_from_matching(
                                                    metavars,
                                                    metavars_objects,
                                                    original_bound_vars,
                                                    copied_bound_vars)
        matched_children = [child.math_object_from_matching(metavars,
                                                            metavars_objects,
                                                            original_bound_vars,
                                                            copied_bound_vars)
                            for child in self.children]

        math_object = MathObject(node=self.node,
                                 info=self.info,
                                 children=matched_children,
                                 math_type=matched_math_type)

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
                definition.implicit_use_activated = True  # Obsolete

    def first_mvar(self, unassigned=True):
        """
        Return the first (unassigned) mvar of self, if any.
        """

        if self.is_metavar and not (unassigned and self.assigned_math_object):
            return self
        else:
            for child in self.children:
                mvar = child.first_mvar(unassigned)
                if mvar:
                    return mvar

    def all_mvars(self, unassigned=False):
        """
        Return the ordered list of all [unassigned] mvars appearing in self.
        """

        if self.is_metavar and not (unassigned and self.assigned_math_object):
            return [self]
        else:
            mvars = []
            for child in self.children:
                mvars.extend(child.all_mvars(unassigned=unassigned))
            return mvars


PatternMathObject.NO_MATH_TYPE = PatternMathObject(node="not provided",
                                                   info={},
                                                   children=[],
                                                   math_type=None)


POMPOMPOM = PatternMathObject(node="...", info={}, children=[])


class MetaVar(PatternMathObject):
    """
    A class to store metavars that occur in PatternMathObject. The main use
    is that MVAR can be affected to a MathObject. This modifies their display.
    """

    adjustable_math_types = ["*NUMBER_TYPES"]

    _assigned_math_object: Optional[MathObject] = None

    metavar_nb: int = 0  # Class attribute (counter)

    def __init__(self, node='METAVAR', info=None, children=None,
                 math_type=None):
        """
        To init a metavar we just need its math_type.
        Nevertheless, we include the other parameters for compatibility with
        MathObject __init__, e.g. for the deepcopy() method.
        """

        # if not math_type or math_type is MathObject.NO_MATH_TYPE:
        #     math_type = PatternMathObject.NO_MATH_TYPE
        MetaVar.metavar_nb += 1
        super().__init__(node='METAVAR',
                         info={'nb': MetaVar.metavar_nb},
                         children=[],
                         math_type=math_type)

    def __eq__(self, other):
        """
        Redefine __eq__, otherwise all METAVARS are equals!?
        """
        eq = (self is other)  # or self.assigned_math_object == other
        return eq

    def __repr__(self):
        math_obj = self.assigned_math_object
        rep = f"MV n°{self.nb}" if not math_obj else \
            f"assigned MV n°{self._info.get('nb')}= {math_obj}"
        return rep

    @property
    def nb(self):
        return self.info['nb']

    @classmethod
    def deep_copy(cls, self, original_bound_vars=None, copied_bound_vars=None,
                  original_metavars=None, copied_metavars=None):
        """
        Deep copy self, including assigned math object.
        """
        new_mvar = super().deep_copy(self, original_bound_vars,
                                     copied_bound_vars,
                                     original_metavars,
                                     copied_metavars)
        mmo = self.assigned_math_object
        if mmo:
            new_mvar.assigned_math_object = mmo.deep_copy(mmo,
                                                          original_bound_vars,
                                                          copied_bound_vars,
                                                          original_metavars,
                                                          copied_metavars)
        return new_mvar

    @property
    def assigned_math_object(self):
        return self._assigned_math_object

    @assigned_math_object.setter
    def assigned_math_object(self, math_object):
        self._assigned_math_object = math_object

    @property
    def assigned_math_type(self):
        if self.assigned_math_object:
            return self.assigned_math_object.math_type

    def check_type_msg(self):
        expected_type = self._math_type.try_to_display(text=True, is_type=True)
        assigned_type = self.assigned_math_type.try_to_display(text=True,
                                                               is_type=True)
        msg = _("Expecting {}, but this is {}").format(
            expected_type, assigned_type)
        return msg

    def check_type(self):
        """
        Check if self._math_type match assigned type.
        Return "" if so, detailed msg if not.
        """
        if isinstance(self._math_type, PatternMathObject):
            test, msg = self._math_type.match(self.assigned_math_type,
                                              return_msg=True)
        elif isinstance(self.assigned_math_type, PatternMathObject):
            test, msg = self.assigned_math_type.match(self._math_type,
                                                      return_msg=True)
        else:  # Use MathObject.is_equal_to()
            test, msg = self.assigned_math_type.is_equal_to(self._math_type,
                                                   use_assigned_math_obj=True,
                                                            return_msg=True)
        if test:
            return ""
        else:
            return self.check_type_msg()  # + "/" + msg

    def matched_math_object(self, metavars, metavar_objects):
        """
        If some MathObject has been matched with self in the match() method,
        then return this object.
        """
        if self not in metavars:
            return MathObject.NO_MATH_TYPE
        else:
            index = metavars.index(self)
            math_object = metavar_objects[index]
            return math_object

    def clear_assignment(self):
        self.assigned_math_object = None
        if isinstance(self.math_type, MetaVar):
            self.math_type.clear_assignment()

    def adjust_type_of_assigned_math_object(self):
        """
        Try to adapt the math_type of self's assigned math_object, if any,
        to self's math_type.
        """

        math_object = self.assigned_math_object
        if not math_object or self.math_type is PatternMathObject.NO_MATH_TYPE:
            return

        mo_type = math_object.math_type
        if mo_type.node in self.adjustable_math_types:
            math_object.math_type = self._math_type  # Not self.math_type!!
            return True
        elif mo_type.is_metavar and not mo_type.assigned_math_object:
            mo_type.assigned_math_object = self._math_type


##################################################
##################################################
# Initialisation of the PatternInit dictionaries #
##################################################
##################################################

PatternInit.pattern_from_string = PatternMathObject.from_string
PatternInit.pattern_init()


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

    # Test is_and
    nb = 0
    tree = lean_expr_with_type_grammar.parse(targets_analysis[nb])
    mo = LeanEntryVisitor().visit(tree)
    mt = mo.math_type

    pattern = PatternMathObject.from_math_object(mt)
    print("Pattern:")
    print("    ", pattern.to_display())
    # print("Pattern matches left?")
    # print(pattern.match(left))

    MathObject.definition_patterns.append(pattern)
    tree = lean_expr_with_type_grammar.parse(hypo)
    mo = LeanEntryVisitor().visit(tree)
    mt = mo.math_type
    print(f"{mt.to_display()} matches {pattern.to_display()} ?")
    print(pattern.children[0].match(mt))
    print(pattern.children[1].math_object_from_matching().to_display())
