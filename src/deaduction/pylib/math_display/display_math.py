"""
##############################################
# display_math: display mathematical objects #
##############################################

Contain the data for processing MathObject into a displayable format:
latex, utf8, text, or lean (to be inserted in Lean code).

The basic data for representing math objects is the latex_from_node dictionary.
It associates, to each MathObject.node attribute, the shape to display, e.g.
    "PROP_INCLUDED": [0, " \\subset ", 1],
where the numbers refer to the MathObject's children.
For generic nodes at least, the from_math_object method picks the right shape
from this dictionary, and then call the Shape.from_shape method.

utf8 and lean format are also provided. The utf8 format is obtained from
the latex string using latex_to_utf8_dic that converts latex commands.
For Lean format some nodes have to be computed from scratch, these are in
lean_from_node; but for most nodes the utf8 string is also OK for Lean.

TO IMPLEMENT A NEW NODE FOR DISPLAY:
- for standards nodes, it suffices to add an entry in the latex_from_node
dictionary (and in the latex_to_ut8, utf8_to_lean, node_to_lean if
necessary). Those dictionaries are in display_data.py.
- for some specific constant, use the latex_from_constant_name dictionary
These constant are displayed through display_application,
e.g. APP(injective, f).
- for more specific nodes, one can define a new display function and call it
via the from_specific_node function.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 06 2020 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

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

"""

import logging
from typing import Any, Union

from deaduction.pylib.math_display.display_data \
                                        import (latex_from_constant_name,
                                                latex_from_quant_node,
                                                needs_paren,
                                                couples_of_nodes_to_latex,
                                                dic_of_first_nodes_latex)

log = logging.getLogger(__name__)
global _

#########################################################################
#########################################################################
# Specific display functions, called by from_specific_node              #
#########################################################################
#########################################################################
# display_constant for "CONSTANT" and "LOCAL_CONSTANT"
# shape_from_application for "APPLICATION"
# display_set_family (called by display_constant when needed)
# display_lambda


def extensive_children(display: []) -> []:
    """
    Return all child nb appearing in display,
    e.g. [0, [\\parentheses, -1, 3]] -> [0, -1, 3]
    """
    if isinstance(display, list):
        children = []
        for item in display:
            children.extend(extensive_children(item))
        return children
    elif isinstance(display, int):
        return [display]
    else:
        return []


def least_children(display) -> Union[int, None]:
    """
    Return None if display has some negative child nb,
    or the greatest child nb otherwise.
    """
    children = extensive_children(display)
    least_used_child = 0
    for child_nb in children:
        if child_nb < 0:  # Negative values forbid supplementary arguments
            return None
        elif child_nb > least_used_child:
            least_used_child = child_nb
    return least_used_child


