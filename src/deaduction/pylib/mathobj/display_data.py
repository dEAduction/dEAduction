"""
##########################################################################
# display_data.py : data for displaying MathObject, used by display_math #
##########################################################################

    This file provides dictionaries for converting MathObjects into strings:
    - latex_from_node, latex_from_quant_node, latex_from_constant_name
    - lean_from_node,
    - latex_to_utf8_dic,
    - latex_to_lean,
    - text_from_node, text_from_quant_node

    It also provides the function needs_paren.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 11 2020 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the d∃∀duction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    d∃∀duction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""
from typing import Union

# from deaduction.pylib.config.i18n import _

# !! Latex commands should be alone in their strings,
# except for spaces around them, so that up to strip(), they appear in
# latex_to_utf8_dic

global _
# FIXME: just for debug, remove!!
# _ = lambda x: x

######################
######################
# LATEX dictionaries #
######################
######################
latex_from_node = {
    "PROP_AND": (0, " " + _("and") + " ", 1),
    "PROP_OR": (0, " " + _("or") + " ", 1),
    "PROP_FALSE": (r"\false", ),  # Macro to be defined
    "PROP_IFF": (0, r" \Leftrightarrow ", 1),
    "PROP_NOT": (r"\not", 0),  # Macro to be define
    # '\if' is just here for text mode:
    "PROP_IMPLIES": (r'\if', 0, r" \Rightarrow ", 1),
    # "∃ (H : P), Q" is treated as "P and Q",
    # and also handled by the 'AND' button
    "PROP_∃":  (0, " " + _("and") + " ", 1),
    ###############
    # SET THEORY: #
    ###############
    "PROP_INCLUDED": (0, r" \subset ", 1),
    "PROP_BELONGS": (0, r" \in ", 1),
    "PROP_NOT_BELONGS": (0, r" \not\in ", 1),
    "SET_INTER": (0, r" \cap ", 1),  # !! small ∩
    "SET_UNION": (0, r" \cup ", 1),  #
    "SET_INTER+": (r"\bigcap", 0),  # !! big ⋂
    "SET_UNION+": (r"\bigcup", 0),
    "SET_DIFF": (0, r" \backslash ", 1),
    "SET_DIFF_SYM": (0, r" \Delta ", 1),
    "SET_EMPTY": (r"\emptyset",),
    "SET_EXTENSION1": (r'\{', 0, r'\}'),
    "SET_EXTENSION2": (r'\{', 0, ', ', 1, r'\}'),
    "SET_EXTENSION3": (r'\{', 0, ', ', 1, ', ', 2, r'\}'),
    "SET_FAMILY": (0,  r" \to ", r'{\mathcal P}', r'\parentheses', 1),
    # "SET_IMAGE": (0, "(", 1, ")"),
    # "SET_INVERSE": (0, [r'^', '-1'], '(', 1, ')'),  # LEAVE the list as is!
    "SET_IMAGE": (0, r'\set_image', 1),
    "SET_INVERSE": (0, r'\set_inverse', 1),
    "SET_PRODUCT": (0, r'\times', 1),
    "COUPLE": ('(', 0, ',', 1, ')'),
    "SET_INTENSION": (r'\{', 1, r' \in ', 0, ' | ', 2, r'\}'),
    # FIXME: instantiate set extensions
    ############
    # NUMBERS: #
    ############
    "COE": (0,),    # We do not want to see bindings
    "PROP_EQUAL": (0, " = ", 1),
    "PROP_EQUAL_NOT": (0, r" \neq ", 1),  # todo
    "PROP_<": (0, " < ", 1),
    "PROP_>": (0, " > ", 1),
    "PROP_≤": (0, r" \leq ", 1),
    "PROP_≥": (0, r" \geq ", 1),
    "DIFFERENCE": (0, " - ", 1),
    "SUM": (0, " + ", 1),
    "MULT": (0, r" \times ", 1),
    "PRODUCT": (0, r" \times ", 1),
    "DIV": (0, r"/", 1),
    "MINUS": ("-", 0),
    ##################
    # GENERAL TYPES: #
    ##################
    "SET": (r'\set_of_subsets', 0),  # (r'{\mathcal P}', "(", 0, ")"),
    "PROP": (r'\proposition',),
    "TYPE": (r'\set',),
    "FUNCTION": (r'\function_from', 0, r'\to', 1),  # (0, r" \to ", 1),
    "SEQUENCE": (r'\sequence_from', 0, r'\to', 1)  # (0, r" \to ", 1),
}

# \in_quant --> "belonging to", or "in" in text mode (but NOT "belongs to")
latex_from_quant_node = {
    "QUANT_∀": (r"\forall", 1, r" \in_quant ", 0, ", ", 2),
    "QUANT_∃": (r"\exists", 1, r" \in_quant ", 0, r'\such_that', 2),
    "PROP_∃": ("*PROP_∃*",),
    "QUANT_∃!": (r"\exists !", 1, r" \in_quant ", 0, r'\such_that', 2)
}

# Negative value = from end of children list
latex_from_constant_name = {
    "STANDARD_CONSTANT": (-1, " " + _("is") + " ", 0),
    "STANDARD_CONSTANT_NOT": (-1, " " + _("is not") + " ", 0),
    # NB: STANDARD_CONSTANT prevents supplementary arguments,
    # Do not use with a CONSTANT c s.t. APP(c, x) is a FUNCTION,
    # or anything that can be applied (i.e. in APP(APP(c,x),...) )
    "symmetric_difference": (-2, r'\Delta', -1),
    "composition": (4, r'\circ', 5),  # APP(compo, X, Y, Z, g, f)
    "prod": (1, r'\times', 2),
    "Identite": ("Id",),
    "ne": (2, r" \neq ", 3),  # Lean name for ≠
    "interval": (r"\[", -2, ",", -1, r"\]"),
    "majorant": (-1, " majorant de ", -2),
    "minorant": (-1, " minorant de ", -2),
    "borne_sup": ("Sup", -2, " = ", -1),
    "borne_inf": ("Inf", -2, " = ", -1),
    "est_majore": (-1, " majoré"),
    "est_minore": (-1, " minoré"),
    "est_borne": (-1, " borné"),
    "limite": ("lim", -2, " = ", -1),
    "abs": ('|', -1, '|'),
    "max": ("Max", [r'\parentheses', -2, ",", -1])
}

###################
###################
# UTF8 dictionary #
###################
###################
# Convert Latex command into utf8 symbols
latex_to_utf8_dic = {
    r'\backslash': '\\',
    r'\Delta': '∆',
    r'\circ': '∘',
    r'\times': '×',
    r'\in': '∈',
    r'\in_quant': '∈',
    r"\in_symbol": '∈',
    r'\in_prop': ":",
    r'\in_set': ":",
    r'\in_function': ":",
    r'\Leftrightarrow': '⇔',
    r'\Rightarrow': '⇒',
    r'\forall': '∀',
    r'\exists': '∃',
    r'\exists !': '∃!',
    r'\subset': '⊂',
    r'\not\in': '∉',
    r'\cap': '∩',
    r'\cup': '∪',
    r'\bigcap': '⋂',
    r'\bigcup': '⋃',
    r'\emptyset': '∅',
    r'\to': '→',
    r'\neq': '≠',
    r'\leq': '≤',
    r'\geq': '≥',
    r'\set_of_subsets': 'P',
    r'\{': '{',
    r'\}': '}',
    r'\[': '[',
    r'\]': ']',
    r'\false': _("Contradiction"),
    r'\proposition': _("proposition"),
    r'\set': _("set"),
    r'\not': _("not") + " ",
    r'\set_image': "",
    r'\set_inverse': [r'^', '-1'],
    r'\if': "",  # '\if' is just here for text mode
    r'\such_that': ", ",
    r'\function_from': ""
                    }


#####################
#####################
# TEXT dictionaries #
#####################
#####################
latex_to_text = {
    r'\Leftrightarrow': " " + _("if and only if") + " ",
    r'\not': _("the negation of") + " ",
    r'\if': _("if") + " ",
    r'\Rightarrow': _("then"),
    r'\set_of_subsets': _("the set of subsets of") + " ",
    r'\proposition': _("a proposition"),
    r'\set': _("a set"),
    r'\such_that': " " + _("such that") + " ",
    r'\forall': _("for all") + " ",
    r'\exists': _("there exists") + " ",
    r"\exists !": _("there exists a unique") + " ",
    r'\function_from': " " + _("a function from") + " ",
    r'\sequence_from': " " + _("a sequence from") + " ",  # FIXME...
    r'\to': " " + _("in") + " ",
    # r'\in': " " + _("belongs to") + " ",
    r'\in_prop': " " + _("is") + " ",
    r'\in_set': " " + _("is") + " ",
    r'\in_function': " " + _("is") + " ",
    r'\in_quant': " " + _("in") + " ",
}


text_from_node = {
    # # "PROP_AND": (0, " " + _("and") + " ", 1),
    # # "PROP_OR": (0, " " + _("or") + " ", 1),
    # # "PROP_FALSE": (_("Contradiction"), ),
    # "PROP_IFF": (0, " " + _("if and only if") + " ", 1),
    # "PROP_NOT": (_("the negation of") + " ", 0),
    # "PROP_IMPLIES": (_("if") + " ", 0, " " + _("then") + " ", 1),
    ###############
    # SET THEORY: #
    ###############
    # "PROP_INCLUDED": (0, " " + _("is included in") + " ", 1),
    # "PROP_BELONGS": (0, " ∈ ", 1),  # This special case is processed in
                                    # the function display_belongs_to
    # "SET_INTER": (_("the intersection of") + " ", 0, " " + _("and") + " ",
    # 1),
    # "SET_UNION": (_("the union of") + " ", 0, " " + _("and") + " ", 1),
    # "SET_INTER+": (_("the intersection of the sets") + " ", 0),
    # "SET_UNION+": (_("the union of the sets") + " ", 0),
    # "SET_COMPLEMENT": (_("the complement of ") + " ", 0),
    # "SET_EMPTY": (_("the empty set"),),
    # "SET_FAMILY": (_("a family of subsets of") + " ", 1),
    # "SET_IMAGE": (_("the image under") + " ", 0, " " + _("of") + " ", 1),
    # "SET_INVERSE": (_("the inverse image under") + " ", 0, " " + _("of") +
    # " ", 1),
    ############
    # NUMBERS: #
    ############
    # "PROP_EQUAL": (0, " " + _("equals") + " ", 1),
    # "PROP_EQUAL_NOT": (0, " " + _("is different from") + " ", 1),
    # "PROP_<": (0, " " + _("is less than") + " ", 1),
    # "PROP_>": (0, " " + _("is greater than") + " ", 1),
    # "PROP_≤": (0, " " + _("is less than or equal to") + " ", 1),
    # "PROP_≥": (0, " " + _("is greater than or equal to") + " ", 1),
    ##################
    # GENERAL TYPES: #
    ##################
    # "SET": ("P(", 0, ")"),
    # "PROP": (_("a proposition"),),
    # "TYPE": (_("a set"),),
    # "FUNCTION": (_("a function from") + " ", 0, " " + _("to") + " ", 1),
}

text_from_all_nodes = {
    "PROP_AND": (0, " " + _("and") + " ", 1),
    "PROP_OR": (0, " " + _("or") + " ", 1),
    "PROP_FALSE": (_("Contradiction"), ),
    "PROP_IFF": (0, " " + _("if and only if") + " ", 1),
    "PROP_NOT": (_("the negation of") + " ", 0),
    "PROP_IMPLIES": (_("if") + " ", 0, " " + _("then") + " ", 1),
    ###############
    # SET THEORY: #
    ###############
    "PROP_INCLUDED": (0, " " + _("is included in") + " ", 1),
    "PROP_BELONGS": (0, " ∈ ", 1),  # This special case is processed in
                                    # the function display_belongs_to
    "SET_INTER": (_("the intersection of") + " ", 0, " " + _("and") + " ", 1),
    "SET_UNION": (_("the union of") + " ", 0, " " + _("and") + " ", 1),
    "SET_INTER+": (_("the intersection of the sets") + " ", 0),
    "SET_UNION+": (_("the union of the sets") + " ", 0),
    "SET_COMPLEMENT": (_("the complement of ") + " ", 0),
    "SET_EMPTY": (_("the empty set"),),
    "SET_FAMILY": (_("a family of subsets of") + " ", 1),
    "SET_IMAGE": (_("the image under") + " ", 0, " " + _("of") + " ", 1),
    "SET_INVERSE": (_("the inverse image under") + " ", 0, " " + _("of") + " ",
                    1),
    ############
    # NUMBERS: #
    ############
    "PROP_EQUAL": (0, " " + _("equals") + " ", 1),
    "PROP_EQUAL_NOT": (0, " " + _("is different from") + " ", 1),
    "PROP_<": (0, " " + _("is less than") + " ", 1),
    "PROP_>": (0, " " + _("is greater than") + " ", 1),
    "PROP_≤": (0, " " + _("is less than or equal to") + " ", 1),
    "PROP_≥": (0, " " + _("is greater than or equal to") + " ", 1),
    ##################
    # GENERAL TYPES: #
    ##################
    "SET": ("P(", 0, ")"),
    "PROP": (_("a proposition"),),
    "TYPE": (_("a set"),),
    "FUNCTION": (_("a function from") + " ", 0, " " + _("to") + " ", 1),
}

text_from_quant_node = {
    "QUANT_∀": (_("for every") + " ", 1, " " + _("in") + " ", 0,
                ", ", 2),
    "QUANT_∃": (_("there exists") + " ", 1, " " + _("in") + " ", 0,
                " " + _("such that") + " ", 2),
    "QUANT_∃!": (_("there exists a unique") + " ", 1, " " + _("in") + " ", 0,
                 " " + _("such that") + " ", 2),
    "PROP_∃": ("*PROP_∃*",)
}


###################
###################
# LEAN dictionary #
###################
###################
# Only those lean symbols that are distinct from the latex_to_utf8 dict
latex_to_lean_dic = {
    #'AND': 'and',
    #'OR': 'or',
    #'NOT': 'not',
    r'\Leftrightarrow': '↔',
    r'\Rightarrow': '→',
    r'\cap': '∩',
    r'\cup': '∪',
    r'\bigcap': '⋂',  # probably useless
    r'\bigcup': '⋃',
    r'\false': 'False',
    r'\proposition': 'Prop',
    r'\set': 'Type',
    "SET_FAMILY": (),  # FIXME: should be lean_name
    r'\set_image': " '' ",
    r'\set_inverse': " ⁻¹' ",
    r'\set_of_subsets': "set"
}


####################
####################
# Helper functions #
####################
####################
# Nodes of math objects that need instantiation of bound variables
HAVE_BOUND_VARS = ("QUANT_∀", "QUANT_∃", "QUANT_∃!", "SET_EXTENSION", "LAMBDA")
INEQUALITIES = ("PROP_<", "PROP_>", "PROP_≤", "PROP_≥", "PROP_EQUAL_NOT")

NATURE_LEAVES_LIST = ("PROP", "TYPE", "SET_UNIVERSE", "SET", "ELEMENT",
                      "FUNCTION", "SEQUENCE", "SET_FAMILY",
                      "TYPE_NUMBER", "NUMBER", "VAR", "SET_EMPTY",
                      "CONSTANT", "LOCAL_CONSTANT", "NONE")


def needs_paren(parent, child, child_number) -> bool:
    """
    Decides if parentheses are needed around the child
    e.g. if math_obj.node = PROP.IFF then
    needs_paren(math_obj, children[i], i)
    will be set to True for i = 0, 1 so that the display will be
    ( ... ) <=> ( ... )

    :param parent:          MathObject
    :param child:           MathObject
    :param child_number:    an integer or a list indicating the line_of_descent
    :return:                bool
    """

    # TODO : tenir compte de la profondeur des parenthèses,
    #   et utiliser Biggl( biggl( Bigl( bigl( (x) bigr) Bigr) biggr) Biggr)

    p_node = parent.node
    c_node = child.node if child is not None else "NONE"
    if (p_node in ("SET", "SET_IMAGE", "SET_INVERSE")
            and child_number == 1):  # P(X), f(A), f^{-1}(A)
        return True
    if c_node in NATURE_LEAVES_LIST:
        return False
    if p_node == 'PROP_NOT':
        return True
    if c_node in ("SET_IMAGE", "SET_INVERSE", "PROP_BELONGS", "PROP_EQUAL",
                  "PROP_EQUAL_NOT", "PROP_≤", "PROP_≥", "PROP_<", "PROP_>",
                  "PROP_INCLUDED", "SET_UNION+", "SET_INTER+"):
        return False
    elif (p_node == "SET_INVERSE"
          and child_number == 0
          and c_node != "LOCAL_CONSTANT"):
        # e.g. (f∘g)^{-1} (x)
        return True
    elif c_node == "APPLICATION":
        return False
    elif p_node in ("SET_IMAGE",  # "SET_INVERSE",
                    "SET_UNION+", "SET_INTER+", "APPLICATION",
                    "PROP_INCLUDED",  "PROP_BELONGS", "PROP_NOT_BELONGS",
                    "LAMBDA",
                    "PROP_EQUAL", "PROP_EQUAL_NOT",
                    "PROP_≤", "PROP_≥", "PROP_<", "PROP_>"):
        return False
    elif p_node.startswith("QUANT"):
        # for tuple as child_number, cf the descendant MathObject method
        if child_number in (0, 1, (0,), (1,), (2, 0)):
            # No parentheses around the variable, the type, or the leading
            # inequality
            return False
        elif c_node.startswith("QUANT"):
            return False
    return True


def latex_to_utf8(string: Union[str, list]):
    """
    Convert a string or a list of string from latex to utf8.
    """
    if isinstance(string, list):
        return [latex_to_utf8(item) for item in string]
    elif isinstance(string, str):
        striped_string = string.strip()  # Remove spaces
        if striped_string in latex_to_utf8_dic:
            utf8_string = latex_to_utf8_dic[striped_string]
            if isinstance(utf8_string, str):
                utf8_string = string.replace(striped_string, utf8_string)
            return utf8_string
        else:
            return string
    else:
        return string
