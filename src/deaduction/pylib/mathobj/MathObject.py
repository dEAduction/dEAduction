"""
#####################################################################
# MathObject.py : Take the result of Lean's tactic "Context_analysis", #
# and process it to extract the mathematical content.               #
#####################################################################
    
This files provides python classes for encoding mathematical objects
and propositions (PropObj, AnonymousPO, ProofStatePO, BoundVarPO)
and the following functions:
- create_anonymous_prop_obj and create_pspo instanciate objects respectively
in the classes AnonymousPO, ProofStatePO. The function create_pspo makes use of
analysis.LeanExprVisitor

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

from .display_math      import (display_math_type_of_local_constant,
                                Shape)
from .display_data      import (HAVE_BOUND_VARS,
                                INEQUALITIES)

import deaduction.pylib.mathobj.give_name as give_name


log = logging.getLogger(__name__)


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
    children          : list  # list of MathObjects
    math_type         : Any = field(repr=False)  # Another MathObject
    _math_type        : Any = field(init=False,
                                    repr=False,
                                    default=None)

    has_unnamed_bound_vars: bool = False  # True if bound vars to be named

    Variables = {}  # containing every element having an identifier,
    # i.e. global and bound variables. This avoids duplicate.
    # key = identifier,
    # value = MathObject
    bound_var_number = 0  # a counter to distinguish bound variables


    # Some robust methods to access information stored in attributes
    @property
    def math_type(self) -> Any:
        """
        This is a work-around to the impossibility of defining a class
        recursively. Thus every instance of a MathObject has a math_type
        which is a MathObject (and has a node, info dic, and children list)
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

    @property
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
        """display first child of math_type"""
        math_type = self.math_type
        if math_type.children:
            child = math_type.children[0]
            return child.display_name
        else:
            return '*no_name*'

    def descendant(self, line_of_descent):
        """Return the MathObject corresponding to the line_of_descent
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

    # Main creation method #
    @classmethod
    def from_info_and_children(cls, info: {}, children: []):
        """
        create an instance of MathObject from the lean data collected by
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
            identifier = info['identifier']
            if identifier in MathObject.Variables:  # object already exists
                # log.debug(f"already exists in dict "
                #          f"{[(key, MathObject.Variables[key]) for key in
                #          MathObject.Variables]}")
                math_object = MathObject.Variables[identifier]
            else:  # new object
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
            # end: general instantiation #
            ##############################
            # self has unnamed bound vars if some child has
            child_bool = (True in [child.has_unnamed_bound_vars
                                                    for child in children])
            math_object = MathObject(node=node,
                                     info=info,
                                     math_type=math_type,
                                     children=children,
                                     has_unnamed_bound_vars=child_bool)
        return math_object

    ########################
    # name bound variables #
    ########################
    def name_bound_vars(self):
        """
        Provide a good name for all bound variables of self

        (1) assume all bound vars of self are unnamed (name = 'NO NAME'),
        and have a lean_name (in attribute info)
        (2) name bound var of main node, if any
        (3) recursively call name_bound_vars on self.children

         This order gives the wanted result, e.g.
         ∀ x:X, ∀ x':X, etc. and not the converse

         e.g. when the node is a quantifier, "LAMBDA", "SET_EXTENSION".
         (cf the have_bound_vars list in display_data.py)

        """
        # NB: info["name"] is provided by structures.lean,
        # but may be inadequate (e.g. two distinct variables sharing the
        # same name)
        # For an expression like ∀ x: X, P(x)
        # the logical constraints are: the name of the bound variable
        # (which is going to replace `x`)  must be distinct from all
        # names of variables appearing in the body `P(x)`, whether free
        # or bound
        # bound vars must be unnamed, so that their names will not be on
        # the forbidden list
        if not self.has_unnamed_bound_vars:
            # prevents for (badly) renaming vars several times
            # log.debug("no bound vars")
            return
        self.has_unnamed_bound_vars = False
        node = self.node
        children = self.children
        if node in HAVE_BOUND_VARS:
            bound_var_type, bound_var, local_context = children
            hint = bound_var.info["lean_name"]
            # search for a fresh name valid inside local context
            name = give_name.give_local_name(math_type=bound_var_type,
                                             hints=[hint],
                                             body=local_context)
            bound_var.info["name"] = name
            bound_var.math_type = bound_var_type
            log.debug(f"giving name {name}")

            children = [local_context]

        # recursively name bound variables
        for child in children:
            child.name_bound_vars()

