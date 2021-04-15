"""
############################################################
# utils.py : utilitarian functions used in files in        #
# the actions directory                                    #
############################################################
This file mainly provides the CodeForLean class, which is an abstract
structure for storing complex sequences of instructions for Lean.
In particular, it makes it possible to send sequences like
<instruction 1> <|> <instruction 2> <|> ...
where "<|>" is the "or else" combinator, i.e. Lean will try successively
each instruction until one succeeds. These kind of sequences maybe be
arbitrarily nested with "and then" sequences. An important point that
motivates this class is the possibility to get feedback on which
instructions have succeeded, by using the "add_trace" method, and then
replace the original code by the effective simplified version via the
"select_or_else" method.


Author(s)     : - Marguerite Bin <bin.marguerite@gmail.com>
Maintainer(s) : - Marguerite Bin <bin.marguerite@gmail.com>
Created       : July 2020 (creation)
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

from dataclasses import dataclass
from typing import Any, Union, List, Optional


class LeanCombinator(str):
    """
    Class clarifying combinators for CodeForLean
    """
    single_string =     ""
    and_then =          "and_then"
    or_else =           "or_else"
    try_ =              "try"
    solve1 =            "solve1"
    focus =             "focus"
    iterate =           "iterate"


@dataclass()
class CodeForLean:
    """
    A class for encoding a structured set of instructions for Lean,
    i.e. tactics combined by combinators then or or_else.
    - Basic tactics are defined via the from_string method
    - Combined tactics are defined via the or_else and and_then methods
    - raw code is retrieved via the to_string method
    - an error_message can be added, to be displayed in case of Lean failure
    - a success_message can be added, to be displayed in case of success
    (depending of the effective code in case of or_else combinator)
    """
    instructions:    [Any]   # [str or CodeForLean]
    combinator:             str = LeanCombinator.single_string
    error_message:          str = ""
    success_message:        str = ""
    # The following is used to store the number of an or_else instructions
    or_else_node_number:   Optional[int] = None

    # The following counts the total number of or_else instructions so far
    or_else_node_counter = 0

    @classmethod
    def empty_code(cls, error_message: str = ''):
        """
        Create an empty code, useful to initialize a sequence of codes
        """
        return CodeForLean(instructions=[],
                           error_message=error_message)

    @classmethod
    def from_string(cls,
                    instruction: str,
                    error_message: str = '',
                    success_message: str = ""):
        """
        Create a CodeForLean with a single instruction
        """
        return CodeForLean(instructions=[instruction],
                           error_message=error_message)

    @classmethod
    def or_else_from_list(cls,
                          instructions: Union[str, List[Any]],
                          error_message: str = '',
                          global_success_message: str = ""):
        """
        Create an or_else CodeForLean from a (list of) strings or CodeForLean
        """
        if isinstance(instructions, str):
            instructions = [instructions]
        elif isinstance(instructions, CodeForLean):
            instructions = [instructions]
        for i in range(len(instructions)):
            if isinstance(instructions[i], str):
                instructions[i] = CodeForLean.from_string(instructions[i])
        # From now on instructions is a list of CodeForLean
        if len(instructions) == 1:
            return instructions[0]
        else:
            return CodeForLean(instructions=instructions,
                               combinator=LeanCombinator.or_else,
                               error_message=error_message,
                               success_message=global_success_message)

    @classmethod
    def and_then_from_list(cls,
                          instructions: Union[str, List[Any]],
                          error_message: str = '',
                          global_success_message: str = ""):
        """
        Create an or_else CodeForLean from a (list of) strings or CodeForLean
        """
        if isinstance(instructions, str):
            instructions = [instructions]
        elif isinstance(instructions, CodeForLean):
            instructions = [instructions]
        for i in range(len(instructions)):
            if isinstance(instructions[i], str):
                instructions[i] = CodeForLean.from_string(instructions[i])
        # From now on instructions is a list of CodeForLean
        if len(instructions) == 1:
            return instructions[0]
        else:
            return CodeForLean(instructions=instructions,
                               combinator=LeanCombinator.and_then,
                               error_message=error_message,
                               success_message=global_success_message)

    def or_else(self, other, success_message=""):
        """
        Combine 2 CodeForLean with an or_else combinator.

        :param other:   str or CodeForLean
        :return:        CodeForLean
        """
        if other is None:
            return self
        if isinstance(other, str):
            other = CodeForLean.from_string(other)
        if other.success_message == "":
            other.success_message = success_message
        if self.is_empty():
            return other
        elif self.is_or_else():
            self.instructions.append(other)
            return self
        else:
            return CodeForLean(combinator=LeanCombinator.or_else,
                               instructions=[self, other])

    def and_then(self, other, success_message=""):
        """
        Combine 2 CodeForLean with an and_then combinator.

        :param other:   str or CodeForLean
        :return:        CodeForLean
        """
        if isinstance(other, str):
            other = CodeForLean.from_string(other)
        if self.is_empty():
            return other
        elif other == "" or other.is_empty():
            return self
        elif self.is_and_then():
            self.instructions.append(other)
            self.success_message = success_message
            return self
        else:
            return CodeForLean(combinator=LeanCombinator.and_then,
                               instructions=[self, other],
                               success_message=success_message)

    def single_combinator(self, combinator_type, success_message=""):
        """
        Add a (single) combinator at the top of self.

        :return: CodeForLean
        """

        if combinator_type in ("try", LeanCombinator.try_):
            return self.try_()

        # if isinstance(self, str):
        #     self_ = CodeForLean.from_string(self)
        return CodeForLean(combinator=combinator_type,
                           instructions=[self],
                           success_message=success_message)

    def try_(self, success_message=""):
        """
        Turn self into
                            "self <|> skip",
        which is equivalent to
                            "try {self}"
        but will allow to retrieve an "effective code" message in case of
        failure. (Note that this instruction always succeeds.)

        :return: CodeForLean
        """
        # if isinstance(self, str):
        #     self_ = CodeForLean.from_string(self)
        skip = CodeForLean.from_string("skip")
        return CodeForLean(combinator=LeanCombinator.or_else,
                           instructions=[self, skip],
                           success_message=success_message)

    def solve1(self, success_message=""):
        return CodeForLean(combinator=LeanCombinator.solve1,
                           instructions=[self],
                           success_message=success_message)

    # def and_finally(self, other):
    #     """
    #     Add other before each "or_else" combinator, so that whatever
    #     sequence of instruction that succeeds ends with other
    #     e.g. and_finally ("A or_else B", "C")
    #         -> "(A, C) or_else (B,C)"
    #
    #     :param other:   another instance of CodeForLean
    #     :return:        CodeForLean
    #     """
    #     # fixme: not used anywhere
    #     if isinstance(other, str):
    #         other = CodeForLean.from_string(other)
    #     if self.is_empty():
    #         return other
    #     elif self.is_single_string() or self.is_and_then():
    #         # replace self by self and then other
    #         return self.and_then(other)
    #     elif self.is_or_else():
    #         instructions = [piece_of_code.and_finally(other)
    #                         for piece_of_code in self.instructions]
    #         return CodeForLean(combinator=LeanCombinator.or_else,
    #                            instructions=instructions)

    def to_raw_string(self, exclude_no_meta_vars=False) -> str:
        """
        Format CodeForLean into a string which can be sent to Lean

        :param exclude_no_meta_vars:    if True, 'no_meta_vars' instructions
                                        are discarded
        :return: a string understandable by the Lean parser
        """

        # TODO: handle error_messages
        if self.is_empty():
            return ""
        elif self.is_single_string():
            instruction = self.instructions[0]
            if exclude_no_meta_vars and instruction == 'no_meta_vars':
                return ""
            elif isinstance(instruction, CodeForLean):
                return instruction.to_raw_string()
            elif isinstance(instruction, str):
                return instruction
        elif self.is_and_then():
            strings = []
            for instruction in self.instructions:
                string = instruction.to_raw_string(exclude_no_meta_vars)
                if string:
                    strings.append(string)
            return ', '.join(strings)
        elif self.is_or_else():
            strings = [child.to_raw_string(exclude_no_meta_vars)
                       for child in self.instructions]
            strings = ['`[ ' + string + ']'
                       for string in strings if string != ""]
            return ' <|> '.join(strings)
        else:
            return self.combinator \
                + " {" \
                + self.instructions[0].to_raw_string(exclude_no_meta_vars) \
                + " }"

    def add_trace_effective_code(self):
        """
        This method does two things:
        1) Add
            "trace "EFFECTIVE CODE {<node_number>.<number of success code>}"
        after each instruction of each "or_else" combinator.
        2) mark each "or_else" node with a node_number
        which will be used by the select_or_else method.

        :return: two instances of CodeForLean, the first contains the trace
        messages, the second is self with marked or_else node.
        """

        if self.is_single_string():
            return self, self
        elif self.is_or_else():  # Call recursively on each instruction
            node_number = CodeForLean.or_else_node_counter
            CodeForLean.or_else_node_counter += 1
            code_counter = 0
            instructions2 = []
            for instruction in self.instructions:
                _, ins2 = instruction.add_trace_effective_code()
                trace_string = f'trace \"EFFECTIVE CODE n°' \
                               f'{node_number}.' \
                               f'{code_counter}\"'
                ins2 = ins2.and_then(trace_string)
                code_counter += 1
                instructions2.append(ins2)
            self.or_else_node_number = node_number
        else:
            instructions2 = [ins.add_trace_effective_code()[1] for ins in
                             self.instructions]

        self_with_trace = CodeForLean(combinator=self.combinator,
                                      instructions=instructions2,
                                      error_message=self.error_message,
                                      success_message=self.success_message)

        return self, self_with_trace

    def select_or_else(self, node_number, alternative_number):
        """
        Modify self to reflect the fact that for the or_else node identified by
        code_number, the alternative whose number is alternative_number has
        been successful. Precisely, replace the or_else node by this
        alternative and delete the other alternatives.

        :param node_number: number of or_else_node
        :param alternative_number: number of successful alternative of this
        node
        :return: (1) a CodeForLean which is the modified self,
        (2) A boolean which tells if or_else node has been found
        """

        if self.is_single_string():
            return self, False
        elif self.is_or_else() and self.or_else_node_number == node_number:
            new_code = self.instructions[alternative_number]
            return new_code, True
        else:
            found = False
            new_instructions = []
            for ins in self.instructions:
                ins, found_here = ins.select_or_else(node_number,
                                                     alternative_number)
                new_instructions.append(ins)
                if found_here:
                    found = True
            new_code = CodeForLean(instructions=new_instructions,
                                   combinator=self.combinator,
                                   error_message=self.error_message,
                                   success_message=self.success_message,
                                   or_else_node_number=self.or_else_node_number)

            return new_code, found

    def add_no_meta_vars(self):
        """
        Add the "no_meta_vars" tactic after each piece of code that contains
        "apply"
        """
        no_meta_vars_str = "no_meta_vars"
        if self.is_empty():
            return self
        elif not self.is_or_else():
            # replace self by self and_then no_meta_vars
            if self.could_have_meta_vars():
                return self.and_then(no_meta_vars_str)
            else:
                return self
        else:
            instructions = [piece_of_code.add_no_meta_vars()
                            for piece_of_code in self.instructions]
            return CodeForLean(combinator=LeanCombinator.or_else,
                               instructions=instructions)

    def to_decorated_string(self):
        """
        Turn a CodeForLean into a string that can be sent to Lean, including
        no_meta_vars and trace_effective_code when needed.

        :return: the first element is a CodeForLean which is self with
        "no_meta_vars" instructions, and or_else_node_number decorations.
        The second is the decorated string.
        """

        # ! no_meta_vars, and then trace_effective_code, in that order !
        code1 = self.add_no_meta_vars()
        code1, code2 = code1.add_trace_effective_code()
        string = code2.to_raw_string()
        return code1, string

    def extract_success_message(self, effective_code=""):
        """
        Extract the success message, if any, corresponding to the effective
        code.

        :param effective_code:  Lean's result of the "trace effective code"
                                instruction
        :return:                success message to be displayed
        """
        success_message = ""
        # First try specific success_message corresponding to effective_code
        # (if provided)
        if self.is_or_else() and effective_code:
            for instruction in self.instructions:
                if instruction.to_raw_string().startswith(effective_code):
                    success_message = instruction.success_message
        #  Send global success_message if no specific message has been found
        if not success_message:
            success_message = self.success_message
        return success_message

    def add_error_message(self, error_message: str):
        self.error_message = error_message

    def add_success_message(self, success_message: str):
        self.success_message = success_message

    def is_empty(self):
        return self.instructions == []

    def is_single_string(self):
        return self.combinator == LeanCombinator.single_string

    def is_and_then(self):
        return self.combinator == LeanCombinator.and_then

    def is_or_else(self):
        return self.combinator == LeanCombinator.or_else

    def has_or_else(self):
        """
        True if self has some or_else node.
        """

        # True iff self is an or_else node
        # or one of self's instructions is an or_else node
        if self.is_single_string():
            return False
        elif self.is_or_else():
            return True
        else:
            return True in [code_.has_or_else() for code_ in self.instructions]

    def could_have_meta_vars(self) -> bool:
        if self.is_empty():
            return False
        elif self.is_single_string():
            string = self.instructions[0]
            return string.find("apply") != -1 or string.find("have") != -1
        else:
            return True in [instruction.could_have_meta_vars() for
                            instruction in self.instructions]


