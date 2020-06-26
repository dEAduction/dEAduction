#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 10:55:21 2020

@author: leroux

transform a string produced by Lean's tactic "analysis" into a tree encoded by
a list. See examples at the end.
"""
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

lean_expr_grammar = Grammar(
    """
    expr = name (open_paren expr (comma_sep expr)* closed_paren)?
    open_paren = "¿("
    closed_paren = "¿)"
    comma_sep = "¿, "
    name = (!open_paren !closed_paren !comma_sep ~".")*  
    """
)


class LeanExprVisitor(NodeVisitor):
    """
    Extract the structure of our mathematical object as a dictionary
    This version takes care of APPLICATIONs:
    APPLICATION(APPLICATION(f,x),y)
    is transformed into
    APPLICATION(f,x,y)
    ("uncurrying")
    """

    def visit_expr(self, node, visited_children):
        """
        expr has two children, the first is the name and the second contains
        the parameters.
        """
        name, arguments = visited_children
        output = {"name": name, "arguments": arguments}  # provisoire
        if name == "APPLICATION":
            child0 = arguments[0]
            name_child0 = child0['name']

            if name_child0 == "APPLICATION":
                arguments_child0 = child0['arguments']
                name = arguments_child0[0]['name']
                arg1 = arguments_child0[0]['arguments']
                new_arg1 = [({'name': name, 'arguments': arg1})] \
                           + arguments_child0[1:] \
                           + arguments[1:]
                output = {"name": "APPLICATION", "arguments": new_arg1}
        return [output]

    def visit_name(self, node, visited_children):
        return node.text
        return node.text

    def generic_visit(self, node, visited_children):
        """ The generic visit method.
        Return the concatenated children to compress the huge Tree
        into a more reasonnable one
        """
        concatenated_children = []
        for elem in visited_children:
            concatenated_children.extend(elem)
        return concatenated_children


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


# ESSAIS
if __name__ == '__main__':
    essai11 = "QUELQUESOIT[x]¿(LOCAL_CONSTANT[name:X/identifier:0._fresh.1093.30647]¿, IMPLIQUE¿(<¿(APPLICATION¿(APPLICATION¿(APPLICATION¿(APPLICATION¿(CONSTANT[name:dist'/dist']¿, LOCAL_CONSTANT[name:X/identifier:0._fresh.1093.30647]¿)¿, LOCAL_CONSTANT[name:_inst_1/identifier:0._fresh.1093.30651]¿)¿, LOCAL_CONSTANT[name:x/identifier:0._fresh.1096.43506]¿)¿, VAR[0]¿)¿, LOCAL_CONSTANT[name:δ/identifier:0._fresh.1096.43703]¿)¿, <¿(APPLICATION¿(APPLICATION¿(APPLICATION¿(APPLICATION¿(CONSTANT[name:dist'/dist']¿, LOCAL_CONSTANT[name:Y/identifier:0._fresh.1093.30649]¿)¿, LOCAL_CONSTANT[name:_inst_2/identifier:0._fresh.1093.30653]¿)¿, APPLICATION¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.1093.30659]¿, LOCAL_CONSTANT[name:x/identifier:0._fresh.1096.43506]¿)¿)¿, APPLICATION¿(LOCAL_CONSTANT[name:f/identifier:0._fresh.1093.30659]¿, VAR[1]¿)¿)¿, LOCAL_CONSTANT[name:ε/identifier:0._fresh.1096.43629]¿)¿)¿)"
    essai12 = "APPLICATION¿(APPLICATION¿(APPLICATION¿(CONSTANT[name:ouvert/ouvert]¿, LOCAL_CONSTANT[name:Y/identifier:0._fresh.1093.30649]¿)¿, LOCAL_CONSTANT[name:_inst_2/identifier:0._fresh.1093.30653]¿)¿, LOCAL_CONSTANT[name:O/identifier:0._fresh.1096.43501]¿)"
    Tree = lean_expr_grammar.parse(essai11)
    # print(Tree)
    lv2 = LeanExprVisitor()
    output2 = lv2.visit(Tree)
    print(output2)
    """
    Ex essai11 :
        [{'name': 'QUELQUESOIT[x]', 'arguments': [{'name': 'LOCAL_CONSTANT[name:X/identifier:0._fresh.1093.30647]', 'arguments': []}, {'name': 'IMPLIQUE', 'arguments': [{'name': '<', 'arguments': [{'name': 'APPLICATION', 'arguments': [{'name': "CONSTANT[name:dist'/dist']", 'arguments': []}, {'name': 'LOCAL_CONSTANT[name:X/identifier:0._fresh.1093.30647]', 'arguments': []}, {'name': 'LOCAL_CONSTANT[name:_inst_1/identifier:0._fresh.1093.30651]', 'arguments': []}, {'name': 'LOCAL_CONSTANT[name:x/identifier:0._fresh.1096.43506]', 'arguments': []}, {'name': 'VAR[0]', 'arguments': []}]}, {'name': 'LOCAL_CONSTANT[name:δ/identifier:0._fresh.1096.43703]', 'arguments': []}]}, {'name': '<', 'arguments': [{'name': 'APPLICATION', 'arguments': [{'name': "CONSTANT[name:dist'/dist']", 'arguments': []}, {'name': 'LOCAL_CONSTANT[name:Y/identifier:0._fresh.1093.30649]', 'arguments': []}, {'name': 'LOCAL_CONSTANT[name:_inst_2/identifier:0._fresh.1093.30653]', 'arguments': []}, {'name': 'APPLICATION', 'arguments': [{'name': 'LOCAL_CONSTANT[name:f/identifier:0._fresh.1093.30659]', 'arguments': []}, {'name': 'LOCAL_CONSTANT[name:x/identifier:0._fresh.1096.43506]', 'arguments': []}]}, {'name': 'APPLICATION', 'arguments': [{'name': 'LOCAL_CONSTANT[name:f/identifier:0._fresh.1093.30659]', 'arguments': []}, {'name': 'VAR[1]', 'arguments': []}]}]}, {'name': 'LOCAL_CONSTANT[name:ε/identifier:0._fresh.1096.43629]', 'arguments': []}]}]}]}]
    """

