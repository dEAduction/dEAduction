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
import logging

log = logging.getLogger(__name__)

########################################################
# the following is useful for the function needs_paren #
########################################################
nature_leaves_list = ["PROP", "TYPE", "SET_UNIVERSE", "SET", "ELEMENT",
                      "FUNCTION", "SEQUENCE", "SET_FAMILY",
                      "TYPE_NUMBER", "NUMBER", "VAR", "SET_EMPTY"]

def subscript(string):
    subscript = str.maketrans("0123456789" + "aeijoruvx", "₀₁₂₃₄₅₆₇₈₉" +
                              "ₐₑᵢⱼₒᵣᵤᵥₓ")

    return string.translate(subscript)


def format_arg0(latex_symb, a, PO, format_="latex"):
    return [a[0]]


def format_n0(latex_symb, a, PO, format_="latex"):
    return [latex_symb, a[0]]

def format_n1(latex_symb, a, PO, format_="latex"):
    return [latex_symb, a[1]]


def format_0n1(latex_symb, a, PO, format_="latex"):
    return [a[0], latex_symb, a[1]]

def format_name(latex_symb, a, PO, format_="latex"):
    return [PO.lean_data["name"]]


def format_app_function(latex_symb, a, PO, format_="latex"):
    return [a[0], '(', a[1], ')']  # !! not used anymore !!


def format_app_inverse(latex_symb, a, PO, format_="latex"):
    if format_ == "latex":
        return [a[0], '^{-1}(', a[1], ')']
    elif format_ == "utf8":
        return [a[0], '⁻¹(', a[1], ')']


def format_quantifiers(latex_symb, a, PO, format_="latex"):
    # mind that the variable a[1] comes AFTER the type a[0] in quantifiers
    if format_ == "latex":
        return [latex_symb + ' ' + a[1] + ' \in ', a[0], ', ', a[2]]
    elif format_ == "utf8":
        return [latex_symb + a[1] + ' ∈ ', a[0], ', ', a[2]]


def format_complement(latex_symb, a, PO, format_="latex"):
    if format_ == "latex":
        return [a[0], '^c']
    elif format_ == "utf8":
        return [a[0], 'ᶜ']
    elif format_ == "utf8":
        return ['∁', a[0]]


def format_constant1(latex_symb, a, PO, format_="latex"):
    return [latex_symb]


def format_constant2(latex_symb, a, PO, format_="latex"):
    if "info" in PO.representation.keys():
        name = _(PO.representation["info"])
        return [latex_text(name)]
    else:
        return [latex_text(PO.node)]


# the following includes for instance:
# "f(x)" (application of a function)
# "gf"   (composition of functions)
# "f is injective"
def general_format_application(latex_symb, a, PO, format_="latex"):
    if hasattr(PO.children[0], "math_type"):
        if PO.children[0].math_type.node == "FUNCTION":
            return [a[0], '(', a[1], ')']
    key = PO.children[0].representation['info']
    if key == 'composition':  # composition of functions
        log.debug(f"composition of {a[-2]} and {a[-1]}")
        if format_ == 'latex':
            return [a[-2], r" \circ ", a[-1]]
        elif format_ == 'utf8':
            return [a[-2], '∘', a[-1]]
    elif key in ["injective", "surjective"]:  # adjective with one subject
        noun = a[-1]
        adjective = key
        if format_ == "latex":
            return [r"\text{" + noun + "" + " " + _("is") + " " + adjective +
                    r"}"]
        elif format_ == "utf8":
            return [noun + "" + " " + _("is") + " " + adjective]


def latex_text(string: str, format_="latex"):
    if format_ == "latex":
        string = r"\textsc{" + string + r"}"
    return string


def format_instance_set_family(latex_symb, children_rep, PO, format_="latex"):
    name = PO.lean_data["name"]
    index_rep = children_rep[0]
    index_subscript_rep = subscript(index_rep)
    index_set_rep = PO.math_type.children[0].representation[format_]
    if format_ == "latex":
        string = r"\{" + name + r"_{" + index_rep + r"}, " \
                 + index_rep + r"\in " + index_set_rep + r"\}"
    elif format_ == "utf8":
        string = ["{" + name + index_subscript_rep + ", " \
                  + index_rep + "∈" + index_set_rep + "}"]
    return string

def format_name_index_1(latex_symb, a, PO, format_="latex"):
    name = PO.children[0].lean_data["name"]
    if format_ == "latex":
        return [name, '_', a[1]]
    if format_ == "utf8":
        # TODO : put a[1] in subscript format
        return [name, '_', a[1]]

