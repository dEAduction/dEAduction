"""
###########################################################
# proof_state.py : provides the class ProofState and Goal #
###########################################################

The goal and proof_state classes are designed to reflect Lean's goals and
proof states. A goal is essentially made of a context and a target. The
context is a list of MathObjects, and the target is a MathObject.

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
import logging
from typing import List, Tuple, Any, Optional
from copy import copy

import deaduction.pylib.logger as logger
from deaduction.pylib.config.i18n import _

from .MathObject import MathObject
from .lean_analysis import ( lean_expr_with_type_grammar,
                             LeanEntryVisitor )
# from deaduction.pylib.coursedata import AutoStep
import deaduction.pylib.config.vars as cvars

log = logging.getLogger(__name__)


##################
# The Goal class #
##################
@dataclass
class Goal:
    """
    A goal is made of a context and a target, and reflects Lean's goal.
    The future_tags attribute is used to store the result of the comparison
    with the previous goal during a proof; it essentially tags each object of
    the context as new, modified or unchanged.

    Note that the order in the context is important, since it will be
    displayed as such in the UI. We do not keep Lean's order, which put
    modified objects at the end: for a better user experience we rather try to
    keep the order of the previous step. More precisely,
    - instantiation from_lean_data keeps Lean's order,
    - application of the compare(self, previous_goal) method modify the
    order so that unchanged and modified objects are kept in the order they
    had in the previous_goal, and new objects are kept at the end.

    The class provides methods for
    - comparing goals,
    - splitting goals into objects and properties,
    - printing goals.
    """
    context:        [MathObject]
    target:         MathObject
    future_tags:    [] = None

    @classmethod
    def from_lean_data(cls, hypo_analysis: str, target_analysis: str):
        """
        Construct a goal Python object from Lean's data, i.e. the two
        strings resulting from the tactics hypo_analysis and targets_analysis.

        :param hypo_analysis:   string from the lean tactic hypo_analysis
        :param target_analysis: first string from the lean tactic
                                targets_analysis (only the main target)

        :return: a goal
        """

        log.info("creating new Goal from lean strings")
        # log.debug(hypo_analysis)
        # log.debug(target_analysis)
        lines = hypo_analysis.split("¿¿¿")
        # Put back "¿¿¿" and remove '\n', getting rid of the title line
        # ("context:")
        lines = ['¿¿¿' + item.replace('\n', '') for item in lines[1:]]
        context = []
        for math_obj_string in lines:
            if math_obj_string.startswith("context:"):
                continue
            else:
                # Applying the parser
                tree = lean_expr_with_type_grammar.parse(math_obj_string)
                math_object = LeanEntryVisitor().visit(tree)
                context.append(math_object)

        tree = lean_expr_with_type_grammar.parse(target_analysis)
        target = LeanEntryVisitor().visit(tree)
        return cls(context, target)

    def math_object_from_name(self, name: str) -> MathObject:
        """
        Return the MathObject whose name is name.
        """
        if name == "target":
            return self.target
        else:
            math_objects = [math_object for math_object in self.context if
                            math_object.has_name(name)]
            if math_objects:
                return math_objects[0]

    def compare(self, old_goal):
        """
        Compare the new goal to the old one, and tag the target and the
        elements of the new context accordingly. tag is one of the following:
        "+" means present in the new goal, absent in the old goal
        "=" means present in both and identical
        "≠" means present in both and different

        In the tests, two math_objects are equal if they have the same name
        and the same math_type, and they are modified versions of each other if
        they have the same name and different math_types.

        Note that this method relies heavily on __eq__ MathObject's method,
        which is redefined in the corresponding file as a rather strict
        notion of equality.

        :param self:        new goal
        :param old_goal:    old goal

        :return: no direct return, but
            - the context is permuted (see the Goal class documentation)
            - the future_tags attribute are set, as a list of tags,
            each element being the tag of the corresponding element in the
            context list.
        """

        new_goal = self
        new_context = new_goal.context.copy()
        old_context = old_goal.context.copy()
        # Permuted_new_context will contain the new_context in the order
        # reflecting that of the old_context
        # Each new item that is found in the old_context will be affected at
        # its old index, items that are new will be appended, and then
        # None objects (corresponding to object that have disappeared) will be
        # removed from the list
        permuted_new_context = [None] * len(old_context)
        permuted_new_tags    = [None] * len(old_context)

        log.info("Comparing and tagging old goal and new goal")
        # log.debug(old_context)
        # log.debug(new_context)
        old_names = [math_object_old.info["name"]
                     for math_object_old in old_context]
        new_index = 0
        for math_object in new_context:
            name = math_object.info["name"]

            # (1) Search old_context for an object with the same name
            try:
                old_index = old_names.index(name)
            except ValueError:
                # (2) If no such object then object is new
                old_index = None
                # New objects at the end
                permuted_new_context.append(math_object)
                permuted_new_tags.append("+")
            else:
                # Put new object at old index, and check for modifications
                permuted_new_context[old_index] = math_object
                old_math_type = old_context[old_index].math_type
                new_math_type = math_object.math_type
                # (3) Check if the object has the same type
                if old_math_type == new_math_type:
                    permuted_new_tags[old_index] = "="
                else:  # (4) If not, object has been modified
                    permuted_new_tags[old_index] = "≠"

            if old_index is not None:
                # Will not be considered anymore:
                old_names[old_index]   = None
                old_context[old_index] = None
            new_index += 1

        # (5) Remove 'None' entries
        clean_permuted_new_context = [item for item in permuted_new_context
                                      if item is not None]
        clean_permuted_new_tags    = [item for item in permuted_new_tags
                                      if item is not None]

        # Finally modify order and set tags
        self.context     = clean_permuted_new_context
        self.future_tags = clean_permuted_new_tags

    def tag_and_split_propositions_objects(self) -> ([MathObject, str],
                                                     [MathObject, str]):
        """
        Split the context into
            - a list of tagged objects,
            - a list of tagged propositions
        A tag object is a couple (object, tag), where tag is one of
        "=", "≠", "+"

        Lean, based on type theory, makes no difference between
        mathematical "objects" (e.g. a set, an element of the set,
        a function, ...) and mathematical "propositions" (logical assertions
        concerning the objects). But mathematicians do, and the UI display
        objects and propositions separately.

        :return:
        - a list of tuples (po, tag), where po is an object in the context
        and tag is the tag of po
        - a list of tuples (po, tag), where po is a proposition in the context
        and tag is the tag of po
        """

        log.info("split objects and propositions of the context")
        context = self.context
        if not self.future_tags:
            self.future_tags = ["="] * len(context)
        objects = []
        propositions = []
        for (math_object, tag) in zip(context, self.future_tags):
            if math_object.math_type.is_prop():
                propositions.append((math_object, tag))
            else:
                objects.append((math_object, tag))
        return objects, propositions

    def goal_to_text(self,
                     format_="utf8",
                     to_prove=True,
                     text_depth=1,
                     open_problem=False) -> str:
        """
        Compute a readable version of the goal as the statement of an
        exercise.

        :param format_:     parameter of MathObject.to_display method
        :param to_prove:    boolean.
            If True, the goal will be formulated as "Prove that..."
            If False, the goal will be formulated as "Then..." (useful if
            the goal comes from a Theorem or Definition)
        :param text_depth:  int
            A higher value entail a more verbose formulation (more symbols will
            be replaced by words).
        :param open_problem: if True, then display as "True or False?"

        :return: a text version of the goal
        """

        # fixme: depth>1 does not really work
        context = self.context
        target = self.target
        text = ""
        for math_object in context:
            math_type = math_object.math_type
            if math_type.is_prop():
                prop = math_object.math_type.to_display(text_depth=text_depth,
                                                        format_=format_,
                                                        is_math_type=True)
                new_sentence = _("Assume that") + " " + prop + "."
            else:
                name = math_object.to_display()
                name_type = math_type.to_display(is_math_type=True,
                                                 format_=format_,
                                                 text_depth=text_depth)
                if math_type.node == "FUNCTION" and text_depth == 0:
                    new_sentence = _("Let") + " " + name + ":" \
                                   + " " + name_type + "."
                else:
                    if cvars.get('i18n.select_language') == 'fr_FR':
                        # indispensable pour la gestion des espacements
                        # (le "be" anglais n'a pas d'équivalent en Français)
                        new_sentence = "Soit" + " " + name + " " \
                                       + name_type + "."
                    else:
                        new_sentence = _("Let") + " " + name + " " + _("be") \
                                   + " " + name_type + "."

            if text:
                text += "\n"
            text += new_sentence

        if text:
            text += "\n"
        target_text = target.math_type.to_display(text_depth=text_depth,
                                                  format_="utf8",
                                                  is_math_type=True)
        if to_prove and not open_problem:
            target_text = _("Prove that") + " " + target_text
        elif text:
                target_text = _("Then") + " " + target_text
        else:
            target_text = target_text.capitalize()
            # Little issue: if sentence starts with a lower case
            # variable. This should never happen though...
        if open_problem:
            text = _("True or False?") + "\n" + text

        text += target_text + "."
        return text

    def print_goal(self, open_problem=False, to_prove=True) -> str:
        """
        Return context and target in a raw form.
        """
        context = self.context
        target = self.target
        text = ""
        if open_problem:
            text += _("True or False?") + "\n"
        if len(context) == 1:
            text += _("Hypothesis:") + "\n"
        elif len(context) > 1:
            text += _("Hypotheses:") + "\n"
        for math_object in context:
            math_type = math_object.math_type
            name = math_object.to_display()
            name_type = math_type.to_display(is_math_type=True)
            text_object = name + _(": ") + name_type
            text += "  " + text_object + "\n"
        if to_prove and not open_problem:
            text += _("Prove that") + "\n"
        elif context:
            text += _("Then") + "\n"
        text += target.math_type.to_display(is_math_type=True)
        return text

    def extract_vars(self) -> List[MathObject]:
        """
        Provides the list of all variables in the context,
        (but NOT bound variables, nor names of hypotheses)

        :return: list of MathObject (variables names)
        """
        variables = [math_object for math_object in self.context
                     if not math_object.is_prop()]
        return variables

    def extract_vars_names(self) -> List[str]:
        """
        provides the list of names of all variables in the context,
        (but NOT bound variables, nor names of hypotheses)
        :return: list of MathObject (variables names)
        """
        names = [math_object.info['name'] for math_object in
                 self.extract_vars()]
        return names


########################
# The ProofState class #
########################
@dataclass
class ProofState:
    """
    This class reflects Lean's proofstates, and is essentially made of a
    list of goals. The lean_data attributes stores the strings from
    hypo_analysis and targets_analysis from which the ProofState has been
    built.
    This class has a single method, a class method used for building
    ProofStates from the Lean data.

    Note that only the first goal has a non empty context, since
    hypo_analysis only provide context of the main goal.
    """
    goals: List[Goal]
    lean_data: Tuple[str, str] = None

    @classmethod
    def from_lean_data(cls, hypo_analysis: str, targets_analysis: str):
        """
        :param hypo_analysis:    string from the lean tactic hypo_analysis
        :param targets_analysis: string from the lean tactic targets_analysis
        (with one line per target)

        :return: a ProofState
        """

        log.info("Creating new ProofState from lean strings")
        targets = targets_analysis.split("¿¿¿")
        # Put back "¿¿¿" and remove '\n' :
        targets = ['¿¿¿' + item.replace('\n', '') for item in targets]
        targets.pop(0)  # Removing title line ("targets:")
        main_goal = None
        if targets:
            # Create main goal:
            main_goal = Goal.from_lean_data(hypo_analysis, targets[0])
        else:
            log.warning(f"No target, targets_analysis={targets_analysis}")
        goals = [main_goal]
        for other_string_goal in targets[1:]:
            other_goal = Goal.from_lean_data(hypo_analysis="",
                                             target_analysis=other_string_goal)
            goals.append(other_goal)
        return cls(goals, (hypo_analysis, targets_analysis))


class ProofStep:
    """
    Class to store data associated to a step in proof.
    The step starts with user inputs, and ends with Lean's responses.
    Note that the proof_state attribute is used both for storing the
    proof_state at the beginning of the step, which is used by logical
    action to compute the pertinent Lean Code,
    and for storing the proof_state at the end of the step, to be stored in
    Journal and lean_file's history.
    """

    # ──────────────── Proof memory ─────────────── #
    property_counter: int    = 0
    current_goal_number: int = 1  # Current number of goal in the proof history
    total_goals_counter: int = 1  # Total number of goals in the proof history
    goal_change_msgs: [str]  = None  # TODO e.g. "Second case: we assume x∈A".

    # ──────────────── Input ─────────────── #
    selection      = None  # [MathObject]
    user_input     = None  # [str]
    button         = None  # ActionButton or str, e.g. "history_undo".
    statement_item = None  # StatementsTreeWidgetItem
    lean_code      = None  # CodeForLean

    # ──────────────── Output ─────────────── #
    effective_code            = None  # CodeForLean that proved effective
    error_type: Optional[int] = 0  # 1 = WUI, 2 = FRE
    error_msg: str            = ''
    proof_state               = None
    no_more_goal              = False

    def __init__(self,
                 goal_change_msgs=None,
                 property_counter=0,
                 current_goal_number=1,
                 total_goals_counter=1,
                 proof_state=None):
        self.property_counter    = property_counter
        self.current_goal_number = current_goal_number
        self.total_goals_counter = total_goals_counter
        if goal_change_msgs:
            self.goal_change_msgs = goal_change_msgs
        else:
            self.goal_change_msgs = []

        self.proof_state = proof_state
        self.selection = []
        self.user_input = []

    @classmethod
    def next(cls, proof_step):
        """
        Instantiate a copy of proof_step by duplicating attributes that
        should be pass to the next proof_step.
        """

        pf = proof_step
        npf = ProofStep(property_counter=pf.property_counter,
                        goal_change_msgs=copy(pf.goal_change_msgs),
                        current_goal_number=pf.current_goal_number,
                        total_goals_counter=pf.total_goals_counter,
                        proof_state=pf.proof_state
                        )
        return npf

    @property
    def success_msg(self):
        if self.is_error():
            return ''
        elif self.effective_code:
            return self.effective_code.success_msg
        elif self.lean_code:
            return self.lean_code.success_msg
        else:
            return ''

    @property
    def goal(self):
        if self.proof_state:
            return self.proof_state.goals[0]
        else:
            return None

    def is_undo(self):
        return self.button == 'history_undo'

    def is_redo(self):
        return self.button == 'history_redo'

    def is_rewind(self):
        return self.button == 'history_rewind'

    def is_history_move(self):
        return self.is_undo() or self.is_redo() or self.is_rewind()

    def is_error(self):
        return bool(self.error_type)

    def compare(self, auto_test) -> (str, bool):
        """
        Compare self to an auto_test, and write a report if unexpected
        happened. This is used for auto_test.

        :return: a string containing a written report, and a bool which is
        True iff everything is OK.
        """
        report = ''
        success = True
        # Case of error
        if self.is_error():
            error_nb = self.error_type
            error_type = auto_test.error_dic[error_nb]
            if not auto_test.error_type:
                report = f"unexpected {error_type}"
                report += f", error msg: {self.error_msg}"
                success = False
            elif auto_test.error_type != error_nb:
                expected_error = auto_test.error_dic[auto_test.error_type]
                report = f"unexpected {error_type}, expected {expected_error}"
                report += f", error msg: {self.error_msg}"
                success = False

        # Error msg
        error_msg = self.error_msg
        if error_msg:
            find = error_msg.find(auto_test.error_msg)
            if find == -1:
                report += f'\nUnexpected error msg: {error_msg}, ' \
                          f'expected: {auto_test.error_msg}'
                success = False
        # Success msg
        success_msg = self.success_msg
        if success_msg:
            find = success_msg.find(auto_test.success_msg)
            if find == -1:
                report += f'\nUnexpected success msg: {success_msg}, ' \
                          f'expected: {auto_test.success_msg}'
                success = False

        return report, success


@dataclass
class Proof:
    """
    This class encodes a whole proof history, maybe uncompleted (i.e. the
    goal is not solved) as a list of ProofStates and Actions.

    It provides a method that counts the number of goals during the proof,
    and tells if a goal has been solved, or if a new goal has emerged during
    the last step of the proof. This piece of info is displayed in the UI.
    """

    # TODO: keep the memory of Action in the history of the lean_file
    # TODO: implement a display_tree method
    # NOT TODO: implement a write_up_proof method ??

    steps: [(ProofState, Any)]  # A proof is a list of proof states.

    def count_goals_from_proof(self):
        """
        Compute and return four values:
            - total_goals_counter : total number of goals during Proof history
            - current_goal_number = number of the goal under study
            - current_goals_counter = number of goals at end of Proof
            - goals_counter_evolution = last evolution :
                > 0 means that new goal has appeared
                < 0 means that a goal has been solved
        This method is deprecated, computation is done iteratively at each
        step of the proof.
        """

        total_goals_counter = 0
        current_goal_number = 1
        current_goals_counter = 0
        goals_counter_evolution = 0
        for proof_state, _ in self.steps:
            new_counter = len(proof_state.goals)
            goals_counter_evolution = new_counter - current_goals_counter
            if goals_counter_evolution > 0:  # New goals have appeared
                total_goals_counter += goals_counter_evolution
            elif goals_counter_evolution < 0:  # Some goals have been solved
                current_goal_number -= goals_counter_evolution
            current_goals_counter = new_counter

        return (total_goals_counter,
                current_goal_number,
                current_goals_counter,
                goals_counter_evolution)


def print_proof_state(goal: Goal):
    print("Context:")
    for mt, mt_list in goal.math_types:
        print(f"{[PO.to_display() for PO in mt_list]} :"
              f" {mt.to_display()}")
    print("Target:")
    print(goal.target.math_type.to_display())


if __name__ == '__main__':
    logger.configure()
    from pprint import pprint

    hypo_analysis_new = """"""
    hypo_analysis_old = """"""
    goal_analysis = """"""

    goal = Goal.from_lean_data(hypo_analysis_old, goal_analysis)
    print("context:")
    pprint(goal.context)
    print(("target:"))
    pprint(goal.target.math_type)

    print("variables: ")
    pprint(goal.extract_var_names())

    hypo_essai = """"""

    essai_set_family_hypo = """"""
    essai_set_family_target = """"""


    def print_proof_state(goal):
        print("Context:")
        for mt, mt_list in goal.math_types:
            print(f"{[PO.to_display() for PO in mt_list]} :"
                  f" {mt.to_display()}")
        print("Target:")
        print(goal.target.math_type.to_display())


    goal = Goal.from_lean_data(essai_set_family_hypo, essai_set_family_target)
    print_proof_state(goal)

    print(f"variable names {goal.extract_var_names()}")