def raw_latex_shape_from_application(math_object, negate=False):
    """
    Provide display for node 'APPLICATION'
    This is a very special case, includes e.g.
    - APP(injective, f)                     -> f is injective
    - APP(APP(composition, f),g)            -> r"f \\circ g"
    - APP(f, x)                             -> f(x)
    - APP(APP(APP(composition, f),g),x)     -> r"f \\circ g (x)"

    NB: implicit children are used to transform
                                            APP(APP(...APP(x0,x1),...),xn)
                                    into
                                            APP(x0, x1, ..., xn)
    """

    # FIXME: add structure by using intermediate functions
    nb = math_object.nb_implicit_children()
    implicit_children = [math_object.implicit_children(n)
                         for n in range(nb)]

    display = [0]  # Default = display first child as a function

    first_child = implicit_children[0]
    # (2) Case of index notation: sequences, set families
    if first_child.math_type.node in ["SET_FAMILY", "SEQUENCE",
                                      "RAW_SET_FAMILY", "RAW_SEQUENCE"]:
        # APP(E, i) -> E_i
        # we DO NOT call display for first_child because we just want
        #  "E_i",       but NOT       "{E_i, i ∈ I}_i"      !!!
        # We just take care of two cases of APP(E,i) with either
        # (1) E a local constant, or
        # (2) E a LAMBDA with body APP(F, j) with F local constant
        #  I guess this second case should not happen: substitution should
        #  have been done by Lean!
        if first_child.node == "LOCAL_CONSTANT":
            # name = first_child.display_name
            # Prevent future replacement of "u" by "(u_n)_{n in N}"
            #  or "E" by "{E_i, i in I}".
            display = [0, ['_', 1]]
        elif first_child.node == "LAMBDA":
            body = first_child.children[2]
            if body.node == "APPLICATION" and body.children[0].node == \
                    "LOCAL_CONSTANT":
                name = body.children[0].display_name
            else:
                name = '*set_family*'
            display = [name, ['_', 1]]
        # log.debug(f"Displaying app: {display}")

    # (3) Case of constants, e.g. APP(injective, f)
    elif first_child.node == "CONSTANT":
        name = first_child.display_name
        if name in latex_from_constant_name:
            # Damn bug, I got you!!!!!
            display = list(latex_from_constant_name[name])
        else:  # Standard format
            display = list(latex_from_constant_name['STANDARD_CONSTANT'])
            # display_not = list(latex_from_constant_name[
            #                        'STANDARD_CONSTANT_NOT'])

    ############
    # NEGATION #
    ############
    if negate:
        text_is = r'\text_is'
        text_is_not = r'\text_is_not'
        if text_is in display:
            index = display.index(text_is)
            display[index] = text_is_not
        else:
            display.insert(0, r'\not')

    # (4) Finally: use functional notation for remaining arguments
    # ONLY if they are not type
    # first search for unused children
    # search for least used child
    least_used_child = least_children(display)

    # Keep only those unused_children whose math_type is not TYPE
    # nor other implicit arguments like instances
    if least_used_child is not None:
        more_display = []
        for n in range(least_used_child+1, len(implicit_children)):
            math_type = implicit_children[n].math_type
            if not hasattr(math_type, 'node') or not math_type.is_implicit_arg():
                more_display.append(n)
            else:
                log.debug(f"Implicit arg: {implicit_children[n].display_name}")
        if more_display:
            # display += ['('] + more_display + [')']
            display += [r"\parentheses"] + more_display
            # NB: in generic case APP(f,x), this gives  ['(', 1, ')']

    return display


def display_constant(math_object) -> list:
    """
    Display for nodes 'CONSTANT' and 'LOCAL_CONSTANT'
    NB: expressions APP(constant, ...) are treated directly in
    display_application.
    """
    name = math_object.display_name
    display = [name]  # generic case

    # Displaying some subscript
    if name.count('_') == 1:
        radical, subscript = name.split('_')
        display = [radical, ['_', subscript]]

    # Variables and dummy variables (for coloration)
    if math_object.is_bound_var:
        display = [r'\dummy_variable', display]
    elif math_object.is_variable(is_math_type=True):
        display = [r'\variable', display]

    return display


def display_metavar(math_object) -> list:
    txt = '?'
    if 'nb' in math_object.info:
        txt += '_' + str(math_object.info['nb'])
    return [txt]


def display_number(math_object) -> list:
    """
    Display for nodes 'NUMBER'.

    :param math_object:
    :return:            'display' list
    """
    display = [math_object.info.get('value')]
    return display


def display_quantifier(math_object) -> list:
    """
    Display quantifiers, in particular handles the case of
    "
    ∀ x >0, ...
    which is encoded by Lean as
    ∀ x:R, (x>0 ==> ...)
    but should be displayed as above.
    Here we assume that math_object.node is in the latex_from_quant_node dic.
    """

    # TODO: replace by pattern nodes

    node = math_object.node
    children = math_object.children
    display = list(latex_from_quant_node[node])
    math_type = children[0]
    variable = children[1]
    property = children[2]
    quantifier = display[0]
    # belongs_to = display[2]
    such_that = display[4]

    # First test if quantifier is an instance statement
    # --> no display!
    if math_object.is_for_all(is_math_type=True):
        if variable.is_instance():
            # ∀ _inst_1 : blabla, <prop>
            # --> we want only <prop> to be displayed
            display = [2]
        if variable.is_R():
            # ∀ RealSubGroup : Type, <prop>
            # --> we only want prop
            display = [2]

    # The following tests if math_object has the form
    # ∀ x:X, (x R ... ==> ...)
    # where R is some inequality relation
    if math_object.is_for_all(is_math_type=True):
        if property.is_implication(is_math_type=True):
            premise = property.children[0]  # children (2,0)
            if premise.is_inequality(is_math_type=True):
                item = premise.children[0]
                if item == variable:
                    # (2,0), (2,1) code for descendants:
                    display = [quantifier, (2, 0), such_that, (2, 1)]

    if math_object.is_exists(is_math_type=True):
        if property.is_and(is_math_type=True):
            premise = property.children[0]  # children (2,0)
            if premise.is_inequality(is_math_type=True):
                item = premise.children[0]
                if item == variable:
                    # (2,0), (2,1) code for descendants:
                    display = [quantifier, (2, 0), such_that, (2, 1)]

    return display


