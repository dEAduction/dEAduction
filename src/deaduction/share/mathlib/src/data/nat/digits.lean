/-
Copyright (c) 2020 Scott Morrison. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Scott Morrison
-/
import data.int.modeq
import data.fintype.card
import tactic.ring
import tactic.interval_cases

/-!
# Digits of a natural number

This provides a basic API for extracting the digits of a natural number in a given base,
and reconstructing numbers from their digits.

We also prove some divisibility tests based on digits, in particular completing
Theorem #85 from https://www.cs.ru.nl/~freek/100/.
-/


/-- (Impl.) An auxiliary definition for `digits`, to help get the desired definitional unfolding. -/
def digits_aux_0 : ℕ → list ℕ
| 0 := []
| (n+1) := [n+1]

/-- (Impl.) An auxiliary definition for `digits`, to help get the desired definitional unfolding. -/
def digits_aux_1 (n : ℕ) : list ℕ := list.repeat 1 n

/-- (Impl.) An auxiliary definition for `digits`, to help get the desired definitional unfolding. -/
def digits_aux (b : ℕ) (h : 2 ≤ b) : ℕ → list ℕ
| 0 := []
| (n+1) :=
  have (n+1)/b < n+1 := nat.div_lt_self (nat.succ_pos _) h,
  (n+1) % b :: digits_aux ((n+1)/b)

@[simp] lemma digits_aux_zero (b : ℕ) (h : 2 ≤ b) : digits_aux b h 0 = [] := rfl

lemma digits_aux_def (b : ℕ) (h : 2 ≤ b) (n : ℕ) (w : 0 < n) :
  digits_aux b h n = n % b :: digits_aux b h (n/b) :=
begin
  cases n,
  { cases w, },
  { rw [digits_aux], }
end

/--
`digits b n` gives the digits, in little-endian order,
of a natural number `n` in a specified base `b`.

In any base, we have `of_digits b L = L.foldr (λ x y, x + b * y) 0`.
* For any `2 ≤ b`, we have `l < b` for any `l ∈ digits b n`,
  and the last digit is not zero.
  This uniquely specifies the behaviour of `digits b`.
* For `b = 1`, we define `digits 1 n = list.repeat 1 n`.
* For `b = 0`, we define `digits 0 n = [n]`, except `digits 0 0 = []`.

Note this differs from the existing `nat.to_digits` in core, which is used for printing numerals.
In particular, `nat.to_digits b 0 = [0]`, while `digits b 0 = []`.
-/
def digits : ℕ → ℕ → list ℕ
| 0 := digits_aux_0
| 1 := digits_aux_1
| (b+2) := digits_aux (b+2) (by norm_num)

@[simp] lemma digits_zero (b : ℕ) : digits b 0 = [] :=
begin
  cases b,
  { refl, },
  { cases b; refl, },
end

@[simp] lemma digits_one_succ (n : ℕ) : digits 1 (n + 1) = 1 :: digits 1 n :=
rfl

@[simp] lemma digits_add_two_add_one (b n : ℕ) :
  digits (b+2) (n+1) = (((n+1) % (b+2)) :: digits (b+2) ((n+1) / (b+2))) := rfl

@[simp]
lemma digits_of_lt (b x : ℕ) (w₁ : 0 < x) (w₂ : x < b) : digits b x = [x] :=
begin
  cases b,
  { cases w₂ },
  { cases b,
    { interval_cases x, },
    { cases x,
      { cases w₁, },
      { dsimp [digits],
        rw digits_aux,
        rw nat.div_eq_of_lt w₂,
        dsimp only [digits_aux_zero],
        rw nat.mod_eq_of_lt w₂, } } }
end.

