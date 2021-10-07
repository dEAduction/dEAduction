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
from typing import          List, Any, Optional
from copy import copy
import logging

if __name__ == "__main__":
    import deaduction.pylib.config.i18n

import deaduction.pylib.config.vars            as cvars
from deaduction.pylib.mathobj.display_data import (HAVE_BOUND_VARS,
                                                   INEQUALITIES,
                                                   latex_from_node,
                                                   latex_to_utf8)
from deaduction.pylib.mathobj.display_math import \
    (Shape,
     recursive_display,
     raw_latex_shape_from_couple_of_nodes,
     raw_display_math_type_of_local_constant,
     raw_latex_shape_from_specific_nodes,
     shallow_latex_to_text)
from deaduction.pylib.mathobj.html_display import html_display
from deaduction.pylib.mathobj.utf8_display import utf8_display


from deaduction.pylib.mathobj.utils        import *

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
    bound_vars        : Optional[list]  # All bound vars (including children)

    Variables = {}  # Containing every element having an identifier,
    # i.e. global and bound variables. This is used to avoid duplicate.
    # key = identifier,
    # value = MathObject
    NUMBER_SETS_LIST = ['ℕ', 'ℤ', 'ℚ', 'ℝ']
    number_sets = []  # Ordered list of all sets of numbers involved in some
    # MathObjects of the context, ordered sublist of ['ℕ', 'ℤ', 'ℚ', 'ℝ']
    # So that MathObject.number_sets[-1] always return the largest set of
    # numbers involved in the current exercise
    bound_var_number = 0  # A counter to distinguish bound variables

    # Lists from definitions for implicit use
    #   This is set up at course loading, via the PatternMathObject
    #   set_definitions_for_implicit_use() method.
    implicit_definitions          = []
    definition_patterns           = []
    # The following class attributes are modified each time an implicit
    # definition is used with success:
    last_used_implicit_definition = None
    last_rw_object                = None

    def __init__(self, node, info, children, bound_vars=None, math_type=None):
        """
        Create a MathObject. If bound_vars is None then the dummy vars list is
        inferred from the children's lists and the node.
        """
        # if bound_vars is None:
        #     bound_vars = []
        #     for child in children:
        #         bound_vars.extend(child.bound_vars)
        #     if node in HAVE_BOUND_VARS:
        #         bound_var_type, bound_var, local_context = children
        #         bound_vars.insert(0, bound_var)
        self.node = node
        self.info = info
        self.children = children
        self.bound_vars = bound_vars
        self.math_type = math_type

    def duplicate(self):
        """
        Create a copy of self, by duplicating the info dic.
        Beware that children of duplicates are children of self, not copies!
        """
        new_info = copy(self.info)
        other = MathObject(self.node, new_info, self.children)
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
            return NO_MATH_TYPE
        else:
            return self._math_type

    @math_type.setter
    def math_type(self, math_type: Any):
        self._math_type = math_type

    @property
    def bound_vars(self):
        """Store bound_vars to avoid repeated computation."""
        if not hasattr(self, "_bound_vars") or  not self._bound_vars:
            bound_vars = []
            for child in self.children:
                bound_vars.extend(child.bound_vars)
            if self.node in HAVE_BOUND_VARS:
                bound_var_type, bound_var, local_context = self.children
                bound_vars.insert(0, bound_var)
            self._bound_vars = bound_vars

        return self._bound_vars

    @bound_vars.setter
    def bound_vars(self, bound_vars: []):
        self._bound_vars = bound_vars

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
        cls.bound_var_number = 0
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
    def NO_MATH_TYPE(cls):
        """
        The type of having undefined type as a MathObject.
        """
        # TODO: replace global var
        return cls(node="not provided", info={}, children=[], math_type=None)

    @classmethod
    def from_info_and_children(cls, info: {}, children: []):
        """
        Create an instance of MathObject from the Lean data collected by
        the parser.
        :param info: dictionary with mandatory key  'node_name',
                                    optional keys   'math_type',
                                                    'name'
                                                    'identifier'
        :param children: list of MathObject instances
        :return: a MathObject
        """

        node = info.pop("node_name")
        if 'math_type' in info.keys():
            math_type = info.pop('math_type')
        else:
            math_type = None  # NB math_type is a @property, cf above

        bound_vars = []
        for child in children:
            bound_vars.extend(child.bound_vars)

        #####################################################
        # Treatment of global variables: avoiding duplicate #
        #####################################################
        if 'identifier' in info.keys():
            # This concerns only MathObjects with node=='LOCAL_CONSTANT'
            identifier = info['identifier']
            if identifier in MathObject.Variables:
                # Return already existing MathObject
                # log.debug(f"already exists in dict "
                #          f"{[(key, MathObject.Variables[key]) for key in
                #          MathObject.Variables]}")
                math_object = MathObject.Variables[identifier]
            else:
                # Create new object
                math_object = cls(node=node,
                                  info=info,
                                  math_type=math_type,
                                  children=children,
                                  bound_vars=[])
                MathObject.Variables[identifier] = math_object

        ##############################
        # Treatment of other objects #
        ##############################
        elif node in HAVE_BOUND_VARS:
            #################################################################
            # Quantifiers & lambdas: provisionally "unname" bound variables #
            #################################################################
            # NB: info["name"] is given by structures.lean,
            # but may be inadequate (e.g. two distinct variables sharing the
            # same name)
            # This lean name is saved in info['lean_name'],
            # and info['name'] = "NO NAME" until proper naming
            bound_var_type, bound_var, local_context = children
            new_info = {'name': "NO NAME",  # DO NOT MODIFY THIS !!
                        'lean_name': bound_var.info['name'],
                        'is_bound_var': True,
                        'quantifier': node}
            # Add info to help naming dummy var
            if local_context.is_implication(is_math_type=True):
                child = local_context.children[0]
                if child.is_inequality(is_math_type=True):
                    new_info['inequality'] = child.node
            bound_var.info.update(new_info)
            bound_var.math_type = bound_var_type
            bound_vars.insert(0, bound_var)
            math_object = cls(node=node,
                              info=info,
                              math_type=math_type,
                              children=children,
                              bound_vars=bound_vars)

        else:
            ##############################
            # End: generic instantiation #
            ##############################
            math_object = cls(node=node,
                              info=info,
                              math_type=math_type,
                              children=children,
                              bound_vars=bound_vars)
        # Detect sets of numbers and insert in number_sets if needed
        # at the right place so that the list stay ordered
        name = math_object.display_name
        MathObject.add_numbers_set(name)
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
    def display_name(self) -> str:
        """
        This is both Lean name and the name used to display in deaduction.
        """
        if 'name' in self.info:
            return self.info['name']
        else:
            return '*no_name*'

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

        # TODO: simplify handling of bound variables by using a global list
        #  MathObject.__marked_bound_vars
        #  instead of marking/unmarking bound vars.
        # Successively test for
        #                           nodes
        #                           name (if exists)
        #                           math_type
        #                           children

        equal = True    # Self and other are presumed to be equal
        marked = False  # Will be True if bound variables should be unmarked

        node = self.node
        # Case of NO_MATH_TYPE (avoid infinite recursion!)
        if self is NO_MATH_TYPE \
                and other is NO_MATH_TYPE:
            return True

        # Node
        elif node != other.node:
            # log.debug(f"distinct nodes {self.node, other.node}")
            return False

        # Mark bound vars in quantified expressions to distinguish them
        elif node in HAVE_BOUND_VARS:
            # Here self and other are assumed to be a quantified proposition
            # and children[1] is the bound variable.
            # We mark the bound variables in self and other with same number
            # so that we know that, say, 'x' in self and 'y' in other are
            # linked and should represent the same variable everywhere
            bound_var_1 = self.children[1]
            bound_var_2 = other.children[1]
            self.mark_bound_vars(bound_var_1, bound_var_2)
            marked = True

        # Names
        if 'name' in self.info.keys():
            # For bound variables, do not use names, use numbers
            if self.is_bound_var():
                if not other.is_bound_var():
                    equal = False
                # Here both are bound variables
                elif 'bound_var_number' not in self.info:
                    if 'bound_var_number' in other.info:
                        # The var already appeared in other but not in self
                        equal = False
                    else:
                        # Here both variable are unmarked. This means
                        # we are comparing two subexpressions with respect
                        # to which the variables are not local:
                        # names have a meaning
                        equal = (self.info['name'] == other.info['name'])
                # From now on self.info['bound_var_number'] exists
                elif 'bound_var_number' not in other.info:
                    equal = False
                # From now on both variables have a number
                elif (self.info['bound_var_number'] !=
                      other.info['bound_var_number']):
                    equal = False
            else:  # Self is not bound var
                if other.is_bound_var():
                    equal = False
                elif self.info['name'] != other.info['name']:
                    # None is a bound var
                    equal = False
                    # log.debug(f"distinct names "
                    #          f"{self.info['name'], other.info['name']}")
        # Recursively test for math_types
        elif self.math_type != other.math_type:
            log.debug(f"distinct types {self.math_type}")
            log.debug(f"other type     {other.math_type}")
            equal = False

        # Recursively test for children
        elif len(self.children) != len(other.children):
            equal = False
        else:
            for child0, child1 in zip(self.children, other.children):
                if child0 != child1:
                    equal = False

        # Unmark bound_vars, in prevision of future tests
        if marked:
            self.unmark_bound_vars(bound_var_1, bound_var_2)

        return equal

    def contains(self, other) -> int:
        """
        Compute the number of copies of other contained in self.
        """
        if MathObject.__eq__(self, other):
            counter = 1
        else:
            counter = 0
            for math_object in self.children:
                counter += math_object.contains(other)
        return counter

    def find_in(self, selection):
        """
        Try to find self in a list of math_objects.
        """
        if self in selection:
            index = selection.index(self)
        # else:
        #     for math_object in selection
        #        if math_object.contains(self)
        # ...
            return index

    @classmethod
    def mark_bound_vars(cls, bound_var_1, bound_var_2):
        """
        Mark two bound variables with a common number, so that we can follow
        them along two quantified expressions and check if these expressions
        are identical
        """
        cls.bound_var_number += 1
        bound_var_1.info['bound_var_number'] = cls.bound_var_number
        bound_var_2.info['bound_var_number'] = cls.bound_var_number

    @classmethod
    def unmark_bound_vars(cls, bound_var_1, bound_var_2):
        """
        Unmark the two bound vars.
        """
        bound_var_1.info.pop('bound_var_number')
        bound_var_2.info.pop('bound_var_number')

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
        return math_type.node in INEQUALITIES

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
        return self.display_name == 'Q'

    def is_R(self):
        return self.display_name == 'ℝ'

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

        return math_type.node in ("PROP_NOT", "PROP_NOT_BELONGS")

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

    def is_bound_var(self) -> bool:
        """
        Test if self is a bound variable by searching in the info dict
        """
        if 'is_bound_var' in self.info and self.info['is_bound_var']:
            return True
        else:
            return False

    def is_unnamed(self):
        return self.display_name == "NO NAME" \
               or self.display_name == '*no_name*'

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
                log.debug(f"Implicit definition {name} "
                          f"--> {rw_math_object.to_display()}")
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
                                    bound_vars=None,
                                    math_type=math_object.math_type)
        return rw_math_object

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

    ########################
    # Display math objects #
    ########################
    def raw_latex_shape(self, negate=False, text_depth=0):
        """
        e.g. if self is a MathObject whose node is 'PROP_EQUAL', this method
        will return [0, " = ", 1].
        Includes treatment of "in".
        """
        # Case of special shape from self and its first child:
        shape = raw_latex_shape_from_couple_of_nodes(self, text_depth)

        if shape:
            # NEGATION:
            if negate:
                shape = [r'\not', shape]
        else:
            if self.node in latex_from_node:  # Generic case
                shape = list(latex_from_node[self.node])

                # NEGATION:
                if negate:
                    shape = [r'\not', shape]
            else:  # Node not found in dictionaries: try specific methods
                shape = raw_latex_shape_from_specific_nodes(self, negate)

        # log.debug(f"    --> Raw shape: {shape}")
        return shape

    def expanded_latex_shape(self, text_depth=0):
        """
        Recursively fill the children of raw_display.
        e.g. if self is a MathObject coding for "f(x)=y", this method
        will return something like [[["f"], [\\parentheses, "x"]], " = ", "y"].
        If x is a dummy var then it will be replaced by [\\dummy_var, x].
        """
        display = recursive_display(self, text_depth)
        return display

    def to_display(self, format_="html", text_depth=0) -> str:
        """
        Return a displayable string version of self.

        (1) First compute an "expanded latex shape", a tree of strings with
        latex macro.
        (2) if text_depth >0, replace some symbols by plain text. In any case,
        take care of '\\in' according to the context.
        (3) Turn latex macro into utf8 text and/or html command.

        Note that
        - nice display of "in" is treated in raw_latex_shape
        - nice display of negations is obtained in raw_latex_node
        and recursive_display

        :param format_:     one of 'utf8', 'html', 'latex'
        :param text_depth:  if >0, will try to replace symbols by plain text
        for the upper branches of the MathObject tree.
        """

        # WARNING: if you make some changes here,
        #   then you probably have to do the same changes in
        #   ContextMathObject.math_type_to_display.
        # log.debug(f"Displaying {self.old_to_display()}...")
        # (1) Latex shape, includes treatment of "in"
        # needs_paren is called --> '\parentheses'
        abstract_string = self.expanded_latex_shape(text_depth=text_depth)
        # log.debug(f"(1) --> abstract string: {abstract_string}")
        # (2) Replace some symbol by plain text:
        display = shallow_latex_to_text(abstract_string, text_depth)
        # log.debug(f"(2) --> to text: {abstract_string}")
        # (3) Replace latex macro by utf8:
        if format_ in ('utf8', 'html'):
            display = latex_to_utf8(display)
        if format_ == 'html':
            display = html_display(display)
        elif format_ == 'utf8':
            display = utf8_display(display)
        # log.debug(f"    --> To html: {display}")
        return display

    def raw_latex_shape_of_math_type(self, text_depth=0):
        ########################################################
        # Special math_types for which display is not the same #
        ########################################################
        math_type = self.math_type
        if hasattr(math_type, 'math_type') \
                and hasattr(math_type.math_type, 'node') \
                and math_type.math_type.node == "TYPE":
            name = math_type.info["name"]
            shape = [_("an element of") + " ", name]
            # The "an" is to be removed for short display
        elif math_type.is_N():
            shape = [_('a non-negative integer')]
        elif math_type.is_Z():
            shape = [_('an integer')]
        elif math_type.is_Q():
            shape = [_('a rational number')]
        elif math_type.is_R():
            shape = [_('a real number')]
        elif math_type.node == "SET":
            shape = [_("a subset of") + " ", 0]
            # Idem
        elif math_type.node == "SEQUENCE":
            shape = [_("a sequence in") + " ", 1]
        elif math_type.node == "SET_FAMILY":
            shape = [_("a family of subsets of") + " ", 1]
        else:  # Generic case: usual shape from math_object
            shape = math_type.raw_latex_shape(text_depth=text_depth)

        log.debug(f"Raw shape of math type: {shape}")
        return shape

    def math_type_to_display(self, format_="html", text_depth=0) -> str:
        """
        cf MathObject.to_display
        """
        # log.debug(f"Displaying math_type: {self.old_to_display()}...")

        shape = self.raw_latex_shape_of_math_type(text_depth=text_depth)
        abstract_string = recursive_display(self.math_type,
                                            raw_display=shape,
                                            text_depth=text_depth)
        # Replace some symbol by plain text:
        display = shallow_latex_to_text(abstract_string, text_depth)
        # Replace latex macro by utf8:
        if format_ in ('utf8', 'html'):
            display = latex_to_utf8(display)
        if format_ == 'html':
            display = html_display(display)
        elif format_ == 'utf8':
            display = utf8_display(display)
        # log.debug(f"{self.old_to_display()} -> {display}")

        return display

    def old_to_display(self,
                       is_math_type=False,
                       format_="utf8",  # change to "latex" for latex...
                       text_depth=0
                       ) -> str:
        if is_math_type:
            shape = raw_display_math_type_of_local_constant(self, format_,
                                                        text_depth)
            shape.expand_from_shape()
        else:
            shape = Shape.from_math_object(self, format_, text_depth)

        # log.debug(f"Display: {shape.display}")
        return structured_display_to_string(shape.display)

    @classmethod
    def PROP_AS_MATHOBJECT(cls):
        return MathObject(node="PROP",
                          info={},
                          children=[],
                          math_type=None)


NO_MATH_TYPE = MathObject(node="not provided",
                          info={},
                          children=[],
                          math_type=None)


def structured_display_to_string(structured_display) -> str:
    """
    Turn a (structured) latex or utf-8 display into a latex string.

    :param structured_display:  type is recursively defined as str or list of
                                structured_display
    """
    if isinstance(structured_display, str):
        return structured_display
    elif isinstance(structured_display, list):
        string = ""
        for lr in structured_display:
            lr = structured_display_to_string(lr)
            string += lr
        return cut_spaces(string)
    else:
        log.warning("error in list_string_join: argument should be list or "
                    f"str, not {type(structured_display)}")
        return "**"


def cut_spaces(string: str) -> str:
    """
    Remove unnecessary spaces inside string
    """
    while string.find("  ") != -1:
        string = string.replace("  ", " ")
    return string
