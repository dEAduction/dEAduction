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
from dataclasses import     dataclass, field
from typing import          List, Any
import logging

import deaduction.pylib.logger as logger
if __name__ == "__main__":
    import deaduction.pylib.config.i18n

import deaduction.pylib.config.vars            as cvars
from deaduction.pylib.mathobj.display_math import (Shape,
                                        display_math_type_of_local_constant)

from deaduction.pylib.mathobj.display_data import (HAVE_BOUND_VARS,
                                                   INEQUALITIES)
import deaduction.pylib.mathobj.give_name      as give_name
from deaduction.pylib.mathobj.utils        import *

log = logging.getLogger(__name__)
NUMBER_SETS_LIST = ['ℕ', 'ℤ', 'ℚ', 'ℝ']


class MissingImplicitDefinition(Exception):
    def __init__(self, definition, math_object, rewritten_math_object):
        super().__init__(f"Implicit use of definition "
                         f"{definition.pretty_name} in "
                         f"{math_object.to_display()} -> "
                         f"{rewritten_math_object}")
        self.definition            = definition
        self.math_object           = math_object
        self.rewritten_math_object = rewritten_math_object


def allow_implicit_use(test: callable):
    """
    Modify the function test to allow implicit use of the definitions
    whose patterns are in MathObject.definition_patterns.
    'test' is typically 'is_and', 'is_or', 'is_forall', ...
    """

    # TODO: add call to cvars.config['allow_implicit_use_of_definitions']
    def test_implicit(math_object,
                      is_math_type=False,
                      implicit=False,
                      return_def=False):
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
            # implicit_definitions = MathObject.implicit_definitions
            definition_patterns = MathObject.definition_patterns
            for index in range(len(definition_patterns)):
                # Test right term if self match pattern
                pattern = definition_patterns[index]
                pattern_left = pattern.children[0]
                pattern_right = pattern.children[1]
                if pattern_left.match(math_type):
                    if test(pattern_right, is_math_type=True):
                        # implicit_definition = implicit_definitions[index]
                        # rewritten_math_object = pattern_right.apply_matching()
                        # raise MissingImplicitDefinition(implicit_definition,
                        #                                 math_object,
                        #                                 rewritten_math_object)
                        # if return_def:
                        #     return MathObject.implicit_definitions[index]
                        # else:
                        # Store data for further use
                        MathObject.last_used_implicit_definition = \
                                    MathObject.implicit_definitions[index]
                        MathObject.last_rw_object = \
                            pattern_right.apply_matching()
                        return True
            return False

    return test_implicit