lemma digits_add (b : ℕ) (h : 2 ≤ b) (x y : ℕ) (w : x < b) (w' : 0 < x ∨ 0 < y) :
  digits b (x + b * y) = x :: digits b y :=
begin
  cases b,
  { cases h, },
  { cases b,
    { norm_num at h, },
    { cases y,
      { norm_num at w',
        simp [w, w'], },
      dsimp [digits],
      rw digits_aux_def,
      { congr,
        { simp [nat.add_mod, nat.mod_eq_of_lt w], },
        { simp [mul_comm (b+2), nat.add_mul_div_right, nat.div_eq_of_lt w], }
      },
      { apply nat.succ_pos, }, }, },
end.

/--
`of_digits b L` takes a list `L` of natural numbers, and interprets them
as a number in semiring, as the little-endian digits in base `b`.
-/
-- If we had a function converting a list into a polynomial,
-- and appropriate lemmas about that function,
-- we could rewrite this in terms of that.
def of_digits {α : Type*} [semiring α] (b : α) : list ℕ → α
| [] := 0
| (h :: t) := h + b * of_digits t

lemma of_digits_eq_foldr {α : Type*} [semiring α] (b : α) (L : list ℕ) :
  of_digits b L = L.foldr (λ x y, x + b * y) 0 :=
begin
  induction L with d L ih,
  { refl, },
  { dsimp [of_digits], rw ih, },
end

@[simp] lemma of_digits_one_cons {α : Type*} [semiring α] (h : ℕ) (L : list ℕ) :
  of_digits (1 : α) (h :: L) = h + of_digits 1 L :=
by simp [of_digits]

@[norm_cast] lemma coe_of_digits (α : Type*) [semiring α] (b : ℕ) (L : list ℕ) :
  ((of_digits b L : ℕ) : α) = of_digits (b : α) L :=
begin
  induction L with d L ih,
  { refl, },
  { dsimp [of_digits], push_cast, rw ih, }
end

@[norm_cast] lemma coe_int_of_digits (b : ℕ) (L : list ℕ) :
  ((of_digits b L : ℕ) : ℤ) = of_digits (b : ℤ) L :=
begin
  induction L with d L ih,
  { refl, },
  { dsimp [of_digits], push_cast, rw ih, }
end

lemma digits_zero_of_eq_zero {b : ℕ} (h : 1 ≤ b) {L : list ℕ} (w : of_digits b L = 0) :
  ∀ l ∈ L, l = 0 :=
begin
  induction L with d L ih,
  { intros l m,
    cases m, },
  { intros l m,
    dsimp [of_digits] at w,
    rcases m with rfl,
    { convert nat.eq_zero_of_add_eq_zero_right w, simp, },
    { exact ih ((nat.mul_right_inj h).mp (nat.eq_zero_of_add_eq_zero_left w)) _ m, }, }
end

lemma digits_of_digits
  (b : ℕ) (h : 2 ≤ b) (L : list ℕ)
  (w₁ : ∀ l ∈ L, l < b) (w₂ : ∀ (h : L ≠ []), L.last h ≠ 0) :
  digits b (of_digits b L) = L :=
begin
  induction L with d L ih,
  { dsimp [of_digits], simp },
  { dsimp [of_digits],
    replace w₂ := w₂ (by simp),
    rw digits_add b h,
    { rw ih,
      { simp, },
      { intros l m, apply w₁, exact list.mem_cons_of_mem _ m, },
      { intro h,
        { rw [list.last_cons _ h] at w₂,
            convert w₂, }}},
    { convert w₁ d (list.mem_cons_self _ _), simp, },
    { by_cases h' : L = [],
      { rcases h' with rfl,
        simp at w₂,
        left,
        apply nat.pos_of_ne_zero,
        convert w₂, simp, },
      { right,
        apply nat.pos_of_ne_zero,
        contrapose! w₂,
        apply digits_zero_of_eq_zero _ w₂,
        { rw list.last_cons _ h',
          exact list.last_mem h', },
        { exact le_of_lt h, }, }, }, },
end

lemma of_digits_digits (b n : ℕ) : of_digits b (digits b n) = n :=
begin
  cases b with b,
  { cases n with n,
    { refl, },
    { change of_digits 0 [n+1] = n+1,
      dsimp [of_digits],
      simp, } },
  { cases b with b,
    { induction n with n ih,
      { refl, },
      { simp only [ih, add_comm 1, of_digits_one_cons, nat.cast_id, digits_one_succ], } },
    { apply nat.strong_induction_on n _, clear n,
      intros n h,
      cases n,
      { refl, },
      { simp only [nat.succ_eq_add_one, digits_add_two_add_one],
        dsimp [of_digits],
        rw h _ (nat.div_lt_self' n b),
        rw [nat.cast_id, nat.mod_add_div], }, }, },
end

lemma of_digits_one (L : list ℕ) : of_digits 1 L = L.sum :=
begin
  induction L with d L ih,
  { refl, },
  { simp [of_digits, list.sum_cons, ih], }
end

-- This is really a theorem about polynomials.
lemma dvd_of_digits_sub_of_digits {α : Type*} [comm_ring α]
  {a b k : α} (h : k ∣ a - b) (L : list ℕ) :
  k ∣ of_digits a L - of_digits b L :=
begin
  induction L with d L ih,
  { change k ∣ 0 - 0, simp, },
  { simp only [of_digits, add_sub_add_left_eq_sub],
    exact dvd_mul_sub_mul h ih, }
end

lemma of_digits_modeq' (b b' : ℕ) (k : ℕ) (h : b ≡ b' [MOD k]) (L : list ℕ) :
  of_digits b L ≡ of_digits b' L [MOD k] :=
begin
  induction L with d L ih,
  { refl, },
  { dsimp [of_digits],
    dsimp [nat.modeq] at *,
    conv_lhs { rw [nat.add_mod, nat.mul_mod, h, ih], },
    conv_rhs { rw [nat.add_mod, nat.mul_mod], }, }
end

lemma of_digits_modeq (b k : ℕ) (L : list ℕ) : of_digits b L ≡ of_digits (b % k) L [MOD k] :=
of_digits_modeq' b (b % k) k (nat.modeq.symm (nat.modeq.mod_modeq b k)) L

lemma of_digits_mod (b k : ℕ) (L : list ℕ) : of_digits b L % k = of_digits (b % k) L % k :=
of_digits_modeq b k L

lemma of_digits_zmodeq' (b b' : ℤ) (k : ℕ) (h : b ≡ b' [ZMOD k]) (L : list ℕ) :
  of_digits b L ≡ of_digits b' L [ZMOD k] :=
begin
  induction L with d L ih,
  { refl, },
  { dsimp [of_digits],
    dsimp [int.modeq] at *,
    conv_lhs { rw [int.add_mod, int.mul_mod, h, ih], },
    conv_rhs { rw [int.add_mod, int.mul_mod], }, }
end

lemma of_digits_zmodeq (b : ℤ) (k : ℕ) (L : list ℕ) :
  of_digits b L ≡ of_digits (b % k) L [ZMOD k] :=
of_digits_zmodeq' b (b % k) k (int.modeq.symm (int.modeq.mod_modeq b ↑k)) L

lemma of_digits_zmod (b : ℤ) (k : ℕ) (L : list ℕ) :
  of_digits b L % k = of_digits (b % k) L % k :=
of_digits_zmodeq b k L

lemma modeq_digits_sum (b b' : ℕ) (h : b' % b = 1) (n : ℕ) :
   n ≡ (digits b' n).sum [MOD b] :=
begin
  rw ←of_digits_one,
  conv { congr, skip, rw ←(of_digits_digits b' n) },
  convert of_digits_modeq _ _ _,
  exact h.symm,
end

lemma modeq_three_digits_sum (n : ℕ) : n ≡ (digits 10 n).sum [MOD 3] :=
modeq_digits_sum 3 10 (by norm_num) n

lemma modeq_nine_digits_sum (n : ℕ) : n ≡ (digits 10 n).sum [MOD 9] :=
modeq_digits_sum 9 10 (by norm_num) n

lemma dvd_iff_dvd_digits_sum (b b' : ℕ) (h : b' % b = 1) (n : ℕ) :
  b ∣ n ↔ b ∣ (digits b' n).sum :=
begin
  rw ←of_digits_one,
  conv_lhs { rw ←(of_digits_digits b' n) },
  rw [nat.dvd_iff_mod_eq_zero, nat.dvd_iff_mod_eq_zero, of_digits_mod, h],
end

lemma three_dvd_iff (n : ℕ) : 3 ∣ n ↔ 3 ∣ (digits 10 n).sum :=
dvd_iff_dvd_digits_sum 3 10 (by norm_num) n

lemma nine_dvd_iff (n : ℕ) : 9 ∣ n ↔ 9 ∣ (digits 10 n).sum :=
dvd_iff_dvd_digits_sum 9 10 (by norm_num) n

lemma zmodeq_of_digits_digits (b b' : ℕ) (c : ℤ) (h : b' ≡ c [ZMOD b]) (n : ℕ) :
  n ≡ of_digits c (digits b' n) [ZMOD b] :=
begin
  conv { congr, skip, rw ←(of_digits_digits b' n) },
  rw coe_int_of_digits,
  apply of_digits_zmodeq' _ _ _ h,
end

lemma of_digits_neg_one : Π (L : list ℕ),
  of_digits (-1 : ℤ) L = (L.map (λ n : ℕ, (n : ℤ))).alternating_sum
| [] := rfl
| [n] := by simp [of_digits, list.alternating_sum]
| (a :: b :: t) :=
  begin
    simp only [of_digits, list.alternating_sum, list.map_cons, of_digits_neg_one t],
    push_cast,
    ring,
  end

lemma modeq_eleven_digits_sum (n : ℕ) :
  n ≡ ((digits 10 n).map (λ n : ℕ, (n : ℤ))).alternating_sum [ZMOD 11] :=
begin
  have t := zmodeq_of_digits_digits 11 10 (-1 : ℤ) dec_trivial n,
  rw of_digits_neg_one at t,
  exact t,
end

lemma dvd_iff_dvd_of_digits (b b' : ℕ) (c : ℤ) (h : (b : ℤ) ∣ (b' : ℤ) - c) (n : ℕ) :
  b ∣ n ↔ (b : ℤ) ∣ of_digits c (digits b' n) :=
begin
  rw ←int.coe_nat_dvd,
  exact dvd_iff_dvd_of_dvd_sub
    (int.modeq.modeq_iff_dvd.1
      (zmodeq_of_digits_digits b b' c (int.modeq.modeq_iff_dvd.2 h).symm _).symm),
end

lemma eleven_dvd_iff (n : ℕ) :
  11 ∣ n ↔ (11 : ℤ) ∣ ((digits 10 n).map (λ n : ℕ, (n : ℤ))).alternating_sum :=
begin
  have t := dvd_iff_dvd_of_digits 11 10 (-1 : ℤ) (by norm_num) n,
  rw of_digits_neg_one at t,
  exact t,
end
