"""
##############################################################################
# exercise.py : provide the classes Statement, Exercise, Definition, Theorem #
##############################################################################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 07 2020 (creation)
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
from typing import List, Dict, Any, Optional
import logging
from time import strftime
from copy import      copy
import tomli_w

import deaduction.pylib.config.vars             as cvars

from deaduction.pylib.text                  import (logic_buttons_line_1,
                                                    logic_buttons_line_2,
                                                    compute_buttons_line)
import deaduction.pylib.text.text as text

from deaduction.pylib.actions.actiondef     import Action
import deaduction.pylib.actions.magic
from deaduction.pylib.coursedata.utils     import (find_suffix,
                                                   substitute_macros,
                                                   extract_list)
# from deaduction.pylib.coursedata.settings_parser import vars_from_metadata
from deaduction.pylib.coursedata.auto_steps import AutoStep

log = logging.getLogger(__name__)
global _

##############################################
# Lists of all instances of the Action class #
##############################################
LOGIC_BUTTONS = deaduction.pylib.actions.logic.__actions__
# e.g. key = action_and, value = corresponding instance of the class Action
PROOF_BUTTONS = deaduction.pylib.actions.proofs.__actions__
MAGIC_BUTTONS = deaduction.pylib.actions.magic.__actions__
COMPUTE_BUTTONS = deaduction.pylib.actions.compute.__actions__


@dataclass
class StructuredContent:
    """
    A class to store the structured content of a Lean Statement.
    """

    first_line_nb: int
    last_line_nb: int

    name: str
    hypotheses: str
    conclusion: str
    raw_metadata: Dict[str, str]
    lean_code: str

    course_file_content: str

    skeleton = "lemma {} \n{}:=\n{}\nbegin\n{}\nend\n"

    #  This must be coherent with Exercise.history_date():
    # history_name_prefix = 'exercise.history_'
    
    @property
    def metadata_str(self) -> str:
        """
        Format metadata dict for Lean files. Indent values if needed.
        """

        # metadata_str = metadata_to_str(self.raw_metadata)
        metadata_str = metadata_to_toml(self.raw_metadata)

        packed_metadata = '/- dEAduction\n' + metadata_str + '\n-/\n'
        # print(f"Exercise metadata: {packed_metadata}")
        return packed_metadata

    @property
    def lemma_content(self) -> str:

        # core_content = self.negated_core_content
        # if not core_content:
        core_content = f'{self.hypotheses} :\n{self.conclusion}'

        skeleton = self.skeleton
        content = skeleton.format(self.name,
                                  core_content,
                                  self.metadata_str,
                                  comment(indent(self.lean_code))
                                  )
        # Remove double CR
        while content.find('\n\n') != -1:
            content = content.replace('\n\n', '\n')

        return content

    @classmethod
    def new_content(cls, initial_content, additional_metadata, lean_code,
                    history_nb):
        """
        Create a new StructuredContent instance by updating initial_content
        with additional_metadata, and replacing code by lean_code.
        Date is also included in metadata.
        Name is modified by inserting history_nb at the end.
        """

        # Compute new name
        new_name = initial_content.name + '_' + str(history_nb)

        # Add date to metadata
        date = strftime("%d%b%Hh%M")
        additional_metadata['history_date'] = date

        # New metadata
        new_metadata = initial_content.raw_metadata.copy()
        new_metadata.update(additional_metadata)

        new_content = cls(initial_content.first_line_nb,
                          initial_content.last_line_nb,
                          new_name,
                          initial_content.hypotheses,
                          initial_content.conclusion,
                          new_metadata, lean_code,
                          initial_content.course_file_content)
        return new_content

    def content_with_lemma(self):
        """
        Compute the content of the history file, by adding lemma_content to
        the course_file_content at line self.last_line_nb.
        This method should be applied to a new_content.
        """
        content_lines = self.course_file_content.splitlines()

        part_1 = '\n'.join(content_lines[:self.last_line_nb])
        part_2 = self.lemma_content
        part_3 = '\n'.join(content_lines[self.last_line_nb:])

        history_file = part_1 + '\n\n' + part_2 + '\n' + part_3

        return history_file

    def has_identical_core_lemma_content(self, other):
        return (self.hypotheses.strip(), self.conclusion.strip()) == \
            (other.hypotheses.strip(), other.conclusion.strip())


@dataclass
class Statement:
    """
    A class for storing information about Lean's statements.
    This is the parent class for classes Exercise, Definition, Theorem.
    """
    lean_line:              int
    # line number of the lemma declaration in Lean file
    lean_name:              str
    # 'set_theory.unions_and_intersections.exercise.union_distributive_inter'
    lean_core_statement:    str
    # 'A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)'
    lean_variables:         str
    # '(X : Type) (A : set X)'
    pretty_name:            str
    # e.g. 'Union d'intersections'
    description_intro:      str             = None
    # e.g. "Formalize the following statement:"
    description:            str             = None
    # "L'union est distributive par rapport à l'intersection"
    text_book_identifier:   str             = None
    lean_begin_line_number: int             = None
    # proof starts here...
    # this value is set to None until "begin" is found
    lean_end_line_number:   int             = None
    # ...and ends here

    course:                 Any             = None
    # the parent course

    _initial_proof_state:    Any             = None
    # this is filled when pre-processing

    __negated_goal:         Any                     = None

    # auto_steps: str                         = ''
    auto_test: list                                 = None
    __refined_auto_steps: Optional[List[AutoStep]] = None
    _raw_metadata: Dict[str, str]                  = None

    info:                   Dict[str, Any]         = None
    # Any other (non-essential) information

    # def __repr__(self):
    #     return self.pretty_name if self.pretty_name else self.lean_name

    def __str__(self):
        s = "Statement " + self.pretty_name
        return s

    @property
    def metadata(self):
        return self.info

    def metadata_get(self, name):
        """
        Get metadata by looking in self.metadata, and then by default in
        course.metadata.
        """
        self_metadata = self.metadata.get('name')
        if self_metadata:
            return self_metadata

        return self.course.metadata.get(name)

    def restricted_calculator_definitions(self):
        """
        If self has restricted_calculator_definitions in metadata,
        then return the list.
        Else if this happens in self.course, return this list.
        """

        if self.metadata.get('more_definitions'):
            return None

        restricted_defs = self.metadata_get('restricted_calculator_definitions')

        if restricted_defs:
            if isinstance(restricted_defs, str):
                restricted_defs = restricted_defs.split()
            return restricted_defs
        elif restricted_defs in ("", []):
            return []

        return self.course.restricted_calculator_definitions()

    def calculator_definitions(self):
        """
        Return self's more_definitions if there are some, maybe augmented
        with course defs.
        Else return self's restricted def.
        """
        restricted_defs = self.restricted_calculator_definitions()
        restricted_courses_defs = self.course.restricted_calculator_definitions()
        course_defs = self.course.more_calculator_definitions()
        defs = self.metadata.get('more_calculator_definitions')
        if defs:
            if isinstance(defs, str):
                defs = defs.split()
            if restricted_courses_defs:
                defs += restricted_courses_defs
            if course_defs:
                defs += course_defs
            return defs

        return restricted_defs

    @classmethod
    def from_parser_data(cls, **data):
        """
        Create a Statement instance from data.

        :param data:    dictionary containing the relevant information:
                        keys in data will be transformed into attributes.
        """
        attributes = cls.attributes()
        extract_data = {}
        for attribute in attributes:
            if attribute in data.keys():
                extract_data[attribute] = data.pop(attribute)
        # extract_data = {attribute: data.setdefault(attribute, None)
        #                for attribute in attributes}
        # keep only the relevant data, i.e. the keys which corresponds to
        # attribute of the class. The remaining information are put in
        # the self.info dictionary
        #FIXME: obsolete
        for field_name in data:  # replace string by bool if needed
            if data[field_name] == 'True':
                data[field_name] = True
            elif data[field_name] == 'False':
                data[field_name] = False

        polish_data(extract_data)

        extract_data["info"] = data
        return cls(**extract_data)

    @classmethod
    def attributes(cls):
        """return the list of attributes of the class"""
        # FIXME: deprecated in Python3.10, use inspect.get_annotations(cls)
        attributes = Statement.__annotations__
        if cls != Statement:
            attributes.update(cls.__annotations__)
        return attributes

    @property
    def complete_description(self):
        """
        Return description_intro + description.
        """
        description_intro = self.description_intro
        description = self.description
        if description_intro:
            complete_description = self.description_intro
            if description:
                complete_description += '\n' + description
        else:
            complete_description = description
        return complete_description

    @property
    def html_complete_description(self):
        return self.complete_description.replace("\n", "<br>")

    @property
    def initial_proof_state(self):
        return self._initial_proof_state

    @initial_proof_state.setter
    def initial_proof_state(self, ips):
        self._initial_proof_state = ips

    def to_math_object(self):
        goal = self.goal()
        math_object = goal.to_math_object() if goal else None
        return math_object

    @property
    def lean_short_name(self):
        """
        Keep only the last two parts, e.g.
        'set_theory.unions_and_intersections.exercise.union_distributive_inter'
        -> 'exercise.union_distributive_inter'
        """
        return '.'.join(self.lean_name.split('.')[-2:])

    def statement_to_text(self, text_format='utf8'):
        """
        if self has attribute 'initial_proof_state', then return a string
        with a text version of initial goal. E.g.
        Let X be a set.
        Let A be a subset of X.
        Let B be a subset of X.
        Prove that X \\ (A ∪ B) = (X \\ A) ∩ (X \\ B).
        """
        if self.initial_proof_state is not None:
            initial_goal = self.initial_proof_state.goals[0]
            if isinstance(self, Exercise):
                to_prove = True
                open_pb = self.is_open_question
            else:
                to_prove = False
                open_pb = False
            content = initial_goal.goal_to_text(to_prove=to_prove,
                                                open_problem=open_pb,
                                                format_=text_format)
        else:
            content = ""
        return content

    @property
    def target(self):
        """
        Return target of main goal, whose math_type is the target property.
        """
        if self.initial_proof_state:
            return self.initial_proof_state.goals[0].target

    def pretty_hierarchy(self, outline):
        """
        Return the ordered (chapter > section > …) list of sections pretty
        names corresponding to where self is in the lean file. If the
        self.lean_name is
        'rings_and_ideals.first_definitions.definition.the_statement',
        return ['Rings and ideals', 'First definitions']. Most of the time
        outline will be present_course.outline, where present_course is the
        instance of Course which initiated self.

        :param outline: A dictionary in which keys are hierarchy levels (e.g.
                'rings_and_ideals') and values are their pretty names
                (e.g. 'Rings and ideals').
        :return: The list of sections pretty names.
        """

        pretty_hierarchy = []

        def fkt(rmg_hierarchy):
            if not rmg_hierarchy:
                return
            else:
                pretty_hierarchy.insert(0, outline[rmg_hierarchy])
                # 'a.b.c.d' -> 'a.b.c'
                rmg_hierarchy = '.'.join(rmg_hierarchy.split('.')[:-1])
                fkt(rmg_hierarchy)

        name = '.'.join(self.lean_name.split('.')[:-2])
        fkt(name)

        return pretty_hierarchy

    def ugly_hierarchy(self):
        """
        Return the hierarchical list of lean namespaces ending with the
        namespace containing self.
        e.g.
        'set_theory.unions_and_intersections.exercise.union_distributive_inter'
        -> [set_theory, unions_and_intersections]
        """
        ugly_hierarchy = self.lean_name.split('.')[:-2]
        return ugly_hierarchy

    def open_namespace_str(self) -> str:
        """
        Return a string to be used for opening all namespaces.
        e.g.
        'set_theory.unions_and_intersections.exercise.union_distributive_inter'
        ->
        namespace set_theory
        namespace unions_and_intersections
        """
        namespaces = self.ugly_hierarchy()

        beginning_of_file = ""
        for namespace in namespaces:
            beginning_of_file += "namespace " + namespace + "\n"
        return beginning_of_file

    def close_namespace_str(self) -> str:
        """
        Return a string to be used for closing all namespaces.
        e.g.
        'set_theory.unions_and_intersections.exercise.union_distributive_inter'
        ->
        end unions_and_intersections
        end set_theory
        """
        namespaces = self.ugly_hierarchy()
        end_of_file = ""
        while namespaces:
            namespace = namespaces.pop()
            end_of_file += "end " + namespace + "\n"
        return end_of_file

    def open_read_only_namespace_str(self) -> str:
        """
        Return a string to be used for opening all read-only namespaces that
        occurs prior to self in the course file.
        e.g.
        open set
        open definitions
        """
        if not hasattr(self.course, "opened_namespace_lines"):
            return ""
        lines_dic = self.course.opened_namespace_lines
        namespaces_lines = ["open " + key for key, value in lines_dic.items()
                            if value < self.lean_begin_line_number]
        open_namespaces = "\n".join(namespaces_lines)
        return open_namespaces + '\n'

    def caption(self, is_exercise=False, only_ips=True) -> str:
        """
        Return a string that shows a simplified version of the statement
        (e.g. to be displayed as a tooltip).
        """
        if not self.initial_proof_state:
            if only_ips:
                text = _("(Computing statement, please wait...)")
            else:
                text = self.lean_core_statement
        else:
            goal = self.initial_proof_state.goals[0]
            # target = goal.target
            # text = target.math_type.to_display(is_math_type=True)
            type_ = "exercise" if is_exercise else "non-exercise"
            text = goal.to_tooltip(type_=type_)
            if cvars.get("functionality.allow_implicit_use_of_definitions"):
                if isinstance(self, Definition) and self.implicit_use:
                    implicit = '<i>(' + _("implicit use allowed") + ')</i><br>'
                    text = implicit + text
        return text

    @property
    def refined_auto_steps(self) -> [AutoStep]:
        """
        Turn the toml data parsed from the lean file into a list of AutoStep.
        """
        if self.__refined_auto_steps:
            return self.__refined_auto_steps

        # if not self.auto_steps:
        if not self.auto_test:
            return []
        else:
            auto_steps = [AutoStep.from_toml_data(step)
                          for step in self.auto_test]

        # auto_steps_strings = auto_steps_strings.replace('\\n', ' ')
        # auto_steps_strings = auto_steps_strings.split(',')
        # auto_steps = []
        # for string in auto_steps_strings:
        #     string = string.strip()
        #     if string != '':
        #         auto_steps.append(AutoStep.from_string(string))
        # # Remove None steps:
        # # auto_steps = [step for step in auto_steps if step]
        # self.__refined_auto_steps = auto_steps
        return auto_steps

    @refined_auto_steps.setter
    def refined_auto_steps(self, refined_auto_steps) -> [AutoStep]:
        self.__refined_auto_steps = refined_auto_steps

    def has_name(self, lean_name):
        return self.lean_name.endswith(lean_name)

    def has_pretty_name(self, pretty_name):
        return self.pretty_name.__contains__(pretty_name)

    def is_definition(self):
        return isinstance(self, Definition)

    def is_theorem(self):
        return isinstance(self, Theorem)

    def is_exercise(self):
        return isinstance(self, Exercise)

    # @property
    # def type(self):
    #     if self.is_definition():
    #         return _('definition')
    #     elif self.is_theorem():
    #         return _('theorem')
    #     elif self.is_exercise():
    #         return _('exercise')

    @property
    def type_(self):
        if self.is_definition():
            return _('definition')
        elif self.is_theorem():
            return _('theorem')
        elif self.is_exercise():
            return _('exercise')

    def goal(self):
        ips = self.initial_proof_state
        if ips:
            return ips.goals[0]

    def negated_goal(self):
        if not self.__negated_goal:
            goal = self.goal()
            if goal:
                self.__negated_goal = goal.negated_goal(goal)
        return self.__negated_goal

    @property
    def auxiliary_definitions(self):
        aux_def = self.info.get('auxiliary_definitions')
        if isinstance(aux_def, str):
            return aux_def.split()
        if isinstance(aux_def, list):
            return aux_def
        return []


class Definition(Statement):
    # def __init__(self, **data):
    #     implicit_use = data.pop('implicit_use') if 'implicit_use' in data \
    #                    else False
    #     super().__init__(self, **data)
    #     self.implicit_use_activated = implicit_use

    @property
    def implicit_use(self):
        if 'implicit_use' in self.info and self.info['implicit_use']:
            return True
        else:
            return False

    def extract_iff(self):
        ipf = self.initial_proof_state
        if not ipf:
            return None
        goal = ipf.goals[0]
        target = goal.target
        if not target.is_iff():
            return None
        else:
            return target.math_type

    def extract_left_term(self):
        iff = self.extract_iff()
        if iff:
            return iff.children[0]

    def extract_right_term(self):
        iff = self.extract_iff()
        if iff:
            return iff.children[1]


@dataclass
class Theorem(Statement):
    pass


LEAN_CLASSICAL_LOGIC = "local attribute[instance] classical.prop_decidable\n"


@dataclass
class Exercise(Theorem):
    """
    The class for storing exercises' info.
    On top of the parent class, the attributes stores
    - the lists of buttons that will be available for this specific exercise
        (in each three categories, resp. logic, proof and magic buttons)
    - the list of statements that will be available for this specific exercise.
    """

    settings:                   dict            = None
    available_logic:            List[Action]    = None
    available_magic:            List[Action]    = None
    available_proof:            List[Action]    = None
    available_compute:          List[Action]    = None
    available_statements:       List[Statement] = None
    # FIXME: not used:
    expected_vars_number:       Dict[str, int]  = None  # e.g. {'X': 3, 'A': 1}
    info:                       Dict[str, Any]  = None
    # This is True if the negation of the statement must be proved:
    negate_statement:           bool            = False
    # If self is in a history file, then this points to the original exercise
    # in the original course file:
    original_exercise                           = None

    # NB: settings are treated in self.update_cvars_from_metadata()
    non_pertinent_course_metadata = ('_raw_metadata', 'description',
                                     'description_intro',
                                     'pretty_name', 'settings')

    __launch_in_history_mode = None
    # def __init__(self, **data: dict):
    #     print('init exo')
    #     for (key, value) in data.items():
    #         print(str(key))
    #         self.key = value

    @property
    def display(self):
        return self.info.get('display')

    @property
    def initial_proof_state(self):
        if self.original_exercise:
            return self.original_exercise.initial_proof_state
        else:
            return self._initial_proof_state

    @initial_proof_state.setter
    def initial_proof_state(self, ips):
        self._initial_proof_state = ips

    @property
    def raw_metadata(self) -> Dict[str, str]:
        """
        This is the metadata dictionary reflecting the individual metadata of
        self in the Lean course file.
        """

        if self._raw_metadata is None:
            self._raw_metadata = dict()
        # if self.negate_statement:
        #     self._raw_metadata['negate_statement'] = '  True'
            # lines += ['NegateStatement', '  True']
        # return '\n'.join(lines)
        return self._raw_metadata

    @raw_metadata.setter
    def raw_metadata(self, metadata):
        self._raw_metadata = metadata

    @property
    def launch_in_history_mode(self):
        """
        If True, self should be launched in history mode,
        with refined_auto_steps executed automatically.
        """
        if self.__launch_in_history_mode is not None:
            return self.__launch_in_history_mode
        else:
            return bool(self.refined_auto_steps)

    @launch_in_history_mode.setter
    def launch_in_history_mode(self, yes):
        self.__launch_in_history_mode = yes

    @property
    def structured_content(self) -> StructuredContent:
        """
        This data string structure contains the different parts of self's
        statement in Lean code.
        """
        first_line_nb = self.lean_line
        last_line_nb = self.lean_end_line_number
        name = self.lean_short_name
        hypo = self.lean_variables
        conclusion = self.lean_core_statement
        raw_metadata = self.raw_metadata
        code = "todo\n"
        file_content = self.course.file_content

        return StructuredContent(first_line_nb, last_line_nb,
                                 name, hypo, conclusion, raw_metadata,
                                 code, file_content)

    @property
    def exercise_number(self) -> int:
        exercises = [statement for statement in self.course.statements
                     if isinstance(statement, Exercise)]
        return exercises.index(self)

    @property
    def definitions(self):
        definitions = [st for st in self.available_statements
                       if isinstance(st, Definition)]
        return definitions

    @property
    def definitions_for_implicit_use(self):
        definitions = [defi for defi in self.definitions if defi.implicit_use]
        return definitions

    @classmethod
    def from_parser_data(cls, data: dict, statements: list):
        """
        Create an Exercise from the raw data obtained by the parser.
        The main task is to determine
        - the list of available_statements,
        - the list of available actions (corresponding to buttons of the UI)
        from the metadata. Both lists are computed in roughly the same way.

        Note that the data dictionary is modified by this method.

        :param statements:  list of all Statement instances until the current
                            exercise, from which the available_statements
                            list will be extracted
        :param data:        a dictionary whose keys are fields parsed by the
                            Course.from_file method.
        """

        ########################
        # expected_vars_number #
        # This is not used     #
        ########################
        # expected_vars_number = {}
        # if "expected_vars_number" in data.keys():
        #     try:
        #         for equality in data["expected_vars_number"].split(", "):
        #             key, _, value = equality.partition("=")
        #             key = key.strip()
        #             expected_vars_number[key] = int(value)
        #     # In case int(value) has no meaning:
        #     except AttributeError:
        #         log.error(f"wrong format for ExpectedVarsNumber in exercise "
        #                   f"{data['lean_name']}")
        #     except ValueError:
        #         log.error(f"wrong format for ExpectedVarsNumber in exercise "
        #                   f"{data['lean_name']}")
        # Replace data with formatted data
        # data['expected_vars_number'] = expected_vars_number

        ###########################
        # Treatment of statements #
        ###########################
        data['available_statements'] = extract_available_statements(data,
                                                                    statements)
        # names = [st.pretty_name for st in data['available_statements']]
        # log.debug(f"Available statements: {names}")

        ########################
        # Treatment of buttons #
        ########################
        # The following modifies directly the data dict,
        # i.e. substitutes the data field content corresponding to
        # keys AvailableLogic, ...
        # by the relevant list of Action buttons.
        extract_available_buttons(data)

        ######################################################################
        # Extract the data corresponding to attributes of the Exercise class #
        ######################################################################
        # To keep only the relevant data, the keys that appear as attributes
        # in the class Exercise or in the parent class Statement:
        # this removes the entry in 'data' corresponding to course_metadata
        extract_data = {}
        for attributes in [Statement.attributes(), cls.attributes()]:
            for attribute in attributes:
                if attribute in data.keys():
                    extract_data[attribute] = data.pop(attribute)
        # Keep only the relevant data, i.e. the keys which corresponds to
        # attribute of the class. The remaining information are put in the
        # info dictionary attribute
        for field_name in data:  # replace string by bool if needed
            if data[field_name] == 'True':
                data[field_name] = True
            elif data[field_name] == 'False':
                data[field_name] = False

        extract_data["info"] = data

        polish_data(extract_data)

        # log.debug(f"available_logic: {extract_data['available_logic']}")
        # log.debug(f"available_proof: {extract_data['available_proof']}")
        # log.debug(f"available_statements: "
        #           f"{len(extract_data['available_statements'])}")
        # log.debug(f"Creating exercise with supplementary info"
        #          f" {extract_data['info']}")
        # log.debug(f"Creating exercise, line: {extract_data['lean_line']}")

        #########################################
        # Finally construct the Exercise object #
        #########################################
        exercise = cls(**extract_data)
        return exercise

    def from_history_exercise(self):
        # Copy original exercise to avoid altering attributes
        exercise = copy(self.original_exercise)
        exercise.auto_test = self.auto_test
        exercise.negate_statement = self.negate_statement
        # print("History ex metadata:")
        # print(self.metadata)
        # print(self.settings)
        exercise.info = self.info
        exercise.settings = self.settings
        # print("Copied:")
        # print(exercise.metadata)
        # print(exercise.settings)
        return exercise

    def update_cvars_from_metadata(self) -> dict:
        """
        Update cvars with entries in metadata['settings'], and return a
        (recursive) dictionary with the keys that have been replaced,
        and their previous values.
        """

        # raw_course_settings: str = self.course.metadata.get('settings')
        # more_vars: dict = vars_from_metadata(raw_course_settings)
        # raw_exercise_settings: str = self.raw_metadata.get('settings')
        # exercise_settings: dict = vars_from_metadata(raw_exercise_settings)
        # more_vars.update(exercise_settings)

        more_vars = self.course.metadata.get('settings')
        # print(f"Exercise {self.pretty_name} setting:")
        # print(f"Date: {self.history_date()}")
        if more_vars is None:
            more_vars = dict()
        if self.settings:
            more_vars.update(self.settings)
        # print(more_vars)

        if more_vars:
            # old_vars = {key: cvars.get(key)
            #             for key in more_vars
            #             if key in more_vars.keys()
            #             and (cvars.get(key) != more_vars[key])}
            old_vars = cvars.recursive_update(more_vars)
            # for (key, value) in old_vars.items():
            #     print(f"key {key} updated from {value} to:")
            #     print(more_vars.get(key))
            #     print(f"cvars key:")
            #     print(cvars.get(key))
            #     print(cvars.get(key) == more_vars.get(key))
            return old_vars
        else:
            return dict()

    def check_prove_exists_joker(self):
        """
        Remove the prove_exists_joker button, unless
        usr_jokers_available = true.
        """
        if not cvars.get('logic.usr_jokers_available', False):
            new_logic = [action for action in self.available_logic
                         if action.name != 'prove_exists_joker']
            # assert len(new_logic) == len(self.available_logic) - 1
            self.available_logic = new_logic


    @property
    def is_open_question(self):
        return self.info.get('open_question', False)

    @property
    def is_complete_statement(self):
        return self.info.get('complete_statement', False)

    @property
    def user_proves_statement(self):
        return self.info.get('user_proves_statement', False)

    def statements_for_prover(self) -> [str]:
        """
        Return a list of statements names to be used for automatic proving.
        This is used to check statements with jokers, to be completed by usr.
        """
        statements = self.info.get('statements_for_prover', "")
        statements = statements.split()
        return statements

    def current_name_space(self):
        current_name_space, _, end = self.lean_name.partition(".exercise.")
        return current_name_space

    def all_statements_until(self, statements: List[str]) -> List[str]:
        """
        provide the list of all statements in outline until the namespace
        containing self
        :param outline: outline of the course, as described in the Course class
        TODO: turn this into a @property to be accessed by
        exercise.all_statements_until
        """
        name = self.lean_name
        index = statements.index(name)
        return statements[:index]

    def next_exercise(self):
        """
        Return next Exercise in the statements list of self.Course, or None
        if self is the last exercise in the list.
        """

        statements = self.course.statements
        index = statements.index(self)
        for statement in statements[index+1:]:
            if isinstance(statement, Exercise):
                return statement
        return None

    def is_last(self) -> bool:
        """
        Check if self is the last exercise in the statements list of
        self.Course.
        """
        return self.next_exercise() is None

    @property
    def available_logic_1(self):
        """
        List of actions in self.available_logic whose name are in
        logic_buttons_line_1. The order is that of logic_buttons_line_1.
        """
        # action_names = ["and", "or", "not", "implies", "iff"]
        action_names = logic_buttons_line_1
        actions = []
        for name in action_names:
            for action in self.available_logic:
                if action.name in (name, 'prove_' + name, 'use_' + name):
                    actions.append(action)
        return actions

    @property
    def available_logic_prove(self):
        """
        return the list of demo actions whose names are names of actions in
        self.available_logic, and whose name startswith 'prove".
        """

        names = [action.name for action in self.available_logic_1]
        actions = []
        for action in LOGIC_BUTTONS.values():
            name = action.name
            if name.startswith('prove_'):
                if name in names or name[6:] in names:
                    actions += [action]
        return actions

    @property
    def available_logic_use(self):
        """
        return the list of demo actions whose names are names of actions in
        self.available_logic.
        """
        names = [action.name for action in self.available_logic_1]
        actions = []
        for action in LOGIC_BUTTONS.values():
            name = action.name
            if name.startswith('use_'):
                if name in names or name[4:] in names:
                    actions += [action]
        return actions

    @property
    def available_logic_2(self):
        # action_names = ["forall", "exists", "equal", "map"]
        """
        List of actions in self.available_logic whose name are in
        logic_buttons_line_2. The order is that of logic_buttons_line_2.
        """
        # action_names = ["and", "or", "not", "implies", "iff"]
        action_names = logic_buttons_line_2
        actions = []
        for name in action_names:
            for action in self.available_logic:
                if action.name == name:
                    actions.append(action)
        return actions

    @property
    def begin_metadata_line(self):
        return self.info.get('begin_metadata_line')

    @staticmethod
    def analysis_code2(seq_num=0) -> str:
        code = f"    targets_analysis2 {seq_num},\n" \
               f"    all_goals {{hypo_analysis2 {seq_num}}},\n"
        return code

    def __begin_end_code(self, seq_num, code_lines: str) -> str:
        """
        Return a Lean code string containint code_lines in a begin/end block,
        including hypo/targets analyses.
        """
        code_string = code_lines.strip()
        if not code_string.endswith(","):
            code_string += ","

        if not code_string.endswith("\n"):
            code_string += "\n"

        tabulation = "  "
        code_lines = tabulation + code_lines
        code_lines = code_lines.replace("\n", "\n" + tabulation)
        analysis = self.analysis_code2(seq_num) if seq_num is not None else ""

        code = "begin\n" \
               + code_lines \
               + analysis \
               + "end\n"
        return code

    def file_contents_from_goal(self, goal=None, seq_num=None,
                                code_lines="todo\n",
                                additional_metadata=None):
        """
        Set the file content from goal and code. e.g.
        import ...
        namespace ...
        open ...
        lemma <exercise_name> <Lean content, e.g. (X: Type) : true> :=
        <additional metadata>
        begin
            <some code>
        end
        """

        if goal is None:
            if self.initial_proof_state:
                goal = self.initial_proof_state.goals[0]
            else:
                log.warning("Unable to get file_contents_from_goal")
                return

        seq_num_line = f"-- Seq num {seq_num}\n" if seq_num is not None else ""

        # Metadata, e.g. AutoSteps
        if additional_metadata:
            metadata_lines = [key + '\n' + additional_metadata[key]
                              for key in additional_metadata]
            metadata_lines = '\n'.join(metadata_lines)
            metadata_lines = '/- dEAduction\n' + metadata_lines + '\n-/\n'
        else:
            metadata_lines = ""

        title = self.lean_name

        file_content = seq_num_line \
            + self.course.lean_import_course_preamble() \
            + LEAN_CLASSICAL_LOGIC \
            + "section course\n" \
            + self.open_namespace_str() \
            + self.open_read_only_namespace_str() \
            + goal.to_lean_statement(title) \
            + metadata_lines \
            + self.__begin_end_code(seq_num, code_lines) \
            + self.close_namespace_str() \
            + "end course\n"
        return file_content

    def lean_file_afterword(self, seq_num=0) -> str:
        # Construct short end of file by closing all open namespaces
        end_of_file = "end\n"
        end_of_file += self.close_namespace_str()
        end_of_file += "end course"
        lean_file_afterword = self.analysis_code2(seq_num) + end_of_file
        return lean_file_afterword

    #######################################
    # Managing versions from history file #
    #######################################
    def __new_file_content(self, lean_code="todo ",
                           additional_metadata=None,
                           history_nb=1) -> str:
        """
        Insert additional metadata (e.g. AutoSteps) and code_lines
        into self.course.file_content.
        """

        struct_content = self.structured_content
        new_st_content = StructuredContent.new_content(struct_content,
                                                       additional_metadata,
                                                       lean_code, history_nb)
        new_file_content = new_st_content.content_with_lemma()
        return new_file_content

    def history_date(self):
        """
        Return the date when this exercise was saved.
        Pertinent only if self is from the history file.
        """

        # prefix = StructuredContent.history_name_prefix  # --> "exercise.history_"
        # if self.lean_name.find(prefix) == -1:
        #     return
        # end_name = self.lean_name.split(prefix)[1]  # --> _<date>_<short_name>
        # date = end_name.split('_')[0]
        # print(f"date: {date}")
        date = self.info.get('history_date')
        return date

    # def is_from_history_file(self):
    #     """
    #     True if self is an exercise as saved in history file.
    #     """
    #     tests = [self.course.is_history_file(),
    #              self.history_date(),
    #              self.auto_test]
    #     return all(tests)

    def is_solved_in_auto_test(self):
        # txt = self.refined_auto_steps[-1].success_msg
        # solved_txts = [text.proof_complete, _(text.proof_complete)]
        # # solved_txts = [txt.replace(' ', '_') for txt in solved_txts]
        # # print(solved_txts)
        # test = any(txt.find(solved_txt) != -1
        #            for solved_txt in solved_txts)
        test = self.raw_metadata.get('all_goals_solved', False)
        return test

    def versions_saved_in_history_course(self) -> []:
        """
        Return the versions of self as saved in self.history_course().
        """
        return self.course.history_versions_from_exercise(self)

    def nb_versions_saved_in_history_course(self) -> int:
        return len(self.versions_saved_in_history_course())

    def has_versions_in_history_course(self):
        """
        True if at least one saved version of self in history_course.
        """
        return self.nb_versions_saved_in_history_course() > 0

    def is_solved_in_history_course(self):
        """
        True if at least one version as saved in history_course has a
        complete proof.
        """
        return any([exo.is_solved_in_auto_test()
                    for exo in self.versions_saved_in_history_course()])

    def is_copy_of(self, other) -> bool:
        """
        This is true if self is a copy of other (in a distinct file).
        Name and core content are tested.
        """
        if not isinstance(other, Exercise):
            return False
        tests = [self.structured_content.has_identical_core_lemma_content(
                 other.structured_content),
                 self.lean_name == other.lean_name]
        return all(tests)

    def is_history_version_of(self, other):
        """
        True if self is a history version of other. Name and core content are
        tested.
        """
        tests = [self.history_date(), self.auto_test,
                 self.structured_content.has_identical_core_lemma_content(
                 other.structured_content),
                 self.lean_name.startswith(other.lean_name + '_')]
        return all(tests)

    def save_with_auto_steps(self, additional_metadata, lean_code):
        """
        Save current exercise with auto_steps in self.course's history file.
        If the history file does not exist, create it with initial content
        identical to self.course.file_content.
        The exercise is saved just after the original exercise in the history
        file.
        """

        path = self.course.abs_history_file_path

        # (1) Take history file into account, if any
        if self.course.history_course():
            exercise = self.course.original_version_in_history_file(self)
            if not exercise:
                exercise = self
        else:
            exercise = self

        # # (2) Negate statement?
        # if self.negate_statement:
        #     exercise.negate_statement = True

        # (3) Compute new content
        history_nb = len(self.versions_saved_in_history_course()) + 1
        content = exercise.__new_file_content(lean_code, additional_metadata,
                                              history_nb)

        # (4) Save!
        with open(path, mode='wt', encoding='utf-8') as output:
            output.write(content)

        # (5) Reload history_course to get new entry
        self.course.set_history_course()

    def delete_in_history_file(self):
        """
        Assuming self comes from a history file, delete the corresponding
        entry. Beware that self is saved exercise, not original one.
        """
        path = self.course.relative_course_path.resolve()

        first_line_nb = self.structured_content.first_line_nb
        last_line_nb = self.structured_content.last_line_nb

        content: str = self.course.file_content
        content_lines = content.splitlines()
        new_content_lines = (content_lines[:first_line_nb-1] +
                             content_lines[last_line_nb:])
        new_content = '\n'.join(new_content_lines)

        # Save new content!
        with open(path, mode='wt', encoding='utf-8') as output:
            output.write(new_content)

        # Reload history_course to remove deleted entry
        # self.original_exercise.course.set_history_course()

    def history_number(self) -> int:
        """
        Return the number at the end of self's name, which may serve as a
        history number. If no such number, return -1.

        E.g. "exercise.complete_lemme_de_gauss_12" --> 12
        """
        name = self.lean_name
        suffix = name.split('_')[-1]
        try:
            nb = int(suffix)
        except ValueError:
            nb = -1

        return nb