#############################################
# MathObject: general mathematical entities #
#############################################
@dataclass
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
    math_type         : Any = field(repr=False)  # Necessary with @dataclass
    _math_type        : Any = field(init=False,
                                    repr=False,
                                    default=None)

    has_unnamed_bound_vars: bool = False  # True if bound vars to be named

    Variables = {}  # Containing every element having an identifier,
    # i.e. global and bound variables. This is used to avoid duplicate.
    # key = identifier,
    # value = MathObject
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
    last_used_implicit_definition = None
    last_rw_object                = None

    # Some robust methods to access information stored in attributes
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
    def display_name(self) -> str:
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

    def math_type_child_name(self, format_) -> str:
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
        if type(line_of_descent) == int:
            return self.children[line_of_descent]
        child_number, *remaining = line_of_descent
        child = self.children[child_number]
        if not remaining:
            return child
        else:
            return child.descendant(remaining)

    def has_name(self, name: str):
        return self.display_name == name

    @classmethod
    def clear(cls):
        """Re-initialise various class variables, in particular the
        Variables dict. It is crucial that this method is called when Lean
        server is stopped, because in the next session Lean could
        re-attributes an identifier that is in Variables, entailing chaos."""
        cls.Variables = {}
        cls.number_sets = []
        cls.bound_var_number = 0

    # Main creation method #
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
                math_object = MathObject(node=node,
                                         info=info,
                                         math_type=math_type,
                                         children=children
                                         )
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
            new_info = {'name': "NO NAME",
                        'lean_name': bound_var.info['name'],
                        'is_bound_var': True}
            bound_var.info.update(new_info)
            math_object = MathObject(node=node,
                                     info=info,
                                     math_type=math_type,
                                     children=children,
                                     has_unnamed_bound_vars=True)

        else:
            ##############################
            # End: generic instantiation #
            ##############################
            # Self has unnamed bound vars if some child has
            child_bool = (True in [child.has_unnamed_bound_vars
                                   for child in children])
            math_object = MathObject(node=node,
                                     info=info,
                                     math_type=math_type,
                                     children=children,
                                     has_unnamed_bound_vars=child_bool)
        # Detect sets of numbers and insert in number_sets if needed
        # at the right place so that the list stay ordered
        name = math_object.display_name
        cls.add_numbers_set(name)
        return math_object

    @classmethod
    def add_numbers_set(cls, name: str):
        """
        Insert name in cls.number_sets at the right place
        :param name: an element of NUMBER_SETS_LIST = ['ℕ', 'ℤ', 'ℚ', 'ℝ']
        """
        if name in NUMBER_SETS_LIST and name not in cls.number_sets:
            cls.number_sets.append(name)
            counter = len(MathObject.number_sets) -1
            while counter > 0:
                old_item = cls.number_sets[counter - 1]
                if NUMBER_SETS_LIST.index(name) < \
                   NUMBER_SETS_LIST.index(old_item):
                    # Swap
                    cls.number_sets[counter] = old_item
                    cls.number_sets[counter-1] = name
                    counter -= 1
                else:
                    break
            log.debug(f"Number_sets: {MathObject.number_sets}")

    ########################
    # Name bound variables #
    ########################
    def name_bound_vars(self, forbidden_vars=None):
        """
        Provide a good name for all bound variables of self
         e.g. when the node is a quantifier, "LAMBDA", "SET_EXTENSION".
         (cf the have_bound_vars list in display_data.py)

        (1) Assume all bound vars of self are unnamed (name = 'NO NAME')
        (2) Name bound var of main node, if any
        (3) Recursively call name_bound_vars on self.children

         This order gives the wanted result, e.g.
         ∀ x:X, ∀ x':X, etc. and not the converse
        """
        # NB: info["name"] is provided by structures.lean,
        # but may be inadequate (e.g. two distinct variables sharing the
        # same name).
        # The Lean name is just used as a hint to find a good name
        # but even this might turn out to be a bad idea

        # For an expression like ∀ x: X, P(x)
        # the constraints are:
        # (1) the name of the bound variable
        # (which is going to replace `x`)  must be distinct from all names
        # of variables appearing in the body `P(x)`, whether free or bound
        # (2) the name of the bound variable must be distinct from names
        # of bound variables appearing previously in the same MathObject

        # Bound vars inside P(x) must be unnamed, so that their names will not
        # be on the forbidden list

        if not self.has_unnamed_bound_vars:
            # Prevents for (badly) renaming vars several times
            # log.debug("no bound vars")
            return
        # log.debug(f"Naming bound vars in {self}")
        self.has_unnamed_bound_vars = False
        if not forbidden_vars:
            forbidden_vars = []
        node = self.node
        children = self.children
        if node in HAVE_BOUND_VARS:
            bound_var_type, bound_var, local_context = children
            hint = bound_var.info["lean_name"]
            # Search for a fresh name valid inside local context
            name = give_name.give_local_name(math_type=bound_var_type,
                                             hints=[hint],
                                             body=local_context,
                                             forbidden_vars=forbidden_vars)
            bound_var.info["name"] = name
            # Bound vars have no math_type indication
            # but we need one for further proper naming
            bound_var.math_type = bound_var_type
            # log.debug(f"giving name {name}")

            children = [local_context]
            # Prevent further bound vars in the expression to take the same
            # name
            forbidden_vars.append(bound_var)
        # Recursively name bound variables in local_context
        for child in children:
            child.name_bound_vars(forbidden_vars=forbidden_vars)

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
                    #log.debug(f"distinct names "
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
        bound_var_1.info['bound_var_number'] = MathObject.bound_var_number
        bound_var_2.info['bound_var_number'] = MathObject.bound_var_number

    @classmethod
    def unmark_bound_vars(cls, bound_var_1, bound_var_2):
        """
        Mark two bound variables with a common number, so that we can follow
        them along two quantified expressions and check tif these expressions
        are identical
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

    def is_inequality(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is an inequality.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node in INEQUALITIES

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

    def which_number_set(self, is_math_type=False) -> str:
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
    def to_display(self,
                   is_math_type=False,
                   format_="utf8",  # change to "latex" for latex...
                   text_depth=0
                   ) -> str:
        if is_math_type:
            #########################################
            # Naming bound variables before display #
            #########################################
            self.name_bound_vars(forbidden_vars=[])
            shape = display_math_type_of_local_constant(self,
                                                        format_,
                                                        text_depth)
        else:
            shape = Shape.from_math_object(self, format_, text_depth)
        return structured_display_to_string(shape.display)

    def find_implicit_definition(self, test=None):
        """
        Search if self matches some definition in
        MathObject.implicit_definitions matching test and if so,
        return the first matching definition.
        """
        definition_patterns = MathObject.definition_patterns
        for index in range(len(definition_patterns)):
            # Test right term if self match pattern
            pattern = definition_patterns[index]
            pattern_left = pattern.children[0]
            if pattern_left.match(self):
                if test is None or test(self):
                    return MathObject.implicit_definitions[index]

    def apply_implicit_definition(self):
        """
        Search if self matches some definition in
        MathObject.implicit_definitions and if so, return the MathObject
        obtained by applying the first matching definition.
        """
        # FIXME: unused?

        definition_patterns = MathObject.definition_patterns
        for index in range(len(definition_patterns)):
            # Test right term if self match pattern
            pattern = definition_patterns[index]
            pattern_left = pattern.children[0]
            if pattern_left.match(self):
                pattern_right = pattern.children[1]
                rewritten_math_object = pattern_right.apply_matching()
                return rewritten_math_object

    def implicit_children(self):
        """
        Search if self matches some definition in
        MathObject.implicit_definitions and if so, return the
        children of the MathObject obtained by applying the first matching
        definition.
        If no definition matches, then return the original children
        """
        # FIXME: unused?
        rewritten_math_object = self.apply_implicit_definition()
        if rewritten_math_object:
            return rewritten_math_object.children
        return self.children


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
