#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 08:05:48 2020

@author: leroux

DESCRIPTION
Recursively compute the latex representation of ProofStatePO's instances,
using the latex formats specified in latex_format_data.
- compute_latex(PO) produces a latex representation of the PO with a tree
structure encoded by lists
- latex_join transforms this latex representation into a valid latex string
"""
from PropObj import process_context, ProofStatePO
from latex_format_data import latex_structures, latex_formats, needs_paren
from dataclasses import dataclass

import deaduction.pylib.logger as logger
import logging


def compute_latex(prop_obj):
    """
    Compute a structured "latex representation" of a prop_obj. Valid latex rep are
    recursively defined as:
    - lists of strings (in latex format)
    - lists of latex rep
    """
    log = logging.getLogger("Latex representation")
    a = []   # will be the list of the latex rep of the children
    node = prop_obj.node
    i = -1
    for arg in prop_obj.children:
        i += 1
        if arg.latex_rep == None:
            arg.latex_rep = compute_latex(arg)
        lr = arg.latex_rep
        parentheses = needs_paren(prop_obj, i)
        if parentheses:
            lr = ["(", lr, ")"]
        a.append(lr)
    latex_symb, format_scheme = latex_structures[node]
    latex_rep = format_scheme(latex_symb, a, prop_obj)
    log.info(f"Je latex {prop_obj.node}: {latex_rep}")
    return latex_rep


def latex_join(latex_rep):
    """
    turn a (structured) latex representation into a latex string
    """
    latex_str = ""
    for lr in latex_rep:
        if type(lr) is list:
            lr = latex_join(lr)
        latex_str += lr
#    log.debug("string:", latex_str)
    return (latex_str)


#essai
if __name__ == '__main__':

    # Ne marche pas : SUBSET est OK pour un ProofStatePO mais pas dans un anPO.
# FUNCTION(I, SUBSET(X)) qui signifie fonction de I dans les 
# sous-ensembles de X, nécessitera un traitement spécial pour obtenir
# la notation usuelle "E indice i"
    essai_inter_qcq = """
    """
    essai_vide = ""
    essai_qqs = ""
    essai_exists = ""
    essai_diff_sym = ""
    essai_compl = ""
    essai_compl_union = """context:
OBJECT[LOCAL_CONSTANT¿[name:X/identifier:0._fresh.13.11644¿]] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:A/identifier:0._fresh.13.11646¿]] ¿= SET¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.13.11644¿]¿)
OBJECT[LOCAL_CONSTANT¿[name:B/identifier:0._fresh.13.11649¿]] ¿= SET¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.13.11644¿]¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.13.12090]/pp_type: -(A ∪ B) = -A ∩ -B] ¿= PROP_EQUAL¿(MINUS¿(SET_UNION¿(LOCAL_CONSTANT¿[name:A/identifier:0._fresh.13.11646¿]¿, LOCAL_CONSTANT¿[name:B/identifier:0._fresh.13.11649¿]¿)¿)¿, SET_INTER¿(MINUS¿(LOCAL_CONSTANT¿[name:A/identifier:0._fresh.13.11646¿]¿)¿, MINUS¿(LOCAL_CONSTANT¿[name:B/identifier:0._fresh.13.11649¿]¿)¿)¿)"""
    essai_image_ens = """"""
    essai_reciproque_union = """context:
