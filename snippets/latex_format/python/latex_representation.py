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
from PropObj2 import process_context
from latex_format_data import latex_structures, latex_formats, needs_paren


def compute_latex(PO, debug = True):
    """
    Compute a structured "latex representation" of a PO. Valid latex rep are
    recursively defined as:
    - lists of strings (in latex format)
    - lists of latex rep
    """
    a = []   # will be the list of the latex rep of the arguments
    nature = PO.nature
    i = -1
    for arg in PO.args:
        i += 1
        if arg.latex_rep == "":
            arg.latex_rep = compute_latex(arg, debug)
        lr = arg.latex_rep
        parentheses = needs_paren(PO, i)
        if parentheses:
            lr = ["(", lr, ")"]
        a.append(lr)
    latex_symb, format_scheme =  latex_structures[nature]
    latex_rep = eval(latex_formats[format_scheme])
    if debug:
        print(f"Je latex {PO.nature}: {latex_rep}")
    return(latex_rep)


def latex_join(latex_rep, debug = True):
    """
    turn a (structured) latex representation into a latex string
    """
    latex_str = ""
    for lr in latex_rep:
        if type(lr) is list:
            lr = latex_join(lr)
        latex_str += lr
    if debug:
        print("string:", latex_str)
    return(latex_str)    
    











