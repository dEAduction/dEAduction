"""
##############################################
# display_math: display mathematical objects #
##############################################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 06 2020 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

Contain the data for processing PropObj into a latex representation

The basic data for representing math objects is the utf8_from_node dictionary.
It associates, to each MathObject.node attribute, the shape to display, e.g.
    "PROP_INCLUDED": [0, " ⊂ ", 1],
where the numbers refer to the MathObject's children.
The display_math_object function pick the right shape from this dictionary,
and then call the display_math_object_from_shape function. Note that the
shape can include calls to some specific formatting functions, e.g.
    - display_application,
    - display_local_constant,
    - display_constant,
    - display_lambda,
    - display_math_type0


    This file is part of dEAduction.

    dEAduction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    dEAduction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.

    TODO: display product:
    - prod (I,J)
    - prod.fst, prod.snd
"""

import logging
import types

import deaduction.pylib.logger              as logger
from deaduction.pylib.mathobj.give_name     import give_local_name
from deaduction.config                      import _
from deaduction.pylib.mathobj.display_data import ( utf8_from_node,
                                                    format_from_constant_name,
                                                    text_from_node
                                                    )


log = logging.getLogger(__name__)


def display_math_object(math_object, format_="utf8", text_depth=1):
    """
    This function essentially looks for a shape in the format_from_node
    dictionary, and then pass the shape to display_math_object_from_shape
    which computes the display.

    :param math_object: the MathObject instance to be displayed
    :param format_:     "utf8", "text+utf8", "latex" TODO: implement latex
    :param text_depth:  when format_="text+utf8", only the symbols at level
                        less than text_depth in the tree are replaced by text.
                        So for instance
                                format_="text+utf8" and text_depth=0
                        will yield the same result as
                                format_="utf8".
    :return:            a "structured string", to be transform into a string
                        by the structured_display_to_string function
    """
    #log.debug(f"Computing math display of {math_object}")
    node = math_object.node
    if format_ == "text+utf8" \
            and text_depth > 0 \
            and node in text_from_node.keys():
        shape = text_from_node[node]
        return display_math_object_from_shape(shape,
                                              math_object,
                                              format_,
                                              text_depth)
    elif node in utf8_from_node.keys():
        shape = utf8_from_node[node]
        return display_math_object_from_shape(shape,
                                              math_object,
                                              format_,
                                              text_depth)
    else:
        log.warning(f"display error: node {node} not in utf8_from_node")
        return ["*unknown*"]


def display_math_object_from_shape(shape,
                                   math_object,
                                   format_="utf8",
                                   text_depth=1):
    """
    Replace each element of shape with its display.
    Ex of shape: [0, " = ", 1]
    For more examples, see values of the format_from_node dictionary.
        - numbers refer to children, and will be replaced by the
            corresponding display,
        - strings are displayed as such for utf8, (see exceptions below)
        - functions are called
    Exceptions for strings:
        - "_child#" code for subscript version of child number #
        - some items may already be in displayable form

    :param shape:       a value of the node_to_utf8 dictionary
    :param math_object: an instance of MathObject
    :param format_:     "utf8", "text+utf8" or "latex"
    :param text_depth:  see display_math_object_as_text
    :return:            a structured string (a list whose items are lists or
                        strings), to be passed to structured_display_to_string
                        in order to get a string
    """
    # log.debug(f"Trying to display from shape {shape}")
    display_shape = []
    counter = -1
    for item in shape:
        counter += 1
        display_item = "¿**"
        # specific display
        if isinstance(item, types.FunctionType):
            # e.g. item = display_constant, display_application, ...
            display_item = item(math_object, format_)
        # integers code for children
        elif isinstance(item, int):
            if item < len(math_object.children):
                child = math_object.children[item]
                display_item = display_math_object(child,
                                                   format_,
                                                   text_depth - 1)
                # with brackets?
                if not format_.startswith("text") or text_depth < 1:
                    if needs_paren(math_object, item):
                        display_item = ['('] + display_item + [')']
            else:  # keep the integer, this could be a pending parameter
                display_item = item
        # strings
        elif isinstance(item, str):
            if item.startswith("_child"):
                number = int(item[len("_child"):])
                child = math_object.children[number]
                pre_display_item = display_math_object(child,
                                                       format_,
                                                       text_depth - 1)
                display_item = global_subscript(pre_display_item)  # TODO
            elif item.find("∈") != -1 and isinstance(shape[counter + 1], int):
                # replace "∈" with ":" in some cases
                type_ = math_object.children[shape[counter + 1]]
                symbol = display_belongs_to(type_, format_, text_depth)
                display_item = item.replace('∈', symbol)
            else:
                display_item = text_to_latex(item, format_)

        elif isinstance(item, list):
            display_item = item
        display_shape.append(display_item)

    if len(display_shape) == 1:
        display_shape = display_shape[0]
    return display_shape


