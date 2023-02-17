/-
Copyright (c) 2017 Simon Hudon All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Simon Hudon, Mario Carneiro
-/
import data.rat.cast
import data.rat.meta_defs
import tactic.doc_commands

/-!
# `norm_num`

Evaluating arithmetic expressions including *, +, -, ^, ≤
-/

universes u v w

namespace tactic

/-- Reflexivity conversion: given `e` returns `(e, ⊢ e = e)` -/
meta def refl_conv (e : expr) : tactic (expr × expr) :=
do p ← mk_eq_refl e, return (e, p)

/-- Transitivity conversion: given two conversions (which take an
expression `e` and returns `(e', ⊢ e = e')`), produces another
conversion that combines them with transitivity, treating failures
as reflexivity conversions. -/
meta def trans_conv (t₁ t₂ : expr → tactic (expr × expr)) (e : expr) :
  tactic (expr × expr) :=
(do (e₁, p₁) ← t₁ e,
  (do (e₂, p₂) ← t₂ e₁,
    p ← mk_eq_trans p₁ p₂, return (e₂, p)) <|>
  return (e₁, p₁)) <|> t₂ e

namespace instance_cache

/-- Faster version of `mk_app ``bit0 [e]`. -/
meta def mk_bit0 (c : instance_cache) (e : expr) : tactic (instance_cache × expr) :=
do (c, ai) ← c.get ``has_add,
   return (c, (expr.const ``bit0 [c.univ]).mk_app [c.α, ai, e])

/-- Faster version of `mk_app ``bit1 [e]`. -/
meta def mk_bit1 (c : instance_cache) (e : expr) : tactic (instance_cache × expr) :=
do (c, ai) ← c.get ``has_add,
   (c, oi) ← c.get ``has_one,
   return (c, (expr.const ``bit1 [c.univ]).mk_app [c.α, oi, ai, e])

end instance_cache

end tactic

open tactic

namespace norm_num
variable {α : Type u}

lemma subst_into_add {α} [has_add α] (l r tl tr t)
  (prl : (l : α) = tl) (prr : r = tr) (prt : tl + tr = t) : l + r = t :=
by rw [prl, prr, prt]

lemma subst_into_mul {α} [has_mul α] (l r tl tr t)
  (prl : (l : α) = tl) (prr : r = tr) (prt : tl * tr = t) : l * r = t :=
by rw [prl, prr, prt]

lemma subst_into_neg {α} [has_neg α] (a ta t : α) (pra : a = ta) (prt : -ta = t) : -a = t :=
by simp [pra, prt]

/-- The result type of `match_numeral`, either `0`, `1`, or a top level
decomposition of `bit0 e` or `bit1 e`. The `other` case means it is not a numeral. -/
meta inductive match_numeral_result
| zero | one | bit0 (e : expr) | bit1 (e : expr) | other

/-- Unfold the top level constructor of the numeral expression. -/
meta def match_numeral : expr → match_numeral_result
| `(bit0 %%e) := match_numeral_result.bit0 e
| `(bit1 %%e) := match_numeral_result.bit1 e
| `(@has_zero.zero _ _) := match_numeral_result.zero
| `(@has_one.one _ _) := match_numeral_result.one
| _ := match_numeral_result.other

theorem zero_succ {α} [semiring α] : (0 + 1 : α) = 1 := zero_add _
theorem one_succ {α} [semiring α] : (1 + 1 : α) = 2 := rfl
theorem bit0_succ {α} [semiring α] (a : α) : bit0 a + 1 = bit1 a := rfl
theorem bit1_succ {α} [semiring α] (a b : α) (h : a + 1 = b) : bit1 a + 1 = bit0 b :=
h ▸ by simp [bit1, bit0, add_left_comm, add_assoc]

section
open match_numeral_result

/-- Given `a`, `b` natural numerals, proves `⊢ a + 1 = b`, assuming that this is provable.
(It may prove garbage instead of failing if `a + 1 = b` is false.) -/
meta def prove_succ : instance_cache → expr → expr → tactic (instance_cache × expr)
| c e r := match match_numeral e with
  | zero := c.mk_app ``zero_succ []
  | one := c.mk_app ``one_succ []
  | bit0 e := c.mk_app ``bit0_succ [e]
  | bit1 e := do
    let r := r.app_arg,
    (c, p) ← prove_succ c e r,
    c.mk_app ``bit1_succ [e, r, p]
  | _ := failed
  end
end

theorem zero_adc {α} [semiring α] (a b : α) (h : a + 1 = b) : 0 + a + 1 = b := by rwa zero_add
theorem adc_zero {α} [semiring α] (a b : α) (h : a + 1 = b) : a + 0 + 1 = b := by rwa add_zero
theorem one_add {α} [semiring α] (a b : α) (h : a + 1 = b) : 1 + a = b := by rwa add_comm
theorem add_bit0_bit0 {α} [semiring α] (a b c : α) (h : a + b = c) : bit0 a + bit0 b = bit0 c :=
h ▸ by simp [bit0, add_left_comm, add_assoc]
theorem add_bit0_bit1 {α} [semiring α] (a b c : α) (h : a + b = c) : bit0 a + bit1 b = bit1 c :=
h ▸ by simp [bit0, bit1, add_left_comm, add_assoc]
theorem add_bit1_bit0 {α} [semiring α] (a b c : α) (h : a + b = c) : bit1 a + bit0 b = bit1 c :=
h ▸ by simp [bit0, bit1, add_left_comm, add_comm]
theorem add_bit1_bit1 {α} [semiring α] (a b c : α) (h : a + b + 1 = c) : bit1 a + bit1 b = bit0 c :=
h ▸ by simp [bit0, bit1, add_left_comm, add_comm]
theorem adc_one_one {α} [semiring α] : (1 + 1 + 1 : α) = 3 := rfl
theorem adc_bit0_one {α} [semiring α] (a b : α) (h : a + 1 = b) : bit0 a + 1 + 1 = bit0 b :=
h ▸ by simp [bit0, add_left_comm, add_assoc]
theorem adc_one_bit0 {α} [semiring α] (a b : α) (h : a + 1 = b) : 1 + bit0 a + 1 = bit0 b :=
h ▸ by simp [bit0, add_left_comm, add_assoc]
theorem adc_bit1_one {α} [semiring α] (a b : α) (h : a + 1 = b) : bit1 a + 1 + 1 = bit1 b :=
h ▸ by simp [bit1, bit0, add_left_comm, add_assoc]
theorem adc_one_bit1 {α} [semiring α] (a b : α) (h : a + 1 = b) : 1 + bit1 a + 1 = bit1 b :=
h ▸ by simp [bit1, bit0, add_left_comm, add_assoc]
theorem adc_bit0_bit0 {α} [semiring α] (a b c : α) (h : a + b = c) : bit0 a + bit0 b + 1 = bit1 c :=
h ▸ by simp [bit1, bit0, add_left_comm, add_assoc]
theorem adc_bit1_bit0 {α} [semiring α] (a b c : α) (h : a + b + 1 = c) : bit1 a + bit0 b + 1 = bit0 c :=
h ▸ by simp [bit1, bit0, add_left_comm, add_assoc]
theorem adc_bit0_bit1 {α} [semiring α] (a b c : α) (h : a + b + 1 = c) : bit0 a + bit1 b + 1 = bit0 c :=
h ▸ by simp [bit1, bit0, add_left_comm, add_assoc]
theorem adc_bit1_bit1 {α} [semiring α] (a b c : α) (h : a + b + 1 = c) : bit1 a + bit1 b + 1 = bit1 c :=
h ▸ by simp [bit1, bit0, add_left_comm, add_assoc]

section
open match_numeral_result

meta mutual def prove_add_nat, prove_adc_nat
with prove_add_nat : instance_cache → expr → expr → expr → tactic (instance_cache × expr)
| c a b r := do
  match match_numeral a, match_numeral b with
  | zero, _ := c.mk_app ``zero_add [b]
  | _, zero := c.mk_app ``add_zero [a]
  | _, one := prove_succ c a r
  | one, _ := do (c, p) ← prove_succ c b r, c.mk_app ``one_add [b, r, p]
  | bit0 a, bit0 b := do let r := r.app_arg, (c, p) ← prove_add_nat c a b r, c.mk_app ``add_bit0_bit0 [a, b, r, p]
  | bit0 a, bit1 b := do let r := r.app_arg, (c, p) ← prove_add_nat c a b r, c.mk_app ``add_bit0_bit1 [a, b, r, p]
  | bit1 a, bit0 b := do let r := r.app_arg, (c, p) ← prove_add_nat c a b r, c.mk_app ``add_bit1_bit0 [a, b, r, p]
  | bit1 a, bit1 b := do let r := r.app_arg, (c, p) ← prove_adc_nat c a b r, c.mk_app ``add_bit1_bit1 [a, b, r, p]
  | _, _ := failed
  end
with prove_adc_nat : instance_cache → expr → expr → expr → tactic (instance_cache × expr)
| c a b r := do
  match match_numeral a, match_numeral b with
  | zero, _ := do (c, p) ← prove_succ c b r, c.mk_app ``zero_adc [b, r, p]
  | _, zero := do (c, p) ← prove_succ c b r, c.mk_app ``adc_zero [b, r, p]
  | one, one := c.mk_app ``adc_one_one []
  | bit0 a, one := do let r := r.app_arg, (c, p) ← prove_succ c a r, c.mk_app ``adc_bit0_one [a, r, p]
  | one, bit0 b := do let r := r.app_arg, (c, p) ← prove_succ c b r, c.mk_app ``adc_one_bit0 [b, r, p]
  | bit1 a, one := do let r := r.app_arg, (c, p) ← prove_succ c a r, c.mk_app ``adc_bit1_one [a, r, p]
  | one, bit1 b := do let r := r.app_arg, (c, p) ← prove_succ c b r, c.mk_app ``adc_one_bit1 [b, r, p]
  | bit0 a, bit0 b := do let r := r.app_arg, (c, p) ← prove_add_nat c a b r, c.mk_app ``adc_bit0_bit0 [a, b, r, p]
  | bit0 a, bit1 b := do let r := r.app_arg, (c, p) ← prove_adc_nat c a b r, c.mk_app ``adc_bit0_bit1 [a, b, r, p]
  | bit1 a, bit0 b := do let r := r.app_arg, (c, p) ← prove_adc_nat c a b r, c.mk_app ``adc_bit1_bit0 [a, b, r, p]
  | bit1 a, bit1 b := do let r := r.app_arg, (c, p) ← prove_adc_nat c a b r, c.mk_app ``adc_bit1_bit1 [a, b, r, p]
  | _, _ := failed
  end

/-- Given `a`,`b`,`r` natural numerals, proves `⊢ a + b = r`. -/
add_decl_doc prove_add_nat
/-- Given `a`,`b`,`r` natural numerals, proves `⊢ a + b + 1 = r`. -/
add_decl_doc prove_adc_nat

