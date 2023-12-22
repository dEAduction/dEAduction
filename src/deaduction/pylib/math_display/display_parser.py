"""
#####################
# display_parser.py #
#####################

This parser is used to parse some metadata of the lean files, e.g.
Display
    divise --> (-2, " divise ", -1)
    pair --> (-1, " est pair")

Note that end of lines are changed to spaces by the course parser.
This parser creates a dictionary that will be used to update
latex_from_constant_name from app_pattern_data. This update will be called
when user selects the course (in start_coex).

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 04 2023
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2023 the dEAduction team

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

from typing import Union, Tuple
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from parsimonious import ParseError


display = """
rules = rule more_rules
more_rules = (more_rule)*
more_rule = rule
rule = constant_name space+ "-->" space+ pattern space*
constant_name = any_char_but_space+
pattern = "(" (space)* item (space)* more_items ")"
item = number / encapsulated_string
more_items = (more_item)*
more_item = "," (space)* item (space)*
number = "-"? digits+
encapsulated_string = ('"' string1 '"') / ("`" string2 "`") 
string1 = (!'"' any_char)*
string2 = (!"`" any_char)*
"""


basic_rules = """
any_char = ~r"."
any_char_but_space = !space ~r"."
digits = ~r"[0-9']"
space = ~r"\s"
"""

display_rules = display + basic_rules


class Item:
    def __init__(self, data: Union[int, str]):
        self.data = data


class DisplayPatternVisitor(NodeVisitor):

    def visit_rules(self, node, visited_children) -> dict:
        rule, more_rules = visited_children
        more_rules.update(rule)
        return more_rules

    def visit_rule(self, node, visited_children) -> dict:
        key = visited_children[0]
        pattern = tuple(visited_children[4])
        rule = {key: pattern}
        return rule

    def visit_more_rules(self, node, visited_children) -> dict:
        more_rules = {}
        for rule in visited_children:
            more_rules.update(rule)
        return more_rules

    def visit_more_rule(self, node, visited_children):
        return visited_children[1]

    def visit_constant_name(self, node, visited_children) -> str:
        return node.text

    def visit_pattern(self, node, visited_children) -> []:
        item = visited_children[2]
        more_items = visited_children[4]
        items = [item.data for item in ([item] + more_items)]
        return items

    def visit_item(self, node, visited_children) -> Item:
        item = Item(visited_children[0])
        return item

    def visit_more_items(self, node, visited_children) -> [Item]:
        # more_items = Item(visited_children[0])
        return visited_children

    def visit_more_item(self, node, visited_children) -> Item:
        more_item = visited_children[2]
        return more_item

    def visit_number(self, node, visited_children) -> int:
        return int(node.text)

    def visit_encapsulated_string(self, node, visited_children) -> str:
        """
        Return the string without quotation marks.
        """
        s = node.text[1:-1]
        return s

    def generic_visit(self, node, visited_children):
        # items = list(filter(lambda it: isinstance(it, Item), visited_children))
        return None


display_grammar = Grammar(display_rules)


if __name__ == "__main__":
    essai = """divise --> (-2, " divise ", -1)"""
    essai2 = """divise  --> ( -2 ,  " divise " ,   -1  )  """
    essai3 = r"""majorant --> (-1, `\text_is`, " majorant de ", -2)"""
    essai4 = """pair --> (-1, "est paire")"""
    tree = display_grammar.parse(essai + " " + essai3 + " " + essai4)
    dic = DisplayPatternVisitor().visit(tree)
    print(dic)

