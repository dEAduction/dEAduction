/-
Copyright (c) 2020 Sébastien Gouëzel. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Sébastien Gouëzel
-/
import analysis.mean_inequalities

/-!
# `L^p` distance on finite products of metric spaces
Given finitely many metric spaces, one can put the max distance on their product, but there is also
a whole family of natural distances, indexed by a real parameter `p ∈ [1, ∞)`, that also induce
the product topology. We define them in this file. The distance on `Π i, α i` is given by
$$
d(x, y) = \left(\sum d(x_i, y_i)^p\right)^{1/p}.
$$

We give instances of this construction for emetric spaces, metric spaces, normed groups and normed
spaces.

To avoid conflicting instances, all these are defined on a copy of the original Pi type, named
`pi_Lp p hp α`, where `hp : 1 ≤ p`. This assumption is included in the definition of the type
to make sure that it is always available to typeclass inference to construct the instances.

We ensure that the topology and uniform structure on `pi_Lp p hp α` are (defeq to) the product
topology and product uniformity, to be able to use freely continuity statements for the coordinate
functions, for instance.

## Implementation notes

We only deal with the `L^p` distance on a product of finitely many metric spaces, which may be
distinct. A closely related construction is the `L^p` norm on the space of
functions from a measure space to a normed space, where the norm is
$$
\left(\int ∥f (x)∥^p dμ\right)^{1/p}.
$$
However, the topology induced by this construction is not the product topology, this only
defines a seminorm (as almost everywhere zero functions have zero `L^p` norm), and some functions
have infinite `L^p` norm. All these subtleties are not present in the case of finitely many
metric spaces (which corresponds to the basis which is a finite space with the counting measure),
hence it is worth devoting a file to this specific case which is particularly well behaved.
The general case is not yet formalized in mathlib.

To prove that the topology (and the uniform structure) on a finite product with the `L^p` distance
are the same as those coming from the `L^∞` distance, we could argue that the `L^p` and `L^∞` norms
are equivalent on `ℝ^n` for abstract (norm equivalence) reasons. Instead, we give a more explicit
(easy) proof which provides a comparison between these two norms with explicit constants.
-/

open real set filter
open_locale big_operators uniformity topological_space

noncomputable theory

variables {ι : Type*}

/-- A copy of a Pi type, on which we will put the `L^p` distance. Since the Pi type itself is
already endowed with the `L^∞` distance, we need the type synonym to avoid confusing typeclass
resolution. Also, we let it depend on `p`, to get a whole family of type on which we can put
different distances, and we provide the assumption `hp` in the definition, to make it available
to typeclass resolution when it looks for a distance on `pi_Lp p hp α`. -/
@[nolint unused_arguments]
def pi_Lp {ι : Type*} (p : ℝ) (hp : 1 ≤ p) (α : ι → Type*) : Type* := Π (i : ι), α i

instance {ι : Type*} (p : ℝ) (hp : 1 ≤ p) (α : ι → Type*) [∀ i, inhabited (α i)] :
  inhabited (pi_Lp p hp α) :=
⟨λ i, default (α i)⟩

namespace pi_Lp

variables (p : ℝ) (hp : 1 ≤ p) (α : ι → Type*)

/-- Canonical bijection between `pi_Lp p hp α` and the original Pi type. We introduce it to be able
to compare the `L^p` and `L^∞` distances through it. -/
protected def equiv : pi_Lp p hp α ≃ Π (i : ι), α i :=
equiv.refl _

section
/-!
### The uniformity on finite `L^p` products is the product uniformity

In this section, we put the `L^p` edistance on `pi_Lp p hp α`, and we check that the uniformity
coming from this edistance coincides with the product uniformity, by showing that the canonical
map to the Pi type (with the `L^∞` distance) is a uniform embedding, as it is both Lipschitz and
antiLipschitz.

We only register this emetric space structure as a temporary instance, as the true instance (to be
registered later) will have as uniformity exactly the product uniformity, instead of the one coming
from the edistance (which is equal to it, but not defeq). See Note [forgetful inheritance]
explaining why having definitionally the right uniformity is often important.
-/

variables [∀ i, emetric_space (α i)] [fintype ι]