/-- Given `a`,`b` natural numerals, returns `(r, ⊢ a + b = r)`. -/
meta def prove_add_nat' (c : instance_cache) (a b : expr) : tactic (instance_cache × expr × expr) := do
  na ← a.to_nat,
  nb ← b.to_nat,
  (c, r) ← c.of_nat (na + nb),
  (c, p) ← prove_add_nat c a b r,
  return (c, r, p)

end

theorem bit0_mul {α} [semiring α] (a b c : α) (h : a * b = c) :
  bit0 a * b = bit0 c := h ▸ by simp [bit0, add_mul]
theorem mul_bit0' {α} [semiring α] (a b c : α) (h : a * b = c) :
  a * bit0 b = bit0 c := h ▸ by simp [bit0, mul_add]
theorem mul_bit0_bit0 {α} [semiring α] (a b c : α) (h : a * b = c) :
  bit0 a * bit0 b = bit0 (bit0 c) := bit0_mul _ _ _ (mul_bit0' _ _ _ h)
theorem mul_bit1_bit1 {α} [semiring α] (a b c d e : α)
  (hc : a * b = c) (hd : a + b = d) (he : bit0 c + d = e) :
  bit1 a * bit1 b = bit1 e :=
by rw [← he, ← hd, ← hc]; simp [bit1, bit0, mul_add, add_mul, add_left_comm, add_assoc]

section
open match_numeral_result

/-- Given `a`,`b` natural numerals, returns `(r, ⊢ a * b = r)`. -/
meta def prove_mul_nat : instance_cache → expr → expr → tactic (instance_cache × expr × expr)
| ic a b :=
  match match_numeral a, match_numeral b with
  | zero, _ := do
    (ic, z) ← ic.mk_app ``has_zero.zero [],
    (ic, p) ← ic.mk_app ``zero_mul [b],
    return (ic, z, p)
  | _, zero := do
    (ic, z) ← ic.mk_app ``has_zero.zero [],
    (ic, p) ← ic.mk_app ``mul_zero [a],
    return (ic, z, p)
  | one, _ := do (ic, p) ← ic.mk_app ``one_mul [b], return (ic, b, p)
  | _, one := do (ic, p) ← ic.mk_app ``mul_one [a], return (ic, a, p)
  | bit0 a, bit0 b := do
    (ic, c, p) ← prove_mul_nat ic a b,
    (ic, p) ← ic.mk_app ``mul_bit0_bit0 [a, b, c, p],
    (ic, c') ← ic.mk_bit0 c,
    (ic, c') ← ic.mk_bit0 c',
    return (ic, c', p)
  | bit0 a, _ := do
    (ic, c, p) ← prove_mul_nat ic a b,
    (ic, p) ← ic.mk_app ``bit0_mul [a, b, c, p],
    (ic, c') ← ic.mk_bit0 c,
    return (ic, c', p)
  | _, bit0 b := do
    (ic, c, p) ← prove_mul_nat ic a b,
    (ic, p) ← ic.mk_app ``mul_bit0' [a, b, c, p],
    (ic, c') ← ic.mk_bit0 c,
    return (ic, c', p)
  | bit1 a, bit1 b := do
    (ic, c, pc) ← prove_mul_nat ic a b,
    (ic, d, pd) ← prove_add_nat' ic a b,
    (ic, c') ← ic.mk_bit0 c,
    (ic, e, pe) ← prove_add_nat' ic c' d,
    (ic, p) ← ic.mk_app ``mul_bit1_bit1 [a, b, c, d, e, pc, pd, pe],
    (ic, e') ← ic.mk_bit1 e,
    return (ic, e', p)
  | _, _ := failed
  end

end

section
open match_numeral_result

/-- Given `a` a positive natural numeral, returns `⊢ 0 < a`. -/
meta def prove_pos_nat (c : instance_cache) : expr → tactic (instance_cache × expr)
| e :=
  match match_numeral e with
  | one := c.mk_app ``zero_lt_one []
  | bit0 e := do (c, p) ← prove_pos_nat e, c.mk_app ``bit0_pos [e, p]
  | bit1 e := do (c, p) ← prove_pos_nat e, c.mk_app ``bit1_pos' [e, p]
  | _ := failed
  end

end

/-- Given `a` a rational numeral, returns `⊢ 0 < a`. -/
meta def prove_pos (c : instance_cache) : expr → tactic (instance_cache × expr)
| `(%%e₁ / %%e₂) := do
  (c, p₁) ← prove_pos_nat c e₁, (c, p₂) ← prove_pos_nat c e₂,
  c.mk_app ``div_pos_of_pos_of_pos [e₁, e₂, p₁, p₂]
| e := prove_pos_nat c e

/-- `match_neg (- e) = some e`, otherwise `none` -/
meta def match_neg : expr → option expr
| `(- %%e) := some e
| _ := none

/-- `match_sign (- e) = inl e`, `match_sign 0 = inr ff`, otherwise `inr tt` -/
meta def match_sign : expr → expr ⊕ bool
| `(- %%e) := sum.inl e
| `(has_zero.zero) := sum.inr ff
| _ := sum.inr tt

theorem ne_zero_of_pos {α} [ordered_add_comm_group α] (a : α) : 0 < a → a ≠ 0 := ne_of_gt
theorem ne_zero_neg {α} [add_group α] (a : α) : a ≠ 0 → -a ≠ 0 := mt neg_eq_zero.1

/-- Given `a` a rational numeral, returns `⊢ a ≠ 0`. -/
meta def prove_ne_zero (c : instance_cache) : expr → tactic (instance_cache × expr)
| a :=
  match match_neg a with
  | some a := do (c, p) ← prove_ne_zero a, c.mk_app ``ne_zero_neg [a, p]
  | none := do (c, p) ← prove_pos c a, c.mk_app ``ne_zero_of_pos [a, p]
  end

theorem clear_denom_div {α} [division_ring α] (a b b' c d : α)
  (h₀ : b ≠ 0) (h₁ : b * b' = d) (h₂ : a * b' = c) : (a / b) * d = c :=
by rwa [← h₁, ← mul_assoc, div_mul_cancel _ h₀]

/-- Given `a` nonnegative rational and `d` a natural number, returns `(b, ⊢ a * d = b)`.
(`d` should be a multiple of the denominator of `a`, so that `b` is a natural number.) -/
meta def prove_clear_denom (c : instance_cache) (a d : expr) (na : ℚ) (nd : ℕ) : tactic (instance_cache × expr × expr) :=
if na.denom = 1 then
  prove_mul_nat c a d
else do
  [_, _, a, b] ← return a.get_app_args,
  (c, b') ← c.of_nat (nd / na.denom),
  (c, p₀) ← prove_ne_zero c b,
  (c, _, p₁) ← prove_mul_nat c b b',
  (c, r, p₂) ← prove_mul_nat c a b',
  (c, p) ← c.mk_app ``clear_denom_div [a, b, b', r, d, p₀, p₁, p₂],
  return (c, r, p)

theorem clear_denom_add {α} [division_ring α] (a a' b b' c c' d : α)
  (h₀ : d ≠ 0) (ha : a * d = a') (hb : b * d = b') (hc : c * d = c')
  (h : a' + b' = c') : a + b = c :=
mul_right_cancel' h₀ $ by rwa [add_mul, ha, hb, hc]

/-- Given `a`,`b`,`c` nonnegative rational numerals, returns `⊢ a + b = c`. -/
meta def prove_add_nonneg_rat (ic : instance_cache) (a b c : expr) (na nb nc : ℚ) : tactic (instance_cache × expr) :=
if na.denom = 1 ∧ nb.denom = 1 then
  prove_add_nat ic a b c
else do
  let nd := na.denom.lcm nb.denom,
  (ic, d) ← ic.of_nat nd,
  (ic, p₀) ← prove_ne_zero ic d,
  (ic, a', pa) ← prove_clear_denom ic a d na nd,
  (ic, b', pb) ← prove_clear_denom ic b d nb nd,
  (ic, c', pc) ← prove_clear_denom ic c d nc nd,
  (ic, p) ← prove_add_nat ic a' b' c',
  ic.mk_app ``clear_denom_add [a, a', b, b', c, c', d, p₀, pa, pb, pc, p]

theorem add_pos_neg_pos {α} [add_group α] (a b c : α) (h : c + b = a) : a + -b = c :=
h ▸ by simp
theorem add_pos_neg_neg {α} [add_group α] (a b c : α) (h : c + a = b) : a + -b = -c :=
h ▸ by simp
theorem add_neg_pos_pos {α} [add_group α] (a b c : α) (h : a + c = b) : -a + b = c :=
h ▸ by simp
theorem add_neg_pos_neg {α} [add_group α] (a b c : α) (h : b + c = a) : -a + b = -c :=
h ▸ by simp
theorem add_neg_neg {α} [add_group α] (a b c : α) (h : b + a = c) : -a + -b = -c :=
h ▸ by simp

/-- Given `a`,`b`,`c` rational numerals, returns `⊢ a + b = c`. -/
meta def prove_add_rat (ic : instance_cache) (ea eb ec : expr) (a b c : ℚ) : tactic (instance_cache × expr) :=
match match_neg ea, match_neg eb, match_neg ec with
| some ea, some eb, some ec := do
  (ic, p) ← prove_add_nonneg_rat ic eb ea ec (-b) (-a) (-c),
  ic.mk_app ``add_neg_neg [ea, eb, ec, p]
| some ea, none, some ec := do
  (ic, p) ← prove_add_nonneg_rat ic eb ec ea b (-c) (-a),
  ic.mk_app ``add_neg_pos_neg [ea, eb, ec, p]
| some ea, none, none := do
  (ic, p) ← prove_add_nonneg_rat ic ea ec eb (-a) c b,
  ic.mk_app ``add_neg_pos_pos [ea, eb, ec, p]
| none, some eb, some ec := do
  (ic, p) ← prove_add_nonneg_rat ic ec ea eb (-c) a (-b),
  ic.mk_app ``add_pos_neg_neg [ea, eb, ec, p]
| none, some eb, none := do
  (ic, p) ← prove_add_nonneg_rat ic ec eb ea c (-b) a,
  ic.mk_app ``add_pos_neg_pos [ea, eb, ec, p]
| _, _, _ := prove_add_nonneg_rat ic ea eb ec a b c
end

/-- Given `a`,`b` rational numerals, returns `(c, ⊢ a + b = c)`. -/
meta def prove_add_rat' (ic : instance_cache) (a b : expr) : tactic (instance_cache × expr × expr) := do
  na ← a.to_rat,
  nb ← b.to_rat,
  let nc := na + nb,
  (ic, c) ← ic.of_rat nc,
  (ic, p) ← prove_add_rat ic a b c na nb nc,
  return (ic, c, p)

theorem clear_denom_simple_nat {α} [division_ring α] (a : α) :
  (1:α) ≠ 0 ∧ a * 1 = a := ⟨one_ne_zero, mul_one _⟩
theorem clear_denom_simple_div {α} [division_ring α] (a b : α) (h : b ≠ 0) :
  b ≠ 0 ∧ a / b * b = a := ⟨h, div_mul_cancel _ h⟩

/-- Given `a` a nonnegative rational numeral, returns `(b, c, ⊢ a * b = c)`
where `b` and `c` are natural numerals. (`b` will be the denominator of `a`.) -/
meta def prove_clear_denom_simple (c : instance_cache) (a : expr) (na : ℚ) : tactic (instance_cache × expr × expr × expr) :=
if na.denom = 1 then do
  (c, d) ← c.mk_app ``has_one.one [],
  (c, p) ← c.mk_app ``clear_denom_simple_nat [a],
  return (c, d, a, p)
else do
  [α, _, a, b] ← return a.get_app_args,
  (c, p₀) ← prove_ne_zero c b,
  (c, p) ← c.mk_app ``clear_denom_simple_div [a, b, p₀],
  return (c, b, a, p)

theorem clear_denom_mul {α} [field α] (a a' b b' c c' d₁ d₂ d : α)
  (ha : d₁ ≠ 0 ∧ a * d₁ = a') (hb : d₂ ≠ 0 ∧ b * d₂ = b')
  (hc : c * d = c') (hd : d₁ * d₂ = d)
  (h : a' * b' = c') : a * b = c :=
mul_right_cancel' ha.1 $ mul_right_cancel' hb.1 $
by rw [mul_assoc c, hd, hc, ← h, ← ha.2, ← hb.2, ← mul_assoc, mul_right_comm a]

/-- Given `a`,`b` nonnegative rational numerals, returns `(c, ⊢ a * b = c)`. -/
meta def prove_mul_nonneg_rat (ic : instance_cache) (a b : expr) (na nb : ℚ) : tactic (instance_cache × expr × expr) :=
if na.denom = 1 ∧ nb.denom = 1 then
  prove_mul_nat ic a b
else do
  let nc := na * nb, (ic, c) ← ic.of_rat nc,
  (ic, d₁, a', pa) ← prove_clear_denom_simple ic a na,
  (ic, d₂, b', pb) ← prove_clear_denom_simple ic b nb,
  (ic, d, pd) ← prove_mul_nat ic d₁ d₂, nd ← d.to_nat,
  (ic, c', pc) ← prove_clear_denom ic c d nc nd,
  (ic, _, p) ← prove_mul_nat ic a' b',
  (ic, p) ← ic.mk_app ``clear_denom_mul [a, a', b, b', c, c', d₁, d₂, d, pa, pb, pc, pd, p],
  return (ic, c, p)

theorem mul_neg_pos {α} [ring α] (a b c : α) (h : a * b = c) : -a * b = -c := h ▸ by simp
theorem mul_pos_neg {α} [ring α] (a b c : α) (h : a * b = c) : a * -b = -c := h ▸ by simp
theorem mul_neg_neg {α} [ring α] (a b c : α) (h : a * b = c) : -a * -b = c := h ▸ by simp

/-- Given `a`,`b` rational numerals, returns `(c, ⊢ a * b = c)`. -/
meta def prove_mul_rat (ic : instance_cache) (a b : expr) (na nb : ℚ) : tactic (instance_cache × expr × expr) :=
match match_sign a, match_sign b with
| sum.inl a, sum.inl b := do
  (ic, c, p) ← prove_mul_nonneg_rat ic a b (-na) (-nb),
  (ic, p) ← ic.mk_app ``mul_neg_neg [a, b, c, p],
  return (ic, c, p)
| sum.inr ff, _ := do
  (ic, z) ← ic.mk_app ``has_zero.zero [],
  (ic, p) ← ic.mk_app ``zero_mul [b],
  return (ic, z, p)
| _, sum.inr ff := do
  (ic, z) ← ic.mk_app ``has_zero.zero [],
  (ic, p) ← ic.mk_app ``mul_zero [a],
  return (ic, z, p)
| sum.inl a, sum.inr tt := do
  (ic, c, p) ← prove_mul_nonneg_rat ic a b (-na) nb,
  (ic, p) ← ic.mk_app ``mul_neg_pos [a, b, c, p],
  (ic, c') ← ic.mk_app ``has_neg.neg [c],
  return (ic, c', p)
| sum.inr tt, sum.inl b := do
  (ic, c, p) ← prove_mul_nonneg_rat ic a b na (-nb),
  (ic, p) ← ic.mk_app ``mul_pos_neg [a, b, c, p],
  (ic, c') ← ic.mk_app ``has_neg.neg [c],
  return (ic, c', p)
| sum.inr tt, sum.inr tt := prove_mul_nonneg_rat ic a b na nb
end

theorem inv_neg {α} [division_ring α] (a b : α) (h : a⁻¹ = b) : (-a)⁻¹ = -b :=
h ▸ by simp only [inv_eq_one_div, one_div_neg_eq_neg_one_div]

theorem inv_one {α} [division_ring α] : (1 : α)⁻¹ = 1 := one_inv_eq
theorem inv_one_div {α} [division_ring α] (a : α) : (1 / a)⁻¹ = a :=
by rw [one_div_eq_inv, inv_inv']
theorem inv_div_one {α} [division_ring α] (a : α) : a⁻¹ = 1 / a :=
inv_eq_one_div _
theorem inv_div {α} [division_ring α] (a b : α) : (a / b)⁻¹ = b / a :=
by simp only [inv_eq_one_div, one_div_div]

/-- Given `a` a rational numeral, returns `(b, ⊢ a⁻¹ = b)`. -/
meta def prove_inv : instance_cache → expr → ℚ → tactic (instance_cache × expr × expr)
| ic e n :=
  match match_sign e with
  | sum.inl e := do
    (ic, e', p) ← prove_inv ic e (-n),
    (ic, r) ← ic.mk_app ``has_neg.neg [e'],
    (ic, p) ← ic.mk_app ``inv_neg [e, e', p],
    return (ic, r, p)
  | sum.inr ff := do
    (ic, p) ← ic.mk_app ``inv_zero [],
    return (ic, e, p)
  | sum.inr tt :=
    if n.num = 1 then
      if n.denom = 1 then do
        (ic, p) ← ic.mk_app ``one_inv_eq [],
        return (ic, e, p)
      else do
        let e := e.app_arg,
        (ic, p) ← ic.mk_app ``inv_one_div [e],
        return (ic, e, p)
    else if n.denom = 1 then do
      (ic, p) ← ic.mk_app ``inv_div_one [e],
      e ← infer_type p,
      return (ic, e.app_arg, p)
    else do
      [_, _, a, b] ← return e.get_app_args,
      (ic, e') ← ic.mk_app ``has_div.div [b, a],
      (ic, p) ← ic.mk_app ``inv_div [a, b],
      return (ic, e', p)
  end

theorem div_eq {α} [division_ring α] (a b b' c : α)
  (hb : b⁻¹ = b') (h : a * b' = c) : a / b = c := by rwa ← hb at h

/-- Given `a`,`b` rational numerals, returns `(c, ⊢ a / b = c)`. -/
meta def prove_div (ic : instance_cache) (a b : expr) (na nb : ℚ) : tactic (instance_cache × expr × expr) :=
do (ic, b', pb) ← prove_inv ic b nb,
  (ic, c, p) ← prove_mul_rat ic a b' na nb⁻¹,
  (ic, p) ← ic.mk_app ``div_eq [a, b, b', c, pb, p],
  return (ic, c, p)

/-- Given `a` a rational numeral, returns `(b, ⊢ -a = b)`. -/
meta def prove_neg (ic : instance_cache) (a : expr) : tactic (instance_cache × expr × expr) :=
match match_sign a with
| sum.inl a := do
  (ic, p) ← ic.mk_app ``neg_neg [a],
  return (ic, a, p)
| sum.inr ff := do
  (ic, p) ← ic.mk_app ``neg_zero [],
  return (ic, a, p)
| sum.inr tt := do
  (ic, a') ← ic.mk_app ``has_neg.neg [a],
  p ← mk_eq_refl a',
  return (ic, a', p)
end

theorem sub_pos {α} [add_group α] (a b b' c : α) (hb : -b = b') (h : a + b' = c) : a - b = c :=
by rwa ← hb at h
theorem sub_neg {α} [add_group α] (a b c : α) (h : a + b = c) : a - -b = c :=
by rwa sub_neg_eq_add

/-- Given `a`,`b` rational numerals, returns `(c, ⊢ a - b = c)`. -/
meta def prove_sub (ic : instance_cache) (a b : expr) : tactic (instance_cache × expr × expr) :=
match match_sign b with
| sum.inl b := do
  (ic, c, p) ← prove_add_rat' ic a b,
  (ic, p) ← ic.mk_app ``sub_neg [a, b, c, p],
  return (ic, c, p)
| sum.inr ff := do
  (ic, p) ← ic.mk_app ``sub_zero [a],
  return (ic, a, p)
| sum.inr tt := do
  (ic, b', pb) ← prove_neg ic b,
  (ic, c, p) ← prove_add_rat' ic a b',
  (ic, p) ← ic.mk_app ``sub_pos [a, b, b', c, pb, p],
  return (ic, c, p)
end

theorem sub_nat_pos (a b c : ℕ) (h : b + c = a) : a - b = c :=
h ▸ nat.add_sub_cancel_left _ _
theorem sub_nat_neg (a b c : ℕ) (h : a + c = b) : a - b = 0 :=
nat.sub_eq_zero_of_le $ h ▸ nat.le_add_right _ _

/-- Given `a : nat`,`b : nat` natural numerals, returns `(c, ⊢ a - b = c)`. -/
meta def prove_sub_nat (ic : instance_cache) (a b : expr) : tactic (expr × expr) :=
do na ← a.to_nat, nb ← b.to_nat,
  if nb ≤ na then do
    (ic, c) ← ic.of_nat (na - nb),
    (ic, p) ← prove_add_nat ic b c a,
    return (c, `(sub_nat_pos).mk_app [a, b, c, p])
  else do
    (ic, c) ← ic.of_nat (nb - na),
    (ic, p) ← prove_add_nat ic a c b,
    return (`(0 : ℕ), `(sub_nat_neg).mk_app [a, b, c, p])

/-- This is needed because when `a` and `b` are numerals lean is more likely to unfold them
than unfold the instances in order to prove that `add_group_has_sub = int.has_sub`. -/
theorem int_sub_hack (a b c : ℤ) (h : @has_sub.sub ℤ add_group_has_sub a b = c) : a - b = c := h

/-- Given `a : ℤ`, `b : ℤ` integral numerals, returns `(c, ⊢ a - b = c)`. -/
meta def prove_sub_int (ic : instance_cache) (a b : expr) : tactic (expr × expr) :=
do (_, c, p) ← prove_sub ic a b,
  return (c, `(int_sub_hack).mk_app [a, b, c, p])

/-- Evaluates the basic field operations `+`,`neg`,`-`,`*`,`inv`,`/` on numerals.
Also handles nat subtraction. Does not do recursive simplification; that is,
`1 + 1 + 1` will not simplify but `2 + 1` will. This is handled by the top level
`simp` call in `norm_num.derive`. -/
meta def eval_field : expr → tactic (expr × expr)
| `(%%e₁ + %%e₂) := do
  n₁ ← e₁.to_rat, n₂ ← e₂.to_rat,
  c ← infer_type e₁ >>= mk_instance_cache,
  let n₃ := n₁ + n₂,
  (c, e₃) ← c.of_rat n₃,
  (_, p) ← prove_add_rat c e₁ e₂ e₃ n₁ n₂ n₃,
  return (e₃, p)
| `(%%e₁ * %%e₂) := do
  n₁ ← e₁.to_rat, n₂ ← e₂.to_rat,
  c ← infer_type e₁ >>= mk_instance_cache,
  prod.snd <$> prove_mul_rat c e₁ e₂ n₁ n₂
| `(- %%e) := do
  c ← infer_type e >>= mk_instance_cache,
  prod.snd <$> prove_neg c e
| `(@has_sub.sub %%α %%inst %%a %%b) := do
  c ← mk_instance_cache α,
  if α = `(nat) then prove_sub_nat c a b
  else if inst = `(int.has_sub) then prove_sub_int c a b
  else prod.snd <$> prove_sub c a b
| `(has_inv.inv %%e) := do
  n ← e.to_rat,
  c ← infer_type e >>= mk_instance_cache,
  prod.snd <$> prove_inv c e n
| `(%%e₁ / %%e₂) := do
  n₁ ← e₁.to_rat, n₂ ← e₂.to_rat,
  c ← infer_type e₁ >>= mk_instance_cache,
  prod.snd <$> prove_div c e₁ e₂ n₁ n₂
| _ := failed

lemma pow_bit0 [monoid α] (a c' c : α) (b : ℕ)
  (h : a ^ b = c') (h₂ : c' * c' = c) : a ^ bit0 b = c :=
h₂ ▸ by simp [pow_bit0, h]

lemma pow_bit1 [monoid α] (a c₁ c₂ c : α) (b : ℕ)
  (h : a ^ b = c₁) (h₂ : c₁ * c₁ = c₂) (h₃ : c₂ * a = c) : a ^ bit1 b = c :=
by rw [← h₃, ← h₂]; simp [pow_bit1, h]

section
open match_numeral_result

/-- Given `a` a rational numeral and `b : nat`, returns `(c, ⊢ a ^ b = c)`. -/
meta def prove_pow (a : expr) (na : ℚ) : instance_cache → expr → tactic (instance_cache × expr × expr)
| ic b :=
  match match_numeral b with
  | zero := do
    (ic, p) ← ic.mk_app ``pow_zero [a],
    (ic, o) ← ic.mk_app ``has_one.one [],
    return (ic, o, p)
  | one := do
    (ic, p) ← ic.mk_app ``pow_one [a],
    return (ic, a, p)
  | bit0 b := do
    (ic, c', p) ← prove_pow ic b,
    nc' ← expr.to_rat c',
    (ic, c, p₂) ← prove_mul_rat ic c' c' nc' nc',
    (ic, p) ← ic.mk_app ``pow_bit0 [a, c', c, b, p, p₂],
    return (ic, c, p)
  | bit1 b := do
    (ic, c₁, p) ← prove_pow ic b,
    nc₁ ← expr.to_rat c₁,
    (ic, c₂, p₂) ← prove_mul_rat ic c₁ c₁ nc₁ nc₁,
    (ic, c, p₃) ← prove_mul_rat ic c₂ a (nc₁ * nc₁) na,
    (ic, p) ← ic.mk_app ``pow_bit1 [a, c₁, c₂, c, b, p, p₂, p₃],
    return (ic, c, p)
  | _ := failed
  end

end

lemma from_nat_pow (a b c : ℕ) (h : @has_pow.pow _ _ monoid.has_pow a b = c) : a ^ b = c :=
(nat.pow_eq_pow _ _).symm.trans h

/-- Evaluates expressions of the form `a ^ b`, `monoid.pow a b` or `nat.pow a b`. -/
meta def eval_pow : expr → tactic (expr × expr)
| `(@has_pow.pow %%α _ %%m %%e₁ %%e₂) := do
  n₁ ← e₁.to_rat,
  c ← infer_type e₁ >>= mk_instance_cache,
  match m with
  | `(@monoid.has_pow %%_ %%_) := prod.snd <$> prove_pow e₁ n₁ c e₂
  | `(nat.has_pow) := do
    (_, c, p) ← prove_pow e₁ n₁ c e₂,
    return (c, `(from_nat_pow).mk_app [e₁, e₂, c, p])
  | _ := failed
  end
| `(monoid.pow %%e₁ %%e₂) := do
  n₁ ← e₁.to_rat,
  c ← infer_type e₁ >>= mk_instance_cache,
  prod.snd <$> prove_pow e₁ n₁ c e₂
| `(nat.pow %%e₁ %%e₂) := do
  n₁ ← e₁.to_rat,
  c ← mk_instance_cache `(ℕ),
  (_, c, p) ← prove_pow e₁ n₁ c e₂,
  return (c, `(from_nat_pow).mk_app [e₁, e₂, c, p])
| _ := failed

theorem nonneg_pos {α} [ordered_cancel_add_comm_monoid α] (a : α) : 0 < a → 0 ≤ a := le_of_lt

theorem lt_one_bit0 {α} [linear_ordered_semiring α] (a : α) (h : 1 ≤ a) : 1 < bit0 a :=
lt_of_lt_of_le one_lt_two (bit0_le_bit0.2 h)
theorem lt_one_bit1 {α} [linear_ordered_semiring α] (a : α) (h : 0 < a) : 1 < bit1 a :=
one_lt_bit1.2 h
theorem lt_bit0_bit0 {α} [linear_ordered_semiring α] (a b : α) : a < b → bit0 a < bit0 b := bit0_lt_bit0.2
theorem lt_bit0_bit1 {α} [linear_ordered_semiring α] (a b : α) (h : a ≤ b) : bit0 a < bit1 b :=
lt_of_le_of_lt (bit0_le_bit0.2 h) (lt_add_one _)
theorem lt_bit1_bit0 {α} [linear_ordered_semiring α] (a b : α) (h : a + 1 ≤ b) : bit1 a < bit0 b :=
lt_of_lt_of_le (by simp [bit0, bit1, zero_lt_one, add_assoc]) (bit0_le_bit0.2 h)
theorem lt_bit1_bit1 {α} [linear_ordered_semiring α] (a b : α) : a < b → bit1 a < bit1 b := bit1_lt_bit1.2

theorem le_one_bit0 {α} [linear_ordered_semiring α] (a : α) (h : 1 ≤ a) : 1 ≤ bit0 a :=
le_of_lt (lt_one_bit0 _ h)
-- deliberately strong hypothesis because bit1 0 is not a numeral
theorem le_one_bit1 {α} [linear_ordered_semiring α] (a : α) (h : 0 < a) : 1 ≤ bit1 a :=
le_of_lt (lt_one_bit1 _ h)
theorem le_bit0_bit0 {α} [linear_ordered_semiring α] (a b : α) : a ≤ b → bit0 a ≤ bit0 b := bit0_le_bit0.2
theorem le_bit0_bit1 {α} [linear_ordered_semiring α] (a b : α) (h : a ≤ b) : bit0 a ≤ bit1 b :=
le_of_lt (lt_bit0_bit1 _ _ h)
theorem le_bit1_bit0 {α} [linear_ordered_semiring α] (a b : α) (h : a + 1 ≤ b) : bit1 a ≤ bit0 b :=
le_of_lt (lt_bit1_bit0 _ _ h)
theorem le_bit1_bit1 {α} [linear_ordered_semiring α] (a b : α) : a ≤ b → bit1 a ≤ bit1 b := bit1_le_bit1.2

theorem sle_one_bit0 {α} [linear_ordered_semiring α] (a : α) : 1 ≤ a → 1 + 1 ≤ bit0 a := bit0_le_bit0.2
theorem sle_one_bit1 {α} [linear_ordered_semiring α] (a : α) : 1 ≤ a → 1 + 1 ≤ bit1 a := le_bit0_bit1 _ _
theorem sle_bit0_bit0 {α} [linear_ordered_semiring α] (a b : α) : a + 1 ≤ b → bit0 a + 1 ≤ bit0 b := le_bit1_bit0 _ _
theorem sle_bit0_bit1 {α} [linear_ordered_semiring α] (a b : α) (h : a ≤ b) : bit0 a + 1 ≤ bit1 b := bit1_le_bit1.2 h
theorem sle_bit1_bit0 {α} [linear_ordered_semiring α] (a b : α) (h : a + 1 ≤ b) : bit1 a + 1 ≤ bit0 b :=
(bit1_succ a _ rfl).symm ▸ bit0_le_bit0.2 h
theorem sle_bit1_bit1 {α} [linear_ordered_semiring α] (a b : α) (h : a + 1 ≤ b) : bit1 a + 1 ≤ bit1 b :=
(bit1_succ a _ rfl).symm ▸ le_bit0_bit1 _ _ h

/-- Given `a` a rational numeral, returns `⊢ 0 ≤ a`. -/
meta def prove_nonneg (ic : instance_cache) : expr → tactic (instance_cache × expr)
| e@`(has_zero.zero) := ic.mk_app ``le_refl [e]
| e :=
  if ic.α = `(ℕ) then
    return (ic, `(nat.zero_le).mk_app [e])
  else do
    (ic, p) ← prove_pos ic e,
    ic.mk_app ``nonneg_pos [e, p]

section
open match_numeral_result

/-- Given `a` a rational numeral, returns `⊢ 1 ≤ a`. -/
meta def prove_one_le_nat (ic : instance_cache) : expr → tactic (instance_cache × expr)
| a :=
  match match_numeral a with
  | one := ic.mk_app ``le_refl [a]
  | bit0 a := do (ic, p) ← prove_one_le_nat a, ic.mk_app ``le_one_bit0 [a, p]
  | bit1 a := do (ic, p) ← prove_pos_nat ic a, ic.mk_app ``le_one_bit1 [a, p]
  | _ := failed
  end

meta mutual def prove_le_nat, prove_sle_nat (ic : instance_cache)
with prove_le_nat : expr → expr → tactic (instance_cache × expr)
| a b :=
  if a = b then ic.mk_app ``le_refl [a] else
  match match_numeral a, match_numeral b with
  | zero, _ := prove_nonneg ic b
  | one, bit0 b := do (ic, p) ← prove_one_le_nat ic b, ic.mk_app ``le_one_bit0 [b, p]
  | one, bit1 b := do (ic, p) ← prove_pos_nat ic b, ic.mk_app ``le_one_bit1 [b, p]
  | bit0 a, bit0 b := do (ic, p) ← prove_le_nat a b, ic.mk_app ``le_bit0_bit0 [a, b, p]
  | bit0 a, bit1 b := do (ic, p) ← prove_le_nat a b, ic.mk_app ``le_bit0_bit1 [a, b, p]
  | bit1 a, bit0 b := do (ic, p) ← prove_sle_nat a b, ic.mk_app ``le_bit1_bit0 [a, b, p]
  | bit1 a, bit1 b := do (ic, p) ← prove_le_nat a b, ic.mk_app ``le_bit1_bit1 [a, b, p]
  | _, _ := failed
  end
with prove_sle_nat : expr → expr → tactic (instance_cache × expr)
| a b :=
  match match_numeral a, match_numeral b with
  | zero, _ := prove_nonneg ic b
  | one, bit0 b := do (ic, p) ← prove_one_le_nat ic b, ic.mk_app ``sle_one_bit0 [b, p]
  | one, bit1 b := do (ic, p) ← prove_one_le_nat ic b, ic.mk_app ``sle_one_bit1 [b, p]
  | bit0 a, bit0 b := do (ic, p) ← prove_sle_nat a b, ic.mk_app ``sle_bit0_bit0 [a, b, p]
  | bit0 a, bit1 b := do (ic, p) ← prove_le_nat a b, ic.mk_app ``sle_bit0_bit1 [a, b, p]
  | bit1 a, bit0 b := do (ic, p) ← prove_sle_nat a b, ic.mk_app ``sle_bit1_bit0 [a, b, p]
  | bit1 a, bit1 b := do (ic, p) ← prove_sle_nat a b, ic.mk_app ``sle_bit1_bit1 [a, b, p]
  | _, _ := failed
  end

/-- Given `a`,`b` natural numerals, proves `⊢ a ≤ b`. -/
add_decl_doc prove_le_nat
/-- Given `a`,`b` natural numerals, proves `⊢ a + 1 ≤ b`. -/
add_decl_doc prove_sle_nat

/-- Given `a`,`b` natural numerals, proves `⊢ a < b`. -/
meta def prove_lt_nat (ic : instance_cache) : expr → expr → tactic (instance_cache × expr)
| a b :=
  match match_numeral a, match_numeral b with
  | zero, _ := prove_pos ic b
  | one, bit0 b := do (ic, p) ← prove_one_le_nat ic b, ic.mk_app ``lt_one_bit0 [b, p]
  | one, bit1 b := do (ic, p) ← prove_pos_nat ic b, ic.mk_app ``lt_one_bit1 [b, p]
  | bit0 a, bit0 b := do (ic, p) ← prove_lt_nat a b, ic.mk_app ``lt_bit0_bit0 [a, b, p]
  | bit0 a, bit1 b := do (ic, p) ← prove_le_nat ic a b, ic.mk_app ``lt_bit0_bit1 [a, b, p]
  | bit1 a, bit0 b := do (ic, p) ← prove_sle_nat ic a b, ic.mk_app ``lt_bit1_bit0 [a, b, p]
  | bit1 a, bit1 b := do (ic, p) ← prove_lt_nat a b, ic.mk_app ``lt_bit1_bit1 [a, b, p]
  | _, _ := failed
  end

end

theorem clear_denom_lt {α} [linear_ordered_semiring α] (a a' b b' d : α)
  (h₀ : 0 < d) (ha : a * d = a') (hb : b * d = b') (h : a' < b') : a < b :=
lt_of_mul_lt_mul_right (by rwa [ha, hb]) (le_of_lt h₀)

/-- Given `a`,`b` nonnegative rational numerals, proves `⊢ a < b`. -/
meta def prove_lt_nonneg_rat (ic : instance_cache) (a b : expr) (na nb : ℚ) : tactic (instance_cache × expr) :=
if na.denom = 1 ∧ nb.denom = 1 then
  prove_lt_nat ic a b
else do
  let nd := na.denom.lcm nb.denom,
  (ic, d) ← ic.of_nat nd,
  (ic, p₀) ← prove_pos ic d,
  (ic, a', pa) ← prove_clear_denom ic a d na nd,
  (ic, b', pb) ← prove_clear_denom ic b d nb nd,
  (ic, p) ← prove_lt_nat ic a' b',
  ic.mk_app ``clear_denom_lt [a, a', b, b', d, p₀, pa, pb, p]

lemma lt_neg_pos {α} [ordered_add_comm_group α] (a b : α) (ha : 0 < a) (hb : 0 < b) : -a < b :=
lt_trans (neg_neg_of_pos ha) hb

/-- Given `a`,`b` rational numerals, proves `⊢ a < b`. -/
meta def prove_lt_rat (ic : instance_cache) (a b : expr) (na nb : ℚ) : tactic (instance_cache × expr) :=
match match_sign a, match_sign b with
| sum.inl a, sum.inl b := do
  (ic, p) ← prove_lt_nonneg_rat ic a b (-na) (-nb),
  ic.mk_app ``neg_lt_neg [a, b, p]
| sum.inl a, sum.inr ff := do
  (ic, p) ← prove_pos ic a,
  ic.mk_app ``neg_neg_of_pos [a, p]
| sum.inl a, sum.inr tt := do
  (ic, pa) ← prove_pos ic a,
  (ic, pb) ← prove_pos ic b,
  ic.mk_app ``lt_neg_pos [a, b, pa, pb]
| sum.inr ff, _ := prove_pos ic b
| sum.inr tt, _ := prove_lt_nonneg_rat ic a b na nb
end

theorem clear_denom_le {α} [linear_ordered_semiring α] (a a' b b' d : α)
  (h₀ : 0 < d) (ha : a * d = a') (hb : b * d = b') (h : a' ≤ b') : a ≤ b :=
le_of_mul_le_mul_right (by rwa [ha, hb]) h₀

/-- Given `a`,`b` nonnegative rational numerals, proves `⊢ a ≤ b`. -/
meta def prove_le_nonneg_rat (ic : instance_cache) (a b : expr) (na nb : ℚ) : tactic (instance_cache × expr) :=
if na.denom = 1 ∧ nb.denom = 1 then
  prove_le_nat ic a b
else do
  let nd := na.denom.lcm nb.denom,
  (ic, d) ← ic.of_nat nd,
  (ic, p₀) ← prove_pos ic d,
  (ic, a', pa) ← prove_clear_denom ic a d na nd,
  (ic, b', pb) ← prove_clear_denom ic b d nb nd,
  (ic, p) ← prove_le_nat ic a' b',
  ic.mk_app ``clear_denom_le [a, a', b, b', d, p₀, pa, pb, p]

lemma le_neg_pos {α} [ordered_add_comm_group α] (a b : α) (ha : 0 ≤ a) (hb : 0 ≤ b) : -a ≤ b :=
le_trans (neg_nonpos_of_nonneg ha) hb

/-- Given `a`,`b` rational numerals, proves `⊢ a ≤ b`. -/
meta def prove_le_rat (ic : instance_cache) (a b : expr) (na nb : ℚ) : tactic (instance_cache × expr) :=
match match_sign a, match_sign b with
| sum.inl a, sum.inl b := do
  (ic, p) ← prove_le_nonneg_rat ic a b (-na) (-nb),
  ic.mk_app ``neg_le_neg [a, b, p]
| sum.inl a, sum.inr ff := do
  (ic, p) ← prove_nonneg ic a,
  ic.mk_app ``neg_nonpos_of_nonneg [a, p]
| sum.inl a, sum.inr tt := do
  (ic, pa) ← prove_nonneg ic a,
  (ic, pb) ← prove_nonneg ic b,
  ic.mk_app ``le_neg_pos [a, b, pa, pb]
| sum.inr ff, _ := prove_nonneg ic b
| sum.inr tt, _ := prove_le_nonneg_rat ic a b na nb
end

/-- Given `a`,`b` rational numerals, proves `⊢ a ≠ b`. This version
tries to prove `⊢ a < b` or `⊢ b < a`, and so is not appropriate for types without an order relation. -/
meta def prove_ne_rat (ic : instance_cache) (a b : expr) (na nb : ℚ) : tactic (instance_cache × expr) :=
if na < nb then do
  (ic, p) ← prove_lt_rat ic a b na nb,
  ic.mk_app ``ne_of_lt [a, b, p]
else do
  (ic, p) ← prove_lt_rat ic b a nb na,
  ic.mk_app ``ne_of_gt [a, b, p]

theorem nat_cast_zero {α} [semiring α] : ↑(0 : ℕ) = (0 : α) := nat.cast_zero
theorem nat_cast_one {α} [semiring α] : ↑(1 : ℕ) = (1 : α) := nat.cast_one
theorem nat_cast_bit0 {α} [semiring α] (a : ℕ) (a' : α) (h : ↑a = a') : ↑(bit0 a) = bit0 a' :=
h ▸ nat.cast_bit0 _
theorem nat_cast_bit1 {α} [semiring α] (a : ℕ) (a' : α) (h : ↑a = a') : ↑(bit1 a) = bit1 a' :=
h ▸ nat.cast_bit1 _
theorem int_cast_zero {α} [ring α] : ↑(0 : ℤ) = (0 : α) := int.cast_zero
theorem int_cast_one {α} [ring α] : ↑(1 : ℤ) = (1 : α) := int.cast_one
theorem int_cast_bit0 {α} [ring α] (a : ℤ) (a' : α) (h : ↑a = a') : ↑(bit0 a) = bit0 a' :=
h ▸ int.cast_bit0 _
theorem int_cast_bit1 {α} [ring α] (a : ℤ) (a' : α) (h : ↑a = a') : ↑(bit1 a) = bit1 a' :=
h ▸ int.cast_bit1 _
theorem rat_cast_bit0 {α} [division_ring α] [char_zero α] (a : ℚ) (a' : α) (h : ↑a = a') : ↑(bit0 a) = bit0 a' :=
h ▸ rat.cast_bit0 _
theorem rat_cast_bit1 {α} [division_ring α] [char_zero α] (a : ℚ) (a' : α) (h : ↑a = a') : ↑(bit1 a) = bit1 a' :=
h ▸ rat.cast_bit1 _

/-- Given `a' : α` a natural numeral, returns `(a : ℕ, ⊢ ↑a = a')`.
(Note that the returned value is on the left of the equality.) -/
meta def prove_nat_uncast (ic nc : instance_cache) : ∀ (a' : expr),
  tactic (instance_cache × instance_cache × expr × expr)
| a' :=
  match match_numeral a' with
  | match_numeral_result.zero := do
    (nc, e) ← nc.mk_app ``has_zero.zero [],
    (ic, p) ← ic.mk_app ``nat_cast_zero [],
    return (ic, nc, e, p)
  | match_numeral_result.one := do
    (nc, e) ← nc.mk_app ``has_one.one [],
    (ic, p) ← ic.mk_app ``nat_cast_one [],
    return (ic, nc, e, p)
  | match_numeral_result.bit0 a' := do
    (ic, nc, a, p) ← prove_nat_uncast a',
    (nc, a0) ← nc.mk_bit0 a,
    (ic, p) ← ic.mk_app ``nat_cast_bit0 [a, a', p],
    return (ic, nc, a0, p)
  | match_numeral_result.bit1 a' := do
    (ic, nc, a, p) ← prove_nat_uncast a',
    (nc, a1) ← nc.mk_bit1 a,
    (ic, p) ← ic.mk_app ``nat_cast_bit1 [a, a', p],
    return (ic, nc, a1, p)
  | _ := failed
  end

/-- Given `a' : α` a natural numeral, returns `(a : ℤ, ⊢ ↑a = a')`.
(Note that the returned value is on the left of the equality.) -/
meta def prove_int_uncast_nat (ic zc : instance_cache) : ∀ (a' : expr),
  tactic (instance_cache × instance_cache × expr × expr)
| a' :=
  match match_numeral a' with
  | match_numeral_result.zero := do
    (zc, e) ← zc.mk_app ``has_zero.zero [],
    (ic, p) ← ic.mk_app ``int_cast_zero [],
    return (ic, zc, e, p)
  | match_numeral_result.one := do
    (zc, e) ← zc.mk_app ``has_one.one [],
    (ic, p) ← ic.mk_app ``int_cast_one [],
    return (ic, zc, e, p)
  | match_numeral_result.bit0 a' := do
    (ic, zc, a, p) ← prove_int_uncast_nat a',
    (zc, a0) ← zc.mk_bit0 a,
    (ic, p) ← ic.mk_app ``int_cast_bit0 [a, a', p],
    return (ic, zc, a0, p)
  | match_numeral_result.bit1 a' := do
    (ic, zc, a, p) ← prove_int_uncast_nat a',
    (zc, a1) ← zc.mk_bit1 a,
    (ic, p) ← ic.mk_app ``int_cast_bit1 [a, a', p],
    return (ic, zc, a1, p)
  | _ := failed
  end

/-- Given `a' : α` a natural numeral, returns `(a : ℚ, ⊢ ↑a = a')`.
(Note that the returned value is on the left of the equality.) -/
meta def prove_rat_uncast_nat (ic qc : instance_cache) (cz_inst : expr) : ∀ (a' : expr),
  tactic (instance_cache × instance_cache × expr × expr)
| a' :=
  match match_numeral a' with
  | match_numeral_result.zero := do
    (qc, e) ← qc.mk_app ``has_zero.zero [],
    (ic, p) ← ic.mk_app ``rat.cast_zero [cz_inst],
    return (ic, qc, e, p)
  | match_numeral_result.one := do
    (qc, e) ← qc.mk_app ``has_one.one [],
    (ic, p) ← ic.mk_app ``rat.cast_one [],
    return (ic, qc, e, p)
  | match_numeral_result.bit0 a' := do
    (ic, qc, a, p) ← prove_rat_uncast_nat a',
    (qc, a0) ← qc.mk_bit0 a,
    (ic, p) ← ic.mk_app ``rat_cast_bit0 [cz_inst, a, a', p],
    return (ic, qc, a0, p)
  | match_numeral_result.bit1 a' := do
    (ic, qc, a, p) ← prove_rat_uncast_nat a',
    (qc, a1) ← qc.mk_bit1 a,
    (ic, p) ← ic.mk_app ``rat_cast_bit1 [cz_inst, a, a', p],
    return (ic, qc, a1, p)
  | _ := failed
  end

theorem rat_cast_div {α} [division_ring α] [char_zero α] (a b : ℚ) (a' b' : α)
  (ha : ↑a = a') (hb : ↑b = b') : ↑(a / b) = a' / b' :=
ha ▸ hb ▸ rat.cast_div _ _

/-- Given `a' : α` a nonnegative rational numeral, returns `(a : ℚ, ⊢ ↑a = a')`.
(Note that the returned value is on the left of the equality.) -/
meta def prove_rat_uncast_nonneg (ic qc : instance_cache) (cz_inst a' : expr) (na' : ℚ) :
 tactic (instance_cache × instance_cache × expr × expr) :=
if na'.denom = 1 then
  prove_rat_uncast_nat ic qc cz_inst a'
else do
  [_, _, a', b'] ← return a'.get_app_args,
  (ic, qc, a, pa) ← prove_rat_uncast_nat ic qc cz_inst a',
  (ic, qc, b, pb) ← prove_rat_uncast_nat ic qc cz_inst b',
  (qc, e) ← qc.mk_app ``has_div.div [a, b],
  (ic, p) ← ic.mk_app ``rat_cast_div [cz_inst, a, b, a', b', pa, pb],
  return (ic, qc, e, p)

theorem int_cast_neg {α} [ring α] (a : ℤ) (a' : α) (h : ↑a = a') : ↑-a = -a' :=
h ▸ int.cast_neg _
theorem rat_cast_neg {α} [division_ring α] (a : ℚ) (a' : α) (h : ↑a = a') : ↑-a = -a' :=
h ▸ rat.cast_neg _

/-- Given `a' : α` an integer numeral, returns `(a : ℤ, ⊢ ↑a = a')`.
(Note that the returned value is on the left of the equality.) -/
meta def prove_int_uncast (ic zc : instance_cache) (a' : expr) :
  tactic (instance_cache × instance_cache × expr × expr) :=
match match_neg a' with
| some a' := do
  (ic, zc, a, p) ← prove_int_uncast_nat ic zc a',
  (zc, e) ← zc.mk_app ``has_neg.neg [a],
  (ic, p) ← ic.mk_app ``int_cast_neg [a, a', p],
  return (ic, zc, e, p)
| none := prove_int_uncast_nat ic zc a'
end

/-- Given `a' : α` a rational numeral, returns `(a : ℚ, ⊢ ↑a = a')`.
(Note that the returned value is on the left of the equality.) -/
meta def prove_rat_uncast (ic qc : instance_cache) (cz_inst a' : expr) (na' : ℚ) :
  tactic (instance_cache × instance_cache × expr × expr) :=
match match_neg a' with
| some a' := do
  (ic, qc, a, p) ← prove_rat_uncast_nonneg ic qc cz_inst a' (-na'),
  (qc, e) ← qc.mk_app ``has_neg.neg [a],
  (ic, p) ← ic.mk_app ``rat_cast_neg [a, a', p],
  return (ic, qc, e, p)
| none := prove_rat_uncast_nonneg ic qc cz_inst a' na'
end

theorem nat_cast_ne {α} [semiring α] [char_zero α] (a b : ℕ) (a' b' : α)
  (ha : ↑a = a') (hb : ↑b = b') (h : a ≠ b) : a' ≠ b' :=
ha ▸ hb ▸ mt nat.cast_inj.1 h
theorem int_cast_ne {α} [ring α] [char_zero α] (a b : ℤ) (a' b' : α)
  (ha : ↑a = a') (hb : ↑b = b') (h : a ≠ b) : a' ≠ b' :=
ha ▸ hb ▸ mt int.cast_inj.1 h
theorem rat_cast_ne {α} [division_ring α] [char_zero α] (a b : ℚ) (a' b' : α)
  (ha : ↑a = a') (hb : ↑b = b') (h : a ≠ b) : a' ≠ b' :=
ha ▸ hb ▸ mt rat.cast_inj.1 h

/-- Given `a`,`b` rational numerals, proves `⊢ a ≠ b`. Currently it tries two methods:

  * Prove `⊢ a < b` or `⊢ b < a`, if the base type has an order
  * Embed `↑(a':ℚ) = a` and `↑(b':ℚ) = b`, and then prove `a' ≠ b'`.
    This requires that the base type be `char_zero`, and also that it be a `division_ring`
    so that the coercion from `ℚ` is well defined.

We may also add coercions to `ℤ` and `ℕ` as well in order to support `char_zero`
rings and semirings. -/
meta def prove_ne : instance_cache → expr → expr → ℚ → ℚ → tactic (instance_cache × expr)
| ic a b na nb := prove_ne_rat ic a b na nb <|> do
  cz_inst ← mk_mapp ``char_zero [ic.α, none, none] >>= mk_instance,
  if na.denom = 1 ∧ nb.denom = 1 then
    if na ≥ 0 ∧ nb ≥ 0 then do
      guard (ic.α ≠ `(ℕ)),
      nc ← mk_instance_cache `(ℕ),
      (ic, nc, a', pa) ← prove_nat_uncast ic nc a,
      (ic, nc, b', pb) ← prove_nat_uncast ic nc b,
      (nc, p) ← prove_ne_rat nc a' b' na nb,
      ic.mk_app ``nat_cast_ne [cz_inst, a', b', a, b, pa, pb, p]
    else do
      guard (ic.α ≠ `(ℤ)),
      zc ← mk_instance_cache `(ℤ),
      (ic, zc, a', pa) ← prove_int_uncast ic zc a,
      (ic, zc, b', pb) ← prove_int_uncast ic zc b,
      (zc, p) ← prove_ne_rat zc a' b' na nb,
      ic.mk_app ``int_cast_ne [cz_inst, a', b', a, b, pa, pb, p]
  else do
    guard (ic.α ≠ `(ℚ)),
    qc ← mk_instance_cache `(ℚ),
    (ic, qc, a', pa) ← prove_rat_uncast ic qc cz_inst a na,
    (ic, qc, b', pb) ← prove_rat_uncast ic qc cz_inst b nb,
    (qc, p) ← prove_ne_rat qc a' b' na nb,
    ic.mk_app ``rat_cast_ne [cz_inst, a', b', a, b, pa, pb, p]

/-- Given `∣- p`, returns `(true, ⊢ p = true)`. -/
meta def true_intro (p : expr) : tactic (expr × expr) :=
prod.mk `(true) <$> mk_app ``eq_true_intro [p]

/-- Given `∣- ¬ p`, returns `(false, ⊢ p = false)`. -/
meta def false_intro (p : expr) : tactic (expr × expr) :=
prod.mk `(false) <$> mk_app ``eq_false_intro [p]

theorem not_refl_false_intro {α} (a : α) : (a ≠ a) = false :=
eq_false_intro $ not_not_intro rfl

/-- Evaluates the inequality operations `=`,`<`,`>`,`≤`,`≥`,`≠` on numerals. -/
meta def eval_ineq : expr → tactic (expr × expr)
| `(%%e₁ < %%e₂) := do
  n₁ ← e₁.to_rat, n₂ ← e₂.to_rat,
  c ← infer_type e₁ >>= mk_instance_cache,
  if n₁ < n₂ then
    do (_, p) ← prove_lt_rat c e₁ e₂ n₁ n₂, true_intro p
  else if n₁ = n₂ then do
    (_, p) ← c.mk_app ``lt_irrefl [e₁],
    false_intro p
  else do
    (c, p') ← prove_lt_rat c e₂ e₁ n₂ n₁,
    (_, p) ← c.mk_app ``not_lt_of_gt [e₁, e₂, p'],
    false_intro p
| `(%%e₁ ≤ %%e₂) := do
  n₁ ← e₁.to_rat, n₂ ← e₂.to_rat,
  c ← infer_type e₁ >>= mk_instance_cache,
  if n₁ ≤ n₂ then do
    (_, p) ←
      if n₁ = n₂ then c.mk_app ``le_refl [e₁]
      else prove_le_rat c e₁ e₂ n₁ n₂,
    true_intro p
  else do
    (c, p) ← prove_lt_rat c e₂ e₁ n₂ n₁,
    (_, p) ← c.mk_app ``not_le_of_gt [e₁, e₂, p],
    false_intro p
| `(%%e₁ = %%e₂) := do
  n₁ ← e₁.to_rat, n₂ ← e₂.to_rat,
  c ← infer_type e₁ >>= mk_instance_cache,
  if n₁ = n₂ then mk_eq_refl e₁ >>= true_intro
  else do (_, p) ← prove_ne c e₁ e₂ n₁ n₂, false_intro p
| `(%%e₁ > %%e₂) := mk_app ``has_lt.lt [e₂, e₁] >>= eval_ineq
| `(%%e₁ ≥ %%e₂) := mk_app ``has_le.le [e₂, e₁] >>= eval_ineq
| `(%%e₁ ≠ %%e₂) := do
  n₁ ← e₁.to_rat, n₂ ← e₂.to_rat,
  c ← infer_type e₁ >>= mk_instance_cache,
  if n₁ = n₂ then
    prod.mk `(false) <$> mk_app ``not_refl_false_intro [e₁]
  else do (_, p) ← prove_ne c e₁ e₂ n₁ n₂, true_intro p
| _ := failed

theorem nat_succ_eq (a b c : ℕ) (h₁ : a = b) (h₂ : b + 1 = c) : nat.succ a = c := by rwa h₁

/-- Evaluates the expression `nat.succ ... (nat.succ n)` where `n` is a natural numeral.
(We could also just handle `nat.succ n` here and rely on `simp` to work bottom up, but we figure
that towers of successors coming from e.g. `induction` are a common case.) -/
meta def prove_nat_succ (ic : instance_cache) : expr → tactic (instance_cache × ℕ × expr × expr)
| `(nat.succ %%a) := do
  (ic, n, b, p₁) ← prove_nat_succ a,
  let n' := n + 1,
  (ic, c) ← ic.of_nat n',
  (ic, p₂) ← prove_add_nat ic b `(1) c,
  return (ic, n', c, `(nat_succ_eq).mk_app [a, b, c, p₁, p₂])
| e := do
  n ← e.to_nat,
  p ← mk_eq_refl e,
  return (ic, n, e, p)

lemma nat_div (a b q r m : ℕ) (hm : q * b = m) (h : r + m = a) (h₂ : r < b) : a / b = q :=
by rw [← h, ← hm, nat.add_mul_div_right _ _ (lt_of_le_of_lt (nat.zero_le _) h₂),
       nat.div_eq_of_lt h₂, zero_add]

lemma int_div (a b q r m : ℤ) (hm : q * b = m) (h : r + m = a) (h₁ : 0 ≤ r) (h₂ : r < b) : a / b = q :=
by rw [← h, ← hm, int.add_mul_div_right _ _ (ne_of_gt (lt_of_le_of_lt h₁ h₂)),
       int.div_eq_zero_of_lt h₁ h₂, zero_add]

lemma nat_mod (a b q r m : ℕ) (hm : q * b = m) (h : r + m = a) (h₂ : r < b) : a % b = r :=
by rw [← h, ← hm, nat.add_mul_mod_self_right, nat.mod_eq_of_lt h₂]

lemma int_mod (a b q r m : ℤ) (hm : q * b = m) (h : r + m = a) (h₁ : 0 ≤ r) (h₂ : r < b) : a % b = r :=
by rw [← h, ← hm, int.add_mul_mod_self, int.mod_eq_of_lt h₁ h₂]

lemma int_div_neg (a b c' c : ℤ) (h : a / b = c') (h₂ : -c' = c) : a / -b = c :=
h₂ ▸ h ▸ int.div_neg _ _

lemma int_mod_neg (a b c : ℤ) (h : a % b = c) : a % -b = c :=
(int.mod_neg _ _).trans h

/-- Given `a`,`b` numerals in `nat` or `int`,
  * `prove_div_mod ic a b ff` returns `(c, ⊢ a / b = c)`
  * `prove_div_mod ic a b tt` returns `(c, ⊢ a % b = c)`
-/
meta def prove_div_mod (ic : instance_cache) : expr → expr → bool → tactic (instance_cache × expr × expr)
| a b mod :=
  match match_neg b with
  | some b := do
    (ic, c', p) ← prove_div_mod a b mod,
    if mod then
      return (ic, c', `(int_mod_neg).mk_app [a, b, c', p])
    else do
      (ic, c, p₂) ← prove_neg ic c',
      return (ic, c, `(int_div_neg).mk_app [a, b, c', c, p, p₂])
  | none := do
    nb ← b.to_nat,
    na ← a.to_int,
    let nq := na / nb,
    let nr := na % nb,
    let nm := nq * nr,
    (ic, q) ← ic.of_int nq,
    (ic, r) ← ic.of_int nr,
    (ic, m, pm) ← prove_mul_rat ic q b (rat.of_int nq) (rat.of_int nb),
    (ic, p) ← prove_add_rat ic r m a (rat.of_int nr) (rat.of_int nm) (rat.of_int na),
    (ic, p') ← prove_lt_nat ic r b,
    if ic.α = `(nat) then
      if mod then return (ic, r, `(nat_mod).mk_app [a, b, q, r, m, pm, p, p'])
      else        return (ic, q, `(nat_div).mk_app [a, b, q, r, m, pm, p, p'])
    else if ic.α = `(int) then do
      (ic, p₀) ← prove_nonneg ic r,
      if mod then return (ic, r, `(int_mod).mk_app [a, b, q, r, m, pm, p, p₀, p'])
      else        return (ic, q, `(int_div).mk_app [a, b, q, r, m, pm, p, p₀, p'])
    else failed
  end

theorem dvd_eq_nat (a b c : ℕ) (p) (h₁ : b % a = c) (h₂ : (c = 0) = p) : (a ∣ b) = p :=
(propext $ by rw [← h₁, nat.dvd_iff_mod_eq_zero]).trans h₂
theorem dvd_eq_int (a b c : ℤ) (p) (h₁ : b % a = c) (h₂ : (c = 0) = p) : (a ∣ b) = p :=
(propext $ by rw [← h₁, int.dvd_iff_mod_eq_zero]).trans h₂

/-- Evaluates some extra numeric operations on `nat` and `int`, specifically
`nat.succ`, `/` and `%`, and `∣` (divisibility). -/
meta def eval_nat_int_ext : expr → tactic (expr × expr)
| e@`(nat.succ _) := do
  ic ← mk_instance_cache `(ℕ),
  (_, _, ep) ← prove_nat_succ ic e,
  return ep
| `(%%a / %%b) := do
  c ← infer_type a >>= mk_instance_cache,
  prod.snd <$> prove_div_mod c a b ff
| `(%%a % %%b) := do
  c ← infer_type a >>= mk_instance_cache,
  prod.snd <$> prove_div_mod c a b tt
| `(%%a ∣ %%b) := do
  α ← infer_type a,
  ic ← mk_instance_cache α,
  th ← if α = `(nat) then return (`(dvd_eq_nat):expr) else
       if α = `(int) then return `(dvd_eq_int) else failed,
  (ic, c, p₁) ← prove_div_mod ic b a tt,
  (ic, z) ← ic.mk_app ``has_zero.zero [],
  (e', p₂) ← mk_app ``eq [c, z] >>= eval_ineq,
  return (e', th.mk_app [a, b, c, e', p₁, p₂])
| _ := failed

lemma not_prime_helper (a b n : ℕ)
  (h : a * b = n) (h₁ : 1 < a) (h₂ : 1 < b) : ¬ nat.prime n :=
by rw ← h; exact nat.not_prime_mul h₁ h₂

lemma is_prime_helper (n : ℕ)
  (h₁ : 1 < n) (h₂ : nat.min_fac n = n) : nat.prime n :=
nat.prime_def_min_fac.2 ⟨h₁, h₂⟩

lemma min_fac_bit0 (n : ℕ) : nat.min_fac (bit0 n) = 2 :=
by simp [nat.min_fac_eq, show 2 ∣ bit0 n, by simp [bit0_eq_two_mul n]]

/-- A predicate representing partial progress in a proof of `min_fac`. -/
def min_fac_helper (n k : ℕ) : Prop :=
0 < k ∧ bit1 k ≤ nat.min_fac (bit1 n)

theorem min_fac_helper.n_pos {n k : ℕ} (h : min_fac_helper n k) : 0 < n :=
nat.pos_iff_ne_zero.2 $ λ e,
by rw e at h; exact not_le_of_lt (nat.bit1_lt h.1) h.2

lemma min_fac_ne_bit0 {n k : ℕ} : nat.min_fac (bit1 n) ≠ bit0 k :=
by rw bit0_eq_two_mul; exact λ e, absurd
  ((nat.dvd_add_iff_right (by simp [bit0_eq_two_mul n])).2
    (dvd_trans ⟨_, e⟩ (nat.min_fac_dvd _)))
  dec_trivial

lemma min_fac_helper_0 (n : ℕ) (h : 0 < n) : min_fac_helper n 1 :=
begin
  refine ⟨zero_lt_one, lt_of_le_of_ne _ min_fac_ne_bit0.symm⟩,
  refine @lt_of_le_of_ne ℕ _ _ _ (nat.min_fac_pos _) _,
  intro e,
  have := nat.min_fac_prime _,
  { rw ← e at this, exact nat.not_prime_one this },
  { exact ne_of_gt (nat.bit1_lt h) }
end

lemma min_fac_helper_1 {n k k' : ℕ} (e : k + 1 = k')
  (np : nat.min_fac (bit1 n) ≠ bit1 k)
  (h : min_fac_helper n k) : min_fac_helper n k' :=
begin
  rw ← e,
  refine ⟨nat.succ_pos _,
    (lt_of_le_of_ne (lt_of_le_of_ne _ _ : k+1+k < _)
      min_fac_ne_bit0.symm : bit0 (k+1) < _)⟩,
  { rw add_right_comm, exact h.2 },
  { rw add_right_comm, exact np.symm }
end

lemma min_fac_helper_2 (n k k' : ℕ) (e : k + 1 = k')
  (np : ¬ nat.prime (bit1 k)) (h : min_fac_helper n k) : min_fac_helper n k' :=
begin
  refine min_fac_helper_1 e _ h,
  intro e₁, rw ← e₁ at np,
  exact np (nat.min_fac_prime $ ne_of_gt $ nat.bit1_lt h.n_pos)
end

lemma min_fac_helper_3 (n k k' c : ℕ) (e : k + 1 = k')
  (nc : bit1 n % bit1 k = c) (c0 : 0 < c)
  (h : min_fac_helper n k) : min_fac_helper n k' :=
begin
  refine min_fac_helper_1 e _ h,
  refine mt _ (ne_of_gt c0), intro e₁,
  rw [← nc, ← nat.dvd_iff_mod_eq_zero, ← e₁],
  apply nat.min_fac_dvd
end

lemma min_fac_helper_4 (n k : ℕ) (hd : bit1 n % bit1 k = 0)
  (h : min_fac_helper n k) : nat.min_fac (bit1 n) = bit1 k :=
by rw ← nat.dvd_iff_mod_eq_zero at hd; exact
le_antisymm (nat.min_fac_le_of_dvd (nat.bit1_lt h.1) hd) h.2

lemma min_fac_helper_5 (n k k' : ℕ) (e : bit1 k * bit1 k = k')
  (hd : bit1 n < k') (h : min_fac_helper n k) : nat.min_fac (bit1 n) = bit1 n :=
begin
  refine (nat.prime_def_min_fac.1 (nat.prime_def_le_sqrt.2
    ⟨nat.bit1_lt h.n_pos, _⟩)).2,
  rw ← e at hd,
  intros m m2 hm md,
  have := le_trans h.2 (le_trans (nat.min_fac_le_of_dvd m2 md) hm),
  rw nat.le_sqrt at this,
  exact not_le_of_lt hd this
end

/-- Given `e` a natural numeral and `d : nat` a factor of it, return `⊢ ¬ prime e`. -/
meta def prove_non_prime (e : expr) (n d₁ : ℕ) : tactic expr :=
do let e₁ := reflect d₁,
  c ← mk_instance_cache `(nat),
  (c, p₁) ← prove_lt_nat c `(1) e₁,
  let d₂ := n / d₁, let e₂ := reflect d₂,
  (c, e', p) ← prove_mul_nat c e₁ e₂,
  guard (e' =ₐ e),
  (c, p₂) ← prove_lt_nat c `(1) e₂,
  return $ `(not_prime_helper).mk_app [e₁, e₂, e, p, p₁, p₂]

/-- Given `a`,`a1 := bit1 a`, `n1` the value of `a1`, `b` and `p : min_fac_helper a b`,
  returns `(c, ⊢ min_fac a1 = c)`. -/
meta def prove_min_fac_aux (a a1 : expr) (n1 : ℕ) :
  instance_cache → expr → expr → tactic (instance_cache × expr × expr)
| ic b p := do
  k ← b.to_nat,
  let k1 := bit1 k,
  let b1 := `(bit1:ℕ→ℕ).mk_app [b],
  if n1 < k1*k1 then do
    (ic, e', p₁) ← prove_mul_nat ic b1 b1,
    (ic, p₂) ← prove_lt_nat ic a1 e',
    return (ic, a1, `(min_fac_helper_5).mk_app [a, b, e', p₁, p₂, p])
  else let d := k1.min_fac in
  if to_bool (d < k1) then do
    let k' := k+1, let e' := reflect k',
    (ic, p₁) ← prove_succ ic b e',
    p₂ ← prove_non_prime b1 k1 d,
    prove_min_fac_aux ic e' $ `(min_fac_helper_2).mk_app [a, b, e', p₁, p₂, p]
  else do
    let nc := n1 % k1,
    (ic, c, pc) ← prove_div_mod ic a1 b1 tt,
    if nc = 0 then
      return (ic, b1, `(min_fac_helper_4).mk_app [a, b, pc, p])
    else do
      (ic, p₀) ← prove_pos ic c,
      let k' := k+1, let e' := reflect k',
      (ic, p₁) ← prove_succ ic b e',
      prove_min_fac_aux ic e' $ `(min_fac_helper_3).mk_app [a, b, e', c, p₁, pc, p₀, p]

/-- Given `a` a natural numeral, returns `(b, ⊢ min_fac a = b)`. -/
meta def prove_min_fac (ic : instance_cache) (e : expr) : tactic (instance_cache × expr × expr) :=
match match_numeral e with
| match_numeral_result.zero := return (ic, `(2:ℕ), `(nat.min_fac_zero))
| match_numeral_result.one := return (ic, `(1:ℕ), `(nat.min_fac_one))
| match_numeral_result.bit0 e := return (ic, `(2), `(min_fac_bit0).mk_app [e])
| match_numeral_result.bit1 e := do
  n ← e.to_nat,
  c ← mk_instance_cache `(nat),
  (c, p) ← prove_pos c e,
  let a1 := `(bit1:ℕ→ℕ).mk_app [e],
  prove_min_fac_aux e a1 (bit1 n) c `(1) (`(min_fac_helper_0).mk_app [e, p])
| _ := failed
end

/-- Evaluates the `prime` and `min_fac` functions. -/
meta def eval_prime : expr → tactic (expr × expr)
| `(nat.prime %%e) := do
  n ← e.to_nat,
  match n with
  | 0 := false_intro `(nat.not_prime_zero)
  | 1 := false_intro `(nat.not_prime_one)
  | _ := let d₁ := n.min_fac in
    if d₁ < n then prove_non_prime e n d₁ >>= false_intro
    else do
      let e₁ := reflect d₁,
      c ← mk_instance_cache `(nat),
      (c, p₁) ← prove_lt_nat c `(1) e₁,
      (c, e₁, p) ← prove_min_fac c e,
      true_intro $ `(is_prime_helper).mk_app [e, p₁, p]
  end
| `(nat.min_fac %%e) := do
  ic ← mk_instance_cache `(ℕ),
  prod.snd <$> prove_min_fac ic e
| _ := failed

/-- This version of `derive` does not fail when the input is already a numeral -/
meta def derive' (e : expr) : tactic (expr × expr) :=
eval_field e <|> eval_nat_int_ext e <|>
eval_pow e <|> eval_ineq e <|> eval_prime e

meta def derive : expr → tactic (expr × expr) | e :=
do e ← instantiate_mvars e,
   (_, e', pr) ←
    ext_simplify_core () {} simp_lemmas.mk (λ _, failed) (λ _ _ _ _ _, failed)
      (λ _ _ _ _ e,
        do (new_e, pr) ← derive' e,
           guard (¬ new_e =ₐ e),
           return ((), new_e, some pr, tt))
      `eq e,
    return (e', pr)

end norm_num

namespace tactic.interactive
open norm_num interactive interactive.types

/-- Basic version of `norm_num` that does not call `simp`. -/
meta def norm_num1 (loc : parse location) : tactic unit :=
do ns ← loc.get_locals,
   tt ← tactic.replace_at derive ns loc.include_goal
      | fail "norm_num failed to simplify",
   when loc.include_goal $ try tactic.triv,
   when (¬ ns.empty) $ try tactic.contradiction

/-- Normalize numerical expressions. Supports the operations
`+` `-` `*` `/` `^` and `%` over numerical types such as
`ℕ`, `ℤ`, `ℚ`, `ℝ`, `ℂ` and some general algebraic types,
and can prove goals of the form `A = B`, `A ≠ B`, `A < B` and `A ≤ B`,
where `A` and `B` are numerical expressions.
It also has a relatively simple primality prover. -/
meta def norm_num (hs : parse simp_arg_list) (l : parse location) : tactic unit :=
repeat1 $ orelse' (norm_num1 l) $
simp_core {} (norm_num1 (loc.ns [none])) ff hs [] l

add_hint_tactic "norm_num"

/-- Normalizes a numerical expression and tries to close the goal with the result. -/
meta def apply_normed (x : parse texpr) : tactic unit :=
do x₁ ← to_expr x,
  (x₂,_) ← derive x₁,
  tactic.exact x₂

/--
Normalises numerical expressions. It supports the operations `+` `-` `*` `/` `^` and `%` over
numerical types such as `ℕ`, `ℤ`, `ℚ`, `ℝ`, `ℂ`, and can prove goals of the form `A = B`, `A ≠ B`,
`A < B` and `A ≤ B`, where `A` and `B` are
numerical expressions. It also has a relatively simple primality prover.
```lean
import data.real.basic

example : (2 : ℝ) + 2 = 4 := by norm_num
example : (12345.2 : ℝ) ≠ 12345.3 := by norm_num
example : (73 : ℝ) < 789/2 := by norm_num
example : 123456789 + 987654321 = 1111111110 := by norm_num
example (R : Type*) [ring R] : (2 : R) + 2 = 4 := by norm_num
example (F : Type*) [linear_ordered_field F] : (2 : F) + 2 < 5 := by norm_num
example : nat.prime (2^13 - 1) := by norm_num
example : ¬ nat.prime (2^11 - 1) := by norm_num
example (x : ℝ) (h : x = 123 + 456) : x = 579 := by norm_num at h; assumption
```

The variant `norm_num1` does not call `simp`.

Both `norm_num` and `norm_num1` can be called inside the `conv` tactic.

The tactic `apply_normed` normalises a numerical expression and tries to close the goal with
the result. Compare:
```lean
def a : ℕ := 2^100
#print a -- 2 ^ 100

def normed_a : ℕ := by apply_normed 2^100
#print normed_a -- 1267650600228229401496703205376
```
-/
add_tactic_doc
{ name        := "norm_num",
  category    := doc_category.tactic,
  decl_names  := [`tactic.interactive.norm_num1, `tactic.interactive.norm_num,
                  `tactic.interactive.apply_normed],
  tags        := ["arithmetic", "decision procedure"] }

end tactic.interactive

namespace conv.interactive
open conv interactive tactic.interactive
open norm_num (derive)

/-- Basic version of `norm_num` that does not call `simp`. -/
meta def norm_num1 : conv unit := replace_lhs derive

/-- Normalize numerical expressions. Supports the operations
`+` `-` `*` `/` `^` and `%` over numerical types such as
`ℕ`, `ℤ`, `ℚ`, `ℝ`, `ℂ` and some general algebraic types,
and can prove goals of the form `A = B`, `A ≠ B`, `A < B` and `A ≤ B`,
where `A` and `B` are numerical expressions.
It also has a relatively simple primality prover. -/
meta def norm_num (hs : parse simp_arg_list) : conv unit :=
repeat1 $ orelse' norm_num1 $
simp_core {} norm_num1 ff hs [] (loc.ns [none])

end conv.interactive