#############
# utilities #
#############
def extract_available_statements(data: dict, statements: list):
    """
    Extract from the statements list the sublist specified by the data dict.

    :param data:        dict whose pertinent keys are
                available_statements,
                available_definitions,
                available_theorems,
                available_exercises
                        and values are either 'NONE', 'UNTIL_NOW',
                        a macro defined in the Lean file,
                        with modifications using "+" or "-",
                        or a (string) list of statement names
    e.g.
    $UNTIL_NOW -union_quelconque_ensembles -intersection_quelconque_ensembles

    :param statements:  list of Statements
    :return:
    """
    # Default value = '$UNTIL_NOW'
    # Other pre-defined value = 'NONE'
    # Other possibility = macro defined in the Lean file
    unsorted_statements = []
    for statement_type in ['definition',
                           'theorem',
                           'exercise',
                           'statement'
                           ]:
        field_name = 'available_' + statement_type + 's'
        if 'available_statements' in data:
            if data['available_statements'].endswith("NONE"):
                # If data['available_statements'].endswith("NONE")
                # then default value is '$NONE'
                data.setdefault(field_name, "$NONE")
        elif (statement_type == 'statement'
              and 'available_statements' not in data.keys()
        ):
            continue  # DO NOT add all statements!
        # if not NONE then default value = UNTIL_NOW
        data.setdefault(field_name, "$UNTIL_NOW")
        # Now field_name is in data
        if data[field_name].endswith("NONE"):
            continue  # No statement of type statement_type

        # (Step 1) Substitute macros in string
        string = substitute_macros(data[field_name], data)
        # this is still a string containing
        # (a) macro names that should either be '$ALL'
        # or in data.keys() with values in Statements, and
        # (b) usual names describing statements.

        statement_callable = make_statement_callable(statement_type,
                                                     statements)
        # This is the function that computes Statements from names
        # We can now compute the available_actions:

        # (Step 2) Replace every word in string by the corresponding
        # statement or list of statements
        more_statements = extract_list(string, data, statement_callable)
        unsorted_statements.extend(more_statements)

    # Finally sort unsorted_statements in the order given by statements:
    # this is not optimised!!
    available_statements = []
    for item in statements:
        if item in unsorted_statements:
            available_statements.append(item)
    return available_statements