def display_lambda(math_object, format_="latex") -> list:
    """
    Display lambda expression. Note that set families and sequences should
    not be processed here, but catched by the "couple of nodes" trick.
    - mere functions are encoded by
        LAMBDA(X, x, APP(f, x))  --> "f"
    - anything else is displayed as
        "x ↦ f(x)"
    """
#     log.warning("Unexpected lambda")
#     math_type = math_object.math_type
#     _, var, body = math_object.children
#     # log.debug(f"display LAMBDA with var, body, type = {var, body,
#     # math_type}")
#     if math_type.node == "SET_FAMILY":
#         display = [r'\{', 2, ', ', 1, r"\in_symbol", 0, r'\}']
#     elif math_type.node == "SEQUENCE":
#         display = ['(', 2, ')', ['_', 1], r"\in_symbol", 0]
#         # todo: manage subscript
#     elif body.node == "APPLICATION" and body.children[1] == var:
#         # Object is of the form x -> f(x)
#         mere_function = body.children[0]  # this is 'f'
#         # We call the whole process in case 'f' is not a LOCAL_CONSTANT
#         display = Shape.from_math_object(mere_function, format_).display
#     else:  # Generic display
#         display = [1, '↦', 2]
#     if not display:
#         display = ['*unknown lambda*']
#     # log.debug(f"--> {display}")
    return [1, '↦', 2]


# # The following is not called directly, but via display_constant
# def display_sequence(math_object) -> list:
#     """
#     A sequence is encoded in Lean as an object u of type
#     nat -> X,
#     and Lean just display 'u'.
#     We compute a good name for an index in nat (e.g. 'n'),
#     and display "(u_n)_{n \in N}".
#     """
#     # This is deprecated
#     log.warning("Deprecated display of set family")
#
#     name = math_object.display_name
#     math_type_name = math_object.math_type_child_name()
#     bound_var_type = math_object.math_type.children[0]
#     index_name = give_local_name(math_type=bound_var_type,
#                                  body=math_object)
#     display = [r"(", name, ['_', index_name], ')',
#                ['_', index_name, r"\in_symbol", math_type_name]]
#     return display


# def display_set_family(math_object) -> list:
#     """
#     A set family is usually encoded in Lean as an object E of type
#     I -> set X,
#     and Lean just display 'E'.
#     We compute a good name for an index in I (e.g. 'i'),
#     and display "{E_i, i in I}".
#     """
#
#     # This is deprecated
#     log.warning("Deprecated display of set family")
#     # FIXME:    this bound variable is not referenced anywhere, in particular
#     #           it will not appear in extract_local_vars.
#
#     # First find a name for the bound var
#     name = math_object.display_name
#     math_type_name = math_object.math_type_child_name()
#     bound_var_type = math_object.math_type.children[0]
#     index_name = give_local_name(math_type=bound_var_type,
#                                  body=math_object)
#     display = [r"\{", name, ['_', index_name], ', ',
#                index_name, r"\in_symbol", math_type_name, r"\}"]
#     return display