/-- Endowing the space `pi_Lp p hp α` with the `L^p` edistance. This definition is not satisfactory,
as it does not register the fact that the topology and the uniform structure coincide with the
product one. Therefore, we do not register it as an instance. Using this as a temporary emetric
space instance, we will show that the uniform structure is equal (but not defeq) to the product one,
and then register an instance in which we replace the uniform structure by the product one using
this emetric space and `emetric_space.replace_uniformity`. -/
def emetric_aux : emetric_space (pi_Lp p hp α) :=
have pos : 0 < p := lt_of_lt_of_le zero_lt_one hp,
{ edist          := λ f g, (∑ (i : ι), (edist (f i) (g i)) ^ p) ^ (1/p),
  edist_self     := λ f, by simp [edist, ennreal.zero_rpow_of_pos pos,
                                  ennreal.zero_rpow_of_pos (inv_pos.2 pos)],
  edist_comm     := λ f g, by simp [edist, edist_comm],
  edist_triangle := λ f g h, calc
    (∑ (i : ι), edist (f i) (h i) ^ p) ^ (1 / p) ≤
    (∑ (i : ι), (edist (f i) (g i) + edist (g i) (h i)) ^ p) ^ (1 / p) :
    begin
      apply ennreal.rpow_le_rpow _ (div_nonneg zero_le_one pos),
      refine finset.sum_le_sum (λ i hi, _),
      exact ennreal.rpow_le_rpow (edist_triangle _ _ _) (le_trans zero_le_one hp)
    end
    ... ≤
    (∑ (i : ι), edist (f i) (g i) ^ p) ^ (1 / p) + (∑ (i : ι), edist (g i) (h i) ^ p) ^ (1 / p) :
      ennreal.Lp_add_le _ _ _ hp,
  eq_of_edist_eq_zero := λ f g hfg,
  begin
    simp [edist, ennreal.rpow_eq_zero_iff, pos, asymm pos, finset.sum_eq_zero_iff_of_nonneg] at hfg,
    exact funext hfg
  end }

local attribute [instance] pi_Lp.emetric_aux

lemma lipschitz_with_equiv : lipschitz_with 1 (pi_Lp.equiv p hp α) :=
begin
  have pos : 0 < p := lt_of_lt_of_le zero_lt_one hp,
  have cancel : p * (1/p) = 1 := mul_div_cancel' 1 (ne_of_gt pos),
  assume x y,
  simp only [edist, forall_prop_of_true, one_mul, finset.mem_univ, finset.sup_le_iff,
             ennreal.coe_one],
  assume i,
  calc
  edist (x i) (y i) = (edist (x i) (y i) ^ p) ^ (1/p) :
    by simp [← ennreal.rpow_mul, cancel, -one_div_eq_inv]
  ... ≤ (∑ (i : ι), edist (x i) (y i) ^ p) ^ (1 / p) :
  begin
    apply ennreal.rpow_le_rpow _ (div_nonneg zero_le_one pos),
    exact finset.single_le_sum (λ i hi, (bot_le : (0 : ennreal) ≤ _)) (finset.mem_univ i)
  end
end

lemma antilipschitz_with_equiv :
  antilipschitz_with ((fintype.card ι : nnreal) ^ (1/p)) (pi_Lp.equiv p hp α) :=
begin
  have pos : 0 < p := lt_of_lt_of_le zero_lt_one hp,
  have cancel : p * (1/p) = 1 := mul_div_cancel' 1 (ne_of_gt pos),
  assume x y,
  simp [edist, -one_div_eq_inv],
  calc (∑ (i : ι), edist (x i) (y i) ^ p) ^ (1 / p) ≤
  (∑ (i : ι), edist (pi_Lp.equiv p hp α x) (pi_Lp.equiv p hp α y) ^ p) ^ (1 / p) :
  begin
    apply ennreal.rpow_le_rpow _ (div_nonneg zero_le_one pos),
    apply finset.sum_le_sum (λ i hi, _),
    apply ennreal.rpow_le_rpow _ (le_of_lt pos),
    exact finset.le_sup (finset.mem_univ i)
  end
  ... = (((fintype.card ι : nnreal)) ^ (1/p) : nnreal) *
    edist (pi_Lp.equiv p hp α x) (pi_Lp.equiv p hp α y) :
  begin
    simp only [nsmul_eq_mul, finset.card_univ, ennreal.rpow_one, finset.sum_const,
      ennreal.mul_rpow_of_nonneg _ _ (div_nonneg zero_le_one pos), ←ennreal.rpow_mul, cancel],
    have : (fintype.card ι : ennreal) = (fintype.card ι : nnreal) :=
      (ennreal.coe_nat (fintype.card ι)).symm,
    rw [this, ennreal.coe_rpow_of_nonneg _ (div_nonneg zero_le_one pos)]
  end
end

lemma aux_uniformity_eq :
  𝓤 (pi_Lp p hp α) = @uniformity _ (Pi.uniform_space _) :=
begin
  have A : uniform_embedding (pi_Lp.equiv p hp α) :=
    (antilipschitz_with_equiv p hp α).uniform_embedding
      (lipschitz_with_equiv p hp α).uniform_continuous,
  have : (λ (x : pi_Lp p hp α × pi_Lp p hp α),
    ((pi_Lp.equiv p hp α) x.fst, (pi_Lp.equiv p hp α) x.snd)) = id,
    by ext i; refl,
  rw [← A.comap_uniformity, this, comap_id]