def extract_available_buttons(data: dict):
    """
    Extract from the LOGIC_BUTTONS, PROOF_BUTTONS, MAGIC_BUTTONS lists
    the buttons specified in data.

    :param data: dict with pertinent info corresponding to keys
    data['available_logic'],
    data['available_proof'],
    data['available_magic'].
    data['available_compute'].

    :return: no direct return, but modify the data dict.
    """
    for action_type in ['logic', 'proof', 'magic', 'compute']:
        field_name = 'available_' + action_type
        default_field_name = 'default_' + field_name
        if field_name not in data.keys():
            if default_field_name in data.keys():  # Take default list
                data[field_name] = data[default_field_name]
            else:  # Take all buttons
                data[field_name] = '$ALL'  # not optimal

        # log.debug(f"Processing data in {field_name}, {data[field_name]}")

        string = substitute_macros(data[field_name], data)
        # This is still a string with macro names that should either
        # be '$ALL' or in data.keys() with values in Action
        action_callable = make_action_from_name(action_type)
        # This is the function that computes Actions from names.
        # We can now compute the available_actions:
        data[field_name] = extract_list(string, data, action_callable)


def make_action_from_name(prefix) -> callable:
    """
    Construct the function corresponding to prefix
    :param prefix: one of logic, proof, magic
    :return: a callable
    """
    if prefix == 'logic':
        dictionary = LOGIC_BUTTONS
    elif prefix == 'proof':
        dictionary = PROOF_BUTTONS
    elif prefix == 'magic':
        dictionary = MAGIC_BUTTONS
    elif prefix == 'compute':
        dictionary = COMPUTE_BUTTONS

    def action_from_name(name: str) -> [Action]:
        """
        Return list of actions corresponding to name, and to prefix
        ('logic', 'proof', 'magic'). name can also be $ALL, $NONE.
        e.g. 'and' -> [ LOGIC_BUTTONS['action_and'] ]
        '$ALL' -> LOGIC_BUTTONS
        Does not include prove and use versions of actions.
        """
        # log.debug(f"searching Action {name}")
        if name in ['NONE', '$NONE']:
            return []
        if name in ['ALL', '$ALL']:
            return [action for action in dictionary.values()
                    if not action.name.endswith('prove') and not
                    action.name.endswith('use')]
        if not name.startswith("action_"):
            name = "action_" + name
        action = [dictionary[name]] if name in dictionary else None
        return action

    return action_from_name


