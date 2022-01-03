"""
# patterns.py : <#ShortDescription> #
    
    <#optionalLongDescription>

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 01 2022 (creation)
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

from .pattern_math_objects import MathObject, PatternMathObject
from enum import IntEnum

NO_MATH_TYPE = PatternMathObject.NO_MATH_TYPE
PROP = MathObject.PROP

class NodeType(IntEnum):
    """
    A class for clarifying node type.
    """
    logic = 0
    set_theory = 1


class PMO(PatternMathObject):
    """
    A class for defining a list of PatternMathObjects to be used in the
    calculator.
    """
    node_type: NodeType

    def __init__(self, node, info=None, children=None,
                 bound_vars=None, math_type=None, node_type=0):
        super().__init__(node=node,
                         info=info,
                         children=children,
                         bound_vars=bound_vars,
                         math_type=math_type)
    #########
    # LOGIC #
    #########

    @classmethod
    def AND(cls):
        P = cls.new_metavar(math_type=PROP)
        Q = cls.new_metavar(math_type=PROP)
        return cls(node="PROP_AND",
                   children=[P, Q],
                   math_type=PROP)

    @classmethod
    def OR(cls):
        P = cls.new_metavar(math_type=PROP)
        Q = cls.new_metavar(math_type=PROP)
        return cls(node="PROP_OR",
                   children=[P, Q],
                   math_type=PROP)

    @classmethod
    def NOT(cls):
        P = cls.new_metavar(math_type=PROP)
        return cls(node="PROP_NOT",
                   children=[P],
                   math_type=PROP)

    @classmethod
    def IFF(cls):
        P = cls.new_metavar(math_type=PROP)
        Q = cls.new_metavar(math_type=PROP)
        return cls(node="PROP_IFF",
                   children=[P, Q],
                   math_type=PROP)

    @classmethod
    def IMPLIES(cls):
        P = cls.new_metavar(math_type=PROP)
        Q = cls.new_metavar(math_type=PROP)
        return cls(node="PROP_IMPLIES",
                   children=[P, Q],
                   math_type=PROP)

    @classmethod
    def FORALL(cls):
        X = cls.new_metavar(math_type=NO_MATH_TYPE)
        x = cls.new_metavar(math_type=X)
        P = cls.new_metavar(math_type=PROP)
        return cls(node="QUANT_∀",
                   children=[X, x, P],
                   math_type=PROP)

    ##############
    # SET THEORY #
    ##############

    @classmethod
    def INCLUDED(cls):
        X = cls.new_metavar(math_type=NO_MATH_TYPE)
        set_X = cls(node="SET", children=[X], math_type=NO_MATH_TYPE)
        A = cls.new_metavar(math_type=set_X)
        B = cls.new_metavar(math_type=set_X)
        return cls(node="PROP_INCLUDED",
                   children=[A, B],
                   math_type=PROP)

    @classmethod
    def BELONGS(cls):
        X = cls.new_metavar(math_type=NO_MATH_TYPE)
        set_X = cls(node="SET", children=[X], math_type=NO_MATH_TYPE)
        A = cls.new_metavar(math_type=set_X)
        x = cls.new_metavar(math_type=X)
        return cls(node="PROP_BELONGS",
                   children=[x, A],
                   math_type=PROP)

    @classmethod
    def INTER(cls):
        X = cls.new_metavar(math_type=NO_MATH_TYPE)
        set_X = cls(node="SET", children=[X], math_type=NO_MATH_TYPE)
        A = cls.new_metavar(math_type=set_X)
        B = cls.new_metavar(math_type=set_X)
        return cls(node="SET_INTER",
                   children=[A, B],
                   math_type=set_X)

    @classmethod
    def UNION(cls):
        X = cls.new_metavar(math_type=NO_MATH_TYPE)
        set_X = cls(node="SET", children=[X], math_type=NO_MATH_TYPE)
        A = cls.new_metavar(math_type=set_X)
        B = cls.new_metavar(math_type=set_X)
        return cls(node="SET_UNION",
                   children=[A, B],
                   math_type=set_X)


class CalculatorPMO(PMO):
    """
    A class for storing a MathObject under construction in the calculator.
    This is a subclass of PMO with an attribute to store the selected node.
    """

    def __init__(self, selected_node):
        super().__init__(self)
        self.selected_node = selected_node

    @classmethod
    def empty_object(cls):
        return cls.new_metavar(NO_MATH_TYPE)

    def assign(self, math_object: MathObject):
        """
        Assign math_object to selected_node, and change selected_node to first
        metavar in object if any, or next metavar if none.
        """

    def move_next_node(self):
        """
        Move selected_node to next node in the object tree.
        """

    def move_next_metavar(self):
        """
        Move selected_node to next metavar.
        """

    def move_previous_node(self):
        """
        Move selected_node to previous node.
        """

    def move_previous_metavar(self):
        """
        Move selected_node to previous metavar.
        """

