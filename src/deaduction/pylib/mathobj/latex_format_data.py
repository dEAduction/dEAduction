#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 11:15:58 2020

@author: leroux
DESCRIPTION

Contain the data for processing PropObj into a latex representation

"""
import gettext
_ = gettext.gettext

########################################################
# the following is useful for the function needs_paren #
########################################################
nature_leaves_list = ["PROP", "TYPE", "SET_UNIVERSE", "SET", "ELEMENT",
                      "FUNCTION", "SEQUENCE", "SET_FAMILY",
                      "TYPE_NUMBER", "NUMBER", "VAR", "SET_EMPTY"]


def format_constant(latex_symb, a, PO, format="latex"):
    return [latex_symb]


def format_arg0(latex_symb, a, PO, format="latex"):
    return [a[0]]


def format_n0(latex_symb, a, PO, format="latex"):
    return [latex_symb, a[0]]


def format_0n1(latex_symb, a, PO, format="latex"):
    return [a[0], latex_symb, a[1]]


def format_name(latex_symb, a, PO, format="latex"):
    return [PO.lean_data["name"]]


def format_app_function(latex_symb, a, PO, format="latex"):
    return [a[0], '(', a[1], ')']


def format_app_inverse(latex_symb, a, PO, format="latex"):
    if format == "latex":
        return [a[0], '^{-1}(', a[1], ')']
    elif format == "utf8":
        return [a[0], '⁻¹(', a[1], ')']


def format_quantifiers(latex_symb, a, PO, format="latex"):
    # mind that the variable a[1] comes AFTER the type a[0] in quantifiers
    if format == "latex":
        return [latex_symb + ' ' + a[1] + ' \in ', a[0], ', ', a[2]]
    elif format == "utf8":
        return [latex_symb  + a[1] + ' ∈ ', a[0], ', ', a[2]]


def format_complement(latex_symb, a, PO, format="latex"):
    if format == "latex":
        return [a[0], '^c']
    elif format == "utf8":
        return [a[0], 'ᶜ']


# dict nature -> (latex symbol, format name)
##########
# LOGIC: #
##########
latex_structures = {"PROP_AND": (r" \text{{ " + _("AND") + " }} ", format_0n1),
                    "PROP_OR": (r" \text{{ " + _("OR") + " }} ", format_0n1),
                    "PROP_IFF": (r" \Leftrightarrow ", format_0n1),
                    "PROP_NOT": (r" \text{{" + _("NOT") + " }} ", format_n0),
                    "PROP_IMPLIES": (r" \Rightarrow ", format_0n1),
                    "QUANT_∀": (r"\forall ", format_quantifiers),
                    "QUANT_∃": (r"\exists ", format_quantifiers),
                    "PROP_∃": ("", ""),
                    ###############
                    # SET THEORY: #
                    ###############
                    "SET_INTER": (r" \cap ", format_0n1),  # set theory
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
                    ############
                    # NUMBERS: #
                    ############
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
                    ##################
                    # GENERAL TYPES: #
                    ##################
                    "PROP": (r"\text{{ " + _("a proposition") + "}",
                            format_constant),
                    "TYPE": (r" \text{ " + _("a set") + "} ",
                            format_constant),
                    "SET": (r" \text{ " + _("a subset of") + " } ",
                            format_n0),
                    "ELEMENT": (r" \{{ " + _("an element of") + " }} ",
                                format_n0),
                    "FUNCTION": (r" \to ", format_0n1),
                    "SEQUENCE": ("", ""),
                    "SET_FAMILY": ("", ""),
                    "TYPE_NUMBER[name:ℕ]": ("\mathbb{N}", format_constant),
                    "TYPE_NUMBER[name:ℝ]": ("\mathbb{R}", format_constant),
                    "NUMBER": ("", "")
                    }

utf8_structures = {"PROP_AND": (" " + _("AND") + " ", format_0n1),  # logic
                   "PROP_OR": (" " + _("OR") + " ", format_0n1),
                   "PROP_IFF": (" ⇔ ", format_0n1),
                   "PROP_NOT": (" " + _("NOT") + " ", format_n0),
                   "PROP_IMPLIES": (" ⇒ ", format_0n1),
                   "QUANT_∀": ("∀ ", format_quantifiers),
                   "QUANT_∃": ("∃ ", format_quantifiers),
                   "PROP_∃": ("", ""),
                   "SET_INTER": (r" ∩ ", format_0n1),  # set theory
                   "SET_UNION": (r" ∪ ", format_0n1),
                   "SET_INTER+": ("", ""),
                   "SET_UNION+": ("", ""),
                   "PROP_INCLUDED": (" ⊂ ", format_0n1),
                   "PROP_BELONGS": (r" ∈ ", format_0n1),
                   "SET_SYM_DIFF": (r" \\ ", format_0n1),
                   "SET_COMPLEMENT": (r"", "complement"),
                   "SET_UNIVERSE": ("", format_arg0),
                   "SET_EMPTY": (r" ∅ ", format_constant),
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
                   "PROP": (_(" a proposition"), format_constant),
                   "TYPE": (_(" a set"), format_constant),
                   "SET": (_(" a subset of "), format_n0),
                   "ELEMENT": (_(" an element of "), format_n0),
                   "FUNCTION": (" → ", format_0n1),
                   "SEQUENCE": ("", ""),
                   "SET_FAMILY": ("", ""),
                   "TYPE_NUMBER[name:ℕ]": ("ℕ", format_constant),
                   "TYPE_NUMBER[name:ℝ]": ("ℝ", format_constant),
                   "NUMBER": ("", "")
                   }

# TODO A traiter : R, N ; NUMBER ; emptyset ; PROP_∃ ; SET_INTER+ ; SEQUENCE ;
# MINUS (n0 ou 0n1 selon le nb d'arguments)
# NB : two notations for complement :
# COMPLEMENT:
# A^c (lean) -> A^c
# set.univ \ A (lean) -> X \ A
# avoid notation - A