"""
###########################################################
# pattern_parser.py : Parser for pattern data for display #
###########################################################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 11 2022 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2022 the d∃∀duction team

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

from typing import Any, Optional
from dataclasses import dataclass
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
import logging

log = logging.getLogger(__name__)

############################################################################
# Authorized expression are made of one node
# (with optional type indicated after ":")
# with 0 or more children indicated between parentheses separated by commas.
# Children are themselves expressions
############################################################################
structure = """
    expr = node children
    node = node_name info_type?
    info_type = type_sep expr
    node_name = ~"[a-z A-Z 0-9 *?_∀∃+<>≥≤!.'/= - ℕℤℚℝ]"+
    children = (open_paren expr more_expr closed_paren)?
    more_expr = (comma expr)*
    """
separators = """
    open_paren = "(" spaces
    closed_paren = spaces ")"
    type_sep = ":" spaces
    comma = "," spaces
    spaces = (" ")*
"""

rules = structure + separators
pattern_grammar = Grammar(rules)


node_dict = {'APP': "APPLICATION",
             'CST?': "CONSTANT/name=?",
             "NOT": "PROP_NOT"}


@dataclass
class Tree:
    """
    A class to store tree, with attributes node and children.
    """
    node: str
    children: []  # [Tree]
    type_: Any  # Tree

    def display(self, depth=0):
        MUL = 1
        sep = "|  "
        preamble = "   " + sep * depth * MUL

        depth_str = str(depth)
        preamble_root = depth_str + preamble[len(depth_str):]
        # display = preamble_root + self.node \
        #     + (": " + self.type_.node if self.type_ else "")
        display = preamble_root + self.node \
            + (": " if self.type_ else "")
        print(display)
        if self.type_:
            self.type_.display(depth=len(display)//len(sep))
        for child in self.children:
            child.display(depth + 1)


class PatternEntryVisitor(NodeVisitor):
    """
    A class to visit nodes of the parsing tree. See the rules to understand
    the data in each node. Return a tree (instance of the Tree class).
    """

    def visit_expr(self, _, visited_children) -> Tree:
        """
        expr = node children
        Here visited_children = [ (node_name, node_type), children: Tree].
        We create and return the corresponding Tree.
        """

        [(node_name, node_type), children] = visited_children

        # Infos

        return Tree(node=node_name, children=children, type_=node_type)

    def visit_node(self, _, visited_children) -> (str, Optional[Tree]):
        """
        node_ = node_name info_type?
        """

        [node_name, info_type] = visited_children
        node_type = None if not info_type else info_type[0]
        return node_name, node_type

    def visit_children(self, _, visited_children) -> [Tree]:
        """
        children_ = (open_paren expr more_expr closed_paren)?
        We assume that more_expr return the list of supplementary children.
        We return the content of expr and more_expr, which corresponds to the
        list of all children.
        """
        if not visited_children:
            return []
        [[_, first_child, other_children, _]] = visited_children
        return [first_child] + other_children

    def visit_more_expr(self, _, visited_children) -> [Tree]:
        """
        more_expr = (sep_comma expr)*
        has a single visited_children,
        which itself has two visited_children.
        """
        more_children = [child for [_, child] in visited_children]
        return more_children

    def visit_node_name(self, node, _) -> str:
        node_name = (node.text).strip()
        if node_name in node_dict.keys():
            node_name = node_dict[node_name]
        return node_name

    def visit_info_type(self, _, visited_children) -> Tree:
        """
        info_type = type_sep expr
        has two visited_children, we return the second one.
        """
        [_, type_] = visited_children
        return type_

    def generic_visit(self, _, visited_children):
        return visited_children


def tree_from_str(s: str) -> Tree:
    parsed_tree = pattern_grammar.parse(s)
    tree = PatternEntryVisitor().visit(parsed_tree)
    return tree


if __name__ == "__main__":
    text = "APP(APP(1, 2), 3)"
    text2 = "FORALL(SET(?0), ?1, ?2)"
    text3 = "APP('composition', ..., ?-2, ?-1)"
    text4 = "NOT(APP(APP(?0, ?-2), ?-1))"
    text5 = "APP(?0: FUNCTION(?1, ?2), ?3)"
    print(tree_from_str(text5).display())



