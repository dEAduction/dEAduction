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

utf8_from_node = {
#    "APPLICATION": [display_application],
#    "LOCAL_CONSTANT": [display_constant],
#    "CONSTANT": [display_constant],
#    "LAMBDA": [display_lambda],

    "PROP_AND": [0, " " + _("AND") + " ", 1],
    "PROP_OR": [0, " " + _("OR") + " ", 1],
    "PROP_FALSE": [_("Contradiction"), ],
    "PROP_IFF": [0, " ⇔ ", 1],
    "PROP_NOT": [_("NOT") + " ", 0],
    "PROP_IMPLIES": [0, " ⇒ ", 1],
    "QUANT_∀": ["∀", 1, " ∈ ", 0, ", ", 2],
    "QUANT_∃": ["∃", 1, " ∈ ", 0, ", ", 2],
    "PROP_∃": "not implemented",
    "QUANT_∃!": ["∃!",  1, " ∈ ", 0, ", ", 2],
    ###############
    # SET THEORY: #
    ###############
    "PROP_INCLUDED": [0, " ⊂ ", 1],
    "PROP_BELONGS": [0, " ∈ ", 1],
    "PROP_NOT_BELONGS": [0, " ∉ ", 1],
#    "SET_UNIVERSE": [display_math_type0],
    "SET_INTER": [0, " ∩ ", 1],  # !! small ∩
    "SET_UNION": [0, " ∪ ", 1],  #
    "SET_INTER+": ["⋂", 0],  # !! big ⋂
    "SET_UNION+": ["⋃", 0],
    "SET_DIFF": [0, r" \ ", 1],
    "SET_DIFF_SYM": [0, " ∆ ", 1],
#    "SET_COMPLEMENT": [display_math_type0, r" \ ", 0],
    "SET_EMPTY": ["∅"],
    "SET_FAMILY": [_("a family of subsets of") + " ", 1],
    "SET_IMAGE": [0, "(", 1, ")"],
    "SET_INVERSE": [0, '⁻¹(', 1, ')'],
    "SET_PRODUCT": [0, '×', 1],
    "COUPLE": ['(', 0, ',', 1, ')'],
    "SET_EXTENSION": ['{', 1, ' ∈ ', 0, ' | ', 2, '}'],  # FIXME: instantiate
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
    "+": [0, "+", 1],
    "PRODUCT": [0, "×", 1],
    ##################
    # GENERAL TYPES: #
    ##################
    "SET": ["P(", 0, ")"],
    "PROP": [_("a proposition")],
    "TYPE": [_("a set")],
    "FUNCTION": [0, " → ", 1],
}

# negative value = pending parameter
format_from_constant_name = {
    "symmetric_difference": [-1, '∆', -2],
    "composition": [-1, '∘', -2],
    "prod": [-1, '×', -2],  # FIXME: does not work (parameters are types)
    "Identite": ["Id"]
}

symbols_to_latex = {  # TODO : complete the dictionary
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

text_from_node = {
    # "APPLICATION": [display_application],
    # "LOCAL_CONSTANT": [display_constant],
    # "CONSTANT": [display_constant],
    # "LAMBDA": [display_lambda],
    #
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
    # "PROP_∃": "not implemented",
    ###############
    # SET THEORY: #
    ###############
    "PROP_INCLUDED": [0, " " + _("is included in") + " ", 1],
    # "PROP_BELONGS": [0, " " + _("belongs to") + " ", 1],
    "PROP_BELONGS": [0, " ∈ ", 1],  # this special case is processed in
    # the function display_belongs_to
    "SET_INTER": [_("the intersection of") + " ", 0, " " + _("and") + " ", 1],
    "SET_UNION": [_("the union of") + " ", 0, " " + _("and") + " ", 1],
    "SET_INTER+": [_("the intersection of the sets") + " ", 0],
    "SET_UNION+": [_("the union of the sets") + " ", 0],
    # "SET_DIFF": [0, r" \\ ", 1],
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
    # "MINUS": [0, " - ", 1],
    # "+": [0, " + ", 1],
    ##################
    # GENERAL TYPES: #
    ##################
    "SET": ["P(", 0, ")"],
    "PROP": [_("a proposition")],
    "TYPE": [_("a set")],
    "FUNCTION": [_("a function from") + " ", 0, " " + _("to") + " ", 1],
}
