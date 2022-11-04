"""
# nice_display_tree.py : Display string with parentheses /  bracket in a
tree-like way #

    Useful for debugging.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 09 2021 (creation)
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

from dataclasses import dataclass

import logging
log = logging.getLogger()


def split_first_symb(s: str, symbols="(),") -> (str, str, str):
    """
    Return a triplet head, symbol, tail, where symbol is the first occurence
    in s of a character in symbols (empty if no occurence), head is the
    substring before and tail is the substring after (maybe empty) this
    character in s.
    """

    if not s:
        return "", "", ""

    first_car = s[0]
    end = s[1:]
    if first_car in symbols:
        return "", first_car, end
    else:
        head, symbol, tail = split_first_symb(end, symbols)
        return first_car + head, symbol, tail


@dataclass
class TreeNode:
    label: str
    children: []

    def display(self, depth=0):
        MUL = 1
        preamble = "   " + "|  " * depth * MUL

        depth_str = str(depth)
        preamble_root = depth_str + preamble[len(depth_str):]
        print(preamble_root + self.label)
        for child in self.children:
            child.display(depth + 1)


def tree_list(s: str, left_symbols="(", right_symbols=")") -> [TreeNode]:
    """
    Convert the string s into a tree encoded by lists.
    """

    symbols = left_symbols + right_symbols + ","
    node_pile = []
    children_pile = [[]]  # Empty list will welcome the root of the tree
    while s:
        node, symbol, s = split_first_symb(s, symbols)
        node = node.strip()
        print(f"Node {node}, Symbol {symbol}")
        if symbol in left_symbols:  # Start a new tree node
            node_pile.append(node)
            children_pile.append([])
        else:
            if not children_pile:
                print(f"Unexpected right parenthesis at {node + symbol + s}")
                return
            if node:
                leaf = TreeNode(label=node, children=[])
                children_pile[-1].append(leaf)
            if symbol in right_symbols:  # Create new tree node
                children = children_pile.pop()
                if not node_pile:
                    print(f"Unexpected right parenthesis at "
                          f"{node + symbol + s}")
                    return
                node = node_pile.pop()
                tree = TreeNode(label=node, children=children)
                children_pile[-1].append(tree)
    if not children_pile:
        print("Unexpected right parenthesis")
        return
    elif len(children_pile) > 1:
        print(f"Unexpected left parenthesis ({len(children_pile)} terms in "
              f"children_pile)")
        print(f"Children_pile: {children_pile}")
    return children_pile[0]


def nice_display_tree(s: str, left_symbols="(", right_symbols=")"):
    trees = tree_list(s, left_symbols, right_symbols)
    for tree in trees:
        tree.display()


if __name__ == "__main__":
    essai = "toto(toi[zou, bleu], moi)"
    trees = tree_list(essai, left_symbols="([", right_symbols=")]")
    print(trees)
    for tree in trees:
        tree.display()
    string = """CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['exfalso'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=1)], combinator='and_then', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=[CodeForLean(instructions=['left'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['exfalso'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=4)], combinator='and_then', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=3)], combinator='and_then', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['right'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=[CodeForLean(instructions=['left'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['exfalso'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=7)], combinator='and_then', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=6)], combinator='and_then', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['right'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['exfalso'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=9)], combinator='and_then', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=8)], combinator='and_then', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=5)], combinator='and_then', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=2)], combinator='or_else', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=0)
"""
    nice_display_tree(string, left_symbols="([", right_symbols=")]")