def needs_paren(parent, child_number: int) -> bool:
    """
    Decides if parentheses are needed around the child
    e.g. if PropObj.node = PROP.IFF then
    needs_paren(PropObj,i) will be set to True for i = 0, 1
    so that the display will be
    ( ... ) <=> ( ... )

    TODO : tenir compte de la profondeur des parenthèses,
    et utiliser \Biggl(\biggl(\Bigl(\bigl((x)\bigr)\Bigr)\biggr)\Biggr)
    """
    nature_leaves_list = ["PROP", "TYPE", "SET_UNIVERSE", "SET", "ELEMENT",
                          "FUNCTION", "SEQUENCE", "SET_FAMILY",
                          "TYPE_NUMBER", "NUMBER", "VAR", "SET_EMPTY"]
    child_prop_obj = parent.children[child_number]
    p_node = parent.node
    # if child_prop_obj.node == "LOCAL_CONSTANT":
    #     return False
    if not child_prop_obj.children:
        return False
    c_node = child_prop_obj.node
    if c_node in nature_leaves_list + \
            ["SET_IMAGE", "SET_INVERSE", "PROP_BELONGS", "PROP_EQUAL",
             "PROP_INCLUDED", "SET_UNION+", "SET_INTER+"]:
        return False
    elif c_node == "APPLICATION":
        return False
    elif p_node in ["SET_IMAGE", "SET_INVERSE",
                    "SET_UNION+", "SET_INTER+", "APPLICATION",
                    "PROP_EQUAL", "PROP_INCLUDED", "PROP_BELONGS", "LAMBDA"]:
        return False
    elif c_node.startswith("QUANT") and p_node.startswith("QUANT"):
        return False
    return True


#########################################################################
#########################################################################
# Special display functions, called from display_math_object_from_shape #
# (see also the format_from_node dictionary)                            #
#########################################################################
#########################################################################
def display_name(math_object, format_):
    """display name"""
    return [math_object.info['name']]


def display_math_type0(math_object, format_):
    """display first child of math_type"""
    return display_math_object(math_object.math_type.children[0], format_)


def display_constant(math_object, format_):
    """
    Display for nodes 'CONSTANT' and 'LOCAL_CONSTANT'

    :param math_object:
    :param format_:
    :return:
    """
    display = "*CST*"
    if hasattr(math_object.math_type,"node"):
        if math_object.math_type.node == "SET_FAMILY":
            return display_instance_set_family(math_object, format_)
        elif math_object.math_type.node == "SEQUENCE":
            return "*SEQ*"  # todo
    if 'name' in math_object.info.keys():
        display = [math_object.info['name']]
    # if display in format_from_constant_name.keys():
    #     shape = format_from_constant_name[display]
    #     return display_math_object_from_shape(shape, math_object, format_)
    return display


