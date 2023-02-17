/-
Copyright (c) 2018 Robert Y. Lewis. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Robert Y. Lewis
-/
import data.rat
import algebra.gcd_domain
import algebra.field_power
import ring_theory.multiplicity
import data.real.cau_seq

/-!
# p-adic norm

This file defines the p-adic valuation and the p-adic norm on ℚ.

The p-adic valuation on ℚ is the difference of the multiplicities of `p` in the numerator and
denominator of `q`. This function obeys the standard properties of a valuation, with the appropriate
assumptions on p.

The valuation induces a norm on ℚ. This norm is a nonarchimedean absolute value.
It takes values in {0} ∪ {1/p^k | k ∈ ℤ}.

## Notations

This file uses the local notation `/.` for `rat.mk`.

## Implementation notes

Much, but not all, of this file assumes that `p` is prime. This assumption is inferred automatically
by taking `[fact (prime p)]` as a type class argument.

## References

* [F. Q. Gouêva, *p-adic numbers*][gouvea1997]
* [R. Y. Lewis, *A formal proof of Hensel's lemma over the p-adic integers*][lewis2019]
* <https://en.wikipedia.org/wiki/P-adic_number>

## Tags

p-adic, p adic, padic, norm, valuation
-/

universe u

open nat

open_locale rat

open multiplicity

/--
For `p ≠ 1`, the p-adic valuation of an integer `z ≠ 0` is the largest natural number `n` such that
p^n divides z.

`padic_val_rat` defines the valuation of a rational `q` to be the valuation of `q.num` minus the
valuation of `q.denom`.
If `q = 0` or `p = 1`, then `padic_val_rat p q` defaults to 0.
-/
def padic_val_rat (p : ℕ) (q : ℚ) : ℤ :=
if h : q ≠ 0 ∧ p ≠ 1
then (multiplicity (p : ℤ) q.num).get
    (multiplicity.finite_int_iff.2 ⟨h.2, rat.num_ne_zero_of_ne_zero h.1⟩) -
  (multiplicity (p : ℤ) q.denom).get
    (multiplicity.finite_int_iff.2 ⟨h.2, by exact_mod_cast rat.denom_ne_zero _⟩)
else 0

/--
A simplification of the definition of `padic_val_rat p q` when `q ≠ 0` and `p` is prime.
-/
lemma padic_val_rat_def (p : ℕ) [hp : fact p.prime] {q : ℚ} (hq : q ≠ 0) : padic_val_rat p q =
  (multiplicity (p : ℤ) q.num).get (finite_int_iff.2 ⟨hp.ne_one, rat.num_ne_zero_of_ne_zero hq⟩) -
  (multiplicity (p : ℤ) q.denom).get
    (finite_int_iff.2 ⟨hp.ne_one, by exact_mod_cast rat.denom_ne_zero _⟩) :=
dif_pos ⟨hq, hp.ne_one⟩

namespace padic_val_rat
open multiplicity
section padic_val_rat
variables {p : ℕ}

/--
`padic_val_rat p q` is symmetric in `q`.
-/
@[simp] protected lemma neg (q : ℚ) : padic_val_rat p (-q) = padic_val_rat p q :=
begin
  unfold padic_val_rat,
  split_ifs,
  { simp [-add_comm]; refl },
  { exfalso, simp * at * },
  { exfalso, simp * at * },
  { refl }
end

/--
`padic_val_rat p 1` is 0 for any `p`.
-/
@[simp] protected lemma one : padic_val_rat p 1 = 0 :=
by unfold padic_val_rat; split_ifs; simp *

/--
For `p ≠ 0, p ≠ 1, `padic_val_rat p p` is 1.
-/
@[simp] lemma padic_val_rat_self (hp : 1 < p) : padic_val_rat p p = 1 :=
by unfold padic_val_rat; split_ifs; simp [*, nat.one_lt_iff_ne_zero_and_ne_one] at *

/--
The p-adic value of an integer `z ≠ 0` is the multiplicity of `p` in `z`.
-/
lemma padic_val_rat_of_int (z : ℤ) (hp : p ≠ 1) (hz : z ≠ 0) :
  padic_val_rat p (z : ℚ) = (multiplicity (p : ℤ) z).get
    (finite_int_iff.2 ⟨hp, hz⟩) :=
by rw [padic_val_rat, dif_pos]; simp *; refl

end padic_val_rat

section padic_val_nat

/--
A convenience function for the case of `padic_val_rat` when both inputs are natural numbers.
-/
def padic_val_nat (p : ℕ) (n : ℕ) : ℕ :=
int.to_nat (padic_val_rat p n)

/--
`padic_val_nat` is defined as an `int.to_nat` cast; this lemma ensures that the cast is well-behaved.
-/
lemma zero_le_padic_val_rat_of_nat (p n : ℕ) : 0 ≤ padic_val_rat p n :=
begin
  unfold padic_val_rat,
  split_ifs,
  { simp, },
  { trivial, },
end

/--
`padic_val_rat` coincides with `padic_val_nat`.
-/
@[simp, norm_cast] lemma padic_val_rat_of_nat (p n : ℕ) : ↑(padic_val_nat p n) = padic_val_rat p n :=
begin
  unfold padic_val_nat,
  rw int.to_nat_of_nonneg (zero_le_padic_val_rat_of_nat p n),
end

/--
A simplification of `padic_val_nat` when one input is prime, by analogy with `padic_val_rat_def`.
-/
lemma padic_val_nat_def {p : ℕ} [hp : fact p.prime] {n : ℕ} (hn : n ≠ 0) :
  padic_val_nat p n =
  (multiplicity p n).get (multiplicity.finite_nat_iff.2 ⟨nat.prime.ne_one hp, bot_lt_iff_ne_bot.mpr hn⟩) :=
begin
  have n_nonzero : (n : ℚ) ≠ 0, by simpa only [cast_eq_zero, ne.def],
  -- Infinite loop with @simp padic_val_rat_of_nat unless we restrict the available lemmas here,
  -- hence the very long list
  simpa only
    [ int.coe_nat_multiplicity p n, rat.coe_nat_denom n, (padic_val_rat_of_nat p n).symm,
      int.coe_nat_zero, int.coe_nat_inj', sub_zero, get_one_right, int.coe_nat_succ, zero_add,
      rat.coe_nat_num ]
    using padic_val_rat_def p n_nonzero,
end

end padic_val_nat

section padic_val_rat
open multiplicity
variables (p : ℕ) [p_prime : fact p.prime]
include p_prime

/--
The multiplicity of `p : ℕ` in `a : ℤ` is finite exactly when `a ≠ 0`.
-/
lemma finite_int_prime_iff {p : ℕ} [p_prime : fact p.prime] {a : ℤ} : finite (p : ℤ) a ↔ a ≠ 0 :=
by simp [finite_int_iff, ne.symm (ne_of_lt (p_prime.one_lt))]

/--
A rewrite lemma for `padic_val_rat p q` when `q` is expressed in terms of `rat.mk`.
-/
protected lemma defn {q : ℚ} {n d : ℤ} (hqz : q ≠ 0) (qdf : q = n /. d) :
  padic_val_rat p q = (multiplicity (p : ℤ) n).get (finite_int_iff.2
    ⟨ne.symm $ ne_of_lt p_prime.one_lt, λ hn, by simp * at *⟩) -
  (multiplicity (p : ℤ) d).get (finite_int_iff.2 ⟨ne.symm $ ne_of_lt p_prime.one_lt,
    λ hd, by simp * at *⟩) :=
have hn : n ≠ 0, from rat.mk_num_ne_zero_of_ne_zero hqz qdf,
have hd : d ≠ 0, from rat.mk_denom_ne_zero_of_ne_zero hqz qdf,
let ⟨c, hc1, hc2⟩ := rat.num_denom_mk hn hd qdf in
by rw [padic_val_rat, dif_pos];
  simp [hc1, hc2, multiplicity.mul' (nat.prime_iff_prime_int.1 p_prime),
    (ne.symm (ne_of_lt p_prime.one_lt)), hqz]

/--
A rewrite lemma for `padic_val_rat p (q * r)` with conditions `q ≠ 0`, `r ≠ 0`.
-/
protected lemma mul {q r : ℚ} (hq : q ≠ 0) (hr : r ≠ 0) :
  padic_val_rat p (q * r) = padic_val_rat p q + padic_val_rat p r :=
have q*r = (q.num * r.num) /. (↑q.denom * ↑r.denom), by rw_mod_cast rat.mul_num_denom,
have hq' : q.num /. q.denom ≠ 0, by rw rat.num_denom; exact hq,
have hr' : r.num /. r.denom ≠ 0, by rw rat.num_denom; exact hr,
have hp' : _root_.prime (p : ℤ), from nat.prime_iff_prime_int.1 p_prime,
begin
  rw [padic_val_rat.defn p (mul_ne_zero hq hr) this],
  conv_rhs { rw [←(@rat.num_denom q), padic_val_rat.defn p hq',
    ←(@rat.num_denom r), padic_val_rat.defn p hr'] },
  rw [multiplicity.mul' hp', multiplicity.mul' hp']; simp [add_comm, add_left_comm, sub_eq_add_neg]
end

/--
A rewrite lemma for `padic_val_rat p (q^k) with condition `q ≠ 0`.
-/
protected lemma pow {q : ℚ} (hq : q ≠ 0) {k : ℕ} :
    padic_val_rat p (q ^ k) = k * padic_val_rat p q :=
by induction k; simp [*, padic_val_rat.mul _ hq (pow_ne_zero _ hq),
  pow_succ, add_mul, add_comm]

/--
A rewrite lemma for `padic_val_rat p (q⁻¹)` with condition `q ≠ 0`.
-/
protected lemma inv {q : ℚ} (hq : q ≠ 0) :
  padic_val_rat p (q⁻¹) = -padic_val_rat p q :=
by rw [eq_neg_iff_add_eq_zero, ← padic_val_rat.mul p (inv_ne_zero hq) hq,
    inv_mul_cancel hq, padic_val_rat.one]

/--
A rewrite lemma for `padic_val_rat p (q / r)` with conditions `q ≠ 0`, `r ≠ 0`.
-/
protected lemma div {q r : ℚ} (hq : q ≠ 0) (hr : r ≠ 0) :
  padic_val_rat p (q / r) = padic_val_rat p q - padic_val_rat p r :=
by rw [div_eq_mul_inv, padic_val_rat.mul p hq (inv_ne_zero hr),
    padic_val_rat.inv p hr, sub_eq_add_neg]

/--
A condition for `padic_val_rat p (n₁ / d₁) ≤ padic_val_rat p (n₂ / d₂),
in terms of divisibility by `p^n`.
-/
lemma padic_val_rat_le_padic_val_rat_iff {n₁ n₂ d₁ d₂ : ℤ}
  (hn₁ : n₁ ≠ 0) (hn₂ : n₂ ≠ 0) (hd₁ : d₁ ≠ 0) (hd₂ : d₂ ≠ 0) :
  padic_val_rat p (n₁ /. d₁) ≤ padic_val_rat p (n₂ /. d₂) ↔
  ∀ (n : ℕ), ↑p ^ n ∣ n₁ * d₂ → ↑p ^ n ∣ n₂ * d₁ :=
have hf1 : finite (p : ℤ) (n₁ * d₂),
  from finite_int_prime_iff.2 (mul_ne_zero hn₁ hd₂),
have hf2 : finite (p : ℤ) (n₂ * d₁),
  from finite_int_prime_iff.2 (mul_ne_zero hn₂ hd₁),
  by conv {
    to_lhs,
    rw [padic_val_rat.defn p (rat.mk_ne_zero_of_ne_zero hn₁ hd₁) rfl,
      padic_val_rat.defn p (rat.mk_ne_zero_of_ne_zero hn₂ hd₂) rfl,
      sub_le_iff_le_add',
      ← add_sub_assoc,
      le_sub_iff_add_le],
    norm_cast,
    rw [← multiplicity.mul' (nat.prime_iff_prime_int.1 p_prime) hf1, add_comm,
      ← multiplicity.mul' (nat.prime_iff_prime_int.1 p_prime) hf2,
      enat.get_le_get, multiplicity_le_multiplicity_iff]
  }

/--
Sufficient conditions to show that the p-adic valuation of `q` is less than or equal to the
p-adic vlauation of `q + r`.
-/
theorem le_padic_val_rat_add_of_le {q r : ℚ}
  (hq : q ≠ 0) (hr : r ≠ 0) (hqr : q + r ≠ 0)
  (h : padic_val_rat p q ≤ padic_val_rat p r) :
  padic_val_rat p q ≤ padic_val_rat p (q + r) :=
have hqn : q.num ≠ 0, from rat.num_ne_zero_of_ne_zero hq,
have hqd : (q.denom : ℤ) ≠ 0, by exact_mod_cast rat.denom_ne_zero _,
have hrn : r.num ≠ 0, from rat.num_ne_zero_of_ne_zero hr,
have hrd : (r.denom : ℤ) ≠ 0, by exact_mod_cast rat.denom_ne_zero _,
have hqdv : q.num /. q.denom ≠ 0, from rat.mk_ne_zero_of_ne_zero hqn hqd,
have hrdv : r.num /. r.denom ≠ 0, from rat.mk_ne_zero_of_ne_zero hrn hrd,
have hqreq : q + r = (((q.num * r.denom + q.denom * r.num : ℤ)) /. (↑q.denom * ↑r.denom : ℤ)),
  from rat.add_num_denom _ _,
have hqrd : q.num * ↑(r.denom) + ↑(q.denom) * r.num ≠ 0,
  from rat.mk_num_ne_zero_of_ne_zero hqr hqreq,
begin
  conv_lhs { rw ←(@rat.num_denom q) },
  rw [hqreq, padic_val_rat_le_padic_val_rat_iff p hqn hqrd hqd (mul_ne_zero hqd hrd),
    ← multiplicity_le_multiplicity_iff, mul_left_comm,
    multiplicity.mul (nat.prime_iff_prime_int.1 p_prime), add_mul],
  rw [←(@rat.num_denom q), ←(@rat.num_denom r),
    padic_val_rat_le_padic_val_rat_iff p hqn hrn hqd hrd, ← multiplicity_le_multiplicity_iff] at h,
  calc _ ≤ min (multiplicity ↑p (q.num * ↑(r.denom) * ↑(q.denom)))
    (multiplicity ↑p (↑(q.denom) * r.num * ↑(q.denom))) : (le_min
    (by rw [@multiplicity.mul _ _ _ _ (_ * _) _ (nat.prime_iff_prime_int.1 p_prime), add_comm])
    (by rw [mul_assoc, @multiplicity.mul _ _ _ _ (q.denom : ℤ)
        (_ * _) (nat.prime_iff_prime_int.1 p_prime)];
      exact add_le_add_left' h))
    ... ≤ _ : min_le_multiplicity_add
end

/--
The minimum of the valuations of `q` and `r` is less than or equal to the valuation of `q + r`.
-/
theorem min_le_padic_val_rat_add {q r : ℚ}
  (hq : q ≠ 0) (hr : r ≠ 0) (hqr : q + r ≠ 0) :
  min (padic_val_rat p q) (padic_val_rat p r) ≤ padic_val_rat p (q + r) :=
(le_total (padic_val_rat p q) (padic_val_rat p r)).elim
  (λ h, by rw [min_eq_left h]; exact le_padic_val_rat_add_of_le _ hq hr hqr h)
  (λ h, by rw [min_eq_right h, add_comm]; exact le_padic_val_rat_add_of_le _ hr hq
    (by rwa add_comm) h)

end padic_val_rat
end padic_val_rat

/--
If `q ≠ 0`, the p-adic norm of a rational `q` is `p ^ (-(padic_val_rat p q))`.
If `q = 0`, the p-adic norm of `q` is 0.
-/
def padic_norm (p : ℕ) (q : ℚ) : ℚ :=
if q = 0 then 0 else (↑p : ℚ) ^ (-(padic_val_rat p q))

namespace padic_norm

section padic_norm
open padic_val_rat
variables (p : ℕ)

/--
Unfolds the definition of the p-adic norm of `q` when `q ≠ 0`.
-/
@[simp] protected lemma eq_fpow_of_nonzero {q : ℚ} (hq : q ≠ 0) :
  padic_norm p q = p ^ (-(padic_val_rat p q)) :=
by simp [hq, padic_norm]

/--
The p-adic norm is nonnegative.
-/
protected lemma nonneg (q : ℚ) : 0 ≤ padic_norm p q :=
if hq : q = 0 then by simp [hq, padic_norm]
else
  begin
    unfold padic_norm; split_ifs,
    apply fpow_nonneg_of_nonneg,
    exact_mod_cast nat.zero_le _
  end

/--
The p-adic norm of 0 is 0.
-/
@[simp] protected lemma zero : padic_norm p 0 = 0 := by simp [padic_norm]

/--
The p-adic norm of 1 is 1.
-/
@[simp] protected lemma one : padic_norm p 1 = 1 := by simp [padic_norm]

/--
The image of `padic_norm p` is {0} ∪ {p^(-n) | n ∈ ℤ}.
-/
protected theorem image {q : ℚ} (hq : q ≠ 0) : ∃ n : ℤ, padic_norm p q = p ^ (-n) :=
⟨ (padic_val_rat p q), by simp [padic_norm, hq] ⟩

variable [hp : fact p.prime]
include hp

/--
If `q ≠ 0`, then `padic_norm p q ≠ 0`.
-/
protected lemma nonzero {q : ℚ} (hq : q ≠ 0) : padic_norm p q ≠ 0 :=
begin
  rw padic_norm.eq_fpow_of_nonzero p hq,
  apply fpow_ne_zero_of_ne_zero,
  exact_mod_cast ne_of_gt hp.pos
end

/--
`padic_norm p` is symmetric.
-/
@[simp] protected lemma neg (q : ℚ) : padic_norm p (-q) = padic_norm p q :=
if hq : q = 0 then by simp [hq]
else by simp [padic_norm, hq, hp.one_lt]

/--
If the p-adic norm of `q` is 0, then `q` is 0.
-/
lemma zero_of_padic_norm_eq_zero {q : ℚ} (h : padic_norm p q = 0) : q = 0 :=
begin
  apply by_contradiction, intro hq,
  unfold padic_norm at h, rw if_neg hq at h,
  apply absurd h,
  apply fpow_ne_zero_of_ne_zero,
  exact_mod_cast hp.ne_zero
end

/--
The p-adic norm is multiplicative.
-/
@[simp] protected theorem mul (q r : ℚ) : padic_norm p (q*r) = padic_norm p q * padic_norm p r :=
if hq : q = 0 then
  by simp [hq]
else if hr : r = 0 then
  by simp [hr]
else
  have q*r ≠ 0, from mul_ne_zero hq hr,
  have (↑p : ℚ) ≠ 0, by simp [hp.ne_zero],
  by simp [padic_norm, *, padic_val_rat.mul, fpow_add this, mul_comm]

/--
The p-adic norm respects division.
-/
@[simp] protected theorem div (q r : ℚ) : padic_norm p (q / r) = padic_norm p q / padic_norm p r :=
if hr : r = 0 then by simp [hr] else
eq_div_of_mul_eq _ _ (padic_norm.nonzero _ hr) (by rw [←padic_norm.mul, div_mul_cancel _ hr])

/--
The p-adic norm of an integer is at most 1.
-/
protected theorem of_int (z : ℤ) : padic_norm p ↑z ≤ 1 :=
if hz : z = 0 then by simp [hz, zero_le_one] else
begin
  unfold padic_norm,
  rw [if_neg _],
  { refine fpow_le_one_of_nonpos _ _,
    { exact_mod_cast le_of_lt hp.one_lt, },
    { rw [padic_val_rat_of_int _ hp.ne_one hz, neg_nonpos],
      norm_cast, simp }},
  exact_mod_cast hz
end

private lemma nonarchimedean_aux {q r : ℚ} (h : padic_val_rat p q ≤ padic_val_rat p r) :
  padic_norm p (q + r) ≤ max (padic_norm p q) (padic_norm p r) :=
have hnqp : padic_norm p q ≥ 0, from padic_norm.nonneg _ _,
have hnrp : padic_norm p r ≥ 0, from padic_norm.nonneg _ _,
if hq : q = 0 then
  by simp [hq, max_eq_right hnrp, le_max_right]
else if hr : r = 0 then
  by simp [hr, max_eq_left hnqp, le_max_left]
else if hqr : q + r = 0 then
  le_trans (by simpa [hqr] using hnqp) (le_max_left _ _)
else
  begin
    unfold padic_norm, split_ifs,
    apply le_max_iff.2,
    left,
    apply fpow_le_of_le,
    { exact_mod_cast le_of_lt hp.one_lt },
    { apply neg_le_neg,
      have : padic_val_rat p q =
              min (padic_val_rat p q) (padic_val_rat p r),
        from (min_eq_left h).symm,
      rw this,
      apply min_le_padic_val_rat_add; assumption }
  end

/--
The p-adic norm is nonarchimedean: the norm of `p + q` is at most the max of the norm of `p` and
the norm of `q`.
-/
protected theorem nonarchimedean {q r : ℚ} :
  padic_norm p (q + r) ≤ max (padic_norm p q) (padic_norm p r) :=
begin
    wlog hle := le_total (padic_val_rat p q) (padic_val_rat p r) using [q r],
    exact nonarchimedean_aux p hle
end

/--
The p-adic norm respects the triangle inequality: the norm of `p + q` is at most the norm of `p`
plus the norm of `q`.
-/
theorem triangle_ineq (q r : ℚ) : padic_norm p (q + r) ≤ padic_norm p q + padic_norm p r :=
calc padic_norm p (q + r) ≤ max (padic_norm p q) (padic_norm p r) : padic_norm.nonarchimedean p
                       ... ≤ padic_norm p q + padic_norm p r :
                         max_le_add_of_nonneg (padic_norm.nonneg p _) (padic_norm.nonneg p _)

/--
The p-adic norm of a difference is at most the max of each component. Restates the archimedean
property of the p-adic norm.
-/
protected theorem sub {q r : ℚ} : padic_norm p (q - r) ≤ max (padic_norm p q) (padic_norm p r) :=
by rw [sub_eq_add_neg, ←padic_norm.neg p r]; apply padic_norm.nonarchimedean

/--
If the p-adic norms of `q` and `r` are different, then the norm of `q + r` is equal to the max of
the norms of `q` and `r`.
-/
lemma add_eq_max_of_ne {q r : ℚ} (hne : padic_norm p q ≠ padic_norm p r) :
  padic_norm p (q + r) = max (padic_norm p q) (padic_norm p r) :=
begin
  wlog hle := le_total (padic_norm p r) (padic_norm p q) using [q r],
  have hlt : padic_norm p r < padic_norm p q, from lt_of_le_of_ne hle hne.symm,
  have : padic_norm p q ≤ max (padic_norm p (q + r)) (padic_norm p r), from calc
   padic_norm p q = padic_norm p (q + r - r) : by congr; ring
               ... ≤ max (padic_norm p (q + r)) (padic_norm p (-r)) : padic_norm.nonarchimedean p
               ... = max (padic_norm p (q + r)) (padic_norm p r) : by simp,
  have hnge : padic_norm p r ≤ padic_norm p (q + r),
  { apply le_of_not_gt,
    intro hgt,
    rw max_eq_right_of_lt hgt at this,
    apply not_lt_of_ge this,
    assumption },
  have : padic_norm p q ≤ padic_norm p (q + r), by rwa [max_eq_left hnge] at this,
  apply _root_.le_antisymm,
  { apply padic_norm.nonarchimedean p },
  { rw max_eq_left_of_lt hlt,
    assumption }
end

/--
The p-adic norm is an absolute value: positive-definite and multiplicative, satisfying the triangle
inequality.
-/
instance : is_absolute_value (padic_norm p) :=
{ abv_nonneg := padic_norm.nonneg p,
  abv_eq_zero :=
    begin
      intros,
      constructor; intro,
      { apply zero_of_padic_norm_eq_zero p, assumption },
      { simp [*] }
    end,
  abv_add := padic_norm.triangle_ineq p,
  abv_mul := padic_norm.mul p }

/--
If `p^n` divides an integer `z`, then the p-adic norm of `z` is at most `p^(-n)`.
-/
lemma le_of_dvd {n : ℕ} {z : ℤ} (hd : ↑(p^n) ∣ z) : padic_norm p z ≤ ↑p ^ (-n : ℤ) :=
begin
  unfold padic_norm, split_ifs with hz hz,
  { apply fpow_nonneg_of_nonneg,
    exact_mod_cast le_of_lt hp.pos },
  { apply fpow_le_of_le,
    exact_mod_cast le_of_lt hp.one_lt,
    apply neg_le_neg,
    rw padic_val_rat_of_int _ hp.ne_one _,
    { norm_cast,
      rw [← enat.coe_le_coe, enat.coe_get],
      apply multiplicity.le_multiplicity_of_pow_dvd,
      exact_mod_cast hd },
    { exact_mod_cast hz }},
end

end padic_norm
end padic_norm
