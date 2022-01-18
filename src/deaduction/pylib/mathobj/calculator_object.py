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

import logging

from typing import Dict

from deaduction.pylib.mathobj import (MathObject, PatternMathObject,
                                      HAVE_BOUND_VARS)
from enum import IntEnum

log = logging.getLogger(__name__)
global _

PMO = PatternMathObject
NO_MATH_TYPE = PMO.NO_MATH_TYPE
PROP = PMO.PROP()
TYPE = PMO.TYPE()
PROP.math_type = NO_MATH_TYPE
TYPE.math_type = NO_MATH_TYPE


class NodeType(IntEnum):
    """
    A class for clarifying node type.
    """
    logic = 0
    set_theory = 1
    local_constant = 10
    metavar = 11


class CalculatorSubObject(PatternMathObject):
    """
    A class for storing MathObjects to be used in the calculator. In
    particular, the use of a new class permits to duplicate MathObjects, e.g.
    local constants, that may appear at different places of some object.

    Children should always be instances of CalculatorSubObject, except for
    metavars that may have MathObjects local constants as their only child.
    Metavars are designed to be later assigned to some other
    CalculatorSubObject, or to a local constant; in that case the object is
    set as their child.
    """
    # TODO: class method for automatically creating instances from MathObjects
    #  (one instance for each node type?)

    metavars_dict: Dict[int, PMO] = None

    def __init__(self, node, info=None, children: [PatternMathObject]=None,
                 bound_vars=None, math_type=None,
                 parent=None, node_type=None):
        super().__init__(node=node,
                         info=info,
                         children=children,
                         bound_vars=bound_vars,
                         math_type=math_type)
        
        self.parent: CalculatorSubObject = parent
        self.node_type = node_type  # FIXME: suppress?
        for child in children:
            if isinstance(child, CalculatorSubObject):
                child.parent = self

    @property
    def child_nb(self):
        parent = self.parent
        if parent:
            return parent.children.index(self)

    @property
    def next_brother(self):
        child_nb = self.child_nb
        if child_nb:
            parent = self.parent
            if child_nb + 1 < len(parent.children):
                return parent.children[child_nb+1]

    def set_child(self, child, child_nb=None):
        """
        Insert child into self.children at child_nb if provided, or append
        it.
        """
        if child_nb:
            self.children[child_nb] = child
        else:
            self.children.append(child)
        if isinstance(child, CalculatorSubObject):
            child.parent = self

    def first_unassigned_metavar(self):
        """
        Return the first unassigned (i.e. with no child) metavar in the tree of
        self, ia any, including self.
        """
        if self.is_metavar() and not self.children:
            return self
        else:
            for child in self.children:
                if isinstance(child, CalculatorSubObject):
                    metavar = child.first_unassigned_metavar()
                    if metavar:
                        return metavar

    def next_unassigned_metavar(self, nb=0, cycle=True):
        """
        Return next metavar after self, not including self,
        starting at self.children[nb]. If cycle=True then start from
        beginning if no metavar is found after self. If self has no
        unassigned metavar then return None.
        """

        metavar = None
        # (1) Search in the children's trees from child n° nb
        for child in self.children[nb:]:
            if isinstance(child, CalculatorSubObject):
                metavar = child.first_unassigned_metavar()
                if metavar:
                    return metavar

        # (2) No metavars in subtree, go to parent
        parent = self.parent
        if parent:
            metavar = parent.next_unassigned_metavar(nb=self.child_nb+1,
                                                     cycle=cycle)

        if metavar:
            return metavar
        elif cycle:
            return self.first_unassigned_metavar()

    def previous_unassigned_metavar(self):
        """
        Return previous metavar.
        """
        # TODO

    def match(self, other: MathObject) -> bool:
        """
        Test if math_object match self. This is a recursive test.
        The list PatternMathObject.metavars contains the metavars that have
        already been matched against a math_object, which is stored with the
        same index in the list PatternMathObject.metavar_objects.
        e.g. 'g∘f is injective' matches 'metavar_28 is injective'
        (note that math_types of metavars should also match).
        """

        CSO.metavars_dict = {}
        match = self.recursive_match(other)
        # log.debug(f"Matching...")
        # list_ = [(PatternMathObject.metavars[idx].to_display(),
        #           PatternMathObject.metavar_objects[idx].to_display())
        #          for idx in range(len(PatternMathObject.metavars))]
        # log.debug(f"    Metavars, objects: {list_}")

        return match

    def recursive_match(self, other: MathObject, assign=False) -> bool:
        """
        Test if other match self. This methods overclass the
        PatternMathObject.recursive_match method.
        This is a recursive test.
        CSO.metavars_dict is a dictionary whose keys are metavars nb that
        have been matched, and values are the corresponding PatternMathObject.
        """

        if other is self:
            return True

        assert isinstance(other, CSO)

        metavars = self.metavars_dict
        match = True    # Self and math_object are presumed to match
        marked = False  # Will be True if bound variables should be unmarked

        node = self.node
        # Case of NO_MATH_TYPE (avoid infinite recursion!)
        if self is NO_MATH_TYPE:
            return True

        # METAVAR: this is where the method differs from PMO.recursive_match.
        elif self.is_metavar():
            if len(self.children) == 1:
                corresponding_object = self.children[0]
                match = corresponding_object.recursive_match(other)
            # If self has already been identified, other matches self
            #   iff it matches the corresponding item in metavars_dict
            # If not, then self matches with other providing their
            #   math_types match. In this case, identify metavar.
            elif self.nb in metavars:
                corresponding_object = metavars[self.nb]
                match = corresponding_object.recursive_match(other)
            else:
                self_type = self.math_type
                other_type = other.math_type
                match = self_type.recursive_match(other_type)
                if match:
                    metavars[self.nb] = other
            return match
        elif other.is_metavar():
            if other.nb in metavars:
                corresponding_object = metavars[other.nb]
                match = self.recursive_match(corresponding_object)
            else:
                self_type = self.math_type
                other_type = other.math_type
                match = self_type.recursive_match(other_type)
                if match:
                    metavars[other.nb] = self
            return match
        # Node
        elif node != other.node:
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
            bound_var_2 = other.children[1]
            self.mark_bound_vars(bound_var_1, bound_var_2)
            marked = True

        # Names
        if 'name' in self.info.keys():
            # For bound variables, do not use names, use numbers
            if self.is_bound_var():
                if not other.is_bound_var():
                    match = False
                # Here both are bound variables
                elif 'bound_var_number' not in self.info:
                    if 'bound_var_number' in other.info:
                        # Already appeared in math_object but not in self
                        match = False
                    else:
                        # Here both variable are unmarked. This means
                        # we are comparing two subexpressions with respect
                        # to which the variables are not local:
                        # names have a meaning
                        match = (self.info['name'] == other.info['name'])
                # From now on self.info['bound_var_number'] exists
                elif 'bound_var_number' not in other.info:
                    match = False
                # From now on both variables have a number
                elif (self.info['bound_var_number'] !=
                      other.info['bound_var_number']):
                    match = False
            else:  # Self is not bound var
                if other.is_bound_var():
                    match = False
                elif self.info['name'] != other.info['name']:
                    # None is a bound var
                    match = False
                    # log.debug(f"distinct names "
                    #        f"{self.info['name'], math_object.info['name']}")

        # Recursively test for math_types
        #  (added: also when names)
        if not self.math_type.recursive_match(other.math_type):
            # log.debug(f"distinct types {self.math_type}")
            # log.debug(f"math_object type     "
            #           f"{math_object.math_type.to_display()}")
            match = False

        # Recursively test matching for children
        elif len(self.children) != len(other.children):
            match = False
        else:
            for child0, child1 in zip(self.children, other.children):
                if not child0.recursive_match(child1):
                    match = False

        # Unmark bound_vars, in prevision of future tests
        if marked:
            self.unmark_bound_vars(bound_var_1, bound_var_2)

        return match

    def apply_matching(self):
        """
        After two CSO are successfully matched, apply the matching to
        propagate the matching to all metavars inside self whose number is a
        key in CSO.metavars_dict.
        """

        metavar = self.next_unassigned_metavar(cycle=False)
        if not metavar:
            return None
        nb = metavar.nb
        if nb in CSO.metavars_dict:
            if not metavar.children:
                metavar.set_child()
        # FIXME


    #########
    # LOGIC #
    #########

    @classmethod
    def EQUALS(cls):
        X = CSO.new_metavar(math_type=NO_MATH_TYPE)
        L = CSO.new_metavar(math_type=X)
        R = CSO.new_metavar(math_type=X)
        return cls(node="PROP_EQUAL",
                   children=[L, R],
                   math_type=PROP,
                   node_type=NodeType.logic)

    @classmethod
    def AND(cls):
        P = CSO.new_metavar(math_type=PROP)
        Q = CSO.new_metavar(math_type=PROP)
        return cls(node="PROP_AND",
                   children=[P, Q],
                   math_type=PROP,
                   node_type=NodeType.logic)

    @classmethod
    def OR(cls):
        P = CSO.new_metavar(math_type=PROP)
        Q = CSO.new_metavar(math_type=PROP)
        return cls(node="PROP_OR",
                   children=[P, Q],
                   math_type=PROP,
                   node_type=NodeType.logic)

    @classmethod
    def NOT(cls):
        P = CSO.new_metavar(math_type=PROP)
        return cls(node="PROP_NOT",
                   children=[P],
                   math_type=PROP,
                   node_type=NodeType.logic)

    @classmethod
    def IFF(cls):
        P = CSO.new_metavar(math_type=PROP)
        Q = CSO.new_metavar(math_type=PROP)
        return cls(node="PROP_IFF",
                   children=[P, Q],
                   math_type=PROP,
                   node_type=NodeType.logic)

    @classmethod
    def IMPLIES(cls):
        P = CSO.new_metavar(math_type=PROP)
        Q = CSO.new_metavar(math_type=PROP)
        return cls(node="PROP_IMPLIES",
                   children=[P, Q],
                   math_type=PROP,
                   node_type=NodeType.logic)

    @classmethod
    def FORALL(cls):
        X = CSO.new_metavar(math_type=NO_MATH_TYPE)
        x = CSO.new_metavar(math_type=X)
        P = CSO.new_metavar(math_type=PROP)
        return cls(node="QUANT_∀",
                   children=[X, x, P],
                   math_type=PROP,
                   node_type=NodeType.logic)

    ##############
    # SET THEORY #
    ##############

    @classmethod
    def INCLUDED(cls):
        X = CSO.new_metavar(math_type=NO_MATH_TYPE)
        set_X = cls(node="SET", children=[X], math_type=NO_MATH_TYPE)
        A = CSO.new_metavar(math_type=set_X)
        B = CSO.new_metavar(math_type=set_X)
        return cls(node="PROP_INCLUDED",
                   children=[A, B],
                   math_type=PROP,
                   node_type=NodeType.set_theory)

    @classmethod
    def BELONGS(cls):
        X = CSO.new_metavar(math_type=NO_MATH_TYPE)
        set_X = cls(node="SET", children=[X], math_type=NO_MATH_TYPE)
        A = CSO.new_metavar(math_type=set_X)
        x = CSO.new_metavar(math_type=X)
        return cls(node="PROP_BELONGS",
                   children=[x, A],
                   math_type=PROP,
                   node_type=NodeType.set_theory)

    @classmethod
    def INTER(cls):
        X = CSO.new_metavar(math_type=NO_MATH_TYPE)
        set_X = cls(node="SET", children=[X], math_type=NO_MATH_TYPE)
        A = CSO.new_metavar(math_type=set_X)
        B = CSO.new_metavar(math_type=set_X)
        return cls(node="SET_INTER",
                   children=[A, B],
                   math_type=set_X,
                   node_type=NodeType.set_theory)

    @classmethod
    def UNION(cls):
        X = CSO.new_metavar(math_type=NO_MATH_TYPE)
        set_X = cls(node="SET", children=[X], math_type=NO_MATH_TYPE)
        A = CSO.new_metavar(math_type=set_X)
        B = CSO.new_metavar(math_type=set_X)
        return cls(node="SET_UNION",
                   children=[A, B],
                   math_type=set_X,
                   node_type=NodeType.set_theory)

    @classmethod
    def SINGLETON(cls):
        X = CSO.new_metavar(math_type=NO_MATH_TYPE)
        set_X = cls(node="SET", children=[X], math_type=NO_MATH_TYPE)
        x = CSO.new_metavar(math_type=X)
        return cls(node="SET_EXTENSION1",
                   children=[x],
                   math_type=set_X,
                   node_type=NodeType.set_theory)

    @classmethod
    def PAIRE(cls):
        X = CSO.new_metavar(math_type=NO_MATH_TYPE)
        set_X = cls(node="SET", children=[X], math_type=NO_MATH_TYPE)
        x = CSO.new_metavar(math_type=X)
        y = CSO.new_metavar(math_type=X)
        return cls(node="SET_EXTENSION2",
                   children=[x, y],
                   math_type=set_X,
                   node_type=NodeType.set_theory)


