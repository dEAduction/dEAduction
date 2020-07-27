from pprint import pprint
from deaduction.pylib.actions.logic import *
from deaduction.pylib.mathobj.proof_state import Goal

if __name__ == "__main__":
    #logger.configure()
    #log = logging.getLogger("test action logiques")
    
    hypo_analysis = ""
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.1754.49417]/pp_type: ¬¬A] ¿= PROP_NOT¿(PROP_NOT¿(LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1754.49396¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST NOT ON GOAL-------------")
    assert action_and(goal, []) == ""
    assert action_or(goal,[]) == ""
    assert action_exists(goal,[]) == ""
    assert action_forall(goal, []) == ""
    print("retour de action_negate : " + action_negate(goal, []))
    
    hypo_analysis = """OBJECT[LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1767.44447¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:Ha/identifier:0._fresh.1767.44459¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
PROPERTY[LOCAL_CONSTANT¿[name:H/identifier:0._fresh.1767.44467¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: ¬¬¬¬A] ¿= PROP_NOT¿(PROP_NOT¿(PROP_NOT¿(PROP_NOT¿(LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1767.44447¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)¿)¿)"""
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.1754.49417]/pp_type: ¬¬A] ¿= PROP_NOT¿(PROP_NOT¿(LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1754.49396¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST NOT ON HYPOTHESIS-------------")
    assert action_and(goal, []) == ""
    assert action_or(goal,[]) == ""
    assert action_exists(goal,[]) == ""
    assert action_forall(goal, []) == ""
    print("retour de action_negate : " + action_negate(goal, [goal.context[2]]))
    
    hypo_analysis = ""
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.380.5357]/pp_type: ∀ (x : ℝ), x = x] ¿= QUANT_∀¿(TYPE_NUMBER¿[name:ℝ¿]¿, LOCAL_CONSTANT¿[name:x/identifier:_fresh.380.5698¿]¿(TYPE_NUMBER¿[name:ℝ¿]¿)¿, PROP_EQUAL¿(LOCAL_CONSTANT¿[name:x/identifier:_fresh.380.5698¿]¿(TYPE_NUMBER¿[name:ℝ¿]¿)¿, LOCAL_CONSTANT¿[name:x/identifier:_fresh.380.5698¿]¿(TYPE_NUMBER¿[name:ℝ¿]¿)¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST FORALL -------------")
    assert action_and(goal, []) == ""
    assert action_or(goal,[]) == ""
    assert action_exists(goal,[]) == ""
    print("retour de action_forall : " + action_forall(goal, []))
    print("retour de action_forall : " + action_forall(goal, []))
    print("retour de action_forall : " + action_forall(goal, []))
    print("retour de action_forall : " + action_forall(goal, []))
    print("retour de action_forall : " + action_forall(goal, []))
    print("retour de action_forall : " + action_forall(goal, []))
    
    hypo_analysis = """PROPERTY[LOCAL_CONSTANT¿[name:H/identifier:0._fresh.1497.44014¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: ∃ (n : ℕ), n = 2] ¿= QUANT_∃¿(TYPE_NUMBER¿[name:ℕ¿]¿, LOCAL_CONSTANT¿[name:n/identifier:_fresh.1497.44016¿]¿(TYPE_NUMBER¿[name:ℕ¿]¿)¿, PROP_EQUAL¿(LOCAL_CONSTANT¿[name:n/identifier:_fresh.1497.44016¿]¿(TYPE_NUMBER¿[name:ℕ¿]¿)¿, NUMBER¿[2¿]¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST APPLY EXISTS -------------")
    assert action_and(goal, []) == ""
    assert action_or(goal,[]) == ""
    #assert action_forall(goal,[]) == ""
    print("retour de action_exists : " + action_exists(goal, [goal.context[0]]))
    
    
    hypo_analysis = """PROPERTY[LOCAL_CONSTANT¿[name:H2/identifier:0._fresh.1789.42154¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: ∃ (n : ℕ) (H : n > 0), n = 2] ¿= QUANT_∃¿(TYPE_NUMBER¿[name:ℕ¿]¿, LOCAL_CONSTANT¿[name:n/identifier:_fresh.1789.42156¿]¿(TYPE_NUMBER¿[name:ℕ¿]¿)¿, PROP_∃¿(PROP_>¿(LOCAL_CONSTANT¿[name:n/identifier:_fresh.1789.42156¿]¿(TYPE_NUMBER¿[name:ℕ¿]¿)¿, NUMBER¿[0¿]¿)¿, PROP_EQUAL¿(LOCAL_CONSTANT¿[name:n/identifier:_fresh.1789.42156¿]¿(TYPE_NUMBER¿[name:ℕ¿]¿)¿, NUMBER¿[2¿]¿)¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("""------------- TEST APPLY "DOUBLE" EXISTS -------------""")
    assert action_and(goal, []) == ""
    assert action_or(goal,[]) == ""
    #assert action_forall(goal,[]) == ""
    print("retour de action_exists : " + action_exists(goal, [goal.context[0]]))
    
    
    
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.1518.14133]/pp_type: ∃ (x : ℝ), x = x] ¿= QUANT_∃¿(TYPE_NUMBER¿[name:ℝ¿]¿, LOCAL_CONSTANT¿[name:x/identifier:_fresh.1518.14461¿]¿(TYPE_NUMBER¿[name:ℝ¿]¿)¿, PROP_EQUAL¿(LOCAL_CONSTANT¿[name:x/identifier:_fresh.1518.14461¿]¿(TYPE_NUMBER¿[name:ℝ¿]¿)¿, LOCAL_CONSTANT¿[name:x/identifier:_fresh.1518.14461¿]¿(TYPE_NUMBER¿[name:ℝ¿]¿)¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST CONSTRUCT EXISTS -------------")
    assert action_and(goal, []) == ""
    assert action_or(goal,[]) == ""
    assert action_forall(goal,[]) == ""
    print("retour de action_exists : " + action_exists(goal, []))
    
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.1681.2584]/pp_type: ∃ (x : ℝ), x = 0] ¿= QUANT_∃¿(TYPE_NUMBER¿[name:ℝ¿]¿, LOCAL_CONSTANT¿[name:x/identifier:_fresh.1681.2585¿]¿(TYPE_NUMBER¿[name:ℝ¿]¿)¿, PROP_EQUAL¿(LOCAL_CONSTANT¿[name:x/identifier:_fresh.1681.2585¿]¿(TYPE_NUMBER¿[name:ℝ¿]¿)¿, NUMBER¿[0¿]¿)¿)"""
    hypo_analysis = """OBJECT[LOCAL_CONSTANT¿[name:x/identifier:0._fresh.1691.4404¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE_NUMBER¿[name:ℝ¿]
PROPERTY[LOCAL_CONSTANT¿[name:Hx/identifier:0._fresh.1691.4405¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: x = 0] ¿= PROP_EQUAL¿(LOCAL_CONSTANT¿[name:x/identifier:0._fresh.1691.4404¿]¿(CONSTANT¿[name:1/1¿]¿)¿, NUMBER¿[0¿]¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST CONSTRUCT EXISTS USING EXISTING OBJECT -------------")
    assert action_and(goal, []) == ""
    assert action_or(goal,[]) == ""
    assert action_forall(goal,[]) == ""
    print("retour de action_exists : " + action_exists(goal, [goal.context[0]]))
    
    
    hypo_analysis = ""
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.180.20417]/pp_type: 5 = 5 ∧ 6 = 6] ¿= PROP_AND¿(PROP_EQUAL¿(NUMBER¿[5¿]¿, NUMBER¿[5¿]¿)¿, PROP_EQUAL¿(NUMBER¿[6¿]¿, NUMBER¿[6¿]¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST CONSTRUCT AND -------------")
    print("retour de action_and : ", action_and(goal,[]))
    assert action_or(goal,[]) == ""
    assert action_exists(goal,[]) == ""
    assert action_forall(goal, []) == ""
    
    hypo_analysis = """PROPERTY[LOCAL_CONSTANT¿[name:H/identifier:0._fresh.215.31382¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: 5 = 5 ∧ 6 = 6] ¿= PROP_AND¿(PROP_EQUAL¿(NUMBER¿[5¿]¿, NUMBER¿[5¿]¿)¿, PROP_EQUAL¿(NUMBER¿[6¿]¿, NUMBER¿[6¿]¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST APPLY AND -------------")
    print("retour de action_and : ", action_and(goal,[goal.context[0]]))
    assert action_or(goal,[goal.context[0]]) == ""
    assert action_exists(goal,[goal.context[0]]) == ""
    assert action_forall(goal,[goal.context[0]]) == ""
    
    hypo_analysis = ""
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.282.38692]/pp_type: 5 = 5 ∨ 6 = 0] ¿= PROP_OR¿(PROP_EQUAL¿(NUMBER¿[5¿]¿, NUMBER¿[5¿]¿)¿, PROP_EQUAL¿(NUMBER¿[6¿]¿, NUMBER¿[0¿]¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST CONSTRUCT OR -------------")
    print("retour de action_or : ", action_or(goal,[]))
    assert action_and(goal,[]) == ""
    assert action_exists(goal,[]) == ""
    assert action_forall(goal, []) == ""
    
    hypo_analysis= """PROPERTY[LOCAL_CONSTANT¿[name:H/identifier:0._fresh.306.39727¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: 1 = 1 ∨ 2 = 2] ¿= PROP_OR¿(PROP_EQUAL¿(NUMBER¿[1¿]¿, NUMBER¿[1¿]¿)¿, PROP_EQUAL¿(NUMBER¿[2¿]¿, NUMBER¿[2¿]¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST APPLY OR -------------")
    print("retour de action_or : ", action_or(goal,[goal.context[0]]))
    assert action_and(goal,[goal.context[0]]) == ""
    assert action_exists(goal,[goal.context[0]]) == ""
    assert action_forall(goal,[goal.context[0]]) == ""
    
    
    hypo_analysis= ""
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.1868.30569]/pp_type: (∃ (n : ℕ), n = 2) → 5 = 5] ¿= PROP_IMPLIES¿(QUANT_∃¿(TYPE_NUMBER¿[name:ℕ¿]¿, LOCAL_CONSTANT¿[name:n/identifier:_fresh.1868.30938¿]¿(TYPE_NUMBER¿[name:ℕ¿]¿)¿, PROP_EQUAL¿(LOCAL_CONSTANT¿[name:n/identifier:_fresh.1868.30938¿]¿(TYPE_NUMBER¿[name:ℕ¿]¿)¿, NUMBER¿[2¿]¿)¿)¿, PROP_EQUAL¿(NUMBER¿[5¿]¿, NUMBER¿[5¿]¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST CONSTRUCT IMPLICATION -------------")
    print("retour de action_implicate : ", action_implicate(goal,[]))
    assert action_and(goal,[]) == ""
    assert action_exists(goal,[]) == ""
    assert action_forall(goal,[]) == ""
    
    hypo_analysis= """OBJECT[LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1979.53339¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
OBJECT[LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1979.53341¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE
PROPERTY[LOCAL_CONSTANT¿[name:H/identifier:0._fresh.1980.55522¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: A → B] ¿= PROP_IMPLIES¿(LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1979.53339¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1979.53341¿]¿(CONSTANT¿[name:1/1¿]¿)¿)
PROPERTY[LOCAL_CONSTANT¿[name:a/identifier:0._fresh.1980.55524¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: A] ¿= LOCAL_CONSTANT¿[name:A/identifier:0._fresh.1979.53339¿]¿(CONSTANT¿[name:1/1¿]¿)"""
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.1984.12632]/pp_type: B] ¿= LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1983.5124¿]¿(CONSTANT¿[name:1/1¿]¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST APPLY IMPLICATION -------------")
    print("retour de action_implicate : ", action_implicate(goal,[goal.context[2]]))
    assert action_and(goal,[goal.context[2]]) == ""
    assert action_exists(goal,[goal.context[2]]) == ""
    assert action_forall(goal,[goal.context[2]]) == ""
   
    hypo_analysis = """OBJECT[LOCAL_CONSTANT¿[name:a/identifier:0._fresh.2030.33679¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE_NUMBER¿[name:ℝ¿]
OBJECT[LOCAL_CONSTANT¿[name:b/identifier:0._fresh.2030.33681¿]¿(CONSTANT¿[name:1/1¿]¿)] ¿= TYPE_NUMBER¿[name:ℝ¿]
PROPERTY[LOCAL_CONSTANT¿[name:H/identifier:0._fresh.2031.31966¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: a = 0 → a = b] ¿= PROP_IMPLIES¿(PROP_EQUAL¿(LOCAL_CONSTANT¿[name:a/identifier:0._fresh.2030.33679¿]¿(CONSTANT¿[name:1/1¿]¿)¿, NUMBER¿[0¿]¿)¿, PROP_EQUAL¿(LOCAL_CONSTANT¿[name:a/identifier:0._fresh.2030.33679¿]¿(CONSTANT¿[name:1/1¿]¿)¿, LOCAL_CONSTANT¿[name:b/identifier:0._fresh.2030.33681¿]¿(CONSTANT¿[name:1/1¿]¿)¿)¿)
PROPERTY[LOCAL_CONSTANT¿[name:H2/identifier:0._fresh.2031.31968¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: a = 0] ¿= PROP_EQUAL¿(LOCAL_CONSTANT¿[name:a/identifier:0._fresh.2030.33679¿]¿(CONSTANT¿[name:1/1¿]¿)¿, NUMBER¿[0¿]¿)"""
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.1984.12632]/pp_type: B] ¿= LOCAL_CONSTANT¿[name:B/identifier:0._fresh.1983.5124¿]¿(CONSTANT¿[name:1/1¿]¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    print("------------- TEST APPLY IMPLICATION -------------")
    print("retour de action_implicate : ", action_implicate(goal,[goal.context[2], goal.context[3]]))
    assert action_and(goal,[goal.context[2]]) == ""
    assert action_exists(goal,[goal.context[2],]) == ""
    assert action_forall(goal,[goal.context[2],]) == ""
    
## TRASH

def test_format_with_type_as_utf8():
    hypo_analysis= """PROPERTY[LOCAL_CONSTANT¿[name:H/identifier:0._fresh.1851.36428¿]¿(CONSTANT¿[name:1/1¿]¿)/pp_type: ∃ (n : ℕ), n = 2] ¿= QUANT_∃¿(TYPE_NUMBER¿[name:ℕ¿]¿, LOCAL_CONSTANT¿[name:n/identifier:_fresh.1851.36430¿]¿(TYPE_NUMBER¿[name:ℕ¿]¿)¿, PROP_EQUAL¿(LOCAL_CONSTANT¿[name:n/identifier:_fresh.1851.36430¿]¿(TYPE_NUMBER¿[name:ℕ¿]¿)¿, NUMBER¿[2¿]¿)¿)"""
    
    goal_analysis = """PROPERTY[METAVAR[_mlocal._fresh.282.38692]/pp_type: 5 = 5 ∨ 6 = 0] ¿= PROP_OR¿(PROP_EQUAL¿(NUMBER¿[5¿]¿, NUMBER¿[5¿]¿)¿, PROP_EQUAL¿(NUMBER¿[6¿]¿, NUMBER¿[0¿]¿)¿)"""
    goal = Goal.from_lean_data(hypo_analysis, goal_analysis)
    #print("affichage : ", goal.target.format_with_type_as_utf8())
    for hyp in goal.context:
       print(hyp.format_with_type_as_utf8())
    
    
