#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 14:28:37 2020

@author: leroux
"""

"""
Take the result of Lean's tactic "Context_analysis", and process it to extract 
the mathematical content.
"""
from dataclasses import dataclass
import analysis2 as analysis

equal_sep = "+=+ "


@dataclass
class PropObj:
    is_prop: bool
    identifier: str
    lean_pp: str
    genus: str
    arguments: dict
    latex: str
    
    dico={} #dictionary (identifier,prop_obj)
    
    
def process_context(context_analysis: str):
    context_list = context_analysis.splitlines()
    if context_analysis.startswith("context"):
        del(context_list[0])
    prop_obj_list = [] #liste locale, ne pas confondre avec la liste  globale de la class PropObj
    for prop_obj_str in context_list:
        prop_obj = prop_obj_create(prop_obj_str)
        prop_obj_list.append(prop_obj)
    # A COMPLETER        
        
    return(prop_obj_list)
    



    
def prop_obj_create(prop_obj_str:str):
    """
    take a string from context_analysis and turn it into a mathematical object
    or proposition, an instance of the class PropObj. 
    This version assume that all atomis objects on which
    this new object is based have already been defined (this seems to be OK
    with the way Lean orders the objects)
    prop_obj_str is assumed to have format 
    %%head = %%tail where = is defined in equal_sep
    """
    head, _, tail = prop_obj_str.partition(equal_sep)
    # extract info from the head
    identifier = extract_identifier(head)
    is_prop = head.startswith("PROP")
    lean_pp = extract_lean_pp(head)
    # extract genus and arguments from the tail
    tree = analysis.lean_expr_grammar.parse(tail)
    prop_obj_list = analysis.LeanExprVisitor().visit(tree)
    if len(prop_obj_list) != 1: print("ERR: plus d'un objet")  # test à modifier
    genus = prop_obj_list[0]["name"]
    arguments = []
    for arg in prop_obj_list[0]["arguments"]:
        prop_obj = prop_obj_create2(arg)
        arguments.append(prop_obj)        

    latex = lean_pp  #provisoire 

    if identifier not in PropObj.dico:
        prop_obj = PropObj(is_prop, identifier, lean_pp, genus, arguments, latex)
        if identifier !="":
            PropObj.dico[identifier]=prop_obj # add to list
    else:  # object already exists
        prop_obj = PropObj.dico[identifier]
    return(prop_obj)

def prop_obj_create2(prop_obj_dict: dict): 
    """
    For sub-objects
    """
    genus = prop_obj_dict["name"]
    lean_pp = extract_lean_pp(genus)
    is_prop = None
    identifier = extract_identifier(genus)
    
    arguments = prop_obj_dict["arguments"]
    arg_po_list = []
    for arg in arguments:
        arg_prop_obj = prop_obj_create2(arg)
        arg_po_list.append(arg_prop_obj)
    
    latex = "" # provisoire
  
    if identifier not in PropObj.dico:
        prop_obj = PropObj(is_prop, identifier, lean_pp, genus, arg_po_list, latex)
        if identifier !="":
            PropObj.dico[identifier]=prop_obj # add to list
    else:  # object already exists
        prop_obj = PropObj.dico[identifier]
    return(prop_obj)
    

def extract_identifier(name:str):
    """
    Assuming name contains something like "identifieur:0._fresh.9756.178226",
    extract the useful part "9756.178226"
    """
    pos = name.find("0._fresh.")
    if  pos != -1:
        length = len("0._fresh.")
        ident = name[pos+length:pos+length+11]
    else: ident = ""
    return(ident)

def extract_lean_pp(name:str):
    """
    Assuming name contains something like "pp:***/ident",
    extract the useful part "***"
    which is the pretty name of the object in Lean
    """
    pos1 = name.find("pp:")
    pos2 = name.find("/ident",pos1)
    if pos1 != -1 and pos2 != -1:
        lean_pp = name[pos1+len("pp:"):pos2]
    else: lean_pp = ""
    return(lean_pp)


#essai
if __name__ == '__main__':
    essai1 = """context:
