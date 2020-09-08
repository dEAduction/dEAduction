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

import deaduction.pylib.mathobj.MathObject as MathObject
import deaduction.pylib.mathobj.display_math as display_math
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
        # get info from HEAD and a math_object from TAIL
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
        log.debug(f"collected info at expr: {node_info, children}")
        ####################################################################
        # Obsolete: decurryfying APPLICATIONs:

        # #
        # APP(APP([children]), new_child)  ->  APP([children + new_child]) #
        ####################################################################
        # if node_info['node_name'] == "APPLICATION" \
        #     and children[0].node == "APPLICATION":
        #     log.debug('decurryfying...')
        #     math_object = children[0]
        #     math_object.children.append(children[1])
        # else:
        math_object = MathObject.from_info_and_children(info=node_info,
                                                            children=children)
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
    logger.configure(debug=True)
    hypo_analysis = []
    hypo_analysis.append("""¿¿¿object: LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿= PROP
¿¿¿object: LOCAL_CONSTANT¿[name: Q¿/ identifier: 0._fresh.1613.3¿]¿= PROP
¿¿¿object: LOCAL_CONSTANT¿[name: R¿/ identifier: 0._fresh.1613.5¿]¿= PROP
¿¿¿property¿[pp_type: P → P¿]: LOCAL_CONSTANT¿[name: H0¿/ identifier: 0._fresh.1613.11¿]¿= PROP_IMPLIES¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿, LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿)
¿¿¿property¿[pp_type: P ∧ Q → Q ∧ P¿]: LOCAL_CONSTANT¿[name: H0¿/ identifier: 0._fresh.1613.21¿]¿= PROP_IMPLIES¿[type: PROP¿]¿(PROP_AND¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿, LOCAL_CONSTANT¿[name: Q¿/ identifier: 0._fresh.1613.3¿]¿)¿, PROP_AND¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: Q¿/ identifier: 0._fresh.1613.3¿]¿, LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿)¿)
¿¿¿property¿[pp_type: P ∨ Q ↔ Q ∨ P¿]: LOCAL_CONSTANT¿[name: H1¿/ identifier: 0._fresh.1613.33¿]¿= PROP_IFF¿[type: PROP¿]¿(PROP_OR¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿, LOCAL_CONSTANT¿[name: Q¿/ identifier: 0._fresh.1613.3¿]¿)¿, PROP_OR¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: Q¿/ identifier: 0._fresh.1613.3¿]¿, LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿)¿)
¿¿¿property¿[pp_type: ¬¬P ↔ P¿]: LOCAL_CONSTANT¿[name: H2¿/ identifier: 0._fresh.1613.41¿]¿= PROP_IFF¿[type: PROP¿]¿(PROP_NOT¿[type: PROP¿]¿(PROP_NOT¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿)¿)¿, LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿)
¿¿¿property¿[pp_type: R ∧ ¬R → false¿]: LOCAL_CONSTANT¿[name: H3¿/ identifier: 0._fresh.1613.51¿]¿= PROP_NOT¿[type: PROP¿]¿(PROP_AND¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: R¿/ identifier: 0._fresh.1613.5¿]¿, PROP_NOT¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: R¿/ identifier: 0._fresh.1613.5¿]¿)¿)¿)
¿¿¿property¿[pp_type: false¿]: LOCAL_CONSTANT¿[name: H4¿/ identifier: 0._fresh.2228.6946¿]¿= PROP_FALSE¿[type: PROP¿]""")

    hypo_analysis.append("""¿¿¿object: LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿= TYPE
¿¿¿object: LOCAL_CONSTANT¿[name: X'¿/ identifier: 0._fresh.2289.4274¿]¿= TYPE
¿¿¿object: LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2289.4280¿]¿= FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿, LOCAL_CONSTANT¿[name: X'¿/ identifier: 0._fresh.2289.4274¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.2289.4284¿]¿= SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.2289.4289¿]¿= SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: C¿/ identifier: 0._fresh.2289.4294¿]¿= SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: A'¿/ identifier: 0._fresh.2289.4299¿]¿= SET¿(LOCAL_CONSTANT¿[name: X'¿/ identifier: 0._fresh.2289.4274¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: B'¿/ identifier: 0._fresh.2289.4304¿]¿= SET¿(LOCAL_CONSTANT¿[name: X'¿/ identifier: 0._fresh.2289.4274¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.2289.4307¿]¿= LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]
¿¿¿property¿[pp_type: x ∈ A¿]: LOCAL_CONSTANT¿[name: H0¿/ identifier: 0._fresh.2289.4370¿]¿= PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.2289.4307¿]¿, LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.2289.4284¿]¿)
¿¿¿property¿[pp_type: C = A ∩ B¿]: LOCAL_CONSTANT¿[name: H1a¿/ identifier: 0._fresh.2289.4403¿]¿= PROP_EQUAL¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: C¿/ identifier: 0._fresh.2289.4294¿]¿, SET_INTER¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)¿]¿(LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.2289.4284¿]¿, LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.2289.4289¿]¿)¿)
¿¿¿property¿[pp_type: C = A ∪ B¿]: LOCAL_CONSTANT¿[name: H1b¿/ identifier: 0._fresh.2289.4433¿]¿= PROP_EQUAL¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: C¿/ identifier: 0._fresh.2289.4294¿]¿, SET_UNION¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)¿]¿(LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.2289.4284¿]¿, LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.2289.4289¿]¿)¿)
¿¿¿property¿[pp_type: A = ∁B¿]: LOCAL_CONSTANT¿[name: H1c¿/ identifier: 0._fresh.2289.4447¿]¿= PROP_EQUAL¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.2289.4284¿]¿, SET_COMPLEMENT¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)¿]¿(LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.2289.4289¿]¿)¿)
¿¿¿property¿[pp_type: A' = ∁B'¿]: LOCAL_CONSTANT¿[name: H1d¿/ identifier: 0._fresh.2289.4463¿]¿= PROP_EQUAL¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: A'¿/ identifier: 0._fresh.2289.4299¿]¿, SET_COMPLEMENT¿[type: SET¿(LOCAL_CONSTANT¿[name: X'¿/ identifier: 0._fresh.2289.4274¿]¿)¿]¿(LOCAL_CONSTANT¿[name: B'¿/ identifier: 0._fresh.2289.4304¿]¿)¿)
¿¿¿property¿[pp_type: f⟮A⟯ ⊆ A'¿]: LOCAL_CONSTANT¿[name: H2¿/ identifier: 0._fresh.2289.4504¿]¿= PROP_INCLUDED¿[type: PROP¿]¿(SET_IMAGE¿[type: SET¿(LOCAL_CONSTANT¿[name: X'¿/ identifier: 0._fresh.2289.4274¿]¿)¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2289.4280¿]¿, LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.2289.4284¿]¿)¿, LOCAL_CONSTANT¿[name: A'¿/ identifier: 0._fresh.2289.4299¿]¿)
¿¿¿property¿[pp_type: A ⊆ (f⁻¹⟮A'⟯)¿]: LOCAL_CONSTANT¿[name: H4¿/ identifier: 0._fresh.2289.4545¿]¿= PROP_INCLUDED¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.2289.4284¿]¿, SET_INVERSE¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2289.4280¿]¿, LOCAL_CONSTANT¿[name: A'¿/ identifier: 0._fresh.2289.4299¿]¿)¿)
¿¿¿property¿[pp_type: f⁻¹⟮A' ∩ B'⟯ = f⁻¹⟮A'⟯ ∩ (f⁻¹⟮B'⟯)¿]: LOCAL_CONSTANT¿[name: H6¿/ identifier: 0._fresh.2289.4642¿]¿= PROP_EQUAL¿[type: PROP¿]¿(SET_INVERSE¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2289.4280¿]¿, SET_INTER¿[type: SET¿(LOCAL_CONSTANT¿[name: X'¿/ identifier: 0._fresh.2289.4274¿]¿)¿]¿(LOCAL_CONSTANT¿[name: A'¿/ identifier: 0._fresh.2289.4299¿]¿, LOCAL_CONSTANT¿[name: B'¿/ identifier: 0._fresh.2289.4304¿]¿)¿)¿, SET_INTER¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)¿]¿(SET_INVERSE¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2289.4280¿]¿, LOCAL_CONSTANT¿[name: A'¿/ identifier: 0._fresh.2289.4299¿]¿)¿, SET_INVERSE¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2289.4280¿]¿, LOCAL_CONSTANT¿[name: B'¿/ identifier: 0._fresh.2289.4304¿]¿)¿)¿)
¿¿¿property¿[pp_type: f⁻¹⟮A' ∪ B'⟯ = f⁻¹⟮A'⟯ ∪ (f⁻¹⟮B'⟯)¿]: LOCAL_CONSTANT¿[name: H8¿/ identifier: 0._fresh.2289.4739¿]¿= PROP_EQUAL¿[type: PROP¿]¿(SET_INVERSE¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2289.4280¿]¿, SET_UNION¿[type: SET¿(LOCAL_CONSTANT¿[name: X'¿/ identifier: 0._fresh.2289.4274¿]¿)¿]¿(LOCAL_CONSTANT¿[name: A'¿/ identifier: 0._fresh.2289.4299¿]¿, LOCAL_CONSTANT¿[name: B'¿/ identifier: 0._fresh.2289.4304¿]¿)¿)¿, SET_UNION¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)¿]¿(SET_INVERSE¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2289.4280¿]¿, LOCAL_CONSTANT¿[name: A'¿/ identifier: 0._fresh.2289.4299¿]¿)¿, SET_INVERSE¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2289.4271¿]¿)¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2289.4280¿]¿, LOCAL_CONSTANT¿[name: B'¿/ identifier: 0._fresh.2289.4304¿]¿)¿)¿)""")

    hypo_analysis.append("""¿¿¿object: LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿= TYPE
¿¿¿object: LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿= TYPE
¿¿¿object: LOCAL_CONSTANT¿[name: J¿/ identifier: 0._fresh.2258.6803¿]¿= TYPE
¿¿¿object: LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.2258.6807¿]¿= SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: E¿/ identifier: 0._fresh.2258.6816¿]¿= SET_FAMILY¿(LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: F¿/ identifier: 0._fresh.2258.6826¿]¿= SET_FAMILY¿(LOCAL_CONSTANT¿[name: J¿/ identifier: 0._fresh.2258.6803¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)
¿¿¿property¿[pp_type: E = λ (i : I), E i¿]: LOCAL_CONSTANT¿[name: H0¿/ identifier: 0._fresh.2258.6842¿]¿= PROP_EQUAL¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: E¿/ identifier: 0._fresh.2258.6816¿]¿, LAMBDA¿[type: SET_FAMILY¿(LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿, LOCAL_CONSTANT¿[name: i¿/ identifier: _fresh.2259.7402¿]¿, APPLICATION¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(LOCAL_CONSTANT¿[name: E¿/ identifier: 0._fresh.2258.6816¿]¿, LOCAL_CONSTANT¿[name: i¿/ identifier: _fresh.2259.7402¿]¿)¿)¿)
¿¿¿property¿[pp_type: A = set.Union E¿]: LOCAL_CONSTANT¿[name: H2a¿/ identifier: 0._fresh.2258.6864¿]¿= PROP_EQUAL¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.2258.6807¿]¿, SET_UNION+¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(LOCAL_CONSTANT¿[name: E¿/ identifier: 0._fresh.2258.6816¿]¿)¿)
¿¿¿property¿[pp_type: A = ⋃ (i : I), E i¿]: LOCAL_CONSTANT¿[name: H2b¿/ identifier: 0._fresh.2258.6886¿]¿= PROP_EQUAL¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.2258.6807¿]¿, SET_UNION+¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(LAMBDA¿[type: SET_FAMILY¿(LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿, LOCAL_CONSTANT¿[name: i¿/ identifier: _fresh.2259.7412¿]¿, APPLICATION¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(LOCAL_CONSTANT¿[name: E¿/ identifier: 0._fresh.2258.6816¿]¿, LOCAL_CONSTANT¿[name: i¿/ identifier: _fresh.2259.7412¿]¿)¿)¿)¿)
¿¿¿property¿[pp_type: A = set.Inter E¿]: LOCAL_CONSTANT¿[name: H4¿/ identifier: 0._fresh.2258.6906¿]¿= PROP_EQUAL¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.2258.6807¿]¿, SET_INTER+¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(LOCAL_CONSTANT¿[name: E¿/ identifier: 0._fresh.2258.6816¿]¿)¿)
¿¿¿property¿[pp_type: set.Union E ∩ set.Union F = ⋃ (k : I × J), E k.fst ∩ F k.snd¿]: LOCAL_CONSTANT¿[name: H6¿/ identifier: 0._fresh.2258.7016¿]¿= PROP_EQUAL¿[type: PROP¿]¿(SET_INTER¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(SET_UNION+¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(LOCAL_CONSTANT¿[name: E¿/ identifier: 0._fresh.2258.6816¿]¿)¿, SET_UNION+¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(LOCAL_CONSTANT¿[name: F¿/ identifier: 0._fresh.2258.6826¿]¿)¿)¿, SET_UNION+¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(LAMBDA¿[type: SET_FAMILY¿(APPLICATION¿(APPLICATION¿(CONSTANT¿[name: prod¿]¿, LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿)¿, LOCAL_CONSTANT¿[name: J¿/ identifier: 0._fresh.2258.6803¿]¿)¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(APPLICATION¿[type: TYPE¿]¿(APPLICATION¿[type: FUNCTION¿(TYPE¿, TYPE¿)¿]¿(CONSTANT¿[name: prod¿]¿[type: FUNCTION¿(TYPE¿, FUNCTION¿(TYPE¿, TYPE¿)¿)¿]¿, LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿)¿, LOCAL_CONSTANT¿[name: J¿/ identifier: 0._fresh.2258.6803¿]¿)¿, LOCAL_CONSTANT¿[name: k¿/ identifier: _fresh.2259.7423¿]¿, SET_INTER¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(APPLICATION¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(LOCAL_CONSTANT¿[name: E¿/ identifier: 0._fresh.2258.6816¿]¿, APPLICATION¿[type: LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿]¿(APPLICATION¿[type: FUNCTION¿(APPLICATION¿(APPLICATION¿(CONSTANT¿[name: prod¿]¿, LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿)¿, LOCAL_CONSTANT¿[name: J¿/ identifier: 0._fresh.2258.6803¿]¿)¿, LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: β¿/ identifier: _fresh.2259.7464¿]¿, FUNCTION¿(APPLICATION¿(APPLICATION¿(CONSTANT¿[name: prod¿]¿, LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿)¿, LOCAL_CONSTANT¿[name: β¿/ identifier: _fresh.2259.7464¿]¿)¿, LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿)¿)¿]¿(CONSTANT¿[name: prod.fst¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: α¿/ identifier: _fresh.2259.7483¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: β¿/ identifier: _fresh.2259.7490¿]¿, FUNCTION¿(APPLICATION¿(APPLICATION¿(CONSTANT¿[name: prod¿]¿, LOCAL_CONSTANT¿[name: α¿/ identifier: _fresh.2259.7483¿]¿)¿, LOCAL_CONSTANT¿[name: β¿/ identifier: _fresh.2259.7490¿]¿)¿, LOCAL_CONSTANT¿[name: α¿/ identifier: _fresh.2259.7483¿]¿)¿)¿)¿]¿, LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿)¿, LOCAL_CONSTANT¿[name: J¿/ identifier: 0._fresh.2258.6803¿]¿)¿, LOCAL_CONSTANT¿[name: k¿/ identifier: _fresh.2259.7423¿]¿)¿)¿, APPLICATION¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.6797¿]¿)¿]¿(LOCAL_CONSTANT¿[name: F¿/ identifier: 0._fresh.2258.6826¿]¿, APPLICATION¿[type: LOCAL_CONSTANT¿[name: J¿/ identifier: 0._fresh.2258.6803¿]¿]¿(APPLICATION¿[type: FUNCTION¿(APPLICATION¿(APPLICATION¿(CONSTANT¿[name: prod¿]¿, LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿)¿, LOCAL_CONSTANT¿[name: J¿/ identifier: 0._fresh.2258.6803¿]¿)¿, LOCAL_CONSTANT¿[name: J¿/ identifier: 0._fresh.2258.6803¿]¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: β¿/ identifier: _fresh.2259.7515¿]¿, FUNCTION¿(APPLICATION¿(APPLICATION¿(CONSTANT¿[name: prod¿]¿, LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿)¿, LOCAL_CONSTANT¿[name: β¿/ identifier: _fresh.2259.7515¿]¿)¿, LOCAL_CONSTANT¿[name: β¿/ identifier: _fresh.2259.7515¿]¿)¿)¿]¿(CONSTANT¿[name: prod.snd¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: α¿/ identifier: _fresh.2259.7534¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: β¿/ identifier: _fresh.2259.7541¿]¿, FUNCTION¿(APPLICATION¿(APPLICATION¿(CONSTANT¿[name: prod¿]¿, LOCAL_CONSTANT¿[name: α¿/ identifier: _fresh.2259.7534¿]¿)¿, LOCAL_CONSTANT¿[name: β¿/ identifier: _fresh.2259.7541¿]¿)¿, LOCAL_CONSTANT¿[name: β¿/ identifier: _fresh.2259.7541¿]¿)¿)¿)¿]¿, LOCAL_CONSTANT¿[name: I¿/ identifier: 0._fresh.2258.6800¿]¿)¿, LOCAL_CONSTANT¿[name: J¿/ identifier: 0._fresh.2258.6803¿]¿)¿, LOCAL_CONSTANT¿[name: k¿/ identifier: _fresh.2259.7423¿]¿)¿)¿)¿)¿)¿)""")

    hypo_analysis.append("""¿¿¿object: LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿= TYPE
¿¿¿object: LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿= TYPE
¿¿¿object: LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]¿= TYPE
¿¿¿object: LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2258.7088¿]¿= FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: g¿/ identifier: 0._fresh.2258.7094¿]¿= FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: h¿/ identifier: 0._fresh.2258.7100¿]¿= FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]¿)
¿¿¿object: LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.2258.7102¿]¿= LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]
¿¿¿object: LOCAL_CONSTANT¿[name: y¿/ identifier: 0._fresh.2258.7104¿]¿= LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]
¿¿¿object: LOCAL_CONSTANT¿[name: z¿/ identifier: 0._fresh.2258.7106¿]¿= LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]
¿¿¿property¿[pp_type: h = theorie_des_ensembles.applications_II.definitions.composition g f¿]: LOCAL_CONSTANT¿[name: H0¿/ identifier: 0._fresh.2258.7131¿]¿= PROP_EQUAL¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: h¿/ identifier: 0._fresh.2258.7100¿]¿, APPLICATION¿[type: FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]¿)¿]¿(APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]¿)¿)¿]¿(APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]¿)¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]¿)¿)¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.2257.8171¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.2257.8171¿]¿)¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.2257.8171¿]¿)¿)¿)¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8246¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.2257.8275¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8246¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.2257.8275¿]¿)¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8246¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.2257.8275¿]¿)¿)¿)¿)¿)¿]¿(CONSTANT¿[name: theorie_des_ensembles.applications_II.definitions.composition¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.2257.8354¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8385¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.2257.8414¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8385¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.2257.8414¿]¿)¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.2257.8354¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8385¿]¿)¿, FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.2257.8354¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: _fresh.2257.8414¿]¿)¿)¿)¿)¿)¿)¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿)¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿)¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]¿)¿, LOCAL_CONSTANT¿[name: g¿/ identifier: 0._fresh.2258.7094¿]¿)¿, LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2258.7088¿]¿)¿)
¿¿¿property¿[pp_type: theorie_des_ensembles.applications_II.definitions.injective f¿]: LOCAL_CONSTANT¿[name: H1¿/ identifier: 0._fresh.2258.7139¿]¿= APPLICATION¿[type: PROP¿]¿(APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿)¿, PROP¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8479¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8479¿]¿)¿, PROP¿)¿)¿]¿(CONSTANT¿[name: theorie_des_ensembles.applications_II.definitions.injective¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.2257.8506¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8518¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.2257.8506¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8518¿]¿)¿, PROP¿)¿)¿)¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿)¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿)¿, LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2258.7088¿]¿)
¿¿¿property¿[pp_type: theorie_des_ensembles.applications_II.definitions.surjective g¿]: LOCAL_CONSTANT¿[name: H2¿/ identifier: 0._fresh.2258.7150¿]¿= APPLICATION¿[type: PROP¿]¿(APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]¿)¿, PROP¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8553¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8553¿]¿)¿, PROP¿)¿)¿]¿(CONSTANT¿[name: theorie_des_ensembles.applications_II.definitions.surjective¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.2257.8580¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8592¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.2257.8580¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.2257.8592¿]¿)¿, PROP¿)¿)¿)¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿)¿, LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]¿)¿, LOCAL_CONSTANT¿[name: g¿/ identifier: 0._fresh.2258.7094¿]¿)
¿¿¿property¿[pp_type: h x = g (f x)¿]: LOCAL_CONSTANT¿[name: H3¿/ identifier: 0._fresh.2258.7160¿]¿= PROP_EQUAL¿[type: PROP¿]¿(APPLICATION¿[type: LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]¿]¿(LOCAL_CONSTANT¿[name: h¿/ identifier: 0._fresh.2258.7100¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.2258.7102¿]¿)¿, APPLICATION¿[type: LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]¿]¿(LOCAL_CONSTANT¿[name: g¿/ identifier: 0._fresh.2258.7094¿]¿, APPLICATION¿[type: LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2258.7088¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.2258.7102¿]¿)¿)¿)
¿¿¿property¿[pp_type: ∀ (x x' : X), f x = f x' → x = x'¿]: LOCAL_CONSTANT¿[name: H4¿/ identifier: 0._fresh.2258.7182¿]¿= QUANT_∀¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.2257.8628¿]¿, QUANT_∀¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.2258.7076¿]¿, LOCAL_CONSTANT¿[name: x'¿/ identifier: _fresh.2257.8635¿]¿, PROP_IMPLIES¿[type: PROP¿]¿(PROP_EQUAL¿[type: PROP¿]¿(APPLICATION¿[type: LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2258.7088¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.2257.8628¿]¿)¿, APPLICATION¿[type: LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.2258.7088¿]¿, LOCAL_CONSTANT¿[name: x'¿/ identifier: _fresh.2257.8635¿]¿)¿)¿, PROP_EQUAL¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.2257.8628¿]¿, LOCAL_CONSTANT¿[name: x'¿/ identifier: _fresh.2257.8635¿]¿)¿)¿)¿)
¿¿¿property¿[pp_type: ∃ (y : Y), g y = z¿]: LOCAL_CONSTANT¿[name: H5¿/ identifier: 0._fresh.2258.7199¿]¿= QUANT_∃¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.2258.7079¿]¿, LOCAL_CONSTANT¿[name: y¿/ identifier: _fresh.2257.8643¿]¿, PROP_EQUAL¿[type: PROP¿]¿(APPLICATION¿[type: LOCAL_CONSTANT¿[name: Z¿/ identifier: 0._fresh.2258.7082¿]¿]¿(LOCAL_CONSTANT¿[name: g¿/ identifier: 0._fresh.2258.7094¿]¿, LOCAL_CONSTANT¿[name: y¿/ identifier: _fresh.2257.8643¿]¿)¿, LOCAL_CONSTANT¿[name: z¿/ identifier: 0._fresh.2258.7106¿]¿)¿)""")

    counter = 0
    displays = []
    titles = ["Propositional logic", "Set theory", "set families",
              "applications and quantifiers"]
    for trials in hypo_analysis:
        trials = trials.split("¿¿¿")
        trials = ['¿¿¿' + item.replace('\n', '') for item in trials[1:]]
        for item in trials:
            print(item)

        math_objects = []
        for trial in trials:
            print(trials.index(trial))
            tree = lean_expr_with_type_grammar.parse(trial)
            output = LeanEntryVisitor().visit(tree)
            math_objects.append(output)

        displays.append([])
        for math_object in math_objects:
            display = display_math.display_math_object(math_object, "utf8")
            display_mt = \
                display_math.display_math_type_of_local_constant(math_object, "utf8")
            displays[counter].append([display, display_mt])

        print(titles[counter])
        for c in displays[counter]:
            print(c)
        print(displays[counter])

        counter += 1

    for d in zip(titles, displays):
        print(d)
