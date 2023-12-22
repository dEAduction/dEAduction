"""
##################################################################
# parser_course.py : Parse lean course to extract pertinent data #
##################################################################

1) A Lean file is parsed according to the grammar described in the "rules"
string below.
2) Parsimonious.grammar computes a tree description of the file
according to this grammar.
3) Then the tree is visited and information is collected at each pertinent
node through the methods below. The information is stored in
course_history. This is some sort of idealized version of the file,
retaining only the dEAduction-pertinent information. Specifically, it is a
list that contains the following type of events:
- course metadata
- end_of_line (indispensable to determine positions of proofs in the file),
- opening and closing of namespaces (and their metadata),
- statements (definitions, theorems, exercises) and their metadata.
The variable 'data' is a dictionary which is used locally to collect
information that will be stored with each event: an event is a couple
(type_of_event: str, data). For instance for statements, the data is a
dictionary that contains all the metadata associated to the statement.
Then course_history is processed by course.py.


Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 08 2020 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

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

from typing import List, Tuple
from pathlib import Path
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
import logging

import deaduction.pylib.logger as logger

log = logging.getLogger(__name__)


############################
# Some aspect of the rules #
############################
# statement = starts with "lemma" + "definition." / "theorem." / "exercise." ;
#           lean_statement includes variables definition,
#           must end with ":=".

# Test somewhere else that core_proof does not contain "hypo_analysis"
# it is important that ALL ends of lines are detected by the end_of_line node

# Does not support proof-like 'begin ... end' string in a comment between
# statement and proof
# nor "lemma exercise." in a docstring comment

# Statements name must be followed by a space or end_of_line

# metadata = starts with /- dEAduction,
#           must end with a line starting with "-/".
# metadata are optional. The proof of a definition can be before or after
# the metadata but the interlude between statement and metadata cannot
# contain the words "lemma" nor "namespace"
# for exercises, the optional metadata must come immediately after the
# statement, and the begin/end environment must come immediately after
# metadata or statement
# metadata field names are made of anything but spaces
# metadata field contents are indented, and at least one line (maybe empty)
# if the format is not met then the statement will not appear in the list,
# and a log.warning will be issued (in course.py)
# identifiers (lemma and namespace's names between '.') can contain only
# letters, digits and '_'

##################
# Lean Statement #
##################
# The only purpose of this small parser is to separate variables from the core
# statement in Lean's lemmas
# This is NOT the parser for Lean exercises files, just an independent parser
# for statements!
statement_rules = """
statement = variables spaces ":" core_statement
    variables = variable*
        variable =  paren_expr / accol_expr / bracket_expr
            paren_expr      =  spaces "(" (any_char_but_p / variable)* ")" 
            accol_expr      =  spaces "{" (any_char_but_p / variable)* "}"
            bracket_expr    =  spaces "[" (any_char_but_p / variable)* "]"
    core_statement = any_char*

spaces = (" " / end_of_line)*
any_char_but_p = (!"(" !")" !"{" !"}" !"[" !"]" any_char_but_eol) / 
end_of_line 
any_char = any_char_but_eol / end_of_line
any_char_but_eol = ~r"."
end_of_line = "\\n"
"""

statement_grammar = Grammar(statement_rules)


class StatementVisitor(NodeVisitor):

    def visit_statement(self,
                        node: str,
                        visited_children: []) -> Tuple[str, str]:
        """
        Return data from statement.

        :param visited_children:    list of data from children. The pertinent
        children are variables and core_statement.
        :return:                    pertinent visited children
        """
        # filter spaces and ":" to keep just variables and core_statement
        visited_children = list(filter(my_filter, visited_children))
        return visited_children

    def visit_variables(self, node, visited_children):
        return node.text

    def visit_core_statement(self, node, visited_children):
        return node.text

    def generic_visit(self, node, visited_children):
        return None


visitor = StatementVisitor()


def my_filter(text: str) -> bool:
    return text not in [" ", ":", None, "\n", "\\n"]


def extract_core_statement(statement: str) -> Tuple[str, str]:
    """
    Split a Lean statement into the "variables" and the "core" parts.
    e.g.
    - variables:    {X : Type} (A B C : set X)'
    - core:         'A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)'

    WARNING: core must be left as is, so that it might be manipulated by
    DEAduction if needed (e.g. for negating the statement)

    """
    statement_tree = statement_grammar.parse(statement)
    variables, core_statement = visitor.visit(statement_tree)
    return variables, core_statement


################
# Course rules #
################
course_rules = """course = 
            (something_else metadata)?
            (something_else? 
             space_or_eol*   (open_open / namespace_open_or_close / statement))+
            (something_else space_or_eol*)?
