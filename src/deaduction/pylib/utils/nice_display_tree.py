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

import re
import logging
log = logging.getLogger()
# from deaduction.pylib import logger
# logger.configure()
# log = lambda x:x

LEFT_SPLIT_STRINGS = '({'
REGEXP_LEFT_SPLIT_STRINGS = '\(\{'
RIGHT_SPLIT_STRINGS = ')}'


def split_children(string):
    """Find commas outside parentheses in string"""
    children = []
    child = ""
    depth = 0
    for carac in string:
        child += carac
        if carac in LEFT_SPLIT_STRINGS:
            depth += 1
        elif carac in RIGHT_SPLIT_STRINGS:
            depth -= 1
            if depth < 0:
                log.warning("Wrong balanced expr")
        elif carac == ',' and depth == 0:
            children.append((child[:-1]).strip())
            child = ""
        # Last child
    children.append(child.strip())
    print(f"Children of {string}: {children}")
    return children


def split_once(string: str):
    left = REGEXP_LEFT_SPLIT_STRINGS + ','
    # Search first splitting string from left
    # mot followed by parenthesis or comma
    pattern_root = '^[^' + left + ']*[' + left + ']'
    mo = re.search(pattern_root, string)
    if mo:
        root = mo.group()
        children_string = string[len(root):]  # -1
        print(f"Split once: {root} // {children_string}")
        return root[:-1], children_string


def split_once_alt(string: str):
    left = LEFT_SPLIT_STRINGS + ','
    ignore_left = '['
    ignore_right = ']'
    # Search first splitting string from left
    # mot followed by parenthesis or comma
    root = ""
    ignore_depth = 0
    for carac in string:
        root += carac
        if carac in ignore_left:
            ignore_depth += 1
        elif carac in ignore_right:
            ignore_depth -= 1
        elif carac in left and ignore_depth ==0:
            break
    if root != string:
        children_string = string[len(root):]
        print(f"Split once: {root} // {children_string}")
        return root, children_string


def tree_str_to_list(tree_str: str) -> []:
    split = split_once_alt(tree_str)
    if split:
        root, children_string = split
        children = split_children(children_string)
        children_tree = []
        for child in children:
            child_tree = tree_str_to_list(child)
            children_tree.append(child_tree)
        return root, children_tree
    else:
        return tree_str


def display_tree(tree, depth=0):
    MUL = 1
    # Leaf
    preamble = "   " + "|  " * depth*MUL
    if isinstance(tree, str):
        print(preamble + tree)
    elif isinstance(tree, tuple):
        root, children = tree
        depth_str = str(depth)
        preamble_root = depth_str + preamble[len(depth_str):]
        print(preamble_root + root + '{')
        for child in children:
            display_tree(child, depth+1)
        print(preamble_root + ' '*len(root) + '}')
    elif isinstance(tree, list):
        for child in tree:
            display_tree(child, depth+1)


def nice_display_tree(tree_str: str):
    """
    Nice display for strings from targets_analysis and hypo_analysis.
    :param tree_str:
    :return:
    """
    tree = tree_str_to_list(tree_str)
    display_tree(tree)


if __name__ == "__main__":
    essai = "toto(toi[zou, bleu], moi)"
    tree = tree_str_to_list(essai)
    print(tree)
    display_tree(tree, 0)
    string = """CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['exfalso'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=1)], combinator='and_then', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=[CodeForLean(instructions=['left'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['exfalso'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=4)], combinator='and_then', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=3)], combinator='and_then', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['right'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=[CodeForLean(instructions=['left'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['exfalso'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=7)], combinator='and_then', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=6)], combinator='and_then', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['right'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['exfalso'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=[CodeForLean(instructions=['assumption'], combinator='', error_msg='', success_msg='', or_else_node_number=None), CodeForLean(instructions=['contradiction'], combinator='', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=9)], combinator='and_then', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=8)], combinator='and_then', error_msg='', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='', success_msg='', or_else_node_number=5)], combinator='and_then', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=None)], combinator='or_else', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=2)], combinator='or_else', error_msg='Je ne sais pas comment conclure', success_msg='', or_else_node_number=0)
"""
    nice_display_tree(string)