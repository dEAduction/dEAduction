"""
# proof_state.py : provides the class ProofState and Goals
    
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
from typing import List, Dict
from PropObj import ProofStatePO, create_pspo, extract_identifier1


@dataclass
class Goal:
    context: List[ProofStatePO]
    target: ProofStatePO
    variables_names: List[str]

    def update(self, updated_hypo_analysis):
        """
        search for the new identifiers in updated_old_hypo_analysis,
        and substitute them in the ProofStatePO's of the context
        :param updated_old_hypo_analysis: string from the lean tactic
        hypo_analysis corresponding to the previous step)
        """
        log = logging.getLogger("proof_state")
        log.info("updating old context with new identifiers")
        identifiers = []
        context = self.context
        counter = 0
        for line in updated_hypo_analysis.splitlines():
            ident = extract_identifier1(line)
            pfpo = context[counter]
            pfpo.lean_data["id"] = ident
            counter += 1

    def compare(new_goal, old_goal):
        """
        Compare the new goal to the old one, and tag the target and the element
        of both new and old context accordingly. tag is one of the following:
        "+" (in new tag) means present in the new goal, absent in the old goal
        "-" (in old tag) means absent in the new goal, present in the old goal
        "=" (in both) means present in both and identical
        "≠" (in both) means present in both and different

        :param new_goal: new goal
        :param old_goal: old goal
        :return:
            - two lists old_goal_diff, new_goal_diff of tags
            - two more tags old_goal_diff, new_goal_diff
        """
        pass

    def extract_var_names(self) -> List[str]:
        """
        provides the list of names of all variables in the context,
        including bound variables as listed in the bound_vars field of
        ProofStatePO's instances
        :return: list of strings (variables names)
        """
        context = self.context
        goal = self.target
        names = []
        for pfpo in context:
            name = pfpo.lean_data["name"]
            if name != '':
                names.append(name)
            names.extend(pfpo.bound_vars)
        names.extend(goal.bound_vars)
        self.variables_names = names
        return names


    @classmethod
    def from_lean_data(cls, hypo_analysis: str, goal_analysis: str):
        """
        :param hypo_analysis: string from the lean tactic hypo_analysis
        :param goal_analysis: first string from the lean tactic goals_analysis
        (only one target)
        :return: a Goal
        """
        list_ = hypo_analysis.splitlines()
        #    is_goal = None
        context = []
        for prop_obj_string in list_:
            prop_obj = create_pspo(prop_obj_string)
            #           PO.is_goal = is_goal
            context.append(prop_obj)
        target = create_pspo(goal_analysis)
        variables_names = []  # todo
        return cls(context, target, variables_names)

    def context_obj(self):
        """
        provide the sublist of self.context containing all the math objects
        (as opposed to propositions)
        """
        return [o for o in self.context if not o.math_type.is_prop()]

    def context_prop(self):
        """
        provide the sublist of self.context containing all the math
        propositions
        (as opposed to objects)
        """
        return [o for o in self.context if o.math_type.is_prop()]


@dataclass
class ProofState:
    goals: List[Goal]

    @classmethod
    def from_lean_data(cls, hypo_analysis: str, goals_analysis: str):
        """
        :param hypo_analysis: string from the lean tactic hypo_analysis
        :param goals_analysis: string from the lean tactic goals_analysis
        (with one line per target)
        :return: a ProofState
        """
        list_goals = goals_analysis.splitlines()
        main_goal = Goal.from_lean_data(hypo_analysis, list_goals[0])
        goals = [main_goal]
        for other_string_goal in list_goals[1:]:
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
    pprint(goal.context)
    goal.update(hypo_analysis_new)
    print("New context: ")
    pprint(goal.context)

    print("variables: ")
    pprint(goal.extract_var_names())

    hypo_essai = """OBJECT[LOCAL_CONSTANT¿[
    name:X/identifier:0._fresh.725.7037¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.725.7039¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:f/identifier:0._fresh.725.7042¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= FUNCTION¿(LOCAL_CONSTANT¿[name:X/identifier:0._fresh.725.7037¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.725.7039¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:B/identifier:0._fresh.725.7044¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.725.7039¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.725.7047¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= SET¿(LOCAL_CONSTANT¿[name:Y/identifier:0._fresh.725.7039¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
OBJECT[LOCAL_CONSTANT¿[name:x/identifier:0._fresh.726.4018¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= LOCAL_CONSTANT¿[name:X/identifier:0._fresh.725.7037¿]¿(CONSTANT¿[name:1/1¿]¿)
PROPERTY[LOCAL_CONSTANT¿[name:H/identifier:0._fresh.726.4020¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: x ∈ (f⁻¹⟮B ∪ B'⟯)] ¿= PROP_BELONGS¿(LOCAL_CONSTANT¿[name:x/identifier:0._fresh.726.4018¿]¿(CONSTANT¿[name:1/1¿]¿)¿, SET_INVERSE¿(LOCAL_CONSTANT¿[name:f/identifier:0._fresh.725.7042¿]¿(CONSTANT¿[name:1/1¿]¿)¿, SET_UNION¿(LOCAL_CONSTANT¿[name:B/identifier:0._fresh.725.7044¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B'/identifier:0._fresh.725.7047¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)"""
    goal = Goal.from_lean_data(hypo_essai, "")
    print("Objects:")
    pprint(goal.context_obj())
    print("Propositions:")
    pprint(goal.context_prop())
