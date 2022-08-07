"""
#########################################################
# lean_analysis.py: Provide methods to parse lean files #
#########################################################

This module transforms a string produced by Lean's tactics "hypo_analysis"
or "goals_analysis" into a tree encoded by a list. See example in the file
comments.

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

from deaduction.pylib.mathobj import MathObject, ContextMathObject

log = logging.getLogger(__name__)

"""
Example of Lean context and target, and the corresponding output of 
hypo_analysis and targets_analysis:

* The Lean context:
XY : Type
f : X → Y
BB' : set Y
x : X
H2 : x ∈ f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯)
⊢ x ∈ (f⁻¹⟮B ∪ B'⟯)

* The output of hypo_analysis:
context:
¿¿¿object: LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.4965.24615¿]¿= TYPE
¿¿¿object: LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.4965.24617¿]¿= TYPE
¿¿¿object: LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.4965.24619¿]¿= FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.4965.24615¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.4965.24617¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.4965.24620¿]¿= SET¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.4965.24617¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: B'¿/ identifier: 0._fresh.4965.24622¿]¿= SET¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.4965.24617¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.4966.29549¿]¿= LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.4965.24615¿]
¿¿¿property¿[pp_type: x ∈ f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯)¿]: LOCAL_CONSTANT¿[name: H2¿/ identifier: 0._fresh.4966.29572¿]¿= PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.4966.29549¿]¿, SET_UNION¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.4965.24615¿]¿)¿]¿(SET_INVERSE¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.4965.24615¿]¿)¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.4965.24619¿]¿, LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.4965.24620¿]¿)¿, SET_INVERSE¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.4965.24615¿]¿)¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.4965.24619¿]¿, LOCAL_CONSTANT¿[name: B'¿/ identifier: 0._fresh.4965.24622¿]¿)¿)¿)

* The output of targets_analysis:
targets:
¿¿¿property¿[pp_type: x ∈ (f⁻¹⟮B ∪ B'⟯)¿]: METAVAR¿[name: _mlocal._fresh.4966.29573¿]¿= PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.4966.29549¿]¿, SET_INVERSE¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.4965.24615¿]¿)¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.4965.24619¿]¿, SET_UNION¿[type: SET¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.4965.24617¿]¿)¿]¿(LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.4965.24620¿]¿, LOCAL_CONSTANT¿[name: B'¿/ identifier: 0._fresh.4965.24622¿]¿)¿)¿)
"""

######################################################################
# Rules for parsing strings provided by Lean's tactics hypo_analysis #
######################################################################
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
    info_field_name = !"type" ("name" / "identifier" / "pp_type" / "value") 
    info_field_content = any_non_sep_symbol+ 
    
    node_name = ~"[a-z A-Z 0-9 _∀∃+-<>≥≤!]"+
     
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
    A class to visit nodes of the parsing tree. See the rules to understand
    the data in each node. e.g.
    "ENTRY = HEAD sep_equal TAIL"
    -> the node ENTRY has 3 children, and only the 1st and 3rd carry
    relevant info.

    Almost all visits return info in the same format:
    a tuple T with
        T[0] a list of mathematical objects,
        T[1] a dictionary containing pertinent information
    """

    def visit_ENTRY(self, node, visited_children) -> ContextMathObject:
        """
        Create a global_var corresponding to the entry
        According to the rules, Entry has three children
        (head, sep_equal, tail)
        :return:
        """
        # Get info from HEAD and a math_object from TAIL
        (_, head), _, ([tail], _) = visited_children
        info = head
        info['math_type'] = tail
        math_object = ContextMathObject.from_info_and_children(info=info,
                                                               children=[])
        # log.debug(f"Creating global var MathObject {math_object}")
        return math_object

    def visit_node_name(self, node, visited_children):
        return [], {'node_name': node.text}

    def visit_expr(self, node, visited_children):
        """
        Create MathObject from children
        (node, children, math_type if any, NO representation)
        """
        node_info = visited_children[0][1]
        children = concatenate(visited_children[1:])[0]
        math_object = MathObject.from_info_and_children(info=node_info,
                                                        children=children)
        return [math_object], {}

    def visit_info_type(self, node, visited_children):
        """
        info_type has 4 children:
        [ type: expr ]
        and we care only about the third one

        Return: a MathObject representing the math type
        """
        [expr], _ = concatenate(visited_children)
        # No info and just one object
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


# For debugging
def pprint(essai: str):
    """
    Display the tree structure of a string formatted with "¿(", "¿)", "¿,".
    For debugging only.

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
