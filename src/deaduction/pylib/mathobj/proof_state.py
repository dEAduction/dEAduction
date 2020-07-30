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
import deaduction.pylib.logger as logger
import logging
from typing import List, Tuple
from deaduction.pylib.mathobj import PropObj, ProofStatePO, \
    math_type_store
from snippets.mathobj.give_name import give_name0, instantiate_bound_var

log = logging.getLogger(__name__)


@dataclass
class Goal:
    context: List[ProofStatePO]
    target: ProofStatePO
    math_types: List[Tuple[PropObj, List[ProofStatePO]]]
    variables_names: List[str]

    def compare(self, old_goal, goal_is_new):
        """
        Compare the new goal to the old one, and tag the target and the element
        of both new and old context accordingly. tag is one of the following:
        "+" (in new tag) means present in the new goal, absent in the old goal
        "+" (in old tag) means absent in the new goal, present in the old goal
        "=" (in both) means present in both and identical
        "≠" (in both) means present in both and different

        In the tests, two pfPO's are equal if they have the same name and
        the same math_type, and they are modified versions of each other if
        they have the same name and different math_types.
        If goal_is_new == True then all objects will be tagged as new.

        :param new_goal: new goal
        :param old_goal: old goal
        :param goal_is_new: True if previous goal has been solved
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
            tags_new_context = ["+" for PO in new_context]
            tags_old_context = ["+" for PO in old_context]
            tag_new_target = "+"
            tag_old_target = "+"
        else:
            ##################################
            # tag objects in the new context #
            ##################################
            tags_new_context = [""] * len(new_context)
            tags_old_context = [""] * len(old_context)
            new_index = 0
            old_names = [pfPO_old.lean_data["name"] for pfPO_old in
                         old_context]
            for pfPO in new_context:
                name = pfPO.lean_data["name"]
                log.debug(f"pfPO: {name}")
                try:
                    old_index = old_names.index(name)
                except ValueError:
                    # log.debug("the name does not exist in old_context")
                    tag = "+"
                else:
                    # next test uses PropObj.__eq__, which is redefined
                    # in PropObj (recursively test nodes)
                    if old_context[old_index].math_type == pfPO.math_type:
                        tag = "="
                    else:
                        tag = "≠"
                tags_new_context[new_index] = tag
                tags_old_context[old_index] = tag
                new_context[new_index] = None  # will not be considered
                                               # anymore
                old_context[old_index] = None  # will not be considered
                                               # anymore
                new_index += 1

            # Tag the remaining objects in old_context as new ("+")
            old_index = 0
            for pfPO in old_context:
                if pfPO is not None:
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

    def extract_var_names(self) -> List[str]:
        """
        provides the list of names of all variables in the context,
        including bound variables as listed in the bound_vars field of
        ProofStatePO's instances
        :return: list of strings (variables names)
        """
        if self.variables_names:
            return self.variables_names
        log.info("extracting the list of variables's names")
        context = self.context
        target = self.target
        names = []
        for pfpo in context:
            name = pfpo.lean_data["name"]
            if name != '':
                names.append(name)
            names.extend(pfpo.bound_vars)
        names.extend(target.bound_vars)
        self.variables_names = names
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
        lines = hypo_analysis.splitlines()
        context = []
        math_types = []  # this is a list of tuples
        # (math_type, math_type_instances)
        # where math_type_instances is a list of instances of math_type
        # computing new pfPO's
        for prop_obj_string in lines:
            if prop_obj_string.startswith("context:"):
                continue
            else:
                prop_obj = ProofStatePO.from_string(prop_obj_string)
                math_type_store(math_types, prop_obj, prop_obj.math_type)
                context.append(prop_obj)
        target = ProofStatePO.from_string(target_analysis)
        variables_names = []
        goal = cls(context, target, math_types, variables_names)
        #
        for pfpo in goal.context:
            ############################################################
            # special format that needs supplementary bounds variables #
            ############################################################
            math_type = pfpo.math_type
            if math_type.node in ["SET_FAMILY", "SEQUENCE"]:  # TODO : mettre ça dans latex_format
                pfpo.node += "INSTANCE_OF_" + math_type.node
                bound_var_type = math_type.children[0]
                name = give_name0(goal, bound_var_type)
                bound_var = instantiate_bound_var(math_type, name)
                pfpo.children = [bound_var]
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
        for (po, tag) in zip(context, tags):
            if po.math_type.is_prop():
                propositions.append((po, tag))
            else:
                objects.append((po, tag))
        return objects, propositions

@dataclass
class ProofState:
    goals: List[Goal]

    @classmethod
    def from_lean_data(cls, hypo_analysis: str, targets_analysis: str):
        """
        :param hypo_analysis: string from the lean tactic hypo_analysis
        :param targets_analysis: string from the lean tactic targets_analysis
        (with one line per target)
        :return: a ProofState
        """
        log.info("creating new ProofState from lean strings")
        targets = targets_analysis.splitlines()
        if targets[0].startswith("targets:"):
            targets.pop(0)
        main_goal = Goal.from_lean_data(hypo_analysis, targets[0])
        goals = [main_goal]
        for other_string_goal in targets[1:]:
            other_goal = Goal.from_lean_data("", other_string_goal)
            goals.append(other_goal)
        return cls(goals)


if __name__ == '__main__':
    logger.configure()
    from pprint import pprint

    hypo_analysis_new = """OBJECT[LOCAL_CONSTANT¿[
    name:X/identifier:0._fresh.667.14907¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
    OBJECT[LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.667.14909¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
    OBJECT[LOCAL_CONSTANT¿[name:f/identifier:0._fresh.667.14912¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= FUNCTION¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.667.14907¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.667.14909¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
    OBJECT[LOCAL_CONSTANT¿[name:B/identifier:0._fresh.667.14914¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.667.14909¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
    OBJECT[LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.667.14917¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.667.14909¿]¿(CONSTANT¿[name:1/1¿]¿)¿)"""
    hypo_analysis_old = """OBJECT[LOCAL_CONSTANT¿[
    name:X/identifier:0._fresh.680.5802¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
    OBJECT[LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.680.5804¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
    OBJECT[LOCAL_CONSTANT¿[name:f/identifier:0._fresh.680.5807¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= FUNCTION¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.680.5802¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.680.5804¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
    OBJECT[LOCAL_CONSTANT¿[name:B/identifier:0._fresh.680.5809¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.680.5804¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
    OBJECT[LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.680.5812¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.680.5804¿]¿(CONSTANT¿[name:1/1¿]¿)¿)"""
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.679.4460]/pp_type: ∀ ⦃x : X⦄, x ∈ (f⁻¹⟮B ∪ B'⟯) → x ∈ f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯)] ¿= QUANT_∀¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.680.5802¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:x/identifier:_fresh.679.4484¿]¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.680.5802¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, PROP_IMPLIES¿(PROP_BELONGS¿(LOCAL_CONSTANT¿[name:x/identifier:_fresh.679.4484¿]¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.680.5802¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.680.5807¿]¿(CONSTANT¿[name:1/1¿]¿)¿, SET_UNION¿(LOCAL_CONSTANT¿[name:B/identifier:0._fresh.680.5809¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.680.5812¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)¿, PROP_BELONGS¿(LOCAL_CONSTANT¿[name:x/identifier:_fresh.679.4484¿]¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.680.5802¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, SET_UNION¿(SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.680.5807¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B/identifier:0._fresh.680.5809¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.680.5807¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.680.5812¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)¿)¿)"""

    goal = Goal.from_lean_data(hypo_analysis_old, goal_analysis)
    print("context:")
    pprint(goal.context)
    print(("target:"))
    pprint(goal.target)

    print("variables: ")
    pprint(goal.extract_var_names())

    hypo_essai = """OBJECT[LOCAL_CONSTANT¿[name:X/identifier:0._fresh.725.7037¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.725.7039¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:f/identifier:0._fresh.725.7042¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= FUNCTION¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.725.7037¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.725.7039¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:B/identifier:0._fresh.725.7044¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.725.7039¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.725.7047¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.725.7039¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:x/identifier:0._fresh.726.4018¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= LOCAL_CONSTANT¿[name:X/identifier:0._fresh.725.7037¿]¿(CONSTANT¿[name:1/1¿]¿)
PROPERTY[LOCAL_CONSTANT¿[name:H/identifier:0._fresh.726.4020¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: x ∈ (f⁻¹⟮B ∪ B'⟯)] ¿= PROP_BELONGS¿(LOCAL_CONSTANT¿[name:x/identifier:0._fresh.726.4018¿]¿(CONSTANT¿[name:1/1¿]¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.725.7042¿]¿(CONSTANT¿[name:1/1¿]¿)¿, SET_UNION¿(LOCAL_CONSTANT¿[name:B/identifier:0._fresh.725.7044¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.725.7047¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)"""


    essai_set_family_hypo = """context:
OBJECT[LOCAL_CONSTANT¿[name:X/identifier:0._fresh.212.23980¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:I/identifier:0._fresh.212.23982¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:E/identifier:0._fresh.212.23985¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET_FAMILY¿(LOCAL_CONSTANT¿[name:I/identifier:0._fresh.212.23982¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:X/identifier:0._fresh.212.23980¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:F/identifier:0._fresh.212.23989¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET_FAMILY¿(LOCAL_CONSTANT¿[name:I/identifier:0._fresh.212.23982¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:X/identifier:0._fresh.212.23980¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
PROPERTY[LOCAL_CONSTANT¿[name:H/identifier:0._fresh.212.24016¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: ∀ (i : I), F i = (E iᶜ)] ¿= QUANT_∀¿(LOCAL_CONSTANT¿[name:I/identifier:0._fresh.212.23982¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:i/identifier:_fresh.214.20405¿]¿(LOCAL_CONSTANT¿[name:I/identifier:0._fresh.212.23982¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, PROP_EQUAL¿(APPLICATION¿(LOCAL_CONSTANT¿[name:F/identifier:0._fresh.212.23989¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:i/identifier:_fresh.214.20405¿]¿(LOCAL_CONSTANT¿[name:I/identifier:0._fresh.212.23982¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿, SET_COMPLEMENT¿(APPLICATION¿(LOCAL_CONSTANT¿[name:E/identifier:0._fresh.212.23985¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:i/identifier:_fresh.214.20405¿]¿(LOCAL_CONSTANT¿[name:I/identifier:0._fresh.212.23982¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)¿)¿)"""
    essai_set_family_target = """PROPERTY[METAVAR[_mlocal._fresh.214.20069]/pp_type: Union Eᶜ = Inter F] ¿= PROP_EQUAL¿(SET_COMPLEMENT¿(SET_UNION+¿(LOCAL_CONSTANT¿[name:E/identifier:0._fresh.212.23985¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿, SET_INTER+¿(LOCAL_CONSTANT¿[name:F/identifier:0._fresh.212.23989¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)"""
    def print_proof_state(goal):
        print("Context:")
        for mt, mt_list in goal.math_types:
            print(f"{[PO.format_as_utf8() for PO in mt_list]} :"
                  f" {mt.format_as_utf8()}")
        print("Target:")

    goal = Goal.from_lean_data(essai_set_family_hypo, essai_set_family_target)
    print_proof_state(goal)