######################################
# Tests for equality related methods #
######################################

    def __eq__(self, other) -> bool:
        """
        test if the two prop_obj code for the same mathematical objects,
        by recursively testing nodes.
        This is used for instance to guarantee uniqueness of those AnonymousPO
        objects that appears as math_types

        Note that even for global variables we do NOT want to use identifiers,
        since Lean change them every time the file is modified

        WARNING: this should probably not be used for bound variables
        """

        # Successively test for
        #                           nodes
        #                           name (if exists)
        #                           math_type
        #                           children

        equal = True    # Self and other are presumed to be equal
        marked = False  # Will be True if bound variables should be unmarked

        node = self.node
        # Case of NO_MATH_TYPE
        if self is NO_MATH_TYPE \
                and other is NO_MATH_TYPE:
            return True  # avoid infinite recursion!

        # Node
        elif node != other.node:
            log.debug(f"distinct nodes {self.node, other.node}")
            return False

        # Mark bound vars in quantified expressions to distinguish them
        elif node in HAVE_BOUND_VARS:
            # Here self and other are assumed to be a quantified proposition
            # and children[1] is the bound variable.
            # We mark the bound variables in self and other
            bound_var_1 = self.children[1]
            bound_var_2 = other.children[1]
            mark_bound_vars(bound_var_1, bound_var_2)
            marked = True

        # Names
        if 'name' in self.info.keys():
            # for bound variables, do not use names, use numbers
            if self.is_bound_var():
                if not other.is_bound_var():
                    equal = False
                # here both are bound variables
                elif 'bound_var_number' not in self.info:
                    if 'bound_var_number' in other.info:
                        equal = False
                    else:
                        # unmarked bound vars: we are comparing two parts of
                        # a given quantified expression, names have a meaning
                        equal = (self.info['name'] == other.info['name'])
                # From now on self.info['bound_var_number'] exists
                elif 'bound_var_number' not in other.info:
                    equal = False
                # From now on both variables have a number
                elif self.info['bound_var_number'] != \
                        other.info['bound_var_number']:
                    equal = False
            else:  # self is not bound var
                if other.is_bound_var():
                    equal = False
                elif self.info['name'] != other.info['name']:
                    log.debug(f"distinct names "
                              f"{self.info['name'], other.info['name']}")
                    equal = False
        # Recursively test for math_types
        elif self.math_type != other.math_type:
            log.debug(f"distinct types {self.math_type}")
            log.debug(f"other type     {other.math_type}")
            equal = False

        # Recursively test for children
        elif len(self.children) != len(other.children):
            equal = False
        else:  # recursively test for children
            for child0, child1 in zip(self.children, other.children):
                if child0 != child1:
                    equal = False

        # Unmark bound_vars, in prevision of future tests
        if marked:
            unmark_bound_vars(bound_var_1, bound_var_2)

        return equal

    def contains(self, other):
        """
        Compute the number of copies of other contained in self
        """
        if MathObject.__eq__(self, other):
            counter = 1
        else:
            counter = 0
            for math_object in self.children:
                counter += math_object.contains(other)
        return counter

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
        For global variables, only the math_type attribute should be tested !
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "PROP"

    def is_type(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) is a "universe"
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "TYPE"

    def is_nat(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) is a "universe"
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "CONSTANT" and math_type.info['name'] == "ℕ"

    def is_function(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is function.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "FUNCTION"

    def is_and(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is an implication.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "PROP_AND"

    def is_implication(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is an implication.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "PROP_IMPLIES"

    def is_exists(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is an implication.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node in ("QUANT_∃", "QUANT_∃!")

    def is_for_all(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is function.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "QUANT_∀"

    def is_quantifier(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is function.
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return (math_type.is_exists(is_math_type=True)
                or math_type.is_for_all(is_math_type=True))

    def is_equality(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is an equality
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node == "PROP_EQUAL"

    def is_inequality(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is an equality
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        return math_type.node in INEQUALITIES

    def is_iff(self, is_math_type=False) -> bool:
        """
        Test if (math_type of) self is 'PROP_IFF'
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type

        return math_type.node == "PROP_IFF"

    def is_false(self, is_math_type=False) -> bool:
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

    # Determine some important classes of MathObjects
    def can_be_used_for_substitution(self, is_math_type=False) -> bool:
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
        """
        if is_math_type:
            math_type = self
        else:
            math_type = self.math_type
        if math_type.is_equality(is_math_type=True) \
                or math_type.is_iff(is_math_type=True):
            return True
        elif math_type.is_for_all(is_math_type=True):
            # NB : ∀ var : type, body
            body = math_type.children[2]
            # recursive call
            return body.can_be_used_for_substitution(is_math_type=True)
        else:
            return False

    def can_be_used_for_implication(self, is_math_type=False) -> bool:
        """
        Determines if a proposition can be used as a basis for substituting,
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
            # recursive call
            return body.can_be_used_for_implication(is_math_type=True)
        else:
            return False

    ###############################
    # collect the local variables #
    ###############################
    def extract_local_vars(self) -> list:
        """
        recursively collect the list of variables used in the definition of
        self (leaves of the tree). Here by definition, being a variable
        means having an info["name"]
        :return: list of MathObject instances
        """
        # todo: change by testing if node == "LOCAL_CONSTANT" ?
        if "name" in self.info.keys():
            return [self]
        local_vars = []
        for child in self.children:
            local_vars.extend(child.extract_local_vars())
        return local_vars

    def extract_local_vars_names(self) -> List[str]:  # deprecated
        """
        collect the list of names of variables used in the definition of self
        (leaves of the tree)
        """
        l = [math_obj.info["name"] for math_obj in self.extract_local_vars()]
        return l

    ########################
    # display math objects #
    ########################
    def to_display(self,
                   is_math_type=False,
                   format_="utf8",  # change to "latex" for latex...
                   text_depth=0
                   ):
        if is_math_type:
            #########################################
            # naming bound variables before display #
            #########################################
            self.name_bound_vars()
            shape = display_math_type_of_local_constant(self,
                                                        format_,
                                                        text_depth)
        else:
            shape = Shape.from_math_object(self, format_, text_depth)
        return structured_display_to_string(shape.display)


NO_MATH_TYPE = MathObject(node="not provided",
                          info={},
                          children=[],
                          math_type=None)


#########
# Utils #
#########
def mark_bound_vars(bound_var_1, bound_var_2):
    """
    Mark two bound variables with a common number, so that we can follow
    them along two quantified expressions and check tif these expressions
    are identical
    """
    MathObject.bound_var_number += 1
    bound_var_1.info['bound_var_number'] = MathObject.bound_var_number
    bound_var_2.info['bound_var_number'] = MathObject.bound_var_number


def unmark_bound_vars(bound_var_1, bound_var_2):
    """
    Mark two bound variables with a common number, so that we can follow
    them along two quantified expressions and check tif these expressions
    are identical
    """
    bound_var_1.info.pop('bound_var_number')
    bound_var_2.info.pop('bound_var_number')


def structured_display_to_string(structured_display) -> str:
    """
    turn a (structured) latex or utf-8 display into a latex string

    :param structured_display: type is recursively defined as str or list of
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


##########
# essais #
##########
if __name__ == '__main__':
    logger.configure()
