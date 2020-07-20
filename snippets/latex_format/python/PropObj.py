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
import deaduction.pylib.logger as logger
import logging

import lean_analysis
from latex_format_data import latex_structures, utf8_structures


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
    utf8_rep: list
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
    # APPLICATION ?
    leaves_list = ["PROP", "TYPE", "SET", "ELEMENT",
                   "FUNCTION", "SEQUENCE", "SET_FAMILY",
                   "TYPE_NUMBER", "NUMBER", "VAR"]

    # VAR should not be used any more

    def is_prop(self) -> bool:
        return self.node.startswith("PROP") or self.node.startswith("QUANT")

    def structured_format(self, format = "latex"):
        """
        Compute a structured "latex representation" of a prop_obj.
        Valid latex rep are recursively defined as:
        - lists of strings (in latex format)
        - lists of latex rep
        """
        log = logging.getLogger("Latex representation")
        if format == "latex":
            log.info(f"computing latex representation of {self}")
            field = "latex_rep"
        else:
            log.info(f"computing utf8 representation of {self}")
            field = "utf8_rep"
        if eval("self." + field) != None: # should be useless
            return
        a = []  # will be the list of the latex rep of the children
        node = self.node
        i = -1
        for arg in self.children:
            i += 1
            if eval("arg." + field) == None:
                PropObj.structured_format(arg, format) # = compute_latex
            lr = eval("arg." + field)
            parentheses = needs_paren(self, i)
            if parentheses:
                lr = ["(", lr, ")"]
            a.append(lr)
        log.debug(f"Node: {node}")
        if format == "latex":
            symbol, format_scheme = latex_structures[node]
            self.latex_rep = format_scheme(symbol, a, self, format="latex")
        else:
            symbol, format_scheme = utf8_structures[node]
            self.utf8_rep = format_scheme(symbol, a, self, format="utf8")
        log.info(f"--> {self.latex_rep}")
        return

    def format_as_latex(self):
        PropObj.structured_format(self, format="latex")
        lr = self.latex_rep
        if not isinstance(lr, list):
            return lr
        else:
            return list_string_join(lr)

    def format_as_utf8(self):
        PropObj.structured_format(self, format="utf8")
        lr = self.utf8_rep
        if not isinstance(lr, list):
            return lr
        else:
            return list_string_join(lr)


def list_string_join(latex_or_utf8__rep):
    """
    turn a (structured) latex representation into a latex string
    """
    string = ""
    for lr in latex_or_utf8__rep:
        if type(lr) is list:
            lr = list_string_join(lr)
        string += lr
    #    log.debug("string:", latex_str)
    return string

# TODO : tenir compte de la profondeur des parenthèses,
# et utiliser \Biggl(\biggl(\Bigl(\bigl((x)\bigr)\Bigr)\biggr)\Biggr)

nature_leaves_list = ["PROP", "TYPE", "SET_UNIVERSE", "SET", "ELEMENT",
                      "FUNCTION", "SEQUENCE", "SET_FAMILY",
                      "TYPE_NUMBER", "NUMBER", "VAR", "SET_EMPTY"]

def needs_paren(parent: PropObj, child_number: int):
    """
    Decides if parentheses are needed around the child
    """
    b = True
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
        b = False
    elif p_node in ["SET_IMAGE", "SET_INVERSE", "APPLICATION_FUNCTION",
                    "PROP_EQUAL", "PROP_INCLUDED", "PROP_BELONGS"]:
        b = False
    elif c_node == "SET_COMPLEMENT" and p_node != "SET_COMPLEMENT":
        b = False
    return b