_VAR_NB = 0
_FUN_NB = 0


def get_new_var():
    global _VAR_NB
    _VAR_NB += 1
    return "x{0}".format(_VAR_NB)


def get_new_fun():
    global _FUN_NB
    _FUN_NB += 1
    return "f{0}".format(_FUN_NB)


# OBSOLETE : see mathobj.give_name.get_new_hyp()
def get_new_hyp():
    global _VAR_NB
    _VAR_NB += 1
    return "h{0}".format(_VAR_NB)


def solve1_wrap(string: str) -> str:
    # (obsolete)
    return "solve1 {" + string + "}"


def get_effective_code_numbers(trace_effective_code: str) -> (int, int):
    """
    Convert a string traced by Lean into a tuple
    Effective code n°12.2   -->   12, 2
    """

    # Find string right of "n°"...
    string1 = trace_effective_code.split('n°')[1]
    # ...and split at '.'
    string2, string3 = string1.split('.')
    return int(string2), int(string3)


if __name__ == '__main__':
    code = CodeForLean.from_string('assumption')
    code = code.and_then(CodeForLean.from_string("toto").try_())
    code.add_success_message("CQFD!")
    code2 = CodeForLean.or_else_from_list(['apply H', 'Great !'])
    code = code.or_else(code2)
    code = code.or_else('goodbye', success_message="I am leaving!")
    code.add_success_message("Success!")
    # code = code.add_trace_effective_code(42)
    # code = code.add_no_meta_vars()

    print(code.to_raw_string())
    code, decorated_code_string = code.to_decorated_string()
    print(decorated_code_string)

    for choice in [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 1),
                   (3,67)]:
        code1, b = code.select_or_else(*choice)
        print(f"Choice {choice} found: {b}")
        print(code1.to_raw_string())

    code1, b = code.select_or_else(0,1)
    code2, b = code1.select_or_else(2,1)
    print(code2.to_raw_string())

    code1 = CodeForLean.from_string("norm_num at *").solve1()
    code2 = CodeForLean.from_string("compute_n 10")
    code3 = (CodeForLean.from_string("norm_num at *").try_()).and_then(code2)
    possible_code = code1.or_else(code3)

    print("----------------")
    print(possible_code.to_raw_string())
    code, deco = possible_code.to_decorated_string()
    # print(deco)
    print(code)
    code, found = code.select_or_else(3,0)
    print(code.to_raw_string())
    print(code.has_or_else())
    code, found = code.select_or_else(4,0)
    print(code.to_raw_string())
    print(code.has_or_else())


