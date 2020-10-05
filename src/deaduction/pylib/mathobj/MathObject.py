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
from dataclasses import dataclass
from typing import Tuple, List, Any
import logging

import deaduction.pylib.logger as logger
from deaduction.pylib.mathobj.display_math import \
    display_math_object, display_math_type_of_local_constant

import deaduction.pylib.mathobj.give_name as give_name

log = logging.getLogger(__name__)


##########################################
# MathObject: general mathematical entities #
##########################################

@dataclass
class MathObject:
    """
    Python representation of mathematical entities,
    both objects (sets, elements, functions, ...)
    and properties ("a belongs to A", ...)
    """
    node:           str         # e.g. "LOCAL_CONSTANT", "FUNCTION", "QUANT_∀"
    info:           dict        # e.g. "name", "id", "pp_type"
    math_type:      Any         # Another MathObject
    children:       list        # list of MathObjects

    Variables = {}              # dictionary containing every element having
    # an identifier, i.e. global and bound variables.
    # key = identifier,
    # value = MathObject

    @classmethod
    def from_info_and_children(cls, info, children):
        """
        create an instance of MathObject from the lean data collected by
        the parser.
        :param info: dictionary with mandatory key   'node_name',
                                    optional keys 'math_type',
                                            'name'
                                            'identifier'
        :param children:
        :return:
        """
        node = info.pop("node_name")
        if 'math_type' in info.keys():
            math_type = info.pop('math_type')
        else:
            math_type = "not provided"
        #####################################################
        # Treatment of global variables: avoiding duplicate #
        #####################################################
        if 'identifier' in info.keys():
            identifier = info['identifier']
            if identifier in MathObject.Variables:    # object already exists
                #log.debug(f"already exists in dict "
                #          f"{[(key, MathObject.Variables[key]) for key in
                #          MathObject.Variables]}")
                math_object = MathObject.Variables[identifier]
            else:                                       # new object
                math_object = MathObject(node=node,
                                         info=info,
                                         math_type=math_type,
                                         children=children
                                         )
                MathObject.Variables[identifier] = math_object
        ##############################
        # Treatment of other objects #
        ##############################
        else:
            #############################################################
            # Quantifiers & lambdas: give a good name to bound variable #
            #############################################################
            # NB: lean_data["name"] is given by structures.lean,
            # but may be inadequate (e.g. two distinct variables sharing the
            # same name)
            # For an expression like ∀ x: X, P(x)
            # the logical constraints are: the name of the bound variable
            # (which is going to replace `x`)  must be distinct from all
            # names of variables appearing in the body `P(x)`, whether free
            # or bound
            if node.startswith("QUANT") or node == "LAMBDA":
                bound_var_type, bound_var, local_context = children
                # changing info["name"]
                # so that it will not be on the forbidden list
                hint = bound_var.info["name"]
                bound_var.info["lean_name"] = hint  # storing just in case
                bound_var.info["name"] = "processing name..."
                # search for a fresh name valid inside local context
                name = give_name.give_local_name(math_type=bound_var_type,
                                                 hints=[hint],
                                                 body=local_context)
                bound_var.info["name"] = name
                bound_var.math_type = bound_var_type
            ######################
            # end: instantiation #
            ######################
            math_object = MathObject(node=node,
                              info=info,
                              math_type=math_type,
                              children=children
                              )
        return math_object




    def __eq__(self, other):
        """
        test if the two prop_obj code for the same mathematical objects,
        by recursively testing nodes.
        This is used for instance to guarantee uniqueness of those AnonymousPO
        objects that appears as math_types

        Not that even for global variables we do NOT want to use identifiers,
        since they Lean change them every time the file is modified

        WARNING: this should probably not be used for bound variables

        :param self: AnonymousPO
        :param other: AnonymousPO
        :return: bool
        """
        # successively test for     nodes
        #                           name (if exists)
        #                           math_type
        #                           children
        if self.node != other.node:
            return False
        elif 'name' in self.info.keys():
            if self.info['name'] != other.info['name']:
                return False
        elif self.math_type != other.math_type:
            return False
        elif len(self.children) != len(other.children):
            return False
        else:
            for child0, child1 in zip(self.children, other.children):
                if not MathObject.__eq__(child0, child1):
                    return False
        return True

    def is_prop(self) -> bool:
        """
        Test if self represents a mathematical Proposition
        For global variables, only the math_type attribute should be tested !
        """
        math_type = self.math_type
        if hasattr(math_type, 'node'):
            return self.math_type.node == "PROP"
        else:
            return False

    def is_type(self) -> bool:
        """
        Test if self is a "universe"
        """
        if hasattr(self.math_type, "node"):
            return self.math_type.node == "TYPE"
        else:
            log.warning(f"is_type called on {self}, but math_type is "
                        f"{self.math_type}")
            return None

    ###############################
    # collect the local variables #
    ###############################
    def extract_local_vars(self) -> list:
        """
        recursively collect the list of variables used in the definition of
        self (leaves of the tree). Here by definition, being a variable
        means having an info["name"]
        :return: list of MathObject
        """
        # todo: change by testing if node == "LOCAL_CONSTANT" ?
        if "name" in self.info.keys():
            return [self]
        local_vars = []
        for child in self.children:
            local_vars.extend(child.extract_local_vars())
        return local_vars

    def extract_local_vars_names(self) -> List[str]:
        """
        collect the list of names of variables used in the definition of self
        (leaves of the tree)
        """
        L = [math_obj.info["name"] for math_obj in self.extract_local_vars()]
        return L

    ##########################################
    # Computation of display of math objects #
    ##########################################
    def format_as_latex(self, is_math_type=False):
        format_ = "latex"
        if is_math_type:
            display = display_math_type_of_local_constant(self, format_)
        else:
            display = display_math_object(self, format_="latex")
        return list_string_join(display)

    def format_as_utf8(self, is_math_type=False):
        format_ = "utf8"
        if is_math_type:
            display = display_math_type_of_local_constant(self, format_)
        else:
            display = display_math_object(self, format_="utf8")
        return list_string_join(display)


def list_string_join(structured_display) -> str:
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
            lr = list_string_join(lr)
            string += lr
        #    log.debug("string:", latex_str)
        return string
    else:
        log.warning("error in list_string_join: argument should be list or "
                    f"str, not {type(structured_display)}")
        return "**"


##########
# essais #
##########
if __name__ == '__main__':
    logger.configure()
