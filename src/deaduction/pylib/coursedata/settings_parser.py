"""
#####################
# settings_parser.py #
#####################

This parser is used to parse some metadata of the lean files, e.g.
Settings
    logic.button_use_or_prove_mode --> "display_switch"
    logic.force_indices_for_dummy_vars --> false
    display.depth_of_unfold_statements --> 1

Note that end of lines are changed to spaces by the course parser.
This parser creates a dictionary that will be used to update the config.vars
dictionary. This update will be called when user selects the course
(in course.py). These entries can also be set individually in the
metadata of each exercise, another update will be occur at exercise init.

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

import deaduction.pylib.config.vars as cvars


settings = """
rules = rule more_rules
more_rules = (more_rule)*
more_rule = rule
rule = field_name space+ "-->" space+ field_value space*

field_name = any_char_but_space+
field_value = string_with_quotes / number / bool

string_with_quotes = ('"' string1 '"')
string1 = (!'"' any_char)*
number = "-"? digits+
bool = 'true' / 'false' / 'True' / 'False'
"""


basic_rules = """
any_char = ~r"."
any_char_but_space = !space ~r"."
digits = ~r"[0-9']"
space = ~r"\s"
"""

settings_rules = settings + basic_rules


class SettingsVisitor(NodeVisitor):

    def visit_rules(self, node, visited_children) -> dict:
        rule, more_rules = visited_children
        more_rules.update(rule)
        return more_rules

    def visit_rule(self, node, visited_children) -> dict:
        field_name = visited_children[0]
        field_value = visited_children[4]
        rule = {field_name: field_value}
        return rule

    def visit_more_rules(self, node, visited_children) -> dict:
        more_rules = {}
        for rule in visited_children:
            more_rules.update(rule)
        return more_rules

    def visit_more_rule(self, node, visited_children):
        return visited_children[1]

    def visit_field_name(self, node, visited_children):
        return node.text

    def visit_field_value(self, node, visited_children):
        return visited_children[0]

    def visit_string_with_quotes(self, node, visited_children):
        """
        Return the string without quotes.
        """
        return node.text[1:-1]

    # def visit_string1(self, node, visited_children):
    #     return node.text

    def visit_number(self, node, visited_children):
        return int(node.text)

    def visit_bool(self, node, visited_children):
        return True if node.text in ('true', 'True') else False

    def generic_visit(self, node, visited_children):
        # items = list(filter(lambda it: isinstance(it, Item), visited_children))
        return None


settings_grammar = Grammar(settings_rules)


def vars_from_metadata(metadata_settings: str) -> dict:
    """
    Convert the string metadata_settings, from the Lean file metadata of
    individual exercise, into a dict that can be used to update cvars.
    """

    if metadata_settings:
        tree = settings_grammar.parse(metadata_settings)
        vars_from_metadata = SettingsVisitor().visit(tree)
        return vars_from_metadata
    else:
        return dict()


def metadata_str_from_cvar_keys(keys: [str]):
    """
    Complement to the vars_form_metadata() method.
    Given a list of keys, retrieve the corresponding values in cvars and
    convert these data into a string that can be inserted in Lean's file
    metadata with field name 'Settings'.
    """

    settings_line = []
    for key in keys:
        value = cvars.get(key)
        separator = '"' if isinstance(value, str) else ''
        settings_line.append(f'{key} --> {separator}{value}{separator}')

    settings = '\n'.join(settings_line) if keys else None
    return settings


if __name__ == "__main__":
    essai = """logic --> "toto" """
    essai2 = """divise  --> true  """
    essai3 = r"""majorant --> false"""
    essai4 = """pair --> 14"""
    tree = settings_grammar.parse(essai + " " + essai2 + " " + essai3 + " " +
                                                         essai4)
    dic = SettingsVisitor().visit(tree)
    print(dic)

