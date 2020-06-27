"""
#############################################################################################
# PropObj.py : Take the result of Lean's tactic "Context_analysis", and process it to extract
# the mathematical content.
##############################################################################################

TODO
(1) META-APPLI, LOCAL CST, etc: avoir un nom invariable et passer pp et
identifiant en argument.

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
import analysis

equal_sep = "¿= "

@dataclass
class PropObj:
    """
    Python representation of mathematical entities, 
    both objects (sets, elements, functions, ...)
    and properties ("a belongs to A", ...)
    """
    nature: str
    nature_compl : str  # e.g. name of VAR, value of a NUMBER, ...
    nature_subtree: str # in nature_subtree_list
    args: list          # list of PO
    latex_rep: str
    
    nature_nodes_list = ["PROP_AND", "PROP_OR", "PROP_IFF", "PROP_NOT", "PROP_IMPLIES", 
                   "QUANT_∀", "QUANT_∃", "PROP_∃",
                   "SET_INTER", "SET_UNION", "SET_INTER+", "SET_UNION+", 
                   "PROP_INCLUDED", "PROP_BELONGS", "SET_COMPLEMENT"
                   "SET_IMAGE", "SET_INVERSE",
                   "PROP_EQUAL", "PROP_EQUAL_NOT",
                   "PROP_<", "PROP_>", "PROP_≤", "PROP_≥",
                   "MINUS", "+",
                   "APPLICATION_FUNCTION", "VAR"]
    # APPLICATION ?
    nature_leaves_list = ["PROP", "TYPE", "SET", "ELEMENT",
                           "FUNCTION", "SEQUENCE", "SET_FAMILY",
                           "TYPE_NUMBER", "NUMBER", "VAR"]  # VAR should not be used any more
    # CONSTANT ? LOCAL_CONSTANT ?
    # A traiter : 
    # de façon générale, APPLICATION, CONSTANT, LOCAL_CONSTANT
    

    def pprint_PO(self, inc = 0):
        """representation as a tree - for debug"""
        if isinstance(self, ProofStatePO):
            name = self.name
        else:
            name = ""
            print("|  " * inc + f"{self.nature}: {name}")
            inc +=1
            for arg in self.args:
                PropObj.print_PO(arg,inc)
   


     
@dataclass
class ProofStatePO(PropObj):
    """
    Objects and Propositions of the proof state
    """
    is_goal: bool
    lean_identifier: str    # the Lean unique internal identifier for the object
    lean_name: str               # the Lean user access the object/prop
    latex_type : str        # for Obj only. Identical to lean_name?    
    P_lean_pp_type: str     # for Prop only, mostly for debugging
    dict_ = {}              #dictionary (identifier,PropObj) of all instances

    def short_rep(self):  # nice rep for debugging
        return(f"name = {self.name}, latex = {self.latex_rep}, {self.latex_type}, \
            nature = {self.nature}, \
            arguments = {arg.name for arg in self.arguments}")
        
@dataclass
class AnonymousPO(PropObj):
    """
    Objects and Propositions not in the proof state, in practice they will be
    sub-objects of the ProofStatePO instances
    """
    

@dataclass
class BoundVarPO(AnonymousPO):
    """Variables that are bound by a quantifier"""
    lean_identifier: str    # the Lean unique internal identifier for the object
    lean_name: str               # the Lean pp of the bound var
    dict_ = {}
    
def process_context(analysis: str, debug = True):
    """
    process the strings provided by Lean's context_analysis and goals_analysis
    and create the corresponding ProofStatePO instances by calling create_psPO
    """
    list_ = analysis.splitlines()
    is_goal = None
    PO_list = []
    for PO_str in list_:
        if PO_str.startswith("context"):
            is_goal = False
        else:
            if PO_str.startswith("goals"):
                is_goal = True
            else:
                PO = create_psPO(PO_str, debug)
                PO.is_goal = is_goal
                PO_list.append(PO)        
    return(PO_list)
    


def create_psPO(prop_obj_str:str, debug = True):
    """
    take a string from context_analysis or goals_analysis and turn it into a 
    an instance of the class ProofStatePO. 
    Makes use of 
        - analysis.lean_expr_grammar.parse
        - create_anPO.
    prop_obj_str is assumed to have format 
    `%%head %= %%tail` where %= is defined in equal_sep
    """
    head, _ , tail = prop_obj_str.partition(equal_sep)
##### extract info from the head : lean_identifier, lean_name, 
# P_lean_pp_type, nature_leaves = PROP ?
    ident = extract_identifier1(head)
    assert(ident not in ProofStatePO.dict_) # PO should not have already been created
#    if ident in ProofStatePO.dict_: # check if PO already exists (probably useless)
#        PO = ProofStatePO.dict_[ident]
#        if debug:
#            print("Etrange, un pfPO déjà codé")
#        return(PO)
    lean_name = extract_name(head)
    if head.startswith("PROP"):   # A BOUGER
        nature_subtree = "PROP"
        P_lean_pp_type = extract_pp_type(head)
    else:
        P_lean_pp_type = ""
##### extract nature and arguments from the tail
    tree = analysis.lean_expr_grammar.parse(tail)
    PO_str_list = analysis.LeanExprVisitor().visit(tree)  
    nature, _ , compl = PO_str_list[0]["name"].partition("[")
    nature_compl = compl[0:-1]
    nature_subtree = pre_nature_sub(nature)
##### treatment of bound variables
#    bound_vars_list = []
#    if nature in ["QUANT_∀", "QUANT_∃"]:
#        name_var = nature_compl
#        bound_vars_list.append(name_var)
#        if debug:
#            print("list of bound variables:", bound_vars_list)
# creation of children PO    
    args = []
    for arg in PO_str_list[0]["arguments"]:
        PO = create_anPO(arg, debug)
#        PO = create_anPO(arg, bound_vars_list, debug)
        args.append(PO)  
#### Nature subtree : special cases (undefined with nature alone)
    if nature == "APPLICATION" and  args[0].nature == "FUNCTION":
        nature = "APPLICATION_FUNCTION"
        nature_subtree = args[-1].nature_subtree
#    elif nature == "MINUS" and args[0].nature_subtree == "SET":
#        nature = "SET_COMPLEMENT"
#        nature_subtree = "SET"
    elif nature == "LOCAL_CONSTANT":
        ident_type = extract_identifier2(nature_compl)
        if ident_type !="":
            psPO = ProofStatePO.dict_[ident_type]
            args = [psPO]
            if psPO.nature == "TYPE":
                nature = "ELEMENT"
### ADD OTHER SPECIAL CASES HERE           
    if debug:
        print("nature_subtree:", nature_subtree)

### end
    latex_rep = lean_name  # useless if PROP
    is_goal = None
#    needs_paren = False
    latex_type = ""                                 # will be computed later
    PO = ProofStatePO(nature, nature_compl, nature_subtree, args, latex_rep, 
#                      needs_paren,
                      is_goal, ident, lean_name, latex_type, P_lean_pp_type)
    if ident !="":
        ProofStatePO.dict_[ident]=PO
        if debug:
            print(f"j'ajoute {PO.nature} au dico, ident = {ident}")
    return(PO)



def create_anPO(PO_dict: dict, debug):
    """
    create anonymous sub-objects and props, or refer to existing pfPO
    """
    latex_rep = ""  # latex representation is computed later (except for VAR)
    
    nature, _, compl = PO_dict["name"].partition("[")
    nature_compl = compl[:-1]
    ident = extract_identifier2(nature_compl)
    if ident in ProofStatePO.dict_:    # check if PO already exists
        PO = ProofStatePO.dict_[ident]
        return(PO)
    nature_subtree = pre_nature_sub(nature)
##### treatment of bound variables
#    if nature in ["QUANT_∀", "QUANT_∃"]:
#        name_var = nature_compl
#        bound_vars_list.insert(0,name_var)
#        if debug:
#            print(f"bound_var_list: {bound_vars_list}")
#    elif nature == "VAR":  # PO is a bound variable
#        De_Bruijn_index = int(nature_compl)
#        latex_rep = bound_vars_list[De_Bruijn_index]
#        if debug:
#            print(f"VAR{De_Bruijn_index}: {latex_rep}")
####
    arguments = PO_dict["arguments"]
#### creation of children PO
    args = []
#    if nature != "PROP_IMPLIES":
    for arg in arguments:
        arg_PO = create_anPO(arg, debug)
        args.append(arg_PO)
#### Nature subtree : special cases
    if nature == "APPLICATION" and  args[0].nature == "FUNCTION":
        nature_subtree = args[-1].nature_subtree
        nature = "APPLICATION_FUNCTION"
##### treatment of bound variables
    assert(ident == "" or nature == "LOCAL_CONSTANT")
    if nature == "LOCAL_CONSTANT":  #  bound variable
        pass
#        nature
#        nature_compl
#        nature_subtree
#        args
#        latex_rep
#        lean_identifier
#        Lean_name
#        PO = BoundVarPO()

# obsolete
#        elif nature == "MINUS" and args[0].nature_subtree == "SET":
#                nature_subtree = "SET"
#                nature = "SET_COMPLEMENT"
#        elif nature == "LOCAL_CONSTANT" and 
#    else:                               # IMPLIES special case for bound vars
#        arg0 = arguments[0]
#        arg0_PO = create_anPO(arg0, bound_vars_list, debug)
#        bound_vars_list.insert(0,"")
#        if debug:
#            print(f"bound_var_list: {bound_vars_list}")
#        arg1 = arguments[1]
#        arg1_PO = create_anPO(arg1, bound_vars_list, debug)
#        args = [arg0_PO, arg1_PO]
####
    if debug:
        print("nature_pre_subtree:", nature_subtree)
    PO = AnonymousPO(nature, nature_compl, nature_subtree, args, latex_rep)
    return(PO)
    

def pre_nature_sub(nature):
    #nature = self.nature
    if nature in  ["FUNCTION", "NUMBER", "TYPE_NUMBER", "PROP"] \
        or nature in PropObj.nature_leaves_list:
        return(nature)        
    prefix = extract_nature_subtree(nature)
    if prefix in ["QUANT", "PROP"]:
        return("PROP")
    elif prefix == "SET":
        return("SET")
    return("unknown")    
# APPLICATION : nature_sub = recursively nature_sub of last arg
# VAR ? CONSTANT ? LOCAL_CONSTANT ?



###########################
# String extraction tools #
###########################

#def extract_nature_compl(string: str):
#    str1 = "["
#    str2 = "]"
#    return(extract(string, str1, str2))
    
def extract_nature_subtree(string: str):
    return(extract(string, "", "_"))

def extract_identifier1(string: str):
    str1 = "identifier:"
    str2 = "]"
    return(extract(string,str1,str2))

def extract_identifier2(string: str):
    str1 = "identifier:"
    str2 = ""
    return(extract(string,str1,str2))
    
def extract_pp_type(string: str):
    str1 = "pp_type:"
    str2 = "]"
    return(extract(string,str1,str2))

def extract_name(string: str):
    str1 = "name:"
    str2 = "/ident"
    return(extract(string,str1,str2))

def extract_num_var(string: str):
    str1 = "VAR["
    str2 = "]"
    return(int(extract(string,str1,str2)))  # Integer !!

def extract(string:str, str1:str, str2=""): 
    if str1 == "":
        pos1 = 0
    else:
        pos1 = string.find(str1)
    if str2 =="":
        pos2 = len(string)    
    else:
        pos2 = string.find(str2,pos1)
    if pos1 != -1 and pos2 != -1:
        str_extr = string[pos1+len(str1):pos2]
    else: str_extr = ""
    return(str_extr)
    

#essai
if __name__ == '__main__':
    debug = True
    