#essai
if __name__ == '__main__':
# Ne marche pas : SUBSET est OK pour un ProofStatePO mais pas dans un anPO.
# FUNCTION(I, SUBSET(X)) qui signifie fonction de I dans les 
# sous-ensembles de X, nécessitera un traitement spécial pour obtenir
# la notation usuelle "E indice i"
    essai_inter_qcq = """
    """
    essai_vide = """context:
OBJECT[LOCAL_CONSTANT[name:X/identifier:0._fresh.2080.4097] ¿= TYPE
OBJECT[LOCAL_CONSTANT[name:A/identifier:0._fresh.2080.4098] ¿= SET¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.2080.4097]¿)
OBJECT[LOCAL_CONSTANT[name:B/identifier:0._fresh.2080.4100] ¿= SET¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.2080.4097]¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.2077.3082]/pp_type: A ⊆ B ↔ B \ A = ∅] ¿= PROP_IFF¿(PROP_INCLUDED¿(LOCAL_CONSTANT[name:A/identifier:0._fresh.2080.4098]¿, LOCAL_CONSTANT[name:B/identifier:0._fresh.2080.4100]¿)¿, PROP_EQUAL¿(SET_SYM_DIFF¿(LOCAL_CONSTANT[name:B/identifier:0._fresh.2080.4100]¿, LOCAL_CONSTANT[name:A/identifier:0._fresh.2080.4098]¿)¿, SET_EMPTY¿)¿)"""
    essai_qqs = """context:
OBJECT[LOCAL_CONSTANT[name:X/identifier:0._fresh.2297.10256] ¿= TYPE
OBJECT[LOCAL_CONSTANT[name:Y/identifier:0._fresh.2297.10257] ¿= TYPE
OBJECT[LOCAL_CONSTANT[name:f/identifier:0._fresh.2297.10259] ¿= FUNCTION¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.2297.10256]¿, LOCAL_CONSTANT[name:Y/identifier:0._fresh.2297.10257]¿)
OBJECT[LOCAL_CONSTANT[name:B/identifier:0._fresh.2297.10260] ¿= SET¿(LOCAL_CONSTANT[name:Y/identifier:0._fresh.2297.10257]¿)
OBJECT[LOCAL_CONSTANT[name:B'/identifier:0._fresh.2297.10262] ¿= SET¿(LOCAL_CONSTANT[name:Y/identifier:0._fresh.2297.10257]¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.2300.17601]/pp_type: ∀ ⦃x : X⦄, x ∈ (f⁻¹⟮B ∪ B'⟯) → x ∈ f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯)] ¿= QUANT_∀[x]¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.2297.10256]¿, PROP_IMPLIES¿(PROP_BELONGS¿(VAR[0]¿, SET_INVERSE¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.2297.10259]¿, SET_UNION¿(LOCAL_CONSTANT[name:B/identifier:0._fresh.2297.10260]¿, LOCAL_CONSTANT[name:B'/identifier:0._fresh.2297.10262]¿)¿)¿)¿, PROP_BELONGS¿(VAR[1]¿, SET_UNION¿(SET_INVERSE¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.2297.10259]¿, LOCAL_CONSTANT[name:B/identifier:0._fresh.2297.10260]¿)¿, SET_INVERSE¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.2297.10259]¿, LOCAL_CONSTANT[name:B'/identifier:0._fresh.2297.10262]¿)¿)¿)¿)¿)"""       
    essai_exists = """context:
OBJECT[LOCAL_CONSTANT[name:X/identifier:0._fresh.23.34034] ¿= TYPE
OBJECT[LOCAL_CONSTANT[name:A/identifier:0._fresh.23.34036] ¿= SET¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.23.34034]¿)
OBJECT[LOCAL_CONSTANT[name:A'/identifier:0._fresh.23.34039] ¿= SET¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.23.34034]¿)
OBJECT[LOCAL_CONSTANT[name:Y/identifier:0._fresh.23.34042] ¿= TYPE
OBJECT[LOCAL_CONSTANT[name:f/identifier:0._fresh.23.34045] ¿= FUNCTION¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.23.34034]¿, LOCAL_CONSTANT[name:Y/identifier:0._fresh.23.34042]¿)
OBJECT[LOCAL_CONSTANT[name:b/identifier:0._fresh.24.15207] ¿= LOCAL_CONSTANT[name:Y/identifier:0._fresh.23.34042]
PROPERTY[LOCAL_CONSTANT[name:H/identifier:0._fresh.24.15232]/pp_type: ∃ (a : X), a ∈ A ∩ A' ∧ f a = b] ¿= QUANT_∃[a]¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.23.34034]¿, PROP_AND¿(PROP_BELONGS¿(VAR[0]¿, SET_INTER¿(LOCAL_CONSTANT[name:A/identifier:0._fresh.23.34036]¿, LOCAL_CONSTANT[name:A'/identifier:0._fresh.23.34039]¿)¿)¿, PROP_EQUAL¿(APPLICATION¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.23.34045]¿, VAR[0]¿)¿, LOCAL_CONSTANT[name:b/identifier:0._fresh.24.15207]¿)¿)¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.24.15237]/pp_type: b ∈ f⟮A⟯ ∩ (f⟮A'⟯)] ¿= PROP_BELONGS¿(LOCAL_CONSTANT[name:b/identifier:0._fresh.24.15207]¿, SET_INTER¿(SET_IMAGE¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.23.34045]¿, LOCAL_CONSTANT[name:A/identifier:0._fresh.23.34036]¿)¿, SET_IMAGE¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.23.34045]¿, LOCAL_CONSTANT[name:A'/identifier:0._fresh.23.34039]¿)¿)¿)"""
    essai_diff_sym = """context:
OBJECT[LOCAL_CONSTANT[name:X/identifier:0._fresh.1373.44476] ¿= TYPE
OBJECT[LOCAL_CONSTANT[name:A/identifier:0._fresh.1373.44477] ¿= SET¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.1373.44476]¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.1374.48675]/pp_type: set.univ \ (set.univ \ A) = A] ¿= PROP_EQUAL¿(SET_SYM_DIFF¿(SET_UNIVERSE¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.1373.44476]¿)¿, SET_SYM_DIFF¿(SET_UNIVERSE¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.1373.44476]¿)¿, LOCAL_CONSTANT[name:A/identifier:0._fresh.1373.44477]¿)¿)¿, LOCAL_CONSTANT[name:A/identifier:0._fresh.1373.44477]¿)"""
    essai_compl = """context:
OBJECT[LOCAL_CONSTANT[name:X/identifier:0._fresh.2027.4564] ¿= TYPE
OBJECT[LOCAL_CONSTANT[name:A/identifier:0._fresh.2027.4566] ¿= SET¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.2027.4564]¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.2026.5981]/pp_type: A^c^c = A] ¿= PROP_EQUAL¿(SET_COMPLEMENT¿(SET_COMPLEMENT¿(LOCAL_CONSTANT[name:A/identifier:0._fresh.2027.4566]¿)¿)¿, LOCAL_CONSTANT[name:A/identifier:0._fresh.2027.4566]¿)"""
    essai_compl_union = """context:
OBJECT[LOCAL_CONSTANT[name:X/identifier:0._fresh.2045.41463] ¿= TYPE
OBJECT[LOCAL_CONSTANT[name:A/identifier:0._fresh.2045.41464] ¿= SET¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.2045.41463]¿)
OBJECT[LOCAL_CONSTANT[name:B/identifier:0._fresh.2045.41466] ¿= SET¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.2045.41463]¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.2046.23108]/pp_type: A ∪ B^c = A^c ∩ (B^c)] ¿= PROP_EQUAL¿(SET_COMPLEMENT¿(SET_UNION¿(LOCAL_CONSTANT[name:A/identifier:0._fresh.2045.41464]¿, LOCAL_CONSTANT[name:B/identifier:0._fresh.2045.41466]¿)¿)¿, SET_INTER¿(SET_COMPLEMENT¿(LOCAL_CONSTANT[name:A/identifier:0._fresh.2045.41464]¿)¿, SET_COMPLEMENT¿(LOCAL_CONSTANT[name:B/identifier:0._fresh.2045.41466]¿)¿)¿)"""
    essai_image_ens = """context:
OBJECT[LOCAL_CONSTANT[name:X/identifier:0._fresh.2101.8518] ¿= TYPE
OBJECT[LOCAL_CONSTANT[name:Y/identifier:0._fresh.2101.8520] ¿= TYPE
OBJECT[LOCAL_CONSTANT[name:f/identifier:0._fresh.2101.8523] ¿= FUNCTION¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.2101.8518]¿, LOCAL_CONSTANT[name:Y/identifier:0._fresh.2101.8520]¿)
OBJECT[LOCAL_CONSTANT[name:B/identifier:0._fresh.2101.8525] ¿= SET¿(LOCAL_CONSTANT[name:Y/identifier:0._fresh.2101.8520]¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.2104.9749]/pp_type: f⟮(f⁻¹⟮B⟯)⟯ ⊆ B] ¿= PROP_INCLUDED¿(SET_IMAGE¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.2101.8523]¿, SET_INVERSE¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.2101.8523]¿, LOCAL_CONSTANT[name:B/identifier:0._fresh.2101.8525]¿)¿)¿, LOCAL_CONSTANT[name:B/identifier:0._fresh.2101.8525]¿)"""
    essai_reciproque_union = """context:
OBJECT[LOCAL_CONSTANT[name:X/identifier:0._fresh.2103.19210] ¿= TYPE
OBJECT[LOCAL_CONSTANT[name:Y/identifier:0._fresh.2103.19212] ¿= TYPE
OBJECT[LOCAL_CONSTANT[name:f/identifier:0._fresh.2103.19215] ¿= FUNCTION¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.2103.19210]¿, LOCAL_CONSTANT[name:Y/identifier:0._fresh.2103.19212]¿)
OBJECT[LOCAL_CONSTANT[name:B/identifier:0._fresh.2103.19217] ¿= SET¿(LOCAL_CONSTANT[name:Y/identifier:0._fresh.2103.19212]¿)
OBJECT[LOCAL_CONSTANT[name:B'/identifier:0._fresh.2103.19220] ¿= SET¿(LOCAL_CONSTANT[name:Y/identifier:0._fresh.2103.19212]¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.2102.6532]/pp_type: ∀ ⦃x : X⦄, x ∈ (f⁻¹⟮B ∪ B'⟯) → x ∈ f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯)] ¿= QUANT_∀[x]¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.2103.19210]¿, PROP_IMPLIES¿(PROP_BELONGS¿(VAR[0]¿, SET_INVERSE¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.2103.19215]¿, SET_UNION¿(LOCAL_CONSTANT[name:B/identifier:0._fresh.2103.19217]¿, LOCAL_CONSTANT[name:B'/identifier:0._fresh.2103.19220]¿)¿)¿)¿, PROP_BELONGS¿(VAR[1]¿, SET_UNION¿(SET_INVERSE¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.2103.19215]¿, LOCAL_CONSTANT[name:B/identifier:0._fresh.2103.19217]¿)¿, SET_INVERSE¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.2103.19215]¿, LOCAL_CONSTANT[name:B'/identifier:0._fresh.2103.19220]¿)¿)¿)¿)¿)
PROPERTY[METAVAR[_mlocal._fresh.2102.6517]/pp_type: f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯) ⊆ (f⁻¹⟮B ∪ B'⟯)] ¿= PROP_INCLUDED¿(SET_UNION¿(SET_INVERSE¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.2103.19215]¿, LOCAL_CONSTANT[name:B/identifier:0._fresh.2103.19217]¿)¿, SET_INVERSE¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.2103.19215]¿, LOCAL_CONSTANT[name:B'/identifier:0._fresh.2103.19220]¿)¿)¿, SET_INVERSE¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.2103.19215]¿, SET_UNION¿(LOCAL_CONSTANT[name:B/identifier:0._fresh.2103.19217]¿, LOCAL_CONSTANT[name:B'/identifier:0._fresh.2103.19220]¿)¿)¿)"""
    essai_inter_union = """context:
OBJECT[LOCAL_CONSTANT[name:X/identifier:0._fresh.2552.7048] ¿= TYPE
OBJECT[LOCAL_CONSTANT[name:A/identifier:0._fresh.2552.7050] ¿= SET¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.2552.7048]¿)
OBJECT[LOCAL_CONSTANT[name:B/identifier:0._fresh.2552.7053] ¿= SET¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.2552.7048]¿)
OBJECT[LOCAL_CONSTANT[name:C/identifier:0._fresh.2552.7056] ¿= SET¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.2552.7048]¿)
OBJECT[LOCAL_CONSTANT[name:a/identifier:0._fresh.2554.2408] ¿= LOCAL_CONSTANT[name:X/identifier:0._fresh.2552.7048]
PROPERTY[LOCAL_CONSTANT[name:HA/identifier:0._fresh.2554.2441]/pp_type: a ∈ A] ¿= PROP_BELONGS¿(LOCAL_CONSTANT[name:a/identifier:0._fresh.2554.2408]¿, LOCAL_CONSTANT[name:A/identifier:0._fresh.2552.7050]¿)
PROPERTY[LOCAL_CONSTANT[name:HB/identifier:0._fresh.2554.2442]/pp_type: a ∈ B ∪ C] ¿= PROP_BELONGS¿(LOCAL_CONSTANT[name:a/identifier:0._fresh.2554.2408]¿, SET_UNION¿(LOCAL_CONSTANT[name:B/identifier:0._fresh.2552.7053]¿, LOCAL_CONSTANT[name:C/identifier:0._fresh.2552.7056]¿)¿)
goals:
PROPERTY[METAVAR[_mlocal._fresh.2554.2443]/pp_type: a ∈ A ∩ B ∪ A ∩ C] ¿= PROP_BELONGS¿(LOCAL_CONSTANT[name:a/identifier:0._fresh.2554.2408]¿, SET_UNION¿(SET_INTER¿(LOCAL_CONSTANT[name:A/identifier:0._fresh.2552.7050]¿, LOCAL_CONSTANT[name:B/identifier:0._fresh.2552.7053]¿)¿, SET_INTER¿(LOCAL_CONSTANT[name:A/identifier:0._fresh.2552.7050]¿, LOCAL_CONSTANT[name:C/identifier:0._fresh.2552.7056]¿)¿)¿)
PROPERTY[METAVAR[_mlocal._fresh.2554.2382]/pp_type: A ∩ B ∪ A ∩ C ⊆ A ∩ (B ∪ C)] ¿= PROP_INCLUDED¿(SET_UNION¿(SET_INTER¿(LOCAL_CONSTANT[name:A/identifier:0._fresh.2552.7050]¿, LOCAL_CONSTANT[name:B/identifier:0._fresh.2552.7053]¿)¿, SET_INTER¿(LOCAL_CONSTANT[name:A/identifier:0._fresh.2552.7050]¿, LOCAL_CONSTANT[name:C/identifier:0._fresh.2552.7056]¿)¿)¿, SET_INTER¿(LOCAL_CONSTANT[name:A/identifier:0._fresh.2552.7050]¿, SET_UNION¿(LOCAL_CONSTANT[name:B/identifier:0._fresh.2552.7053]¿, LOCAL_CONSTANT[name:C/identifier:0._fresh.2552.7056]¿)¿)¿)"""
    debug = True
    essai = essai_inter_union
    liste = process_context(essai, debug)
#    print(liste)
    print("")
    for pfPO in liste:
        pfPO.latex_type = compute_latex(pfPO, debug)
        pfPO.latex_type_str = latex_join(pfPO.latex_type, debug)
        print("-------")
    for pfPO in liste:    
        print(f"{pfPO.latex_rep} : {pfPO.latex_type}")
        print(f"assemblé :  {pfPO.latex_type_str}")
    
          
       
