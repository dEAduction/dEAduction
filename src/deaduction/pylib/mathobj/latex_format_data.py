#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 11:15:58 2020

@author: leroux
DESCRIPTION

Contain the data for processing PropObj into a latex representation

"""
import logging
import gettext

_ = gettext.gettext

log = logging.getLogger(__name__)

########################################################
# the following is useful for the function needs_paren #
########################################################
nature_leaves_list = ["PROP", "TYPE", "SET_UNIVERSE", "SET", "ELEMENT",
                      "FUNCTION", "SEQUENCE", "SET_FAMILY",
                      "TYPE_NUMBER", "NUMBER", "VAR", "SET_EMPTY"]


def subscript(structured_string):
    """
    recursive version, for strings to be displayed use global_subscript instead
    :param structured_string: list of sturctured string
    :return: the structured string in a subscript version if available,
    or the structured string unchanged if not,
    and a boolean is_subscriptable
    """
    normal_list = "0123456789" + "aeioruv"
    subscript_list = "₀₁₂₃₄₅₆₇₈₉" + "ₐₑᵢₒᵣᵤᵥ"
    #subscript_list = "₀₁₂₃₄₅₆₇₈₉" + "ₐₑᵢⱼₒᵣᵤᵥₓ"
    is_subscriptable = True
    if isinstance(structured_string, list):
        sub_list = []
        for item in structured_string:
            sub, bool = subscript(item)
            if not bool:  # not subscriptable
                return structured_string, False
            else:
                sub_list.append(sub)
        return sub_list, True

    # from now on structured_string is assumed to be a string
    for letter in structured_string:
        if letter not in normal_list:
            is_subscriptable = False
    if is_subscriptable:
        subscript_string = ""
        for l in structured_string:
            subscript_string += subscript_list[normal_list.index(l)]
    else:
        subscript_string = structured_string
    return subscript_string, is_subscriptable

def global_subscript(structured_string):
    sub, is_subscriptable = subscript(structured_string)
    if is_subscriptable:
        return sub
    else:
        return ['_'] + [sub]
        # [sub] necessary in case sub is an (unstructured) string


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
    if PO.children[0].node == "FUNCTION":  # the bound var is a function
        separator = ' : '
    else:
        if format_ == "latex":
            separator = r'\in'
        elif format_ == "utf8":
            separator = '∈'
    return [latex_symb + ' ' + a[1] + separator, a[0], ', ', a[2]]


def format_complement(latex_symb, a, PO, format_="latex"):
    if format_ == "latex":
        return [a[0], '^c']
    elif format_ == "utf8":
        return ['∁', a[0]]


def format_constant1(latex_symb, a, PO, format_="latex"):
    return [latex_symb]


def format_constant2(latex_symb, a, PO, format_="latex"):
    if "info" in PO.representation.keys():
        name = _(PO.representation["info"])
        return [latex_text(name, format_)]
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
        if PO.children[0].math_type.node in ["SET_FAMILY", "SEQUENCE"]:
            index = global_subscript([a[1]])
            return [PO.children[0].lean_data['name']] + index
    key = PO.children[0].representation['info']
    if key == 'composition':  # composition of functions
        #log.debug(f"composition of {a[-2]} and {a[-1]}")
        if format_ == 'latex':
            return [a[-2], r" \circ ", a[-1]]
        elif format_ == 'utf8':
            return [a[-2], '∘', a[-1]]
    else:
        # select children that are not Types
        pertinent_children = []
        pertinent_children_rep = []
        counter = 0  # the first child is always pertinent, we leave it aside
        for child in PO.children[1:]:
            counter +=1
            if hasattr(child, "math_type"):
                if child.math_type.node == 'TYPE':
                    continue
            pertinent_children.append(child)
            pertinent_children_rep.append(a[counter])
        # log.debug(f"pertinent children: {pertinent_children_rep}")
        # discriminate according of number of pertinent children
        if len(pertinent_children) == 0:  # CONSTANT, e.g. 'Identité'
            return a[0]
        if len(pertinent_children) == 1:  # ADJECTIVE, e.g. 'f is injective'
            adjective = a[0]
            noun = pertinent_children_rep[0]
            if format_ == "latex":
                return [r"\text{", noun, " " + _("is") + " ", adjective, r"}"]
            elif format_ == "utf8":
                return [noun, " " + _("is") + " ", adjective]
        else:
            return "??"


def format_lambda(latex_symb, a, PO, format_="latex"):
    """
    format for lambda expression,
    i.e. set families with explicit bound variable
    (lambda (i:I), E i)
    """
    ################
    # set families #
    ################
    # format LAMBDA(i, I, APPLICATION(E, i)) -> {E_i,i in I}
    # where E : SET_FAMILY
    [type_rep, var_rep, body_rep] = a
    # [type_, var_, body] = PO.children
    # if body.node == "APPLICATION":
    #     E = body.children[0]
    #     if E.node == "INSTANCE_OF_SET_FAMILY":
    #         # the bound var has already
    #         # been given a name in dEAduction
    #         var_name = E.children[0].representation[format_]
    #         return format_instance_set_family("", [var_name],
    #                                           E, format_)
    #     elif hasattr(E, "math_type"):
    #         if E.math_type.node == "SET_FAMILY":
    #             return format_instance_set_family("", [var_rep],
    #                                               E, format_)

    # TODO: adapt for functions and sequences
    # this is only for set families
    if format_ == "latex":
        return [r'\{', body_rep, ', ', var_rep, r' \in ', type_rep, r'\}']
    elif format_ == "utf8":
        return ['{', body_rep, ', ', var_rep, '∈', type_rep, '}']



def latex_text(string: str, format_="latex"):
    if format_ == "latex":
        string = r"\textsc{" + string + r"}"
    return string


def format_instance_set_family(latex_symb, children_rep, PO, format_="latex"):
    """
    :param children_rep: list or str, structured format of children
    :param PO: PropObj
    :return: None
    """
    name = PO.lean_data["name"]
    index_rep = children_rep[0]
    index_subscript_rep = global_subscript(index_rep)
    index_set_rep = PO.math_type.children[0].representation[format_]
    if format_ == "latex":
        rep = [r"\{", name,  r"_{", index_rep, r"}, ",
               index_rep, r"\in ", index_set_rep, r"\}"]
    elif format_ == "utf8":
        rep = ["{", name, index_subscript_rep, ", ",
               index_rep, "∈", index_set_rep, "}"]
    return rep

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
                    "LAMBDA": ("", format_lambda),
                    "PROP": (r"\text{ " + _("a proposition") + "}",
                             format_constant1),
                    "TYPE": (r" \text{ " + _("a set") + "} ",
                             format_constant1),
                    "SET": (r" \text{ " + _("a subset of") + " }",
                            format_n0),
                    "ELEMENT": (r" \text{ " + _("an element of") + " }",
                                format_n0),
                    "FUNCTION": (r" \to ", format_0n1),
                    "SEQUENCE": ("", ""),  # TODO: and also INSTANCE_OF_SEQ
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
                   "PROP_BELONGS": (r" ∈", format_0n1),
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
                   "LAMBDA": ("", format_lambda),
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