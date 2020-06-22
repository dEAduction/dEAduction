#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 11:15:58 2020

@author: leroux
DESCRIPTION

Contain the data for processing PropObj into a latex representation

"""
from PropObj2 import PropObj

nature_leaves_list = ["PROP", "TYPE", "SET_UNIVERSE", "SET", "ELEMENT",
                      "FUNCTION", "SEQUENCE", "SET_FAMILY",
                      "TYPE_NUMBER", "NUMBER", "VAR", "SET_EMPTY"]

    
# dict format name -> format scheme
latex_formats = {"const": "[latex_symb]",
                 "arg0": "[a[0]]",
                 "n0": "[latex_symb, a[0]]",
                 "0n1": "[a[0], latex_symb, a[1]]",
                 "name": "[PO.lean_name]",
                 "app_function": "[a[0],  '(', a[1], ')']",
                 "app_inverse": "[a[0],  '^{-1}(', a[1],  ')']",
                 "quantifiers": "[latex_symb + ' ' + PO.nature_compl + ' \in ', a[0], ', ', a[1]]",
                 "var": "[PO.nature_compl]",
                 "complement": "[a[0], '^c']"}

# dict nature -> (latex symbol, format name)
latex_structures = {"PROP_AND": (r" \text{{ ET }} ", "0n1"),
                    "PROP_OR": (r" \text{{ OU }} ", "0n1"),
                    "PROP_IFF": (r" \Leftrightarrow ", "0n1"),
                    "PROP_NOT": (r" \text{{NON }} ", "n0"),
                    "PROP_IMPLIES": (r" \Rightarrow ", "0n1"),
                   "QUANT_∀": (r"\forall ", "quantifiers"),
                   "QUANT_∃": (r"\exists ", "quantifiers"),
                   "PROP_∃": ("", ""),
                   "SET_INTER": (r" \cap ", "0n1"),
                   "SET_UNION": (r" \cup ", "0n1"),
                   "SET_INTER+": ("", ""),
                   "SET_UNION+": ("", ""),
                   "PROP_INCLUDED": (r" \subset ", "0n1"),
                   "PROP_BELONGS": (r" \in ", "0n1"),
                   "SET_SYM_DIFF": (r" \backslash ", "0n1"),
                   "SET_COMPLEMENT": (r"", "complement"),
                   "SET_UNIVERSE": ("", "arg0"),
                   "SET_EMPTY": (r" \emptyset ", "const"),
                   "SET_IMAGE": ("", "app_function"),
                   "SET_INVERSE": ("", "app_inverse"),
                   "PROP_EQUAL": (" = ", "0n1"),
                   "PROP_EQUAL_NOT": ("", ""),
                   "PROP_<": ("<", "0n1"),
                   "PROP_>": (">", "0n1"),
                   "PROP_≤": ("≤", "0n1"),
                   "PROP_≥": ("≥", "0n1"),
                   "MINUS": ("", ""),
                   "+": ("+", "0n1"),
                   "APPLICATION_FUNCTION": ("", "app_function"),
                   "VAR": ("", "var"),
                    "PROP": (r"\text{{ une proposition}", "const"),
                    "TYPE": (r" \text{ un ensemble} ", "const"),
                    "SET": (r" \text{ un sous-ensemble de } ", "n0"),
                    "ELEMENT": (r" \{{ un élément de }} ", "n0"),
                    "FUNCTION": (r" \to ", "0n1"),
                    "SEQUENCE": ("", ""),
                    "SET_FAMILY": ("", ""),
                    "TYPE_NUMBER": ("", ""),
                    "NUMBER": ("", "")
                    }

# A traiter : R, N ; NUMBER ; emptyset ; PROP_∃ ; SET_INTER+ ; SEQUENCE ; 
# MINUS (n0 ou 0n1 selon le nb d'arguments)
# NB : two notations for complement :
# COMPLEMENT:
    # A^c (lean) -> A^c
    # set.univ \ A (lean) -> X \ A
    # avoid notation - A


# AJOUTER : tenir compte de la profondeur des parenthèses, 
# et utiliser \Biggl(\biggl(\Bigl(\bigl((x)\bigr)\Bigr)\biggr)\Biggr)
############# AFER
def needs_paren(parent:PropObj, child:int):
    """
    Decides if parentheses are needed around the child
    """
    b = True
    childPO = parent.args[child]
    pnat = parent.nature
    cnat = childPO.nature
    if childPO.args == []:
        b = False
    elif cnat in nature_leaves_list + \
        ["SET_IMAGE", "SET_INVERSE", "PROP_BELONGS", "PROP_EQUAL", 
         "PROP_INCLUDED"]:
        b = False             
    elif pnat in ["SET_IMAGE", "SET_INVERSE", "APPLICATION_FUNCTION",
                           "PROP_EQUAL", "PROP_INCLUDED", "PROP_BELONGS"]:
        b = False
    elif cnat == "SET_COMPLEMENT" and pnat != "SET_COMPLEMENT":
        b = False
    return(b)
