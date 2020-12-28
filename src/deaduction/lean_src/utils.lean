import tactic


meta def tactic.interactive.no_meta_vars : tactic unit :=
mwhen (expr.has_meta_var <$> (tactic.target >>= tactic.instantiate_mvars)) $ tactic.fail "target contains metavars"


-- open tactic.interactive
-- example : ∃ x : ℕ, x = 0 :=
-- begin
--   existsi _,
--   no_meta_vars
-- end