# dict nature -> (latex symbol, format name)
##########
# LOGIC: #
##########
latex_structures = {"PROP_AND": (r" \text{ " + _("AND") + " } ", format_0n1),
                    "PROP_OR": (r" \text{ " + _("OR") + " } ", format_0n1),
                    "PROP_FALSE": (r"\textsc{" + _("Contradiction") + "}",
                                   format_constant1),
                    "PROP_IFF": (r" \Leftrightarrow ", format_0n1),
                    "PROP_NOT": (r" \text{" + _("NOT") + " } ", format_n0),
                    "PROP_IMPLIES": (r" \Rightarrow ", format_0n1),
                    "QUANT_∀": (r"\forall ", format_quantifiers),
                    "QUANT_∃": (r"\exists ", format_quantifiers),
                    "PROP_∃": ("", ""),
                    ###############
                    # SET THEORY: #
                    ###############
                    "SET_INTER": (r" \cap ", format_0n1),
                    "SET_UNION": (r" \cup ", format_0n1),
                    "SET_INTER+": (r"\bigcap", format_n0),  # TODO: improve
                    "SET_UNION+": (r"\bigcup", format_n0),
                    "PROP_INCLUDED": (r" \subset ", format_0n1),
                    "PROP_BELONGS": (r" \in ", format_0n1),
                    "SET_DIFF": (r" \backslash ", format_0n1),
                    "SET_SYM_DIFF": (r" \backslash ", format_0n1),
                    "SET_COMPLEMENT": (r"", format_complement),
                    "SET_UNIVERSE": ("", format_arg0),
                    "SET_EMPTY": (r" \emptyset ", format_constant1),
                    "SET_IMAGE": ("", format_app_function),
                    "SET_INVERSE": ("", format_app_inverse),
                    "SET_FAMILY": (r"\text{ " + _("a family of subsets of") +
                                   " }", format_n1),
                    "INSTANCE_OF_SET_FAMILY": ("", format_instance_set_family),
                    "APPLICATION_OF_SET_FAMILY": ("", format_name_index_1),
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
                    "APPLICATION": ("", general_format_application),
                    "PROP": (r"\text{ " + _("a proposition") + "}",
                             format_constant1),
                    "TYPE": (r" \text{ " + _("a set") + "} ",
                             format_constant1),
                    "SET": (r" \text{ " + _("a subset of") + " }",
                            format_n0),
                    "ELEMENT": (r" \text{ " + _("an element of") + " }",
                                format_n0),
                    "FUNCTION": (r" \to ", format_0n1),
                    "SEQUENCE": ("", ""),
                    "TYPE_NUMBER[name:ℕ]": ("\mathbb{N}", format_constant1),
                    "TYPE_NUMBER[name:ℝ]": ("\mathbb{R}", format_constant1),
                    "NUMBER": ("", ""),
                    "CONSTANT": ("", format_constant2)
                    }

utf8_structures = {"PROP_AND": (" " + _("AND") + " ", format_0n1),  # logic
                   "PROP_OR": (" " + _("OR") + " ", format_0n1),
                   "PROP_FALSE": (_("Contradiction"), format_constant1),
                   "PROP_IFF": (" ⇔ ", format_0n1),
                   "PROP_NOT": (" " + _("NOT") + " ", format_n0),
                   "PROP_IMPLIES": (" ⇒ ", format_0n1),
                   "QUANT_∀": ("∀ ", format_quantifiers),
                   "QUANT_∃": ("∃ ", format_quantifiers),
                   "PROP_∃": ("", ""),
                   ###############
                   # SET THEORY: #
                   ###############
                   "PROP_INCLUDED": (" ⊂ ", format_0n1),
                   "PROP_BELONGS": (r" ∈ ", format_0n1),
                   "SET_INTER": (r" ∩ ", format_0n1),  # set theory
                   "SET_UNION": (r" ∪ ", format_0n1),
                   "SET_INTER+": (" ∩", format_n0),
                   "SET_UNION+": (" ∪", format_n0),
                   "SET_DIFF": (r" \\ ", format_0n1),
                   "SET_COMPLEMENT": (r"", format_complement),
                   "SET_UNIVERSE": ("", format_arg0),
                   "SET_EMPTY": (r" ∅ ", format_constant1),
                   "SET_IMAGE": ("", format_app_function),
                   "SET_INVERSE": ("", format_app_inverse),
                   "SET_FAMILY": (" " + _("a family of subsets of") + " ",
                                  format_n1),
                   "INSTANCE_OF_SET_FAMILY": ("", format_instance_set_family),
                   "APPLICATION_OF_SET_FAMILY": ("", format_name_index_1),
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
                   "VAR": ("", "var"),
                   "APPLICATION": ("", general_format_application),
                   ##################
                   # GENERAL TYPES: #
                   ##################
                   "PROP": (" " + _("a proposition"), format_constant1),
                   "TYPE": (" " + _("a set"), format_constant1),
                   "SET": (" " + _("a subset of "), format_n0),
                   "ELEMENT": (" " + _("an element of "), format_n0),
                   "FUNCTION": (" → ", format_0n1),
                   "SEQUENCE": ("", ""),
                   "TYPE_NUMBER[name:ℕ]": ("ℕ", format_constant1),
                   "TYPE_NUMBER[name:ℝ]": ("ℝ", format_constant1),
                   "NUMBER": ("", ""),
                   "CONSTANT": ("", format_constant2)
                   }


# TODO A traiter : R, N ; NUMBER ; emptyset ; PROP_∃ ; SET_INTER+ ; SEQUENCE ;
# MINUS (n0 ou 0n1 selon le nb d'arguments)
# NB : two notations for complement :
# COMPLEMENT:
# A^c (lean) -> A^c
# set.univ \ A (lean) -> X \ A
# avoid notation - A