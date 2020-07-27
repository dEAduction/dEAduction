from deaduction.pylib.actions.proofs import *
from deaduction.pylib.mathobj.proof_state import Goal


def test_assumption():
    hypo_analysis = """OBJECT[LOCAL_CONSTANT¿[name:A/identifier:0._fresh.95.26636¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:B/identifier:0._fresh.95.26638¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
PROPERTY[LOCAL_CONSTANT¿[name:H/identifier:0._fresh.93.21233¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: A → B] ¿= PROP_IMPLIES¿(LOCAL_CONSTANT¿[name:A/identifier:0._fresh.95.26636¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B/identifier:0._fresh.95.26638¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
PROPERTY[LOCAL_CONSTANT¿[name:a/identifier:0._fresh.93.21235¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: A] ¿= LOCAL_CONSTANT¿[name:A/identifier:0._fresh.95.26636¿]¿(CONSTANT¿[name:1/1¿]¿)"""
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.93.21239]/pp_type: A] ¿= LOCAL_CONSTANT¿[name:A/identifier:0._fresh.95.26636¿]¿(CONSTANT¿[name:1/1¿]¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST NOT ON GOAL-------------")
    #assert action_and(goal, []) == ""
    #assert action_or(goal,[]) == ""
    #assert action_exists(goal,[]) == ""
    #assert action_forall(goal, []) == ""
    print("retour de action_assumption : " + action_assumption(goal, []))
    
def test_case_based_reasoning():
    hypo_analysis = """OBJECT[LOCAL_CONSTANT¿[name:A/identifier:0._fresh.145.2520¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:P/identifier:0._fresh.145.2522¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
PROPERTY[LOCAL_CONSTANT¿[name:a/identifier:0._fresh.146.3141¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: ¬¬P] ¿= PROP_NOT¿(PROP_NOT¿(LOCAL_CONSTANT¿[name:P/identifier:0._fresh.145.2522¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)"""
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.151.1958]/pp_type: P] ¿= LOCAL_CONSTANT¿[name:P/identifier:0._fresh.153.1047¿]¿(CONSTANT¿[name:1/1¿]¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST CASE-BASED REASONING -------------")
    #assert action_and(goal, []) == ""
    #assert action_or(goal,[]) == ""
    #assert action_exists(goal,[]) == ""
    #assert action_forall(goal, []) == ""
    print("retour de action_cbr : " + action_cbr(goal, []))
    
def test_absurdum():
    hypo_analysis = """PROPERTY[METAVAR[_mlocal._fresh.1080.12809]/pp_type: ∃ (n : ℕ), ¬n = 0] ¿= QUANT_∃¿(TYPE_NUMBER¿[name:ℕ¿]¿, LOCAL_CONSTANT¿[name:n/identifier:_fresh.1080.13175¿]¿(TYPE_NUMBER¿[name:ℕ¿]¿)¿, PROP_NOT¿(PROP_EQUAL¿(LOCAL_CONSTANT¿[name:n/identifier:_fresh.1080.13175¿]¿(TYPE_NUMBER¿[name:ℕ¿]¿)¿, NUMBER¿[0¿]¿)¿)¿)"""
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.1080.12809]/pp_type: ∃ (n : ℕ), ¬n = 0] ¿= QUANT_∃¿(TYPE_NUMBER¿[name:ℕ¿]¿, LOCAL_CONSTANT¿[name:n/identifier:_fresh.1080.13175¿]¿(TYPE_NUMBER¿[name:ℕ¿]¿)¿, PROP_NOT¿(PROP_EQUAL¿(LOCAL_CONSTANT¿[name:n/identifier:_fresh.1080.13175¿]¿(TYPE_NUMBER¿[name:ℕ¿]¿)¿, NUMBER¿[0¿]¿)¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST REDUCTIO AD ABSURDUM -------------")
    #assert action_and(goal, []) == ""
    #assert action_or(goal,[]) == ""
    #assert action_exists(goal,[]) == ""
    #assert action_forall(goal, []) == ""
    print("retour de action_absurdum : " + action_absurdum(goal, []))

def test_contrapositive():
    hypo_analysis = """OBJECT[LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1133.4078¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:Ha/identifier:0._fresh.1133.4090¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE"""
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.1133.4091]/pp_type: ¬A → ¬¬¬A] ¿= PROP_IMPLIES¿(PROP_NOT¿(LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1133.4078¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿, PROP_NOT¿(PROP_NOT¿(PROP_NOT¿(LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1133.4078¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST PROOF BY CONTRAPOSITIVE -------------")
    #assert action_and(goal, []) == ""
    #assert action_or(goal,[]) == ""
    #assert action_exists(goal,[]) == ""
    #assert action_forall(goal, []) == ""
    print("retour de action_contrapose : " + action_contrapose(goal, []))

if __name__ == "__main__":
    test_assumption()
    test_case_based_reasoning()
    test_absurdum()
    test_contrapositive()
