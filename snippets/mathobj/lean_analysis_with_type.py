"""
#####################################################################
# MathObject.py : Take the result of Lean's tactic "Context_analysis", #
# and process it to extract the mathematical content.               #
#####################################################################

This module transforms a string produced by Lean's tactic "hypo_analysis"
or "goals_analysis" into a tree encoded by a list. See examples at the end.

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

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
import logging

from snippets.mathobj.MathObject import MathObject
import deaduction.pylib.logger as logger

log = logging.getLogger(__name__)

outline = """
    ENTRY = HEAD sep_equal TAIL
    HEAD  = sep_begin 
                ("object: " / ("property" infos? ": ") ) 
                node
    TAIL  = expr
    """

details = """
    expr = node (open_paren expr (sep_comma expr)* closed_paren)?

    node = node_name infos? info_type?
        
    info_type = open_bra
                    "type: " expr
                closed_bra

    infos = open_bra 
            info_field (sep_slash info_field)*
            closed_bra
    info_field = info_field_name ": " info_field_content    
    info_field_name = !"type" ("name" / "identifier" / "pp_type") 
    info_field_content = any_non_sep_symbol+ 
    
    node_name = ~"[a-z A-Z 0-9 _∀∃+-<>≥≤]"+
     
    any_non_sep_symbol = !"¿" (~r"." / "\\n")
    """

separators = """
    open_paren = "¿("
    closed_paren = "¿)"
    sep_comma = "¿, "
    open_bra = "¿["
    closed_bra = "¿]"
    sep_slash = "¿/ "
    sep_begin = "¿¿¿"
    sep_equal = "¿= "
    """

rules = outline + details + separators
lean_expr_with_type_grammar = Grammar(rules)


class LeanEntryVisitor(NodeVisitor):
    """
    Almost all visits return info in the same format:
    a tuple T with
        T[0] a list of mathematical objects,
        T[1] a dictionary containing pertinent information
    """

    def visit_ENTRY(self, node, visited_children):
        """
        Create a global_var corresponding to the entry
        Entry has three children.
        :return:
        """
        (_, head), _, ([tail], _) = visited_children
        info = head
        info['math_type'] = tail
        math_object = MathObject.from_info_and_children(info=info,
                                                        children=[])
        log.info(f"Creating MathObject {math_object}")
        return math_object

    def visit_node_name(self, node, visited_children):
        return [], {'node_name': node.text}

    def visit_expr(self, node, visited_children):
        """
        Create AnonymousPO from children
        (node, children, math_type if any, NO representation)
        """
        node_info = visited_children[0][1]
        children = concatenate(visited_children[1:])[0]
        math_object = MathObject.from_info_and_children(info=node_info,
                                                        children=children)
        log.debug(f"collected info at expr: {node_info, children}")
        log.debug(f"---> {math_object}")
        return [math_object], {}

    def visit_info_type(self, node, visited_children):
        """
        info_type has 4 children:
        [ type: expr ]
        and we care only about the third one

        Return: an AnonymousPO representing the math type
        """
        [expr], _ = concatenate(visited_children)  # no info and just one
        # object
        return [], {'math_type': expr}

    def visit_info_field(self, node, visited_children):
        """
        info_field has three children
        Return: a dictionary with a single entry
        """
        info_field_name, _, info_field_content = visited_children
        info = {info_field_name: info_field_content}
        return [], info

    def visit_info_field_name(self, node, visited_children):
        """Return name of field"""
        return node.text

    def visit_info_field_content(self, node, visited_children):
        """Return content of field"""
        return node.text

    def generic_visit(self, node, visited_children):
        """
        Return the list of concatenated children
        """
        return concatenate(visited_children)


def concatenate(children):
    """
    children is a list of tuples T,
    with T[0] a list of object,
    T(1) a dictionary
    :return: a tuple BIG_T with BIG_T[0] the concatenation of the T[0]'s,
    and same thing for BIG_T[1]
    """
    objects = []
    info = {}
    for more_objects, more_info in children:
        objects.extend(more_objects)
        if more_info:
            info.update(more_info)
    return objects, info


# DEBUG
def pprint(essai: str):
    """
    Display the tree structure of a string formatted with "¿(", "¿)", "¿,".

    :param essai: string to be displayed
    """
    inc = 0
    while essai != "":
        if essai.find("¿") == -1:
            print("ERREUR DE FORMAT")
            break
        name, _, essai = essai.partition("¿")
        if essai.startswith("("):
            print("  |" * inc + name)
            inc += 1
        elif essai.startswith(")"):
            print("  |" * inc + name + ")")
            inc -= 1
            essai = essai[1:]
        elif essai.startswith(","):
            print("  |" * inc + name + ",")
            essai = essai[2:]
        else:
            print("  |" * inc + name)
            essai = essai[1:]


if __name__ == "__main__":
    logger.configure()
    trials = ["¿¿¿object: LOCAL_CONSTANT¿= TYPE",
              "¿¿¿object: LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.650.7276¿]¿= TYPE",
              "¿¿¿object: LOCAL_CONSTANT¿[name: f¿/ identifier: "
              "0._fresh.650.7283¿]¿= FUNCTION¿(LOCAL_CONSTANT¿[name: "
              "X¿/ identifier: 0._fresh.650.7276¿]¿, LOCAL_CONSTANT¿[name: "
              "Y¿/ identifier: 0._fresh.650.7278¿]¿)",
              "¿¿¿property¿[pp_type: surjective f¿]: LOCAL_CONSTANT¿[name: "
              "H1¿/ identifier: 0._fresh.650.7294¿]¿= APPLICATION¿[type: "
              "PROP¿]¿(APPLICATION¿)",
              """¿¿¿property¿[pp_type: surjective f¿]: LOCAL_CONSTANT∀¿[name: H1¿/ identifier: 0._fresh.793.6964¿]¿= APPLICATION¿[type: PROP¿]¿(APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.793.6946¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.793.6948¿]¿)¿, PROP¿)¿]¿)""",
              """¿¿¿object: essai_surjective¿= CONSTANT¿[name: surjective¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.792.10224¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10236¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.792.10224¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10236¿]¿)¿, PROP¿)¿)¿)¿]""",
              """¿¿¿object: blabla¿= APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10197¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.793.6946¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10197¿]¿)¿, PROP¿)¿)¿]¿(CONSTANT¿[name: surjective¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.792.10224¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10236¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.792.10224¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10236¿]¿)¿, PROP¿)¿)¿)¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.793.6946¿]¿)""",
              """¿¿¿object: LOCAL_CONSTANT¿= APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.793.6946¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.793.6948¿]¿)¿, PROP¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10197¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.793.6946¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10197¿]¿)¿, PROP¿)¿)¿]¿(CONSTANT¿[name: surjective¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.792.10224¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10236¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.792.10224¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10236¿]¿)¿, PROP¿)¿)¿)¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.793.6946¿]¿)¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.793.6948¿]¿)""",
              """¿¿¿property¿[pp_type: surjective f¿]: LOCAL_CONSTANT¿[name: H1¿/ identifier: 0._fresh.793.6964¿]¿= APPLICATION¿[type: PROP¿]¿(APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.793.6946¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.793.6948¿]¿)¿, PROP¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10197¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.793.6946¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10197¿]¿)¿, PROP¿)¿)¿]¿(CONSTANT¿[name: surjective¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.792.10224¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10236¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.792.10224¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.792.10236¿]¿)¿, PROP¿)¿)¿)¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.793.6946¿]¿)¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.793.6948¿]¿)¿, LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.793.6953¿]¿)""",
              """¿¿¿property¿[pp_type: surjective (composition g f)¿]: METAVAR¿[name: _mlocal._fresh.798.1615¿]¿= APPLICATION¿[type: PROP¿]¿(APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.799.3243¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.799.3247¿]¿)¿, PROP¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.798.2045¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.799.3243¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.798.2045¿]¿)¿, PROP¿)¿)¿]¿(CONSTANT¿[name: surjective¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.798.2072¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.798.2084¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.798.2072¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.798.2084¿]¿)¿, PROP¿)¿)¿)¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.799.3243¿]¿)¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.799.3247¿]¿)¿, APPLICATION¿[type: FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.799.3243¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.799.3247¿]¿)¿]¿(APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.799.3243¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.799.3245¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.799.3243¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.799.3247¿]¿)¿)¿]¿(APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.799.3245¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.799.3247¿]¿)¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.799.3243¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.799.3245¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.799.3243¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.799.3247¿]¿)¿)¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.798.2195¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.799.3245¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.798.2195¿]¿)¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.799.3243¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.799.3245¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.799.3243¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.798.2195¿]¿)¿)¿)¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.798.2270¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.798.2299¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.798.2270¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.798.2299¿]¿)¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.799.3243¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.798.2270¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.799.3243¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.798.2299¿]¿)¿)¿)¿)¿)¿]¿(CONSTANT¿[name: composition¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.798.2378¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.798.2409¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.798.2438¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.798.2409¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.798.2438¿]¿)¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.798.2378¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.798.2409¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.798.2378¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.798.2438¿]¿)¿)¿)¿)¿)¿)¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.799.3243¿]¿)¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.799.3245¿]¿)¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.799.3247¿]¿)¿, LOCAL_CONSTANT¿[name: g¿/ identifier: 0._fresh.799.3251¿]¿)¿, LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.799.3249¿]¿)¿)""",
              """¿¿¿property¿[pp_type: ∃ (x : Y), g x = y¿]: LOCAL_CONSTANT¿[name: H3¿/ identifier: 0._fresh.830.7332¿]¿= QUANT_∃¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.833.4473¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.830.7488¿]¿, PROP_EQUAL¿[type: PROP¿]¿(APPLICATION¿[type: LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.833.4475¿]¿]¿(LOCAL_CONSTANT¿[name: g¿/ identifier: 0._fresh.833.4479¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.830.7488¿]¿)¿, LOCAL_CONSTANT¿[name: y¿/ identifier: 0._fresh.830.7325¿]¿)¿)""",
              """¿¿¿property¿[pp_type: ∃ (x : X), composition g f x = y¿]: METAVAR¿[name: _mlocal._fresh.830.7333¿]¿= QUANT_∃¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.833.4471¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.830.7498¿]¿, PROP_EQUAL¿[type: PROP¿]¿(APPLICATION¿[type: LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.833.4475¿]¿]¿(APPLICATION¿[type: FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.833.4471¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.833.4475¿]¿)¿]¿(APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.833.4471¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.833.4473¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.833.4471¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.833.4475¿]¿)¿)¿]¿(APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.833.4473¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.833.4475¿]¿)¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.833.4471¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.833.4473¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.833.4471¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.833.4475¿]¿)¿)¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.830.7601¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.833.4473¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.830.7601¿]¿)¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.833.4471¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.833.4473¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.833.4471¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.830.7601¿]¿)¿)¿)¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.830.7676¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.830.7705¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.830.7676¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.830.7705¿]¿)¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.833.4471¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.830.7676¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.833.4471¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.830.7705¿]¿)¿)¿)¿)¿)¿]¿(CONSTANT¿[name: composition¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.830.7784¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.830.7815¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.830.7844¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.830.7815¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.830.7844¿]¿)¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.830.7784¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.830.7815¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.830.7784¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.830.7844¿]¿)¿)¿)¿)¿)¿)¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.833.4471¿]¿)¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.833.4473¿]¿)¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.833.4475¿]¿)¿, LOCAL_CONSTANT¿[name: g¿/ identifier: 0._fresh.833.4479¿]¿)¿, LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.833.4477¿]¿)¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.830.7498¿]¿)¿, LOCAL_CONSTANT¿[name: y¿/ identifier: 0._fresh.830.7325¿]¿)¿)"""
              ]

    for trial in trials:
        print(trials.index(trial))
        tree = lean_expr_with_type_grammar.parse(trial)
        output = LeanEntryVisitor().visit(tree)
