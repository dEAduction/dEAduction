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

# TODO: add a fake_math_object attribute when display format is too
#  different from lean, e.g. for set families
#  this would be used for display, but the original format is kept for
#  coherence with Lean
# TODO: test for text_depth
# TODO: improve text quantifiers, text belongs to

import logging
from typing import Any
from dataclasses import dataclass

import deaduction.pylib.logger              as logger
from deaduction.pylib.config.i18n import _

from deaduction.pylib.mathobj.give_name     import give_local_name
from .display_data import ( latex_from_constant_name,
                            text_from_node,
                            text_from_quant_node,
                            lean_from_node,
                            latex_from_node,
                            latex_from_quant_node,
                            latex_to_utf8_dic,
                            latex_to_lean_dic,
                            needs_paren
                            )

log = logging.getLogger(__name__)


@dataclass
class Shape:
    """
    Class used to compute the display of some MathObject.
    Example: if node = 'PROP_EQUAL',
    - as a first step the shape will have display attribute [0, " = ", 1]
    (as a result of the from_math_object() class method)
    - as a second step, this display will be expanded with '0' and '1' replaced
    by the shapes of the children (by the expand_from_shape() method)

    To distinguish expanded vs non expanded forms, the latter is usually named
    "raw_shape" instead of "shape".

    display_not contains a prettier negated version of display, if available.
    """

    display:                    list
    #   e.g. [0, " = ", 1] (raw_shape), or ['A', " = ", 'B'] (expanded_shape)
    math_object:                Any
    #   The MathObject to be displayed
    format_:                    str         = 'latex'
    #   Supported Format: 'latex', 'utf8', 'lean', 'text'.
    text_depth:                 int         = 0
    #   depth until which a text version should be displayed if available.
    display_not:                list        = None
    all_app_arguments:          list        = None
    #   Contains supplementary children if needed. See display_application.
    negate:                     bool        = False
    #   When negate is True, try to compute display_not instead of display.

    @classmethod
    def from_math_object(cls,
                         math_object: Any,
                         format_="latex",
                         text_depth=0,
                         negate=False):
        """
        This function essentially looks in the format_from_node
        dictionary, and then pass the result to the from_shape method
        which recursively computes the display. If node is not found,
        then it calls the from_specific_nodes method.
        If format_='utf8' then the latex shape is converted to utf8
        by the latex_to_utf8 method before being expanded.

        :param math_object: the MathObject instance to be displayed
        :param format_:     "utf8", "latex", "lean", "text"
        :param text_depth:  when format_="latex" or "utf8", only the symbols at
                            level less than text_depth in the tree are replaced
                            by text. So for instance   "text_depth=0"
                            uses only symbols ; this is used to display context

        :return:            an (expanded) shape, whose display attribute is a
                            structured string, to be transform into a string by
                            the structured_display_to_string function
        """
        log.debug(f"Computing shape of {math_object}")
        if format_ not in ["latex", 'utf8', "lean"]:
            return shape_error(f"unknown format = {format_}")

        node = math_object.node
        if format_ == "lean" and node in lean_from_node:
            raw_shape = Shape(display=list(lean_from_node[node]),
                              math_object=math_object,
                              format_=format_)

        elif node in text_from_node and text_depth > 0:
            raw_shape = Shape(display=list(text_from_node[node]),
                              math_object=math_object,
                              format_=format_)

        elif node in latex_from_node:
            raw_shape = Shape(display=list(latex_from_node[node]),
                              math_object=math_object,
                              format_=format_)

        else:  # Node not found in dictionaries: try specific methods
            raw_shape = Shape.from_specific_nodes(math_object,
                                                  format_,
                                                  text_depth
                                                  )

        # From now on shape is an instance of Shape, with latex format
        if format_ == "lean" and node not in lean_from_node:
            raw_shape.latex_to_lean()
        elif format_ == "utf8":
            raw_shape.latex_to_utf8()
        elif format == "latex" and text_depth <= 0:
            raw_shape.text_to_latex()

        # Finally expand raw_shape
        raw_shape.expand_from_shape(negate=negate)
        return raw_shape  # Now expanded

    @classmethod
    def from_specific_nodes(cls, math_object, format_, text_depth):
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

        :return:            A raw shape
        """

        node = math_object.node
        display = []
        shape = None
        if node == "No more goal":
            display = _("All goals reached!")
        elif node == "APPLICATION":
            # This one returns a shape, to handle supplementary children
            shape = shape_from_application(math_object, format_)
        elif node in ["LOCAL_CONSTANT", "CONSTANT"]:
            # ! Return display, not shape
            display = display_constant(math_object, format_)
        elif node == 'NUMBER':
            display = display_number(math_object, format_)
        elif math_object.is_quantifier(is_math_type=True):
            display = display_quantifier(math_object, format_, text_depth)
        elif node == "LAMBDA":
            display = display_lambda(math_object, format_)
        elif node == "SET_UNIVERSE":
            display = [math_object.math_type_child_name(format_)]
        elif node == "SET_COMPLEMENT":
            universe = math_object.math_type_child_name(format_)
            display = [universe, r" \backslash ", 0]
        if display:
            shape = Shape(display,
                          math_object,
                          format_,
                          text_depth)
        if shape:
            return shape
        else:
            return shape_error("unknown object")

    def expand_from_shape(self, negate=False):
        """
        Expand the shape: in self.display,
        (1) replace numbers by display of corresponding children
        (2) take care of subscript/superscript
        (3) takes care of display of "\\in" according to context

        if negate is True, this indicates that it is the negation that we
        need: display_not will be expanded instead of display
        (except if display_not is None).
        This is effective for instance for properties to display
        'f is not injective' instead of 'NOT (f is injective)'.

        :return: a modified instance of Shape with expanded display
        """
        format_not = (latex_from_node["PROP_NOT"][0],
                      text_from_node["PROP_NOT"][0])
        # log.debug(f"Expanding shape {self.display}")
        if negate and self.display_not:
            # Negation will be computed if required and possible
            display =      self.display_not
        else:
            display = self.display
        math_object =  self.math_object
        format_ =      self.format_
        text_depth =   self.text_depth
        if math_object:  # Math_object is None if shape = error_shape
            children = math_object.children

        # Case of supplementary children (when node == "APPLICATION")
        if self.all_app_arguments:
            children = self.all_app_arguments

        # Successively expand each item in display list
        expanded_display = []
        counter = -1
        subscript = False
        superscript = False
        negate_child = False
        for item in display:
            counter += 1
            display_item = item

            # (1) Integers code for children, or tuples for grandchildren
            if isinstance(item, int):
                child = children[item]
            elif isinstance(item, tuple):  # DO NOT call this when item was int
                # (case of supplementary children from 'application' node)
                child = math_object.descendant(item)
            if isinstance(item, int) or isinstance(item, tuple):
                # Recursively get shape for child
                shape = Shape.from_math_object(math_object=child,
                                               format_=format_,
                                               text_depth=text_depth - 1,
                                               negate=negate_child
                                               )
                display_item = shape.display
                if negate_child and shape.display_not:
                    # If negation has already been incorporated in display:
                    expanded_display.pop()  # remove the 'not' before item
                negate_child = False

                # In parentheses?
                if text_depth < 1:
                    if needs_paren(math_object, child, item):
                        display_item = ['('] + display_item + [')']

            # (2) Strings: handling "belongs to", and negations
            elif isinstance(item, str):
                if r"\in" in item:  # NB: '\in' is kept even when format='utf8'
                    # Replace "∈" with ":" in some cases
                    if (counter + 1 < len(display)
                            and (isinstance(display[counter + 1], int)
                                 or isinstance(display[counter + 1], tuple))):
                        type_ = math_object.descendant(display[counter + 1])
                    else:
                        type_ = "unknown"
                    symbol = display_belongs_to(type_, format_, text_depth)
                    display_item = item.replace(r"\in", symbol)
                elif item in format_not:
                    # Next item will be negated prettily if possible
                    negate_child = True
            # (3) Handling subscript and superscript
            if counter > 0:
                if display[counter - 1] == '_':
                    subscript = True
                elif display[counter - 1] == '^':
                    superscript = True
            if subscript or superscript:
                expanded_display.pop()  # remove the '_'/'^' in last entry
                display_item = text_to_subscript_or_sup(display_item,
                                                        format_,
                                                        sup=superscript)
                subscript = False
                superscript = False

            expanded_display.append(display_item)

        # Finally: remove unnecessary nesting, and replace display
        if len(expanded_display) == 1 and isinstance(expanded_display[0],
                                                     list):
            expanded_display = expanded_display[0]

        self.display = expanded_display

    def latex_to_utf8(self):
        """
        Call latex_to_utf8_dic to replace each item in self by utf8 version.
        """
        display = self.display
        # log.debug(f"convert {display} to utf8")
        for string, n in zip(display, range(len(display))):
            if isinstance(string, str):
                striped_string = string.strip()  # remove spaces
                if striped_string in latex_to_utf8_dic:
                    utf8_string = latex_to_utf8_dic[striped_string]
                    utf8_string = string.replace(striped_string, utf8_string)
                    display[n] = utf8_string

    def latex_to_lean(self):
        """
        Call latex_to_lean dictionary.
        """
        display = self.display
        for string, n in zip(display, range(len(display))):
            if isinstance(string, str):
                striped_string = string.strip()  # remove spaces
                if striped_string in latex_to_lean_dic:
                    lean_string = latex_to_lean_dic[striped_string]
                    lean_string = string.replace(striped_string, lean_string)
                    display[n] = lean_string
                elif striped_string in latex_to_utf8_dic:
                    lean_string = latex_to_utf8_dic[striped_string]
                    lean_string = string.replace(striped_string,
                                                 lean_string)
                    display[n] = lean_string

    def text_to_latex(self):
        """
        For each string item in self which is pure text,
        add "\text{}" around item.
        """
        display = self.display
        for item, n in zip(display, range(len(display))):
            if isinstance(item, str):
                latex_item = string_to_latex(item)
                display[n] = latex_item


#########################################################################
#########################################################################
# Specific display functions, called by from_specific_node              #
#########################################################################
#########################################################################
# display_constant for "CONSTANT" and "LOCAL_CONSTANT"
# shape_from_application for "APPLICATION"
# display_set_family (called by display_constant when needed)
# display_lambda
def shape_from_application(math_object,
                           format_,
                           all_app_arguments=None
                           ) -> Shape:
    """
    Provide display for node 'APPLICATION'
    This is a very special case, includes e.g.
    - APP(injective, f)                     -> f is injective
    - APP(APP(composition, f),g)            -> r"f \\circ g"
    - APP(f, x)                             -> f(x)
    - APP(APP(APP(composition, f),g),x)     -> r"f \\circ g (x)"

    :param all_app_arguments: use to transform
                                            APP(APP(...APP(x0,x1),...,xn)
                                    into
                                            APP(x0, x1, ..., xn)
    """

    # log.debug(f"shape from app {math_object.display_debug}")
    if all_app_arguments is None:
        all_app_arguments = []
    first_child     = math_object.children[0]
    second_child    = math_object.children[1]
    all_app_arguments.insert(0, second_child)

    # (1) Call the function recursively until all args are in
    # all_app_arguments
    if first_child.node == "APPLICATION":
        return shape_from_application(first_child,
                                      format_,
                                      all_app_arguments)
    # Finally insert first child at first position
    all_app_arguments.insert(0, first_child)

    display = [0]  # Default = display first child as a function
    display_not = None

    # (2) Case of index notation: sequences, set families
    if first_child.math_type.node in ["SET_FAMILY", "SEQUENCE"]:
        # APP(E, i) -> E_i
        # we DO NOT call display for first_child because we just want
        #  "E_i",       but NOT       "{E_i, i ∈ I}_i"      !!!
        # We just take care of two cases of APP(E,i) with either
        # (1) E a local constant, or
        # (2) E a LAMBDA with body APP(F, j) with F local constant
        name = 0  # Default case
        if first_child.node == "LOCAL_CONSTANT":
            name = first_child.display_name
        if first_child.node == "LAMBDA":
            body = first_child.children[2]
            if body.node == "APPLICATION" and body.children[0].node == \
                    "LOCAL_CONSTANT":
                name = body.children[0].display_name
            else:
                name = '*set_family*'
        display = [name, '_', 1]

    # (3) Case of constants, e.g. APP(injective, f)
    elif first_child.node == "CONSTANT":
        name = first_child.display_name
        if name in latex_from_constant_name:
            # Damn bug, I got you!!!!!
            display = list(latex_from_constant_name[name])
            pass
        else:  # Standard format
            display = list(latex_from_constant_name['STANDARD_CONSTANT'])
            display_not = list(latex_from_constant_name[
                                   'STANDARD_CONSTANT_NOT'])

    # (4) Finally: use functional notation for remaining arguments
    # ONLY if they are not type
    # first search for unused children
    # search for least used child
    least_used_child = 0
    for item in display:
        if isinstance(item, int):
            if item < 0:  # Negative values forbid supplementary arguments
                least_used_child = len(all_app_arguments) + 10
            if item > least_used_child:
                least_used_child = item

    # Keep only those unused_children whose math_type is not TYPE
    more_display = []
    for n in range(least_used_child+1, len(all_app_arguments)):
        math_type = all_app_arguments[n].math_type
        if not hasattr(math_type, 'node') or not math_type.node == 'TYPE':
            more_display.append(n)
    if more_display:
        display += ['('] + more_display + [')']
        # NB: in generic case APP(f,x), this gives  ['(', 1, ')']
    # names = [item.display_name for item in all_app_arguments]
    # log.debug(f"all arguments : {names}")
    # log.debug(f"more display: {more_display}")
    # log.debug(f"display: {display}")

    raw_shape = Shape(display=display,
                      display_not=display_not,
                      math_object=math_object,
                      format_=format_,
                      all_app_arguments=all_app_arguments
                      )
    return raw_shape


def display_constant(math_object, format_) -> list:
    """
    Display for nodes 'CONSTANT' and 'LOCAL_CONSTANT'
    NB: expressions APP(constant, ...) are treated directly in
    display_application.

    :param math_object:
    :param format_:
    :return:            'display' list
    """
    display = [math_object.display_name]  # generic case
    if hasattr(math_object.math_type, "node"):
        if math_object.math_type.node == "SET_FAMILY":
            display = display_set_family(math_object, format_)
        elif math_object.math_type.node == "SEQUENCE":
            display = "*SEQ*"  # todo

    return display


def display_number(math_object, format_) -> list:
    """
    Display for nodes 'NUMBER'.

    :param math_object:
    :param format_:
    :return:            'display' list
    """
    display = [math_object.info['value']]
    return display


def display_quantifier(math_object, format_="latex", text_depth=0) -> list:
    """
    Display quantifiers, in particular handles the case of
    "
    ∀ x >0, ...
    which is encoded by Lean as
    ∀ x:R, (x>0 ==> ...)
    but should be displayed as above.
    """

    # TODO: handle format='text'

    node = math_object.node
    children = math_object.children
    if text_depth > 0:
        display = list(text_from_quant_node[node])
    else:
        display = list(latex_from_quant_node[node])
    variable = children[1]
    potential_implication = children[2]

    # The following tests if math_object has the form
    # ∀ x:X, (x R ... ==> ...)
    # where R is some inequality relation
    if potential_implication.is_implication(is_math_type=True):
        premise = potential_implication.children[0]  # children (2,0)
        if premise.is_inequality(is_math_type=True):
            item = premise.children[0]
            if item == variable:
                quantifier = display[0]
                display = [quantifier, (2, 0), ", ", (2, 1)]
    return display


def display_lambda(math_object, format_="latex") -> list:
    """
    Display lambda expression, e.g.
    - set families with explicit bound variable
        lambda (i:I), E i
        encoded by LAMBDA(I, i, APP(E, i)) --> "{E_i, i ∈ I}"
    - sequences,
    - mere functions
        encoded by LAMBDA(X, x, APP(f, x))  --> "f"
    - anything else is displayed as "x ↦ f(x)"
    """

    math_type = math_object.math_type
    _, var, body = math_object.children
    # log.debug(f"display LAMBDA with var, body, type = {var, body,
    # math_type}")
    if math_type.node == "SET_FAMILY":
        display = [r'\{', 2, ', ', 1, r' \in ', 0, r'\}']
    elif math_type.node == "SEQUENCE":
        display = ['(', 2, ')', '_', 1, r' \in ', 0, '}']
        # todo: manage subscript
    elif body.node == "APPLICATION" and body.children[1] == var:
        # Object is of the form x -> f(x)
        mere_function = body.children[0]  # this is 'f'
        # We call the whole process in case 'f' is not a LOCAL_CONSTANT
        display = Shape.from_math_object(mere_function, format_).display
    else:  # Generic display
        display = [1, '↦', 2]
    if not display:
        display = ['*unknown lambda*']
    # log.debug(f"--> {display}")
    return display


# The following is not called directly, but via display_constant
def display_sequence(math_object, format_="latex") -> list:
    # TODO: on the model of display_set_family
    pass


def display_set_family(math_object, format_="latex") -> list:
    """
    A set family is usually encoded in Lean as an object E of type
    I -> set X,
    and Lean just display 'E'.
    We compute a good name for an index in I (e.g. 'i'),
    and display "{E_i, i in I}".

    FIXME: this bound variable is not referenced anywhere, in particular
     it will not appear in extract_local_vars.
    """
    # First find a name for the bound var
    # log.debug(f"Display set family")
    name = math_object.display_name
    math_type_name = math_object.math_type_child_name(format_)
    bound_var_type = math_object.math_type.children[0]
    index_name = give_local_name(math_type=bound_var_type,
                                 body=math_object)
    display = [r"\{", name, '_', index_name, ', ',
               index_name, r" \in ", math_type_name, r"\}"]
    return display


##################
# Other displays #
##################
# This function is called directly by MathObject.to_display
# Thus it has to return an EXPANDED shape
def display_math_type_of_local_constant(math_type,
                                        format_,
                                        text_depth=0) -> Shape:
    """
    Process special cases, e.g.
    (1) x : element of X"
     In this case   math_object represents x,
                    math_object.math_type represents X,
                    and the analysis is based on the math_type of X.
    (2) A : subset of X

    :param math_type:       MathObject
    :param format_:         as usual
    :param text_depth:      int
    :return:                shape with expanded display
    """
    ########################################################
    # Special math_types for which display is not the same #
    ########################################################
    display = []
    if hasattr(math_type, 'math_type') \
            and hasattr(math_type.math_type, 'node') \
            and math_type.math_type.node == "TYPE":
        name = math_type.info["name"]
        if text_depth > 0:
            display = [_("an element of") + " ", name]
        else:
            display = [_("element of") + " ", name]
    elif hasattr(math_type, 'node') and math_type.node == "SET":
        if text_depth > 0:
            display = [_("a subset of") + " ", 0]
        else:
            display = [_("subset of") + " ", 0]
    if display:
        raw_shape = Shape(display=display,
                          math_object=math_type,
                          format_=format_,
                          text_depth=text_depth
                          )
    #################
    # Generic case  #
    #################
    else:  # Compute Shape from math_object
        raw_shape = Shape.from_math_object(math_object=math_type,
                                           format_=format_,
                                           text_depth=text_depth
                                           )
    raw_shape.expand_from_shape()
    return raw_shape


######################
######################
# auxiliary displays #
######################
######################
def display_belongs_to(math_type: Any, format_, text_depth, belonging=True) \
        -> str:
    """
    Compute the adequate shape for display of "x belongs to X", e.g.
    - generically, "x∈X"
    - specifically,
        - "f : X -> Y" (and not f ∈ X-> Y),
        or "f is a function from X to Y"
        - "P: a proposition" (and not P ∈ a proposition),

        :param math_type:   MathObject or "unknown"
        :param format_:     as usual
        :param text_depth:  int
        :param belonging:   fixme: unused
        :return:
    """

    # log.debug(f"display ∈ with {math_type}, {format_}, {text_depth}")
    # if 'unknown' == math_type:  # should not happen anymore
    #    if format_ in ('utf8', 'lean'):
    #        return "∈"
    # from now on math_type is an instance of MathObject
    if math_type is 'unknown':
        if text_depth > 0:
            symbol = _("is")
        else:
            symbol = "∈" if format_ == "utf8" else r"\in"
        return symbol
    if text_depth > 0:
        if math_type.is_prop(is_math_type=True) \
                or math_type.is_type(is_math_type=True) \
                or (math_type.is_function(is_math_type=True)
                    and text_depth > 1):
            symbol = _("is")
        elif math_type.is_function(is_math_type=True) and text_depth == 1:
            symbol = ":"
        else:
            symbol = _("belongs to")
    else:
        if math_type.is_function(is_math_type=True) \
                or math_type.is_prop(is_math_type=True) \
                or math_type.is_type(is_math_type=True):
            symbol = ":"
        else:
            symbol = "∈" if format_ == "utf8" else r"\in"
    return symbol


def string_to_latex(string: str):
    """Put the "\text" command around pure text for Latex format"""
    if string.isalpha():
        string = r"\text{" + string + r"}"
    return string


#######################################
#######################################
# Some tools for manipulating strings #
#######################################
#######################################
def text_to_subscript_or_sup(structured_string,
                             format_="latex",
                             sup=False
                             ):
    """
    Convert structured_string to subscript of superscript

    :param structured_string:   list
    :param format_:             "latex" or "utf8" or "lean"
    :param sup:                 True if superscript, else subscript
    :return:                    list, converted structured string
    """
    # log.debug(f"converting into sub/superscript {structured_string}")
    if format_ == 'latex':
        if sup:
            return [r'^{', structured_string, r'}']
        else:
            return [r'_{', structured_string, r'}']
    else:
        sub_or_sup, is_subscriptable = recursive_subscript(structured_string,
                                                           sup)
        if not is_subscriptable:
            if sup:
                sub_or_sup = ['^'] + [structured_string]
            else:
                sub_or_sup = ['_'] + [structured_string]
            # [sub] necessary in case sub is an (unstructured) string
        # log.debug(f"--> {sub_or_sup}")
        return sub_or_sup


SOURCE = {'sub': " 0123456789" + "aeioruv",
          'sup': " -1"}
TARGET = {'sub': " ₀₁₂₃₄₅₆₇₈₉" + "ₐₑᵢₒᵣᵤᵥ",
          'sup': " ⁻¹"}


def recursive_subscript(structured_string, sup):
    """
    Recursive version, for strings to be displayed use global_subscript instead
    This is not for latex format.

    :param structured_string:   list of structured string
    :param sup:                 bool
    :return: the structured string in a subscript version if available,
                or the structured string unchanged if not,
                and a boolean is_subscriptable
    """
    is_subscriptable = True
    if isinstance(structured_string, list):
        sub_list = []
        for item in structured_string:
            sub, still_is_sub = recursive_subscript(item, sup)
            if not still_is_sub:  # Not subscriptable
                return structured_string, False
            else:
                sub_list.append(sub)
        return sub_list, True

    # From now on structured_string is assumed to be a string
    style = 'sup' if sup else 'sub'
    for letter in structured_string:
        if letter not in SOURCE[style]:
            is_subscriptable = False
    if is_subscriptable:
        subscript_string = ""
        for letter in structured_string:
            pos = SOURCE[style].index(letter)
            subscript_string += TARGET[style][pos]
    else:
        subscript_string = structured_string
    return subscript_string, is_subscriptable


def display_text_quant(math_object, format_, text_depth):
    """
    Compute a smart text version of a quantified sentence.

    :param math_object: a math object with node "QUANT_∀", "QUANT_∃", or
                        "QUANT_∃!".
    :param format_:     "text+utf8"
    :param text_depth:  see display_math_object
    """

    # TODO
    pass


def display_text_belongs_to(math_object, format_, text_depth):
    """Compute a smart text version of 'belongs to'.

    :param math_object: a math object whose node is "PROP_BELONGS"
    :param format_:     "text+utf8"
    :param text_depth:  see display_math_object
    """

    # TODO
    pass


def shape_error(message: str, math_object=None, format_="", text_depth=0):
    shape = Shape(['*' + message + '*'],
                  math_object,
                  format_,
                  text_depth)
    return shape