OBJET[LOCAL_CONSTANT[pp:X/identifieur:0._fresh.9730.128210]]+=+ TYPE
OBJET[LOCAL_CONSTANT[pp:Y/identifieur:0._fresh.9730.128211]]+=+ TYPE
OBJET[LOCAL_CONSTANT[pp:_inst_1/identifieur:0._fresh.9730.128212]]+=+ META_APPLICATION+(+CONSTANT[espace_metrique]+,+ LOCAL_CONSTANT[pp:X/identifieur:0._fresh.9730.128210]+)+
OBJET[LOCAL_CONSTANT[pp:_inst_2/identifieur:0._fresh.9730.128213]]+=+ META_APPLICATION+(+CONSTANT[espace_metrique]+,+ LOCAL_CONSTANT[pp:Y/identifieur:0._fresh.9730.128211]+)+
OBJET[LOCAL_CONSTANT[pp:f/identifieur:0._fresh.9730.128216]]+=+ FONCTION+(+LOCAL_CONSTANT[pp:X/identifieur:0._fresh.9730.128210]+,+ LOCAL_CONSTANT[pp:Y/identifieur:0._fresh.9730.128211]+)+
PROPRIETE[LOCAL_CONSTANT[pp:cont/identifieur:0._fresh.9737.148668]]+=+ META_APPLICATION+(+META_APPLICATION+(+META_APPLICATION+(+META_APPLICATION+(+META_APPLICATION+(+CONSTANT[continue]+,+ LOCAL_CONSTANT[pp:X/identifieur:0._fresh.9730.128210]+)++,+ LOCAL_CONSTANT[pp:Y/identifieur:0._fresh.9730.128211]+)++,+ LOCAL_CONSTANT[pp:_inst_1/identifieur:0._fresh.9730.128212]+)++,+ LOCAL_CONSTANT[pp:_inst_2/identifieur:0._fresh.9730.128213]+)++,+ LOCAL_CONSTANT[pp:f/identifieur:0._fresh.9730.128216]+)+
OBJET[LOCAL_CONSTANT[pp:O/identifieur:0._fresh.9737.148670]]+=+ SOUS-ENSEMBLE+(+LOCAL_CONSTANT[pp:Y/identifieur:0._fresh.9730.128211]+)+
PROPRIETE[LOCAL_CONSTANT[pp:O_ouvert/identifieur:0._fresh.9737.148672]]+=+ META_APPLICATION+(+META_APPLICATION+(+META_APPLICATION+(+CONSTANT[ouvert]+,+ LOCAL_CONSTANT[pp:Y/identifieur:0._fresh.9730.128211]+)++,+ LOCAL_CONSTANT[pp:_inst_2/identifieur:0._fresh.9730.128213]+)++,+ LOCAL_CONSTANT[pp:O/identifieur:0._fresh.9737.148670]+)+
OBJET[LOCAL_CONSTANT[pp:x/identifieur:0._fresh.9737.148675]]+=+ LOCAL_CONSTANT[pp:X/identifieur:0._fresh.9730.128210]
PROPRIETE[LOCAL_CONSTANT[pp:x_dans_reciproque/identifieur:0._fresh.9737.148710]]+=+ APPARTIENT+(+META_APPLICATION+(+LOCAL_CONSTANT[pp:f/identifieur:0._fresh.9730.128216]+,+ LOCAL_CONSTANT[pp:x/identifieur:0._fresh.9737.148675]+)++,+ LOCAL_CONSTANT[pp:O/identifieur:0._fresh.9737.148670]+)+
OBJET[LOCAL_CONSTANT[pp:ε/identifieur:0._fresh.9737.148787]]+=+ CONSTANT[real]
PROPRIETE[LOCAL_CONSTANT[pp:ε_positif/identifieur:0._fresh.9737.148800]]+=+ >+(+LOCAL_CONSTANT[pp:ε/identifieur:0._fresh.9737.148787]+,+ NOMBRE[0]+)+
PROPRIETE[LOCAL_CONSTANT[pp:boule_dans_O/identifieur:0._fresh.9737.148801]]+=+ INCLUS+(+META_APPLICATION+(+META_APPLICATION+(+META_APPLICATION+(+META_APPLICATION+(+CONSTANT[boule]+,+ LOCAL_CONSTANT[pp:Y/identifieur:0._fresh.9730.128211]+)++,+ LOCAL_CONSTANT[pp:_inst_2/identifieur:0._fresh.9730.128213]+)++,+ META_APPLICATION+(+LOCAL_CONSTANT[pp:f/identifieur:0._fresh.9730.128216]+,+ LOCAL_CONSTANT[pp:x/identifieur:0._fresh.9737.148675]+)++)++,+ LOCAL_CONSTANT[pp:ε/identifieur:0._fresh.9737.148787]+)++,+ LOCAL_CONSTANT[pp:O/identifieur:0._fresh.9737.148670]+)+
OBJET[LOCAL_CONSTANT[pp:δ/identifieur:0._fresh.9737.148847]]+=+ CONSTANT[real]
PROPRIETE[LOCAL_CONSTANT[pp:δ_positif/identifieur:0._fresh.9737.148860]]+=+ >+(+LOCAL_CONSTANT[pp:δ/identifieur:0._fresh.9737.148847]+,+ NOMBRE[0]+)+
PROPRIETE[LOCAL_CONSTANT[pp:H/identifieur:0._fresh.9737.148861]]+=+ QUELQUESOIT[x]+(+LOCAL_CONSTANT[pp:X/identifieur:0._fresh.9730.128210]+,+ IMPLIQUE+(+<+(+META_APPLICATION+(+META_APPLICATION+(+META_APPLICATION+(+META_APPLICATION+(+CONSTANT[dist']+,+ LOCAL_CONSTANT[pp:X/identifieur:0._fresh.9730.128210]+)++,+ LOCAL_CONSTANT[pp:_inst_1/identifieur:0._fresh.9730.128212]+)++,+ LOCAL_CONSTANT[pp:x/identifieur:0._fresh.9737.148675]+)++,+ VAR[0]+)++,+ LOCAL_CONSTANT[pp:δ/identifieur:0._fresh.9737.148847]+)++,+ <+(+META_APPLICATION+(+META_APPLICATION+(+META_APPLICATION+(+META_APPLICATION+(+CONSTANT[dist']+,+ LOCAL_CONSTANT[pp:Y/identifieur:0._fresh.9730.128211]+)++,+ LOCAL_CONSTANT[pp:_inst_2/identifieur:0._fresh.9730.128213]+)++,+ META_APPLICATION+(+LOCAL_CONSTANT[pp:f/identifieur:0._fresh.9730.128216]+,+ LOCAL_CONSTANT[pp:x/identifieur:0._fresh.9737.148675]+)++)++,+ META_APPLICATION+(+LOCAL_CONSTANT[pp:f/identifieur:0._fresh.9730.128216]+,+ VAR[1]+)++)++,+ LOCAL_CONSTANT[pp:ε/identifieur:0._fresh.9737.148787]+)++)++)+
OBJET[LOCAL_CONSTANT[pp:x'/identifieur:0._fresh.9737.148991]]+=+ LOCAL_CONSTANT[pp:X/identifieur:0._fresh.9730.128210]
PROPRIETE[LOCAL_CONSTANT[pp:hx'/identifieur:0._fresh.9737.148993]]+=+ APPARTIENT+(+LOCAL_CONSTANT[pp:x'/identifieur:0._fresh.9737.148991]+,+ META_APPLICATION+(+META_APPLICATION+(+META_APPLICATION+(+META_APPLICATION+(+CONSTANT[boule]+,+ LOCAL_CONSTANT[pp:X/identifieur:0._fresh.9730.128210]+)++,+ LOCAL_CONSTANT[pp:_inst_1/identifieur:0._fresh.9730.128212]+)++,+ LOCAL_CONSTANT[pp:x/identifieur:0._fresh.9737.148675]+)++,+ LOCAL_CONSTANT[pp:δ/identifieur:0._fresh.9737.148847]+)++)+"""
    liste = process_context(essai1)
    print(liste)
#    essai2 = liste[0]
    
          
          
          
          