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
                - Frédéric Le ROux <frederic.le-roux@imj-prg.fr>
Maintainer(s) : - Frédéric Le ROux <frederic.le-roux@imj-prg.fr>
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
from logging import getLogger

from deaduction.pylib.utils import injective_union, intersection_list

log = getLogger(__name__)


class LeanCombinator(str):
    """
    Class clarifying combinators for CodeForLean.
    """
    single_code =     ""
    and_then =          "and_then"
    or_else =           "or_else"
    try_ =              "try"
    solve1 =            "solve1"
    focus =             "focus"
    iterate =           "iterate"


class SingleCode:
    """
    A class for encapsulating a single Lean instruction, keeping the
    information of which MathObject are used by the instruction.

    Ex: SingleCode.string = and.intro {} {}
        SingleCode.used_properties = list of 2 MathObjects representing the
        properties.
    The operator, rw_item, outcome_operator attributes are used to build the
    proof tree widget. They are either MathObject or Statements.

    :param rw_item: the property used for a substitution, e.g. "f(
    x)=y", or a definition or theorem.

    """
    def __init__(self, string: str, used_properties=None,
                 operator=None, rw_item=None, outcome_operator=None):
        self.string = string
        if used_properties is None:
            used_properties = []
        if not isinstance(used_properties, list):
            used_properties = [used_properties]
        self.used_properties = used_properties
        self.operator = operator
        self.rw_item = rw_item
        self.outcome_operator = outcome_operator

    def __repr__(self):
        attributes = []
        for key in self.__dict__:
            value = str(self.__getattribute__(key))
            if key == "string":
                value = '"' + value + '"'
            attributes.append(key + "=" + value)
        string = "SingleCode(" + ", ".join(attributes) + ")"
        return string

    def to_code(self) -> str:
        """
        Return the code to be sent to Lean.
        """
        if self.string.find("{}") != -1:
            names = [prop.display_name for prop in self.used_properties]
            return self.string.format(*names)
        else:
            return self.string


