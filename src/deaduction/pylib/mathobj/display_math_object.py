#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 11:15:58 2020

@author: leroux
DESCRIPTION

Contain the data for processing PropObj into a latex representation

TODO: remove 'PROP' from node names, here and in Structures.lean.
"""
import logging
import gettext
import types

from deaduction.pylib.mathobj.give_name import give_local_name

_ = gettext.gettext

log = logging.getLogger(__name__)


def display_math_object(math_object, format_):
    """
    This function essentially looks for a shape in the format_from_node
    dictionary, and then pass the shape to the function
    display_math_object_from_shape
    which comutes the display.

    :param math_object:
    :param format_:
    :return:
    """
    log.debug(f"Computing math display of {math_object}")
    node = math_object.node
    if node in format_from_node.keys():
        shape = format_from_node['node']
        return display_math_object_from_shape(shape, math_object, format_)

    else:
        log.warning(f"display error: node {node} not in display_format")
        return ["****"]


def display_math_object_from_shape(shape, math_object, format_):
    """
    Replace each element of shape with its display.
        - numbers refer to children, and are replaced by the
            corresponding display,
        - strings are displayed as such for utf8, (see exceptions below)
        - functions are called

    Exceptions:
        - "_child#" code for subscript version of child number #

    :param shape:
    :param math_object:
    :param format_:
    :return:    a structured string, to be passed to list_string_join in order
                to get a fully displayable string
    """
    display_shape = []
    for item in shape:
        display_item = "**"
        if isinstance(item, types.FunctionType):
            display_item = item(math_object, format_)

        elif isinstance(item, int):
            if item < len(math_object.children):
                child = math_object.children[item]
                display_item = [display_math_object(child, format_)]
                if needs_paren(math_object, item):
                    display_item = ['('] + display_item + [')']
            else:  # keep the integer, this could be a pending parameter
                display_item = item
        elif isinstance(item, str):
            if item.startswith("_child"):
                number = int(item[len("_child"):])
                child = math_object.children[number]
                pre_display_item = display_math_object(child, format_)
                display_item = subscript(pre_display_item, format_)  # TODO
            else:
                display_item = text_to_latex(item, format_)

        display_shape.append(display_item)
    return display_shape


def needs_paren(parent, child_number: int) -> bool:
    """
    Decides if parentheses are needed around the child
    e.g. if PropObj.node = PROP.IFF then
    needs_paren(PropObj,i) will be set to True for i = 0, 1
    so that the display will be
    ( ... ) <=> ( ... )
    :param parent: MathObject
    :param child_number:
    :return:
    """
    child_prop_obj = parent.children[child_number]
    p_node = parent.node
    # if child_prop_obj.node == "LOCAL_CONSTANT":
    #     return False
    if not child_prop_obj.children:
        return False
    c_node = child_prop_obj.node
    if c_node in nature_leaves_list + \
            ["SET_IMAGE", "SET_INVERSE", "PROP_BELONGS", "PROP_EQUAL",
             "PROP_INCLUDED"]:
        return False
    elif p_node in ["SET_IMAGE", "SET_INVERSE",
                    "SET_UNION+", "SET_INTER+", "APPLICATION",
                    "PROP_EQUAL", "PROP_INCLUDED", "PROP_BELONGS", "LAMBDA"]:
        return False
    elif c_node == "SET_COMPLEMENT" and p_node != "SET_COMPLEMENT":
        return False
    return True


#########################################################################
#########################################################################
# Special display functions, called from display_math_object_from_shape #
# (see also the format_from_node dictionary)                            #
#########################################################################
#########################################################################
def display_math_type0(math_object, format_):
    return math_object.math_type[0]


def display_constant(math_object, format_):
    """
    Display CONSTANT and LOCAL_CONSTANT

    :param math_object:
    :param format_:
    :return:
    """
    if math_object.math_type.node == "SET_FAMILY":
        return display_instance_set_family(math_object, format_)
    elif math_object.math_type == "SEQUENCE":
        return "**"  # todo
    display = math_object.info["name"]
    # if display in format_from_constant_name.keys():
    #     shape = format_from_constant_name[display]
    #     return display_math_object_from_shape(shape, math_object, format_)
    return [display]


def display_application(math_object, format_):
    """
    Very special case of APPLICATION
    :param math_object:
    :param format_:
    :return:
    """
    first_child = math_object.children[0]
    shape = ["***"]

    # strange cases
    if first_child.node == "CONSTANT":
        name = first_child.info['name']
        if name in format_from_constant_name.keys():
            shape = format_from_constant_name[name]
        else:
            shape = [name, 1]   # presumably we will get some argument
                                # to apply name
    # case of index notation
    elif first_child.math_type.node in ["SET_FAMILY", "SEQUENCE"]:
        shape = [0, "_child1"]
        return display_math_object_from_shape(shape, math_object, format_)

    display = display_math_object_from_shape(shape, math_object, format_)

    # general case, functional notation : f(x)
    elif not has_pending_parameter()


        shape = [0, "(", 1, ")"]
        return display_math_object_from_shape(shape, math_object, format_)
    ###################################
    # treatment of pending parameters #
    ###################################
    second_child = math_object.children[1]


    return display_math_object_from_shape(shape, math_object, format_)


def has_pending_parameter(structured_display: [str]):
    for item in structured_display:
        if isinstance(item, int):
            return True
    return False


def display_math_type_of_local_constant(math_object, format_):
    """

    :param math_object:
    :param format_:
    :return:
    """
    #######################################################
    # special math_types for which display is not the same #
    #######################################################
    if math_object.math_type.node == "TYPE":
        name_ = math_object.info["name"]
        return [text_to_latex(_("an element of") + " ", format_), name_]
    elif math_object.math_type.node == "SET":
        shape = [_("a subset of") + " ", 0]
        return display_math_object_from_shape(shape, math_object, format_)
    #################
    # no difference #
    #################
    else:
        return display_math_object(math_object, format_)


# the following is not called directly, but via display_constant
def display_instance_set_family(math_object, format_="latex"):
    """
    e.g. if E: I -> set X,
    then compute a good name for an index in I (e.g. 'i'),
    and display "{E_i, i in I}"

    WARNING: this bound variable is not referenced anywhere, in particular
    it will not appear in extract_local_vars.

    :param children_rep:
    :param math_object: PropObj
    :return: None
    """
    # first find a name for the bound var
    # log.debug("instance of set family")
    bound_var_type = math_object.math_type.children[0]
    index_name = give_local_name(math_type=bound_var_type,
                                 body=math_object)
    index_rep = index_name
    index_subscript_rep = global_subscript(index_rep)
    index_set_rep = math_object.math_type.children[0].representation[format_]
    name = math_object.lean_data["name"]
    if format_ == "latex":
        rep = [r"\{", name, r"_{", index_rep, r"}, ",
               index_rep, r"\in ", index_set_rep, r"\}"]
    else:
        rep = ["{", name, index_subscript_rep, ", ",
               index_rep, "∈", index_set_rep, "}"]
    return rep


#######################################
#######################################
# some tools for manipulating strings #
#######################################
#######################################

def text_to_latex(string: str, format_="latex"):
    if format_ == "latex":
        # TODO: replace symbol according to latex_symbols dictionary
        string = r"\textsc{" + string + r"}"
    return string


def subscript(index, format_):
    # TODO !!
    return "_" + index


def text_to_subscript(structured_string):
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
            sub, bool = text_to_subscript(item)
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
    sub, is_subscriptable = text_to_subscript(structured_string)
    if is_subscriptable:
        return sub
    else:
        return ['_'] + [sub]
        # [sub] necessary in case sub is an (unstructured) string


# TODO : tenir compte de la profondeur des parenthèses,
# et utiliser \Biggl(\biggl(\Bigl(\bigl((x)\bigr)\Bigr)\biggr)\Biggr)
nature_leaves_list = ["PROP", "TYPE", "SET_UNIVERSE", "SET", "ELEMENT",
                      "FUNCTION", "SEQUENCE", "SET_FAMILY",
                      "TYPE_NUMBER", "NUMBER", "VAR", "SET_EMPTY"]

format_from_node = {
    "APPLICATION": [display_application],
    "LOCAL_CONSTANT": [display_constant],
    "CONSTANT": [display_constant],

    "PROP_AND": [0, " " + _("AND") + " ", 1],
    "PROP_OR": [0, " " + _("OR") + " ", 1],
    "PROP_FALSE": [_("Contradiction"), ],
    "PROP_IFF": [0, " ⇔ ", 1],
    "PROP_NOT": [" " + _("NOT") + " ", 0],
    "PROP_IMPLIES": [0, " ⇒ ", 1],
    "QUANT_∀": ["∀ ", 0, " ∈", 1, ", ", 2],
    "QUANT_∃": ["∃ ", 0, " ∈", 1, ", ", 2],
    "PROP_∃": "not implemented",
    ###############
    # SET THEORY: #
    ###############
    "PROP_INCLUDED": [0, " ⊂ ", 1],
    "PROP_BELONGS": [0, " ∈", 1],
    "SET_INTER": [0, " ⋂ ", 1],
    "SET_UNION": [0, " ⋃ ", 1],
    "SET_INTER+": ["∩", 0],
    "SET_UNION+": ["∪", 0],
    "SET_DIFF": [0, r" \\ ", 1],
    "SET_COMPLEMENT": [display_math_type0, r" \\ ", 0],
    "SET_EMPTY": ["∅"],
    "SET_FAMILY": [_("a family of subsets of"), 1],
    ############
    # NUMBERS: #
    ############
    "PROP_EQUAL": [0, " = ", 1],
    "PROP_EQUAL_NOT": [0, " ≠ ", 1],
    "PROP_<": [0, " < ", 1],
    "PROP_>": [0, " > ", 1],
    "PROP_≤": [0, " ≤ ", 1],
    "PROP_≥": [0, " ≥ ", 1],
    "MINUS": [0, " - ", 1],
    "+": [0, " + ", 1],
    ##################
    # GENERAL TYPES: #
    ##################
    "PROP": [" " + _("a proposition")],
    "TYPE": [" " + _("a set")],
    "FUNCTION": [0, " → ", 1],
}

format_from_constant_name = {
    "composition": [0, '∘', 1]
}

latex_symbols = {  # TODO : complete the dictionary
    " ⇔ ": r" \LeftRightarrow",
    " ⇒ ": r" \Rightarrow",
    "∀ ": r" \forall",
    "∃ ": r" \exists",
    ###############
    # SET THEORY: #
    ###############
    "PROP_INCLUDED": " ⊂ ",
    "PROP_BELONGS": r" ∈",
    "SET_INTER": r" ⋂ ",
    "SET_UNION": r" ⋃ ",
    "SET_INTER+": "∩",
    "SET_UNION+": "∪",
    "SET_DIFF": r" \\ ",
    "SET_COMPLEMENT": "∁",
    "SET_EMPTY": r"∅",
    ############
    # NUMBERS: #
    ############
    "PROP_EQUAL": " = ",
    "PROP_EQUAL_NOT": " ≠ ",
    "PROP_<": "<",
    "PROP_>": ">",
    "PROP_≤": "≤",
    "PROP_≥": "≥",
    "MINUS": "-",
    "+": "+",
    ##################
    # GENERAL TYPES: #
    ##################
    "FUNCTION": " → ",
    "composition": '∘',
}
