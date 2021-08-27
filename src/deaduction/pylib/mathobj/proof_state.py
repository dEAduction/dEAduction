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
import deaduction.pylib.config.vars as cvars

from .MathObject import MathObject
from .context_math_object import ContextMathObject
from .lean_analysis import ( lean_expr_with_type_grammar,
                             LeanEntryVisitor )
from .give_name import name_bound_vars, inj_list
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
    context:        [ContextMathObject]
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

    @property
    def context_objects(self) -> [ContextMathObject]:
        objects = [cmo for cmo in self.context if not cmo.math_type.is_prop()]
        return objects

    @property
    def context_props(self) -> [ContextMathObject]:
        props = [cmo for cmo in self.context if cmo.math_type.is_prop()]
        return props

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
                math_object.is_new = True
            else:
                # Put new object at old index, copy tags for ui,
                #  and check for modifications
                old_object = old_context[old_index]
                permuted_new_context[old_index] = math_object
                math_object.copy_tags(old_object)
                old_math_type = old_object.math_type
                new_math_type = math_object.math_type
                # (3) Check if the object has the same type
                if old_math_type == new_math_type:
                    permuted_new_tags[old_index] = "="
                else:  # (4) If not, object has been modified
                    permuted_new_tags[old_index] = "≠"
                    math_object.is_modified = True
                    math_object.is_hidden = False  # Reveal if modified?

            if old_index is not None:
                # Will not be considered anymore:
                old_names[old_index]   = None
                old_context[old_index] = None

        # (5) Remove 'None' entries
        clean_permuted_new_context = [item for item in permuted_new_context
                                      if item is not None]
        clean_permuted_new_tags    = [item for item in permuted_new_tags
                                      if item is not None]

        # Finally modify order and set tags
        self.context     = clean_permuted_new_context
        self.future_tags = clean_permuted_new_tags

    def __name_bound_vars_in_data(self, math_types, dummy_vars, forb_vars,
                                  future_vars):
        """
        Name all vars in dummy_vars, type by type.

        :param math_types: union of all types of vars in dummy_vars.
        :param dummy_vars: unnamed dummy_vars, to be named
        :param forb_vars:  vars whose name is forbidden.
        :param future_vars:  anticipated vars in future context, whose name
        is to be forbidden and used as guide for naming.
        """

        glob_vars = self.context_objects
        for math_type in math_types:
            glob_vars_of_type = [var for var in glob_vars
                                  if var.math_type == math_type]
            dummy_vars_of_type = [var for var in dummy_vars
                                  if var.math_type == math_type]
            future_vars_of_type = [var for var in future_vars
                                  if var.math_type == math_type]
            log.debug(f"Naming vars of type "
                      f"{math_type.to_display()}")
            name_bound_vars(math_type=math_type,
                            named_vars=glob_vars_of_type + future_vars_of_type,
                            unnamed_vars=dummy_vars_of_type,
                            forbidden_vars=forb_vars + future_vars_of_type)
            log.debug(f"    --> "
                      f"{[var.to_display() for var in dummy_vars_of_type]}")

    def __name_bound_vars_in_prop(self, prop: MathObject, future_vars):
        """
        Name all dummy vars in prop.

        :param prop: MathObject, whose math_type is a proposition.
        :return:
        """
        not_glob = cvars.get("logic.do_not_name_dummy_vars_as_global_vars",
                             True)

        glob_vars = self.context_objects

        log.debug(f"Naming vars in {prop.to_display()}:")
        if prop.math_type.bound_vars:
            log.debug(f"""-->Dummy vars types: {[var.math_type.to_display()
                                  for var in prop.math_type.bound_vars]}""")
            # Collect math_types of bound_vars with no rep
            math_types = inj_list([var.math_type for var in
                                   prop.math_type.bound_vars])
            log.debug(f"-->Math_types : "
                      f"{[mt.to_display() for mt in math_types]}")
            # math_types = []
            # for var in prop.bound_vars:
            #     math_type = var.math_type
            #     if math_type not in math_types:
            #         math_types.append(math_type)
            # (Level 1 or 0)
            forb_vars = glob_vars if not_glob \
                else prop.math_type.extract_local_vars()

            data = (math_types,
                    prop.math_type.bound_vars,
                    forb_vars,
                    future_vars)
            self.__name_bound_vars_in_data(*data)

    def name_bound_vars(self, to_prove=True):
        """
        Give a name to all dummy vars appearing in the properties of
        self.context. Three level of constraint are taken into account,
        according to cvars values:
        * Level 0: dummy vars can share names with dummy vars of other props
        and with glob vars.
        * Level 1: dummy vars can share names with dummy vars of other props
        but not with glob vars.
        * Level 2: dummy vars cannot share names with glob vars nor dummy vars
            of other props.

        We first name dummy vars for target, and then estimate future
        context vars from target. Note that thos two sets of vars are not
        disjoint but not identical: target usually contains dummy vars that
        will not be introduced (e.g. existence quantifier, or any dummy var
        in a premisse), and dummy vars will also appear in definitions
        that have not been unfolded yet.
        Those future vars will be considered as forbidden vars, to prevent
        dummy vars name of context properties to from changing too much as
        user unfolds the target.
        
        :param to_prove: True if this is the goal of an exercise, as opposed to
        coming from the initial_proof_state of a statement.
        """
        # (0) Some unnamed vars?
        there_are_unamed_vars = False
        if self.target.math_type.has_unnamed_bound_vars:
            there_are_unamed_vars = True
        else:
            for context_math_prop in self.context_props:
                if context_math_prop.math_type.has_unnamed_bound_vars:
                    there_are_unamed_vars = True
        if not there_are_unamed_vars:
            return

        # (1) Name dummy_vars in target
        self.__name_bound_vars_in_prop(self.target, [])


        # not_glob = cvars.get("logic.do_not_name_dummy_vars_as_global_vars",
        #                      True)
        not_dummy = cvars.get("logic.do_not_name_dummy_vars_as_dummy_vars",
                             False)  # All dummy vars have distinct names

        # glob_vars = self.context_objects

        # (2) Estimate future context names from target (if to_prove == True)
        future_vars = []  # Future context vars to be named
        if to_prove:
            future_vars = self.target.math_type.glob_vars_when_proving()
            math_types = inj_list([var.math_type for var in future_vars])
            data = (math_types, future_vars, self.context_objects, [])
            log.debug("Naming future vars:")
            self.__name_bound_vars_in_data(*data)

        if not_dummy:  # (Level 2)
            # Collect all math_types, with no repetition
            math_types = inj_list([var.math_type
                                   for var in prop.math_type.bound_vars
                                   for prop in self.context_props])
            dummy_vars = [var for var in prop.math_type.bound_vars
                          for prop in prop]  # All dummy vars (no repetition)
            data = (math_types, dummy_vars, self.context_objects, future_vars)
            self.__name_bound_vars_in_data(*data)
        else:  # Types and dummy vars prop by prop
            data = []
            for prop in self.context_props:
                self.__name_bound_vars_in_prop(prop, future_vars)

    def objects_of_type(self, math_type):
        """
        Return all object of self.context whose type is math_type.
        """
        return [obj for obj in self.context_objects
                if obj.math_type == math_type]

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

    ###################
    # Display methods #
    ###################
    def goal_to_text(self,
                     format_="utf8",
                     to_prove=True,
                     text_depth=5,
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

        # Name bound vars if needed!
        self.name_bound_vars(to_prove=to_prove)

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

        # Name bound vars if needed
        self.name_bound_vars(to_prove=to_prove)

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

    def to_tooltip(self, type_='exercise') -> str:
        """
        Return context and target in a raw form as a tooltip for a goal.
        """

        # Name bound vars if needed
        self.name_bound_vars(to_prove=(type_=='exercise'))

        context = self.context
        target = self.target

        # Context
        if context:
            if type_ == "exercise":
                text = _("Context:")
            else:
                text = _("Hypothesis:") if len(context) == 1 else \
                    _("Hypotheses:")
            text += "\n"
        else:
            # text = _("Empty context") + "\n"
            text = ""
        for math_object in context:
            math_type = math_object.math_type
            name = math_object.to_display()
            name_type = math_type.to_display(is_math_type=True)
            text_object = name + _(": ") + name_type
            text += "  " + text_object + "\n"

        # Goal
        if type_ == "exercise":
            text += _("Goal:")
        else:
            text += _("Conclusion:")
        text += "\n"
        text += " " + target.math_type.to_display(is_math_type=True)
        return text


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
    def from_lean_data(cls, hypo_analysis: str, targets_analysis: str,
                       to_prove=True):
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
