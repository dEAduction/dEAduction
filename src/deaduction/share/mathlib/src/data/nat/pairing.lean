/-
Copyright (c) 2015 Microsoft Corporation. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Leonardo de Moura, Mario Carneiro

Elegant pairing function.
-/
import data.nat.sqrt
open prod decidable

namespace nat

/-- Pairing function for the natural numbers. -/
def mkpair (a b : ℕ) : ℕ :=
if a < b then b*b + a else a*a + a + b

/-- Unpairing function for the natural numbers. -/
def unpair (n : ℕ) : ℕ × ℕ :=
let s := sqrt n in
if n - s*s < s then (n - s*s, s) else (s, n - s*s - s)

@[simp] theorem mkpair_unpair (n : ℕ) : mkpair (unpair n).1 (unpair n).2 = n :=
let s := sqrt n in begin
  dsimp [unpair], change sqrt n with s,
  have sm : s * s + (n - s * s) = n := nat.add_sub_cancel' (sqrt_le _),
  by_cases h : n - s * s < s; simp [h, mkpair],
  { exact sm },
  { have hl : n - s*s - s ≤ s :=
      nat.sub_le_left_of_le_add (nat.sub_le_left_of_le_add $
      by rw ← add_assoc; apply sqrt_le_add),
    suffices : s * s + (s + (n - s * s - s)) = n, {simpa [not_lt_of_ge hl, add_assoc]},
    rwa [nat.add_sub_cancel' (le_of_not_gt h)] }
end

theorem mkpair_unpair' {n a b} (H : unpair n = (a, b)) : mkpair a b = n :=
by simpa [H] using mkpair_unpair n

@[simp] theorem unpair_mkpair (a b : ℕ) : unpair (mkpair a b) = (a, b) :=
begin
  by_cases a < b; simp [h, mkpair],
  { show unpair (b * b + a) = (a, b),
    have be : sqrt (b * b + a) = b,
    { rw sqrt_add_eq, exact le_trans (le_of_lt h) (le_add_left _ _) },
    simp [unpair, be, nat.add_sub_cancel, h] },
  { show unpair (a * a + a + b) = (a, b),
    have ae : sqrt (a * a + (a + b)) = a,
    { rw sqrt_add_eq, exact add_le_add_left (le_of_not_gt h) _ },
    simp [unpair, ae, not_lt_zero, add_assoc] }
end

theorem unpair_lt {n : ℕ} (n1 : 1 ≤ n) : (unpair n).1 < n :=
let s := sqrt n in begin
  simp [unpair], change sqrt n with s,
  by_cases h : n - s * s < s; simp [h],
  { exact lt_of_lt_of_le h (sqrt_le_self _) },
  { simp at h,
    have s0 : 0 < s := sqrt_pos.2 n1,
    exact lt_of_le_of_lt h (nat.sub_lt_self n1 (mul_pos s0 s0)) }
end

theorem unpair_le_left : ∀ (n : ℕ), (unpair n).1 ≤ n
| 0     := dec_trivial
| (n+1) := le_of_lt (unpair_lt (nat.succ_pos _))

theorem le_mkpair_left (a b : ℕ) : a ≤ mkpair a b :=
by simpa using unpair_le_left (mkpair a b)

theorem le_mkpair_right (a b : ℕ) : b ≤ mkpair a b :=
begin
  by_cases h : a < b; simp [mkpair, h],
  exact le_trans (le_mul_self _) (le_add_right _ _)
end

theorem unpair_le_right (n : ℕ) : (unpair n).2 ≤ n :=
by simpa using le_mkpair_right n.unpair.1 n.unpair.2

theorem mkpair_lt_mkpair_left {a₁ a₂} (b) (h : a₁ < a₂) : mkpair a₁ b < mkpair a₂ b :=
begin
  by_cases h₁ : a₁ < b; simp [mkpair, h₁, add_assoc],
  { by_cases h₂ : a₂ < b; simp [mkpair, h₂, h],
    simp at h₂,
    apply add_lt_add_of_le_of_lt,
    exact mul_self_le_mul_self h₂,
    exact lt_add_right _ _ _ h },
  { simp at h₁,
    simp [not_lt_of_gt (lt_of_le_of_lt h₁ h)],
    apply add_lt_add,
    exact mul_self_lt_mul_self h,
    apply add_lt_add_right; assumption }
end

theorem mkpair_lt_mkpair_right (a) {b₁ b₂} (h : b₁ < b₂) : mkpair a b₁ < mkpair a b₂ :=
begin
  by_cases h₁ : a < b₁; simp [mkpair, h₁, add_assoc],
  { simp [mkpair, lt_trans h₁ h, h],
    exact mul_self_lt_mul_self h },
  { by_cases h₂ : a < b₂; simp [mkpair, h₂, h],
    simp at h₁,
    rw [add_comm, add_comm _ a, add_assoc, add_lt_add_iff_left],
    rwa [add_comm, ← sqrt_lt, sqrt_add_eq],
    exact le_trans h₁ (le_add_left _ _) }
end

end nat