# ##################
# # Other displays #
# ##################
# # This function is called directly by MathObject.to_display
# # Thus it has to return an EXPANDED shape
# def raw_display_math_type_of_local_constant(math_type,
#                                         format_,
#                                         text_depth=0) -> Shape:
#     """
#     Process special cases, e.g.
#     (1) x : element of X"
#      In this case   math_object represents x,
#                     math_object.math_type represents X,
#                     and the analysis is based on the math_type of X.
#     (2) A : subset of X
#
#     :param math_type:       MathObject
#     :param format_:         as usual
#     :param text_depth:      int
#     :return:                shape with expanded display
#     """
#     # FIXME: deprecated
#     ########################################################
#     # Special math_types for which display is not the same #
#     ########################################################
#     display = []
#     if hasattr(math_type, 'math_type') \
#             and hasattr(math_type.math_type, 'node') \
#             and math_type.math_type.node == "TYPE":
#         name = math_type.info["name"]
#         if text_depth > 0:
#             display = [_("an element of") + " ", name]
#         else:
#             display = [_("element of") + " ", name]
#     elif hasattr(math_type, 'node') and math_type.node == "SET":
#         if text_depth > 0:
#             display = [_("a subset of") + " ", 0]
#         else:
#             display = [_("subset of") + " ", 0]
#     elif math_type.node == "SEQUENCE":
#         display = [_("a sequence in") + " ", 1]
#     elif math_type.node == "SET_FAMILY":
#         display = [_("a family of subsets of") + " ", 1]
#     if display:
#         raw_shape = Shape(display=display,
#                           math_object=math_type,
#                           format_=format_,
#                           text_depth=text_depth
#                           )
#     #################
#     # Generic case  #
#     #################
#     else:  # Compute Shape from math_object
#         raw_shape = math_type.raw_latex_shape()
#         raw_shape = Shape.raw_shape_from_math_object(math_object=math_type,
#                                                      format_=format_,
#                                                      text_depth=text_depth)
#     # raw_shape.expand_from_shape()
#     return raw_shape


######################
######################
# auxiliary displays #
######################
######################
# def display_belongs_to(math_type: Any, format_, text_depth) -> str:
#     """
#     Compute the adequate shape for display of "x belongs to X", e.g.
#     - generically, "x∈X"
#     - specifically,
#         - "f : X -> Y" (and not f ∈ X-> Y),
#         or "f is a function from X to Y"
#         - "P: a proposition" (and not P ∈ a proposition),
#
#         :param math_type:   MathObject or "unknown"
#         :param format_:     as usual
#         :param text_depth:  int
#         :return:
#     """
#     # FIXME: deprecated
#
#     # log.debug(f"display ∈ with {math_type}, {format_}, {text_depth}")
#     # if 'unknown' == math_type:  # should not happen anymore
#     #    if format_ in ('utf8', 'lean'):
#     #        return "∈"
#     # from now on math_type is an instance of MathObject
#     if math_type is 'unknown' or math_type is None:  # DO NOT change is into ==
#         if text_depth > 0:
#             symbol = _("is")
#         else:
#             symbol = "∈" if format_ == "utf8" else r"\in"
#         return symbol
#     if text_depth > 0:
#         if math_type.is_prop(is_math_type=True) \
#                 or math_type.is_type(is_math_type=True) \
#                 or (math_type.is_function(is_math_type=True)
#                     and text_depth > 1):
#             symbol = _("is")
#         elif math_type.is_function(is_math_type=True) and text_depth == 1:
#             symbol = ":"
#         else:
#             symbol = _("belongs to")
#     else:
#         if math_type.is_function(is_math_type=True) \
#                 or math_type.is_prop(is_math_type=True) \
#                 or math_type.is_type(is_math_type=True):
#             symbol = ":"
#         else:
#             symbol = "∈" if format_ == "utf8" else r"\in"
#     return symbol


# def various_belongs(math_type) -> str:
#     """
#     Return a latex macro for specific belonging.
#     This is useful to display, e.g.
#             - "f : X -> Y" (and not f ∈ X-> Y),
#         or "f is a function from X to Y"
#         - "P: a proposition" (and not P ∈ a proposition), or "X: a set"
#
#     :param math_type:
#     the type of the element (the set to which it
#     belongs)
#     :return: e.g. [r'\\in', math_type], or [r'\\in_prop'], [r'\\in_set'],
#     [r'\\in_function'].
#     """
#     # FIXME: deprecated?
#     belongs = (r'\in_prop' if math_type.is_prop(is_math_type=True)
#                else r'\in_set' if math_type.is_type(is_math_type=True)
#                else r'\in_function' if math_type.is_function(is_math_type=True)
#                else '')
#     return belongs


