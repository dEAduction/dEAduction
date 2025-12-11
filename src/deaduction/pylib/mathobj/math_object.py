"""
#####################################################################
# MathObject.py : Take the result of Lean's tactic "Context_analysis", #
# and process it to extract the mathematical content.               #
#####################################################################
    
This files provides the python class MathObject for encoding mathematical
objects and propositions.

Examples:
    - a function f : X → Y corresponds to  a MathObject with
        node = 'LOCAL_CONSTANT'
        info['name'] = 'f'
        math_type = a MathObject with
            node = FUNCTION,
            children = [MathObject corresponding to X,
                        MathObject corresponding to Y]
    - a property H2 : x ∈ f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯) corresponds to a MathObject with
    node = 'LOCAL_CONSTANT' and info['name']='H2', and math_type is a
    MathObject with
            node = 'PROP_BELONGS'
            children = [MathObject corresponding to x,
                        MathObject corresponding to f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯)]

Note in particular that for a property, the math content of the property is
actually stored in the math_type attribute of the MathObject.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 06 2020 (creation)
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
from typing import Any, Optional, Union
from copy import copy, deepcopy
import logging
from functools import partial

import deaduction.pylib.config.vars as cvars

from deaduction.pylib.math_display import MathList, MathDescendant
from deaduction.pylib.utils import inj_list

log = logging.getLogger(__name__)
global _


CONSTANT_IMPLICIT_ARGS = ("real.decidable_linear_order",)


def allow_implicit_use(test_: callable) -> callable:
    """
    Modify the function test to allow implicit use of the definitions
    whose patterns are in MathObject.definition_patterns.
    'test' is typically 'is_and', 'is_or', 'is_forall', ...
    And if an implicit definition is actually used, store it in
    MathObject.last_used_implicit_definition.
    """

    def test_implicit(math_object,
                      is_math_type=False,
                      implicit=False,
                      include_iff=False) -> bool:
        """
        Apply test to math_object.

        :param implicit:     if False, implicit definitions are not used.
        """
        implicit = implicit and cvars.get(
            "functionality.allow_implicit_use_of_definitions")
        test = (partial(test_, include_iff=include_iff) if include_iff
                else test_)
        if not implicit:
            return test(math_object, is_math_type)
        elif test(math_object, is_math_type):
            return True
        else:
            MathObject.last_used_implicit_definition = None
            MathObject.last_rw_object = None
            if is_math_type:
                math_type = math_object
            else:
                math_type = math_object.math_type
            definition_patterns = MathObject.definition_patterns
            for index in range(len(definition_patterns)):
                # Test right term if self match pattern
                pattern = definition_patterns[index]
                pattern_left = pattern.children[0]
                # pattern_right = pattern.deep_copy(pattern.children[1])
                pattern_right = pattern.children[1]
                # Un-name bound vars to prevent conflict:
                # pattern_right.unname_all_bound_vars()
                log.debug(f"(Trying definition "
                      f"{MathObject.implicit_definitions[index].pretty_name}"
                      f"...)")
                if pattern_left.match(math_type):
                    if test(pattern_right, is_math_type=True):
                        definition = MathObject.implicit_definitions[index]
                        MathObject.last_used_implicit_definition = definition
                        metavars = pattern_left.metavars
                        objects = pattern_left.metavar_objects
                        # pattern_right.unname_all_bound_vars()
                        rw_math_object = pattern_right.math_object_from_matching(
                            metavars, objects)
                        MathObject.last_rw_object = rw_math_object
                        # pattern_right.rename_all_bound_vars()
                        log.debug(f"Implicit definition: "
                                  f"{definition.pretty_name}")
                        log.debug(f"    {math_type.to_display()}  <=>"
                                  f" {rw_math_object.to_display()}")
                        return True
            return False
    return test_implicit


#############################################
# MathObject: general mathematical entities #
#############################################
class MathObject:
    """
    Python representation of mathematical entities,
    both objects (sets, elements, functions, ...)
    and properties ("a belongs to A", ...)
    NB : When instancing, math_type and item in the children list must be
    instances of MathObject (except for the constant NO_MATH_TYPE)
    """

    _node              : str   # e.g. "LOCAL_CONSTANT", "FUNCTION", "QUANT_∀"
    _info              : dict  # e.g. "name", "id", "pp_type"
    _children          : list  # List of MathObjects

    Variables = {}  # Containing every element having an identifier,
    # i.e. global and bound variables, whose node is LOCAL_CONSTANT.
    # This is used to avoid duplicate.
    # key = identifier,
    # value = MathObject
    constants = {}  # WHen node='CONSTANT'. Again, used to avoid duplicates.
    NUMBER_SETS_LIST = ['ℕ', 'ℤ', 'ℚ', 'ℝ']
    number_sets = []  # Ordered list of all sets of numbers involved in some
    # MathObjects of the context, ordered sublist of ['ℕ', 'ℤ', 'ℚ', 'ℝ']
    # So that MathObject.number_sets[-1] always return the largest set of
    # numbers involved in the current exercise
    bound_var_counter = 0  # A counter to distinguish bound variables
    is_bound_var = False
    is_metavar = False

    ###########################################
    # Lists from definitions for implicit use #
    ###########################################
    #   This is set up at course loading, via the PatternMathObject
    #   set_definitions_for_implicit_use() method.
    definitions = []
    implicit_definitions          = []
    definition_patterns           = []
    # The following class attributes are modified each time an implicit
    # definition is used with success:
    last_used_implicit_definition = None
    last_rw_object                = None

    # NB: all of these should be binary relations
    INEQUALITIES = ("PROP_<", "PROP_>", "PROP_≤", "PROP_≥", "PROP_EQUAL_NOT")
    BOUNDED_QUANT_OPERATORS = ("PROP_BELONGS", "PROP_INCLUDED",
                               "PROP_EQUAL_NOT", "PROP_NOT_BELONGS") \
                              + INEQUALITIES

#######################
# Fundamental methods #
#######################
    def __init__(self, node, info, children, math_type=None):
        """
        Create a MathObject.
        """
        self._node = node
        self._info = info
        self._children = children
        self._math_type = math_type

        if self.has_bound_var():  # Set bound var math_type and parent
            # Every object here should have children matching this:
            math_type = self.children[0]
            bound_var = self.children[1]
            bound_var.parent = self
            bound_var.math_type = math_type  # This should be useless

        # ---------- APP(APP(1, 2, ...), n) --> APP(1, 2, ..., n) ---------- #
        # (i.e. uncurryfy)
        if (node == 'APPLICATION' and children and
                children[0].node == 'APPLICATION'):
            self.children = self.children[0].children + [self.children[1]]

    def debug_repr(self, typ):
        if self.name:
            rep = self.name
        elif self.value:
            rep = self.value
        elif self.children:
            children_rep = [child.__repr__() for child in self.children]
            rep = f"{typ}(node={self.node}, children={children_rep})"
        else:
            rep = f"{typ}(node={self.node})"
        return rep

    def __repr__(self):
        return self.debug_repr('MO')

    # def __str__(self):
    #     return self.to_display(format_='lean')

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, node):
        self._node = node

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, info):
        self._info = info

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children):
        self._children = children

    @property
    def math_type(self) -> Any:
        """
        This is a work-around to the impossibility of defining a class
        recursively. Thus every instance of a MathObject has a math_type
        which is a MathObject (and has a node, info dict, and children list)
        The constant NO_MATH_TYPE is defined below, after the methods
        """
        if self._math_type is None:
            return self.NO_MATH_TYPE
        else:
            return self._math_type

    @math_type.setter
    def math_type(self, math_type: Any):
        self._math_type = math_type

    def is_no_math_type(self):
        return self is self.NO_MATH_TYPE

    @classmethod
    def lambda_(cls, var, body, math_type):
        """
        Construct a MathObject corresponding to lambda var: body.
        NB: math_type is the type of the lambda, not the var type.
        It can be a function, sequence, set family, ...
        """
        lam = cls(node="LAMBDA",
                  info={},
                  children=[var.math_type, var, body],
                  math_type=math_type)
        var.parent = lam
        return lam

    def process_sequences_and_likes(self):
        """
        This method does two things:
        (1) if self is a local_constant which represent a set family or a
        sequence, it adds a child BoundVar, which will be used to display self
        (as the var n in (u_n)_{n in N} ), but ONLY in the context.
        (2) if self has such a local constant as a child, this local constant
        is replaced by a lambda. This adds a new bound var which will be used
        for display, and correctly named: in particular its name may vary
        according to local context.
        This is done only if self is not applying this local constant to an
        index, i.e. self is not a lambda or an application.
        We also not do this if this child is itself a bound var.
        """

        # (1) Add child BoundVar
        if (self.is_variable(is_math_type=True) or self.is_bound_var) \
                and (self.is_sequence() or self.is_set_family()):
            if not self.children:
                bound_var_type = self.math_type.children[0]
                bound_var = BoundVar.from_math_type(bound_var_type,
                                                    parent=self)
                # We add 3 children for compatibility
                self.children = [bound_var_type, bound_var,
                                 MathObject.PROP]

        # (2) Replace child sequence by a lambda
        if self.node not in ('APPLICATION', 'LAMBDA'):
            for index in range(len(self.children)):
                child = self.children[index]
                # DO NOT change BoundVar by lambdas,
                #  e.g. in "for all sequences u..."
                if child.is_variable(is_math_type=True) \
                        and (child.is_sequence() or child.is_set_family())\
                        and not child.is_bound_var:
                    # child.math_type is SEQ(index, target)
                    var_type = child.math_type.children[0]
                    var = BoundVar.from_math_type(var_type)
                    body = MathObject.application(child, var)
                    lam = MathObject.lambda_(var, body, child.math_type)
                    # Replace child by lambda with the same math_type
                    self.children[index] = lam

    @classmethod
    def add_numbers_set(cls, name: str):
        """
        Insert name in cls.number_sets at the right place
        :param name: an element of NUMBER_SETS_LIST = ['ℕ', 'ℤ', 'ℚ', 'ℝ']
        """
        if name in cls.NUMBER_SETS_LIST and name not in cls.number_sets:
            cls.number_sets.append(name)
            counter = len(MathObject.number_sets) - 1
            while counter > 0:
                old_item = cls.number_sets[counter - 1]
                if cls.NUMBER_SETS_LIST.index(name) < \
                   cls.NUMBER_SETS_LIST.index(old_item):
                    # Swap
                    cls.number_sets[counter] = old_item
                    cls.number_sets[counter-1] = name
                    counter -= 1
                else:
                    break
            log.debug(f"Number_sets: {MathObject.number_sets}")

    @classmethod
    def from_info_and_children(cls, info: {}, children: []):
        """
        Create an instance of MathObject from the Lean data collected by
        the parser.
        :param info: dictionary with optional keys 'name', 'identifier',
        'lean_name', 'bound_var_nb'
        :param children: list of MathObject instances
        :return: a MathObject
        """

        # (0) Name and math_type
        node = info.pop("node_name")
        if 'math_type' in info.keys():
            math_type = info.get('math_type')
        else:
            math_type = None  # NB math_type is a @property, cf above

        # (1) Treatment of constants
        if node == 'CONSTANT':
            name = info.get('name')
            if name and name in MathObject.constants:
                math_object = MathObject.constants[name]
            else:
                math_object = cls(node=node,
                                  info=info,
                                  math_type=math_type,
                                  children=children)
                MathObject.constants[name] = math_object

        # (2) Treatment of global variables: avoiding duplicate
        # This concerns only MathObjects with node=='LOCAL_CONSTANT'
        elif 'identifier' in info.keys():
            identifier = info['identifier']
            if identifier in MathObject.Variables:
                # (1.a) Return already existing MathObject
                math_object = MathObject.Variables[identifier]
            else:
                # (1.b) Create new object
                # (i) BoundVar case
                name = info.get('name')
                if name and name.endswith('.BoundVar'):
                    # if name == 'u.BoundVar':
                    #     print("debug")
                    # Remove suffix and create a BoundVar
                    # info['name'] = info['name'][:-len('.BoundVar')]
                    math_object = BoundVar(node=node,
                                           info=info,
                                           math_type=math_type,
                                           children=children,
                                           parent=None)
                else:
                    # (ii) Global var case
                    math_object = cls(node=node,
                                      info=info,
                                      math_type=math_type,
                                      children=children)
                MathObject.Variables[identifier] = math_object

        else:
            # (3) Generic instantiation (everything but not variable)
            math_object = cls(node=node,
                              info=info,
                              math_type=math_type,
                              children=children)

        # (4) Detect sets of numbers and insert in number_sets if needed
        # at the right place so that the list stay ordered
        name = math_object.display_name
        MathObject.add_numbers_set(name)

        # (5) Special treatment for sequences and set families
        math_object.process_sequences_and_likes()

        return math_object

    @classmethod
    def clear(cls):
        """Re-initialise various class variables, in particular the
        Variables dict. It is crucial that this method is called when Lean
        server is stopped, because in the next session Lean could
        re-attributes an identifier that is in Variables, entailing chaos."""
        cls.Variables = {}
        cls.number_sets = []
        cls.bound_var_counter = 0
        # cls.context_bound_vars = []

    def duplicate(self):
        """
        Create a copy of self, by duplicating the info dic.
        Beware that children of duplicates are children of self, not copies!
        """
        new_info = copy(self.info)
        other = MathObject(node=self.node, info=new_info,
                           children=self.children, math_type=self.math_type)
        return other

    @classmethod
    def deep_copy(cls, self, original_bound_vars=None, copied_bound_vars=None,
                  original_metavars=None, copied_metavars=None,
                  recursion_depth=0):
        """
        Return a deep copy of self. This should work for subclasses.
        NB: in the copied object, original bound vars must be duplicated only
        once, and all occurrences of a given bound var must be replaced by
        the same object. This is the purpose
        of the original_bound_vars and copied_bound_vars lists.
        This is crucial for coherent bound var naming: if the name of the
        bound var is modified then this modification must apply to all the
        other occurrences.
        Likewise for metavars.
        TODO: we could just do that for every sub_object, not only metavars/bv.
        """

        MAX_RECURSION_DEPTH = 5
        if recursion_depth >= MAX_RECURSION_DEPTH:
            return cls.NO_MATH_TYPE

        if original_bound_vars is None:
            original_bound_vars = []
        if copied_bound_vars is None:
            copied_bound_vars = []
        if original_metavars is None:
            original_metavars = []
        if copied_metavars is None:
            copied_metavars = []

        if self in original_bound_vars:
            idx = original_bound_vars.index(self)
            return copied_bound_vars[idx]
        elif self in original_metavars:
            idx = original_metavars.index(self)
            return copied_metavars[idx]

        # Consider self._math_type, NOT self.math_type, cf metavar
        # but beware this can be NONE
        new_info = deepcopy(self._info)
        math_type: cls = self._math_type
        children: [cls] = self.children  # Real type could be different
        try:
            new_math_type = (math_type if (math_type is None or
                                           math_type.is_no_math_type())
                             else self if math_type == self  # Hum
                             else math_type.deep_copy(math_type,
                                                      original_bound_vars,
                                                      copied_bound_vars,
                                                      original_metavars,
                                                      copied_metavars,
                                                      recursion_depth+1))
        except RecursionError:
            raise RecursionError(f"Infinite loop in deep copying {self},"
                                 f"math_type={math_type}")
        new_children = [child.deep_copy(child,
                                        original_bound_vars,
                                        copied_bound_vars,
                                        original_metavars,
                                        copied_metavars,
                                        recursion_depth)
                        for child in children]

        new_math_object = cls(node=self.node, info=new_info,
                              children=new_children, math_type=new_math_type)

        if self.is_bound_var:
            new_math_object.name_bound_var(self.name)  # Copy name
            original_bound_vars.append(self)
            copied_bound_vars.append(new_math_object)
        if self.is_metavar:
            original_metavars.append(self)
            copied_metavars.append(new_math_object)

        return new_math_object

    def constants_in_self(self):
        """
        Return the injective list of all CONSTANTs in self.
        """

        if self.is_constant():
            return [self]

        # if self.is_application():
        #     nb_args = len(self.children) - 1
        #     if nb_args > 0:
        #         child = self.children[0]
        #         if child.name == "max":
        #             print(self)
        #             print("type :")
        #             print(child.math_type)
        #             print(child.math_type.info)
        #             print([c.info for c in child.math_type.children])
        #             print([c.info for c in self.children])

                    # print("other children:")
                    # print(self.children[1])
                    # print(self.children[1].info)
                    # print(self.children[2])
                    # print(self.children[1].info)
        # elif self.is_application():
        #     nb_args = len(self.children)-1
        #     if nb_args > -1 and self.children[0].is_constant():
        #         return [(self.children[0], nb_args)]

        csts = []
        for child in self.children:
            for cst in child.constants_in_self():
                if cst not in csts:
                    csts.append(cst)
        return csts

##################################
# Some particular instantiations #
##################################
    @classmethod
    def application(cls, function, var):
        """
        Construct a MathObject obtained by applying function to var.
        """
        f_type = function.math_type
        children = f_type.children
        if len(children) < 1:
            raise ValueError(f"Math_type {f_type.to_display(format_='utf8')}"
                             f" of {function.to_display(format_='utf8')}"
                             f"does not have 2 children")
        return cls(node="APPLICATION",
                   info={},
                   children=[function, var],
                   math_type=children[1])

    @classmethod
    def FALSE(cls):
        """
        The constant FALSE as a MathObject.
        """
        return cls(node="PROP_FALSE", info={}, children=[], math_type="PROP")

    @classmethod
    def negate(cls, math_object):
        """
        Construct a new MathObject instance which stands for the negation of
        math_object.
        """
        return cls(node="PROP_NOT",
                   info={},
                   children=[math_object],
                   math_type=cls.PROP)

    @classmethod
    def forall(cls, old_var, body):
        """
        Construct a new MathObject instance which stands for a universal
        property obtained by replacing old_var by a fresh boundvar in body.
        """
        var_type = old_var.math_type
        new_var = BoundVar.from_math_type(var_type)
        new_var.process_sequences_and_likes()
        new_body = cls.substitute(old_var, new_var, body)
        forall = cls(node="QUANT_∀",
                     info={},
                     children=[var_type, new_var, new_body],
                     math_type=cls.PROP)
        new_var.parent = forall
        new_var.name_bound_var(old_var.name)
        new_var.set_binder_info(old_var.binder_info)
        # new_var.name_bound_var("Z")
        return forall

    @classmethod
    def conjunction(cls, math_objects):
        """
        Construct the conjunction of a list of properties.
        """
        if not math_objects:
            return
        elif len(math_objects) == 1:
            return math_objects[0]
        else:
            prop = math_objects.pop()
            trail_conjunction = cls.conjunction(math_objects)
            return cls(node="PROP_AND",
                       info={},
                       children=[prop, trail_conjunction],
                       math_type=cls.PROP)

    @classmethod
    def implication(cls, premise, conclusion):
        """
        Construct an implication.
        """
        return cls(node="PROP_IMPLIES",
                   info={},
                   children=[premise, conclusion],
                   math_type=cls.PROP)

    @classmethod
    def raw_lean_code(cls, code: str):
        """
        Return a fake MathObject to encapsulate a piece of pure string Lean
        code.
        """

        # TODO: remove all obviously unnecessary parentheses

        new_object = MathObject(node='RAW_LEAN_CODE',
                                info={'name': code},
                                children=[],
                                math_type=None)
        return new_object

    @classmethod
    def between_parentheses(cls, math_object):
        """
        Put math_object between parentheses.
        """
        new_object = MathObject(node='GENERIC_PARENTHESES',
                                info={},
                                children=[math_object],
                                math_type=math_object.math_type)
        return new_object

    @classmethod
    def add_leading_parentheses(cls, math_object):
        """
        Put math_object between parentheses if needed, i.e. if math_object
        has children and is not already GENERIC_PARENTHESES or
        RAW_LEAN_CODE. This is used to secure Lean object, e.g. before
        passing them as arg to a univ prop.
        """

        node = math_object.node
        tests = (bool(math_object.children),
                 node != "GENERIC_PARENTHESES",
                 node != "RAW_LEAN_CODE")

        if all(tests):
            new_object = MathObject(node='GENERIC_PARENTHESES',
                                    info={},
                                    children=[math_object],
                                    math_type=math_object.math_type)
            return new_object

        else:
            return math_object


    @classmethod
    def place_holder(cls):
        """
        A place holder ('_') for Lean code.
        """
        new_object = MathObject(node='PLACE_HOLDER',
                                info={},
                                children=[],
                                math_type=None)
        return new_object

######################
# Bound vars methods #
######################
    def has_bound_var(self):
        """
        This crucial method check if self has bound vars. Every math_object
        having bound var should have exactly 3 children, and the bound var is
        self.children[1]. This includes
        - quantified expression,
        - set intension, e.g. {x in X, f(x) in A}
        - lambda expression, e.g. x -> f(x),

        We exclude
        - sequences, e.g. (u_n)_{n in N}
        - set families, e.g. {E_i, i in I}.
        for which the bound var is used only to display a context object
        (in propositions they are replaced by lambda expressions).
        """
        nodes = ("QUANT_∀", "QUANT_∃", "QUANT_∃!", "SET_INTENSION", "LAMBDA",
                 "LOCAL_CONSTANT")

        if self.node in nodes:
            return len(self.children) == 3 and self.children[1].is_bound_var
        # elif self.is_variable(is_math_type=True) and \
        #         (self.is_sequence() or self.is_set_family()):
        #     return len(self.children) == 3 and self.children[1].is_bound_var

        return False

    @property
    def bound_var_type(self):
        if self.has_bound_var():
            return self.children[0]

    @property
    def bound_var(self):
        if self.has_bound_var():
            return self.children[1]

    @property
    def body(self):
        if self.has_bound_var():
            return self.children[2]

    def bound_vars(self,  # include_sequences=True,
                   math_type=None) -> []:
        """
        Recursively determine the list of all bound vars in self,
        of a given math_type (or all math_type if none is given).
        Each bound var will appear only once, and is detected from
        has_bound_var() method.
        """

        # (1) Self's has direct bound var?
        self_vars = []
        if self.has_bound_var():
            # if include_sequences or \
            #         not (self.is_sequence(is_math_type=True)
            #              or self.is_set_family(is_math_type=True)):
            if (not math_type) or self.bound_var_type == math_type:
                self_vars = [self.bound_var]

        # (2) children's vars:
        child_vars = sum([child.bound_vars(math_type=math_type)
                          for child in self.children], [])

        return self_vars + child_vars

    def all_bound_vars(self) ->[]:
        """
        Return the list of all bound vars appearing in self, with repetition.
        Just for debugging.
        """
        if self.is_bound_var:
            return [self]
        else:
            return sum([child.all_bound_vars() for child in self.children], [])

    def set_local_context(self, local_context=None):
        """
        The local context of a given bound var is the list of all bound vars
        that are "alive" at the place where the given bound var is introduced by
        its bounding quantifier. This method propagates the bound vars along
        the MathObject tree, and set the local_context attribute of bound vars.
        """

        # This bool tells us if we want to name all bound_vars differently,
        #  in which case all bound vars occuring befor a given one must be
        #  put in its local context.
        local_is_local = not cvars.get(
            'logic.do_not_name_dummy_vars_as_dummy_vars_in_one_prop', False)
        if local_context is None:
            local_context = []

        # Set local context for bound vars, and add them to local context.
        for child in self.children:
            if child.is_bound_var:
                # Copy so that child's local ctxt will not be affected
                #  by future changes
                child.local_context = copy(local_context)
                # Add child to local context so that it will propagate to body
                local_context.append(child)

        # Propagate (enriched) local context to other children
        for child in self.children:
            if not child.is_bound_var:
                # If local_is_local, loc ctxts of children are independent
                new_local_context = (copy(local_context) if local_is_local
                                     else local_context)

                child.set_local_context(new_local_context)

#######################
# Properties and like #
#######################
    @property
    def name(self):
        return self.info.get('name')

    @property
    def lean_name(self):
        """
        For compatibility with Statement.
        """
        return self.to_display(format_='lean')

    @property
    def value(self):
        return self.info.get('value')

    @value.setter
    def value(self, new_value):
        self.info['value'] = new_value

    @property
    def binder_info(self):
        """
        e.g. 'default', 'implicit' (i.e. this var should not be provided when
        the statement is applied).
        """
        return self.info.get('binder_info')

    def set_binder_info(self, binder_info):
        self.info['binder_info'] = binder_info

    @property
    def display_name(self) -> str:
        """
        This is the name used to display in deaduction.
        """
        return self.name if self.name else '*no_name*'

    @property
    def local_constant_shape(self) -> []:
        """
        Shape for a local constant, may be used in patterns for display.
        """
        if self.is_bound_var:
            return [r'\dummy_variable', self.display_name]

        elif self.is_variable(is_math_type=True):
            return [r'\variable', self.display_name]

        else:
            return [self.display_name]

    @property  # For debugging
    def display_debug(self) -> str:
        display = self.display_name + ', Node: *' + self.node + '*'
        display_child = ''
        for child in self.children:
            if display_child:
                display_child += ' ; '
            display_child += child.display_debug
        if display_child:
            display += ', children: **' + display_child + '**'
        return display

    def math_type_child_name(self) -> str:
        """display name of first child of math_type"""
        math_type = self.math_type
        if math_type.children:
            child = math_type.children[0]
            return child.display_name
        else:
            return '*no_name*'

    def descendant(self, line_of_descent):
        """
        Return the MathObject corresponding to the line_of_descent
        e.g. self.descendant((1.0))  -> children[1].children[0]

        :param line_of_descent:     int or tuple or list
        :return:                    MathObject
        """

        if isinstance(line_of_descent, int):  # Including 0!!!
            return self.children[line_of_descent]
        elif not line_of_descent:
            # e.g. empty tuple or list but not 0!
            return self
        elif (isinstance(line_of_descent, tuple)
              or isinstance(line_of_descent, list)):
            child_number, *remaining = line_of_descent
            if not isinstance(child_number, int):
                return self
            if (child_number >= len(self.children)
                    or child_number < -len(self.children)):
                return None
            child = self.children[child_number]
            if not remaining:
                return child
            else:
                return child.descendant(remaining)

    def give_name(self, name):
        self.info["name"] = name

    def has_name(self, name: str):
        return self.display_name == name

    def search_in_name(self, name):
        """
        Return all sub-objects whose name contains name.
        Do not use assigned_math_objects name.
        """
        math_objects = []
        self_name = self._info.get('name')
        if self_name and name in self_name:
            math_objects.append(self)

        for child in self.children:
            math_objects.extend(child.search_in_name(name))

        return math_objects

##########################################
# Tests for equality and related methods #
##########################################
    def __eq__(self, other) -> bool:
        """
        Test if the two MathObjects code for the same mathematical objects,
        by recursively testing nodes. This is crucial for instance to
        compare a new context with the previous one.

        Note that even for global variables we do NOT want to use identifiers,
        since Lean changes them every time the file is modified.

        We also want the method to identify properly two quantified
        expressions that have the same meaning, like '∀x, P(x)' and '∀y, P(y)'
        even if the bound variables are distinct.

        WARNING: this should probably not be used for bound variables.
        """
        test, msg = self.is_equal_to(other,
                                remove_generic_paren=False,
                                use_assigned_math_obj=False)
        return test

    def is_equal_to(self, other,
                    remove_generic_paren=False,
                    use_assigned_math_obj=False,
                    return_msg=False) -> (bool, str):
        """
        If return_msg is False, then the returned string will be empty.
        Otherwise, we use self.to_display() to return an error msg explaining
        where other differs from self (for debugging only).
        (This method is used in to_display(), and thus we cannot
        use to_display() here with return_msg = True.)
        """
        ##########################################################
        # Mod out by generic_parentheses / assigned_math_objects #
        ##########################################################
        mo0 = self
        mo1 = other
        # if return_msg:
        #     oname, onode = ("", "None") if not other else (other, "STR!!") if (
        #         isinstance(other, str)) else (other.name, other.node)
        #     print(f"Comparing {self.try_to_display()} with"
        #           f" {onode, oname}")

        if use_assigned_math_obj:
            if hasattr(self, 'assigned_math_object'):
                if self.assigned_math_object:
                    mo0 = self.assigned_math_object
                    # print(f"Assigned mo: {mo0.to_display(format_='utf8')}")
            if hasattr(other, 'assigned_math_object'):
                if other.assigned_math_object:
                    mo1 = other.assigned_math_object

        if remove_generic_paren:
            if mo0.node == "GENERIC_PARENTHESES":
                mo0 = self.children[0]
                # if return_msg:
                #     print(f"--> replaced by {mo0.try_to_display()}")
            elif mo1.node == "GENERIC_PARENTHESES":
                mo1 = other.children[0]

        if (mo0 is not self) or (mo1 is not other):
            # if return_msg:
            #     print(f"Assigned mo or parentheses: {mo0}")
            test = mo0.is_equal_to(mo1,
                                   remove_generic_paren=remove_generic_paren,
                                   use_assigned_math_obj=use_assigned_math_obj,
                                   return_msg=return_msg)
            return test

        # Successively test for
        #                           nodes
        #                           bound var nb
        #                           name
        #                           math_type
        #                           children

        # Include case of NO_MATH_TYPE (avoid infinite recursion!)
        if self is other:
            return True, ""

        if return_msg:
            error_msg = self.try_to_display() + " ≠ "
        else:
            error_msg = ""

        if other is None or not isinstance(other, MathObject):
            # if return_msg:
            #     print(error_msg)
            return False, error_msg + ""  # str(other) BIG BUG!!
        if return_msg:
            error_msg += other.try_to_display()

        # Test math_types only if they are both defined:
        if self.is_no_math_type() or other.is_no_math_type():
            return True, ""

        ################################################
        # Test node, bound var, name, value, math_type #
        ################################################
        if (self.node, self.is_bound_var, self.name, self.value) != \
                (other.node, other.is_bound_var, other.name, other.value):
            # if return_msg:
            #     print(error_msg)
            return False, error_msg

        # Test math_types
        mt0 = self.math_type
        mt1 = other.math_type
        test, msg = mt0.is_equal_to(mt1,
                               remove_generic_paren=remove_generic_paren,
                               use_assigned_math_obj=use_assigned_math_obj,
                               return_msg=return_msg)
        if not test:
            return test, msg

        # BoundVar has an __eq__() method
        # if self.is_bound_var:
        #     if self.bound_var_nb() != other.bound_var_nb():
        #         return False

        #################################
        # Recursively test for children #
        #################################
        elif len(self.children) != len(other.children):
            return False, error_msg
        else:
            equal = True
            bound_var_1 = None
            bound_var_2 = None

            ##############
            # Bound vars #
            ##############
            # Mark bound vars in quantified expressions to distinguish them
            # if self.node in self.HAVE_BOUND_VARS:
            if self.has_bound_var():
                # Here self and other are assumed to be a quantified proposition
                # and children[1] is the bound variable.
                # We mark the bound variables in self and other with same number
                # so that we know that, say, 'x' in self and 'y' in other are
                # linked and should represent the same variable everywhere
                bound_var_1 = self.children[1]
                bound_var_2 = other.children[1]
                bound_var_1.mark_identical_bound_vars(bound_var_2)
                # log.debug(f"Comparing {self} and {other}")
                # log.debug(f"Marking BV {bound_var_1, bound_var_2}")

            # Test children
            children_error_msg = ""
            for ch0, ch1 in zip(self.children, other.children):
                test, msg = ch0.is_equal_to(ch1,
                                       remove_generic_paren=remove_generic_paren,
                                       use_assigned_math_obj=use_assigned_math_obj,
                                       return_msg=return_msg)

                if not test:
                    # if self.node == 'PROP_≥':
                    #     log.debug(f"Distinct child: {child0} ")
                    #     log.debug(f"and {child1}")
                    #     log.debug(f" in {self}")
                    equal = False
                    children_error_msg = msg
                    break

            # Un-mark bound_vars
            if bound_var_1:
                bound_var_1.unmark_bound_var()
                bound_var_2.unmark_bound_var()

            return equal, children_error_msg

    def is_in(self, others: [],
              remove_generic_paren=False,
              use_assigned_math_obj=False) -> Union[int, bool]:
        """
        True is self equals one element of the list others,
        with the is_equal method instead of __eq__.
        """

        idx = 0
        for other in others:
            # print(f"Testing {other}")
            test, msg = self.is_equal_to(other,
                                    remove_generic_paren=remove_generic_paren,
                                    use_assigned_math_obj=use_assigned_math_obj,
                                         return_msg=False)
            # print(f"/Testing {other}")
            if test:
                return idx
            idx += 1

        return False

    def contains(self, other) -> int:
        """
        Compute the number of copies of other contained in self,
        recursively investigating self's children.
        """

        if self is self.NO_MATH_TYPE:  # NO_MATH_TYPE is equal to anything...
            return 0

        if MathObject.__eq__(self, other):
            return 1
        else:
            # for child in self.children:
            #     test = child.contains(other)
            #     # if test:
            #     #     print("debug")

            return sum([child.contains(other) for child in self.children])

    def contains_including_types(self, other):
        """
        True if other recursively appears in self, including math_types.
        """

        if self is self.NO_MATH_TYPE:  # NO_MATH_TYPE is equal to anything...
            return 0

        if MathObject.__eq__(self, other):
            return True
        else:
            if self.math_type.contains_including_types(other):
                return True
            for child in self.children:
                if child.contains_including_types(other):
                    return True
            return False

    def is_joker(self):
        name = self._info.get('name')
        return 'JOKER' in name if name else None

    def is_usr_joker(self):
        name = self._info.get('name')
        return 'USR_JOKER' in name if name else None

    def usr_jkr_nb(self):
        name = self._info.get('name')
        if 'USR_JOKER' in name:
            prefix, nb = name.split('USR_JOKER')
            return nb
        else:
            return None

    def contains_joker(self):
        if self.is_joker():
            return True
        return any(child.contains_joker() for child in self.children)

    def contains_usr_joker(self):
        if self.is_usr_joker():
            return True
        return any(child.contains_usr_joker() for child in self.children)

    def contains_non_usr_joker(self):
        if self.is_joker() and not self.is_usr_joker():
            return True
        return any(child.contains_non_usr_joker() for child in self.children)

    def jokers_n_vars(self) -> []:
        """
        Return the list of jokers and their vars in self.
        Search recursively in children, but not in jokers (that are assumed
        to be non-assigned).
        NB: APP(JOKER0, a, b, c) --> [ (JOKER0, [a,b,c] ) ]
        """
        if self.is_application() and self.children:
            joke = self.children[0]
            if joke.is_joker():
                variables = self.variables_of_app()
                return [(self, variables)]

        elif self.is_constant() or self.is_local_constant():
            if self.is_joker():
                return [(self, [])]

        return sum([child.jokers_n_vars() for child in self.children] , [])

    def local_constants_in(self) -> []:
        """
        Return the list of local constants in self.
        """
        if self.is_local_constant():
            return [self]

        else:
            lci = []
            for child in self.children:
                lci.extend(child.local_constants_in())
            return inj_list(lci)

    @classmethod
    def substitute(cls, old_var, new_var, math_object):
        """
        Return a new MathObject instance by replacing old_var by new_var inside
        math_object. There is no side effect on math_object.
        """
        if math_object is old_var:
            return new_var

        elif math_object.contains(old_var):
            new_children = [child.substitute(old_var, new_var, child)
                            for child in math_object.children]

            # Do we need to duplicate math_type here??
            return cls(node=math_object.node,
                       info=copy(math_object.info),
                       children=new_children,
                       math_type=math_object.math_type)
        else:
            return math_object

    def direction_for_substitution_in(self, other) -> str:
        """
        Assuming self is an equality or an iff,
        and other a property, search if
        left/right members of equality self appear in other.

        WARNING: does not work if the equality (or iff) is hidden behind
        'forall", so for the moment we cannot use this when applying statements

        :return:
            - None,
            - '>' if left member appears, but not right member,
            - '<' in the opposite case,
            - 'both' if both left and right members appear

        TODO: improve this
        FIXME: not used
        """
        equality = self.math_type
        if equality.node not in ['PROP_EQUAL', 'PROP_IFF']:
            return ''
        left, right = equality.children
        contain_left = other.contains(left)
        contain_right = other.contains(right)
        decision = {(False, False): '',
                    (True, False): '>',
                    (False, True): '<',
                    (True, True): 'both'
                    }
        return decision[contain_left, contain_right]

    def length(self):
        """
        Return the number of nodes in self.
        """
        return 1 + sum(child.length() for child in self.children)

#######################
# Tests for math_type #
#######################
    def is_prop(self, is_math_type=False) -> bool:
        """
        Test if self represents a mathematical Proposition
        WARNING:
        For global variables, only the math_type attribute should be tested!
        e.g. If self represents property (H : ∀ x, P(x) )
        then self.math_type.is_prop() is True,
        but NOT self.is_prop()
        (so if self is H, then self.math_type.math_type.is_prop() is True).
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "PROP"

    def is_type(self, is_math_type=False, include_index_set=True) -> bool:
        """
        Test if (math_type of) self is a "universe".
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return (math_type.node == "TYPE" or
                (include_index_set and math_type.node == "SET_INDEX"))

    def is_variable(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is a variable (used for coloration).
        The (somewhat subjective) conditions are:
        - to be a local constant,
        - not a property nor a type
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type

        if math_type.node == "LOCAL_CONSTANT":
            math_type_of_math_type = math_type.math_type
            if not (math_type_of_math_type.is_prop(is_math_type=False) or
                    math_type_of_math_type.is_type(is_math_type=True) or
                    math_type_of_math_type.is_no_math_type()):
                return True
        return False

    def is_sequence(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is "SEQUENCE".
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "SEQUENCE"

    def is_app_of_local_constant(self) -> bool:
        """
        Test if self is of the form APP(LOCAL_CONSTANT). This is useful to
        know that the local constant bound var (if any) will NOT be used in
        display.
        """
        if self.node == 'APPLICATION' and self.children[0].node == \
                'LOCAL_CONSTANT':
            return True
        else:
            return False

    def is_suitable_for_app(self, is_math_type=False) -> bool:
        """
        Test if self may be the first argument of an application,
        e.g. self is a function, a sequence or a set family.
        """
        tests = (self.is_function(is_math_type=is_math_type),
                 self.is_sequence(is_math_type=is_math_type),
                 self.is_set_family(is_math_type=is_math_type))
        return any(tests)

    def is_set_family(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is "SET_FAMILY".
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "SET_FAMILY"

    def is_lambda(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is "LAMBDA".
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "LAMBDA"

    def is_nat(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is ℕ.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "CONSTANT" and math_type.info['name'] == "ℕ"

    def is_function(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is a function.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "FUNCTION"

    def is_atomic_belong(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is belongs.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        test = (math_type.node == "PROP_BELONGS" and
                math_type.children[1].node == "LOCAL_CONSTANT")
        return test

    @allow_implicit_use
    def is_and(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is a conjunction.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return (math_type.node == "PROP_AND"
                or math_type.node == "PROP_∃")

    @allow_implicit_use
    def is_or(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is a disjunction.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "PROP_OR"

    @allow_implicit_use
    def is_implication(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is an implication.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "PROP_IMPLIES"

    def premise(self, is_math_type=False) -> bool:
        """
        If self is an implication, return its premise.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type

        premise = math_type.children[0] if self.is_implication(is_math_type) \
            else None
        return premise

    @allow_implicit_use
    def is_exists(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is an existence property.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node in ("QUANT_∃", "QUANT_∃!")

    @allow_implicit_use
    def is_for_all(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is a universal property.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "QUANT_∀"

    def is_place_holder(self):
        return self.node == 'PLACE_HOLDER'

    def implicit(self, test: callable):
        """
        Call the implicit version of test.
         - if test is False, return None,
         - if test  is explicitly True, return self,
         - if test is implicitly True, return the implicit version of self.

         :param test: one of is_and, is_or, is_implication, is_exists,
                      is_for_all.
        """
        if not test(self, implicit=True, is_math_type=True):
            return None
        if test(self, implicit=False, is_math_type=True):
            return self
        else:
            return self.last_rw_object

    def is_quantifier(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is a quantified property.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return (math_type.is_exists(is_math_type=True)
                or math_type.is_for_all(is_math_type=True))

    def explicit_quant(self):
        """
        Return self if self is_forall or self is_exists,
        of self after unfolding definition if self is implicitly so.
        """
        if (self.is_for_all(is_math_type=True, implicit=False)
                or self.is_exists(is_math_type=True, implicit=False)):
            return self
        elif (self.is_for_all(is_math_type=True, implicit=True)
                or self.is_exists(is_math_type=True, implicit=True)):
            return self.last_rw_object

    def var_of_explicit_quant(self):
        quant = self.explicit_quant()
        if quant:
            return quant.children[1]

    def type_of_explicit_quant(self):
        quant = self.explicit_quant()
        if quant:
            return quant.children[0]

    def body_of_explicit_quant(self):
        quant = self.explicit_quant()
        if quant:
            return quant.children[2]

    def bound_prop_n_actual_body_of_bounded_quant(self):
        """
        Check if math_object.math_type has the form
        ∀ x:X, (x R ? ==>  Q)
        where R is some relation, and if so return "x R ?" and Q.
        """

        explicit_self = self.explicit_quant()
        if not explicit_self:
            return

        dummy_var = explicit_self.children[1]
        body: MathObject = explicit_self.children[2]
        if body.is_implication(is_math_type=True):
            premise = body.children[0]
            tests = (premise.is_inequality(is_math_type=True),
                     premise.is_belongs_or_included(is_math_type=True))
            if any(tests) and dummy_var == premise.children[0]:
                conclusion = body.children[1]
                return premise, conclusion

    def types_n_vars_of_univ_prop(self, implicit_def=True,
                                  jump_first_ineq=True):
        """
        If self is a universal property, either explicit or implicit,
        extract the type of the variable, and the name in the explicit case.
        In the explicit case, recursively extend the list in the case when
        the body is again an explicit universal statement.
        """

        if not self.is_for_all(is_math_type=True, implicit=implicit_def):
            return

        types_n_vars = []
        explicit_self = self.explicit_quant()
        math_type = explicit_self.children[0]
        dummy_var = explicit_self.children[1]
        body: MathObject = explicit_self.children[2]

        types_n_vars.append((math_type, dummy_var))

        if jump_first_ineq:
            test = self.bound_prop_n_actual_body_of_bounded_quant()
            if test:
                premise, new_body = test
                if premise.is_inequality(is_math_type=True):
                    body = new_body

        more = body.types_n_vars_of_univ_prop(implicit_def=False,
                                              jump_first_ineq=False)
        if more:
            types_n_vars.extend(more)

        return types_n_vars

        # # TODO: get iiiv from settings
        # iiiv = include_initial_implicit_vars
        # types_n_vars = []
        # math_type = self.type_of_explicit_quant()
        #
        # # Get dummy_var name in case of explicit forall
        # if self.is_for_all(is_math_type=True, implicit=False):
        #     dummy_var = self.children[1]
        # else:
        #     dummy_var = None
        #
        # # Include var except dummy_var is implicit and if not iiiv
        # if (not dummy_var
        #         or dummy_var.binder_info != 'implicit'
        #         or iiiv):
        #     types_n_vars.append((math_type, dummy_var))
        #
        # # Always include implicit vars after an explicit one
        # if dummy_var and dummy_var.binder_info != 'implicit':
        #     iiiv = True
        #
        # if dummy_var:
        #     body: MathObject = self.children[2]
        #     more = body.types_n_vars_of_univ_prop(implicit_def=False,
        #                                           include_initial_implicit_vars=iiiv)
        #     if more:
        #         types_n_vars.extend(more)
        # if types_n_vars:
        #     return types_n_vars

    # def nb_initial_implicit_vars(self):
    #     """
    #     Return the number of implicit vars:
    #      before first explicit
    #     (or total nb if no explicit var).
    #     """
    #
    #     types_n_vars = self.types_n_vars_of_univ_prop(
    #         include_initial_implicit_vars=True)
    #     nb = 0
    #     for t, var in types_n_vars:
    #         if not var:
    #             break
    #         elif var.binder_info != 'implicit':
    #             break
    #         else:
    #             nb += 1
    #     return nb

    def is_equality(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is an equality.
        """
        math_type = self if is_math_type else self.math_type
        return math_type.node == "PROP_EQUAL"

    def is_subset(self):
        return self.math_type.node == "SET"

    def is_set_equality(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is an equality between subsets.
        """

        if not self.is_equality(is_math_type=is_math_type):
            return False

        math_type = self if is_math_type else self.math_type
        return math_type.children[0].is_subset()

    def is_non_equality(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is an equality.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "PROP_EQUAL_NOT"

    def is_inequality(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is an inequality.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node in self.INEQUALITIES

    def is_bounded_quant_op(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self can be used for bounded quantification.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node in self.BOUNDED_QUANT_OPERATORS

    def bounded_quant(self, variable):
        """
        Check if math_object has the form
                ∀ x:X, (x R ... ==> ...)
        where R is some binary relation, and if this statement may be
        applied to variable. If so, return inequality with x replaced by
        variable.
        """

        math_object = self
        p_n_b = math_object.bound_prop_n_actual_body_of_bounded_quant()
        if not p_n_b:
            return
        inequality, body = p_n_b
        if inequality.node not in self.BOUNDED_QUANT_OPERATORS:
            return
        # child = inequality.children[0]
        # if child != variable:
        #     return
        children = [variable, inequality.children[1]]
        new_inequality = MathObject(node=inequality.node,
                                    info = {},
                                    children = children,
                                    math_type = inequality.math_type)
        return new_inequality

    def is_instance(self) -> bool:
        """
        Test if self is a variable whose name begins by "_inst";
        that is, self represents a proof that some type is an instance of
        some class (information that should not be displayed in deaduction)
        """
        name = self.info.get("name")
        if name:
            if name.startswith("_inst_"):
                return True
        return False

    def concerns_numbers(self) -> bool:
        """
        True iff self is an equality or an inequality between numbers,
        i.e. elements of the MathObject.NUMBER_SETS_LIST.
        """
        if (self.is_equality(is_math_type=True)
            or self.is_inequality(is_math_type=True)
                or self.is_non_equality(is_math_type=True)):
            name = self.children[0].math_type.display_name
            if name in self.NUMBER_SETS_LIST:
                return True
        return False

    # Numbers : ['ℕ', 'ℤ', 'ℚ', 'ℝ']
    def is_N(self):
        return self.display_name == 'ℕ'

    def is_Z(self):
        return (self.display_name == 'ℤ'
                or self.display_name == 'IntegerSubGroup')

    def is_Q(self):
        return self.display_name == 'ℚ'

    def is_R(self):
        return (self.display_name == 'ℝ'
                or self.display_name == 'RealSubGroup')

    def is_number(self):
        return any([self.is_N(), self.is_Z(), self.is_Q(), self.is_R()])

    def is_generic_number(self):
        return self.node == '*NUMBER_TYPES'

    def ring_expr(self) -> Optional[int]:
        """
        Test if self is a pure ring expr, i.e. consists only of numbers,
        local constants, and operations + - * /.
        If this is so, then return the nb of arithmetic operations in self.
        If not, return False.
        """

        allowed_nodes = ['PARENTHESES', 'GENERIC_PARENTHESES', 'NUMBER',
                         'LOCAL_CONSTANT']
        ring_nodes = ['SUM', 'DIFFERENCE', 'MULT', 'DIV', 'POWER']

        if self.node in ring_nodes + allowed_nodes:
            tests = [child.ring_expr() for child in self.children]
            if None in tests:
                return False
            else:
                total_nb_op = sum(tests)
                if self.node in ring_nodes:
                    total_nb_op += 1
                return total_nb_op

        else:
            return False

        # if not (self.math_type.is_number()
        #         or self.node in allowed_nodes):
        # return 0

    def is_iff(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is 'PROP_IFF'.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type

        return math_type.node == "PROP_IFF"

# ------------ Negation methods ---------------- #
    def is_not(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is a negation.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type

        return math_type.node in ("PROP_NOT", "PROP_NOT_BELONGS",
                                  "PROP_EQUAL_NOT")

    def body_of_negation(self):
        """
        Assuming self is "not P", return a new MathObject equal to P. Handle
        special cases of not belong, not equal.
        """
        body = None
        if self.node == "PROP_NOT":
            body = self.children[0]
        elif self.node in ("PROP_NOT_BELONGS", "PROP_EQUAL_NOT"):
            not_not_node = self.node.replace("_NOT", "")
            body = MathObject(node=not_not_node,
                              info=self.info,
                              children=self.children,
                              math_type=self.math_type)

        return body

    def is_simplifiable_body_of_neg(self, is_math_type=False):
        """
        Return True if not (self) may be directly simplified.
        """
        tests = [self.is_not(is_math_type=is_math_type),
                 self.is_for_all(is_math_type=is_math_type),
                 self.is_exists(is_math_type=is_math_type),
                 self.is_and(is_math_type=is_math_type),
                 self.is_or(is_math_type=is_math_type),
                 self.is_implication(is_math_type=is_math_type),
                 self.is_inequality(is_math_type=is_math_type)]
        return any(tests)

    def first_pushable_body_of_neg(self, is_math_type=False):
        """
        If self contains some negation that can be pushed,
        e.g. not (P => Q), return its body, e.g. (P => Q).

        Note that the method does explore the tree under unpushable
        negation,
        i.e. in
            not( P <=> not (Q => R) )
        the part not (Q => R) will be detected. Note that push_neg_once
        will work in that case.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type

        # (1) Self is a negation
        if math_type.is_not(is_math_type=True):
            body = math_type.body_of_negation()
            if body.is_simplifiable_body_of_neg(is_math_type=True):
                return body
            else:  # This part allow to explore tree under unpushable negation:
                pass
                # return None

        # Explore children
        for child in math_type.children:
            body = child.first_pushable_body_of_neg(is_math_type=True)
            if body:
                return body
# ---------------------------------------------------------- #

    def is_false(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is 'contradiction'.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        if math_type.node == "PROP_FALSE":
            return True
        else:
            return False

    def is_application(self):
        return self.node == "APPLICATION"

    def is_constant(self):
        return self.node == "CONSTANT"

    def is_local_constant(self):
        return self.node == "LOCAL_CONSTANT"

    def is_implicit_arg(self):
        if (self.node == "TYPE"
                or (self.is_constant() and self.display_name in
                CONSTANT_IMPLICIT_ARGS)):
            return True
        else:
            return False

    def which_number_set(self, is_math_type=False) -> Optional[str]:
        """
        Return 'ℕ', 'ℤ', 'ℚ', 'ℝ' if self is a number, else None
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        name = math_type.display_name
        if math_type.node == 'CONSTANT' and name in ['ℕ', 'ℤ', 'ℚ', 'ℝ']:
            return name
        else:
            return None

    def variables_of_app(self):
        """
        If self is app, then return all ending children of self which are local
        constant (except first child).
        """
        if not self.is_application():
            return None
        variables = []
        for idx in range(len(self.children)).__reversed__():
            if idx != 0:
                child = self.children[idx]
                if child.is_local_constant():
                    variables.append(child)
        return variables

    # Determine some important classes of MathObjects
    def can_be_used_for_substitution(self, is_math_type=False) -> (bool,
                                                                   Any):
        """
        Determines if a proposition can be used as a basis for substituting,
        i.e. is of the form
            (∀ ...)*  a = b
        or
            (∀ ...)*  P <=> Q
         with zero or more universal quantifiers at the beginning.

        This is a recursive function: in case self is a universal quantifier,
        self can_be_used_for_substitution iff the body of self
        can_be_used_for_substitution.

        :return: a couple containing
            - the result of the test (a boolean)
            - the equality or iff, so that the two terms may be retrieved
            (or None)
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        if math_type.is_equality(is_math_type=True) \
                or math_type.is_iff(is_math_type=True):
            return True, math_type
        elif math_type.is_for_all(is_math_type=True):
            # NB : ∀ var : type, body
            body = math_type.children[2]
            # Recursive call
            return body.can_be_used_for_substitution(is_math_type=True)
        else:
            return False, None

    @allow_implicit_use
    def can_be_used_for_implication(self, is_math_type=False,
                                    include_iff=False) -> bool:
        """
        Determines if a proposition can be used as a basis for implication,
        i.e. is of the form
            (∀ ...)*  P => Q
         with zero or more universal quantifiers at the beginning.

        This is a recursive function.

        If include_iff is True, then iff are included. Nevertheless,
        this will not work for implicit definitions, only true implication
        will be detected.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        if (math_type.is_implication(is_math_type=True)
                or (include_iff and math_type.is_iff(is_math_type=True))):
            return True
        elif math_type.is_for_all(is_math_type=True):
            # NB : ∀ var : type, body
            body = math_type.children[2]
            # Recursive call
            return body.can_be_used_for_implication(is_math_type=True,
                                                    include_iff=include_iff)
        else:
            return False

    def is_belongs_or_included(self, is_math_type=False):
        """
        Test if self matches
        - "x belongs to A": then return A;
        - "A subset B": then return P(B)
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type

        if math_type.node == "PROP_BELONGS":
            return math_type.children[1]
        elif math_type.node == "PROP_INCLUDED":
            sup_set = math_type.children[1]
            type_ = MathObject(node="SET", children=[sup_set])
            return type_
        else:
            return False

    def bounded_quantification(self, is_math_type=False):
        """
        Test if self is a universal implication of the form
                    ∀ x, P(x) => Q(x).
        If this is so, return P(x).
        """

        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type

        if math_type.is_for_all(is_math_type=True):
            if math_type.children[2].is_implication(is_math_type=True):
                premise = math_type.children[2].children[0]
                return premise

        return False

    def bounded_quant_real_type(self, is_math_type=False):
        """
        If self is a universal property with bounded quantification, try to
        return the real type of the bounded variable.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type

        premise = math_type.bounded_quantification(is_math_type=True)
        if premise:
            type_ = premise.is_belongs_or_included(is_math_type=True)
            if type_:
                return type_

        return False

    def main_symbol(self, is_math_type=True) -> Optional[str]:
        """
        Return the main symbol of self, e.g. if self is a universal property
        then return "forall".
        """

        if self.is_and(is_math_type=is_math_type):
            return "and"
        elif self.is_or(is_math_type=is_math_type):
            return "or"
        elif self.is_not(is_math_type=is_math_type):
            return "not"
        elif self.is_implication(is_math_type=is_math_type):
            return "implies"
        elif self.is_iff(is_math_type=is_math_type):
            return "iff"
        elif self.is_for_all(is_math_type=is_math_type):
            return "forall"
        elif self.is_exists(is_math_type=is_math_type):
            return "exists"
        elif self.is_equality(is_math_type=is_math_type):
            return "equal"
        elif self.is_function(is_math_type=is_math_type):
            return "function"
        elif self.is_atomic_belong(is_math_type=is_math_type):
            return "belong"
        else:
            return None

################################
# Implicit definitions methods #
################################
    def unfold_implicit_definition(self):  # -> [MathObject]
        """
        Try to unfold each implicit definition at top level only,
        and return the list of resulting math_objects.
        If no definition matches then the empty list is returned.
        """

        definition_patterns = MathObject.definition_patterns
        rw_math_objects = []
        for index in range(len(definition_patterns)):
            # Test right term if self match pattern
            pattern = definition_patterns[index]
            pattern_left = pattern.children[0]
            pattern_right = pattern.children[1]
            if pattern_left.match(self):
                definition = MathObject.implicit_definitions[index]
                MathObject.last_used_implicit_definition = definition
                rw_math_object = pattern_right.math_object_from_matching(
                    metavars=pattern_left.metavars,
                    metavars_objects=pattern_left.metavar_objects
                )
                rw_math_objects.append(rw_math_object)
                # name = MathObject.implicit_definitions[index].pretty_name
                # log.debug(f"Implicit definition {name} "
                #           f"--> {rw_math_object.to_display()}")
        return rw_math_objects

    def unfold_implicit_definition_recursively(self):
        """
        Unfold implicit definition recursively, keeping only the first match at
        each unfolding.
        """
        # (1) Unfold definitions at top level
        math_object = self
        rw_math_objects = math_object.unfold_implicit_definition()
        if rw_math_objects:
            math_object = rw_math_objects[0]

        # (2) Unfold definitions recursively for children
        rw_children = []
        for child in math_object.children:
            rw_child = child.unfold_implicit_definition_recursively()
            rw_children.append(rw_child)

        # (3) Create new object with all defs unfolded
        rw_math_object = MathObject(node=math_object.node,
                                    info=math_object.info,
                                    children=rw_children,
                                    math_type=math_object.math_type)
        return rw_math_object

    def check_unroll_definitions(self, is_math_type=False) -> []:
        """
        Return the definitions that match self. This is used for the
        ContextMathObject.help_definition() method.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type

        # if self.node == 'PROP_BELONGS' and self.children[1].node == \
        #         'SET_INTER+':
        #     print("inter")
        definitions = MathObject.definitions
        matching_defs = [defi for defi in definitions
                         if defi.match(math_type)]
        return matching_defs

    def glob_vars_when_proving(self):
        """
        Try to determine the variables that will be introduced when proving
        self. Implicit definitions must be unfolded prior to calling this
        method.

        :return: list of vars (local constants). Order has no meaning.
        NB: these vars can be manipulated (e.g. named) with no damage,
        they are (shallow) copies of the original vars. Their math_type
        should not be touched, however.

        NB: this method is not used.
        """

        math_type = self
        vars = []
        if self.is_for_all(is_math_type=True, implicit=False):
            # if not self.is_for_all(is_math_type=True, implicit=False):
            #     math_type = MathObject.last_rw_object  # Implicit forall
            #####################################
            # This is where we find a new var!! #
            #####################################
            # vars.append(copy(math_type.children[1])) BUG!!
            vars.append(math_type.children[1].duplicate())
            children = [math_type.children[2]]
        elif (self.is_and(is_math_type=True, implicit=False)
                or self.is_or(is_math_type=True, implicit=False)
                or self.is_not(is_math_type=False)
                or self.is_iff(is_math_type=False)):
            # if not (self.is_and(is_math_type=True, implicit=False)
            #         or self.is_or(is_math_type=True, implicit=False)
            #         or self.is_not(is_math_type=True)
            #         or self.is_iff(is_math_type=True)):
            #     math_type = MathObject.last_rw_object  # Implicit and, etc.
            children = math_type.children  # (we will take "Max" of children)
        elif self.is_implication(is_math_type=True, implicit=False):
            # if not self.is_implication(is_math_type=True, implicit=False):
            #     math_type = MathObject.last_rw_object
            children = [math_type.children[1]]  # Vars of premise ignored
        elif self.is_exists(is_math_type=True, implicit=False):
            # if not self.is_exists(is_math_type=True, implicit=False):
            #     math_type = MathObject.last_rw_object
            children = [math_type.children[2]]
        else:
            children = []  # Nothing else?

        children_vars = [child.glob_vars_when_proving() for child in children]
        # Keep max of each type:
        #  Repeat until empty: pop any var from all children_vars
        #  that contain it, and add it to vars
        more_vars = []
        while children_vars:
            child_vars = children_vars[0]
            if child_vars == []:
                children_vars.remove([])
            else:
                var = child_vars.pop()
                more_vars.append(var)
                # Search for vars of same type in other children vars:
                for other_child_vars in children_vars[1:]:
                    types = [v.math_type for v in other_child_vars]
                    if var.math_type in types:
                        index = types.index(var.math_type)
                        other_child_vars.pop(index)

        vars.extend(more_vars)
        return vars

################################################
# Display methods: implemented in math_display #
################################################
    def to_display(self, format_="html", text=False,
                   use_color=True, bf=False, is_type=False,
                   used_in_proof=False,
                   pretty_parentheses=True) -> str:
        """
        This method is actually defined in math_display/new_display.
        """
        display = MathList.display(self, format_=format_, text=text,
                                   use_color=use_color, bf=bf, is_type=is_type,
                                   used_in_proof=used_in_proof,
                                   pretty_parentheses=pretty_parentheses)
        return display

    def try_to_display(self, text=False, is_type=False):
        """
        Version of to_display() that catch infinite recursion, mainly for
        debugging.
        """
        # FIXME:
        # display = self.__repr__()
        try:
            display = self.to_display(format_="utf8", text=text,
                                      is_type=is_type)
        except RecursionError:
            if self.name:
                display = self.name
            else:
                display = str(self)
        return display

    def math_type_to_display(self, format_="html", text=False,
                             is_math_type=False, used_in_proof=False,
                             pretty_parentheses=True) -> str:

        math_type = self if is_math_type else self.math_type
        return math_type.to_display(format_, text=text, is_type=True,
                                    used_in_proof=used_in_proof,
                                    pretty_parentheses=pretty_parentheses)

    def latex_shape(self, is_type=False, text=False, lean_format=False):
        """
        This method is actually defined in math_display/new_display.
        """
        shape = MathList.latex_shape(self, is_type=is_type, text=text,
                                     lean_format=lean_format)
        return shape

    def lean_shape(self, is_type=False, text=False, lean_format=True):
        """
        This method is actually defined in math_display/new_display.
        """

        shape = MathList.lean_shape(self)
        return shape

    def recursive_match(self, other, metavars, metavar_objects,
                        symmetric_match=False, debug=False, return_msg=False)\
                        -> (bool, str):
        """
        For compatibility with the PatternMathObject class.
        """
        if self == other:
            return True, ""
        else:
            if return_msg:
                error_msg = (self.try_to_display() + " ≠match "
                             + other.try_to_display())
            else:
                error_msg = ""
            return False, error_msg

    def to_math_object(self):
        """
        For compatibility.
        """
        return self.math_type

    def unname_all_bound_vars(self, forbidden_names=None):
        """
        This method unname all bound vars in self. If forbidden_name is not
        None, then only var with name in forbidden_names are unnamed.
        """

        # bound_var = self.bound_var
        # if bound_var:
        #     bound_var.set_unnamed_bound_var()
        #
        # for child in self.children:
        #     if child.is_prop(is_math_type=True):
        #         child.unname_all_bound_vars()

        for bv in self.bound_vars():
            if (not forbidden_names) or bv.name in forbidden_names:
                bv.set_unnamed_bound_var()

    def rename_all_bound_vars(self):
        for bv in self.bound_vars():
            bv.rename()


MathObject.NO_MATH_TYPE = MathObject(node="not provided",
                                     info={},
                                     children=[],
                                     math_type=None)


MathDescendant.NO_MATH_TYPE = MathObject.NO_MATH_TYPE


MathObject.NO_MORE_GOALS = MathObject(node="NO_MORE_GOAL",
                                      info={},
                                      children=[],
                                      math_type=None)

MathObject.CURRENT_GOAL_SOLVED = MathObject(node="CURRENT_GOAL_SOLVED",
                                            info={},
                                            children=[],
                                            math_type=None)

MathObject.PROP = MathObject(node="PROP",
                             info={},
                             children=[],
                             math_type=None)


class BoundVar(MathObject):
    is_bound_var = True  # Override MathObject attribute
    is_unnamed = False
    untouched_bound_var_names = ["RealSubGroup", "IntegerSubGroup",
                                 "_inst_1", "_inst_2", "inst_3"]

    identifier_nb = 0

    def __init__(self, node, info, children, math_type,
                 parent=None, deep_copy=False, keep_name=False):
        """
        The local context is the list of BoundVar instances that are
        meaningful where self is introduced. In particular, self's name
        should be different from all these (and from all the names of the
        (global) context variables).
        """
        MathObject.__init__(self, node, info, children, math_type)
        self.parent = parent

        if not deep_copy and not keep_name:  # FIXME: unused?
            self.is_unnamed = True
            self.set_unnamed_bound_var()
            if self.keep_lean_name():
                self.name_bound_var(self.lean_name)
        self._local_context = []

        self.set_id_nb()

    def is_equal_to(self, other,
                    remove_generic_paren=False,
                    use_assigned_math_obj=False,
                    return_msg=False) -> (bool, str):
        """
        For compatibility with MathObject.is_equal_to().
        """

        if self == other:
            return True, ""
        else:
            msg = (self.name + " ≠ " + other.to_display(format_="utf8") if
                   return_msg else "")
            return False, msg

    def __eq__(self, other):
        """
        During an equality test for MathObjects, matching BoundVar are
        numbered by the same number. Equality test for bound var amounts to
        equality of their numbers.
        """
        # The following happens when comparing portions of self
        #  e.g. for matching MetaVars
        if self is other:
            return True

        elif isinstance(other, BoundVar):
            if self.bound_var_nb() != -1:
                return self.bound_var_nb() == other.bound_var_nb()
            else:
                # Is this too easy??
                return self.name == other.name and self.lean_name == other.lean_name
        else:
            return False

    def __repr__(self):
        return self.debug_repr('BV')

    @classmethod
    def from_math_type(cls, math_type, parent=None):
        """
        Return a new bound var of given math_type.
        """

        if parent is None:
            parent = MathObject.NO_MATH_TYPE
        info = {'name': "NO NAME",  # DO NOT MODIFY THIS !!
                'lean_name': ''}
        bound_var = BoundVar(node="LOCAL_CONSTANT",
                             info=info,
                             children=[],
                             math_type=math_type,
                             parent=parent)
        return bound_var

    def set_id_nb(self):
        """
        Set a unique identifier nb for self. This nb should be copied
        identically when self is deep_copied.
        """
        if not self.info.get('identifier_nb'):
            BoundVar.identifier_nb += 1
            self.info['identifier_nb'] = BoundVar.identifier_nb

        # print(f"New bv {self.name} with id {self.id_nb}")

    def refer_to_the_same_bound_var(self, other):
        """
        True iff self and other have the same identifier nb.
        """
        if not isinstance(other, BoundVar):
            return False
        id_nb1 = self.info.get('identifier_nb')
        id_nb2 = other.info.get('identifier_nb')
        return id_nb1 and (id_nb1 == id_nb2)

    @property
    def id_nb(self):
        return self.info.get('identifier_nb')

    @property
    def name(self):
        # TODO: make it an attribute
        return self.info['name']

    @property
    def lean_name(self):
        name = self.info.get('lean_name')
        if not name:
            name = self.info.get('name')
        return name

    def keep_lean_name(self):
        if (self.lean_name in self.untouched_bound_var_names
                or self.lean_name.startswith("_inst_")):
            return True

    @property
    def local_context(self):
        return self._local_context

    @local_context.setter
    def local_context(self, local_context):
        self._local_context = local_context

################
# Name methods #
################
    def preferred_letter(self) -> str:
        """
        Return a preferred letter for naming self. We want to use such a
        letter when self is a number, because numbers are designed by
        distinct letters according to their mathematical meaning.
        This letter is based on the lean name, from the lean source file.
        We allow exceptional cases: if the lean name ends with '__' then it
        will also be used, whatever self's math_type is.
        """

        lean_name = self.info.get('lean_name', '')
        old_name = self.info.get('old_name', '')
        if lean_name in ("NO NAME", '*no_name*', '?'):
            lean_name = ''
        letter = (lean_name[:-2] if lean_name.endswith('__')
                  else lean_name if (lean_name and self.math_type.is_number())
                  else 'n' if self.math_type.is_N()
                  else 'x' if self.math_type.is_R()
                  else old_name if old_name  # FIXME: trial
                  else '')
        sub = letter.find('_')
        if sub > 0:
            letter = letter[:sub]
        prime = letter.find("'")
        if prime > 0:
            letter = letter[:prime]

        if letter.isalpha():
            return letter
        else:
            return ''

    def name_bound_var(self, name: str):
        """
        FIXME: this should be the only way to name a bound var.
        """
        self.info['name'] = name
        self.is_unnamed = False

    def set_unnamed_bound_var(self):

        lean_name = self.info.get('lean_name', '')
        old_name = self.info.get('name', '')
        if lean_name in ("NO NAME", '*no_name*'):
            lean_name = ''
        if lean_name and lean_name.endswith('.BoundVar'):
            # Remove suffix
            lean_name = lean_name[:-len('.BoundVar')]
        if not lean_name:
            lean_name = old_name
            if lean_name and lean_name.endswith('.BoundVar'):
                # Remove suffix
                lean_name = lean_name[:-len('.BoundVar')]
            if lean_name in ("NO NAME", '*no_name*'):
                lean_name = ''

        new_info = {'name': "NO NAME",  # DO NOT MODIFY THIS !!
                    'lean_name': lean_name,
                    'old_name': old_name,
                    'bound_var_nb': -1}
        self.info.update(new_info)
        self.is_unnamed = True

    def rename(self):
        if self.is_unnamed:
            old_name = self.info.get('old_name')
            if old_name:
                self.name_bound_var(old_name)

    def bound_var_nb(self):
        return self.info.get('bound_var_nb')

    def mark_identical_bound_vars(self, other):
        """
        Mark two bound variables with a common number, so that we can follow
        them along two quantified expressions and check if these expressions
        are identical
        """
        MathObject.bound_var_counter += 1
        self.info['bound_var_nb'] = MathObject.bound_var_counter
        other.info['bound_var_nb'] = MathObject.bound_var_counter

    def unmark_bound_var(self):
        """
        Unmark the two bound vars.
        """
        self.info['bound_var_nb'] = -1

#################################
# Methods for PatternMathObject #
#################################
    def recursive_match(self, other, metavars, metavar_objects,
                        symmetric_match=False, debug=False, return_msg=False)\
                        -> (bool, str):
        """
        For compatibility with the PatternMathObject class.
        """
        if other.is_bound_var and self.bound_var_nb() == other.bound_var_nb():
            return True, ""
        else:
            if return_msg:
                error_msg = (self.try_to_display() + " ≠match "
                             + other.try_to_display())
            else:
                error_msg = ""
            return False, error_msg

    def math_object_from_matching(self, metavars=None, metavars_objects=None,
                                  original_bound_vars=None,
                                  copied_bound_vars=None):
        """
        Just return a smart copy of self.
        """

        # return copy(self)
        return self.smart_duplicate(original_bound_vars, copied_bound_vars)

    def smart_duplicate(self, original_bound_vars, copied_bound_vars,
                        keep_name=False):
        """
        Duplicate self once, then take the same copy for further duplication
        of self.
        """

        if self in original_bound_vars:
            # Self has already been duplicated
            idx = original_bound_vars.index(self)
            return copied_bound_vars[idx]

        # Copy info so that names become independent!
        new_info = {key: value for key, value in self.info.items()}
        new_self = BoundVar(node=self.node,
                            children=self.children,
                            math_type=self.math_type,
                            info=new_info,
                            keep_name=keep_name)

        # Add self to copied_bound_vars
        original_bound_vars.append(self)
        copied_bound_vars.append(new_self)

        return new_self

