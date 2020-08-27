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
from deaduction.pylib.mathobj.give_name import give_local_name

_ = gettext.gettext

log = logging.getLogger(__name__)

########################################################
# the following is useful for the function needs_paren #
########################################################
nature_leaves_list = ["PROP", "TYPE", "SET_UNIVERSE", "SET", "ELEMENT",
                      "FUNCTION", "SEQUENCE", "SET_FAMILY",
                      "TYPE_NUMBER", "NUMBER", "VAR", "SET_EMPTY"]


def format_arg0(**kwargs):
    a = kwargs["children_rep"]
    return [a[0]]


def format_n0(**kwargs):
    symbol = kwargs["symbol"]
    a = kwargs["children_rep"]
    return [symbol, a[0]]


def format_n1(**kwargs):
    symbol = kwargs["symbol"]
    a = kwargs["children_rep"]
    return [symbol, a[1]]


def format_0n1(**kwargs):
    symbol = kwargs["symbol"]
    a = kwargs["children_rep"]
    return [a[0], symbol, a[1]]


def format_name(**kwargs):
    po = kwargs["po"]
    return [po.lean_data["name"]]


def format_app_function(**kwargs):
    """Used for the image of a set under a function"""
    children_rep = kwargs["children_rep"]
    return [children_rep[0], '(', children_rep[1], ')']


def format_app_inverse(**kwargs):
    format_ = kwargs["format_"]
    a = kwargs["children_rep"]
    if format_ == "latex":
        return [a[0], '^{-1}(', a[1], ')']
    elif format_ == "utf8":
        return [a[0], '⁻¹(', a[1], ')']


def format_quantifiers(**kwargs):
    symbol = kwargs["symbol"]
    format_ = kwargs["format_"]
    a = kwargs["children_rep"]
    po = kwargs["po"]
    # mind that the variable a[1] comes AFTER the type a[0] in quantifiers
    if po.children[0].node == "FUNCTION":  # the bound var is a function
        separator = ' : '
    else:
        if format_ == "latex":
            separator = r'\in'
        elif format_ == "utf8":
            separator = '∈'
    return [symbol + ' ' + a[1] + separator, a[0], ', ', a[2]]


def format_complement(**kwargs):
    """TODO: use type to find universe and use notation X \ E
    (type is not implemented yet when E is AnonymousPO)"""
    format_ = kwargs["format_"]
    a = kwargs["children_rep"]
    po = kwargs["po"]
    if format_ == "latex":
        return [a[0], '^c']
    elif format_ == "utf8":
        return ['∁', a[0]]


def format_constant1(**kwargs):
    symbol = kwargs["symbol"]
    return [symbol]


def format_constant2(**kwargs):
    format_ = kwargs["format_"]
    po = kwargs["po"]
    if "info" in po.representation.keys():
        name = _(po.representation["info"])
        return [latex_text(name, format_)]
    else:
        return [latex_text(po.node, format_)]


def general_format_application(**kwargs):
    """
This function includes for instance:
    "APPLICATION(f,x)" -> "f(x)" (application of a function)
    "APPLICATION(composition, g, f)" ->  "gf"   (composition of functions)
    "APPLICATION(injective, f)" -> "f is injective"

NB : Type arguments are ignored, e.g. "APPLICATION(composition, g, f)" is
actually "APPLICATION(composition, X,Y,Z, g, f)"
    """
    format_ = kwargs["format_"]
    children_rep = kwargs["children_rep"]
    po = kwargs["po"]
    children = po.children
    #####################################################
    # 1st case: application of a function to a variable #
    #####################################################
    # e.g. f(x), {E_i, i in I}, u_n
    if hasattr(children[0], "math_type"):
        if children[0].math_type.node == "FUNCTION":
            return format_app_function(**kwargs)
        if children[0].math_type.node in ["SET_FAMILY", "SEQUENCE"]:
            index = global_subscript([children_rep[1]])
            return [children[0].lean_data['name']] + index
    ######################################
    # 2nd case: composition of functions #
    ######################################
    if hasattr(children[0], "representation"):
        if "info" in children[0].representation.keys():
            key = children[0].representation['info']
            if key == 'composition' and len(children) > 5:
                # log.debug(f"composition of {a[-2]} and {a[-1]}")
                if format_ == 'latex':
                    f_circ_g =  [children_rep[4], r" \circ ", children_rep[5]]
                else:  # format_ == 'utf8':
                    f_circ_g =  [children_rep[4], '∘', children_rep[5]]
                if len(children) == 6:
                    return f_circ_g
                elif len(children) == 7:
                    # case of 'f \circ g (x)'
                    new_children_rep = [f_circ_g, children_rep[6]]
                    return format_app_function(children_rep=new_children_rep)
                else:
                    log.warning(f"Do not know how to display APP("
                                f"composition, ...) with more than 7 "
                                f"arguments")
                    return "***"
    ###############
    # other cases #
    ###############
    # first find the pertinent children
    # select children that are not Types
    pertinent_children = []
    pertinent_children_rep = []
    counter = 0  # the first child is always pertinent, we leave it aside
    for child in children[1:]:
        counter += 1
        if hasattr(child, "math_type"):
            if child.math_type.node == 'TYPE':
                continue
        pertinent_children.append(child)
        pertinent_children_rep.append(children_rep[counter])
    # log.debug(f"pertinent children: {pertinent_children_rep}")
    ##########################################################################
    # discriminate according of number of pertinent (i.e. not Type) children #
    ##########################################################################
    # no pertinent argument
    if len(pertinent_children) == 0:  # CONSTANT, e.g. 'Identité'
        return children_rep[0]
    # 1 pertinent argument
    if len(pertinent_children) == 1:  # ADJECTIVE, e.g. 'f is injective'
        adjective = children_rep[0]
        noun = pertinent_children_rep[0]
        if format_ == "latex":
            return [r"\text{", noun, " " + _("is") + " ", adjective, r"}"]
        elif format_ == "utf8":
            return [noun, " " + _("is") + " ", adjective]
    ###################################################
    # more than 1 pertinent argument: not implemented #
    ###################################################
    else:
        return "**"



