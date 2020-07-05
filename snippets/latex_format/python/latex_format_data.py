#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 11:15:58 2020

@author: leroux
DESCRIPTION

Contain the data for processing PropObj into a latex representation

"""
from PropObj2 import PropObj, ProofStatePO

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
                 "quantifiers": "[latex_symb + ' ' + a[0] + ' \in ', a[1], ', ', a[2]]",
                 "var": "[PO.nature_compl]",  # OUT OF DATE
                 "complement": "[a[0], '^c']"}


def format_constant(latex_symb, a, PO):
    return [latex_symb]


def format_arg0(latex_symb, a, PO):
    return [a[0]]


def format_n0(latex_symb, a, PO):
    return [latex_symb, a[0]]


def format_0n1(latex_symb, a, PO):
    return [a[0], latex_symb, a[1]]


def format_name(latex_symb, a, PO):
    return [PO.lean_data["name"]]


def format_app_function(latex_symb, a, PO):
    return [a[0], '(', a[1], ')']


def format_app_inverse(latex_symb, a, PO):
    return [a[0], '^{-1}(', a[1], ')']


def format_quantifiers(latex_symb, a, PO):
# mind that the variable a[1] comes AFTER the type a[0] in quantifiers
    return [latex_symb + ' ' + a[1] + ' \in ', a[0], ', ', a[2]]


def format_complement(latex_symb, a, PO):
    return [a[0], '^c']


# dict nature -> (latex symbol, format name)
latex_structures = {"PROP_AND": (r" \text{{ ET }} ", format_0n1),   # logics
                    "PROP_OR": (r" \text{{ OU }} ", format_0n1),
                    "PROP_IFF": (r" \Leftrightarrow ", format_0n1),
                    "PROP_NOT": (r" \text{{NON }} ", format_n0),
                    "PROP_IMPLIES": (r" \Rightarrow ", format_0n1),
                    "QUANT_∀": (r"\forall ", format_quantifiers),
                    "QUANT_∃": (r"\exists ", format_quantifiers),
                    "PROP_∃": ("", ""),
                    "SET_INTER": (r" \cap ", format_0n1),       # set theory
                    "SET_UNION": (r" \cup ", format_0n1),
                    "SET_INTER+": ("", ""),
                    "SET_UNION+": ("", ""),
                    "PROP_INCLUDED": (r" \subset ", format_0n1),
                    "PROP_BELONGS": (r" \in ", format_0n1),
                    "SET_SYM_DIFF": (r" \backslash ", format_0n1),
                    "SET_COMPLEMENT": (r"", "complement"),
                    "SET_UNIVERSE": ("", format_arg0),
                    "SET_EMPTY": (r" \emptyset ", format_constant),
                    "SET_IMAGE": ("", format_app_function),
                    "SET_INVERSE": ("", format_app_inverse),
                    "PROP_EQUAL": (" = ", format_0n1),
                    "PROP_EQUAL_NOT": ("", ""),
                    "PROP_<": ("<", format_0n1),
                    "PROP_>": (">", format_0n1),
                    "PROP_≤": ("≤", format_0n1),
                    "PROP_≥": ("≥", format_0n1),
                    "MINUS": ("-", format_n0),
                    "+": ("+", format_0n1),
                    "APPLICATION_FUNCTION": ("", format_app_function),
                    "VAR": ("", "var"),
                    "PROP": (r"\text{{ une proposition}", format_constant),
                    "TYPE": (r" \text{ un ensemble} ", format_constant),
                    "SET": (r" \text{ un sous-ensemble de } ", format_n0),
                    "ELEMENT": (r" \{{ un élément de }} ", format_n0),
                    "FUNCTION": (r" \to ", format_0n1),
                    "SEQUENCE": ("", ""),
                    "SET_FAMILY": ("", ""),
                    "TYPE_NUMBER[name:ℕ]": ("\mathbb{N}", format_constant),
                    "TYPE_NUMBER[name:ℝ]": ("\mathbb{R}", format_constant),
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
