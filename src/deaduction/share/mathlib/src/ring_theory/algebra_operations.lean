/-
Copyright (c) 2019 Kenny Lau. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Kenny Lau

Multiplication and division of submodules of an algebra.
-/
import ring_theory.algebra
import ring_theory.ideals
import algebra.pointwise

universes u v

open algebra

local attribute [instance] set.pointwise_mul_semiring

namespace submodule

variables {R : Type u} [comm_ring R]

section ring

variables {A : Type v} [ring A] [algebra R A]
variables (S T : set A) {M N P Q : submodule R A} {m n : A}

instance : has_one (submodule R A) :=
⟨submodule.map (of_id R A).to_linear_map (⊤ : ideal R)⟩

theorem one_eq_map_top :
  (1 : submodule R A) = submodule.map (of_id R A).to_linear_map (⊤ : ideal R) := rfl

theorem one_eq_span : (1 : submodule R A) = span R {1} :=
begin
  apply submodule.ext,
  intro a,
  erw [mem_map, mem_span_singleton],
  apply exists_congr,
  intro r,
  simpa [smul_def],
end

theorem one_le : (1 : submodule R A) ≤ P ↔ (1 : A) ∈ P :=
by simpa only [one_eq_span, span_le, set.singleton_subset_iff]

instance : has_mul (submodule R A) :=
⟨λ M N, ⨆ s : M, N.map $ algebra.lmul R A s.1⟩

theorem mul_mem_mul (hm : m ∈ M) (hn : n ∈ N) : m * n ∈ M * N :=
(le_supr _ ⟨m, hm⟩ : _ ≤ M * N) ⟨n, hn, rfl⟩

theorem mul_le : M * N ≤ P ↔ ∀ (m ∈ M) (n ∈ N), m * n ∈ P :=
⟨λ H m hm n hn, H $ mul_mem_mul hm hn,
λ H, supr_le $ λ ⟨m, hm⟩, map_le_iff_le_comap.2 $ λ n hn, H m hm n hn⟩

@[elab_as_eliminator] protected theorem mul_induction_on
  {C : A → Prop} {r : A} (hr : r ∈ M * N)
  (hm : ∀ (m ∈ M) (n ∈ N), C (m * n))
  (h0 : C 0) (ha : ∀ x y, C x → C y → C (x + y))
  (hs : ∀ (r : R) x, C x → C (r • x)) : C r :=
(@mul_le _ _ _ _ _ _ _ ⟨C, h0, ha, hs⟩).2 hm hr

