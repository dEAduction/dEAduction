"""
#############################################################################################
# PropObj.py : Take the result of Lean's tactic "Context_analysis", and process it to extract
# the mathematical content.
##############################################################################################
    
This files provides python classes for encoding mathematical objects and propositions
(PropObj, AnonymousPO, ProofStatePO, BoundVarPO)
and the following functions
- create_anonymous_prop_obj and create_pspo instanciate objects respectively
in the classes AnonymousPO, ProofStatePO. The function create_pspo makes use of
analysis.LeanExprVisitor
- process_context translates the Lean output into objects, making use of create_pspo.

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

    TODO:
    - make PropObj hashable -> math_type_dict
    - for this, use frozen
    - for this... incorporer le calcul de latex_rep dans la création de AnonymousPO

"""
from dataclasses import dataclass
import analysis

equal_sep = "¿= "
open_bra = "¿["
closed_bra = "¿]"


@dataclass
class PropObj:
    """
    Python representation of mathematical entities,
    both objects (sets, elements, functions, ...)
    and properties ("a belongs to A", ...)
    !! No instance should be deleted until the exercise is over
    !! Once created, a field can be added but no field should be modified
    """
    node: str
    children: list
    latex_rep: list
    nodes_list = ["PROP_AND", "PROP_OR", "PROP_IFF", "PROP_NOT", "PROP_IMPLIES",
                  "QUANT_∀", "QUANT_∃", "PROP_∃",
                  "SET_INTER", "SET_UNION", "SET_INTER+", "SET_UNION+",
                  "PROP_INCLUDED", "PROP_BELONGS", "SET_COMPLEMENT"
                                                   "SET_IMAGE", "SET_INVERSE",
                  "PROP_EQUAL", "PROP_EQUAL_NOT",
                  "PROP_<", "PROP_>", "PROP_≤", "PROP_≥",
                  "MINUS", "+",
                  "APPLICATION_FUNCTION", "VAR"]
    # APPLICATION ?
    leaves_list = ["PROP", "TYPE", "SET", "ELEMENT",
                   "FUNCTION", "SEQUENCE", "SET_FAMILY",
                   "TYPE_NUMBER", "NUMBER", "VAR"]  # VAR should not be used any more


@dataclass
class AnonymousPO(PropObj):
    """
    Objects and Propositions not in the proof state, in practice they will be
    sub-objects of the ProofStatePO instances
    """

    def __eq__(self, other):
        """
        test if the two prop_obj code for the same mathematical objects.
        This is used to guarantee uniqueness of those AnonymousPO objects that appears as math_types

        :param self: AnonymousPO
        :param other: AnonymousPO
        :return: bool
        """
        if self.node != other.node:
            return False
        if len(self.children) != len(other.children):
            return False
        for i in range(len(self.children)):
            if not self.children[i] == other.children[i]:
                return False
        return True

#    def __hash__(self):
#        return PropObj.__hash__(self)


#    __hash__ = PropObj.__hash__

@dataclass
class ProofStatePO(PropObj):
    """
    Objects and Propositions of the proof state and bound variables
    """
    lean_data: dict  # the Lean data ; keys = "id", "name", "pptype"
    math_type: PropObj
    # list_of_terms: only when the object is the math_type of some other object
    dict_ = {}  # dictionary of all instances of ProofStatePO with identifiers as keys
    context_dict = {}  # dictionary of instances in the current context (useful e.g. to baptize new variables)
    list_ = []  # list of all instances
    math_types_list = []  # list of AnonymousPO that occurs as math_type of some ProofStatePO,
    math_types_instances = [] # list of ProofStatePO whose math_type equals the corresponding term of math_types_list


@dataclass
class BoundVarPO(ProofStatePO):
    """
    Variables that are bound by a quantifier
    """
    names_list = []


