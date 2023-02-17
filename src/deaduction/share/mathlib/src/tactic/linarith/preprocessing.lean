/-
Copyright (c) 2020 Robert Y. Lewis. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Robert Y. Lewis
-/

import tactic.linarith.datatypes
import tactic.zify
import tactic.cancel_denoms

/-!
# Linarith preprocessing

This file contains methods used to preprocess inputs to `linarith`.

In particular, `linarith` works over comparisons of the form `t R 0`, where `R ∈ {<,≤,=}`.
It assumes that expressions in `t` have integer coefficients and that the type of `t` has
well-behaved subtraction.

## Implementation details

A `global_preprocessor` is a function `list expr → tactic(list expr)`. Users can add custom
preprocessing steps by adding them to the `linarith_config` object. `linarith.default_preprocessors`
is the main list, and generally none of these should be skipped unless you know what you're doing.
-/

open native tactic expr
namespace linarith

/-! ### Preprocessing -/

open tactic

set_option eqn_compiler.max_steps 50000

/--
If `prf` is a proof of `¬ e`, where `e` is a comparison,
`rem_neg prf e` flips the comparison in `e` and returns a proof.
For example, if `prf : ¬ a < b`, ``rem_neg prf `(a < b)`` returns a proof of `a ≥ b`.
-/
meta def rem_neg (prf : expr) : expr → tactic expr
| `(_ ≤ _) := mk_app ``lt_of_not_ge [prf]
| `(_ < _) := mk_app ``le_of_not_gt [prf]
| `(_ > _) := mk_app ``le_of_not_gt [prf]
| `(_ ≥ _) := mk_app ``lt_of_not_ge [prf]
| e := failed

private meta def rearr_comp_aux : expr → expr → tactic expr
| prf `(%%a ≤ 0) := return prf
| prf  `(%%a < 0) := return prf
| prf  `(%%a = 0) := return prf
| prf  `(%%a ≥ 0) := mk_app ``neg_nonpos_of_nonneg [prf]
| prf  `(%%a > 0) := mk_app `neg_neg_of_pos [prf]
| prf  `(0 ≥ %%a) := to_expr ``(id_rhs (%%a ≤ 0) %%prf)
| prf  `(0 > %%a) := to_expr ``(id_rhs (%%a < 0) %%prf)
| prf  `(0 = %%a) := mk_app `eq.symm [prf]
| prf  `(0 ≤ %%a) := mk_app ``neg_nonpos_of_nonneg [prf]
| prf  `(0 < %%a) := mk_app `neg_neg_of_pos [prf]
| prf  `(%%a ≤ %%b) := mk_app ``sub_nonpos_of_le [prf]
| prf  `(%%a < %%b) := mk_app `sub_neg_of_lt [prf]
| prf  `(%%a = %%b) := mk_app `sub_eq_zero_of_eq [prf]
| prf  `(%%a > %%b) := mk_app `sub_neg_of_lt [prf]
| prf  `(%%a ≥ %%b) := mk_app ``sub_nonpos_of_le [prf]
| prf  `(¬ %%t) := do nprf ← rem_neg prf t, tp ← infer_type nprf, rearr_comp_aux nprf tp
| prf  a := trace a >> fail "couldn't rearrange comp"

/--
`rearr_comp e` takes a proof `e` of an equality, inequality, or negation thereof,
and turns it into a proof of a comparison `_ R 0`, where `R ∈ {=, ≤, <}`.
 -/
meta def rearr_comp (e : expr) : tactic expr :=
infer_type e >>= rearr_comp_aux e

/-- If `e` is of the form `((n : ℕ) : ℤ)`, `is_nat_int_coe e` returns `n : ℕ`. -/
meta def is_nat_int_coe : expr → option expr
| `((↑(%%n : ℕ) : ℤ)) := some n
| _ := none

