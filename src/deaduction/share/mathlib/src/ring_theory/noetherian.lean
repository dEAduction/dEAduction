/-
Copyright (c) 2018 Mario Carneiro and Kevin Buzzard. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mario Carneiro, Kevin Buzzard
-/
import ring_theory.ideal_operations
import linear_algebra.basis

/-!
# Noetherian rings and modules

The following are equivalent for a module M over a ring R:
1. Every increasing chain of submodule M₁ ⊆ M₂ ⊆ M₃ ⊆ ⋯ eventually stabilises.
2. Every submodule is finitely generated.

A module satisfying these equivalent conditions is said to be a *Noetherian* R-module.
A ring is a *Noetherian ring* if it is Noetherian as a module over itself.

## Main definitions

Let `R` be a ring and let `M` and `P` be `R`-modules. Let `N` be an `R`-submodule of `M`.

* `fg N : Prop` is the assertion that `N` is finitely generated as an `R`-module.

* `is_noetherian R M` is the proposition that `M` is a Noetherian `R`-module. It is a class,
  implemented as the predicate that all `R`-submodules of `M` are finitely generated.

## Main statements

* `exists_sub_one_mem_and_smul_eq_zero_of_fg_of_le_smul` is Nakayama's lemma, in the following form:
  if N is a finitely generated submodule of an ambient R-module M and I is an ideal of R
  such that N ⊆ IN, then there exists r ∈ 1 + I such that rN = 0.

* `is_noetherian_iff_well_founded` is the theorem that an R-module M is Noetherian iff
  `>` is well-founded on `submodule R M`.

Note that the Hilbert basis theorem, that if a commutative ring R is Noetherian then so is R[X],
is proved in `ring_theory.polynomial`.

## References

* [M. F. Atiyah and I. G. Macdonald, *Introduction to commutative algebra*][atiyah-macdonald]

## Tags

Noetherian, noetherian, Noetherian ring, Noetherian module, noetherian ring, noetherian module

-/

open set
open_locale big_operators

namespace submodule
variables {R : Type*} {M : Type*} [ring R] [add_comm_group M] [module R M]

/-- A submodule of `M` is finitely generated if it is the span of a finite subset of `M`. -/
def fg (N : submodule R M) : Prop := ∃ S : finset M, submodule.span R ↑S = N

theorem fg_def {N : submodule R M} :
  N.fg ↔ ∃ S : set M, finite S ∧ span R S = N :=
⟨λ ⟨t, h⟩, ⟨_, finset.finite_to_set t, h⟩, begin
  rintro ⟨t', h, rfl⟩,
  rcases finite.exists_finset_coe h with ⟨t, rfl⟩,
  exact ⟨t, rfl⟩
end⟩

/-- Nakayama's Lemma. Atiyah-Macdonald 2.5, Eisenbud 4.7, Matsumura 2.2, Stacks 00DV -/
theorem exists_sub_one_mem_and_smul_eq_zero_of_fg_of_le_smul {R : Type*} [comm_ring R]
  {M : Type*} [add_comm_group M] [module R M]
  (I : ideal R) (N : submodule R M) (hn : N.fg) (hin : N ≤ I • N) :
  ∃ r : R, r - 1 ∈ I ∧ ∀ n ∈ N, r • n = (0 : M) :=
