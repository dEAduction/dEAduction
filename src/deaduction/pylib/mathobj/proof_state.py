"""
# proof_state.py : provides the class ProofState and Goal
    
    (#optionalLongDescription)

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
from typing import List, Tuple, Any

import deaduction.pylib.logger  as              logger
from deaduction.config          import          _, user_config

from deaduction.pylib.mathobj.MathObject import MathObject
from deaduction.pylib.mathobj.lean_analysis import \
                                                lean_expr_with_type_grammar, \
                                                LeanEntryVisitor


log = logging.getLogger(__name__)


@dataclass
class Goal:
    context: List[MathObject]
    target: MathObject

    # the following would be useful if we decide to display objects of the
    # same type together:
    # math_types: List[Tuple[MathObject, List[MathObject]]]
    # variables_names: List[str]

    def compare(self, old_goal, goal_is_new=False):
        """
        Compare the new goal to the old one, and tag the target and the element
        of both new and old context accordingly. tag is one of the following:
        "+" (in new tag) means present in the new goal, absent in the old goal
        "+" (in old tag) means absent in the new goal, present in the old goal
        "=" (in both) means present in both and identical
        "≠" (in both) means present in both and different

        In the tests, two math_object's are equal if they have the same name
        and the same math_type, and they are modified versions of each other if
        they have the same name and different math_types.
        If goal_is_new == True then all objects will be tagged as new.
        fixme: That's bad: probably in that case objects should be compared
         with objects of the goal that is logically (and not
         chronologically) just before the present context
         Anyway, this is never used
        :param self: new goal
        :param old_goal: old goal
        :param goal_is_new: True if previous goal has been solved
        THIS IS NOT USED for the moment
        :return:
            - two lists old_goal_diff, new_goal_diff of tags
            - two more tags old_goal_diff, new_goal_diff
        """
        log.info("comparing and tagging old goal and new goal")
        new_goal = self
        new_context = new_goal.context.copy()
        old_context = old_goal.context.copy()
        log.debug(old_context)
        log.debug(new_context)
        if goal_is_new:
            tags_new_context = ["+"] * len(new_context)
            tags_old_context = ["+"] * len(old_context)
            tag_new_target = "+"
            tag_old_target = "+"
        else:
            ##################################
            # tag objects in the new context #
            ##################################
            tags_new_context = [""] * len(new_context)
            tags_old_context = [""] * len(old_context)
            new_index = 0
            old_names = [math_object_old.info["name"] for math_object_old in
                         old_context]
            for math_object in new_context:
                name = math_object.info["name"]
                # log.debug(f"math_object: {name}")
                try:
                    old_index = old_names.index(name)
                except ValueError:
                    # log.debug("the name does not exist in old_context")
                    tag = "+"
                    old_index = None
                else:
                    # next test uses PropObj.__eq__, which is redefined
                    # in PropObj (recursively test nodes)
                    old_math_type = old_context[old_index].math_type
                    new_math_type = math_object.math_type
                    if old_math_type == new_math_type:
                        tag = "="
                    else:
                        log.warning("Modified objects")
                        log.debug(f"Old:{old_context[old_index].math_type}")
                        log.debug(f"New:{math_object.math_type}")
                        tag = "≠"
                tags_new_context[new_index] = tag
                new_context[new_index] = None  # will not be considered
                # anymore
                if old_index is not None:
                    tags_old_context[old_index] = tag
                    old_context[old_index] = None  # will not be considered
                    # anymore
                new_index += 1

            # Tag the remaining objects in old_context as new ("+")
            for old_index in range(len(old_context)):
                if old_context[old_index] is not None:
                    tags_old_context[old_index] = "+"
            ###################
            # tag the targets #
            ###################
            # if goal is not new then the target is either modified ("≠")
            # or unchanged ("=")
            new_target = new_goal.target.math_type
            old_target = old_goal.target.math_type
            if new_target == old_target:
                tag_new_target, tag_old_target = "=", "="
            else:
                tag_new_target, tag_old_target = "≠", "≠"
        new_goal.future_tags = (tags_new_context, tag_new_target)
        old_goal.past_tags_old_context = (tags_old_context, tag_old_target)
        # log.debug(f"Old goal old tags: {old_goal.past_tags_old_context}")
        # log.debug(f"New goal future tags: {new_goal.future_tags}")

    def extract_vars(self) -> List[MathObject]:
        """
        provides the list of all variables in the context,
        (but NOT bound variables, nor names of hypotheses)
        :return: list of MathObject (variables names)
        """
        # log.info("extracting the list of global variables")
        variables = [math_object for math_object in self.context
                     if not math_object.is_prop()]
        return variables

    def extract_vars_names(self) -> List[str]:
        """
        provides the list of names of all variables in the context,
        (but NOT bound variables, nor names of hypotheses)
        :return: list of MathObject (variables names)
        """
        # log.info("extracting the list of global variables")
        names = [math_object.info['name'] for math_object in
                     self.extract_vars()]
        return names

    @classmethod
    def from_lean_data(cls, hypo_analysis: str, target_analysis: str):
        """
        :param hypo_analysis: string from the lean tactic hypo_analysis
        :param target_analysis: first string from the lean tactic
        targets_analysis
        (only one target)
        :return: a Goal
        """
        log.info("creating new Goal from lean strings")
        # log.debug(hypo_analysis)
        # log.debug(target_analysis)
        lines = hypo_analysis.split("¿¿¿")
        # put back "¿¿¿" and remove '\n', getting rid of the title line
        # ("context:")
        lines = ['¿¿¿' + item.replace('\n', '') for item in lines[1:]]
        context = []
        # math_types = []  # this is a list of tuples
        # (math_type, math_type_instances)
        # where math_type_instances is a list of instances of math_type
        # computing new math_object's
        for math_obj_string in lines:
            if math_obj_string.startswith("context:"):
                continue
            else:
                tree = lean_expr_with_type_grammar.parse(math_obj_string)
                math_object = LeanEntryVisitor().visit(tree)
                # math_type_store(math_types, prop_obj, prop_obj.math_type)
                context.append(math_object)

        tree = lean_expr_with_type_grammar.parse(target_analysis)
        target = LeanEntryVisitor().visit(tree)
        goal = cls(context, target)
        return goal

    def tag_and_split_propositions_objects(self):
        """
        :return:
        - a list of tuples (po, tag), where po is an object in the context
        and tag is the tag of po
        - a list of tuples (po, tag), where po is a proposition in the context
        and tag is the tag of po
        """
        log.info("split objects and propositions of the context")
        context = self.context
        try:
            tags = self.future_tags[0]  # tags of the context
        except AttributeError:  # if tags have not been computed
            tags = ["="] * len(context)
        objects = []
        propositions = []
        for (math_object, tag) in zip(context, tags):
            if math_object.math_type.is_prop():
                propositions.append((math_object, tag))
            else:
                objects.append((math_object, tag))
        return objects, propositions

    def goal_to_text(self, format_="utf8", to_prove=True, text_depth=1) \
            -> str:
        """compute a readable version of the goal as the statement of an
        exercise.

        :param format_:     NOT USED
        :param to_prove:    boolean.
            If True, the goal will be formulated as "Prove that..."
            If False, the goal will be formulated as "Then..." (useful if
            the goal comes from a Theorem or Definition)
        :param text_depth:  int
            A higher value entail a more verbose formulation (more symbols will
            be replaced by words).
            fixme: depth>1 does not really work
        :return: a text version of the goal
        """
        context = self.context
        target = self.target
        text = ""
        for mathobj in context:
            math_type = mathobj.math_type
            if math_type.is_prop():
                prop = mathobj.math_type.to_display(
                    text_depth=text_depth,
                    is_math_type=True)
                new_sentence = _("Assume that") + " " + prop + "."
            else:
                name = mathobj.to_display()
                name_type = math_type.to_display(is_math_type=True,
                                                 text_depth=text_depth - 1)
                if math_type.node == "FUNCTION":  # and text_depth == 0:
                    new_sentence = _("Let") + " " + name + ":" \
                                   + " " + name_type + "."
                else:
                    if user_config['select_language'] == 'fr_FR':
                        # indispensable pour la gestion des espacements
                        # (le "be" anglais n'a pas d'équivalent en français)
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
                                                  is_math_type=True,
                                                  format_="utf8")
        if to_prove:
            target_text = _("Prove that") + " " + target_text
        else:
            if text:
                target_text = _("Then") + " " + target_text
            else:
                target_text = target_text.capitalize()
                # little problem: if sentence starts with a lower case
                # variable. This should never happen though...

        text += target_text + "."
        return text

    def print_goal(self) -> str:
            """
            return context and target in a raw form
            """
            context = self.context
            target = self.target
            text = _("Context:") + "\n"
            for mathobj in context:
                math_type = mathobj.math_type
                # if math_type.is_prop():
                #     prop = mathobj.math_type.to_display(is_math_type=True)
                #     new_sentence = _("Assume that") + " " + prop + "."
                name = mathobj.to_display()
                name_type = math_type.to_display(is_math_type=True)
                text_object = name + " : " + name_type
                text += "  " + text_object + "\n"
            text += _("Target:") + "\n"
            text += target.math_type.to_display(is_math_type=True)
            return text


# def instantiate_bound_var(math_type, name: str):
#     """
#     create a BoundVarPOof with a given math_type and name
#     :param math_type: PropObj
#     :param name:
#     :return: BoundVarPO
#     """
#     info = {"name": name}
#     math_obj = MathObject(node='BOUND_VAR_DEADUCTION', info=info,
#                           math_type=math_type, children=[])
#     return math_obj