def display_application(math_object, format_):
    """
    display for node 'APPLICATION'
    This is a very special case
    todo: product (prod.fst, prod.snd, prod, node = 'CONSTANT')
    todo: improve robustness
    :param math_object:
    :param format_:
    :return:
    """
    first_child = math_object.children[0]
    second_child = math_object.children[1]
    #log.debug(f"displaying APP, 1st child = {first_child}, "
    #          f"2nd child = {second_child}")
    shape = ["*APP*"]

    # case of index notation
    if first_child.math_type.node in ["SET_FAMILY", "SEQUENCE"]:
        # we DO NOT call display for first_child because we just want
        #  "E_i",       but NOT       "{E_i, i ∈ I}_i"      !!!
        # We just take care of two cases of APP(E,i) with either
        # (1) E a local constant, or
        # (2) E a LAMBDA with body APP(F, j) with F local constant
        name = 0  # for the unknown case
        if first_child.node == "LOCAL_CONSTANT":
            name = first_child.info['name']
        elif first_child.node == "LAMBDA":
            body = first_child.children[2]
            if body.node == "APPLICATION" and body.children[0].node == \
                    "LOCAL_CONSTANT":
                name = body.children[0].info['name']
        shape = [name, "_child1"]
        return display_math_object_from_shape(shape, math_object, format_)
    # strange cases
    elif first_child.node == "CONSTANT":
        name = first_child.info['name']
        if name in format_from_constant_name.keys():
            shape = format_from_constant_name[name]
        #elif not second_child.is_type():
        #    shape = [name, -1]  # '-1' is a place for a pending parameter
        else:
            # shape = [name, 0]
            shape = [-1, " " + _("is") + " ", name]  # we hope to get some
            # argument to apply name
    elif first_child.node == "APPLICATION":
        display_first_child = display_math_object(first_child, format_)
        if has_pending_parameter(display_first_child):
            shape = display_first_child

    if not has_pending_parameter(shape):
        if shape == ["*APP*"]:
            if math_object.is_prop():
                # display of a property, e.g. "f is injective"
                shape = [1, " " + _("is") + " ", 0]
            else:
                # general case, functional notation: f(x)
                shape = [0, "(", 1, ")"]
        return display_math_object_from_shape(shape, math_object, format_)
    ###################################
    # treatment of pending parameters #
    ###################################
    # here shape comes from first_child,
    # either from display if node == APPLICATION
    # or if node == CONSTANT
    # if second parameter is not type, insert it in shape
    # then return shape if there remains some pending parameters,
    # else display shape
    if not second_child.is_type():
        shape = insert_pending_param(second_child, shape, format_)
    if has_pending_parameter(shape):
        return shape
    else:
        return display_math_object_from_shape(shape, math_object, format_)


def has_pending_parameter(structured_display: [str]):
    """
    A structured display is supposed to be a list whose items are either
    lists or strings. But it may contain "pending parameters" which are
    integer.
    """
    for item in structured_display:
        if isinstance(item, int) and item < 0:
            return True
    return False


def insert_pending_param(math_object, shape, format_):
    """
    Modify shape:
    replace first integer 0 by math_object and then shift every integer by 1
    """
    # insert math_object where there is a '-1'
    shape1 = [display_math_object(math_object, format_)
              if item == -1 else item for item in shape]
    # shift integers
    shape2 = [item + 1 if isinstance(item, int) else item for item in shape1]
    return shape2


def display_math_type_of_local_constant(math_type, format_):
    """
    process special cases, e.g.
    1) x : an element of X"
    (in this case   math_object represents x,
                    math_object.math_type represents X,
                    and the analysis is based on the math_type of X.
    2) A : a subset of X
    """
    #######################################################
    # special math_types for which display is not the same #
    #######################################################
    if hasattr(math_type, 'math_type') \
            and hasattr(math_type.math_type, 'node') \
            and math_type.math_type.node == "TYPE":
        name_ = math_type.info["name"]
        return [text_to_latex(_("an element of") + " ", format_), name_]
    elif hasattr(math_type, 'node') and math_type.node == "SET":
        shape = [_("a subset of") + " ", 0]
        return display_math_object_from_shape(shape, math_type, format_)
    #################
    # no difference #
    #################
    else:
        return display_math_object(math_type, format_)


