"""
# display_data.py : <#ShortDescription> #
    
    <#optionalLongDescription>

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

from deaduction.config                      import _

# !! Latex commands should be alone in their strings,
# except for spaces around them, so that up to strip(), they appear in
# latex_to_utf8_dic
latex_from_node = {
    "PROP_AND": [0, " " + _("AND") + " ", 1],
    "PROP_OR": [0, " " + _("OR") + " ", 1],
    "PROP_FALSE": [_("Contradiction"), ],
    "PROP_IFF": [0, r" \Leftrightarrow ", 1],
    "PROP_NOT": [_("NOT") + " ", 0],
    "PROP_IMPLIES": [0, r" \Rightarrow ", 1],
    "QUANT_∀": [r"\forall", 1, r" \in ", 0, ", ", 2],
    "QUANT_∃": [r"\exists", 1, r" \in ", 0, ", ", 2],
    "PROP_∃": "*PROP_∃*",  # should not happen
    "QUANT_∃!": [r"\exists !",  1, r" \in ", 0, ", ", 2],
    ###############
    # SET THEORY: #
    ###############
    "PROP_INCLUDED": [0, r" \subset ", 1],
    "PROP_BELONGS": [0, r" \in ", 1],
    "PROP_NOT_BELONGS": [0, r" \not\in ", 1],
    "SET_INTER": [0, r" \cap ", 1],  # !! small ∩
    "SET_UNION": [0, r" \cup ", 1],  #
    "SET_INTER+": [r"\bigcap", 0],  # !! big ⋂
    "SET_UNION+": [r"\bigcup", 0],
    "SET_DIFF": [0, r" \backslash ", 1],
    "SET_DIFF_SYM": [0, " \Delta ", 1],
    "SET_EMPTY": ["\emptyset"],
    "SET_FAMILY": [_("a family of subsets of") + " ", 1],
    "SET_IMAGE": [0, "(", 1, ")"],
    "SET_INVERSE": [0, '^{-1}', '(', 1, ')'],  # todo: exponent ⁻¹
    "SET_PRODUCT": [0, r'\times', 1],
    "COUPLE": ['(', 0, ',', 1, ')'],
    "SET_EXTENSION": [r'\{', 1, ' \in ', 0, ' | ', 2, r'\}'],
    # FIXME: instantiate set extensions
    ############
    # NUMBERS: #
    ############
    "PROP_EQUAL": [0, " = ", 1],
    "PROP_EQUAL_NOT": [0, r" \neq ", 1],  # todo
    "PROP_<": [0, " < ", 1],
    "PROP_>": [0, " > ", 1],
    "PROP_≤": [0, r" \leq ", 1],
    "PROP_≥": [0, r" \geq ", 1],
    "MINUS": [0, " - ", 1],
    "+": [0, " + ", 1],
    "PRODUCT": [0, r" \times ", 1],
    ##################
    # GENERAL TYPES: #
    ##################
    "SET": ["{\mathcal P}", "(", 0, ")"],
    "PROP": [_("a proposition")],
    "TYPE": [_("a set")],
    "FUNCTION": [0, r" \to ", 1],
                  }

# Lean formats that cannot be deduced from latex
lean_from_node = {  # todo: complete
    "PROP_FALSE": ['False'],
    "SET_INTER+": [],
    "SET_UNION+": [],
    "SET_FAMILY": [],
    "SET_IMAGE": [],
    "SET_INVERSE": [],
    "SET": [],
    "PROP": [],
    "TYPE": []
                  }


# negative value = from end of children list
latex_from_constant_name = {
    "STANDARD": [1, " " + _("is") + " ", 0],
    "symmetric_difference": [-2, r'\Delta', -1],
    "composition": [-2, r'\circ', -1],
    "prod": [0, r'\times', 1],
    "Identite": ["\mathrm{Id}"]
                            }

latex_to_utf8_dic = {  # TODO: complete
    '\Delta': '∆',
    '\circ': '∘',
    r'\times': '×',
    r'\in': '∈',
    r'\LeftRightarrow': '⇔',
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
    r'{\mathcal P}': '𝒫',
    r'\{': '{'
                     }

# only those lean symbols that are not in the latex_to_utf8 dict
latex_to_lean_dic = {
    'AND': '∧',
    'OR': '∨',
    'NOT': '¬',
    r'\LeftRightarrow': '↔',
    r'\Rightarrow': '→',
    r'\cap': '∩',
    r'\cup': '∪',
    r'\bigcap': '⋂',  # probably useless
    r'\bigcup': '⋃'
                    }


text_from_node = {
    "PROP_AND": [0, " " + _("and") + " ", 1],
    "PROP_OR": [0, " " + _("or") + " ", 1],
    "PROP_FALSE": [_("Contradiction"), ],
    "PROP_IFF": [0, " " + _("if and only if") + " ", 1],
    "PROP_NOT": [_("the negation of") + " ", 0],
    "PROP_IMPLIES": [_("if") + " ", 0, " " + _("then") + " ", 1],
    "QUANT_∀": [_("for every") + " ", 1, " " + "in" + " ", 0,
                ", ", 2],
    "QUANT_∃": [_("there exists") + " ", 1, " " + "in" + " ", 0,
                " " + _("such that") + " ", 2],
    ###############
    # SET THEORY: #
    ###############
    "PROP_INCLUDED": [0, " " + _("is included in") + " ", 1],
    "PROP_BELONGS": [0, " ∈ ", 1],  # this special case is processed in
                                    # the function display_belongs_to
    "SET_INTER": [_("the intersection of") + " ", 0, " " + _("and") + " ", 1],
    "SET_UNION": [_("the union of") + " ", 0, " " + _("and") + " ", 1],
    "SET_INTER+": [_("the intersection of the sets") + " ", 0],
    "SET_UNION+": [_("the union of the sets") + " ", 0],
    "SET_COMPLEMENT": [_("the complement of ") + " ", 0],
    "SET_EMPTY": [_("the empty set")],
    "SET_FAMILY": [_("a family of subsets of") + " ", 1],
    "SET_IMAGE": [_("the image under") + " ", 0, " " + _("of") + " ", 1],
    "SET_INVERSE": [_("the inverse image under") + " ", 0, " " + _("of") + " ",
                    1],
    ############
    # NUMBERS: #
    ############
    "PROP_EQUAL": [0, " " + _("equals") + " ", 1],
    "PROP_EQUAL_NOT": [0, " " + _("is different from") + " ", 1],
    "PROP_<": [0, " " + _("is less than") + " ", 1],
    "PROP_>": [0, " " + _("is greater than") + " ", 1],
    "PROP_≤": [0, " " + _("is less than or equal to") + " ", 1],
    "PROP_≥": [0, " " + _("is greater than or equal to") + " ", 1],
    ##################
    # GENERAL TYPES: #
    ##################
    "SET": ["P(", 0, ")"],
    "PROP": [_("a proposition")],
    "TYPE": [_("a set")],
    "FUNCTION": [_("a function from") + " ", 0, " " + _("to") + " ", 1],
}

# nodes of math objects that need instantiation of bound variables
have_bound_vars = ["QUANT_∀", "QUANT_∃", "QUANT_∃!", "SET_EXTENSION", "LAMBDA"]

nature_leaves_list = ["PROP", "TYPE", "SET_UNIVERSE", "SET", "ELEMENT",
                      "FUNCTION", "SEQUENCE", "SET_FAMILY",
                      "TYPE_NUMBER", "NUMBER", "VAR", "SET_EMPTY"]


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