end

end

/-! ### Instances on finite `L^p` products -/

instance uniform_space [∀ i, uniform_space (α i)] : uniform_space (pi_Lp p hp α) :=
Pi.uniform_space _

variable [fintype ι]

/-- emetric space instance on the product of finitely many emetric spaces, using the `L^p`
edistance, and having as uniformity the product uniformity. -/
instance [∀ i, emetric_space (α i)] : emetric_space (pi_Lp p hp α) :=
(emetric_aux p hp α).replace_uniformity (aux_uniformity_eq p hp α).symm

protected lemma edist {p : ℝ} {hp : 1 ≤ p} {α : ι → Type*}
  [∀ i, emetric_space (α i)] (x y : pi_Lp p hp α) :
  edist x y = (∑ (i : ι), (edist (x i) (y i)) ^ p) ^ (1/p) := rfl

/-- metric space instance on the product of finitely many metric spaces, using the `L^p` distance,
and having as uniformity the product uniformity. -/
instance [∀ i, metric_space (α i)] : metric_space (pi_Lp p hp α) :=
begin
  /- we construct the instance from the emetric space instance to avoid checking again that the
  uniformity is the same as the product uniformity, but we register nevertheless a nice formula
  for the distance -/
  have pos : 0 < p := lt_of_lt_of_le zero_lt_one hp,
  refine emetric_space.to_metric_space_of_dist
    (λf g, (∑ (i : ι), (dist (f i) (g i)) ^ p) ^ (1/p)) (λ f g, _) (λ f g, _),
  { simp [pi_Lp.edist, ennreal.rpow_eq_top_iff, asymm pos, pos,
          ennreal.sum_eq_top_iff, edist_ne_top] },
  { have A : ∀ (i : ι), i ∈ (finset.univ : finset ι) → edist (f i) (g i) ^ p < ⊤ :=
      λ i hi, by simp [lt_top_iff_ne_top, edist_ne_top, le_of_lt pos],
    simp [dist, -one_div_eq_inv, pi_Lp.edist, ← ennreal.to_real_rpow,
          ennreal.to_real_sum A, dist_edist] }
end

protected lemma dist {p : ℝ} {hp : 1 ≤ p} {α : ι → Type*}
  [∀ i, metric_space (α i)] (x y : pi_Lp p hp α) :
  dist x y = (∑ (i : ι), (dist (x i) (y i)) ^ p) ^ (1/p) := rfl

/-- normed group instance on the product of finitely many normed groups, using the `L^p` norm. -/
instance normed_group [∀i, normed_group (α i)] : normed_group (pi_Lp p hp α) :=
{ norm := λf, (∑ (i : ι), norm (f i) ^ p) ^ (1/p),
  dist_eq := λ x y, by { simp [pi_Lp.dist, dist_eq_norm] },
  .. pi.add_comm_group }

lemma norm_eq {p : ℝ} {hp : 1 ≤ p} {α : ι → Type*}
  [∀i, normed_group (α i)] (f : pi_Lp p hp α) :
  ∥f∥ = (∑ (i : ι), ∥f i∥ ^ p) ^ (1/p) := rfl

variables (𝕜 : Type*) [normed_field 𝕜]

/-- The product of finitely many normed spaces is a normed space, with the `L^p` norm. -/
instance normed_space [∀i, normed_group (α i)] [∀i, normed_space 𝕜 (α i)] :
  normed_space 𝕜 (pi_Lp p hp α) :=
{ norm_smul_le :=
  begin
    assume c f,
    have : p * (1 / p) = 1 := mul_div_cancel' 1 (ne_of_gt (lt_of_lt_of_le zero_lt_one hp)),
    simp only [pi_Lp.norm_eq, norm_smul, mul_rpow, norm_nonneg, ←finset.mul_sum, pi.smul_apply],
    rw [mul_rpow (rpow_nonneg_of_nonneg (norm_nonneg _) _), ← rpow_mul (norm_nonneg _),
        this, rpow_one],
    exact finset.sum_nonneg (λ i hi, rpow_nonneg_of_nonneg (norm_nonneg _) _)
  end,
  .. pi.semimodule ι α 𝕜 }

/- Register simplification lemmas for the applications of `pi_Lp` elements, as the usual lemmas
for Pi types will not trigger. -/
variables {𝕜 p hp α}
[∀i, normed_group (α i)] [∀i, normed_space 𝕜 (α i)] (c : 𝕜) (x y : pi_Lp p hp α) (i : ι)

@[simp] lemma add_apply : (x + y) i = x i + y i := rfl
@[simp] lemma sub_apply : (x - y) i = x i - y i := rfl
@[simp] lemma smul_apply : (c • x) i = c • x i := rfl
@[simp] lemma neg_apply : (-x) i = - (x i) := rfl

end pi_Lp
