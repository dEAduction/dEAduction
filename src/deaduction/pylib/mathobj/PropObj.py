"""
#####################################################################
# PropObj.py : Take the result of Lean's tactic "Context_analysis", #
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
from typing import Tuple, List, Dict
import logging

import deaduction.pylib.logger as logger
import deaduction.pylib.mathobj.lean_analysis as lean_analysis
import deaduction.pylib.mathobj.display_math_object as latex_format_data
import deaduction.pylib.mathobj.give_name as give_name

log = logging.getLogger(__name__)

equal_sep = "¿= "
open_bra = "¿["
closed_bra = "¿]"


##########################################
# PropObj: general mathematical entities #
##########################################

@dataclass
class PropObj:
    """
    Python representation of mathematical entities,
    both objects (sets, elements, functions, ...)
    and properties ("a belongs to A", ...)
    !! No instance should be deleted until the exercise is over
    """
    node: str  # e.g.
    children: list
    representation: Dict[str, list]
    # features of representation:
    # keys = 'latex, 'utf8', 'info'
    # 'info' value is used when node = 'CONSTANT' to store CONSTANT name
    # (e.g. "false")
    # default value = "??"

    # The following are here just to help reading the code
    # See structures.lean for more accurate lists
    nodes_list = ["PROP_AND", "PROP_OR", "PROP_IFF", "PROP_NOT",
                  "PROP_IMPLIES",
                  "QUANT_∀", "QUANT_∃", "PROP_∃",
                  "SET_INTER", "SET_UNION", "SET_INTER+", "SET_UNION+",
                  "PROP_INCLUDED", "PROP_BELONGS", "SET_COMPLEMENT"
                                                   "SET_IMAGE", "SET_INVERSE",
                  "PROP_EQUAL", "PROP_EQUAL_NOT",
                  "PROP_<", "PROP_>", "PROP_≤", "PROP_≥",
                  "MINUS", "+",
                  "APPLICATION_FUNCTION", "VAR"]
    leaves_list = ["PROP", "TYPE", "SET", "ELEMENT",
                   "FUNCTION", "SEQUENCE", "SET_FAMILY",
                   "TYPE_NUMBER", "NUMBER", "VAR"]

    # VAR should not be used any more (they should be instantiated in Lean's
    # structure tactic)

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
                if not PropObj.__eq__(self.children[index],
                                      other.children[index]):
                    return False
        return True

    def is_prop(self) -> bool:
        """
        Test if self represents a mathematical Proposition
        (as opposed to object).
        ! MIND ! that for ProofStatePO's, only the math_type attribute
        should be tested !
        For ProofSatetPO's, this function is redefined by testing the math_type
        """
        if self.node == "":
            return False
        else:
            return self.node.startswith("PROP") \
                   or self.node.startswith("QUANT")

    ###############################
    # collect the local variables #
    ###############################
    def extract_local_vars(self) -> list:
        """
        recursively collect the list of variables used in the definition of
        self (leaves of the tree). Here by definition, being a variable
        means having a len_data["name"]
        :return: list of PropObj
        """
        if hasattr(self, "lean_data"):
            if "name" in self.lean_data.keys():
                name = self.lean_data["name"]
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
        return [po.lean_data["name"] for po in self.extract_local_vars()]

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
            PropObj.structured_format(arg, format_)
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
        PropObj.structured_format(self, "latex", is_type_of_pfpo)
        structured_rep  = self.representation["latex"]
        return list_string_join(structured_rep)

    def format_as_utf8(self, is_type_of_pfpo=False):
        PropObj.structured_format(self, "utf8", is_type_of_pfpo)
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


def needs_paren(parent: PropObj, child_number: int) -> bool:
    """
    Decides if parentheses are needed around the child
    e.g. if PropObj.node = PROP.IFF then
    needs_paren(PropObj,i) will be set to True for i = 0, 1
    so that the display will be
    ( ... ) <=> ( ... )
    """
    child_prop_obj = parent.children[child_number]
    p_node = parent.node
    if isinstance(child_prop_obj, ProofStatePO):
        return False
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


###########################################################
# AnonymousPO: math bricks for ProofStatePO's math_type's #
###########################################################

@dataclass(eq=False)  # will inherit the __eq__ method from PropObj
class AnonymousPO(PropObj):
    """
    Objects and Propositions not in the proof state, in practice they will be
    sub-objects of the math_types of ProofStatePO instances
    """

    @classmethod
    def from_tree(cls, prop_obj_dict: dict):
        """
        create anonymous sub-objects and props, or refer to existing pfPO
        :param prop_obj_dict: dictionary provided by analysis.LeanExprVisitor
        :return: an instance of AnonymousPO
        """
        representation = {'latex': "??", 'utf8': "??", 'info': "??"}
        # latex representation is computed later
        node = prop_obj_dict["node"]
        lean_data = extract_lean_data(node)
        ##############################
        # check if PO already exists #
        ##############################
        if lean_data["id"] in ProofStatePO.dict_:
            prop_obj = ProofStatePO.dict_[lean_data["id"]]
            return prop_obj
        ####################################
        # creation of children AnonymousPO #
        ####################################
        arguments = prop_obj_dict["children"]
        children = []
        for arg in arguments:
            arg_prop_obj = AnonymousPO.from_tree(arg)
            children.append(arg_prop_obj)

        ###################
        # Bound variables #
        ###################
        if node.startswith("LOCAL_CONSTANT"):
            # unidentified local constant = bound variable
            # NB: will be given a name when dealing with quantifier or lambda
            # lean_data["name"] must be kept untouched here
            # since it will serve as hint for good name
            representation = {"latex": "??",
                              "utf8": "??"}
            node = "LOCAL_CONSTANT"
            math_type = children[0]
            prop_obj = BoundVarPO(node, [], representation, lean_data,
                                  math_type)
            ProofStatePO.dict_[lean_data["id"]] = prop_obj
            #log.info(
            #    f"adding {lean_data['name']} to the dictionary, ident ="
            #    f" {lean_data['id']}")

            return prop_obj

        #############################################################
        # Quantifiers & lambdas: give a good name to bound variable #
        #############################################################
        # NB: lean_data["name"] is given by structures.lean,
        # but may be inadequate (e.g. two distinct variables sharing the
        # same name)
        # For an expression like ∀ x: X, P(x)
        # the logical constraints are: the name of the bound variable (
        # which is going to replace `x`)  must be distinct from all names of
        # variables appearing in the body `P(x)`, whether free or bound

        if node.startswith("QUANT") or node == "LAMBDA":
            bound_var_type, bound_var, local_context = children
            #log.debug(f"Processing bound var in {node, children}")
            # changing lean_data["name"]
            # so that it will not be on the forbidden list
            hint = bound_var.lean_data["name"]
            bound_var.lean_data["name"] = "processing name..."
            # search for a fresh name valid inside pfpo
            name = give_name.give_local_name(math_type=bound_var_type,
                                             hints=[hint],
                                             body=local_context)
            # store the new name for representation
            bound_var.representation = {"latex": name,
                                        "utf8": name}
            # store the new name for list of variables'names
            # BEWARE: original lean nam is changed
            bound_var.lean_data["name"] = name
                                     # of mere string
            #log.debug(f"Give name {name} to bound var {bound_var} in {node}")

        #############
        # CONSTANTS #
        #############
        # todo: suppress
        if node.startswith("CONSTANT"):
            info = extract_name(node)
            representation['info'] = info
            node = "CONSTANT"
            #log.debug(f"creating CONSTANT {info}")
        #################
        # Instantiation #
        #################
        prop_obj = cls(node, children, representation)
        return prop_obj


@dataclass(eq=False)
class ProofStatePO(PropObj):
    """
    Objects and Propositions of the proof state (and bound variables)
    """
    lean_data: dict  # the Lean data ; keys = "id", "name", "pptype"
    math_type: PropObj

    dict_ = {}  # dictionary of all instances of ProofStatePO

    # with identifiers as keys. This is used to guarantee
    # uniqueness of ProofStatePO's instances
    # including bound variables
    # (useful e.g. to provide name to new variables)

    @classmethod
    def from_string(cls, prop_obj_str: str):
        """
        Take a string from context_analysis or goals_analysis and turn it into
        an instance of the class ProofStatePO.
        Makes use of
            - analysis.lean_expr_grammar.parse
            - AnonymousPO.from_tree
        prop_obj_str is assumed to have format
        `%%head ¿= %%tail` where ¿= is defined in equal_sep

        This function also calls the creation of all the intermediate
        AnonymousPO's that are needed to describe the mathematical entity.

        :param prop_obj_str: a string from Lean that describes the object
        :return: the new object
        """
        #log.debug(f"processing to create ProofStatePO from {prop_obj_str}")
        head, _, tail = prop_obj_str.partition(equal_sep)
        # extract lean_data from the head : name, id, pptype (if prop)
        lean_data = extract_lean_data(head)
        if lean_data["id"] in ProofStatePO.dict_:  # object already exists
            prop_obj = ProofStatePO.dict_[lean_data["id"]]
            #        ProofStatePO.context_dict[lean_data["id"]] = prop_obj
            return prop_obj
        ##################################################################
        # extract math_type from the tail and call AnonymousPO.from_tree #
        ##################################################################
        tree = lean_analysis.lean_expr_grammar.parse(tail)
        po_str_list = lean_analysis.LeanExprVisitor().visit(tree)
        math_type = AnonymousPO.from_tree(po_str_list[0])
        #log.debug(f"math type: {math_type}")
        node = "LOCAL_CONSTANT"
        children = []
        representation = {"latex": lean_data["name"],
                          "utf8": lean_data["name"]}
        #################
        # Instantiation #
        #################
        prop_obj = cls(node, children, representation, lean_data, math_type)
        ######################################
        # Adjusting data : dict_, math_types #
        ######################################
        if lean_data["id"] != "":
            ProofStatePO.dict_[lean_data["id"]] = prop_obj
            #log.info(f"adding {lean_data['name']} to the dictionary, ident ="
            #         f" {lean_data['id']}")
        #        if not math_type.is_prop():
        #            math_type_store(prop_obj, math_type)
        return prop_obj

    def is_prop_math_type(self) -> bool:
        """
        tells if the math_type of self is a Proposition
        NB: for ProofStatePO's (but not for all PropObj),
        if self.math_type.node = 'APPLICATION' then self
        is the term of a Proposition
        (e.g 'injective' vs 'composition')
        """
        return self.math_type.is_prop() \
               or self.math_type.node == 'APPLICATION' \
               or (hasattr(self.math_type, "math_type") \
                   and self.math_type.math_type.node == 'PROP')


@dataclass(eq=False)
class BoundVarPO(ProofStatePO):
    """
    Variables that are bound by a quantifier
    """


def math_type_store(math_types: List[Tuple[PropObj, List[ProofStatePO]]],
                    prop_obj: ProofStatePO, math_type: PropObj):
    """
    Store PropObj in the ProofStatePO.math_types_instances list,
    after adding math_type in math_types if needed

    :param prop_obj: instance of ProofStatePO to be stored
    :param math_type: math_type of PropObj
    :param math_types: list of tuples (math_type, math_type_instances)
    where math_type_instances is a list of instances of math_type
    """
    #log.debug(f"storing {prop_obj.representation['utf8']} in"
    #          f"math_types_instances of {math_type}")
    index = 0
    for item, item_list in math_types:
        if item == math_type:
            break
        index += 1
    if index == len(math_types):
        # this is the first instance of math_type
        math_types.append((math_type, []))
    # add prop_obj to the instances of path_type
    # NB: math_types[index][1] is the list of instances
    # of math_types[index][0]
    math_types[index][1].append(prop_obj)


def extract_lean_data(local_constant: str) -> dict:
    ident = extract_identifier1(local_constant)
    name = extract_name(local_constant)
    lean_data = {"name": name, "id": ident}
    if local_constant.startswith("PROP"):
        lean_data["pptype"] = extract_pp_type(local_constant)
    return lean_data


###########################
# String extraction tools #
###########################

def extract_nature_subtree(string: str):
    return (extract(string, "", "_"))


def extract_identifier1(string: str):
    str1 = "identifier:"
    str2 = closed_bra
    return (extract(string, str1, str2))


def extract_identifier2(string: str):
    str1 = "identifier:"
    str2 = ""
    return (extract(string, str1, str2))


def extract_pp_type(string: str):
    str1 = "pp_type:"
    str2 = "]"
    return (extract(string, str1, str2))


def extract_name(string: str):
    str1 = "name:"
    str2 = "/"
    return (extract(string, str1, str2))


def extract_num_var(string: str):
    str1 = "VAR["
    str2 = "]"
    return (int(extract(string, str1, str2)))  # Integer !!


def extract(string: str, str1: str, str2=""):
    if str1 == "":
        pos1 = 0
    else:
        pos1 = string.find(str1)
    if str2 == "":
        pos2 = len(string)
    else:
        pos2 = string.find(str2, pos1)
    if pos1 != -1 and pos2 != -1:
        str_extr = string[pos1 + len(str1):pos2]
    else:
        str_extr = ""
    return (str_extr)


##########
# essais #
##########
if __name__ == '__main__':
    logger.configure()
    essai_reciproque_union = """OBJECT[LOCAL_CONSTANT¿[name:X/identifier:0._fresh.680.5802¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.680.5804¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:f/identifier:0._fresh.680.5807¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= FUNCTION¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.680.5802¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.680.5804¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:B/identifier:0._fresh.680.5809¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.680.5804¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.680.5812¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.680.5804¿]¿(CONSTANT¿[name:1/1¿]¿)¿)"""
    essai_context_union = """context:
OBJECT[LOCAL_CONSTANT¿[name:X/identifier:0._fresh.436.13260¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:A/identifier:0._fresh.436.13262¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.436.13260¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:B/identifier:0._fresh.436.13265¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.436.13260¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:C/identifier:0._fresh.436.13268¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.436.13260¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:a/identifier:0._fresh.437.4734¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= LOCAL_CONSTANT¿[name:X/identifier:0._fresh.436.13260¿]¿(CONSTANT¿[name:1/1¿]¿)
PROPERTY[LOCAL_CONSTANT¿[name:H/identifier:0._fresh.437.4736¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: a ∈ A ∩ (B ∪ C)] ¿= PROP_BELONGS¿(LOCAL_CONSTANT¿[name:a/identifier:0._fresh.437.4734¿]¿(CONSTANT¿[name:1/1¿]¿)¿, SET_INTER¿(LOCAL_CONSTANT¿[name:A/identifier:0._fresh.436.13262¿]¿(CONSTANT¿[name:1/1¿]¿)¿, SET_UNION¿(LOCAL_CONSTANT¿[name:B/identifier:0._fresh.436.13265¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:C/identifier:0._fresh.436.13268¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)"""
    essai = essai_context_union