/-- If `e : ℕ`, returns a proof of `0 ≤ (e : ℤ)`. -/
meta def mk_coe_nat_nonneg_prf (e : expr) : tactic expr :=
mk_app `int.coe_nat_nonneg [e]

/-- `get_nat_comps e` returns a list of all subexpressions of `e` of the form `((t : ℕ) : ℤ)`. -/
meta def get_nat_comps : expr → list expr
| `(%%a + %%b) := (get_nat_comps a).append (get_nat_comps b)
| `(%%a * %%b) := (get_nat_comps a).append (get_nat_comps b)
| e := match is_nat_int_coe e with
  | some e' := [e']
  | none := []
  end

/--
`mk_coe_nat_nonneg_prfs e` returns a list of proofs of the form `0 ≤ ((t : ℕ) : ℤ)`
for each subexpression of `e` of the form `((t : ℕ) : ℤ)`.
-/
meta def mk_coe_nat_nonneg_prfs (e : expr) : tactic (list expr) :=
(get_nat_comps e).mmap mk_coe_nat_nonneg_prf

/--
If `pf` is a proof of a comparison over `ℕ`, `mk_int_pfs_of_nat_pf pf` returns a proof of the
corresponding inequality over `ℤ`, using `tactic.zify_proof`, along with proofs that the cast
naturals are nonnegative.
-/
meta def mk_int_pfs_of_nat_pf (pf : expr) : tactic (list expr) :=
do pf' ← zify_proof [] pf,
   (a, b) ← infer_type pf' >>= get_rel_sides,
   list.cons pf' <$> ((++) <$> mk_coe_nat_nonneg_prfs a <*> mk_coe_nat_nonneg_prfs b)

/--
If `pf` is a proof of a strict inequality `(a : ℤ) < b`,
`mk_non_strict_int_pf_of_strict_int_pf pf` returns a proof of `a + 1 ≤ b`,
and similarly if `pf` proves a negated weak inequality.
-/
meta def mk_non_strict_int_pf_of_strict_int_pf (pf : expr) : tactic expr :=
do tp ← infer_type pf,
match tp with
| `(%%a < %%b) := to_expr ``(id_rhs (%%a + 1 ≤ %%b) %%pf)
| `(%%a > %%b) := to_expr ``(id_rhs (%%b + 1 ≤ %%a) %%pf)
| `(¬ %%a ≤ %%b) := to_expr ``(id_rhs (%%b + 1 ≤ %%a) %%pf)
| `(¬ %%a ≥ %%b) := to_expr ``(id_rhs (%%a + 1 ≤ %%b) %%pf)
| _ := fail "mk_non_strict_int_pf_of_strict_int_pf failed: proof is not an inequality"
end

/--
`is_nat_prop tp` is true iff `tp` is an inequality or equality between natural numbers
or the negation thereof.
-/
meta def is_nat_prop : expr → bool
| `(@eq ℕ %%_ _) := tt
| `(@has_le.le ℕ %%_ _ _) := tt
| `(@has_lt.lt ℕ %%_ _ _) := tt
| `(@ge ℕ %%_ _ _) := tt
| `(@gt ℕ %%_ _ _) := tt
| `(¬ %%p) := is_nat_prop p
| _ := ff

/--
`is_strict_int_prop tp` is true iff `tp` is a strict inequality between integers
or the negation of a weak inequality between integers.
-/
meta def is_strict_int_prop : expr → bool
| `(@has_lt.lt ℤ %%_ _ _) := tt
| `(@gt ℤ %%_ _ _) := tt
| `(¬ @has_le.le ℤ %%_ _ _) := tt
| `(¬ @ge ℤ %%_ _ _) := tt
| _ := ff

private meta def filter_comparisons_aux : expr → bool
| `(¬ %%p) := p.app_symbol_in [`has_lt.lt, `has_le.le, `gt, `ge]
| tp := tp.app_symbol_in [`has_lt.lt, `has_le.le, `gt, `ge, `eq]

/--
Removes any expressions that are not proofs of inequalities, equalities, or negations thereof.
-/
meta def filter_comparisons : preprocessor :=
{ name := "filter terms that are not proofs of comparisons",
  transform := λ h,
(do tp ← infer_type h,
   is_prop tp >>= guardb,
   guardb (filter_comparisons_aux tp),
   return [h])
<|> return [] }

/--
Replaces proofs of negations of comparisons with proofs of the reversed comparisons.
For example, a proof of `¬ a < b` will become a proof of `a ≥ b`.
-/
meta def remove_negations : preprocessor :=
{ name := "replace negations of comparisons",
  transform := λ h,
do tp ← infer_type h,
match tp with
| `(¬ %%p) := singleton <$> rem_neg h p
| _ := return [h]
end }

/--
If `h` is an equality or inequality between natural numbers,
`nat_to_int h` lifts this inequality to the integers,
adding the facts that the integers involved are nonnegative.
 -/
meta def nat_to_int : preprocessor :=
{ name := "move nats to ints",
  transform := λ h,
do tp ← infer_type h,
   guardb (is_nat_prop tp) >> mk_int_pfs_of_nat_pf h <|> return [h] }

/-- `strengthen_strict_int h` turns a proof `h` of a strict integer inequality `t1 < t2`
into a proof of `t1 ≤ t2 + 1`. -/
meta def strengthen_strict_int : preprocessor :=
{ name := "strengthen strict inequalities over int",
  transform := λ h,
do tp ← infer_type h,
   guardb (is_strict_int_prop tp) >> singleton <$> mk_non_strict_int_pf_of_strict_int_pf h
     <|> return [h] }

/--
`mk_comp_with_zero h` takes a proof `h` of an equality, inequality, or negation thereof,
and turns it into a proof of a comparison `_ R 0`, where `R ∈ {=, ≤, <}`.
 -/
meta def make_comp_with_zero : preprocessor :=
{ name := "make comparisons with zero",
  transform := λ e, singleton <$> rearr_comp e <|> return [] }

