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
from typing import          List, Any, Optional, Union
from copy import copy
import logging

if __name__ == "__main__":
    pass

import deaduction.pylib.config.vars            as cvars
# from deaduction.pylib.math_display import (
#                                            latex_from_node, recursive_display,
#                                            raw_latex_shape_from_couple_of_nodes,
#                                            raw_latex_shape_from_specific_nodes,
#                                            shallow_latex_to_text,
#                                            abstract_string_to_string)

from deaduction.pylib.give_name.give_name import name_single_bound_var

# from deaduction.pylib.math_display.utils import *

log = logging.getLogger(__name__)
global _

# NUMBER_SETS_LIST = ['ℕ', 'ℤ', 'ℚ', 'ℝ']

CONSTANT_IMPLICIT_ARGS = ("real.decidable_linear_order",)


def allow_implicit_use(test: callable) -> callable:
    """
    Modify the function test to allow implicit use of the definitions
    whose patterns are in MathObject.definition_patterns.
    'test' is typically 'is_and', 'is_or', 'is_forall', ...
    """

    def test_implicit(math_object,
                      is_math_type=False,
                      implicit=False) -> bool:
        """
        Apply test to math_object.

        :param implicit:     if False, implicit definitions are not used.
        """
        implicit = implicit and cvars.get(
            "functionality.allow_implicit_use_of_definitions")
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
                pattern_right = pattern.children[1]
                log.debug(f"(Trying definition "
                      f"{MathObject.implicit_definitions[index].pretty_name}"
                      f"...)")
                if pattern_left.match(math_type):
                    if test(pattern_right, is_math_type=True):
                        definition = MathObject.implicit_definitions[index]
                        MathObject.last_used_implicit_definition = definition
                        rw_math_object = pattern_right.apply_matching()
                        MathObject.last_rw_object = rw_math_object
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
# @dataclass
class MathObject:
    """
    Python representation of mathematical entities,
    both objects (sets, elements, functions, ...)
    and properties ("a belongs to A", ...)
    NB : When instancing, math_type and item in the children list must be
    instances of MathObject (except for the constant NO_MATH_TYPE)
    """

    node              : str   # e.g. "LOCAL_CONSTANT", "FUNCTION", "QUANT_∀"
    info              : dict  # e.g. "name", "id", "pp_type"
    children          : list  # List of MathObjects

    Variables = {}  # Containing every element having an identifier,
    # i.e. global and bound variables. This is used to avoid duplicate.
    # key = identifier,
    # value = MathObject
    NUMBER_SETS_LIST = ['ℕ', 'ℤ', 'ℚ', 'ℝ']
    number_sets = []  # Ordered list of all sets of numbers involved in some
    # MathObjects of the context, ordered sublist of ['ℕ', 'ℤ', 'ℚ', 'ℝ']
    # So that MathObject.number_sets[-1] always return the largest set of
    # numbers involved in the current exercise
    bound_var_counter = 0  # A counter to distinguish bound variables

    # Lists from definitions for implicit use
    #   This is set up at course loading, via the PatternMathObject
    #   set_definitions_for_implicit_use() method.
    definitions = []
    implicit_definitions          = []
    definition_patterns           = []
    # The following class attributes are modified each time an implicit
    # definition is used with success:
    last_used_implicit_definition = None
    last_rw_object                = None
    is_bound_var                  = False  # Default value

    # Nodes of math objects that need instantiation of bound variables
    HAVE_BOUND_VARS = ("QUANT_∀", "QUANT_∃", "QUANT_∃!", "SET_INTENSION",
                       "LAMBDA")  # "EXTENDED_SEQUENCE", "EXTENDED_SET_FAMILY")

    INEQUALITIES = ("PROP_<", "PROP_>", "PROP_≤", "PROP_≥", "PROP_EQUAL_NOT")

    def __init__(self, node, info, children, math_type=None,
                 is_bound_var=False):
        """
        Create a MathObject.
        """
        self.node = node
        self.info = info
        self.math_type = math_type
        if is_bound_var:
            self.is_bound_var = is_bound_var

        if node in self.HAVE_BOUND_VARS:
            #################################################################
            # Quantifiers & lambdas: provisionally "unname" bound variables #
            #################################################################
            # NB: info["name"] is given by structures.lean,
            # but may be inadequate (e.g. two distinct variables sharing the
            # same name)
            # This lean name is saved in info['lean_name'],
            # and info['name'] = "NO NAME" until proper naming
            # This is where the local constant is marked as bound var.

            # Every object here should have children matching this:
            bound_var_type, bound_var, local_context = children
            bound_var.is_bound_var = True
            bound_var.set_unnamed_bound_var(bound_var_type)

        ##################################################################
        # APP: uncurryfying APP(APP(1, 2, ...), n) --> APP(1, 2, ..., n) #
        ##################################################################
        if node == 'APPLICATION' and children[0].node == 'APPLICATION':
            children = children[0].children + [children[1]]

        self.children = children

    def __repr__(self):
        return self.to_display(format_="utf8")

    def add_bound_var(self, bound_var_type=None):
        """
        We add a new dummy var to self.children, and name it.
        """
        new_bound_var = MathObject.new_bound_var(bound_var_type)
        name_single_bound_var(new_bound_var)
        self.children.append(new_bound_var)

    def process_sequences_and_likes(self):
        """
        FIXME: obsolete doc, we just add a dummy var to help display.
        This method is called at each MathObject instantiation from lean
        info and children. Local constant representing set families or
        sequences ar modified to obtain the very special display, e.g.
        {E_i, i in I}       instead of E
        (u_n)_{n in N}      instead of u
        For this the MathObject is modified, in particular children are
        added including the bound var, its type, and the body. Note that
        __lambda_var_n_body that creates a duplicate version of the ORIGINAL
        (NOT EXPANDED) self, and body is something like
        APPLICATION(non expanded duplicate, var).
        """
        # if (self.is_sequence() or self.is_set_family())\
        #         and self.node.find("_EXPANDED_") == -1:
        #     log.debug(f"processing sequence {self.display_debug}")
        #     bound_var, body = self.__lambda_var_n_body()
        #     bound_var_type = self.math_type.children[0]
        #     self.children = [bound_var_type, bound_var, body]
        #     self.node += "_EXPANDED_" + self.math_type.node
        if self.is_sequence() or self.is_set_family():
            if self.is_lambda(is_math_type=True):
                pass
            elif not self.children:
                bound_var_type = self.math_type.children[0]
                self.add_bound_var(bound_var_type)

    def duplicate(self):
        """
        Create a copy of self, by duplicating the info dic.
        Beware that children of duplicates are children of self, not copies!
        """
        new_info = copy(self.info)
        other = MathObject(node=self.node, info=new_info,
                           children=self.children, math_type=self.math_type)
        return other

    @property
    def math_type(self) -> Any:
        """
        This is a work-around to the impossibility of defining a class
        recursively. Thus every instance of a MathObject has a math_type
        which is a MathObject (and has a node, info dict, and children list)
        The constant NO_MATH_TYPE is defined below, after the methods
        """
        if self._math_type is None:
            return MathObject.NO_MATH_TYPE
        else:
            return self._math_type

    @math_type.setter
    def math_type(self, math_type: Any):
        self._math_type = math_type

    def is_no_math_type(self):
        return self is self.NO_MATH_TYPE

    ######################
    # Bound vars methods #
    ######################
    @property
    def bound_vars(self, include_sequences=False):
        """Recursively determine the list of all bound vars in self. May
        include bound vars used to display sequences and likes.
        """
    
        if self.node == "LOCAL_CONSTANT" and not include_sequences:
            # Do not return bound vars in sequences/set families/...
            return []
        elif self.is_bound_var:
            return [self]
        else:
            return sum([child.bound_vars for child in self.children], [])

    def remove_names_of_bound_vars(self, include_sequences=False):
        """
        Un-name dummy variables of propositions in self.
        This excludes bound vars used to display lambdas, sequences and set
        families.
        @param include_sequences: 
        """
        
        if self.node == "LOCAL_CONSTANT" and not include_sequences:
            return
        elif self.is_bound_var:
            self.set_unnamed_bound_var()
        else:
            for child in self.children:
                child.remove_names_of_bound_vars(include_sequences)

    def set_unnamed_bound_var(self, bound_var_type=None):
        new_info = {'name': "NO NAME",  # DO NOT MODIFY THIS !!
                    'lean_name': self.info.get('name', ''),
                    'bound_var_nb': -1}
        self.info.update(new_info)
        if bound_var_type:
            self.math_type = bound_var_type
        # self.is_bound_var = True

    @classmethod
    def new_bound_var(cls, math_type):
        """
        Return a new bound var of given math_type.
        """
        bound_var = cls(node="LOCAL_CONSTANT",
                        info={},
                        children=[],
                        math_type=math_type,
                        is_bound_var=True)
        bound_var.set_unnamed_bound_var()
        return bound_var

    def is_unnamed(self):
        return self.display_name == "NO NAME" \
               or self.display_name == '*no_name*'

    def unnamed_bound_vars(self):
        """
        Only unnamed bound vars, tested by is_unnamed method.
        """
        return [var for var in self.bound_vars if var.is_unnamed()]

    def bound_var_nb(self):
        return self.info.get('bound_var_nb')

    def longest_bound_vars_chain(self,
                                 include_sequences=False,
                                 math_type=None):
        """
        Return one of the longest unbound vars chains of self. A chain of
        bound vars is a list of bound vars which cannot pairwise share the same
        name. Each chain corresponds to a leaf of the tree, and contains all
        the bound vars whose corresponding brother-body appears in the path
        from the root to the leaf.
        """
        
        if self.node == "LOCAL_CONSTANT" and not include_sequences:
            # Do not return bound vars in sequences/set families/...
            return []

        # Add self's child bound var if any
        # (this is pertinent only if self in HAVE_BOUND_VARS)
        # This should contain at most one element
        child_bound_vars = [child for child in self.children
                            if child.is_bound_var]
        if math_type:  # Filters by math_type
            child_bound_vars = [child for child in child_bound_vars
                                if child.math_type == math_type]
        assert len(child_bound_vars) <= 1

        # Find the longest chain among children
        longest = []
        for child in self.children:
            maybe_longer = child.longest_bound_vars_chain(include_sequences,
                                                          math_type)
            if len(maybe_longer) > len(longest):
                longest = maybe_longer
                
        return child_bound_vars + longest

    #################
    # Class methods #
    #################
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
    def FALSE(cls):
        """
        The constant FALSE as a MathObject.
        """
        return cls(node="PROP_FALSE", info={}, children=[], math_type="PROP")

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

        node = info.pop("node_name")
        if 'math_type' in info.keys():
            math_type = info.pop('math_type')
        else:
            math_type = None  # NB math_type is a @property, cf above

        #####################################################
        # Treatment of global variables: avoiding duplicate #
        #####################################################
        if 'identifier' in info.keys():
            # This concerns only MathObjects with node=='LOCAL_CONSTANT'
            identifier = info['identifier']
            if identifier in MathObject.Variables:
                # Return already existing MathObject
                math_object = MathObject.Variables[identifier]
            else:  # Create new object
                math_object = cls(node=node,
                                  info=info,
                                  math_type=math_type,
                                  children=children)
                MathObject.Variables[identifier] = math_object

        else:
            ##############################
            # End: generic instantiation #
            ##############################
            math_object = cls(node=node,
                              info=info,
                              math_type=math_type,
                              children=children)
        # Detect sets of numbers and insert in number_sets if needed
        # at the right place so that the list stay ordered
        name = math_object.display_name
        MathObject.add_numbers_set(name)

        # Special treatment for sequences and set families
        math_object.process_sequences_and_likes()
        return math_object

    #######################
    # Properties and like #
    #######################
    @property
    def has_unnamed_bound_vars(self):
        """
        Return True if self has some dummy vars whose name is "NO NAME".
        """
        for var in self.bound_vars:
            if var.is_unnamed():
                return True
        return False

    @property
    def name(self):
        return self.info.get('name')

    @property
    def value(self):
        return self.info.get('value')

    @property
    def display_name(self) -> str:
        """
        This is the name used to display in deaduction.
        """
        return self.name if self.name else '*no_name*'

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

    def nb_implicit_children(self):
        """
        e.g. APP(APP(...APP(x0,x1),...),xn) has (n+1) implicit children.
        cf self.implicit_children().
        """
        if not self.is_application():
            return 0

        if self.children[0].is_application():
            return 1 + self.children[0].nb_implicit_children()
        else:
            return 2

    def implicit_children(self, nb):
        """
        Only when self.is_application().
        e.g. APP(APP(...APP(x0,x1),...),xn) is considered equivalent to
             APP(x0, x1, ..., xn)
        and x0, ... , xn are the (n+1) implicit children.
        """
        if not self.is_application():
            return None

        # From now on self is_application(), and so has exactly 2 children
        nb_children = self.nb_implicit_children()
        if nb < 0:
            nb = nb_children + nb

        if nb == nb_children - 1:
            return self.children[1]
        elif nb_children == 2 and nb == 0:  # APP(x0, x1)
            return self.children[0]
        else:
            return self.children[0].implicit_children(nb)

    def descendant(self, line_of_descent):
        """
        Return the MathObject corresponding to the line_of_descent
        e.g. self.descendant((1.0))  -> children[1].children[0]

        :param line_of_descent:     int or tuple or list
        :return:                    MathObject
        """
        if type(line_of_descent) == int:
            if self.is_application():
                return self.implicit_children(line_of_descent)
            else:
                return self.children[line_of_descent]

        child_number, *remaining = line_of_descent
        child = self.children[child_number]
        if not remaining:
            return child
        else:
            return child.descendant(remaining)

    def give_name(self, name):
        self.info["name"] = name

    def has_name(self, name: str):
        return self.display_name == name