def format_lambda(**kwargs):
    """
    format for lambda expression,
    i.e. set families with explicit bound variable
    lambda (i:I), E i)
    encoded by LAMBDA(I, i, APP(E, i))

    TODO: use math_type of body to chose
    between set_family, function or sequence !

    """
    format_ = kwargs["format_"]
    po = kwargs["po"]
    children_rep = kwargs["children_rep"]
    [type_rep, var_rep, body_rep] = children_rep
    # todo: this could fail, e.g. lambda (i:I), E
    body = po.children[2]  # = APPLICATION(f,x)
    f = body.children[0]
    if body.node == "APPLICATION" and hasattr(f, "math_type"):
        if f.math_type.node == "FUNCTION":
            kwargs["po"] = f
            kwargs["children_rep"] = []
            return format_local_constant(**kwargs)
        elif f.math_type.node == "SEQUENCE":
            return "**"  # TODO
    # presumed to be a set family
    if format_ == "latex":
        return [r'\{', body_rep, ', ', var_rep, r' \in ', type_rep, r'\}']
    else:  # format_ == utf8
        return ['{', body_rep, ', ', var_rep, '∈', type_rep, '}']

def format_name_index_1(**kwargs):
    format_ = kwargs["format_"]
    children_rep = kwargs["children_rep"]
    po = kwargs["po"]
    name = po.children[0].lean_data["name"]
    if format_ == "latex":
        return [name, '_', children_rep[1]]
    if format_ == "utf8":
        # TODO : put a[1] in subscript format
        return [name, '_', children_rep[1]]


def format_local_constant(**kwargs):
    format_ = kwargs["format_"]
    po = kwargs["po"]
    is_type_of_pfpo = kwargs["is_type_of_pfpo"]
    if is_type_of_pfpo:
        if po.math_type.node == "TYPE":
            name = po.lean_data["name"]
            return [latex_text(_("an element of") + " ", format_), name]
    if po.math_type.node == "SET_FAMILY":
        return instance_set_family(po, format_)
    elif po.math_type == "SEQUENCE":
        return "**"  # todo
    elif not hasattr(po, "representation") \
            or format_ not in po.representation.keys():
        return "***"
    representation = po.lean_data["name"]
    return representation


# the following is not called directly, but via format_local_constant
def instance_set_family(po, format_="latex"):
    """
    e.g. if E: I -> set X,
    then compute a good name for an index in I (e.g. 'i'),
    and display "{E_i, i in I}"

    WARNING: this bound variable is not referenced anywhere, in particular
    it will not appear in extract_local_vars.

    :param children_rep:
    :param po: PropObj
    :return: None
    """
    # first find a name for the bound var
    #log.debug("instance of set family")
    bound_var_type = po.math_type.children[0]
    index_name = give_local_name(math_type=bound_var_type,
                                 body=po)
    index_rep = index_name
    index_subscript_rep = global_subscript(index_rep)
    index_set_rep = po.math_type.children[0].representation[format_]
    name = po.lean_data["name"]
    if format_ == "latex":
        rep = [r"\{", name, r"_{", index_rep, r"}, ",
               index_rep, r"\in ", index_set_rep, r"\}"]
    else:
        rep = ["{", name, index_subscript_rep, ", ",
               index_rep, "∈", index_set_rep, "}"]
    return rep