def make_statement_callable(prefix: str, statements) -> callable:
    """
    Construct the function corresponding to prefix
    :param prefix:      one of 'statement', 'definition', 'theorem', 'exercise'
    :param statements:  list of instances of the Statement class
    :return:            a callable
    """
    classes = {'statement': Statement,
               'definition': Definition,
               'theorem': Theorem,
               'exercise': Exercise}
    class_ = classes[prefix]

    def statement_callable(name: str) -> [Statement]:
        """
        Return Statement corresponding to name and prefix

        e.g. "union_quelconque" (prefix = "definition)
        ->  Statement whose name endswith definition.union_quelconque
        """
        # log.debug(f"searching {prefix} {name}")
        if name in ['NONE', '$NONE']:
            return []
        if name in ['$UNTIL_NOW', 'UNTIL_NOW']:
            available_statements = []
            for statement in statements:
                if class_ == Theorem:
                    if (isinstance(statement, Theorem)
                            and not isinstance(statement, Exercise)):
                        available_statements.append(statement)
                        # log.debug(f"Considering {statement.pretty_name}...")
                elif isinstance(statement, class_):
                    available_statements.append(statement)
                    # log.debug(f"Considering {statement.pretty_name}...")
            return available_statements

        statement = None
        name = prefix + '.' + name
        index, nb = find_suffix(name, [item.lean_name for item in statements])
        if nb > 0:
            statement = [statements[index]]
        return statement

    return statement_callable


