from pprint import pprint
from deaduction.pylib.actions.logic import *

if __name__ == "__main__":
    logger.configure()
    log = logging.getLogger("test action logiques")
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
    #pprint(goal.context)
    goal.update(hypo_analysis_new)
    #print("New context: ")
    #pprint(goal.context)

    #print("variables: ")
    #pprint(goal.extract_var_names())
    log.info("retour de and : " + action_and(goal,[]))
    log.info("retour de or : " + action_or(goal,[]))
    log.info("retour de exists : " + action_exists(goal,[]))
    log.info("retour de assumption : " + action_assumption(goal,[]))
    log.info("retour de forall : " + action_forall(goal, []))