##########################################
# Tests for equality and related methods #
##########################################

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

        # Successively test for
        #                           nodes
        #                           bound var nb
        #                           name
        #                           math_type
        #                           children

        # Include case of NO_MATH_TYPE (avoid infinite recursion!)
        if self is other:
            return True

        if other is None or not isinstance(other, MathObject):
            return False

        #########################################
        # Test node, bound var, name, math_type #
        #########################################
        if (self.node, self.bound_var_nb(), self.name, self.value,
            self.math_type) != \
                (other.node, other.bound_var_nb(), other.name, other.value,
                 other.math_type):
            return False

        #################################
        # Recursively test for children #
        #################################
        elif len(self.children) != len(other.children):
            return False
        else:
            equal = True
            bound_var_1 = None
            bound_var_2 = None

            ##############
            # Bound vars #
            ##############
            # Mark bound vars in quantified expressions to distinguish them
            if self.node in self.HAVE_BOUND_VARS:
                # Here self and other are assumed to be a quantified proposition
                # and children[1] is the bound variable.
                # We mark the bound variables in self and other with same number
                # so that we know that, say, 'x' in self and 'y' in other are
                # linked and should represent the same variable everywhere
                bound_var_1 = self.children[1]
                bound_var_2 = other.children[1]
                bound_var_1.mark_identical_bound_vars(bound_var_2)

            for child0, child1 in zip(self.children, other.children):
                if child0 != child1:
                    equal = False

            # Unmark bound_vars
            if bound_var_1:
                bound_var_1.unmark_bound_var()
                bound_var_2.unmark_bound_var()

            return equal

    def contains(self, other) -> int:
        """
        Compute the number of copies of other contained in self.
        """
        if MathObject.__eq__(self, other):
            return 1
        else:
            # counter = 0
            # for math_object in self.children:
            #     counter += math_object.contains(other)
            return sum([child.contains(other) for child in self.children])

    def direction_for_substitution_in(self, other) -> str:
        """
        Assuming self is an equality or an iff,
        and other a property, search if
        left/right members of equality self appear in other.

        WARNING: does not work if the equality (or iff) is hidden behind
        'forall", so for the moment we cannot use this when applying statements
        TODO: improve this
        FIXME: not used
        :return:
            - None,
            - '>' if left member appears, but not right member,
            - '<' in the opposite case,
            - 'both' if both left and right members appear
        """
        equality = self.math_type
        if equality.node not in ['PROP_EQUAL', 'PROP_IFF']:
            return ''
        left, right = equality.children
        contain_left = other.contains(left)
        contain_right = other.contains(right)
        decision = {(False, False): '',
                    (True, False): '>',
                    (False, True): '>',
                    (True, True): 'both'
                    }
        return decision[contain_left, contain_right]

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

    def is_type(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is a "universe"
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "TYPE"

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

        math_type_of_math_type = math_type.math_type
        if math_type.node == "LOCAL_CONSTANT":
            if not (math_type_of_math_type.is_prop(is_math_type=False) or
                    math_type_of_math_type.is_type(is_math_type=True) or
                    math_type_of_math_type == MathObject.NO_MATH_TYPE):
                return True
        return False

    def is_sequence(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is a "universe"
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "SEQUENCE"

    def is_set_family(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is a "universe"
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "SET_FAMILY"

    def is_lambda(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is a "universe"
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
        Test if (math_type of) self is a function.
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

    def is_equality(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is an equality.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "PROP_EQUAL"

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

    def is_instance(self) -> bool:
        """
        Test if self is a variable whose name begins by "_inst";
        that is, self represents a proof that some type is an instance of
        some class (information that should not be displayed in deaduction)
        """
        lean_name = self.info.get("lean_name")
        if lean_name:
            if lean_name.startswith("_inst_"):
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
        return self.display_name == 'ℤ'

    def is_Q(self):
        return self.display_name == 'ℚ'

    def is_R(self):
        return (self.display_name == 'ℝ'
                or self.display_name == 'RealSubGroup')

    def is_iff(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is 'PROP_IFF'.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type

        return math_type.node == "PROP_IFF"

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
        Assuming self is "not P", return P. Handle special cases of not
        belong, not equal.
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
    def can_be_used_for_implication(self, is_math_type=False) -> bool:
        """
        Determines if a proposition can be used as a basis for implication,
        i.e. is of the form
            (∀ ...)*  P => Q
         with zero or more universal quantifiers at the beginning.

        This is a recursive function.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        if math_type.is_implication(is_math_type=True):
            return True
        elif math_type.is_for_all(is_math_type=True):
            # NB : ∀ var : type, body
            body = math_type.children[2]
            # Recursive call
            return body.can_be_used_for_implication(is_math_type=True)
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

    ########################
    # Implicit definitions #
    ########################
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
                rw_math_object = pattern_right.apply_matching()
                rw_math_objects.append(rw_math_object)
                name = MathObject.implicit_definitions[index].pretty_name
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
        Return the definitions that match self.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type

        definitions = MathObject.definitions
        matching_defs = [defi for defi in definitions if defi.match(math_type)]
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
        """

        # Fixme: not used (?)
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

    ###############################
    # Collect the local variables #
    ###############################
    def extract_local_vars(self) -> list:
        """
        Recursively collect the list of variables used in the definition of
        self (leaves of the tree). Here by definition, being a variable
        means having an info["name"] which is not "NO NAME".
        :return: list of MathObject instances
        """
        # TODO: change by testing if node == "LOCAL_CONSTANT"?
        if "name" in self.info.keys() and self.info['name'] != 'NO NAME':
            return [self]
        local_vars = []
        for child in self.children:
            local_vars.extend(child.extract_local_vars())
        return local_vars

    def extract_local_vars_names(self) -> List[str]:  # deprecated
        """
        Collect the list of names of variables used in the definition of self
        (leaves of the tree)
        """
        return [math_obj.info["name"] for
                math_obj in self.extract_local_vars()]

    ################################################
    # Display methods: implemented in math_display #
    ################################################
    def to_display(self, format_="html", text=False,
                   use_color=True, bf=False, is_type=False) -> str:
        return self

    def math_type_to_display(self, format_="html", text=False,
                             is_math_type=False,
                             used_in_proof=False) -> str:
        return self

    # def raw_latex_shape(self, negate=False, text_depth=0):
    #     """
    #     e.g. if self is a MathObject whose node is 'PROP_EQUAL', this method
    #     will return [0, " = ", 1].
    #     """
    #     # (1) Case of special shape from self and its first child:
    #     # NB: here the structure do depend on text_depth
    #     shape = raw_latex_shape_from_couple_of_nodes(self, text_depth)
    #     if shape:
    #         # NEGATION:
    #         if negate:
    #             shape = [" " + r'\not' + " ", r'\parentheses', shape]
    #         # log.debug(f"Shape from couples: {shape}")
    #
    #     # (2) Generic case, in latex_from_node
    #     elif self.node in latex_from_node:
    #         shape = list(latex_from_node[self.node])
    #
    #         # NEGATION:
    #         if negate:
    #             shape = [" " + r'\not' + " ", r'\parentheses', shape]
    #     # (3) Node not found in dictionaries: try specific methods
    #     else:
    #         shape = raw_latex_shape_from_specific_nodes(self, negate)
    #
    #     # log.debug(f"    --> Raw shape: {shape}")
    #     return shape
    #
    # def to_abstract_string(self, text_depth=0) -> Union[list, str]:
    #     """
    #     Return an abstract string representing self, as a tree of string.
    #
    #     (1) First compute the shape, e.g. [0, " = ", 1].
    #     (2) Then compute an "expanded latex shape", a tree of strings with
    #     latex macro.
    #     (3) if text_depth >0, replace some symbols by plain text.
    #     """
    #
    #     # (1) Compute shape
    #     shape = self.raw_latex_shape(negate=False, text_depth=text_depth)
    #
    #     # (2) Compute tree of strings
    #     abstract_string = recursive_display(self, text_depth=text_depth,
    #                                         shape=shape)
    #
    #     # (3) Replace some symbols by plain text:
    #     abstract_string = shallow_latex_to_text(abstract_string, text_depth)
    #
    #     return abstract_string
    #
    # def to_display(self, format_="html", text_depth=0,
    #                use_color=True, bf=False) -> str:
    #     """
    #     Return a displayable string version of self. First compute an
    #     abstract_string (i.e. a tree version) taking text_depth into account,
    #     then concatenate according to format_.
    #
    #     Note that nice display of negations is obtained in raw_latex_node
    #     and recursive_display.
    #
    #     :param format_:     one of 'utf8', 'html', 'latex'
    #     :param text_depth:  if >0, will try to replace symbols by plain text
    #     for the upper branches of the MathObject tree
    #     :param use_color: use colors in html format
    #     :param bf: use boldface fonts in html format.
    #     """
    #     # TODO: the case when text_depth is >0 but not "infinity" has not
    #     #  been tested.
    #     # WARNING: if you make some changes here,
    #     #   then you probably have to do the same changes in
    #     #   ContextMathObject.math_type_to_display.
    #
    #     # (1) Tree of strings
    #     abstract_string = self.to_abstract_string(text_depth)
    #     log.debug(f"Abstract string: {abstract_string}")
    #
    #     # (2) Adapt to format_ and concatenate to get a string
    #     display = abstract_string_to_string(abstract_string, format_,
    #                                         use_color=use_color, bf=bf,
    #                                         no_text=(text_depth <= 0))
    #     return display
    #
    # def raw_latex_shape_of_math_type(self, text_depth=0):
    #     ########################################################
    #     # Special math_types for which display is not the same #
    #     ########################################################
    #     # math_type = self.math_type
    #     math_type = self
    #     if math_type.node == "SET":
    #         shape = [r'\type_subset', 0]
    #     elif math_type.node == "SEQUENCE":
    #         shape = [r'\type_sequence', 1]
    #     elif math_type.node == "SET_FAMILY":
    #         shape = [r'\type_family_subset', 1]
    #     elif hasattr(math_type, 'math_type') \
    #             and hasattr(math_type.math_type, 'node') \
    #             and math_type.math_type.node in ("TYPE", "SET")\
    #             and math_type.node != 'TYPE'\
    #             and math_type.node != 'FUNCTION':
    #             # and math_type.info.get('name'):
    #         # name = math_type.info["name"]
    #         # FIXME: bad format for html, would need format_
    #         name = math_type.to_display(text_depth=text_depth, format_='utf8')
    #         shape = [r'\type_element', name]
    #         # The "an" is to be removed for short display
    #     elif math_type.is_N():
    #         shape = [r'\type_N']
    #     elif math_type.is_Z():
    #         shape = [r'\type_Z']
    #     elif math_type.is_Q():
    #         shape = [r'\type_Q']
    #     elif math_type.is_R():
    #         shape = [r'\type_R']
    #     else:  # Generic case: usual shape from math_object
    #         shape = math_type.raw_latex_shape(text_depth=text_depth)
    #
    #     # log.debug(f"Raw shape of math type: {shape}")
    #     return shape
    #
    # def math_type_to_abstract_string(self, text_depth=0):
    #     """
    #     cf to_abstract_string, but applied to self as a math_type.
    #     :param text_depth:
    #     :return:
    #     """
    #     shape = self.raw_latex_shape_of_math_type(text_depth=text_depth)
    #     abstract_string = recursive_display(self,
    #                                         shape=shape,
    #                                         text_depth=text_depth)
    #     log.debug(f"Abstract string of type: {abstract_string}")
    #
    #     # Replace some symbol by plain text:
    #     abstract_string = shallow_latex_to_text(abstract_string, text_depth)
    #
    #     return abstract_string
    #
    # def math_type_to_display(self, format_="html", text_depth=0,
    #                          is_math_type=False,
    #                          used_in_proof=False) -> str:
    #     """
    #     cf MathObject.to_display, but applied to self as a math_type (if
    #     is_math_type) or to self.math_type (if not is_math_type).
    #     Lean format_ is not pertinent here.
    #     """
    #     log.debug(f"Displaying math_type: {self.display_name}...")
    #
    #     if is_math_type:
    #         math_type = self
    #     else:
    #         math_type = self.math_type
    #     abstract_string = math_type.math_type_to_abstract_string(text_depth)
    #     if used_in_proof:
    #         abstract_string = [r'\used_property'] + abstract_string
    #     # Adapt to format_ and concatenate to get a string
    #     display = abstract_string_to_string(abstract_string, format_,
    #                                         no_text=(text_depth <= 0))
    #
    #     return display

    def __lambda_var_n_body(self):
        """
        Given a MathObject that codes for
            a sequence u = (u_n)_{n in N}
            or a set family E = {E_i, i in I}
        (but maybe a lambda expression), returns the body, that corresponds to
        "u_n" or "E_i".
        """
        if self.is_lambda(is_math_type=True):
            body = self.children[2]
            bound_var = self.children[1]
            name_single_bound_var(bound_var)
        else:
            # NB: math_type is "SET FAMILY ( X, set Y)"
            #   or "SEQUENCE( N, Y)
            # Change type to avoid infinite recursion:
            raw_version = self.duplicate()
            bound_var_type = self.math_type.children[0]
            bound_var = MathObject.new_bound_var(bound_var_type)
            math_type = self.math_type.children[1]
            body = MathObject(node="APPLICATION",
                              info={},
                              children=[raw_version, bound_var],
                              math_type=math_type)

        name_single_bound_var(bound_var)
        return bound_var, body

    # @classmethod
    # def PROP_AS_MATHOBJECT(cls):
    #     return MathObject(node="PROP",
    #                       info={},
    #                       children=[],
    #                       math_type=None)


MathObject.NO_MATH_TYPE = MathObject(node="not provided",
                                     info={},
                                     children=[],
                                     math_type=None)

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