@dataclass
class AnonymousPO(PropObj):
    """
    Objects and Propositions not in the proof state, in practice they will be
    sub-objects of the ProofStatePO instances
    """

    def __eq__(self, other):
        """
        test if the two prop_obj code for the same mathematical objects.
        This is used to guarantee uniqueness of those AnonymousPO
        objects that appears as math_types

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


@dataclass
class ProofStatePO(PropObj):
    """
    Objects and Propositions of the proof state and bound variables
    """
    lean_data: dict  # the Lean data ; keys = "id", "name", "pptype"
    math_type: PropObj
    # list_of_terms: only when the object is the math_type of some other object
    dict_ = {}  # dictionary of all instances of ProofStatePO
    # with identifiers as keys
    context_dict = {}  # dictionary of instances in the current context
    # including bound variables
    # (useful e.g. to provide name to new variables)
    list_ = []  # list of all instances
    math_types_list = []  # list of AnonymousPO
    # that occurs as math_type of some ProofStatePO,
    math_types_instances = []  # list of lists of ProofStatePO
    # whose math_type equals the corresponding term of math_types_list




@dataclass
class BoundVarPO(ProofStatePO):
    """
    Variables that are bound by a quantifier
    """
    names_list = []


def create_pspo(prop_obj_str: str) -> ProofStatePO:
    """
    Take a string from context_analysis or goals_analysis and turn it into a
    an instance of the class ProofStatePO.
    Makes use of
        - analysis.lean_expr_grammar.parse
        - create_anPO.
    prop_obj_str is assumed to have format
    `%%head ¿= %%tail` where ¿= is defined in equal_sep

    This function also creates all the intermediate AnonymousPO's that are
    needed to describe the mathematical entity.

    :param prop_obj_str: a string from Lean that describes the object
    :return: the new object
    """
    log = logging.getLogger("PropObj")
    log.debug(f"processing to create ProofStatePO from {prop_obj_str}")
    head, _, tail = prop_obj_str.partition(equal_sep)
    # extract lean_data from the head : name, id, pptype (if prop)
    lean_data = extract_lean_data(head)
    if lean_data["id"] in ProofStatePO.dict_:  # object already exists
        prop_obj = ProofStatePO.dict_[lean_data["id"]]
        ProofStatePO.context_dict[lean_data["id"]] = prop_obj
        return prop_obj
    # extract math_type from the tail
    tree = lean_analysis.lean_expr_grammar.parse(tail)
    po_str_list = lean_analysis.LeanExprVisitor().visit(tree)
    math_type = create_anonymous_prop_obj(po_str_list[0])
    log.debug(f"math type: {math_type}")
    node = None
    children = None
    latex_rep = lean_data["name"]  # equals "" if is_prop == True
    utf8_rep = lean_data["name"]
    # treatment of objects (not prop): handling of math_types_list
    # todo: use a list method that appends iff not in
    if not math_type.is_prop():
        exists_math_type = False
        length = len(ProofStatePO.math_types_list)
        for i in range(length):
            mt = ProofStatePO.math_types_list[i]
            if math_type == mt:  # test if both Python objects
                # represents the same math objects
                del math_type  # is this useful ?
                mt_number = i
                math_type = mt
                exists_math_type = True
                break
        if not exists_math_type:
            mt_number = length
            ProofStatePO.math_types_list.append(math_type)
            ProofStatePO.math_types_instances.append([])
    # end
    prop_obj = ProofStatePO(node, children, latex_rep, utf8_rep, lean_data,
                            math_type)
    # Adjusting datas
    if lean_data["id"] != "":
        ProofStatePO.dict_[lean_data["id"]] = prop_obj # probably useless
    if not math_type.is_prop():
        ProofStatePO.context_dict[lean_data["id"]] = prop_obj
        ProofStatePO.math_types_instances[mt_number].append(prop_obj)
        log.info(f"adding {lean_data['name']} to the dictionnary, ident ="
             f" {lean_data['id']}")
    return prop_obj


def create_anonymous_prop_obj(prop_obj_dict: dict):
    """
    create anonymous sub-objects and props, or refer to existing pfPO
    :param prop_obj_dict: dictionary provided by analysis.LeanExprVisitor
    :return: an instance of AnonymousPO
    """
    latex_rep = None  # latex representation is computed later
    utf8_rep = None
    node = prop_obj_dict["node"]
    #    ident = extract_identifier2(node)
    lean_data = extract_lean_data(node)
    if lean_data["id"] in ProofStatePO.dict_:  # check if PO already exists
        # (= ProofStatePO or BoundVarPO)
        prop_obj = ProofStatePO.dict_[lean_data["id"]]
        return prop_obj
    #### creation of children PO
    arguments = prop_obj_dict["children"]
    children = []
    for arg in arguments:
        arg_prop_obj = create_anonymous_prop_obj(arg)
        children.append(arg_prop_obj)
    #### special cases
    if node.startswith("LOCAL_CONSTANT"):
        # unidentified local constant = bound variable
        latex_rep = lean_data["name"]
        utf8_rep = lean_data["name"]
        math_type = children[0]
        prop_obj = BoundVarPO(node, [], latex_rep, utf8_rep, lean_data,
                              math_type)
        BoundVarPO.names_list.append(lean_data["name"])
        return prop_obj
    if node == "APPLICATION" and children[0].node == "FUNCTION":
        node = "APPLICATION_FUNCTION"
    prop_obj = AnonymousPO(node, children, latex_rep, utf8_rep)
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


def process_context(lean_analysis: str) -> list:
    """
    Process the strings provided by Lean's context_analysis and goals_analysis
    and create the corresponding ProofStatePO instances by calling create_psPO
    (will probably not be used at the end)

    :param lean_analysis: a string which is the result of Lean's hypo_analysis
    or goals_analysis tactics
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
            prop_obj = create_pspo(prop_obj_string)
            #           PO.is_goal = is_goal
            prop_obj_list.append(prop_obj)
    return prop_obj_list


