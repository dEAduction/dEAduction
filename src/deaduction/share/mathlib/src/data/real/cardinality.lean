/-
Copyright (c) 2019 Floris van Doorn. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Floris van Doorn

The cardinality of the reals.
-/
import set_theory.ordinal
import analysis.specific_limits
import data.rat.denumerable

open nat set
noncomputable theory
namespace cardinal

variables {c : ℝ} {f g : ℕ → bool} {n : ℕ}

def cantor_function_aux (c : ℝ) (f : ℕ → bool) (n : ℕ) : ℝ := cond (f n) (c ^ n) 0

@[simp] lemma cantor_function_aux_tt (h : f n = tt) : cantor_function_aux c f n = c ^ n :=
by simp [cantor_function_aux, h]

@[simp] lemma cantor_function_aux_ff (h : f n = ff) : cantor_function_aux c f n = 0 :=
by simp [cantor_function_aux, h]

lemma cantor_function_aux_nonneg (h : 0 ≤ c) : 0 ≤ cantor_function_aux c f n :=
by { cases h' : f n; simp [h'], apply pow_nonneg h }

lemma cantor_function_aux_eq (h : f n = g n) :
  cantor_function_aux c f n = cantor_function_aux c g n :=
by simp [cantor_function_aux, h]

lemma cantor_function_aux_succ (f : ℕ → bool) :
  (λ n, cantor_function_aux c f (n + 1)) = λ n, c * cantor_function_aux c (λ n, f (n + 1)) n :=
by { ext n, cases h : f (n + 1); simp [h, pow_succ] }

lemma summable_cantor_function (f : ℕ → bool) (h1 : 0 ≤ c) (h2 : c < 1) :
  summable (cantor_function_aux c f) :=
begin
  apply (summable_geometric_of_lt_1 h1 h2).summable_of_eq_zero_or_self,
  intro n, cases h : f n; simp [h]
end

def cantor_function (c : ℝ) (f : ℕ → bool) : ℝ := ∑' n, cantor_function_aux c f n

lemma cantor_function_le (h1 : 0 ≤ c) (h2 : c < 1) (h3 : ∀ n, f n → g n) :
  cantor_function c f ≤ cantor_function c g :=
begin
  apply tsum_le_tsum _ (summable_cantor_function f h1 h2) (summable_cantor_function g h1 h2),
  intro n, cases h : f n, simp [h, cantor_function_aux_nonneg h1],
  replace h3 : g n = tt := h3 n h, simp [h, h3]
end

lemma cantor_function_succ (f : ℕ → bool) (h1 : 0 ≤ c) (h2 : c < 1) :
  cantor_function c f = cond (f 0) 1 0 + c * cantor_function c (λ n, f (n+1)) :=
begin
  rw [cantor_function, tsum_eq_zero_add (summable_cantor_function f h1 h2)],
  rw [cantor_function_aux_succ, tsum_mul_left _ (summable_cantor_function _ h1 h2)], refl
end

lemma increasing_cantor_function (h1 : 0 < c) (h2 : c < 1 / 2) {n : ℕ} {f g : ℕ → bool}
  (hn : ∀(k < n), f k = g k) (fn : f n = ff) (gn : g n = tt) :
  cantor_function c f < cantor_function c g :=
begin
  have h3 : c < 1, { apply lt_trans h2, norm_num },
  induction n with n ih generalizing f g,
  { let f_max : ℕ → bool := λ n, nat.rec ff (λ _ _, tt) n,
    have hf_max : ∀n, f n → f_max n,
    { intros n hn, cases n, rw [fn] at hn, contradiction, apply rfl },
    let g_min : ℕ → bool := λ n, nat.rec tt (λ _ _, ff) n,
    have hg_min : ∀n, g_min n → g n,
    { intros n hn, cases n, rw [gn], apply rfl, contradiction },
    apply lt_of_le_of_lt (cantor_function_le (le_of_lt h1) h3 hf_max),
    apply lt_of_lt_of_le _ (cantor_function_le (le_of_lt h1) h3 hg_min),
    have : c / (1 - c) < 1,
    { rw [div_lt_one_iff_lt, lt_sub_iff_add_lt],
      { convert add_lt_add h2 h2, norm_num },
      rwa sub_pos },
    convert this,
    { rw [cantor_function_succ _ (le_of_lt h1) h3, div_eq_mul_inv,
          ←tsum_geometric_of_lt_1 (le_of_lt h1) h3],
      apply zero_add },
    { apply tsum_eq_single 0, intros n hn, cases n, contradiction, refl, apply_instance }},
  rw [cantor_function_succ f (le_of_lt h1) h3, cantor_function_succ g (le_of_lt h1) h3],
  rw [hn 0 $ zero_lt_succ n],
  apply add_lt_add_left, rw mul_lt_mul_left h1, exact ih (λ k hk, hn _ $ succ_lt_succ hk) fn gn
end

lemma cantor_function_injective (h1 : 0 < c) (h2 : c < 1 / 2) :
  function.injective (cantor_function c) :=
begin
  intros f g hfg, classical, by_contra h, revert hfg,
  have : ∃n, f n ≠ g n,
  { rw [←not_forall], intro h', apply h, ext, apply h' },
  let n := nat.find this,
  have hn : ∀ (k : ℕ), k < n → f k = g k,
  { intros k hk, apply of_not_not, exact nat.find_min this hk },
  cases fn : f n,
  { apply ne_of_lt, refine increasing_cantor_function h1 h2 hn fn _,
    apply eq_tt_of_not_eq_ff, rw [←fn], apply ne.symm, exact nat.find_spec this },
  { apply ne_of_gt, refine increasing_cantor_function h1 h2 (λ k hk, (hn k hk).symm) _ fn,
    apply eq_ff_of_not_eq_tt, rw [←fn], apply ne.symm, exact nat.find_spec this }
end

lemma mk_real : mk ℝ = 2 ^ omega.{0} :=
begin
  apply le_antisymm,
  { dsimp [real], apply le_trans mk_quotient_le, apply le_trans (mk_subtype_le _),
    rw [←power_def, mk_nat, mk_rat, power_self_eq (le_refl _)] },
  { convert mk_le_of_injective (cantor_function_injective _ _),
    rw [←power_def, mk_bool, mk_nat], exact 1 / 3, norm_num, norm_num }
end

lemma not_countable_real : ¬ countable (set.univ : set ℝ) :=
by { rw [countable_iff, not_le, mk_univ, mk_real], apply cantor }

end cardinal