# the following is not called directly, but via display_constant
def display_instance_set_family(math_object, format_="latex"):
    """
    e.g. if E: I -> set X,
    then compute a good name for an index in I (e.g. 'i'),
    and display "{E_i, i in I}"

    WARNING: this bound variable is not referenced anywhere, in particular
    it will not appear in extract_local_vars.
    """
    # first find a name for the bound var
    bound_var_type = math_object.math_type.children[0]
    index_name = give_local_name(math_type=bound_var_type,
                                 body=math_object)
    index_rep = index_name
    index_subscript_rep = global_subscript(index_rep)
    # if format_ == "latex":
    #     rep = [r"\{", name, r"_{", index_rep, r"}, ",
    #            index_rep, r"\in ", index_set_rep, r"\}"]
    shape = ["{", display_name, index_subscript_rep, ", ",
           [index_rep], " ∈ ", display_math_type0, "}"]
    return display_math_object_from_shape(shape, math_object, format_)


def display_lambda(math_object, format_="latex"):
    """
    format for lambda expression, e.g.
    - set families with explicit bound variable
        lambda (i:I), E i)
        encoded by LAMBDA(I, i, APP(E, i)) --> "{E_i, i ∈ I}"
    - sequences,
    - mere functions
        encoded by LAMBDA(X, x, APP(f, x))  --> "f"
    - anything else is displayed as "x ↦ f(x)"
    """
    math_type = math_object.math_type
    _, var, body = math_object.children
    if math_type.node == "SET_FAMILY":
        shape = ['{', 2, ', ', 1, ' ∈ ', 0, '}']
    elif math_type.node == "SEQUENCE":
        shape = ['(', 2, ')', '_{', 1, ' ∈ ', 0, '}']  # todo: manage subscript
    elif body.node == "APPLICATION" and body.children[1] == var:
        # object is of the form x -> f(x)
        mere_function = body.children[0]  # this is 'f'
        shape = [display_math_object(mere_function, format_)]
    else:  # generic display
        shape = [1, '↦', 2]
    return display_math_object_from_shape(shape, math_object, format_)


#######################################
#######################################
# some tools for manipulating strings #
#######################################
#######################################
def display_belongs_to(math_type, format_, text_depth, belonging=True) -> str:
    """
    compute the adequate shape for display of "x belongs to X", e.g.
    - generically, "x∈X"
    - specifically,
        - "f : X -> Y" (and not f ∈ X-> Y),
        or "f is a function from X to Y"
        - "P: a proposition" (and not P ∈ a proposition),
    """
    #log.debug(f"display ∈ with {math_type}, {format_}, {text_depth}")
    if format_ == "text+utf8" and text_depth > 0:
        if math_type.node == "PROP" \
                or (math_type.node == "FUNCTION" and text_depth > 1):
            symbol = _("is")
        elif math_type.node == "FUNCTION" and text_depth == 1:
            symbol = ":"
        else:
            symbol = _("belongs to")
    else:
        if math_type.node in ["FUNCTION", "PROP"]:
            symbol = ":"
        else:
            symbol = "∈"
    return symbol


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


def display_text_quant(math_object, format_, text_depth):
    """
    Compute a smart text version of a quantified sentence.

    :param math_object: a math object with node "QUANT_∀", "QUANT_∃", or
                        "QUANT_∃!".
    :param format_:     "text+utf8"
    :param text_depth:  see display_math_object
    """
    #TODO
    pass


def display_text_belongs_to(math_object, format_, text_depth):
    """Compute a smart version of

    :param math_object: a math object whose node is "PROP_BELONGS"
    :param format_:     "text+utf8"
    :param text_depth:  see display_math_object
    """
    #TODO
    pass


##########
# essais #
##########
if __name__ == '__main__':
    logger.configure()