def string_to_latex(string: str):
    """Put the "\text" command around pure text for Latex format"""
    # Not used
    if string.isalpha():
        string = r"\text{" + string + r"}"
    return string


#######################################
#######################################
# Some tools for manipulating strings #
#######################################
#######################################

# def shape_error(message: str, math_object=None, format_="", text_depth=0):
#     #   FIXME: deprecated
#     shape = Shape(['*' + message + '*'],
#                   math_object,
#                   format_,
#                   text_depth)
#     return shape


def display_error(message: str) -> str:
    return '*' + message + '*'


def insert_children_in_string(string: str, children: tuple) -> []:
    """
    Take a string and a tuple of children, e.g.
    string = _("for every subset {} of {}, {}", children = (1, (0, 0), 2)),
    and insert children at every {} place in string.
    The remaining of the string is cup into words which are tagged with the
    '\text' tag.
    """
    string_list = string.split("{}")
    string_list = [[r'\text', word] for word in string_list]
    assert len(string_list) == len(children) + 1
    shape = [string_list[0]]
    for string, child in zip(string_list[1:], children):
        shape.extend([child, string])
    shape = [item for item in shape if '' != item]  # Remove empty strings

    return shape


def raw_latex_shape_from_couple_of_nodes(math_object, text_depth=0) -> []:
    """
    Return a shape from the dictionaries couples_of_nodes_to_text
    or couples_of_nodes_to_utf8 (according to text_depth)
    if it finds some key that matches math_object and math_object's first child
    nodes. Otherwise, return None.
    """

    # TODO: replace bu pattern nodes

    from deaduction.pylib.math_display import (dic_of_first_nodes_text,
                                               couples_of_nodes_to_text)
    shape = None
    first_node = math_object.node
    if text_depth > 0:
        if first_node in dic_of_first_nodes_text:
            second_node = math_object.children[0].node
            if second_node in dic_of_first_nodes_text[first_node]:
                key = (first_node, second_node)
                string, children = couples_of_nodes_to_text[key]
                shape = insert_children_in_string(string, children)
    if not shape:
        if first_node in dic_of_first_nodes_latex:
            second_node = math_object.children[0].node
            if second_node in dic_of_first_nodes_latex[first_node]:
                key = (first_node, second_node)
                shape = list(couples_of_nodes_to_latex[key])

    # if shape:
    # log.debug("Shape from couple of nodes")
    return shape


def raw_latex_shape_from_specific_nodes(math_object, negate=False):
    """
    Treat the case of some specific nodes by calling the appropriate
    function. Specific nodes include:
    - application,
    - constant and local_constant,
    - numbers,
    - quantifiers,
    - lambda expressions,
    - set families
    - sequences

    :return:            A "raw shape", e.g. [0, "=", 1].
    """

    # TODO: replace everything by standard nodes??

    node = math_object.node
    display = [display_error(_("unknown object"))]
    if node == "NO_MORE_GOAL":
        display = _("All goals reached!")
    elif node == "CURRENT_GOAL_SOLVED":
        display = _("Current goal solved")
    elif node == "APPLICATION":
        # This one returns a shape, to handle supplementary children
        display = raw_latex_shape_from_application(math_object, negate)
    elif node in ["LOCAL_CONSTANT", "CONSTANT"]:
        # ! Return display, not shape
        display = display_constant(math_object)
    elif node == 'METAVAR':
        display = display_metavar(math_object)
    elif node == 'NUMBER':
        display = display_number(math_object)
    elif math_object.is_quantifier(is_math_type=True):
        display = display_quantifier(math_object)
    elif node == "LAMBDA":
        display = display_lambda(math_object)
    elif node == "SET_UNIVERSE":
        display = [math_object.math_type_child_name()]
    # elif node == "SET_COMPLEMENT":
    #     universe = math_object.math_type_child_name()
    #     display = [universe, r" \backslash ", 0]

    if negate and node != "APPLICATION":
        display = [r'\not', display]
    return display