@dataclass
class ProofState:
    goals: List[Goal]
    lean_data: Tuple[str] = None

    @classmethod
    def from_lean_data(cls, hypo_analysis: str, targets_analysis: str):
        """
        :param hypo_analysis: string from the lean tactic hypo_analysis
        :param targets_analysis: string from the lean tactic targets_analysis
        (with one line per target)
        :return: a ProofState
        """
        log.info("creating new ProofState from lean strings")
        targets = targets_analysis.split("¿¿¿")
        # put back "¿¿¿" and remove '\n' :
        targets = ['¿¿¿' + item.replace('\n', '') for item in targets]
        targets.pop(0)  # removing title line ("targets:")
        main_goal = None
        if targets:
            # create main goal:
            main_goal = Goal.from_lean_data(hypo_analysis, targets[0])
        else:
            log.warning(f"No target, targets_analysis={targets_analysis}")
        goals = [main_goal]
        for other_string_goal in targets[1:]:
            other_goal = Goal.from_lean_data(hypo_analysis="",
                                             target_analysis=other_string_goal)
            goals.append(other_goal)
        return cls(goals, (hypo_analysis, targets_analysis))


@dataclass
class Proof:
    """
    This class encodes a whole proof history, maybe uncompleted (i.e. the
    goal is not solved) as a list of ProofStates and Actions.
    TODO: keep the memory of Action in the history of the lean_file
    TODO: implement a display_tree method
    NOT TODO: implement a write_up_proof method ??
    """
    steps: [(ProofState, Any)]

    def count_goals_from_proof(self):
        """
        Compute and return three values:
            - total_goals_counter : total number of goals during Proof history
            - current_goal_number = number of the goal under study
            - current_goals_counter = number of goals at end of Proof
            - goals_counter_evolution = last evolution :
                > 0 means that new goal has appeared
                < 0 means that a goal has been solved
        """
        total_goals_counter = 0
        current_goal_number = 1
        current_goals_counter = 0
        goals_counter_evolution = 0
        # log.debug(f"counting goals in {self} with {len(self.steps)} "
        #          f"steps")
        for proof_state, _ in self.steps:
            new_counter = len(proof_state.goals)
            goals_counter_evolution = new_counter - current_goals_counter
            if goals_counter_evolution > 0:  # new goals have appeared
                total_goals_counter += goals_counter_evolution
            elif goals_counter_evolution < 0:  # some goals have been solved
                current_goal_number -= goals_counter_evolution
            current_goals_counter = new_counter

        return total_goals_counter, \
               current_goal_number, \
               current_goals_counter, \
               goals_counter_evolution


def print_proof_state(goal):
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