def create_pspo(prop_obj_str: str, debug: bool = True) -> ProofStatePO:
    """

    Take a string from context_analysis or goals_analysis and turn it into a
    an instance of the class ProofStatePO.
    Makes use of
        - analysis.lean_expr_grammar.parse
        - create_anPO.
    prop_obj_str is assumed to have format
    `%%head ¿= %%tail` where ¿= is defined in equal_sep

    :param prop_obj_str: aa string from Lean that describes the object
    :param debug:
    :return: the new object
    """
    head, _, tail = prop_obj_str.partition(equal_sep)
    # extract lean_data from the head : name, id, pptype (if prop)
    lean_data = extract_lean_data(head)
    if lean_data["id"] in ProofStatePO.dict_:  # object already exists
        prop_obj = ProofStatePO.dict_[lean_data["id"]]
        ProofStatePO.context_dict[lean_data["id"]] = prop_obj
        return prop_obj
    # extract math_type from the tail
    tree = analysis.lean_expr_grammar.parse(tail)
    po_str_list = analysis.LeanExprVisitor().visit(tree)
    math_type = create_anonymous_prop_obj(po_str_list[0], debug)
    # check if math_type = a previously defined math_type
    exists_math_type = False
    l = len(ProofStatePO.math_types_list)
    for i in range(l):
        mt = ProofStatePO.math_types_list[i]
        if math_type == mt: # test if both Python objects represents the same math objects
            del math_type  # is this useful ?
            mt_number = i
            math_type = mt
            exists_math_type = True
            break
    if not exists_math_type:
        mt_number = l
        ProofStatePO.math_types_list.append(math_type)
        ProofStatePO.math_types_instances.append([])
    # end
    latex_rep = lean_data["name"]  # useless if PROP
    node = ""
    children = []
    prop_obj = ProofStatePO(node, children, latex_rep, lean_data, math_type)
    # Adjusting datas
    ProofStatePO.dict_[lean_data["id"]] = prop_obj
    ProofStatePO.context_dict[lean_data["id"]] = prop_obj
    ProofStatePO.math_types_instances[mt_number].append(prop_obj)
    if debug:
        print(f"j'ajoute {lean_data['name']} au dico, ident = {lean_data['id']}")
    return prop_obj


def create_anonymous_prop_obj(prop_obj_dict: dict, debug):
    """
    create anonymous sub-objects and props, or refer to existing pfPO
    """
    latex_rep = []  # latex representation is computed later
    node = prop_obj_dict["node"]
    #    ident = extract_identifier2(node)
    lean_data = extract_lean_data(node)
    if lean_data["id"] in ProofStatePO.dict_:  # check if PO already exists (= ProofStatePO or BoundVarPO)
        prop_obj = ProofStatePO.dict_[lean_data["id"]]
        return prop_obj
    #### creation of children PO
    arguments = prop_obj_dict["children"]
    children = []
    for arg in arguments:
        arg_prop_obj = create_anonymous_prop_obj(arg, debug)
        children.append(arg_prop_obj)
    #### special cases
    if node.startswith("LOCAL_CONSTANT"):  # unidentified local constant = bound variable
        latex_rep = lean_data["name"]
        math_type = children[0]
        prop_obj = BoundVarPO(node, [], latex_rep, lean_data, math_type)
        BoundVarPO.names_list.append(lean_data["name"])
        return prop_obj
    if node == "APPLICATION" and children[0].node == "FUNCTION":
        node = "APPLICATION_FUNCTION"
    prop_obj = AnonymousPO(node, children, latex_rep)
    return prop_obj


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

# def extract_nature_compl(string: str):
#    str1 = "["
#    str2 = "]"
#    return(extract(string, str1, str2))

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
    str2 = "/ident"
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


def process_context(lean_analysis: str, debug=True) -> list:
    """
    Process the strings provided by Lean's context_analysis and goals_analysis
    and create the corresponding ProofStatePO instances by calling create_psPO
    (will probably not be used at the end)

    :param analysis: a string which is the result of Lean's hypo_analysis or goals_analysis tactics
    :param debug:
    :return: a list of ProofStatePO's
    """
    list_ = lean_analysis.splitlines()
    #    is_goal = None
    prop_obj_list = []
    for prop_obj_string in list_:
        if prop_obj_string.startswith("context"):
            pass
        #            is_goal = False
        elif prop_obj_string.startswith("goals"):
            pass
        #                is_goal = True
        else:
            prop_obj = create_pspo(prop_obj_string, debug)
            #           PO.is_goal = is_goal
            prop_obj_list.append(prop_obj)
    return prop_obj_list


# essai
if __name__ == '__main__':
    debug = True