"""

something_else_rules = """
something_else = (line_comment / 
((non_coding any_char_but_eol)* end_of_line)  )*
non_coding = !namespace_open_or_close !statement !metadata !open_open
"""

namespace_rules = """
namespace_open_or_close = open_namespace / close_namespace

open_namespace = "namespace" space+ namespace_identifier
                (interlude metadata)?

close_namespace = "end" space+ namespace_identifier
"""

open_rules = """
open_open = "open" space+ namespace_identifier
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
                    ((space_or_eol+ metadata)?
                    space_or_eol+ proof)?
                    
    definition_name = "definition." identifier 
    theorem_name = "theorem." identifier
    exercise_name = "exercise." identifier
    
    lean_statement = ((!separator_equal_def any_char_but_eol)* end_of_line*)+
    
    separator_equal_def = ":="
"""

proof_rules = """
proof = begin_proof core_proof end_proof
    begin_proof = "begin" space_or_eol 
    core_proof = ((!begin_proof !end_proof any_char_but_eol*) end_of_line)*
    end_proof = "end" space_or_eol
"""

metadata_rules = """
metadata =  open_metadata
            metadata_field+
            close_metadata
            
    metadata_field = metadata_field_name  end_of_line  metadata_field_content
        
        metadata_field_name = (!space !close_metadata any_char_but_eol)+ space*
        metadata_field_content = ((space+ metadata_content_line end_of_line) 
                                  /end_of_line)+
        metadata_content_line = !close_metadata any_char_but_eol*
    open_metadata = "/-" space+ "dEAduction" space_or_eol+
    close_metadata = "-/"
"""

interlude_rules = """
interlude = ((!metadata !"lemma" !"namespace" any_char_but_eol)* 
                    space_or_eol*)*
"""
# may be empty

line_comment_rules = """
line_comment = space* "--" any_char_but_eol* end_of_line
"""

identifier_rules = """
identifier           = identifier_start (identifier_rest)*
namespace_identifier = identifier_start (identifier_rest)*
    identifier_start = letter / "_"
    identifier_rest = identifier_start / digits
