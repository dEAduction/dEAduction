/-
Copyright (c) 2019 Patrick Massot. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Patrick Massot

Indexed product of uniform spaces
-/
import topology.uniform_space.cauchy
import topology.uniform_space.separation
noncomputable theory

open_locale uniformity topological_space

section
open filter uniform_space
universe u
variables {ι : Type*} (α : ι → Type u) [U : Πi, uniform_space (α i)]
include U

instance Pi.uniform_space : uniform_space (Πi, α i) :=
uniform_space.of_core_eq
  (⨅i, uniform_space.comap (λ a : Πi, α i, a i) (U i)).to_core
  Pi.topological_space $ eq.symm to_topological_space_infi

lemma Pi.uniformity :
  𝓤 (Π i, α i) = ⨅ i : ι, filter.comap (λ a, (a.1 i, a.2 i)) $ 𝓤 (α i) :=
infi_uniformity

lemma Pi.uniform_continuous_proj (i : ι) : uniform_continuous (λ (a : Π (i : ι), α i), a i) :=
begin
  rw uniform_continuous_iff,
  exact infi_le (λ j, uniform_space.comap (λ (a : Π (i : ι), α i), a j) (U j)) i
end

instance Pi.complete [∀ i, complete_space (α i)] : complete_space (Π i, α i) :=
⟨begin
  intros f hf,
  have : ∀ i, ∃ x : α i, filter.map (λ a : Πi, α i, a i) f ≤ 𝓝 x,
  { intro i,
    have key : cauchy (map (λ (a : Π (i : ι), α i), a i) f),
      from cauchy_map (Pi.uniform_continuous_proj α i) hf,
    exact (cauchy_iff_exists_le_nhds $ map_ne_bot hf.1).1 key },
  choose x hx using this,
  use x,
  rw [nhds_pi, le_infi_iff],
  exact λ i, map_le_iff_le_comap.mp (hx i),
end⟩

instance Pi.separated [∀ i, separated_space (α i)] : separated_space (Π i, α i) :=
separated_def.2 $ assume x y H,
begin
  ext i,
  apply eq_of_separated_of_uniform_continuous (Pi.uniform_continuous_proj α i),
  apply H,
end
end