OBJECT[LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1112.20255¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.1112.20257¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1112.20260¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= FUNCTION¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1112.20255¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.1112.20257¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1112.20262¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.1112.20257¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.1112.20265¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.1112.20257¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.1217.17744]/pp_type: ∀ ⦃x : X⦄, x ∈ (f⁻¹⟮B ∪ B'⟯) → x ∈ f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯)] ¿= QUANT_∀¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1215.9868¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:x/identifier:_fresh.1217.17768¿]¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1215.9868¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, PROP_IMPLIES¿(PROP_BELONGS¿(LOCAL_CONSTANT¿[name:x/identifier:_fresh.1217.17768¿]¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1215.9868¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1215.9873¿]¿(CONSTANT¿[name:1/1¿]¿)¿, SET_UNION¿(LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1215.9875¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.1215.9878¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)¿, PROP_BELONGS¿(LOCAL_CONSTANT¿[name:x/identifier:_fresh.1217.17768¿]¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1215.9868¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, SET_UNION¿(SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1215.9873¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1215.9875¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1215.9873¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.1215.9878¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)¿)¿)
PROPERTY[METAVAR[_mlocal._fresh.1217.17729]/pp_type: f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯) ⊆ (f⁻¹⟮B ∪ B'⟯)] ¿= PROP_INCLUDED¿(SET_UNION¿(SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1215.9873¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1215.9875¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1215.9873¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.1215.9878¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.1215.9873¿]¿(CONSTANT¿[name:1/1¿]¿)¿, SET_UNION¿(LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1215.9875¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.1215.9878¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)"""
    essai_reciproque_union2 = """context:
OBJECT[LOCAL_CONSTANT¿[name:X/identifier:0._fresh.36.39518¿]] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.36.39519¿]] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:f/identifier:0._fresh.36.39521¿]] ¿= FUNCTION¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.36.39518¿]¿, LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.36.39519¿]¿)
OBJECT[LOCAL_CONSTANT¿[name:B/identifier:0._fresh.36.39522¿]] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.36.39519¿]¿)
OBJECT[LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.36.39524¿]] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.36.39519¿]¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.37.40379]/pp_type: ∀ ⦃x : X⦄, x ∈ (f⁻¹⟮B ∪ B'⟯) → x ∈ f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯)] ¿= QUANT_∀¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.36.39518¿]¿, LOCAL_CONSTANT¿[name:x/identifier:_fresh.37.40403¿]¿, PROP_IMPLIES¿(PROP_BELONGS¿(LOCAL_CONSTANT¿[name:x/identifier:_fresh.37.40403¿]¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.36.39521¿]¿, SET_UNION¿(LOCAL_CONSTANT¿[name:B/identifier:0._fresh.36.39522¿]¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.36.39524¿]¿)¿)¿)¿, PROP_BELONGS¿(LOCAL_CONSTANT¿[name:x/identifier:_fresh.37.40403¿]¿, SET_UNION¿(SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.36.39521¿]¿, LOCAL_CONSTANT¿[name:B/identifier:0._fresh.36.39522¿]¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.36.39521¿]¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.36.39524¿]¿)¿)¿)¿)¿)
PROPERTY[METAVAR[_mlocal._fresh.37.40364]/pp_type: f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯) ⊆ (f⁻¹⟮B ∪ B'⟯)] ¿= PROP_INCLUDED¿(SET_UNION¿(SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.36.39521¿]¿, LOCAL_CONSTANT¿[name:B/identifier:0._fresh.36.39522¿]¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.36.39521¿]¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.36.39524¿]¿)¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.36.39521¿]¿, SET_UNION¿(LOCAL_CONSTANT¿[name:B/identifier:0._fresh.36.39522¿]¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.36.39524¿]¿)¿)¿)"""
    essai_inter_union = """context:
OBJECT[LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1822.3863¿]] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1822.3865¿]] ¿= SET¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1822.3863¿]¿)
OBJECT[LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1822.3868¿]] ¿= SET¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1822.3863¿]¿)
OBJECT[LOCAL_CONSTANT¿[name:C/identifier:0._fresh.1822.3871¿]] ¿= SET¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.1822.3863¿]¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.1821.3074]/pp_type: A ∪ B ∩ C = (A ∪ B) ∩ (A ∪ C)] ¿= PROP_EQUAL¿(SET_UNION¿(LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1822.3865¿]¿, SET_INTER¿(LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1822.3868¿]¿, LOCAL_CONSTANT¿[name:C/identifier:0._fresh.1822.3871¿]¿)¿)¿, SET_INTER¿(SET_UNION¿(LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1822.3865¿]¿, LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1822.3868¿]¿)¿, SET_UNION¿(LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1822.3865¿]¿, LOCAL_CONSTANT¿[name:C/identifier:0._fresh.1822.3871¿]¿)¿)¿)
"""
    essai = essai_reciproque_union
    liste = process_context(essai)
    print(liste)
    print("")
    for pfprop_obj in liste:
        pfprop_obj.math_type.latex_rep = compute_latex(pfprop_obj.math_type)
#        pfprop_obj.latex_type_str = latex_join(pfprop_obj.latex_type)
        print("-------")
    for pfprop_obj in liste:
        print(f"{pfprop_obj.latex_rep} : {pfprop_obj.math_type.latex_rep}")
        print(f"assemblé :  {latex_join(pfprop_obj.math_type.latex_rep)}")
    print("List of math types:")
    i = 0
    for mt in ProofStatePO.math_types_list:
        print(f" {latex_join(mt.latex_rep)}: ",
              f"{[latex_join(PO.latex_rep) for PO in ProofStatePO.math_types_instances[i]]}")
        i += 1

       