/--
`normalize_denominators_in_lhs h lhs` assumes that `h` is a proof of `lhs R 0`.
It creates a proof of `lhs' R 0`, where all numeric division in `lhs` has been cancelled.
-/
meta def normalize_denominators_in_lhs (h lhs : expr) : tactic expr :=
do (v, lhs') ← cancel_factors.derive lhs,
   if v = 1 then return h else do
   (ih, h'') ← mk_single_comp_zero_pf v h,
   (_, nep, _) ← infer_type h'' >>= rewrite_core lhs',
   mk_eq_mp nep h''

/--
`cancel_denoms pf` assumes `pf` is a proof of `t R 0`. If `t` contains the division symbol `/`,
it tries to scale `t` to cancel out division by numerals.
-/
meta def cancel_denoms : preprocessor :=
{ name := "cancel denominators",
  transform := λ pf,
(do some (_, lhs) ← parse_into_comp_and_expr <$> infer_type pf,
   guardb $ lhs.contains_constant (= `has_div.div),
   singleton <$> normalize_denominators_in_lhs pf lhs)
<|> return [pf] }

/--
`find_squares m e` collects all terms of the form `a ^ 2` and `a * a` that appear in `e`
and adds them to the set `m`.
A pair `(a, tt)` is added to `m` when `a^2` appears in `e`, and `(a, ff)` is added to `m`
when `a*a` appears in `e`.  -/
meta def find_squares : rb_set (expr × bool) → expr → tactic (rb_set (expr × bool))
| s `(%%a ^ 2) := do s ← find_squares s a, return (s.insert (a, tt))
| s e@`(%%e1 * %%e2) := if e1 = e2 then do s ← find_squares s e1, return (s.insert (e1, ff)) else e.mfoldl find_squares s
| s e := e.mfoldl find_squares s

/--
`nlinarith_extras` is the preprocessor corresponding to the `nlinarith` tactic.

* For every term `t` such that `t^2` or `t*t` appears in the input, adds a proof of `t^2 ≥ 0`
  or `t*t ≥ 0`.
* For every pair of comparisons `t1 R1 0` and `t2 R2 0`, adds a proof of `t1*t2 R 0`.

This preprocessor is typically run last, after all inputs have been canonized.
-/
meta def nlinarith_extras : global_preprocessor :=
{ name := "nonlinear arithmetic extras",
  transform := λ ls,
do s ← ls.mfoldr (λ h s', infer_type h >>= find_squares s') mk_rb_set,
   new_es ← s.mfold ([] : list expr) $ λ ⟨e, is_sq⟩ new_es,
     (do p ← mk_app (if is_sq then ``pow_two_nonneg else ``mul_self_nonneg) [e],
      return $ p::new_es),
   new_es ← make_comp_with_zero.globalize.transform new_es,
   linarith_trace "nlinarith preprocessing found squares",
   linarith_trace s,
   linarith_trace_proofs "so we added proofs" new_es,
   with_comps ← (new_es ++ ls).mmap (λ e, do
     tp ← infer_type e,
     return $ (parse_into_comp_and_expr tp).elim (ineq.lt, e) (λ ⟨ine, _⟩, (ine, e))),
   products ← with_comps.mmap_upper_triangle $ λ ⟨posa, a⟩ ⟨posb, b⟩,
     some <$> match posa, posb with
      | ineq.eq, _ := mk_app ``zero_mul_eq [a, b]
      | _, ineq.eq := mk_app ``mul_zero_eq [a, b]
      | ineq.lt, ineq.lt := mk_app ``mul_pos_of_neg_of_neg [a, b]
      | ineq.lt, ineq.le := do a ← mk_app ``le_of_lt [a], mk_app ``mul_nonneg_of_nonpos_of_nonpos [a, b]
      | ineq.le, ineq.lt := do b ← mk_app ``le_of_lt [b], mk_app ``mul_nonneg_of_nonpos_of_nonpos [a, b]
      | ineq.le, ineq.le := mk_app ``mul_nonneg_of_nonpos_of_nonpos [a, b]
      end <|> return none,
   products ← make_comp_with_zero.globalize.transform products.reduce_option,
   return $ new_es ++ ls ++ products }

/--
The default list of preprocessors, in the order they should typically run.
-/
meta def default_preprocessors : list global_preprocessor :=
[filter_comparisons, remove_negations, nat_to_int, strengthen_strict_int,
  make_comp_with_zero, cancel_denoms]

/--
`preprocess pps l` takes a list `l` of proofs of propositions.
It maps each preprocessor `pp ∈ pps` over this list.
The preprocessors are run sequentially: each recieves the output of the previous one.
Note that a preprocessor produces a `list expr` for each input `expr`,
so the size of the list may change.
-/
meta def preprocess (pps : list global_preprocessor) (l : list expr) : tactic (list expr) :=
pps.mfoldl (λ l' pp, pp.process l') l


end linarith