# essai
if __name__ == '__main__':
    logger.configure()
    essai_reciproque_union = """context:
OBJECT[LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1112.20255¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.1112.20257¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1112.20260¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= FUNCTION¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1112.20255¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.1112.20257¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1112.20262¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.1112.20257¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.1112.20265¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.1112.20257¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.1217.17744]/pp_type: ∀ ⦃x : X⦄, x ∈ (f⁻¹⟮B ∪ B'⟯) → x ∈ f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯)] ¿= QUANT_∀¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1215.9868¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:x/identifier:_fresh.1217.17768¿]¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1215.9868¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, PROP_IMPLIES¿(PROP_BELONGS¿(LOCAL_CONSTANT¿[name:x/identifier:_fresh.1217.17768¿]¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1215.9868¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1215.9873¿]¿(CONSTANT¿[name:1/1¿]¿)¿, SET_UNION¿(LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1215.9875¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.1215.9878¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)¿, PROP_BELONGS¿(LOCAL_CONSTANT¿[name:x/identifier:_fresh.1217.17768¿]¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1215.9868¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, SET_UNION¿(SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1215.9873¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1215.9875¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1215.9873¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.1215.9878¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)¿)¿)
PROPERTY[METAVAR[_mlocal._fresh.1217.17729]/pp_type: f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯) ⊆ (f⁻¹⟮B ∪ B'⟯)] ¿= PROP_INCLUDED¿(SET_UNION¿(SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1215.9873¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1215.9875¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1215.9873¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.1215.9878¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1215.9873¿]¿(CONSTANT¿[name:1/1¿]¿)¿, SET_UNION¿(LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1215.9875¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.1215.9878¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)"""

    essai = essai_reciproque_union
    liste = process_context(essai)
    print(liste)
    print("")
#    for pfprop_obj in liste:
#        pfprop_obj.math_type.latex_rep = pfprop_obj.math_type.compute_latex()
#        pfprop_obj.latex_type_str = latex_join(pfprop_obj.latex_type)
#        print("-------")
    format = "utf8"

    for pfprop_obj in liste:
        print(f"{eval('pfprop_obj.format_as_' + format +'()' )} : "
              f"{eval('pfprop_obj.math_type.format_as_' + format + '()')}")
#        print(f"assemblé :  {latex_join(pfprop_obj.math_type.latex_rep)}")
    print("List of math types:")
    i = 0
    for mt in ProofStatePO.math_types_list:
        print(f" {mt.format_as_utf8()}: ",
    f"{[PO.format_as_utf8() for PO in ProofStatePO.math_types_instances[i]]}")
        i += 1