def polish_data(data):
    """
    Make some formal smoothing. Beware that capitalization modifies math
    notations!
    """
    if 'description' in data:
        # data['description'] = data['description'].capitalize()
        if data['description'][-1].isalpha():
            data['description'] += '.'


def indent(text: str) -> str:
    """
    Indent each line by 2 spaces.
    """
    lines = text.splitlines()
    new_lines = [line if line.startswith('  ')
                 else ' ' + line if line.startswith(' ')
                 else '  ' + line
                 for line in lines]
    new_text = '\n'.join(new_lines)
    return new_text


def comment(text: str) -> str:
    """
    Comment each line by adding '# ".
    """
    lines = text.splitlines()
    new_lines = [line if line.strip().startswith('--')
                 else '-- ' + line for line in lines]
    new_text = '\n'.join(new_lines)

    new_text += '\n  todo'
    return new_text


def metadata_to_str(metadata: Dict[str, str]):
    """
    Format metadata dict for Lean files. Indent values if needed.
    """
    if not metadata:
        return ""

    metadata_str = ''
    for key in metadata:
        keys = key.split('_')
        keys = [key.capitalize() if not key[0].isupper() else key
                for key in keys]
        capitalised_key = ''.join(keys)
        # if not key[0].isupper():
        #     key = key.capitalize()
        metadata_str += capitalised_key + '\n'
        value = str(metadata[key])
        metadata_str += indent(value) + '\n'

    return metadata_str


