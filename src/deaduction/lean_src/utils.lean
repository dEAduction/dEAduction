/- This file provides the no_meta_var tactics,
which checks that target or context contains no meta var.
Author: Frédéric Le Roux
-/


import tactic

------------------------------------------------
------------- tactic no_meta_vars --------------
------------------------------------------------
meta def tactic.interactive.generic_no_meta_vars (s: string) (e: expr) : tactic unit :=
mwhen (expr.has_meta_var <$> (tactic.instantiate_mvars e)) $ tactic.fail (s ++ " contains metavars")

/- target_no_meta_vars fails if the target contains metavars-/
meta def tactic.interactive.target_no_meta_vars : tactic unit :=
 tactic.target  >>= tactic.interactive.generic_no_meta_vars "target"

/- context_no_meta_vars fails if the local context contains metavars-/
meta def tactic.interactive.context_no_meta_vars : tactic (list unit) :=
do 
   context ← tactic.local_context,
   context_type ← context.mmap (λ h, tactic.infer_type h),
   context_type.mmap (λ h, tactic.interactive.generic_no_meta_vars "context" h)

/- no_meta_vars succeeds if all goals are accomplished, 
otherwise fails if there are metavariables either in the context or in the target-/
meta def tactic.interactive.no_meta_vars : tactic unit :=
do
   tactic.done <|> 
      `[ tactic.interactive.context_no_meta_vars,
         tactic.interactive.target_no_meta_vars ]
      

open interactive (parse)
open tactic
open lean.parser (ident)

/- -/
meta def tactic.interactive.no_meta_vars_test (id: parse ident): (tactic unit) :=
do e ← get_local id, et ← infer_type e,  trace et


------------------------------------------------
----------------- tactic todo ------------------
------------------------------------------------
axiom todo {p : Prop} : p

namespace tactic
namespace interactive

/--
An axiomatic alternative to `sorry`, used in formal roadmaps.
-/
meta def todo : tactic unit := `[exact todo]

end interactive
end tactic


-- Tests
-- open tactic.interactive
-- example : ∃ x : ℕ, x = 0 :=
-- begin
--    no_meta_vars,
--    existsi _,
--    context_no_meta_vars,
--    have H: 0=0,
--    {refl, trace "toto", no_meta_vars},
--    -- no_meta_vars,
--    sorry
-- end


-- example (H1 : ∀ x:ℕ, x=0) (y:ℕ) : y = 0 :=
-- begin
--    sorry
--    -- don't know how to produce metavars in context!
-- end