CSO = CalculatorSubObject


class CalculatorObject(CalculatorSubObject):
    """
    A class for storing a MathObject under construction in the calculator.
    This is a subclass of PMO with an attribute to store the selected node.

    """

    def __init__(self, math_object: CSO = None, selected_metavar=None):
        """
        Create a CalculatorPMO from a MathObject. If no object is provided,
        then create an "empty" object, with just a root node and one
        metavar as a child. The main node is always "ROOT".
        
        All nodes should be PMO, except local constants which are MathObjects.
        The ROOT node may have several metavar children while the object is 
        being built, but they are supposed to be later assmbled into a 
        single object. Each metavar has exactly one child when assigned, 
        and none if non ussigned.
        """
        if not math_object:
            math_object = CalculatorSubObject.new_metavar(NO_MATH_TYPE)

        super().__init__(node="ROOT", children=[math_object])
        if not selected_metavar:
            selected_metavar = self.first_unassigned_metavar()
        self.selected_metavar = selected_metavar
        self.well_formed = True

    def log_status(self):
        log.debug(f"Calculator: {self.to_display(format_='utf8')}")
        log.debug(f"Selected_metavar: "
                  f"{self.selected_metavar.to_display(format_='utf8')}")
        log.debug(f"Well formed: {self.well_formed}")

    def update_selected_metavar(self):
        """
        If selected_metavar is assigned, change to next unassigned metavar,
        starting again from beginning if needed. If all metavar are assigned
        then select first whole object.
        """
        
        self.move_next_metavar()
        if not self.selected_metavar:  # Selected last whole object
            self.selected_metavar = self.children[-1]

    def erase_child(self, child_nb=None):
        """
        Erase children of self.selected_metavar.
        """
        if child_nb is not None:
            self.selected_metavar.children.pop(child_nb)
        else:
            self.selected_metavar.children = []

    def assign(self, math_object: MathObject):
        """
        Assign math_object to selected_metavar, and update self.well_formed
        flag.
        """

        selected_metavar = self.selected_metavar
        match = selected_metavar.match(math_object)
        selected_metavar.set_child(math_object)
        self.well_formed = (self.well_formed and match
                            and len(selected_metavar.children) == 1)

    def integrate(self, math_object: MathObject):
        """
        Try to integrate math_object with self at the selected_metavar level.
        If selected_metavar is unassigned, then assign math_object to
        selected_metavar.
        In the opposite case, try to match selected_metavar's children with
        metavars of math_object.
        If this does not work either, then add math_object to
        selected_metavar's children.

        Then move metavar to next unassigned.
        """
        selected_metavar = self.selected_metavar
        if not selected_metavar.children:
            self.assign(math_object)
        else:
            if isinstance(math_object, CalculatorSubObject):
                # Try to integrate selected_metavar.children into math_object
                #  by assigning each metavar of math_object to a child
                metavar = math_object.first_unassigned_metavar()
                child_nb = 0
                used_children = []
                while metavar and child_nb < len(selected_metavar.children):
                    child = selected_metavar.children[child_nb]
                    match = metavar.match(child)
                    if match:  # Assign metavar to child
                        metavar.set_child(child)
                        used_children.append(child_nb)
                        # self.erase_child(child_nb)
                        child_nb += 1
                    metavar = metavar.next_unassigned_metavar(cycle=False)
                # Finally remove children incorporated into math_object
                used_children.reverse()
                for child_nb in used_children:
                    self.erase_child(child_nb)
            # If math_object has not been assigned to selected_metavar,
            # then add it to selected_metavar.children
            selected_metavar.set_child(math_object)

        self.update_selected_metavar()
        self.log_status()

    def to_display(self, format_="html", text_depth=0):
        if len(self.children) == 1:
            display = self.children[0].to_display(format_, text_depth)
        else:
            display = []
            for child in self.children:
                display.append(child.to_display(format_, text_depth))
        return display

    def move_next_metavar(self, cycle=True):
        """
        Move selected_metavar to next metavar.
        """
        self.selected_metavar = self.selected_metavar.next_unassigned_metavar()
        if (not self.selected_metavar) and cycle:
            self.selected_metavar = self.first_unassigned_metavar()

    def move_previous_metavar(self):
        """
        Move selected_metavar to previous metavar.
        """
        # TODO

    def move_up(self):
        pass

    def move_down(self):
        pass

    def move_right(self):
        pass

    def move_left(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass


if __name__ == "__main__":
    import deaduction.pylib.config.i18n
    from deaduction.pylib import logger
    logger.configure()

    # A inclus dans dans A inter B
    inclus = CSO.INCLUDED()
    inter = CSO.INTER()
    inter2 = CSO.INTER()
    union = CSO.UNION()
    iff = CSO.IFF()
    equals = CSO.EQUALS()

    X = MathObject(node="LOCAL_CONSTANT", info={"name": "X"}, math_type=TYPE)
    set_X = MathObject(node="SET", children=[X], math_type=NO_MATH_TYPE)
    A = MathObject(node="LOCAL_CONSTANT", math_type=set_X, info={"name": "A"})
    B = MathObject(node="LOCAL_CONSTANT", math_type=set_X, info={"name": "B"})
    C = MathObject(node="LOCAL_CONSTANT", math_type=set_X, info={"name": "C"})
    calculator = CalculatorObject()
    calculator.integrate(A)
    calculator.integrate(B)
    calculator.integrate(inclus)
    calculator.integrate(inter)
    calculator.integrate(C)
    calculator.integrate(C)
    calculator.integrate(equals)
    calculator.integrate(iff)


