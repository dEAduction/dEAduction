/-
Copyright (c) 2017 Johannes Hölzl. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Johannes Hölzl, Mario Carneiro

The Schröder-Bernstein theorem, and well ordering of cardinals.
-/
import order.fixed_points
import order.zorn

open set classical
open_locale classical

universes u v

namespace function
namespace embedding

section antisymm
variables {α : Type u} {β : Type v}

theorem schroeder_bernstein {f : α → β} {g : β → α}
  (hf : function.injective f) (hg : function.injective g) : ∃h:α→β, bijective h :=
let s : set α := lfp $ λs, - (g '' - (f '' s)) in
have hs : s = - (g '' - (f '' s)),
  from lfp_eq $ assume s t h,
    compl_subset_compl.mpr $ image_subset _ $
    compl_subset_compl.mpr $ image_subset _ h,

have hns : - s = g '' - (f '' s),
  from compl_injective $ by simp [hs.symm],

let g' := λa, @inv_fun β ⟨f a⟩ α g a in
have g'g : g' ∘ g = id,
  from funext $ assume b, @left_inverse_inv_fun _ ⟨f (g b)⟩ _ _ hg b,
have hg'ns : g' '' (-s) = - (f '' s),
  by rw [hns, ←image_comp, g'g, image_id],

let h := λa, if a ∈ s then f a else g' a in

have h '' univ = univ,
  from calc h '' univ = h '' s ∪ h '' (- s) : by rw [←image_union, union_compl_self]
    ... = f '' s ∪ g' '' (-s) :
      congr (congr_arg (∪)
        (image_congr $ by simp [h, if_pos] {contextual := tt}))
        (image_congr $ by simp [h, if_neg] {contextual := tt})
    ... = univ : by rw [hg'ns, union_compl_self],
have surjective h,
  from assume b,
  have b ∈ h '' univ, by rw [this]; trivial,
  let ⟨a, _, eq⟩ := this in
  ⟨a, eq⟩,

have split : ∀x∈s, ∀y∉s, h x = h y → false,
  from assume x hx y hy eq,
  have y ∈ g '' - (f '' s), by rwa [←hns],
  let ⟨y', hy', eq_y'⟩ := this in
  have f x = y',
    from calc f x = g' y : by simp [h, hx, hy, if_pos, if_neg] at eq; assumption
      ... = (g' ∘ g) y' : by simp [(∘), eq_y']
      ... = _ : by simp [g'g],
  have y' ∈ f '' s, from this ▸ mem_image_of_mem _ hx,
  hy' this,
have function.injective h,
  from assume x y eq,
  by_cases
    (assume hx : x ∈ s, by_cases
      (assume hy : y ∈ s, by simp [h, hx, hy, if_pos, if_neg] at eq; exact hf eq)
      (assume hy : y ∉ s, (split x hx y hy eq).elim))
    (assume hx : x ∉ s, by_cases
      (assume hy : y ∈ s, (split y hy x hx eq.symm).elim)
      (assume hy : y ∉ s,
        have x ∈ g '' - (f '' s), by rwa [←hns],
        let ⟨x', hx', eqx⟩ := this in
        have y ∈ g '' - (f '' s), by rwa [←hns],
        let ⟨y', hy', eqy⟩ := this in
        have g' x = g' y, by simp [h, hx, hy, if_pos, if_neg] at eq; assumption,
        have (g' ∘ g) x' = (g' ∘ g) y', by simp [(∘), eqx, eqy, this],
        have x' = y', by rwa [g'g] at this,
        calc x = g x' : eqx.symm
          ... = g y' : by rw [this]
          ... = y : eqy)),

⟨h, ‹function.injective h›, ‹function.surjective h›⟩

theorem antisymm : (α ↪ β) → (β ↪ α) → nonempty (α ≃ β)
| ⟨e₁, h₁⟩ ⟨e₂, h₂⟩ :=
  let ⟨f, hf⟩ := schroeder_bernstein h₁ h₂ in
  ⟨equiv.of_bijective f hf⟩

end antisymm

section wo
parameters {ι : Type u} {β : ι → Type v}

@[reducible] private def sets := {s : set (∀ i, β i) |
  ∀ (x ∈ s) (y ∈ s) i, (x : ∀ i, β i) i = y i → x = y}

theorem min_injective (I : nonempty ι) : ∃ i, nonempty (∀ j, β i ↪ β j) :=
let ⟨s, hs, ms⟩ := show ∃s∈sets, ∀a∈sets, s ⊆ a → a = s, from
  zorn.zorn_subset sets (λ c hc hcc, ⟨⋃₀ c,
    λ x ⟨p, hpc, hxp⟩ y ⟨q, hqc, hyq⟩ i hi,
      (hcc.total hpc hqc).elim (λ h, hc hqc x (h hxp) y hyq i hi) (λ h, hc hpc x hxp y (h hyq) i hi),
  λ _, subset_sUnion_of_mem⟩) in
let ⟨i, e⟩ := show ∃ i, ∀ y, ∃ x ∈ s, (x : ∀ i, β i) i = y, from
  classical.by_contradiction $ λ h,
  have h : ∀ i, ∃ y, ∀ x ∈ s, (x : ∀ i, β i) i ≠ y,
    by simpa only [not_exists, classical.not_forall] using h,
  let ⟨f, hf⟩ := axiom_of_choice h in
  have f ∈ s, from
    have insert f s ∈ sets := λ x hx y hy, begin
      cases hx; cases hy, {simp [hx, hy]},
      { subst x, exact λ i e, (hf i y hy e.symm).elim },
      { subst y, exact λ i e, (hf i x hx e).elim },
      { exact hs x hx y hy }
    end, ms _ this (subset_insert f s) ▸ mem_insert _ _,
  let ⟨i⟩ := I in hf i f this rfl in
let ⟨f, hf⟩ := axiom_of_choice e in
⟨i, ⟨λ j, ⟨λ a, f a j, λ a b e',
  let ⟨sa, ea⟩ := hf a, ⟨sb, eb⟩ := hf b in
  by rw [← ea, ← eb, hs _ sa _ sb _ e']⟩⟩⟩

end wo

theorem total {α : Type u} {β : Type v} : nonempty (α ↪ β) ∨ nonempty (β ↪ α) :=
match @min_injective bool (λ b, cond b (ulift α) (ulift.{(max u v) v} β)) ⟨tt⟩ with
| ⟨tt, ⟨h⟩⟩ := let ⟨f, hf⟩ := h ff in or.inl ⟨embedding.congr equiv.ulift equiv.ulift ⟨f, hf⟩⟩
| ⟨ff, ⟨h⟩⟩ := let ⟨f, hf⟩ := h tt in or.inr ⟨embedding.congr equiv.ulift equiv.ulift ⟨f, hf⟩⟩
end

end embedding
end function
