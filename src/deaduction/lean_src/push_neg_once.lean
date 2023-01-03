/-
Copyright (c) 2019 Patrick Massot All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Patrick Massot, Simon Hudon

A tactic pushing negations into an expression
-/

/-
Slight modification by Justin Carel: variation of push_neg that only pushes once.
-/

import logic.basic
import tactic.push_neg
open tactic expr

namespace push_neg_once

-- theorem not_iff_eq (P Q : Prop) : ¬ (P ↔ Q) = (¬ (P → Q) ∨ ¬ (Q → P))
--  := 
-- begin
--   sorry
-- --  rw not_and_distrib,
-- --  (not_and_distrib (iff_def P Q))
-- end

section redef
open push_neg -- we don't want to pollute the namespace outside of this definition

-- this is private in push_neg for some reason, so we have to redefine it here
meta def transform_negation_step (e : expr) :
  tactic (option (expr × expr)) :=
do e ← whnf_reducible e,
   match e with
   | `(¬ %%ne) :=
      (do ne ← whnf_reducible ne,
      match ne with
      -- | `(%%a ↔ %%b)  := do e ← to_expr ``(¬ (%%a → %%b) ∨ ¬ (%%b → %%a)),
      --                       pr ← mk_app ``not_iff_eq [a, b],
      --                       return $ some (e, pr)
      | `(¬ %%a)      := do pr ← mk_app ``not_not_eq [a],
                            return $ some (a, pr)
      | `(%%a ∧ %%b)  := do pr ← mk_app ``not_and_eq [a, b],
                            return (some (`(¬ %%a ∨ ¬ %%b), pr))
      | `(%%a ∨ %%b)  := do pr ← mk_app ``not_or_eq [a, b],
                            return $ some (`(¬ %%a ∧ ¬ %%b), pr)
      | `(%%a ≤ %%b)  := do e ← to_expr ``(%%b < %%a),
                            pr ← mk_app ``not_le_eq [a, b],
                            return $ some (e, pr)
      | `(%%a < %%b)  := do e ← to_expr ``(%%b ≤ %%a),
                            pr ← mk_app ``not_lt_eq [a, b],
                            return $ some (e, pr)
      | `(Exists %%p) := do pr ← mk_app ``not_exists_eq [p],
                            e ← match p with
                                | (lam n bi typ bo) := do
                                    body ← mk_app ``not [bo],
                                    return (pi n bi typ body)
                                | _ := tactic.fail "Unexpected failure negating ∃"
                                end,
                            return $ some (e, pr)
      | (pi n bi d p) := if p.has_var then do
                            pr ← mk_app ``not_forall_eq [lam n bi d p],
                            body ← mk_app ``not [p],
                            e ←  mk_app ``Exists [lam n bi d body],
                            return $ some (e, pr)
                         else do
                            pr ← mk_app ``not_implies_eq [d, p],
                            `(%%_ = %%e') ← infer_type pr,
                            return $ some (e', pr)
      | _             := return none
      end)
    | _        := return none
  end

-- this is private in push_neg for some reason, so we have to redefine it here
meta def transform_negation : expr → tactic (option (expr × expr))
| e :=
do some (e',  pr)  ← transform_negation_step e | return none,
   some (e'', pr') ← transform_negation e' | return $ some (e', pr),
   pr'' ← mk_eq_trans pr pr',
   return $ some (e'', pr'')

end redef

/--
simplify_top_down but without guard against unchanged expressions.
This is necessary, otherwise the user state doesn't update when the proof is by refl.
-/
meta def simplify_top_down' {α} (a : α) (pre : α → expr → tactic (α × expr × expr)) (e : expr) (cfg : simp_config := {}) : tactic (α × expr × expr) :=
ext_simplify_core a cfg simp_lemmas.mk (λ _, failed)
  (λ a _ _ _ e, do (new_a, new_e, pr) ← pre a e, return (new_a, new_e, some pr, tt))
  (λ _ _ _ _ _, failed)
  `eq e

/--
Recursively searches all negations in top down order and pushes the n-th found.
Returns `(e, pr)`, where `e` is the new expression and `pr` is a proof that `old = e`
-/
meta def transform_nth_negation (t : expr) (n : ℕ) : tactic (expr × expr) :=
do (_, e, pr) ← simplify_top_down' (ff, n-1)
                    (λ s e, do
                        pr ← mk_eq_refl e,
                        match s with
                        | (tt, _) := failure  -- already transformed
                        | (ff, 0) := do       -- ready to transform
                            oepr ← transform_negation e,
                            match oepr with
                            | some (e, pr) := return ((tt, 0), e, pr)
                            | none         := return ((ff, 0), e, pr)
                            end
                        | (ff, nat.succ m) := -- encountered less than n-1 negations
                            match e with
                            | `(¬ %%ne) := return ((ff, m), e, pr)
                            | _         := return ((ff, m+1), e, pr)
                            end
                        end)
                    t { eta := ff, single_pass := tt },
   return (e, pr)

meta def push_neg_once_at_hyp (n : ℕ) (h : name) : tactic unit :=
do H ← get_local h,
   t ← infer_type H,
   (e, pr) ← transform_nth_negation t n,
   replace_hyp H e pr,
   skip

meta def push_neg_once_at_goal (n : ℕ) : tactic unit :=
do t ← target,
   (e, pr) ← transform_nth_negation t n,
   replace_target e pr

end push_neg_once

open interactive (parse loc.ns loc.wildcard)
open interactive.types (location)
open lean.parser (small_nat)
open push_neg_once
local postfix `?`:9001 := optional

/--
Variation on push_neg that only pushes the nth negation, once.

Usage:
```
-- push the nth negation at the goal
push_neg_once n
-- push the nth negation at the hypothesis h
push_neg_once n at h
-- push the first negation at the goal and all hypotheses
push_neg_once at *
```
-/
meta def tactic.interactive.push_neg_once : parse small_nat? → parse location → tactic unit
| none l := tactic.interactive.push_neg_once (some 1) l
| (some n) (loc.ns loc_l) :=
  loc_l.mmap' $ λl,
      (match l with
      | some h := do push_neg_once_at_hyp n h,
                     try $ interactive.simp_core { eta := ff } failed tt
                            [simp_arg_type.expr ``(push_neg.not_eq)] []
                            (loc.ns [some h])
      | none   := do push_neg_once_at_goal n,
                     try `[simp only [push_neg.not_eq] { eta := ff }]
      end)
| (some n) loc.wildcard := do
    push_neg_once_at_goal n,
    local_context >>= mmap' (push_neg_once_at_hyp n ∘ local_pp_name),
    try `[simp only [push_neg.not_eq] at * { eta := ff }]

add_tactic_doc
{ name       := "push_neg_once",
  category   := doc_category.tactic,
  decl_names := [`tactic.interactive.push_neg_once],
  tags       := ["logic"] }
