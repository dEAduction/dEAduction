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
import deaduction.pylib.mathobj.latex_format_data as latex_format_data
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

    Global_variables = {}

    @classmethod
    def from_info_and_children(cls, info, children):
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
            if identifier in MathObject.Global_variables:    # object already
                # exists
                log.debug("already exists")
                math_object = MathObject.Global_variables[identifier]
            else:                                       # new object
                math_object = MathObject(node=node,
                                  info=info,
                                  math_type=math_type,
                                  children=children
                                  )
                MathObject.Global_variables[identifier] = math_object
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

        :param self: AnonymousPO
        :param other: AnonymousPO
        :return: bool
        """
        # fixme: just test for node, name, math_type and children
        # first test for class, and then for lean names
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        # then if AnonymousPO, test for nodes
        elif self.__class__.__name__ == "AnonymousPO":
            if self.node != other.node:
                return False
        # if global var, test for names and types
        elif self.__class__.__name__  == 'ProofStatePO':
            if self.lean_data['name'] != other.lean_data['name'] \
                    or self.math_type != other.math_type:
                return False
        # if bound var, just test for types
        elif self.__class__.__name__  == 'BoundVarPO':
            if self.math_type != other.math_type:
                return False

        # now test equality of children
        elif len(self.children) != len(other.children):
            return False
        else:
            for index in range(len(self.children)):
                if not MathObject.__eq__(self.children[index],
                                      other.children[index]):
                    return False
        return True

    def is_prop(self) -> bool:
        """
        Test if self represents a mathematical Proposition
        For global variables, only the math_type attribute should be tested !
        """
        return self.math_type.node == "PROP"

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

    ######################################################
    # Computation of latex and utf-8 display for PropObj #
    ######################################################
    def structured_format(self, format_="latex", is_type_of_pfpo=False):
        """
        Recursively compute a structured latex or utf-8 "representation" of a
        prop_obj.
        Representations are structured into trees represented by lists,
        they can be turned into usual strings by using the list_string_join
        function below.
        Valid representations are recursively defined as:
        - lists of strings (in latex or utf-8 format)
        - lists of representations
        :param format_: "latex" or "utf8"
        :param is_type_of_pfpo: True if the object to display is the
        math_type of a ProofStatePO instance, e.g. "x: an element of X"
        (as opposed to the type theory version "x:X").
        :return:
        """
        # todo: remove the use of "representation" attribute
        if format_ == "latex":
            pass
            log.info(f"computing latex representation of {self}")
        else:
            log.info(f"computing utf-8 representation of {self}")
            format_ = "utf8"
        #######################################################################
        # compute representation of children, and put parentheses when needed #
        #######################################################################
        children_rep = []
        node = self.node
        i = -1
        for arg in self.children:
            i += 1
            MathObject.structured_format(arg, format_)
            rep = arg.representation[format_]
            # the following line computes if parentheses are needed
            # around child n° i
            parentheses = needs_paren(self, i)
            if parentheses:
                rep = ["(", rep, ")"]
            children_rep.append(rep)
        ##############################################################
        # compute representation by calling the appropriate function #
        # according to node as indicated in latex_structures         #
        ##############################################################
        if node not in latex_format_data.latex_structures.keys():
            # node not implemented
            log.warning(f"display of {node} not implemented")
            self.representation['latex'] = '****'
            self.representation['utf8'] = '****'
            return
        elif format_ == "latex":
            symbol, format_scheme = \
                latex_format_data.latex_structures[node]
            self.representation["latex"] = \
                format_scheme(symbol=symbol,
                              children_rep=children_rep,
                              po=self,
                              is_type_of_pfpo=is_type_of_pfpo,
                              format_="latex")
        else:
            symbol, format_scheme = \
                latex_format_data.utf8_structures[node]
            self.representation["utf8"] = \
                format_scheme(symbol=symbol,
                              children_rep=children_rep,
                              po=self,
                              is_type_of_pfpo=is_type_of_pfpo,
                              format_="utf8")
            log.debug(f"---> utf8 rep: {self.representation['utf8']}")
        return

    def format_as_latex(self, is_type_of_pfpo=False):
        MathObject.structured_format(self, "latex", is_type_of_pfpo)
        structured_rep = self.representation["latex"]
        return list_string_join(structured_rep)

    def format_as_utf8(self, is_type_of_pfpo=False):
        MathObject.structured_format(self, "utf8", is_type_of_pfpo)
        structured_rep = self.representation["utf8"]
        return list_string_join(structured_rep)


def list_string_join(latex_or_utf8_rep) -> str:
    """
    turn a (structured) latex or utf-8 representation into a latex string

    :param latex_or_utf8_rep: type is recursively defined as str or list of
    latex_or_utf8_rep
    """
    if isinstance(latex_or_utf8_rep, str):
        return latex_or_utf8_rep
    elif isinstance(latex_or_utf8_rep, list):
        string = ""
        for lr in latex_or_utf8_rep:
            lr = list_string_join(lr)
            string += lr
        #    log.debug("string:", latex_str)
        return string
    else:
        return "?"


# TODO : tenir compte de la profondeur des parenthèses,
# et utiliser \Biggl(\biggl(\Bigl(\bigl((x)\bigr)\Bigr)\biggr)\Biggr)
nature_leaves_list = ["PROP", "TYPE", "SET_UNIVERSE", "SET", "ELEMENT",
                      "FUNCTION", "SEQUENCE", "SET_FAMILY",
                      "TYPE_NUMBER", "NUMBER", "VAR", "SET_EMPTY"]


def needs_paren(parent: MathObject, child_number: int) -> bool:
    """
    Decides if parentheses are needed around the child
    e.g. if PropObj.node = PROP.IFF then
    needs_paren(PropObj,i) will be set to True for i = 0, 1
    so that the display will be
    ( ... ) <=> ( ... )
    """
    child_prop_obj = parent.children[child_number]
    p_node = parent.node
    # if child_prop_obj.node == "LOCAL_CONSTANT":
    #     return False
    if not child_prop_obj.children:
        return False
    c_node = child_prop_obj.node
    if c_node in nature_leaves_list + \
            ["SET_IMAGE", "SET_INVERSE", "PROP_BELONGS", "PROP_EQUAL",
             "PROP_INCLUDED"]:
        return False
    elif p_node in ["SET_IMAGE", "SET_INVERSE",
                    "SET_UNION+", "SET_INTER+", "APPLICATION",
                    "PROP_EQUAL", "PROP_INCLUDED", "PROP_BELONGS", "LAMBDA"]:
        return False
    elif c_node == "SET_COMPLEMENT" and p_node != "SET_COMPLEMENT":
        return False
    return True



        # ###################
        # # Bound variables #
        # ###################
        # if node.startswith("LOCAL_CONSTANT"):
        #     # unidentified local constant = bound variable
        #     # NB: will be given a name when dealing with quantifier or lambda
        #     # lean_data["name"] must be kept untouched here
        #     # since it will serve as hint for good name
        #     representation = {"latex": "??",
        #                       "utf8": "??"}
        #     node = "LOCAL_CONSTANT"
        #     math_type = children[0]
        #     prop_obj = BoundVarPO(node, [], representation, lean_data,
        #                           math_type)
        #     ProofStatePO.dict_[lean_data["id"]] = prop_obj
        #     #log.info(
        #     #    f"adding {lean_data['name']} to the dictionary, ident ="
        #     #    f" {lean_data['id']}")
        #
        #     return prop_obj
        #
        # #############################################################
        # # Quantifiers & lambdas: give a good name to bound variable #
        # #############################################################
        # # NB: lean_data["name"] is given by structures.lean,
        # # but may be inadequate (e.g. two distinct variables sharing the
        # # same name)
        # # For an expression like ∀ x: X, P(x)
        # # the logical constraints are: the name of the bound variable (
        # # which is going to replace `x`)  must be distinct from all names of
        # # variables appearing in the body `P(x)`, whether free or bound
        #
        # if node.startswith("QUANT") or node == "LAMBDA":
        #     bound_var_type, bound_var, local_context = children
        #     #log.debug(f"Processing bound var in {node, children}")
        #     # changing lean_data["name"]
        #     # so that it will not be on the forbidden list
        #     hint = bound_var.lean_data["name"]
        #     bound_var.lean_data["name"] = "processing name..."
        #     # search for a fresh name valid inside pfpo
        #     name = give_name.give_local_name(math_type=bound_var_type,
        #                                      hints=[hint],
        #                                      body=local_context)
        #     # store the new name for representation
        #     bound_var.representation = {"latex": name,
        #                                 "utf8": name}
        #     # store the new name for list of variables'names
        #     # BEWARE: original lean nam is changed
        #     bound_var.lean_data["name"] = name
        #                              # of mere string
        #     #log.debug(f"Give name {name} to bound var {bound_var} in {node}")
        #
        # #############
        # # CONSTANTS #
        # #############
        # # todo: suppress
        # if node.startswith("CONSTANT"):
        #     info = extract_name(node)
        #     representation['info'] = info
        #     node = "CONSTANT"
        #     #log.debug(f"creating CONSTANT {info}")
        # #################
        # # Instantiation #
        # #################
        # prop_obj = cls(node, children, representation)
        # return prop_obj


    # def is_prop_math_type(self) -> bool:
    #     """
    #     tells if the math_type of self is a Proposition
    #     NB: for ProofStatePO's (but not for all PropObj),
    #     if self.math_type.node = 'APPLICATION' then self
    #     is the term of a Proposition
    #     (e.g 'injective' vs 'composition')
    #     """
    #     return self.math_type.is_prop() \
    #            or self.math_type.node == 'APPLICATION' \
    #            or (hasattr(self.math_type, "math_type") \
    #                and self.math_type.math_type.node == 'PROP')


# @dataclass(eq=False)
# class BoundVarPO(ProofStatePO):
#     """
#     Variables that are bound by a quantifier
#     """




##########
# essais #
##########
if __name__ == '__main__':
    logger.configure()