begin
  rw fg_def at hn, rcases hn with ⟨s, hfs, hs⟩,
  have : ∃ r : R, r - 1 ∈ I ∧ N ≤ (I • span R s).comap (linear_map.lsmul R M r) ∧ s ⊆ N,
  { refine ⟨1, _, _, _⟩,
    { rw sub_self, exact I.zero_mem },
    { rw [hs], intros n hn, rw [mem_comap], change (1:R) • n ∈ I • N, rw one_smul, exact hin hn },
    { rw [← span_le, hs], exact le_refl N } },
  clear hin hs, revert this,
  refine set.finite.dinduction_on hfs (λ H, _) (λ i s his hfs ih H, _),
  { rcases H with ⟨r, hr1, hrn, hs⟩, refine ⟨r, hr1, λ n hn, _⟩, specialize hrn hn,
    rwa [mem_comap, span_empty, smul_bot, mem_bot] at hrn },
  apply ih, rcases H with ⟨r, hr1, hrn, hs⟩,
  rw [← set.singleton_union, span_union, smul_sup] at hrn,
  rw [set.insert_subset] at hs,
  have : ∃ c : R, c - 1 ∈ I ∧ c • i ∈ I • span R s,
  { specialize hrn hs.1, rw [mem_comap, mem_sup] at hrn,
    rcases hrn with ⟨y, hy, z, hz, hyz⟩, change y + z = r • i at hyz,
    rw mem_smul_span_singleton at hy, rcases hy with ⟨c, hci, rfl⟩,
    use r-c, split,
    { rw [sub_right_comm], exact I.sub_mem hr1 hci },
    { rw [sub_smul, ← hyz, add_sub_cancel'], exact hz } },
  rcases this with ⟨c, hc1, hci⟩, refine ⟨c * r, _, _, hs.2⟩,
  { rw [← ideal.quotient.eq, ideal.quotient.mk_one] at hr1 hc1 ⊢,
    rw [ideal.quotient.mk_mul, hc1, hr1, mul_one] },
  { intros n hn, specialize hrn hn, rw [mem_comap, mem_sup] at hrn,
    rcases hrn with ⟨y, hy, z, hz, hyz⟩, change y + z = r • n at hyz,
    rw mem_smul_span_singleton at hy, rcases hy with ⟨d, hdi, rfl⟩,
    change _ • _ ∈ I • span R s,
    rw [mul_smul, ← hyz, smul_add, smul_smul, mul_comm, mul_smul],
    exact add_mem _ (smul_mem _ _ hci) (smul_mem _ _ hz) }
end

theorem fg_bot : (⊥ : submodule R M).fg :=
⟨∅, by rw [finset.coe_empty, span_empty]⟩

theorem fg_sup {N₁ N₂ : submodule R M}
  (hN₁ : N₁.fg) (hN₂ : N₂.fg) : (N₁ ⊔ N₂).fg :=
let ⟨t₁, ht₁⟩ := fg_def.1 hN₁, ⟨t₂, ht₂⟩ := fg_def.1 hN₂ in
fg_def.2 ⟨t₁ ∪ t₂, ht₁.1.union ht₂.1, by rw [span_union, ht₁.2, ht₂.2]⟩

variables {P : Type*} [add_comm_group P] [module R P]
variables {f : M →ₗ[R] P}

theorem fg_map {N : submodule R M} (hs : N.fg) : (N.map f).fg :=
let ⟨t, ht⟩ := fg_def.1 hs in fg_def.2 ⟨f '' t, ht.1.image _, by rw [span_image, ht.2]⟩

theorem fg_prod {sb : submodule R M} {sc : submodule R P}
  (hsb : sb.fg) (hsc : sc.fg) : (sb.prod sc).fg :=
let ⟨tb, htb⟩ := fg_def.1 hsb, ⟨tc, htc⟩ := fg_def.1 hsc in
fg_def.2 ⟨prod.inl '' tb ∪ prod.inr '' tc,
  (htb.1.image _).union (htc.1.image _),
  by rw [linear_map.span_inl_union_inr, htb.2, htc.2]⟩

variable (f)
/-- If 0 → M' → M → M'' → 0 is exact and M' and M'' are
finitely generated then so is M. -/
theorem fg_of_fg_map_of_fg_inf_ker {s : submodule R M}
  (hs1 : (s.map f).fg) (hs2 : (s ⊓ f.ker).fg) : s.fg :=
begin
  haveI := classical.dec_eq R, haveI := classical.dec_eq M, haveI := classical.dec_eq P,
  cases hs1 with t1 ht1, cases hs2 with t2 ht2,
  have : ∀ y ∈ t1, ∃ x ∈ s, f x = y,
  { intros y hy,
    have : y ∈ map f s, { rw ← ht1, exact subset_span hy },
    rcases mem_map.1 this with ⟨x, hx1, hx2⟩,
    exact ⟨x, hx1, hx2⟩ },
  have : ∃ g : P → M, ∀ y ∈ t1, g y ∈ s ∧ f (g y) = y,
  { choose g hg1 hg2,
    existsi λ y, if H : y ∈ t1 then g y H else 0,
    intros y H, split,
    { simp only [dif_pos H], apply hg1 },
    { simp only [dif_pos H], apply hg2 } },
  cases this with g hg, clear this,
  existsi t1.image g ∪ t2,
  rw [finset.coe_union, span_union, finset.coe_image],
  apply le_antisymm,
  { refine sup_le (span_le.2 $ image_subset_iff.2 _) (span_le.2 _),
    { intros y hy, exact (hg y hy).1 },
    { intros x hx, have := subset_span hx,
      rw ht2 at this,
      exact this.1 } },
  intros x hx,
  have : f x ∈ map f s, { rw mem_map, exact ⟨x, hx, rfl⟩ },
  rw [← ht1,← set.image_id ↑t1, finsupp.mem_span_iff_total] at this,
  rcases this with ⟨l, hl1, hl2⟩,
  refine mem_sup.2 ⟨(finsupp.total M M R id).to_fun ((finsupp.lmap_domain R R g : (P →₀ R) → M →₀ R) l), _,
    x - finsupp.total M M R id ((finsupp.lmap_domain R R g : (P →₀ R) → M →₀ R) l),
    _, add_sub_cancel'_right _ _⟩,
  { rw [← set.image_id (g '' ↑t1), finsupp.mem_span_iff_total], refine ⟨_, _, rfl⟩,
    haveI : inhabited P := ⟨0⟩,
    rw [← finsupp.lmap_domain_supported _ _ g, mem_map],
    refine ⟨l, hl1, _⟩,
    refl, },
  rw [ht2, mem_inf], split,
  { apply s.sub_mem hx,
    rw [finsupp.total_apply, finsupp.lmap_domain_apply, finsupp.sum_map_domain_index],
    refine s.sum_mem _,
    { intros y hy, exact s.smul_mem _ (hg y (hl1 hy)).1 },
    { exact zero_smul _ }, { exact λ _ _ _, add_smul _ _ _ } },
  { rw [linear_map.mem_ker, f.map_sub, ← hl2],
    rw [finsupp.total_apply, finsupp.total_apply, finsupp.lmap_domain_apply],
    rw [finsupp.sum_map_domain_index, finsupp.sum, finsupp.sum, f.map_sum],
    rw sub_eq_zero,
    refine finset.sum_congr rfl (λ y hy, _),
    unfold id,
    rw [f.map_smul, (hg y (hl1 hy)).2],
    { exact zero_smul _ }, { exact λ _ _ _, add_smul _ _ _ } }
end

end submodule

/--
`is_noetherian R M` is the proposition that `M` is a Noetherian `R`-module,
implemented as the predicate that all `R`-submodules of `M` are finitely generated.
-/
class is_noetherian (R M) [ring R] [add_comm_group M] [module R M] : Prop :=
(noetherian : ∀ (s : submodule R M), s.fg)

section
variables {R : Type*} {M : Type*} {P : Type*}
variables [ring R] [add_comm_group M] [add_comm_group P]
variables [module R M] [module R P]
open is_noetherian
include R

theorem is_noetherian_submodule {N : submodule R M} :
  is_noetherian R N ↔ ∀ s : submodule R M, s ≤ N → s.fg :=
⟨λ ⟨hn⟩, λ s hs, have s ≤ N.subtype.range, from (N.range_subtype).symm ▸ hs,
  linear_map.map_comap_eq_self this ▸ submodule.fg_map (hn _),
λ h, ⟨λ s, submodule.fg_of_fg_map_of_fg_inf_ker N.subtype (h _ $ submodule.map_subtype_le _ _) $
  by rw [submodule.ker_subtype, inf_bot_eq]; exact submodule.fg_bot⟩⟩

theorem is_noetherian_submodule_left {N : submodule R M} :
  is_noetherian R N ↔ ∀ s : submodule R M, (N ⊓ s).fg :=
is_noetherian_submodule.trans
⟨λ H s, H _ inf_le_left, λ H s hs, (inf_of_le_right hs) ▸ H _⟩

theorem is_noetherian_submodule_right {N : submodule R M} :
  is_noetherian R N ↔ ∀ s : submodule R M, (s ⊓ N).fg :=
is_noetherian_submodule.trans
⟨λ H s, H _ inf_le_right, λ H s hs, (inf_of_le_left hs) ▸ H _⟩

variable (M)
theorem is_noetherian_of_surjective (f : M →ₗ[R] P) (hf : f.range = ⊤)
  [is_noetherian R M] : is_noetherian R P :=
⟨λ s, have (s.comap f).map f = s, from linear_map.map_comap_eq_self $ hf.symm ▸ le_top,
this ▸ submodule.fg_map $ noetherian _⟩
variable {M}

theorem is_noetherian_of_linear_equiv (f : M ≃ₗ[R] P)
  [is_noetherian R M] : is_noetherian R P :=
is_noetherian_of_surjective _ f.to_linear_map f.range

instance is_noetherian_prod [is_noetherian R M]
  [is_noetherian R P] : is_noetherian R (M × P) :=
⟨λ s, submodule.fg_of_fg_map_of_fg_inf_ker (linear_map.snd R M P) (noetherian _) $
have s ⊓ linear_map.ker (linear_map.snd R M P) ≤ linear_map.range (linear_map.inl R M P),
from λ x ⟨hx1, hx2⟩, ⟨x.1, trivial, prod.ext rfl $ eq.symm $ linear_map.mem_ker.1 hx2⟩,
linear_map.map_comap_eq_self this ▸ submodule.fg_map (noetherian _)⟩

instance is_noetherian_pi {R ι : Type*} {M : ι → Type*} [ring R]
  [Π i, add_comm_group (M i)] [Π i, module R (M i)] [fintype ι]
  [∀ i, is_noetherian R (M i)] : is_noetherian R (Π i, M i) :=
begin
  haveI := classical.dec_eq ι,
  suffices : ∀ s : finset ι, is_noetherian R (Π i : (↑s : set ι), M i),
  { letI := this finset.univ,
    refine @is_noetherian_of_linear_equiv _ _ _ _ _ _ _ _
      ⟨_, _, _, _, _, _⟩ (this finset.univ),
    { exact λ f i, f ⟨i, finset.mem_univ _⟩ },
    { intros, ext, refl },
    { intros, ext, refl },
    { exact λ f i, f i.1 },
    { intro, ext ⟨⟩, refl },
    { intro, ext i, refl } },
  intro s,
  induction s using finset.induction with a s has ih,
  { split, intro s, convert submodule.fg_bot, apply eq_bot_iff.2,
    intros x hx, refine (submodule.mem_bot R).2 _, ext i, cases i.2 },
  refine @is_noetherian_of_linear_equiv _ _ _ _ _ _ _ _
    ⟨_, _, _, _, _, _⟩ (@is_noetherian_prod _ (M a) _ _ _ _ _ _ _ ih),
  { exact λ f i, or.by_cases (finset.mem_insert.1 i.2)
      (λ h : i.1 = a, show M i.1, from (eq.rec_on h.symm f.1))
      (λ h : i.1 ∈ s, show M i.1, from f.2 ⟨i.1, h⟩) },
  { intros f g, ext i, unfold or.by_cases, cases i with i hi,
    rcases finset.mem_insert.1 hi with rfl | h,
    { change _ = _ + _, simp only [dif_pos], refl },
    { change _ = _ + _, have : ¬i = a, { rintro rfl, exact has h },
      simp only [dif_neg this, dif_pos h], refl } },
  { intros c f, ext i, unfold or.by_cases, cases i with i hi,
    rcases finset.mem_insert.1 hi with rfl | h,
    { change _ = c • _, simp only [dif_pos], refl },
    { change _ = c • _, have : ¬i = a, { rintro rfl, exact has h },
      simp only [dif_neg this, dif_pos h], refl } },
  { exact λ f, (f ⟨a, finset.mem_insert_self _ _⟩, λ i, f ⟨i.1, finset.mem_insert_of_mem i.2⟩) },
  { intro f, apply prod.ext,
    { simp only [or.by_cases, dif_pos] },
    { ext ⟨i, his⟩,
      have : ¬i = a, { rintro rfl, exact has his },
      dsimp only [or.by_cases], change i ∈ s at his,
      rw [dif_neg this, dif_pos his] } },
  { intro f, ext ⟨i, hi⟩,
    rcases finset.mem_insert.1 hi with rfl | h,
    { simp only [or.by_cases, dif_pos], refl },
    { have : ¬i = a, { rintro rfl, exact has h },
      simp only [or.by_cases, dif_neg this, dif_pos h], refl } }
end

end

open is_noetherian submodule function

@[nolint ge_or_gt] -- see Note [nolint_ge]
theorem is_noetherian_iff_well_founded
  {R M} [ring R] [add_comm_group M] [module R M] :
  is_noetherian R M ↔ well_founded ((>) : submodule R M → submodule R M → Prop) :=
⟨λ h, begin
  apply order_embedding.well_founded_iff_no_descending_seq.2,
  swap, { apply is_strict_order.swap },
  rintro ⟨⟨N, hN⟩⟩,
  let Q := ⨆ n, N n,
  resetI,
  rcases submodule.fg_def.1 (noetherian Q) with ⟨t, h₁, h₂⟩,
  have hN' : ∀ {a b}, a ≤ b → N a ≤ N b :=
    λ a b, (strict_mono.le_iff_le (λ _ _, hN.1)).2,
  have : t ⊆ ⋃ i, (N i : set M),
  { rw [← submodule.coe_supr_of_directed N _],
    { show t ⊆ Q, rw ← h₂,
      apply submodule.subset_span },
    { exact λ i j, ⟨max i j,
        hN' (le_max_left _ _),
        hN' (le_max_right _ _)⟩ } },
  simp [subset_def] at this,
  choose f hf using show ∀ x : t, ∃ (i : ℕ), x.1 ∈ N i, { simpa },
  cases h₁ with h₁,
  let A := finset.sup (@finset.univ t h₁) f,
  have : Q ≤ N A,
  { rw ← h₂, apply submodule.span_le.2,
    exact λ x h, hN' (finset.le_sup (@finset.mem_univ t h₁ _))
      (hf ⟨x, h⟩) },
  exact not_le_of_lt (hN.1 (nat.lt_succ_self A))
    (le_trans (le_supr _ _) this)
  end,
  begin
    assume h, split, assume N,
    suffices : ∀ P ≤ N, ∃ s, finite s ∧ P ⊔ submodule.span R s = N,
    { rcases this ⊥ bot_le with ⟨s, hs, e⟩,
      exact submodule.fg_def.2 ⟨s, hs, by simpa using e⟩ },
    refine λ P, h.induction P _, intros P IH PN,
    letI := classical.dec,
    by_cases h : ∀ x, x ∈ N → x ∈ P,
    { cases le_antisymm PN h, exact ⟨∅, by simp⟩ },
    { simp [not_forall] at h,
      rcases h with ⟨x, h, h₂⟩,
      have : ¬P ⊔ submodule.span R {x} ≤ P,
      { intro hn, apply h₂,
        have := le_trans le_sup_right hn,
        exact submodule.span_le.1 this (mem_singleton x) },
      rcases IH (P ⊔ submodule.span R {x})
        ⟨@le_sup_left _ _ P _, this⟩
        (sup_le PN (submodule.span_le.2 (by simpa))) with ⟨s, hs, hs₂⟩,
      refine ⟨insert x s, hs.insert x, _⟩,
      rw [← hs₂, sup_assoc, ← submodule.span_union], simp }
  end⟩

@[nolint ge_or_gt] -- see Note [nolint_ge]
lemma well_founded_submodule_gt (R M) [ring R] [add_comm_group M] [module R M] :
  ∀ [is_noetherian R M], well_founded ((>) : submodule R M → submodule R M → Prop) :=
is_noetherian_iff_well_founded.mp

lemma finite_of_linear_independent {R M} [comm_ring R] [nonzero R] [add_comm_group M] [module R M]
  [is_noetherian R M] {s : set M} (hs : linear_independent R (subtype.val : s → M)) : s.finite :=
begin
  refine classical.by_contradiction (λ hf, order_embedding.well_founded_iff_no_descending_seq.1
    (well_founded_submodule_gt R M) ⟨_⟩),
  have f : ℕ ↪ s, from @infinite.nat_embedding s ⟨λ f, hf ⟨f⟩⟩,
  have : ∀ n, (subtype.val ∘ f) '' {m | m ≤ n} ⊆ s,
  { rintros n x ⟨y, hy₁, hy₂⟩, subst hy₂, exact (f y).2 },
  have : ∀ a b : ℕ, a ≤ b ↔
    span R ((subtype.val ∘ f) '' {m | m ≤ a}) ≤ span R ((subtype.val ∘ f) '' {m | m ≤ b}),
  { assume a b,
    rw [span_le_span_iff zero_ne_one hs (this a) (this b),
      set.image_subset_image_iff (subtype.val_injective.comp f.injective),
      set.subset_def],
    exact ⟨λ hab x (hxa : x ≤ a), le_trans hxa hab, λ hx, hx a (le_refl a)⟩ },
  exact ⟨⟨λ n, span R ((subtype.val ∘ f) '' {m | m ≤ n}),
      λ x y, by simp [le_antisymm_iff, (this _ _).symm] {contextual := tt}⟩,
    by dsimp [gt]; simp only [lt_iff_le_not_le, (this _ _).symm]; tauto⟩
end

/--
A ring is Noetherian if it is Noetherian as a module over itself,
i.e. all its ideals are finitely generated.
-/
@[class] def is_noetherian_ring (R) [ring R] : Prop := is_noetherian R R

instance is_noetherian_ring.to_is_noetherian {R : Type*} [ring R] :
  ∀ [is_noetherian_ring R], is_noetherian R R := id

@[priority 80] -- see Note [lower instance priority]
instance ring.is_noetherian_of_fintype (R M) [fintype M] [ring R] [add_comm_group M] [module R M] :
  is_noetherian R M :=
by letI := classical.dec; exact
⟨assume s, ⟨to_finset s, by rw [set.coe_to_finset, submodule.span_eq]⟩⟩

theorem ring.is_noetherian_of_zero_eq_one {R} [ring R] (h01 : (0 : R) = 1) : is_noetherian_ring R :=
by haveI := subsingleton_of_zero_eq_one R h01;
   haveI := fintype.of_subsingleton (0:R);
   exact ring.is_noetherian_of_fintype _ _

theorem is_noetherian_of_submodule_of_noetherian (R M) [ring R] [add_comm_group M] [module R M]
  (N : submodule R M) (h : is_noetherian R M) : is_noetherian R N :=
begin
  rw is_noetherian_iff_well_founded at h ⊢,
  convert order_embedding.well_founded (order_embedding.rsymm
    (submodule.map_subtype.lt_order_embedding N)) h
end

theorem is_noetherian_of_quotient_of_noetherian (R) [ring R] (M) [add_comm_group M] [module R M]
  (N : submodule R M) (h : is_noetherian R M) : is_noetherian R N.quotient :=
begin
  rw is_noetherian_iff_well_founded at h ⊢,
  convert order_embedding.well_founded (order_embedding.rsymm
    (submodule.comap_mkq.lt_order_embedding N)) h
end

theorem is_noetherian_of_fg_of_noetherian {R M} [ring R] [add_comm_group M] [module R M]
  (N : submodule R M) [is_noetherian_ring R] (hN : N.fg) : is_noetherian R N :=
let ⟨s, hs⟩ := hN in
begin
  haveI := classical.dec_eq M,
  haveI := classical.dec_eq R,
  letI : is_noetherian R R := by apply_instance,
  have : ∀ x ∈ s, x ∈ N, from λ x hx, hs ▸ submodule.subset_span hx,
  refine @@is_noetherian_of_surjective ((↑s : set M) → R) _ _ _ (pi.semimodule _ _ _)
    _ _ _ is_noetherian_pi,
  { fapply linear_map.mk,
    { exact λ f, ⟨∑ i in s.attach, f i • i.1, N.sum_mem (λ c _, N.smul_mem _ $ this _ c.2)⟩ },
    { intros f g, apply subtype.eq,
      change ∑ i in s.attach, (f i + g i) • _ = _,
      simp only [add_smul, finset.sum_add_distrib], refl },
    { intros c f, apply subtype.eq,
      change ∑ i in s.attach, (c • f i) • _ = _,
      simp only [smul_eq_mul, mul_smul],
      exact finset.smul_sum.symm } },
  rw linear_map.range_eq_top,
  rintro ⟨n, hn⟩, change n ∈ N at hn,
  rw [← hs, ← set.image_id ↑s, finsupp.mem_span_iff_total] at hn,
  rcases hn with ⟨l, hl1, hl2⟩,
  refine ⟨λ x, l x.1, subtype.eq _⟩,
  change ∑ i in s.attach, l i.1 • i.1 = n,
  rw [@finset.sum_attach M M s _ (λ i, l i • i), ← hl2,
      finsupp.total_apply, finsupp.sum, eq_comm],
  refine finset.sum_subset hl1 (λ x _ hx, _),
  rw [finsupp.not_mem_support_iff.1 hx, zero_smul]
end

/-- In a module over a noetherian ring, the submodule generated by finitely many vectors is
noetherian. -/
theorem is_noetherian_span_of_finite (R) {M} [ring R] [add_comm_group M] [module R M]
  [is_noetherian_ring R] {A : set M} (hA : finite A) : is_noetherian R (submodule.span R A) :=
is_noetherian_of_fg_of_noetherian _ (submodule.fg_def.mpr ⟨A, hA, rfl⟩)

theorem is_noetherian_ring_of_surjective (R) [comm_ring R] (S) [comm_ring S]
  (f : R →+* S) (hf : function.surjective f)
  [H : is_noetherian_ring R] : is_noetherian_ring S :=
begin
  unfold is_noetherian_ring at H ⊢,
  rw is_noetherian_iff_well_founded at H ⊢,
  convert order_embedding.well_founded (order_embedding.rsymm
    (ideal.lt_order_embedding_of_surjective f hf)) H
end

instance is_noetherian_ring_range {R} [comm_ring R] {S} [comm_ring S] (f : R →+* S)
  [is_noetherian_ring R] : is_noetherian_ring (set.range f) :=
is_noetherian_ring_of_surjective R (set.range f) (f.cod_restrict (set.range f) set.mem_range_self)
  set.surjective_onto_range

theorem is_noetherian_ring_of_ring_equiv (R) [comm_ring R] {S} [comm_ring S]
  (f : R ≃+* S) [is_noetherian_ring R] : is_noetherian_ring S :=
is_noetherian_ring_of_surjective R S f.to_ring_hom f.to_equiv.surjective

namespace is_noetherian_ring

variables {R : Type*} [integral_domain R] [is_noetherian_ring R]
open associates nat

local attribute [elab_as_eliminator] well_founded.fix

lemma well_founded_dvd_not_unit : well_founded (λ a b : R, a ≠ 0 ∧ ∃ x, ¬is_unit x ∧ b = a * x) :=
by simp only [ideal.span_singleton_lt_span_singleton.symm];
   exact inv_image.wf (λ a, ideal.span ({a} : set R)) (well_founded_submodule_gt _ _)

lemma exists_irreducible_factor {a : R} (ha : ¬ is_unit a) (ha0 : a ≠ 0) :
  ∃ i, irreducible i ∧ i ∣ a :=
(irreducible_or_factor a ha).elim (λ hai, ⟨a, hai, dvd_refl _⟩)
  (well_founded.fix
    well_founded_dvd_not_unit
    (λ a ih ha ha0 ⟨x, y, hx, hy, hxy⟩,
      have hx0 : x ≠ 0, from λ hx0, ha0 (by rw [← hxy, hx0, zero_mul]),
      (irreducible_or_factor x hx).elim
        (λ hxi, ⟨x, hxi, hxy ▸ by simp⟩)
        (λ hxf, let ⟨i, hi⟩ := ih x ⟨hx0, y, hy, hxy.symm⟩ hx hx0 hxf in
          ⟨i, hi.1, dvd.trans hi.2 (hxy ▸ by simp)⟩)) a ha ha0)

@[elab_as_eliminator] lemma irreducible_induction_on {P : R → Prop} (a : R)
  (h0 : P 0) (hu : ∀ u : R, is_unit u → P u)
  (hi : ∀ a i : R, a ≠ 0 → irreducible i → P a → P (i * a)) :
  P a :=
by haveI := classical.dec; exact
well_founded.fix well_founded_dvd_not_unit
  (λ a ih, if ha0 : a = 0 then ha0.symm ▸ h0
    else if hau : is_unit a then hu a hau
    else let ⟨i, hii, ⟨b, hb⟩⟩ := exists_irreducible_factor hau ha0 in
      have hb0 : b ≠ 0, from λ hb0, by simp * at *,
      hb.symm ▸ hi _ _ hb0 hii (ih _ ⟨hb0, i,
        hii.1, by rw [hb, mul_comm]⟩))
  a

lemma exists_factors (a : R) : a ≠ 0 →
  ∃f : multiset R, (∀b ∈ f, irreducible b) ∧ associated a f.prod :=
is_noetherian_ring.irreducible_induction_on a
  (λ h, (h rfl).elim)
  (λ u hu _, ⟨0, by simp [associated_one_iff_is_unit, hu]⟩)
  (λ a i ha0 hii ih hia0,
    let ⟨s, hs⟩ := ih ha0 in
    ⟨i::s, ⟨by clear _let_match; finish,
      by rw multiset.prod_cons;
        exact associated_mul_mul (by refl) hs.2⟩⟩)

end is_noetherian_ring

namespace submodule
variables {R : Type*} {A : Type*} [comm_ring R] [ring A] [algebra R A]
variables (M N : submodule R A)

local attribute [instance] set.pointwise_mul_semiring

theorem fg_mul (hm : M.fg) (hn : N.fg) : (M * N).fg :=
let ⟨m, hfm, hm⟩ := fg_def.1 hm, ⟨n, hfn, hn⟩ := fg_def.1 hn in
fg_def.2 ⟨m * n, set.pointwise_mul_finite hfm hfn, span_mul_span R m n ▸ hm ▸ hn ▸ rfl⟩

lemma fg_pow (h : M.fg) (n : ℕ) : (M ^ n).fg :=
nat.rec_on n
(⟨{1}, by simp [one_eq_span]⟩)
(λ n ih, by simpa [pow_succ] using fg_mul _ _ h ih)

end submodule