def recursive_display(math_object, text_depth=0, shape=None,
                      negate=False):
    """
    Consider shape of self, e.g. [0, "\text_is_not", 1],
    then recursively replace integers by the raw_latex_shape of
    corresponding children.

    Take care of parentheses:
        \\parentheses -> to be displayed between parentheses
    Take care of negation.
    """

    # (1) Compute raw display, e.g. [0, "\text_is_not", 1]
    if not shape:
        shape = math_object.raw_latex_shape(negate, text_depth)

    if shape == [r'\not', 0]:
        negate = True
        shape = [0]  # -> [0]
    else:
        negate = False  # negation does not propagate to children

    if shape[0] == r'\no_text':
        text_depth = 0

    # (2) Recursively replace integers by display of children,
    #  e.g. ["f", "\text_is_not", "injective"]
    display = []
    for item in shape:
        # Case of a string
        display_item = item

        # if isinstance(display_item, str) and display_item.startswith("info['"):
        #     field = display_item[len("info['"):-2]
        #     display_item = str(math_object.info.get(field, ""))

        # Integers code for children, or tuples for grandchildren
        if isinstance(item, int) or isinstance(item, tuple):
            child = math_object.descendant(item)
            display_item = recursive_display(child, negate=negate,
                                             text_depth=text_depth-1)
            # Between parentheses?
            if needs_paren(math_object, child, item, text_depth):
                display_item = [r'\parentheses', display_item]

        elif isinstance(item, list):
            display_item = recursive_display(math_object, shape=item,
                                             negate=negate,
                                             text_depth=text_depth)

        display.append(display_item)

    # log.debug(f"    --> Recursive display: {display}")
    return display


def shorten(string: str) -> str:
    """
    Try to shorten string for concise display: e.g.
    "an element of " -> "element of "
    "is injective" -> injective.
    Note that this is called after translation.
    """
    # FIXME: to be adapted according to languages
    to_be_shortened = {_("a function"): _("function"),
                       _("an element"): _("element"),
                       _("a subset"): _("subset"),
                       _('a proposition'): _("proposition"),
                       _("a family"): _("family")
                       }
    to_be_suppressed = (r'\text_is', " ")
    to_be_replaced = {r'\text_is_not': " " + _("not") + " "}

    striped_string = string.strip()
    for phrase in to_be_shortened:
        if striped_string.startswith(phrase):
            shortened_phrase = to_be_shortened[phrase]
            # words = phrase.split(" ")
            # prefix = words[0]
            # # Just replace first occurrence:
            # string = string.replace(prefix+" ", "", 1)
            string = string.replace(phrase, shortened_phrase)
    for word in to_be_suppressed:
        if striped_string == word:
            string = " "

    for word in to_be_replaced:
        if striped_string == word:
            string = string.replace(word, to_be_replaced[word], 1)

    return string


def latex_to_text_func(string: str) -> (str, bool):
    """
    Translate latex into text. We import the latex_to_text dic here so that
    the selected language is applied even if it has changed since the launch
    of deaduction.
    """
    from .display_data import latex_to_text
    # for macro in latex_to_text:
    #     if macro in string:
    #         text_string = string.replace(macro, latex_to_text[macro])
    #         return text_string, True
    striped_string = string.strip()  # Remove spaces
    if striped_string in latex_to_text:
        text_stripped = latex_to_text[striped_string]
        text_string = string.replace(striped_string, text_stripped)
        return text_string, True
    return string, False


def shallow_latex_to_text(abstract_string: Union[list, str], text_depth=0) \
        -> Union[list, str]:
    """
    Try to change symbols for text in a tree representing some MathObject,
    but only until depth given by text_depth. The deepest branches are left
    untouched (so they still contain latex macro that are NOT suitable to
    display without either latex compilation or conversion to utf8).
    """
    if isinstance(abstract_string, list):
        # Stop conversion to text in some cases
        if abstract_string[0] == r'\no_text':
            text_depth = 0
        # Recursion
        abstract_string = [shallow_latex_to_text(item, text_depth-1) for
                           item in abstract_string]
        # log.debug(f"    --> Shallow_to_text: {string}")
        return abstract_string

    elif isinstance(abstract_string, str):
        if text_depth > 0:  # Try to convert to text
            string, success = latex_to_text_func(abstract_string)
            if success:  # Add a tag to indicate this is text (not math).
                string = [r'\text', string]
        else:  # Try to shorten
            string = shorten(abstract_string)
        return string