def metadata_to_toml(metadata: dict) -> str:
    """
    Return metadata dict in toml format.
    This mainly makes use of tomli_w.dumps(), with the followinf modifications:
    - selection, which is a list of lists, is put on one line
    - inside the settings dict, quotation marks are removed around keys
    e.g.
    "functionality.default_functionality_level" = "Free settings"
    --> functionality.default_functionality_level = "Free settings"
    """
    if not metadata:
        return ""
    # print(metadata)
    toml = tomli_w.dumps(metadata)

    # Compact selection data

    lines = toml.split('\n')
    # print("LINES2")
    # print(lines)
    # Remove blank lines and join selection
    stripped_lines = []
    complete_selection = ''
    inside_settings = False
    for line in lines:
        # Beginning of selection:
        if line == 'selection = [':
            complete_selection = line
        elif complete_selection:
            if line == ']' and complete_selection.endswith(','):
                complete_selection = complete_selection[:-1]
            if line != ', ':
                line = line.strip()
                complete_selection += ' ' + line
        elif line:
            if inside_settings:  # Remove quotes from keys
                key_value = line.split(' = ')
                if len(key_value) == 2:
                    [key, value] = key_value
                    if key.startswith('"') and key.endswith('"'):
                        key = key[1:-1]
                        print(f"Old toml line: {line}")
                        line = key + ' = ' + value
                        print(f"New toml line: {line}")
            # ### Add new line: ###
            stripped_lines.append(line)

        # End of selection:
        if complete_selection and line == ']':
            stripped_lines.append(complete_selection)
            complete_selection = ''

        # beginning and end of settings:
        if line == "[settings]":
            inside_settings = True
        elif line.startswith('[') and line.endswith(']'):
            inside_settings = False

    # print("LINES3")
    # print(stripped_lines)
    toml = '\n'.join(stripped_lines)

    return toml


if __name__ == "__main__":
    print(LOGIC_BUTTONS)
    print(PROOF_BUTTONS)
    print(LOGIC_BUTTONS.keys())
    print(PROOF_BUTTONS.keys())