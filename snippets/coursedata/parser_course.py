"""
# parser_course.py : Parse lean course to extract pertinent data

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 08 2020 (creation)
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

from pathlib import Path
from typing import List

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

# metadata = starts with /- dEAduction,
#           must end with a line starting with "-/".
# statement = starts with "lemma" + "definition." / "theorem." / "exercise." ;
#           lean_statement includes variables definition,
#           must end with ":=".

# test somewhere else that core_proof does not contain "hypo_analysis"
# it is important that all ends of line are detected by the end_of_line node

# Does not support proof-like 'begin ... end' string in a comment between
# statement and proof

# metadata are optional but must come immediately after statement or
# namespace declaration (before the proof)
# begin/end environment must come immediately after metadata or statement for
# exercises
# metadata field names starts with $ or an uppercase letter

import logging

import deaduction.pylib.logger as logger

log = logging.getLogger(__name__)

course_rules = """course = 
            (something_else? 
             space_or_eol*   (namespace_open_or_close / statement))+
            (something_else space_or_eol*)?
"""

something_else_rules = """
something_else = (line_comment / 
((!namespace_open_or_close !statement any_char_but_eol)* end_of_line)  )*
"""

namespace_rules = """
namespace_open_or_close = open_namespace / close_namespace

open_namespace = "namespace" space+ namespace_identifier
                (space_or_eol+ namespace_metadata)?

close_namespace = "end" space+ namespace_identifier
"""

statement_rules = """
statement = (exercise / definition_or_theorem)

exercise  = "lemma" space_or_eol+
                    exercise_name space_or_eol+
                    lean_statement
                separator_equal_def
                    (space_or_eol+ metadata)?
                    space_or_eol+ proof

definition_or_theorem = "lemma" space_or_eol+
                    (definition_name / theorem_name) space_or_eol+
                    lean_statement
                separator_equal_def
                    (space_or_eol+ metadata)?
                    
    definition_name = "definition." identifier 
    theorem_name = "theorem." identifier
    exercise_name = "exercise." identifier
    
    lean_statement = ((!separator_equal_def any_char_but_eol)* end_of_line*)+
    
    separator_equal_def = ":="
"""

proof_rules = """
proof = begin_proof core_proof end_proof
    begin_proof = "begin" space_or_eol+
    end_proof = space_or_eol+ "end" space_or_eol+
    core_proof = (!begin_proof !end_proof any_char_but_eol*)
"""

interlude_rules = """
interlude = (!proof !metadata !space_or_eol any_char_but_eol)* space_or_eol*
"""
# NB : interlude does NOT end with a space_or_eol
# (not used anymore)

line_comment_rules = """
line_comment = "--" any_char_but_eol* end_of_line
"""

metadata_rules = """
metadata = open_metadata
                (metadata_field_name  end_of_line
                space+ metadata_field_content  end_of_line)*
            close_metadata
    metadata_field_name = ~r"[A-Z]$" identifier_rest* space*
    metadata_field_content = any_char_but_eol 
    open_metadata = "/- dEAduction" space_or_eol+
    close_metadata = "-/"
    
namespace_metadata = metadata
"""
identifier_rules = """
identifier           = identifier_start (identifier_rest)*
namespace_identifier = identifier_start (identifier_rest)*
    identifier_start = letter / "_"
    identifier_rest = identifier_start / digits