class CodeForLean:
    """
    A class for encoding a structured set of instructions for Lean,
    i.e. tactics combined by combinators and_then / or_else.
    - Basic tactics are defined via the from_string method
    - Combined tactics are defined via the or_else and and_then methods
    - code is retrieved via the to_code method
    - an error_msg can be added, to be displayed in case of Lean failure
    - a success_msg can be added, to be displayed in case of success
    (depending of the effective code in case of or_else combinator)

        - if combinator = single_code, then instructions contains a unique
        term, of type SingleCode
        - else all terms in the instructions list are of type CodeForLean.
    """
    instructions: [Any]   # type: [Union[CodeForLean, SingleCode]]
    combinator:   str = LeanCombinator.single_code
    error_msg:    str = ""
    _success_msg:  str = ""
    conjunction       = None  # type: (Union[MathObject, str])
    disjunction       = None  # type: (Union[MathObject, str])
    subgoal           = None  # type: Union[MathObject, str]
    # The following is used to store the number of an or_else instructions
    or_else_node_number:   Optional[int] = None

    # The following counts the total number of or_else instructions so far
    or_else_node_counter = 0

    attributes = {"instructions", "combinator", "error_msg", "success_msg",
                  "conjunction", "disjunction", "subgoal",
                  "or_else_node_number"}

    def __init__(self, *args, **kwargs):
        """
        __init__ may be called with args either
            - a SingleCode instance,
            - a single string,
            - a string and a list of MathObjects
            These data will be used to make a SingleCode instance.

        kwargs may include any arguments corresponding to a class attribute,
        as in the cls.attribute set.
        """

        # Instruction from args
        if len(args) == 1:
            instruction = args[0]
            if not isinstance(instruction, SingleCode):
                instruction = SingleCode(instruction)
        if len(args) == 2:
            instruction = SingleCode(args[0], used_properties=args[1])
        if args:
            self.instructions = [instruction]
        else:
            self.instructions = []  # Empty code

        # Args in kwargs
        # print("kwargs:")
        # print(kwargs)
        for key in kwargs:
            if key in self.attributes:
                value = kwargs[key]
                self.__setattr__(key, value)
        if len(self.instructions) == 1 and isinstance(self.instructions[0],
                                                      SingleCode):
            self.combinator = LeanCombinator.single_code
        if len(self.instructions) > 1 and self.is_single_code():
            raise AttributeError("Bad Lean combinator: single string for "
                                 "several instructions")

    # The following entails crash when self.operator is a Statement:
    # def __repr__(self):
    #     attributes = []
    #     for key in self.__dict__:
    #         attribute = self.__getattribute__(key)
    #         attribute = ('"' + attribute + '"' if isinstance(attribute, str)
    #                      else str(attribute))
    #         attributes.append(key + "=" + attribute)
    #     string = "CodeForLean(" + ", ".join(attributes) + ")"
    #     return string

    @classmethod
    def empty_code(cls, error_msg: str = ''):
        """
        Create an empty code, useful to initialize a sequence of codes
        """
        return cls(instructions=[],
                   error_msg=error_msg)

    @classmethod
    def from_string(cls,
                    string: str,
                    used_properties=None,  # type: [MathObject]
                    operator=None,
                    rw_prop_or_statement=None,
                    error_msg: str = "",
                    success_msg: str = ""):
        """
        Create a CodeForLean with a single instruction, with no used
        properties.
        """
        instruction = SingleCode(string, used_properties, operator=None,
                                 rw_item=None)
        return cls(instructions=[instruction],
                   error_msg=error_msg,
                   success_msg=success_msg)

    @classmethod
    def from_list(cls,
                  instructions: [],
                  combinator=LeanCombinator.and_then,
                  error_msg: str = '',
                  global_success_msg: str = ""):
        """
        Create a list of instructions chained by or_else or and_then
        combinator.

        :param instructions: list of CodeForLean, str, or tuple.
        """
        for i in range(len(instructions)):
            if isinstance(instructions[i], str):
                instructions[i] = CodeForLean(instructions[i])
            elif isinstance(instructions[i], tuple):
                instructions[i] = CodeForLean(*instructions[i])

        # From now on instructions is a list of CodeForLean
        if len(instructions) == 1:
            instruction = instructions[0]
            if isinstance(instruction, CodeForLean):
                return instruction
            elif isinstance(instruction, SingleCode):
                return CodeForLean(instruction)
        else:
            return cls(instructions=instructions,
                       combinator=combinator,
                       error_msg=error_msg,
                       success_msg=global_success_msg)

    @classmethod
    def or_else_from_list(cls,
                          instructions: [],  # type : [ Union[CodeForLean,
                          #                str, tuple] ]
                          error_msg: str = '',
                          global_success_msg: str = ""):
        """
        Create an or_else CodeForLean from a (list of) strings or CodeForLean

        :param instructions: list of CodeForLean, str, or tuple.
        """
        return cls.from_list(instructions=instructions,
                             combinator=LeanCombinator.or_else,
                             error_msg=error_msg,
                             global_success_msg=global_success_msg)

    @classmethod
    def and_then_from_list(cls,
                           instructions: [],
                           error_msg: str = '',
                           global_success_msg: str = ""):
        """
        Create an or_else CodeForLean from a (list of) strings or CodeForLean.

        :param instructions: list of CodeForLean, str, or tuple.
        """
        return cls.from_list(instructions=instructions,
                             combinator=LeanCombinator.and_then,
                             error_msg=error_msg,
                             global_success_msg=global_success_msg)

    @property
    def operator(self):
        """
        Return the operator attribute of the first SingleCode found in self.
        """
        if not self.instructions:
            return None
        if self.combinator is LeanCombinator.and_then:
            # Return first operator in instructions
            for instruction in self.instructions:
                if instruction.operator:
                    return instruction.operator
        else:
            operator = self.instructions[0].operator
            return operator

    @operator.setter
    def operator(self, operator):
        """
        Set the operator attribute of the first SingleCode in self.
        @param operator: MathObject.
        """
        if self.is_or_else():
            for instruction in self.instructions:
                instruction.operator = operator
        elif self.instructions:
            instruction = self.instructions[0]
            instruction.operator = operator

    @property
    def rw_item(self):
        """
        Return the operator attribute of the first SingleCode found in self.
        """
        if not self.instructions:
            return None
        instruction = self.instructions[0]
        return instruction.rw_item

    @rw_item.setter
    def rw_item(self, rw_item):
        """
        Set the rw_item attribute of the first SingleCode in self, or of all
        the codes if self is or_else.
        """
        if self.is_or_else():
            for instruction in self.instructions:
                instruction.rw_item = rw_item
        elif self.instructions:
            instruction = self.instructions[0]
            instruction.rw_item = rw_item

    @property
    def outcome_operator(self):
        """
        Return the operator attribute of the first SingleCode found in self.
        """
        if not self.instructions:
            return None
        instruction = self.instructions[0]
        return instruction.outcome_operator

    @outcome_operator.setter
    def outcome_operator(self, outcome_operator):
        """
        Set the rw_item attribute of the first SingleCode in self, or of all
        the codes if self is or_else.
        """
        if self.is_or_else():
            for instruction in self.instructions:
                instruction.outcome_operator = outcome_operator
        elif self.instructions:
            instruction = self.instructions[0]
            instruction.outcome_operator = outcome_operator

    @property
    def success_msg(self):
        """
        Return self's success_msg, or, if self is and_then, the first
        success_msg found in self's instructions.
        """
        if self._success_msg:
            return self._success_msg
        elif self.is_and_then():
            for instruction in self.instructions:
                msg = instruction.success_msg
                if msg:
                    return msg

    @success_msg.setter
    def success_msg(self, msg: str):
        self._success_msg = msg

    def or_else(self, other, success_msg=""):
        """
        Combine 2 CodeForLean with an or_else combinator.

        :type other: Union[str, (str, [MathObjects], CodeForLean]
        :return: CodeForLean
        """
        if other is None:
            return self
        if isinstance(other, str) or isinstance(other, tuple):
            other = CodeForLean(other)
        if other.success_msg == "":
            other.success_msg = success_msg
        if other.error_msg:
            self.error_msg = other.error_msg
        if self.is_empty():
            return other
        elif self.is_or_else() \
                and not self.success_msg and not other.success_msg:
            self.instructions.append(other)
            return self
        else:
            return CodeForLean(combinator=LeanCombinator.or_else,
                               instructions=[self, other],
                               error_msg=self.error_msg)

    def and_then(self, other, success_msg=""):
        """
        Combine 2 CodeForLean with an and_then combinator.

        :param other:       str or tuple or SingleCode or CodeForLean
        :param success_msg: str
        :return:            CodeForLean
        """
        if not success_msg:
            success_msg = self.success_msg
        if isinstance(other, str) or isinstance(other, tuple):
            other = CodeForLean(other)
        if self.is_empty():
            if not other.success_msg:
                other.add_success_msg(success_msg)
            return other
        elif other == "" or other.is_empty():
            return self
        elif self.is_and_then():
            self.instructions.append(other)
            self.success_msg = success_msg
            return self
        else:
            return CodeForLean(combinator=LeanCombinator.and_then,
                               instructions=[self, other],
                               success_msg=success_msg)

    def single_combinator(self, combinator_type, success_msg=""):
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
                           success_msg=success_msg)

    def try_(self, success_msg=""):
        """
        Turn self into
                            "self <|> skip",
        which is equivalent to
                            "try {self}"
        but will allow to retrieve an "effective code" msg in case of
        failure. (Note that this instruction always succeeds.)

        :return: CodeForLean
        """
        # if isinstance(self, str):
        #     self_ = CodeForLean.from_string(self)
        skip = CodeForLean.from_string("skip")
        return CodeForLean(instructions=[self, skip],
                           combinator=LeanCombinator.or_else,
                           success_msg=success_msg)

    def solve1(self, success_msg=""):
        code = CodeForLean(instructions=[self],
                           combinator=LeanCombinator.solve1,
                           success_msg=success_msg)
        return code

    def to_code(self, exclude_no_meta_vars=False) -> str:
        """
        Format CodeForLean into a string which can be sent to Lean

        :param exclude_no_meta_vars:    if True, 'no_meta_vars' instructions
                                        are discarded
        :return: a string understandable by the Lean parser
        """

        # TODO: handle error_msgs
        if self.is_empty():
            return ""
        elif exclude_no_meta_vars and self.is_no_meta_vars():
            return ""
        elif self.is_single_code():
            code = self.instructions[0].to_code()
            return code
            # if exclude_no_meta_vars and code == 'no_meta_vars':
            #     return ""
            # else:
            #     return code
        elif self.is_and_then():
            strings = []
            for instruction in self.instructions:
                string = instruction.to_code(exclude_no_meta_vars)
                if string:
                    strings.append(string)
            return ', '.join(strings)
        elif self.is_or_else():
            strings = [child.to_code(exclude_no_meta_vars)
                       for child in self.instructions]
            strings = ['`[ ' + string + ']'
                       for string in strings if string != ""]
            return ' <|> '.join(strings)
        else:
            return self.combinator \
                + " {" \
                + self.instructions[0].to_code(exclude_no_meta_vars) \
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
        msgs, the second is self with marked or_else node.
        """

        if self.is_single_code():
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
                                      error_msg=self.error_msg,
                                      success_msg=self.success_msg)

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

        if self.is_single_code():
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
                                   error_msg=self.error_msg,
                                   success_msg=self.success_msg,
                                   or_else_node_number=self.or_else_node_number)

            return new_code, found

    def add_no_meta_vars(self):
        """
        Add the "no_meta_vars" tactic after each piece of code that contains
        "apply"
        """

        if self.is_empty():
            return self
        elif not self.is_or_else():
            # replace self by self and_then no_meta_vars
            if self.could_have_meta_vars():
                # return self.and_then(no_meta_vars_str)
                return self.and_then(NO_META_VARS)
            else:
                return self
        else:
            instructions = [piece_of_code.add_no_meta_vars()
                            for piece_of_code in self.instructions]
            return CodeForLean(combinator=LeanCombinator.or_else,
                               instructions=instructions,
                               success_msg=self.success_msg,
                               error_msg=self.error_msg)

    def to_decorated_code(self):
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
        string = code2.to_code()
        return code1, string

    def extract_success_msg(self, effective_code=""):
        """
        Extract the success msg, if any, corresponding to the effective
        code.

        :param effective_code:  Lean's result of the "trace effective code"
                                instruction
        :return:                success msg to be displayed
        """
        success_msg = ""
        # First try specific success_msg corresponding to effective_code
        # (if provided)
        if self.is_or_else() and effective_code:
            for instruction in self.instructions:
                if instruction.to_code().startswith(effective_code):
                    success_msg = instruction.success_msg
        #  Send global success_msg if no specific msg has been found
        if not success_msg:
            success_msg = self.success_msg
        return success_msg

    def add_error_msg(self, error_msg: str):
        """
        Add error_message to self, and if self.is_or_else, also add it to
        all the alternatives.
        """
        if self.is_or_else():
            for code in self.instructions:
                code.add_error_msg(error_msg)
        self.error_msg = error_msg

    def add_success_msg(self, success_msg: str):
        if self.is_or_else():
            for code in self.instructions:
                code.add_success_msg(success_msg)
        self.success_msg = success_msg

    def add_conjunction(self, p_and_q, p=None, q=None):
        """
        Indicate that self will split a target conjunction 'P and Q',
        and store 'P and Q', 'P', 'Q'. If not provided, P and Q are computed
        as the children of p_and_q.
        """
        if not p:
            p = p_and_q.children[0]
        if not q:
            q = p_and_q.children[1]
        self.conjunction = (p_and_q, p, q)

    def add_disjunction(self, p_or_q, p=None, q=None):
        """
        Indicate that self will split a target disjunction 'P or Q',
        and store 'P and Q', 'P', 'Q'. If not provided, P and Q are computed
        as the children of p_or_q.
        """
        if not p:
            p = p_or_q.children[0]
        if not q:
            q = p_or_q.children[1]
        self.disjunction = (p_or_q, p, q)

    def add_subgoal(self, subgoal):
        """
        Indicate that self will create a new subgoal.

        :param subgoal: str or MathObject
        """

        # FIXME: obsolete?
        self.subgoal = subgoal

    def is_empty(self):
        return self.instructions == []

    def is_single_code(self):
        return (self.combinator == LeanCombinator.single_code and not
                self.is_empty())

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
        if self.is_single_code():
            return False
        elif self.is_or_else():
            return True
        else:
            return True in [code_.has_or_else() for code_ in self.instructions]

    def could_have_meta_vars(self) -> bool:
        if self.is_empty():
            return False
        elif self.is_single_code():
            code_ = self.instructions[0].to_code()
            return (code_.find("apply") != -1 or code_.find("have") != -1
                    or code_.find("rw") != -1)
        else:
            return any(instruction.could_have_meta_vars() for
                       instruction in self.instructions)

    def is_no_meta_vars(self):
        return (self.is_single_code() and
                self.to_code() == NO_META_VARS.to_code())

    def add_used_properties(self, used_properties):
        """
        Add used properties to every single code instruction in self.

        :param used_properties: MathObject or [MathObject]
        """

        if not isinstance(used_properties, list):
            used_properties = [used_properties]

        if self.is_single_code():
            instruction = self.instructions[0]
            assert isinstance(instruction, SingleCode)
            instruction.used_properties.extend(used_properties)
        else:
            for instruction in self.instructions:
                assert isinstance(instruction, CodeForLean)
                instruction.add_used_properties(used_properties)

    def used_properties(self):
        """
        Return used_properties appearing in self, provided they appear in
        all or_else alternatives. (This is probably useless if there are
        still some or_else alternative in self).

        :return: [Union(ContextMathObject, str)]
        """

        if self.is_single_code():
            instruction = self.instructions[0]
            assert isinstance(instruction, SingleCode)
            up = instruction.used_properties
        elif not self.is_or_else():  # Return union of used_props
            up = injective_union([ins.used_properties()
                                  for ins in self.instructions])
        else:  # Return intersection of used_props
            up = intersection_list([ins.used_properties()
                                    for ins in self.instructions])

        return up

    @classmethod
    def no_meta_vars(cls):
        return cls("no_meta_vars")

    @classmethod
    def norm_num(cls, location=None):
        instr = f"norm_num at {location}" if location else "norm_num"
        return cls(instr)

    def and_try_norm_num(self, location=None):
        """
        Add try {norm_num [at <location>]} after self.
        Beware that this is often too powerful, and normal form sometimes
        differs from expected, e.g. not (P and Q) is normalized into (P =>
        not Q).
        """
        try_norm_num = CodeForLean.norm_num(location=location).try_()
        code = self.and_then(try_norm_num)
        return code

    @classmethod
    def simp_only(cls, lemmas=None, location=None):
        """
        Instruction "simp only [lemmas] at <location>".
        lemmas may be a list of strings or a single string.
        """
        location = f"at {location}" if location else ""
        if not lemmas:
            lemmas = ''
        if isinstance(lemmas, list):
            lemmas = ' '.join(lemmas)

        instr = f"simp only [{lemmas}] {location}"
        return cls(instr)

    def and_try_simp_only(self, lemmas=None, location=None):
        """
        Add try {norm_num [at <location>]} after self.
        """
        simp = CodeForLean.simp_only(lemmas=lemmas, location=location)
        code = self.and_then(simp.try_())
        return code


# _VAR_NB = 0
# _FUN_NB = 0
#
#
# def get_new_var():
#     global _VAR_NB
#     _VAR_NB += 1
#     return "x{0}".format(_VAR_NB)
#
#
# def get_new_fun():
#     global _FUN_NB
#     _FUN_NB += 1
#     return "f{0}".format(_FUN_NB)
#
#
# # OBSOLETE : see mathobj.give_name.get_new_hyp()
# def get_new_hyp():
#     global _VAR_NB
#     _VAR_NB += 1
#     return "h{0}".format(_VAR_NB)
#
#
# def solve1_wrap(string: str) -> str:
#     # (obsolete)
#     return "solve1 {" + string + "}"


NO_META_VARS = CodeForLean("no_meta_vars")


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
    code_ = CodeForLean.from_string('assumption')
    print(code_)
    code_ = code_.and_then(CodeForLean.from_string("toto").try_())
    print(code_)
    code_.add_success_msg("CQFD!")
    code_2 = CodeForLean.or_else_from_list(['apply H', 'Great !'])
    code_ = code_.or_else(code_2)
    code_ = code_.or_else('goodbye', success_msg="I am leaving!")
    code_.add_success_msg("Success!")
    # code_ = code_.add_trace_effective_code_(42)
    # code_ = code_.add_no_meta_vars()

    code_, decorated_code_string = code_.to_decorated_code()
    print(decorated_code_string)
    print(code_.to_code())
    print("Exclude no_meta_vars:")
    print(code_.to_code(True))

    for choice in [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 1),
                   (3, 67)]:
        code_1, b = code_.select_or_else(*choice)
        print(f"Choice {choice} found: {b}")
        print(code_1.to_code())

    code_1, b = code_.select_or_else(0,1)
    code_2, b = code_1.select_or_else(2,1)
    print(code_2.to_code())

    code_1 = CodeForLean.from_string("norm_num at *").solve1()
    code_2 = CodeForLean.from_string("compute_n 10")
    code_3 = (CodeForLean.from_string("norm_num at *").try_()).and_then(code_2)
    possible_code = code_1.or_else(code_3)

    print("----------------")
    print(possible_code.to_code())
    code_, deco = possible_code.to_decorated_code()
    # print(deco)
    print(code_)
    code_, found = code_.select_or_else(3,0)
    print(code_.to_code())
    print(code_.has_or_else())
    code_, found = code_.select_or_else(4,0)
    print(code_.to_code())
    print(code_.has_or_else())