variables R
theorem span_mul_span : span R S * span R T = span R (S * T) :=
begin
  apply le_antisymm,
  { rw mul_le, intros a ha b hb,
    apply span_induction ha,
    work_on_goal 0 { intros, apply span_induction hb,
      work_on_goal 0 { intros, exact subset_span ⟨_, ‹_›, _, ‹_›, rfl⟩ } },
    all_goals { intros, simp only [mul_zero, zero_mul, zero_mem,
        left_distrib, right_distrib, mul_smul_comm, smul_mul_assoc],
      try {apply add_mem _ _ _}, try {apply smul_mem _ _ _} }, assumption' },
  { rw span_le, rintros _ ⟨a, ha, b, hb, rfl⟩,
    exact mul_mem_mul (subset_span ha) (subset_span hb) }
end
variables {R}

variables (M N P Q)
protected theorem mul_assoc : (M * N) * P = M * (N * P) :=
le_antisymm (mul_le.2 $ λ mn hmn p hp, suffices M * N ≤ (M * (N * P)).comap ((algebra.lmul R A).flip p), from this hmn,
  mul_le.2 $ λ m hm n hn, show m * n * p ∈ M * (N * P), from
  (mul_assoc m n p).symm ▸ mul_mem_mul hm (mul_mem_mul hn hp))
(mul_le.2 $ λ m hm np hnp, suffices N * P ≤ (M * N * P).comap (algebra.lmul R A m), from this hnp,
  mul_le.2 $ λ n hn p hp, show m * (n * p) ∈ M * N * P, from
  mul_assoc m n p ▸ mul_mem_mul (mul_mem_mul hm hn) hp)

@[simp] theorem mul_bot : M * ⊥ = ⊥ :=
eq_bot_iff.2 $ mul_le.2 $ λ m hm n hn, by rw [submodule.mem_bot] at hn ⊢; rw [hn, mul_zero]

@[simp] theorem bot_mul : ⊥ * M = ⊥ :=
eq_bot_iff.2 $ mul_le.2 $ λ m hm n hn, by rw [submodule.mem_bot] at hm ⊢; rw [hm, zero_mul]

@[simp] protected theorem one_mul : (1 : submodule R A) * M = M :=
by { conv_lhs { rw [one_eq_span, ← span_eq M] }, erw [span_mul_span, one_mul, span_eq] }

@[simp] protected theorem mul_one : M * 1 = M :=
by { conv_lhs { rw [one_eq_span, ← span_eq M] }, erw [span_mul_span, mul_one, span_eq] }

variables {M N P Q}

@[mono] theorem mul_le_mul (hmp : M ≤ P) (hnq : N ≤ Q) : M * N ≤ P * Q :=
mul_le.2 $ λ m hm n hn, mul_mem_mul (hmp hm) (hnq hn)

theorem mul_le_mul_left (h : M ≤ N) : M * P ≤ N * P :=
mul_le_mul h (le_refl P)

theorem mul_le_mul_right (h : N ≤ P) : M * N ≤ M * P :=
mul_le_mul (le_refl M) h

variables (M N P)
theorem mul_sup : M * (N ⊔ P) = M * N ⊔ M * P :=
le_antisymm (mul_le.2 $ λ m hm np hnp, let ⟨n, hn, p, hp, hnp⟩ := mem_sup.1 hnp in
  mem_sup.2 ⟨_, mul_mem_mul hm hn, _, mul_mem_mul hm hp, hnp ▸ (mul_add m n p).symm⟩)
(sup_le (mul_le_mul_right le_sup_left) (mul_le_mul_right le_sup_right))

theorem sup_mul : (M ⊔ N) * P = M * P ⊔ N * P :=
le_antisymm (mul_le.2 $ λ mn hmn p hp, let ⟨m, hm, n, hn, hmn⟩ := mem_sup.1 hmn in
  mem_sup.2 ⟨_, mul_mem_mul hm hp, _, mul_mem_mul hn hp, hmn ▸ (add_mul m n p).symm⟩)
(sup_le (mul_le_mul_left le_sup_left) (mul_le_mul_left le_sup_right))

lemma mul_subset_mul :
  (↑M : set A) * (↑N : set A) ⊆ (↑(M * N) : set A) :=
begin
  rintros _ ⟨i, hi, j, hj, rfl⟩,
  exact mul_mem_mul hi hj
end

lemma map_mul {A'} [ring A'] [algebra R A'] (f : A →ₐ[R] A') :
  map f.to_linear_map (M * N) = map f.to_linear_map M * map f.to_linear_map N :=
calc map f.to_linear_map (M * N)
    = ⨆ (i : M), (N.map (lmul R A i)).map f.to_linear_map : map_supr _ _
... = map f.to_linear_map M * map f.to_linear_map N  :
  begin
    apply congr_arg Sup,
    ext S,
    split; rintros ⟨y, hy⟩,
    { use [f y, mem_map.mpr ⟨y.1, y.2, rfl⟩],
      refine trans _ hy,
      ext,
      simp },
    { obtain ⟨y', hy', fy_eq⟩ := mem_map.mp y.2,
      use [y', hy'],
      refine trans _ hy,
      rw f.to_linear_map_apply at fy_eq,
      ext,
      simp [fy_eq] }
  end

variables {M N P}

instance : semiring (submodule R A) :=
{ one_mul       := submodule.one_mul,
  mul_one       := submodule.mul_one,
  mul_assoc     := submodule.mul_assoc,
  zero_mul      := bot_mul,
  mul_zero      := mul_bot,
  left_distrib  := mul_sup,
  right_distrib := sup_mul,
  ..submodule.add_comm_monoid_submodule,
  ..submodule.has_one,
  ..submodule.has_mul }

variables (M)

lemma pow_subset_pow {n : ℕ} :
  (↑M : set A)^n ⊆ ↑(M^n : submodule R A) :=
begin
  induction n with n ih,
  { erw [pow_zero, pow_zero, set.singleton_subset_iff], rw [mem_coe, ← one_le], exact le_refl _ },
  { rw [pow_succ, pow_succ],
    refine set.subset.trans (set.pointwise_mul_subset_mul (set.subset.refl _) ih) _,
    apply mul_subset_mul }
end

instance span.is_semiring_hom : is_semiring_hom (submodule.span R : set A → submodule R A) :=
{ map_zero := span_empty,
  map_one := show _ = map _ ⊤,
    by erw [← ideal.span_singleton_one, ← span_image, set.image_singleton, alg_hom.map_one]; refl,
  map_add := span_union,
  map_mul := λ s t, by erw [span_mul_span, set.pointwise_mul_eq_image] }

end ring

section comm_ring

variables {A : Type v} [comm_ring A] [algebra R A]
variables {M N : submodule R A} {m n : A}

theorem mul_mem_mul_rev (hm : m ∈ M) (hn : n ∈ N) : n * m ∈ M * N :=
mul_comm m n ▸ mul_mem_mul hm hn

variables (M N)
protected theorem mul_comm : M * N = N * M :=
le_antisymm (mul_le.2 $ λ r hrm s hsn, mul_mem_mul_rev hsn hrm)
(mul_le.2 $ λ r hrn s hsm, mul_mem_mul_rev hsm hrn)

instance : comm_semiring (submodule R A) :=
{ mul_comm := submodule.mul_comm,
  .. submodule.semiring }

variables (R A)

instance semimodule_set : semimodule (set A) (submodule R A) :=
{ smul := λ s P, span R s * P,
  smul_add := λ _ _ _, mul_add _ _ _,
  add_smul := λ s t P, show span R (s ⊔ t) * P = _, by { erw [span_union, right_distrib] },
  mul_smul := λ s t P, show _ = _ * (_ * _),
    by { rw [← mul_assoc, span_mul_span, set.pointwise_mul_eq_image] },
  one_smul := λ P, show span R {(1 : A)} * P = _,
    by { conv_lhs {erw ← span_eq P}, erw [span_mul_span, one_mul, span_eq] },
  zero_smul := λ P, show span R ∅ * P = ⊥, by erw [span_empty, bot_mul],
  smul_zero := λ _, mul_bot _ }


variables {R A}

lemma smul_def {s : set A} {P : submodule R A} :
  s • P = span R s * P := rfl

lemma smul_le_smul {s t : set A} {M N : submodule R A} (h₁ : s ≤ t) (h₂ : M ≤ N) :
  s • M ≤ t • N :=
mul_le_mul (span_mono h₁) h₂

lemma smul_singleton (a : A) (M : submodule R A) :
  ({a} : set A) • M = M.map (lmul_left _ _ a) :=
begin
  conv_lhs {rw ← span_eq M},
  change span _ _ * span _ _ = _,
  rw [span_mul_span],
  apply le_antisymm,
  { rw span_le,
    rintros _ ⟨b, hb, m, hm, rfl⟩,
    erw [mem_map, set.mem_singleton_iff.mp hb],
    exact ⟨m, hm, rfl⟩ },
  { rintros _ ⟨m, hm, rfl⟩,
    exact subset_span ⟨a, set.mem_singleton a, m, hm, rfl⟩ }
end

section quotient

local attribute [instance] set.smul_set_action

/-- The elements of `I / J` are the `x` such that `x • J ⊆ I`.

In fact, we define `x ∈ I / J` to be `∀ y ∈ J, x * y ∈ I` (see `mem_div_iff_forall_mul_mem`),
which is equivalent to `x • J ⊆ I` (see `mem_div_iff_smul_subset`), but nicer to use in proofs.

This is the general form of the ideal quotient, traditionally written $I : J$.
-/
instance : has_div (submodule R A) :=
⟨ λ I J, {
  carrier   := { x | ∀ y ∈ J, x * y ∈ I },
  zero_mem' := λ y hy, by { rw zero_mul, apply submodule.zero_mem },
  add_mem'  := λ a b ha hb y hy, by { rw add_mul, exact submodule.add_mem _ (ha _ hy) (hb _ hy) },
  smul_mem' := λ r x hx y hy, by { rw algebra.smul_mul_assoc,
    exact submodule.smul_mem _ _ (hx _ hy) } } ⟩

lemma mem_div_iff_forall_mul_mem {x : A} {I J : submodule R A} :
  x ∈ I / J ↔ ∀ y ∈ J, x * y ∈ I :=
iff.refl _

lemma mem_div_iff_smul_subset {x : A} {I J : submodule R A} : x ∈ I / J ↔ x • (J : set A) ⊆ I :=
⟨ λ h y ⟨y', hy', y_eq_xy'⟩, by { rw y_eq_xy', apply h, assumption },
  λ h y hy, h (set.smul_mem_smul_set _ hy)⟩

lemma le_div_iff {I J K : submodule R A} : I ≤ J / K ↔ ∀ (x ∈ I) (z ∈ K), x * z ∈ J := iff.refl _
end quotient

end comm_ring

end submodule
