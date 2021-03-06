"""
############################################################
# utils.py : utilitarian functions used in files in        #
# the actions directory                                    #
############################################################
    

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
from typing import Any, Union, List
from enum import IntEnum

from deaduction.pylib.actions import WrongUserInput


class LeanCombinator(str):
    """
    Class clarifying combinators for CodeForLean
    """
    single =    "single"
    and_then =  "and_then"
    or_else =   "or_else"
    try_ =      "try"
    solve1 =    "solve1"
    focus =     "focus"
    iterate =   "iterate"


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
    combinator:      str = LeanCombinator.single
    error_message:   str = ""
    success_message: str = ""

    # TODO: make properties to ensure combinator

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
        Combine 2 CodeForLean with an or_else combinator

        :param other:   str or CodeForLean
        :return:        CodeForLean
        """
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
        Combine 2 CodeForLean with an and_then combinator

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
        Add the "try" combinator at the top of self.

        :return: CodeForLean
        """
        if isinstance(self, str):
            self_ = CodeForLean.from_string(self)
        return CodeForLean(combinator=combinator_type,
                           instructions=[self],
                           success_message=success_message)

    def and_finally(self, other):
        """
        Add other before each "or_else" combinator, so that whatever
        sequence of instruction that succeeds ends with other
        e.g. and_finally ("A or_else B", "C")
            -> "(A, C) or_else (B,C)"

        :param other:   another instance of CodeForLean
        :return:        CodeForLean
        """
        # fixme: not used anywhere
        if isinstance(other, str):
            other = CodeForLean.from_string(other)
        if self.is_empty():
            return other
        elif self.is_single() or self.is_and_then():
            # replace self by self and then other
            return self.and_then(other)
        elif self.is_or_else():
            instructions = [piece_of_code.and_finally(other)
                            for piece_of_code in self.instructions]
            return CodeForLean(combinator=LeanCombinator.or_else,
                               instructions=instructions)

    def to_raw_string(self, exclude_no_meta_vars=False) -> str:
        """
        Format CodeForLean into a string which can be sent to Lean

        :param exclude_no_meta_vars:    if True, 'no_meta_vars' instructions
                                        are ignored
        :return: a string understandable by the Lean parser
        """
        # TODO: handle error_messages
        if self.is_empty():
            return ""
        elif self.is_single():
            instruction = self.instructions[0]
            if exclude_no_meta_vars and instruction == 'no_meta_vars':
                return ""
            else:
                return instruction
        elif self.is_and_then():
            strings = [child.to_raw_string(exclude_no_meta_vars)
                       for child in self.instructions]
            strings = [string for string in strings if string != ""]
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

    def add_trace_effective_code(self, num_effective_code):
        """
        Add "trace "EFFECTIVE CODE {num_effective_code}: <code>"
        before each "or_else" combinator.

        :return:        CodeForLean
        """
        # todo: take into account all possibilities, allowing as many "trace
        #  effective code" as needed. e.g.:
        #  - try { , and_then TEC ...} (and 'try' may be removed if EC)
        #  - or_else -> add TEC after each child
        #  - solve1 {...} : Ø



        if self.is_empty():
            return self
        elif not self.is_or_else():
            # replace self by self and_then trace the code
            trace_string = f'trace \"EFFECTIVE CODE {num_effective_code}: ' \
                           f'{self.to_raw_string(exclude_no_meta_vars=True)}\"'
            # trace_code = CodeForLean.from_string(trace_string)
            return self.and_then(trace_string)
        else:
            instructions = [piece_of_code.add_trace_effective_code(
                num_effective_code) for piece_of_code in self.instructions]
            return CodeForLean(combinator=LeanCombinator.or_else,
                               instructions=instructions)

    def get_effective_code(self, traces: str) -> Any:
        """
        This function construct a Lean code that can be substituted to self
        in the virtual file, producing the same effect on the proof state as
        self.

        :param traces: list of traces of effective codes sent by Lean
        :return: string or CodeForLean that can effectively replace self
        """

        # TODO
        pass

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
            if self.contains_apply():
                return self.and_then(no_meta_vars_str)
            else:
                return self
        else:
            instructions = [piece_of_code.add_no_meta_vars()
                            for piece_of_code in self.instructions]
            return CodeForLean(combinator=LeanCombinator.or_else,
                               instructions=instructions)

    def to_string(self):
        """
        Turn a CodeForLean into a string that can be sent to Lean, including
        no_meta_vars and trace_effective_code when needed.
        """

        # ! no_meta_vars, and then trace_effective_code, in that order !
        code_ = self.add_no_meta_vars()
        if not self.is_or_else() or len(self.instructions) <= 1:
            string = code_.to_raw_string()
        else:
            global _CODE_NB
            _CODE_NB += 1
            code_ = code_.add_trace_effective_code(_CODE_NB)
            string = code_.to_raw_string()
        return string

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

    def is_single(self):
        return self.combinator == LeanCombinator.single

    def is_and_then(self):
        return self.combinator == LeanCombinator.and_then

    def is_or_else(self):
        return self.combinator == LeanCombinator.or_else

    def contains_apply(self) -> bool:
        if self.is_empty():
            return False
        elif self.is_single():
            string = self.instructions[0]
            return string.find("apply") != -1
        else:
            return True in [instruction.contains_apply() for instruction in
                            self.instructions]


_VAR_NB = 0
_FUN_NB = 0
_CODE_NB = 0


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


def format_orelse(list_of_choices):
    global _CODE_NB
    length = len(list_of_choices)
    if length == 0:
        raise WrongUserInput
    _CODE_NB += 1
    if length == 1:
        choice = list_of_choices[0]
        if choice.find("apply") != -1:
            choice = choice + ", no_meta_vars"
        return choice
    else:
        list_of_choices = list(map(lambda
             string: f'`[ {string}, trace \"EFFECTIVE CODE {_CODE_NB}: '
                     f'{string}\"]', list_of_choices))
        for k in range(length):
            choice = list_of_choices[k]
            if choice.find("apply") != -1:
                list_of_choices[k] = choice + ", no_meta_vars"
            return " <|> ".join(list_of_choices)


def solve1_wrap(string: str) -> str:
    return "solve1 {" + string + "}"


if __name__ == '__main__':
    code = CodeForLean.empty_code()
    code = code.and_then('assumption')
    code.add_success_message("CQFD!")
    code = code.or_else('norm_num, apply H')
    code = code.or_else('goodbye', success_message="I am leaving!")
    code.add_success_message("Success!")
    # code = code.add_trace_effective_code(42)
    # code = code.add_no_meta_vars()

    print(code.to_raw_string())
    print(code.to_string())
    print(code.extract_success_message("assumption"))   # -> CQFD!
    print(code.extract_success_message("norm"))         # -> Success!
    print(code.extract_success_message("goodbye"))      # -> I am leaving!

    codes = ['assumption', 'norm_num, apply H', "goodbye"]
    lean_code = CodeForLean.or_else_from_list(codes)
    print(lean_code.to_string())

    code = CodeForLean.from_string("juste une instruction")
    print("juste une instruction : " + code.to_string())
    code = CodeForLean.or_else_from_list("juste une instruction 2")
    print("juste une instruction2 : " + code.to_string())
    code = CodeForLean.or_else_from_list(["juste une instruction 2"])
    print("juste une instruction2 : " + code.to_string())