def format_set(**kwargs):
    format_ = kwargs["format_"]
    children_rep = kwargs["children_rep"]
    is_type_of_pfpo = kwargs["is_type_of_pfpo"]
    if is_type_of_pfpo:
        text = latex_text(_("a subset of") + " ", format_)
        kwargs["symbol"] = text
        return format_n0(**kwargs)
    else:
        if format_ == "latex":
            return r"\cP(" + children_rep[0] + ")"
        else:
            return "P(" + children_rep[0] + ")"


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
                    "SET_COMPLEMENT": (r"", format_complement),
                    "SET_UNIVERSE": ("", format_arg0),
                    "SET_EMPTY": (r" \emptyset ", format_constant1),
                    "SET_IMAGE": ("", format_app_function),
                    "SET_INVERSE": ("", format_app_inverse),
                    "SET_FAMILY": (r"\text{" + _("a family of subsets of") +
                                   " }", format_n1),
                    #                    "INSTANCE_OF_SET_FAMILY": ("",
                    #                    format_instance_set_family),
                    #                    "APPLICATION_OF_SET_FAMILY": ("", format_name_index_1),
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
                    ##################
                    # GENERAL TYPES: #
                    ##################
                    "LOCAL_CONSTANT": ("", format_local_constant),
                    "APPLICATION": ("", general_format_application),
                    "LAMBDA": ("", format_lambda),
                    "PROP": (r"\text{ " + _("a proposition") + "}",
                             format_constant1),
                    "TYPE": (r" \text{ " + _("a set") + "} ",
                             format_constant1),
                    "SET": ("", format_set),
                    # "SET": (r" \text{ " + _("a subset of") + " }",
                    #         format_n0),
#                    "ELEMENT": (r" \text{ " + _("an element of") + " }",
#                                format_n0),
                    "FUNCTION": (r" \to ", format_0n1),
                    "SEQUENCE": ("", ""),  # TODO: and also instance of SEQ
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
                   "SET_INTER": (r" ⋂ ", format_0n1),  # set theory
                   "SET_UNION": (r" ⋃ ", format_0n1),
                   "SET_INTER+": ("∩", format_n0),
                   "SET_UNION+": ("∪", format_n0),
                   "SET_DIFF": (r" \\ ", format_0n1),
                   "SET_COMPLEMENT": (r"", format_complement),
                   "SET_UNIVERSE": ("", format_arg0),
                   "SET_EMPTY": (r" ∅ ", format_constant1),
                   "SET_IMAGE": ("", format_app_function),
                   "SET_INVERSE": ("", format_app_inverse),
                   "SET_FAMILY": (_("a family of subsets of") + " ",
                                  format_n1),
                   # "INSTANCE_OF_SET_FAMILY": ("", format_instance_set_family),
                   # "APPLICATION_OF_SET_FAMILY": ("", format_name_index_1),
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
                   ##################
                   # GENERAL TYPES: #
                   ##################
                   "LOCAL_CONSTANT": ("", format_local_constant),
                   "APPLICATION": ("", general_format_application),
                   "LAMBDA": ("", format_lambda),
                   "PROP": (" " + _("a proposition"), format_constant1),
                   "TYPE": (" " + _("a set"), format_constant1),
                   "SET": ("", format_set),
#                   (" " + _("a subset of "), format_n0),
#                   "ELEMENT": (" " + _("an element of") + " ", format_n0),
                   "FUNCTION": (" → ", format_0n1),
                   "SEQUENCE": ("", ""),
                   "TYPE_NUMBER[name:ℕ]": ("ℕ", format_constant1),
                   "TYPE_NUMBER[name:ℝ]": ("ℝ", format_constant1),
                   "NUMBER": ("", ""),
                   "CONSTANT": ("", format_constant2)
                   }


def latex_text(string: str, format_="latex"):
    if format_ == "latex":
        string = r"\textsc{" + string + r"}"
    return string


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
    # subscript_list = "₀₁₂₃₄₅₆₇₈₉" + "ₐₑᵢⱼₒᵣᵤᵥₓ"
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

# TODO A traiter : R, N ; NUMBER ; emptyset ; PROP_∃ ; SET_INTER+ ; SEQUENCE ;
# MINUS (n0 ou 0n1 selon le nb d'arguments)
# NB : two notations for complement :
# COMPLEMENT:
# A^c (lean) -> A^c
# set.univ \ A (lean) -> X \ A
# avoid notation - A
