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
from typing import Any

from deaduction.pylib.actions import WrongUserInput


@dataclass()
class CodeForLean:
    """
    A class for encoding a structured set of instructions for Lean,
    i.e. tactics combined by combinators then or or_else.
    - Basic tactics are defined via the from_string method
    - Combined tactics are defined via the or_else and and_then methods
    - raw code is retrieved via the to_string method
    - an error_message can be added, to be displayed in case of Lean failure
    """
    instruction: str = None  # instruction, iff combinator = "single"
    combinator: str = 'single'  # one of "and_then", "or_else", "single"
    children: Any = None  # instance of CodeForLean
    error_message: str = ""

    # TODO: make properties to ensure that either instruction ≠ ""
    #  (and then combinator ='single' and children are empty)
    #  or combinator and children are non empty, and len(children) ≥ 2

    @classmethod
    def from_string(cls, instruction: str, error_message: str = ''):
        """
        Create a CodeForLean with a single instruction
        """
        return CodeForLean(instruction=instruction,
                           error_message=error_message)

    def or_else(self, other):
        """
        Combine 2 CodeForLean with an or_else combinator

        :param other:   another instance of CodeForLean
        :return:        CodeForLean
        """
        if self.is_or_else():
            self.children.append(other)
            return self
        else:
            return CodeForLean(combinator='or_else',
                               children=[self, other])

    def and_then(self, other):
        """
        Combine 2 CodeForLean with an and_then combinator

        :param other:   another instance of CodeForLean
        :return:        CodeForLean
        """
        if self.is_and_then():
            self.children.append(other)
            return self
        else:
            return CodeForLean(combinator='and_then',
                               children=[self, other])

    def and_finally(self, other):
        """
        Add other before each "or_else" combinator, so that whatever
        sequence of instruction that succeeds ends with other

        :param other:   another instance of CodeForLean
        :return:        CodeForLean
        """
        if self.is_single() or self.is_and_then():
            # replace self by self and then other
            return self.and_then(other)
        elif self.is_or_else():
            children = [piece_of_code.and_finally(other)
                        for piece_of_code in self.children]
            return CodeForLean(combinator='or_else',
                               children=children)

    def to_string(self) -> str:
        """
        Format CodeForLean into a string which can be sent to Lean

        :param effective_code:  if True then include a trace instruction to
                                retrieve effective code.
        :return: string to be sent to Lean
        """
        # TODO: handle error_messages
        if self.instruction:
            return self.instruction

        elif self.is_and_then():
            return ', '.join([child.to_string() for child in self.children])

        elif self.is_or_else():
            strings = ['{' + child.to_string() + '}'
                       for child in self.children]
            return ' <|> '.join(strings)

    def add_trace_effective_code(self, num_effective_code):
        """
        Add "trace "EFFECTIVE CODE {num_effective_code}: <code>"
        before each "or_else" combinator.

        :return:        CodeForLean
        """
        if self.is_single() or self.is_and_then():
            # replace self by self and_then trace the code
            trace_string = f'trace \"EFFECTIVE CODE {num_effective_code}: ' \
                           f'{self.to_string()}\"'
            trace_code = CodeForLean.from_string(trace_string)
            return self.and_then(trace_code)
        elif self.is_or_else():
            children = [piece_of_code.add_trace_effective_code(
                num_effective_code) for piece_of_code in self.children]
            return CodeForLean(combinator='or_else',
                               children=children)

    def add_error_message(self, error_message: str):
        self.error_message = error_message

    def record_into_journal(self):
        """
        Add a record in the journal
        """

        pass

    def is_single(self):
        return self.combinator == "single"

    def is_and_then(self):
        return self.combinator == "and_then"

    def is_or_else(self):
        return self.combinator == "or_else"


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
    if len(list_of_choices) == 0:
        raise WrongUserInput
    _CODE_NB += 1
    if len(list_of_choices) == 1:
        return list_of_choices[0]
    else:
        list_of_choices = map(lambda
                                  string: f'`[ {string}, trace \"EFFECTIVE CODE {_CODE_NB} : {string}\"]',
                              list_of_choices)
        return " <|> ".join(list_of_choices)


def solve1_wrap(string: str) -> str:
    return "solve1 {" + string + "}"


if __name__ == '__main__':
    code = CodeForLean.from_string('assumption')
    code = code.or_else(CodeForLean.from_string('norm_num'))
    code = code.or_else(CodeForLean.from_string('good bye'))
    code = code.and_finally(CodeForLean.from_string('no_meta_vars'))

    print(code)
    print(code.to_string())
    effective_code = code.add_trace_effective_code(42)
    print(effective_code.to_string())