"""

basic_rules = """
any_char_but_eol = ~r"."
letter = ~r"[a-zA-Z]"
digits = ~r"[0-9']"
space_or_eol = end_of_line / ~r"\s"
space = !end_of_line ~r"\s"
end_of_line = "\\n"
"""

rules = course_rules + something_else_rules \
        + namespace_rules + open_rules \
        + statement_rules + proof_rules + interlude_rules \
        + metadata_rules \
        + line_comment_rules \
        + identifier_rules + basic_rules

lean_course_grammar = Grammar(rules)


#############################################
# Visiting methods for each pertinent nodes #
#############################################
class LeanCourseVisitor(NodeVisitor):
    def visit_course(self,
                     node: str,
                     visited_children: []) -> ([(str, dict)], dict):
        """
        Each 'visit_...' method returns the data obtained at some node of
        the parsed tree. For instance, the "course =" line in the rules
        indicates that pertinent children for course are
            - initial (optional) metadata,
            - any number of namespace_open_or_close and statements.
        So in this method, visited_children will return data from
        visit_metadata, visit_statement, and visit_namespace_open_or_close.
        Note that each of these methods collects data from its own children.

        :param node:                content of the node. Not pertinent here.
        :param visited_children:    data returned by the 'visit_...' methods
                                    from all children. The children are
                                    determined by the parsing rules.
        :return: a couple made of
            - course_history, which is a list of events, each event is a couple
            (name_of_event: str, data: dict)
            - metadata: dict
        """
        course_history, data = get_info(visited_children)
        data.setdefault("metadata", {})
        metadata = data.pop("metadata")
        return course_history, metadata

    #############
    # Statements #
    #############
    def visit_something_else(self, node, visited_children):
        log.debug("Got 'something else'")
        # Just return the joined data of all children
        course_history, data = get_info(visited_children)
        return course_history, data

    def visit_statement(self, node, visited_children):
        """
        - Collect the metadata from children in data['metadata'],
        the lean_name and type of statement from data['exercise_name'].
        - Create an event in the  course_history list with
            name    = 'exercise', 'definition' or 'theorem'
            content = metadata dictionary
        - This event is placed BEFORE the children's events so that the
        line number is OK (and corresponds to the first line of the statement).

        Keys in data dictionary will include, on top of any field defined by
        the designer of the Lean file:
        lean_name, pretty_name, lean_variables, lean_core_statement.

        The pertinent (children of) children here are
            - the statement_name,
            - the lean_statement,
            - the (optional) metadata

        :param node:                content of the node. Not pertinent here.
        :param visited_children:    data returned by the 'visit_...' methods
                                    from all children. The children are
                                    determined by the parsing rules.
        :return: a couple made of
            - course_history, which is a list of events, each event is a couple
            (name_of_event: str, data: dict)
            - metadata: dict
        """

        course_history, data = get_info(visited_children)
        data.setdefault("metadata", {})
        metadata = data.pop("metadata")
        if "exercise_name" in data.keys():
            event_name = "exercise"
            lean_name = data.pop("exercise_name")
        elif "definition_name" in data.keys():
            event_name = "definition"
            lean_name = data.pop("definition_name")
        elif "theorem_name" in data.keys():
            event_name = "theorem"
            lean_name = data.pop("theorem_name")
        else:  # This should not happen
            log.warning(f"no name found for statement with data "
                        f"{data} and metadata {metadata}")
        metadata["lean_name"] = lean_name
        metadata["lean_variables"] = data.pop("lean_variables")
        metadata["lean_core_statement"] = data.pop("lean_core_statement")
        # Compute automatic pretty_name if not found by parser
        short_name = lean_name.split(".")[1]
        automatic_pretty_name = short_name.replace("_", " ").capitalize()
        metadata.setdefault("pretty_name", automatic_pretty_name)

        event = event_name, metadata
        insert(course_history, event)
        return course_history, data

    def visit_begin_proof(self, node, visited_children):
        """
        Begin and end of proofs for exercises are collected and stored in
        the course_history in order to get the line number where dEAduction
        should start the proof.
        """
        course_history, data = get_info(visited_children)
        event = "begin_proof", None
        insert(course_history, event)  # To get the good line number
        return course_history, data

    def visit_end_proof(self, node, visited_children):
        course_history, data = get_info(visited_children)
        event = "end_proof", None
        insert(course_history, event)
        return course_history, data

    ############
    # Metadata #
    ############
    def visit_metadata(self, node, visited_children):
        """
        Return the joined data of all children
        NB : keys are changed from Lean-deaduction file format
        to PEP8 conventions, e.g. PrettyName -> pretty_name
        """

        course_history, metadata = get_info(visited_children)
        metadata['_raw_metadata'] = metadata.copy()
        data = {"metadata": metadata}
        # event = "begin_metadata", None
        # insert(course_history, event)
        log.debug(f"got metadata {data}")
        return course_history, data

    def visit_metadata_field(self, node, visited_children):
        """Return the joined data of all children."""
        course_history, data = get_info(visited_children)

        # The following collects the metadata in the corresponding field.
        # This is the only info from children, so it is passed as data.
        metadata = {}
        if "metadata_field_content" in data.keys():
            field_name = change_name(data["metadata_field_name"])
            # e.g. PrettyName -> pretty_name
            metadata[field_name] = data["metadata_field_content"]
        return course_history, metadata

    def visit_metadata_field_name(self, node, visited_children):
        """
        Collect metadata field name.
        :param node: {text}, name of the field, collected at this level of the
        parsed tree.
        :param visited_children: data from children (none at this level).
        :return: course_history and data.
        """
        course_history, data = get_info(visited_children)
        data["metadata_field_name"] = node.text.strip()
        return course_history, data

    def visit_metadata_field_content(self, node, visited_children):
        """
        Collect metadata field content.
        :param node: {text}, content of the field, collected at this level
        of the parsed tree.
        :param visited_children: data from children (none at this level).
        :return: course_history and data.
        """
        course_history, data = get_info(visited_children)
        data["metadata_field_content"] = ""
        # If the metadata content spreads on several lines, then get_info
        # gets only the last line...
        for _, child_data in visited_children:
            if 'metadata_content_line' in child_data:
                more_content = child_data['metadata_content_line']
                if data["metadata_field_content"]:
                    data["metadata_field_content"] += " " + more_content
                else:
                    data["metadata_field_content"] = more_content
        return course_history, data

    def visit_metadata_content_line(self, node, visited_children):
        """
        Collect individual lines of metadata
        :param node:
        :param visited_children:
        :return:
        """
        course_history, data = get_info(visited_children)
        # NB: course_history may contain some EOL events
        data["metadata_content_line"] = node.text.strip()
        return course_history, data

    ##############
    # Namespaces #
    ##############
    def visit_open_open(self, node, visited_children):
        """
        visit a line in the Lean file opening a read-only namespace, e.g.
            "open set"
        collect name of the namespace,
        and create an event in course_history.
        """

        course_history, data = get_info(visited_children)
        name = data.pop("namespace_identifier")
        pretty_name = ""
        event = "open_open", {"name": name}
        insert(course_history, event)
        return course_history, data

    def visit_open_namespace(self, node, visited_children):
        """
        visit a line in the Lean file opening a namespace, e.g.
            "namespace set_theory"
        collect name of the namespace,
        and create an event in course_history.
        """

        course_history, data = get_info(visited_children)
        name = data.pop("namespace_identifier")
        pretty_name = ""
        # Get PrettyName or compute it if absent
        if 'metadata' in data:
            metadata = data.pop("metadata")
            pretty_name = metadata.get("pretty_name")
        if not pretty_name:
            pretty_name = name.replace("_", " ").capitalize()
        event = "open_namespace", {"name": name, "pretty_name": pretty_name}
        insert(course_history, event)
        return course_history, data

    def visit_close_namespace(self, node, visited_children):
        """
        This corresponds to an "end" in the Lean file.
        This method creates a "close_namespace" event in course_history.
        This can actually be the closing of a section, but this will be
        treated by course.py.
        """

        course_history, data = get_info(visited_children)
        name = data.pop("namespace_identifier")
        event = "close_namespace", {"name": name}
        insert(course_history, event)
        return course_history, data

    ###############
    # End of line #
    ###############
    def visit_end_of_line(self, node, visited_children):
        """
        Create an end_of_line event that will be collected in course_history
        at higher levels of the tree.
        """
        event = "end_of_line", None
        return [event], {}  # No data here!

    ####################
    # Collecting names #
    ####################
    def visit_definition_name(self, node, visited_children):
        """
        Collect the definition name.
        """
        course_history, data = get_info(visited_children)
        data["definition_name"] = node.text
        return course_history, data

    def visit_theorem_name(self, node, visited_children):
        """
        Collect the theorem name.
        """
        course_history, data = get_info(visited_children)
        data["theorem_name"] = node.text
        return course_history, data

    def visit_exercise_name(self, node, visited_children):
        """
        Collect the exercise name.
        """
        course_history, data = get_info(visited_children)
        data["exercise_name"] = node.text
        return course_history, data

    def visit_lean_statement(self, node, visited_children):
        """
        Get the statement string, and call extract_core_statement to split
        it into lean_variables and core_statement. These data are put into
        the data dictionary.

        :param node: {text} file content corresponding to the statement
        :param visited_children:
        """
        course_history, data = get_info(visited_children)
        statement = node.text
        # split statement into variables / core
        variables, statement = extract_core_statement(statement)
        data["lean_variables"] = variables
        data["lean_core_statement"] = statement
        return course_history, data

    def visit_namespace_identifier(self, node, visited_children):
        """
        Get namespace's name from node.
        """
        course_history, data = get_info(visited_children)
        data["namespace_identifier"] = node.text
        return course_history, data

    #################
    # Generic visit #
    #################
    def generic_visit(self, node, visited_children):
        # Just return the joined data of all children
        course_history, data = get_info(visited_children)
        return course_history, data


def insert(course_history, event):
    """
    Insert and add a log entry.    
    """
    log.debug(f"Inserting event {event}")
    course_history.insert(0, event)


def get_info(children: List[Tuple[list, dict]]) -> Tuple[list, dict]:
    """
    Concatenate info from the children list.
    :param children:    list of tuples (child_history, child_data) where
                        child_history is a list, and child_data is a dict.
    :return:            couple (course_history, concatenated_data)
    """
    course_history = []
    data = {}
    for child_history, child_data in children:
        course_history.extend(child_history)
        if child_data:
            data.update(child_data)
    return course_history, data


def change_name(name: str) -> str:
    """
    e.g. PrettyName -> pretty_name
    Used to adapt keys of metadata to PEP8 format
    """
    if name.startswith('$'):  # macro: do not touch!!
        return name

    upper_case_alphabet = [chr(i) for i in range(65, 91)]
    for letter in upper_case_alphabet:
        name = name.replace(letter, '_' + letter.lower())
    # Finally remove the leading '_'
    if name.startswith('_'):
        name = name[1:]
    return name


#########
# Tests #
#########

if __name__ == "__main__":
    logger.configure()
    course_file = Path('../../../../tests/lean_files/short_course/exercises'
                       '.lean')
    course_file1 = Path(
        '../../../../tests/lean_files/courses'
        '/exercises_theorie_des_ensembles.lean')
    file_content1 = course_file1.read_text()
    file_content2 = """