"""
common_rules = """
any_char_but_eol = ~r"."
letter = ~r"[a-zA-Z]"
digits = ~r"[0-9']"
space_or_eol = end_of_line / ~r"\s"
space = !end_of_line ~r"\s"
end_of_line = "\\n"
"""

rules = course_rules + something_else_rules \
        + namespace_rules \
        + statement_rules + proof_rules \
        + metadata_rules \
        + line_comment_rules \
        + identifier_rules + common_rules
lean_course_grammar = Grammar(rules)


class LeanCourseVisitor(NodeVisitor):
    def visit_course(self, node, visited_children):
        course_history, data = get_info(visited_children)
        return course_history, data

    # def visit_exercise(self, node, visited_children):
    #     pass
    #


    #############
    # statements #
    #############
    def visit_statement(self, node, visited_children):
        course_history, data = get_info(visited_children)
        if "metadata" in data.keys():
            metadata = data.pop("metadata")
        else:
            metadata = {}
        if "exercise_name" in data.keys():
            event_name = "exercise"
            lean_name = data.pop("exercise_name")
        elif "definition_name" in data.keys():
            event_name = "definition"
            lean_name = data.pop("definition_name")
        elif "theorem_name" in data.keys():
            event_name = "theorem"
            lean_name = data.pop("theorem_name")
        else:
            log.warning(f"no name found for statement with data "
                        f"{data} and metadata {metadata}")
        metadata["lean_name"] = lean_name
        metadata["lean_statement"] = data.pop("lean_statement")
        short_name = lean_name.split(".")[1]
        automatic_pretty_name = short_name.replace("_", " ").capitalize()
        metadata.setdefault("PrettyName", automatic_pretty_name)

        event = event_name, metadata
        course_history.append(event)
        return course_history, data

    def visit_begin_proof(self, node, visited_children):
        course_history, data = get_info(visited_children)
        event = "begin_proof", None
        course_history.append(event)
        return course_history, data

    def visit_end_proof(self, node, visited_children):
        course_history, data = get_info(visited_children)
        event = "end_proof", None
        course_history.append(event)
        return course_history, data

    ############
    # metadata #
    ############
    def visit_metadata(self, node, visited_children):
        # return the joined data of all children
        course_history, data = get_info(visited_children)
        # the following line clear the dictionary data
        # and replace it by a single key = "metadata",
        # value = previous data dictionary
        data = {"metadata": data}
        return course_history, data


    ##############
    # namespaces #
    ##############
    def visit_open_namespace(self, node, visited_children):
        course_history, data = get_info(visited_children)
        name = data.pop("namespace_identifier")
        if "metadata" in data.keys():
            metadata = data.pop("metadata")
            pretty_name = metadata["field_content"]
        else:
            pretty_name = name.replace("_", " ").capitalize()
        event = "open_namespace", {"name": name, "pretty_name": pretty_name}
        course_history.append(event)
        return course_history, data

    def visit_close_namespace(self, node, visited_children):
        course_history, data = get_info(visited_children)
        event = "close_namespace", None
        course_history.append(event)
        return course_history, data

    ###############
    # end of line #
    ###############
    def visit_end_of_line(self, node, visited_children):
        event = "end_of_line", None
        return [event], {}

    ###################
    # collecting data #
    ###################

    def visit_definition_name(self, node, visited_children):
        course_history, data = get_info(visited_children)
        data["definition_name"] = node.text
        return course_history, data

    def visit_theorem_name(self, node, visited_children):
        course_history, data = get_info(visited_children)
        data["theorem_name"] = node.text
        return course_history, data

    def visit_exercise_name(self, node, visited_children):
        course_history, data = get_info(visited_children)
        data["exercise_name"] = node.text
        return course_history, data

    def visit_metadata_field_name(self, node, visited_children):
         course_history, data = get_info(visited_children)
         data["metadata_field_name"] = node.text
         return course_history, data

    def visit_metadata_field_content(self, node, visited_children):
         course_history, data = get_info(visited_children)
         data["metadata_field_content"] = node.text
         return course_history, data
    def visit_lean_statement(self, node, visited_children):
        course_history, data = get_info(visited_children)
        data["lean_statement"] = node.text
        return course_history, data

    def visit_namespace_identifier(self, node, visited_children):
        course_history, data = get_info(visited_children)
        data["namespace_identifier"] = node.text
        return course_history, data


    #################
    # generic visit #
    #################
    def generic_visit(self, node, visited_children):
        # return the joined data of all children
        course_history, data = get_info(visited_children)
        return course_history, data


def get_info(children: List[dict]):
    course_history = []
    data = {}
    for child_history, child_data in children:
        course_history.extend(child_history)
        if child_data:
            data.update(child_data)
    return course_history, data




if __name__ == "__main__":
    course_file1 = Path('../../tests/lean_files/short_course/exercises.lean')
    course_file2 = Path(
        '../../tests/lean_files/exercises/exercises_theorie_des_ensembles.lean')
    file_content = course_file2.read_text()
    end_of_line = """
"""
#    extract1 = end_of_line.join(file_content.splitlines()[:145])
    course_tree = lean_course_grammar.parse(file_content)
    print(course_tree)
    visitor = LeanCourseVisitor()
    course_history, _ = visitor.visit(course_tree)
    print(f"course history: {course_history}")