lemma exercise.image_reciproque_inter_quelconque  (H : ∀ i:I,  (E i = f ⁻¹' (F
i))) :  (f ⁻¹'  (set.Inter F)) = set.Inter E :=
/- dEAduction
Description

-/
begin
end

"""
    file_content3 = """
lemma exercise.union_distributive_inter : A ∩ (B ∪ C)  = (A ∩ B) ∪ (A ∩ C) := 
/- dEAduction
PrettyName
    Intersection d'une union
-/
begin
    sorry
end
"""
    file_content4 = """
lemma exercise.union {I : Type} {E : I → set X}  {x : X} :
(x ∈ set.Union (λ i, E i)) ↔ (∃ i:I, x ∈ E i)  := 

/- dEAduction
PrettyName
    Intersection d'une union
-/

begin
    sorry
end
"""
    file_content5 = """
lemma exercise.union_distributive_inter : A ∩ (B ∪ C)  = (A ∩ B) ∪ (A ∩ C) := 


begin
    
end
"""
    course_tree1 = lean_course_grammar.parse(file_content1)
    #    course_tree2 = lean_course_grammar.parse(file_content2)
    #    course_tree3 = lean_course_grammar.parse(file_content3)
    course_tree4 = lean_course_grammar.parse(file_content4)
    #    course_tree5 = lean_course_grammar.parse(file_content5)
    # print(course_tree)
    visitor = LeanCourseVisitor()
    course_history, _ = visitor.visit(course_tree4)
    print(f"course history: {course_history}")
