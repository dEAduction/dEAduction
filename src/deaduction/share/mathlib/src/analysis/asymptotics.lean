/-
Copyright (c) 2019 Jeremy Avigad. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jeremy Avigad, Yury Kudryashov
-/
import analysis.normed_space.basic
import topology.local_homeomorph

/-!
# Asymptotics

We introduce these relations:

* `is_O_with c f g l` : "f is big O of g along l with constant c";
* `is_O f g l` : "f is big O of g along l";
* `is_o f g l` : "f is little o of g along l".

Here `l` is any filter on the domain of `f` and `g`, which are assumed to be the same. The codomains
of `f` and `g` do not need to be the same; all that is needed that there is a norm associated with
these types, and it is the norm that is compared asymptotically.

The relation `is_O_with c` is introduced to factor out common algebraic arguments in the proofs of
similar properties of `is_O` and `is_o`. Usually proofs outside of this file should use `is_O`
instead.

Often the ranges of `f` and `g` will be the real numbers, in which case the norm is the absolute
value. In general, we have

  `is_O f g l ↔ is_O (λ x, ∥f x∥) (λ x, ∥g x∥) l`,

and similarly for `is_o`. But our setup allows us to use the notions e.g. with functions
to the integers, rationals, complex numbers, or any normed vector space without mentioning the
norm explicitly.

If `f` and `g` are functions to a normed field like the reals or complex numbers and `g` is always
nonzero, we have

  `is_o f g l ↔ tendsto (λ x, f x / (g x)) l (𝓝 0)`.

In fact, the right-to-left direction holds without the hypothesis on `g`, and in the other direction
it suffices to assume that `f` is zero wherever `g` is. (This generalization is useful in defining
the Fréchet derivative.)
-/

open filter set
open_locale topological_space big_operators classical

namespace asymptotics

variables {α : Type*} {β : Type*} {E : Type*} {F : Type*} {G : Type*}
  {E' : Type*} {F' : Type*} {G' : Type*} {R : Type*} {R' : Type*} {𝕜 : Type*} {𝕜' : Type*}

variables [has_norm E] [has_norm F] [has_norm G] [normed_group E'] [normed_group F']
  [normed_group G'] [normed_ring R] [normed_ring R'] [normed_field 𝕜] [normed_field 𝕜']
  {c c' : ℝ} {f : α → E} {g : α → F} {k : α → G} {f' : α → E'} {g' : α → F'} {k' : α → G'}
  {l l' : filter α}

section defs

/-! ### Definitions -/

/-- This version of the Landau notation `is_O_with C f g l` where `f` and `g` are two functions on
a type `α` and `l` is a filter on `α`, means that eventually for `l`, `∥f∥` is bounded by `C * ∥g∥`.
In other words, `∥f∥ / ∥g∥` is eventually bounded by `C`, modulo division by zero issues that are
avoided by this definition. Probably you want to use `is_O` instead of this relation. -/
def is_O_with (c : ℝ) (f : α → E) (g : α → F) (l : filter α) : Prop :=
∀ᶠ x in l, ∥ f x ∥ ≤ c * ∥ g x ∥

/-- Definition of `is_O_with`. We record it in a lemma as we will set `is_O_with` to be irreducible
at the end of this file. -/
lemma is_O_with_iff {c : ℝ} {f : α → E} {g : α → F} {l : filter α} :
  is_O_with c f g l ↔ ∀ᶠ x in l, ∥ f x ∥ ≤ c * ∥ g x ∥ := iff.rfl

lemma is_O_with.of_bound {c : ℝ} {f : α → E} {g : α → F} {l : filter α}
  (h : ∀ᶠ x in l, ∥ f x ∥ ≤ c * ∥ g x ∥) : is_O_with c f g l := h

/-- The Landau notation `is_O f g l` where `f` and `g` are two functions on a type `α` and `l` is
a filter on `α`, means that eventually for `l`, `∥f∥` is bounded by a constant multiple of `∥g∥`.
In other words, `∥f∥ / ∥g∥` is eventually bounded, modulo division by zero issues that are avoided
by this definition. -/
def is_O (f : α → E) (g : α → F) (l : filter α) : Prop := ∃ c : ℝ, is_O_with c f g l

/-- Definition of `is_O` in terms of `is_O_with`. We record it in a lemma as we will set
`is_O` to be irreducible at the end of this file. -/
lemma is_O_iff_is_O_with {f : α → E} {g : α → F} {l : filter α} :
  is_O f g l ↔ ∃ c : ℝ, is_O_with c f g l := iff.rfl

/-- Definition of `is_O` in terms of filters. We record it in a lemma as we will set
`is_O` to be irreducible at the end of this file. -/
lemma is_O_iff {f : α → E} {g : α → F} {l : filter α} :
  is_O f g l ↔ ∃ c : ℝ, ∀ᶠ x in l, ∥ f x ∥ ≤ c * ∥ g x ∥ := iff.rfl

lemma is_O.of_bound (c : ℝ) {f : α → E} {g : α → F} {l : filter α}
  (h : ∀ᶠ x in l, ∥ f x ∥ ≤ c * ∥ g x ∥) : is_O f g l := ⟨c, h⟩

/-- The Landau notation `is_o f g l` where `f` and `g` are two functions on a type `α` and `l` is
a filter on `α`, means that eventually for `l`, `∥f∥` is bounded by an arbitrarily small constant
multiple of `∥g∥`. In other words, `∥f∥ / ∥g∥` tends to `0` along `l`, modulo division by zero
issues that are avoided by this definition. -/
def is_o (f : α → E) (g : α → F) (l : filter α) : Prop := ∀ ⦃c : ℝ⦄, 0 < c → is_O_with c f g l

/-- Definition of `is_o` in terms of `is_O_with`. We record it in a lemma as we will set
`is_o` to be irreducible at the end of this file. -/
lemma is_o_iff_forall_is_O_with {f : α → E} {g : α → F} {l : filter α} :
  is_o f g l ↔ ∀ ⦃c : ℝ⦄, 0 < c → is_O_with c f g l := iff.rfl

/-- Definition of `is_o` in terms of filters. We record it in a lemma as we will set
`is_o` to be irreducible at the end of this file. -/
lemma is_o_iff {f : α → E} {g : α → F} {l : filter α} :
  is_o f g l ↔ ∀ ⦃c : ℝ⦄, 0 < c → ∀ᶠ x in l, ∥ f x ∥ ≤ c * ∥ g x ∥ := iff.rfl

lemma is_o.def {f : α → E} {g : α → F} {l : filter α} (h : is_o f g l) {c : ℝ} (hc : 0 < c) :
  ∀ᶠ x in l, ∥ f x ∥ ≤ c * ∥ g x ∥ :=
h hc

lemma is_o.def' {f : α → E} {g : α → F} {l : filter α} (h : is_o f g l) {c : ℝ} (hc : 0 < c) :
  is_O_with c f g l :=
h hc

end defs

/-! ### Conversions -/

theorem is_O_with.is_O (h : is_O_with c f g l) : is_O f g l := ⟨c, h⟩

theorem is_o.is_O_with (hgf : is_o f g l) : is_O_with 1 f g l := hgf zero_lt_one

theorem is_o.is_O (hgf : is_o f g l) : is_O f g l := hgf.is_O_with.is_O

theorem is_O_with.weaken (h : is_O_with c f g' l) (hc : c ≤ c') : is_O_with c' f g' l :=
mem_sets_of_superset h $ λ x hx,
calc ∥f x∥ ≤ c * ∥g' x∥ : hx
... ≤ _ : mul_le_mul_of_nonneg_right hc (norm_nonneg _)

theorem is_O_with.exists_pos (h : is_O_with c f g' l) :
  ∃ c' (H : 0 < c'), is_O_with c' f g' l :=
⟨max c 1, lt_of_lt_of_le zero_lt_one (le_max_right c 1), h.weaken $ le_max_left c 1⟩

theorem is_O.exists_pos (h : is_O f g' l) : ∃ c (H : 0 < c), is_O_with c f g' l :=
let ⟨c, hc⟩ := h in hc.exists_pos

theorem is_O_with.exists_nonneg (h : is_O_with c f g' l) :
  ∃ c' (H : 0 ≤ c'), is_O_with c' f g' l :=
let ⟨c, cpos, hc⟩ := h.exists_pos in ⟨c, le_of_lt cpos, hc⟩

theorem is_O.exists_nonneg (h : is_O f g' l) :
  ∃ c (H : 0 ≤ c), is_O_with c f g' l :=
let ⟨c, hc⟩ := h in hc.exists_nonneg

/-! ### Congruence -/

theorem is_O_with_congr {c₁ c₂} {f₁ f₂ : α → E} {g₁ g₂ : α → F} {l : filter α}
  (hc : c₁ = c₂) (hf : f₁ =ᶠ[l] f₂) (hg : g₁ =ᶠ[l] g₂) :
  is_O_with c₁ f₁ g₁ l ↔ is_O_with c₂ f₂ g₂ l :=
begin
  subst c₂,
  apply filter.congr_sets,
  filter_upwards [hf, hg],
  assume x e₁ e₂,
  dsimp at e₁ e₂ ⊢,
  rw [e₁, e₂]
end

theorem is_O_with.congr' {c₁ c₂} {f₁ f₂ : α → E} {g₁ g₂ : α → F} {l : filter α}
  (hc : c₁ = c₂) (hf : f₁ =ᶠ[l] f₂) (hg : g₁ =ᶠ[l] g₂) :
  is_O_with c₁ f₁ g₁ l → is_O_with c₂ f₂ g₂ l :=
(is_O_with_congr hc hf hg).mp

theorem is_O_with.congr {c₁ c₂} {f₁ f₂ : α → E} {g₁ g₂ : α → F} {l : filter α}
  (hc : c₁ = c₂) (hf : ∀ x, f₁ x = f₂ x) (hg : ∀ x, g₁ x = g₂ x) :
  is_O_with c₁ f₁ g₁ l → is_O_with c₂ f₂ g₂ l :=
λ h, h.congr' hc (univ_mem_sets' hf) (univ_mem_sets' hg)

theorem is_O_with.congr_left {f₁ f₂ : α → E} {l : filter α} (hf : ∀ x, f₁ x = f₂ x) :
  is_O_with c f₁ g l → is_O_with c f₂ g l :=
is_O_with.congr rfl hf (λ _, rfl)

theorem is_O_with.congr_right {g₁ g₂ : α → F} {l : filter α} (hg : ∀ x, g₁ x = g₂ x) :
  is_O_with c f g₁ l → is_O_with c f g₂ l :=
is_O_with.congr rfl (λ _, rfl) hg

theorem is_O_with.congr_const {c₁ c₂} {l : filter α} (hc : c₁ = c₂) :
  is_O_with c₁ f g l → is_O_with c₂ f g l :=
is_O_with.congr hc (λ _, rfl) (λ _, rfl)

theorem is_O_congr {f₁ f₂ : α → E} {g₁ g₂ : α → F} {l : filter α}
    (hf : f₁ =ᶠ[l] f₂) (hg : g₁ =ᶠ[l] g₂) :
  is_O f₁ g₁ l ↔ is_O f₂ g₂ l :=
exists_congr $ λ c, is_O_with_congr rfl hf hg

theorem is_O.congr' {f₁ f₂ : α → E} {g₁ g₂ : α → F} {l : filter α}
    (hf : f₁ =ᶠ[l] f₂) (hg : g₁ =ᶠ[l] g₂) :
  is_O f₁ g₁ l → is_O f₂ g₂ l :=
(is_O_congr hf hg).mp

theorem is_O.congr {f₁ f₂ : α → E} {g₁ g₂ : α → F} {l : filter α}
    (hf : ∀ x, f₁ x = f₂ x) (hg : ∀ x, g₁ x = g₂ x) :
  is_O f₁ g₁ l → is_O f₂ g₂ l :=
λ h, h.congr' (univ_mem_sets' hf) (univ_mem_sets' hg)

theorem is_O.congr_left {f₁ f₂ : α → E} {l : filter α} (hf : ∀ x, f₁ x = f₂ x) :
  is_O f₁ g l → is_O f₂ g l :=
is_O.congr hf (λ _, rfl)

theorem is_O.congr_right {g₁ g₂ : α → E} {l : filter α} (hg : ∀ x, g₁ x = g₂ x) :
  is_O f g₁ l → is_O f g₂ l :=
is_O.congr (λ _, rfl) hg

theorem is_o_congr {f₁ f₂ : α → E} {g₁ g₂ : α → F} {l : filter α}
    (hf : f₁ =ᶠ[l] f₂) (hg : g₁ =ᶠ[l] g₂) :
  is_o f₁ g₁ l ↔ is_o f₂ g₂ l :=
ball_congr (λ c hc, is_O_with_congr (eq.refl c) hf hg)

theorem is_o.congr' {f₁ f₂ : α → E} {g₁ g₂ : α → F} {l : filter α}
    (hf : f₁ =ᶠ[l] f₂) (hg : g₁ =ᶠ[l] g₂) :
  is_o f₁ g₁ l → is_o f₂ g₂ l :=
(is_o_congr hf hg).mp

theorem is_o.congr {f₁ f₂ : α → E} {g₁ g₂ : α → F} {l : filter α}
    (hf : ∀ x, f₁ x = f₂ x) (hg : ∀ x, g₁ x = g₂ x) :
  is_o f₁ g₁ l → is_o f₂ g₂ l :=
λ h, h.congr' (univ_mem_sets' hf) (univ_mem_sets' hg)

theorem is_o.congr_left {f₁ f₂ : α → E} {l : filter α} (hf : ∀ x, f₁ x = f₂ x) :
  is_o f₁ g l → is_o f₂ g l :=
is_o.congr hf (λ _, rfl)

theorem is_o.congr_right {g₁ g₂ : α → E} {l : filter α} (hg : ∀ x, g₁ x = g₂ x) :
  is_o f g₁ l → is_o f g₂ l :=
is_o.congr (λ _, rfl) hg

/-! ### Filter operations and transitivity -/

theorem is_O_with.comp_tendsto (hcfg : is_O_with c f g l)
  {k : β → α} {l' : filter β} (hk : tendsto k l' l):
  is_O_with c (f ∘ k) (g ∘ k) l' :=
hk hcfg

theorem is_O.comp_tendsto (hfg : is_O f g l) {k : β → α} {l' : filter β} (hk : tendsto k l' l) :
  is_O (f ∘ k) (g ∘ k) l' :=
hfg.imp (λ c h, h.comp_tendsto hk)

theorem is_o.comp_tendsto (hfg : is_o f g l) {k : β → α} {l' : filter β} (hk : tendsto k l' l) :
  is_o (f ∘ k) (g ∘ k) l' :=
λ c cpos, (hfg cpos).comp_tendsto hk

theorem is_O_with.mono (h : is_O_with c f g l') (hl : l ≤ l') : is_O_with c f g l :=
hl h

theorem is_O.mono (h : is_O f g l') (hl : l ≤ l') : is_O f g l :=
h.imp (λ c h, h.mono hl)

theorem is_o.mono (h : is_o f g l') (hl : l ≤ l') : is_o f g l :=
λ c cpos, (h cpos).mono hl

theorem is_O_with.trans (hfg : is_O_with c f g l) (hgk : is_O_with c' g k l) (hc : 0 ≤ c) :
  is_O_with (c * c') f k l :=
begin
  filter_upwards [hfg, hgk],
  assume x hx hx',
  calc ∥f x∥ ≤ c * ∥g x∥ : hx
  ... ≤ c * (c' * ∥k x∥) : mul_le_mul_of_nonneg_left hx' hc
  ... = c * c' * ∥k x∥ : (mul_assoc _ _ _).symm
end

theorem is_O.trans (hfg : is_O f g' l) (hgk : is_O g' k l) : is_O f k l :=
let ⟨c, cnonneg, hc⟩ := hfg.exists_nonneg, ⟨c', hc'⟩ := hgk in (hc.trans hc' cnonneg).is_O

theorem is_o.trans_is_O_with (hfg : is_o f g l) (hgk : is_O_with c g k l) (hc : 0 < c) :
  is_o f k l :=
begin
  intros c' c'pos,
  have : 0 < c' / c, from div_pos c'pos hc,
  exact ((hfg this).trans hgk (le_of_lt this)).congr_const (div_mul_cancel _ (ne_of_gt hc))
end

theorem is_o.trans_is_O (hfg : is_o f g l) (hgk : is_O g k' l) : is_o f k' l :=
let ⟨c, cpos, hc⟩ := hgk.exists_pos in hfg.trans_is_O_with hc cpos

theorem is_O_with.trans_is_o (hfg : is_O_with c f g l) (hgk : is_o g k l) (hc : 0 < c) :
  is_o f k l :=
begin
  intros c' c'pos,
  have : 0 < c' / c, from div_pos c'pos hc,
  exact (hfg.trans (hgk this) (le_of_lt hc)).congr_const (mul_div_cancel' _ (ne_of_gt hc))
end

theorem is_O.trans_is_o (hfg : is_O f g' l) (hgk : is_o g' k l) : is_o f k l :=
let ⟨c, cpos, hc⟩ := hfg.exists_pos in hc.trans_is_o hgk cpos

theorem is_o.trans (hfg : is_o f g l) (hgk : is_o g k' l) : is_o f k' l :=
hfg.trans_is_O hgk.is_O

theorem is_o.trans' (hfg : is_o f g' l) (hgk : is_o g' k l) : is_o f k l :=
hfg.is_O.trans_is_o hgk

section

variable (l)

theorem is_O_with_of_le' (hfg : ∀ x, ∥f x∥ ≤ c * ∥g x∥) : is_O_with c f g l :=
univ_mem_sets' hfg

theorem is_O_with_of_le (hfg : ∀ x, ∥f x∥ ≤ ∥g x∥) : is_O_with 1 f g l :=
is_O_with_of_le' l $ λ x, by { rw one_mul, exact hfg x }

theorem is_O_of_le' (hfg : ∀ x, ∥f x∥ ≤ c * ∥g x∥) : is_O f g l :=
(is_O_with_of_le' l hfg).is_O

theorem is_O_of_le (hfg : ∀ x, ∥f x∥ ≤ ∥g x∥) : is_O f g l :=
(is_O_with_of_le l hfg).is_O

end

theorem is_O_with_refl (f : α → E) (l : filter α) : is_O_with 1 f f l :=
is_O_with_of_le l $ λ _, le_refl _

theorem is_O_refl (f : α → E) (l : filter α) : is_O f f l := (is_O_with_refl f l).is_O

theorem is_O_with.trans_le (hfg : is_O_with c f g l) (hgk : ∀ x, ∥g x∥ ≤ ∥k x∥) (hc : 0 ≤ c) :
  is_O_with c f k l :=
(hfg.trans (is_O_with_of_le l hgk) hc).congr_const $ mul_one c

theorem is_O.trans_le (hfg : is_O f g' l) (hgk : ∀ x, ∥g' x∥ ≤ ∥k x∥) :
  is_O f k l :=
hfg.trans (is_O_of_le l hgk)

section bot

variables (c f g)

theorem is_O_with_bot : is_O_with c f g ⊥ := trivial

theorem is_O_bot : is_O f g ⊥ := (is_O_with_bot c f g).is_O

theorem is_o_bot : is_o f g ⊥ := λ c _, is_O_with_bot c f g

end bot

theorem is_O_with.join (h : is_O_with c f g l) (h' : is_O_with c f g l') :
  is_O_with c f g (l ⊔ l') :=
mem_sup_sets.2 ⟨h, h'⟩

theorem is_O_with.join' (h : is_O_with c f g' l) (h' : is_O_with c' f g' l') :
  is_O_with (max c c') f g' (l ⊔ l') :=
mem_sup_sets.2 ⟨(h.weaken $ le_max_left c c'), (h'.weaken $ le_max_right c c')⟩

theorem is_O.join (h : is_O f g' l) (h' : is_O f g' l') : is_O f g' (l ⊔ l') :=
let ⟨c, hc⟩ := h, ⟨c', hc'⟩ := h' in (hc.join' hc').is_O

theorem is_o.join (h : is_o f g l) (h' : is_o f g l') :
  is_o f g (l ⊔ l') :=
λ c cpos, (h cpos).join (h' cpos)

/-! ### Simplification : norm -/

@[simp] theorem is_O_with_norm_right : is_O_with c f (λ x, ∥g' x∥) l ↔ is_O_with c f g' l :=
by simp only [is_O_with, norm_norm]

alias is_O_with_norm_right ↔ asymptotics.is_O_with.of_norm_right asymptotics.is_O_with.norm_right

@[simp] theorem is_O_norm_right : is_O f (λ x, ∥g' x∥) l ↔ is_O f g' l :=
exists_congr $ λ _,  is_O_with_norm_right

alias is_O_norm_right ↔ asymptotics.is_O.of_norm_right asymptotics.is_O.norm_right

@[simp] theorem is_o_norm_right : is_o f (λ x, ∥g' x∥) l ↔ is_o f g' l :=
forall_congr $ λ _, forall_congr $ λ _, is_O_with_norm_right

alias is_o_norm_right ↔ asymptotics.is_o.of_norm_right asymptotics.is_o.norm_right

@[simp] theorem is_O_with_norm_left : is_O_with c (λ x, ∥f' x∥) g l ↔ is_O_with c f' g l :=
by simp only [is_O_with, norm_norm]

alias is_O_with_norm_left ↔ asymptotics.is_O_with.of_norm_left asymptotics.is_O_with.norm_left

@[simp] theorem is_O_norm_left : is_O (λ x, ∥f' x∥) g l ↔ is_O f' g l :=
exists_congr $ λ _, is_O_with_norm_left

alias is_O_norm_left ↔ asymptotics.is_O.of_norm_left asymptotics.is_O.norm_left

@[simp] theorem is_o_norm_left : is_o (λ x, ∥f' x∥) g l ↔ is_o f' g l :=
forall_congr $ λ _, forall_congr $ λ _, is_O_with_norm_left

alias is_o_norm_left ↔ asymptotics.is_o.of_norm_left asymptotics.is_o.norm_left

theorem is_O_with_norm_norm :
  is_O_with c (λ x, ∥f' x∥) (λ x, ∥g' x∥) l ↔ is_O_with c f' g' l :=
is_O_with_norm_left.trans is_O_with_norm_right

alias is_O_with_norm_norm ↔ asymptotics.is_O_with.of_norm_norm asymptotics.is_O_with.norm_norm

theorem is_O_norm_norm :
  is_O (λ x, ∥f' x∥) (λ x, ∥g' x∥) l ↔ is_O f' g' l :=
is_O_norm_left.trans is_O_norm_right

alias is_O_norm_norm ↔ asymptotics.is_O.of_norm_norm asymptotics.is_O.norm_norm

theorem is_o_norm_norm :
  is_o (λ x, ∥f' x∥) (λ x, ∥g' x∥) l ↔ is_o f' g' l :=
is_o_norm_left.trans is_o_norm_right

alias is_o_norm_norm ↔ asymptotics.is_o.of_norm_norm asymptotics.is_o.norm_norm

/-! ### Simplification: negate -/

@[simp] theorem is_O_with_neg_right : is_O_with c f (λ x, -(g' x)) l ↔ is_O_with c f g' l :=
by simp only [is_O_with, norm_neg]

alias is_O_with_neg_right ↔ asymptotics.is_O_with.of_neg_right asymptotics.is_O_with.neg_right

@[simp] theorem is_O_neg_right : is_O f (λ x, -(g' x)) l ↔ is_O f g' l :=
exists_congr $ λ _, is_O_with_neg_right

alias is_O_neg_right ↔ asymptotics.is_O.of_neg_right asymptotics.is_O.neg_right

@[simp] theorem is_o_neg_right : is_o f (λ x, -(g' x)) l ↔ is_o f g' l :=
forall_congr $ λ _, forall_congr $ λ _, is_O_with_neg_right

alias is_o_neg_right ↔ asymptotics.is_o.of_neg_right asymptotics.is_o.neg_right

@[simp] theorem is_O_with_neg_left : is_O_with c (λ x, -(f' x)) g l ↔ is_O_with c f' g l :=
by simp only [is_O_with, norm_neg]

alias is_O_with_neg_left ↔ asymptotics.is_O_with.of_neg_left asymptotics.is_O_with.neg_left

@[simp] theorem is_O_neg_left : is_O (λ x, -(f' x)) g l ↔ is_O f' g l :=
exists_congr $ λ _, is_O_with_neg_left

alias is_O_neg_left ↔ asymptotics.is_O.of_neg_left asymptotics.is_O.neg_left

@[simp] theorem is_o_neg_left : is_o (λ x, -(f' x)) g l ↔ is_o f' g l :=
forall_congr $ λ _, forall_congr $ λ _, is_O_with_neg_left

alias is_o_neg_left ↔ asymptotics.is_o.of_neg_right asymptotics.is_o.neg_left

/-! ### Product of functions (right) -/

lemma is_O_with_fst_prod : is_O_with 1 f' (λ x, (f' x, g' x)) l :=
is_O_with_of_le l $ λ x, le_max_left _ _

lemma is_O_with_snd_prod : is_O_with 1 g' (λ x, (f' x, g' x)) l :=
is_O_with_of_le l $ λ x, le_max_right _ _

lemma is_O_fst_prod : is_O f' (λ x, (f' x, g' x)) l := is_O_with_fst_prod.is_O

lemma is_O_snd_prod : is_O g' (λ x, (f' x, g' x)) l := is_O_with_snd_prod.is_O

lemma is_O_fst_prod' {f' : α → E' × F'} : is_O (λ x, (f' x).1) f' l :=
is_O_fst_prod

lemma is_O_snd_prod' {f' : α → E' × F'} : is_O (λ x, (f' x).2) f' l :=
is_O_snd_prod

section

variables (f' k')

lemma is_O_with.prod_rightl (h : is_O_with c f g' l) (hc : 0 ≤ c) :
  is_O_with c f (λ x, (g' x, k' x)) l :=
(h.trans is_O_with_fst_prod hc).congr_const (mul_one c)

lemma is_O.prod_rightl (h : is_O f g' l) : is_O f (λx, (g' x, k' x)) l :=
let ⟨c, cnonneg, hc⟩ := h.exists_nonneg in (hc.prod_rightl k' cnonneg).is_O

lemma is_o.prod_rightl (h : is_o f g' l) : is_o f (λ x, (g' x, k' x)) l :=
λ c cpos, (h cpos).prod_rightl k' (le_of_lt cpos)

lemma is_O_with.prod_rightr (h : is_O_with c f g' l) (hc : 0 ≤ c) :
  is_O_with c f (λ x, (f' x, g' x)) l :=
(h.trans is_O_with_snd_prod hc).congr_const (mul_one c)

lemma is_O.prod_rightr (h : is_O f g' l) : is_O f (λx, (f' x, g' x)) l :=
let ⟨c, cnonneg, hc⟩ := h.exists_nonneg in (hc.prod_rightr f' cnonneg).is_O

lemma is_o.prod_rightr (h : is_o f g' l) : is_o f (λx, (f' x, g' x)) l :=
λ c cpos, (h cpos).prod_rightr f' (le_of_lt cpos)

end

lemma is_O_with.prod_left_same (hf : is_O_with c f' k' l) (hg : is_O_with c g' k' l) :
  is_O_with c (λ x, (f' x, g' x)) k' l :=
begin
  filter_upwards [hf, hg],
  simp only [mem_set_of_eq],
  exact λ x, max_le
end

lemma is_O_with.prod_left (hf : is_O_with c f' k' l) (hg : is_O_with c' g' k' l) :
  is_O_with (max c c') (λ x, (f' x, g' x)) k' l :=
(hf.weaken $ le_max_left c c').prod_left_same (hg.weaken $ le_max_right c c')

lemma is_O_with.prod_left_fst (h : is_O_with c (λ x, (f' x, g' x)) k' l) :
  is_O_with c f' k' l :=
(is_O_with_fst_prod.trans h zero_le_one).congr_const $ one_mul c

lemma is_O_with.prod_left_snd (h : is_O_with c (λ x, (f' x, g' x)) k' l) :
  is_O_with c g' k' l :=
(is_O_with_snd_prod.trans h zero_le_one).congr_const $ one_mul c

lemma is_O_with_prod_left :
   is_O_with c (λ x, (f' x, g' x)) k' l ↔ is_O_with c f' k' l ∧ is_O_with c g' k' l :=
⟨λ h, ⟨h.prod_left_fst, h.prod_left_snd⟩, λ h, h.1.prod_left_same h.2⟩

lemma is_O.prod_left (hf : is_O f' k' l) (hg : is_O g' k' l) : is_O (λ x, (f' x, g' x)) k' l :=
let ⟨c, hf⟩ := hf, ⟨c', hg⟩ := hg in (hf.prod_left hg).is_O

lemma is_O.prod_left_fst (h : is_O (λ x, (f' x, g' x)) k' l) : is_O f' k' l :=
is_O_fst_prod.trans h

lemma is_O.prod_left_snd (h : is_O (λ x, (f' x, g' x)) k' l) : is_O g' k' l :=
is_O_snd_prod.trans h

@[simp] lemma is_O_prod_left :
  is_O (λ x, (f' x, g' x)) k' l ↔ is_O f' k' l ∧ is_O g' k' l :=
⟨λ h, ⟨h.prod_left_fst, h.prod_left_snd⟩, λ h, h.1.prod_left h.2⟩

lemma is_o.prod_left (hf : is_o f' k' l) (hg : is_o g' k' l) : is_o (λ x, (f' x, g' x)) k' l :=
λ c hc, (hf hc).prod_left_same (hg hc)

lemma is_o.prod_left_fst (h : is_o (λ x, (f' x, g' x)) k' l) : is_o f' k' l :=
is_O_fst_prod.trans_is_o h

lemma is_o.prod_left_snd (h : is_o (λ x, (f' x, g' x)) k' l) : is_o g' k' l :=
is_O_snd_prod.trans_is_o h

@[simp] lemma is_o_prod_left :
  is_o (λ x, (f' x, g' x)) k' l ↔ is_o f' k' l ∧ is_o g' k' l :=
⟨λ h, ⟨h.prod_left_fst, h.prod_left_snd⟩, λ h, h.1.prod_left h.2⟩

/-! ### Addition and subtraction -/

section add_sub

variables {c₁ c₂ : ℝ} {f₁ f₂ : α → E'}

theorem is_O_with.add (h₁ : is_O_with c₁ f₁ g l) (h₂ : is_O_with c₂ f₂ g l) :
  is_O_with (c₁ + c₂) (λ x, f₁ x + f₂ x) g l :=
by filter_upwards [h₁, h₂] λ x hx₁ hx₂,
calc ∥f₁ x + f₂ x∥ ≤ c₁ * ∥g x∥ + c₂ * ∥g x∥ : norm_add_le_of_le hx₁ hx₂
               ... = (c₁ + c₂) * ∥g x∥       : (add_mul _ _ _).symm

theorem is_O.add : is_O f₁ g l → is_O f₂ g l → is_O (λ x, f₁ x + f₂ x) g l
| ⟨c₁, hc₁⟩ ⟨c₂, hc₂⟩ := (hc₁.add hc₂).is_O

theorem is_o.add (h₁ : is_o f₁ g l) (h₂ : is_o f₂ g l) : is_o (λ x, f₁ x + f₂ x) g l :=
λ c cpos, ((h₁ $ half_pos cpos).add (h₂ $ half_pos cpos)).congr_const (add_halves c)

theorem is_O.add_is_o (h₁ : is_O f₁ g l) (h₂ : is_o f₂ g l) : is_O (λ x, f₁ x + f₂ x) g l :=
h₁.add h₂.is_O

theorem is_o.add_is_O (h₁ : is_o f₁ g l) (h₂ : is_O f₂ g l) : is_O (λ x, f₁ x + f₂ x) g l :=
h₁.is_O.add h₂

theorem is_O_with.add_is_o (h₁ : is_O_with c₁ f₁ g l) (h₂ : is_o f₂ g l) (hc : c₁ < c₂) :
  is_O_with c₂ (λx, f₁ x + f₂ x) g l :=
(h₁.add (h₂ (sub_pos.2 hc))).congr_const (add_sub_cancel'_right _ _)

theorem is_o.add_is_O_with (h₁ : is_o f₁ g l) (h₂ : is_O_with c₁ f₂ g l) (hc : c₁ < c₂) :
  is_O_with c₂ (λx, f₁ x + f₂ x) g l :=
(h₂.add_is_o h₁ hc).congr_left $ λ _, add_comm _ _

theorem is_O_with.sub (h₁ : is_O_with c₁ f₁ g l) (h₂ : is_O_with c₂ f₂ g l) :
  is_O_with (c₁ + c₂) (λ x, f₁ x - f₂ x) g l :=
h₁.add h₂.neg_left

theorem is_O_with.sub_is_o (h₁ : is_O_with c₁ f₁ g l) (h₂ : is_o f₂ g l) (hc : c₁ < c₂) :
  is_O_with c₂ (λ x, f₁ x - f₂ x) g l :=
h₁.add_is_o h₂.neg_left hc

theorem is_O.sub (h₁ : is_O f₁ g l) (h₂ : is_O f₂ g l) : is_O (λ x, f₁ x - f₂ x) g l :=
h₁.add h₂.neg_left

theorem is_o.sub (h₁ : is_o f₁ g l) (h₂ : is_o f₂ g l) : is_o (λ x, f₁ x - f₂ x) g l :=
h₁.add h₂.neg_left

end add_sub

/-! ### Lemmas about `is_O (f₁ - f₂) g l` / `is_o (f₁ - f₂) g l` treated as a binary relation -/

section is_oO_as_rel

variables {f₁ f₂ f₃ : α → E'}

theorem is_O_with.symm (h : is_O_with c (λ x, f₁ x - f₂ x) g l) :
  is_O_with c (λ x, f₂ x - f₁ x) g l :=
h.neg_left.congr_left $ λ x, neg_sub _ _

theorem is_O_with_comm :
  is_O_with c (λ x, f₁ x - f₂ x) g l ↔ is_O_with c (λ x, f₂ x - f₁ x) g l :=
⟨is_O_with.symm, is_O_with.symm⟩

theorem is_O.symm (h : is_O (λ x, f₁ x - f₂ x) g l) : is_O (λ x, f₂ x - f₁ x) g l :=
h.neg_left.congr_left $ λ x, neg_sub _ _

theorem is_O_comm : is_O (λ x, f₁ x - f₂ x) g l ↔ is_O (λ x, f₂ x - f₁ x) g l :=
⟨is_O.symm, is_O.symm⟩

theorem is_o.symm (h : is_o (λ x, f₁ x - f₂ x) g l) : is_o (λ x, f₂ x - f₁ x) g l :=
by simpa only [neg_sub] using h.neg_left

theorem is_o_comm : is_o (λ x, f₁ x - f₂ x) g l ↔ is_o (λ x, f₂ x - f₁ x) g l :=
⟨is_o.symm, is_o.symm⟩

theorem is_O_with.triangle (h₁ : is_O_with c (λ x, f₁ x - f₂ x) g l)
  (h₂ : is_O_with c' (λ x, f₂ x - f₃ x) g l) :
  is_O_with (c + c') (λ x, f₁ x - f₃ x) g l :=
(h₁.add h₂).congr_left $ λ x, sub_add_sub_cancel _ _ _

theorem is_O.triangle (h₁ : is_O (λ x, f₁ x - f₂ x) g l) (h₂ : is_O (λ x, f₂ x - f₃ x) g l) :
  is_O (λ x, f₁ x - f₃ x) g l :=
(h₁.add h₂).congr_left $ λ x, sub_add_sub_cancel _ _ _

theorem is_o.triangle (h₁ : is_o (λ x, f₁ x - f₂ x) g l) (h₂ : is_o (λ x, f₂ x - f₃ x) g l) :
  is_o (λ x, f₁ x - f₃ x) g l :=
(h₁.add h₂).congr_left $ λ x, sub_add_sub_cancel _ _ _

theorem is_O.congr_of_sub (h : is_O (λ x, f₁ x - f₂ x) g l) :
  is_O f₁ g l ↔ is_O f₂ g l :=
⟨λ h', (h'.sub h).congr_left (λ x, sub_sub_cancel _ _),
 λ h', (h.add h').congr_left (λ x, sub_add_cancel _ _)⟩

theorem is_o.congr_of_sub (h : is_o (λ x, f₁ x - f₂ x) g l) :
  is_o f₁ g l ↔ is_o f₂ g l :=
⟨λ h', (h'.sub h).congr_left (λ x, sub_sub_cancel _ _),
 λ h', (h.add h').congr_left (λ x, sub_add_cancel _ _)⟩

end is_oO_as_rel

/-! ### Zero, one, and other constants -/

section zero_const

variables (g g' l)

theorem is_o_zero : is_o (λ x, (0 : E')) g' l :=
λ c hc, univ_mem_sets' $ λ x, by simpa using mul_nonneg (le_of_lt hc) (norm_nonneg $ g' x)

theorem is_O_with_zero (hc : 0 ≤ c) : is_O_with c (λ x, (0 : E')) g' l :=
univ_mem_sets' $ λ x, by simpa using mul_nonneg hc (norm_nonneg $ g' x)

theorem is_O_with_zero' : is_O_with 0 (λ x, (0 : E')) g l :=
univ_mem_sets' $ λ x, by simp

theorem is_O_zero : is_O (λ x, (0 : E')) g l := ⟨0, is_O_with_zero' _ _⟩

theorem is_O_refl_left : is_O (λ x, f' x - f' x) g' l :=
(is_O_zero g' l).congr_left $ λ x, (sub_self _).symm

theorem is_o_refl_left : is_o (λ x, f' x - f' x) g' l :=
(is_o_zero g' l).congr_left $ λ x, (sub_self _).symm

variables {g g' l}

theorem is_O_with_zero_right_iff :
  is_O_with c f' (λ x, (0 : F')) l ↔ ∀ᶠ x in l, f' x = 0 :=
by simp only [is_O_with, exists_prop, true_and, norm_zero, mul_zero, norm_le_zero_iff]

theorem is_O_zero_right_iff : is_O f' (λ x, (0 : F')) l ↔ ∀ᶠ x in l, f' x = 0 :=
⟨λ h, let ⟨c, hc⟩ := h in  (is_O_with_zero_right_iff).1 hc,
  λ h, (is_O_with_zero_right_iff.2 h : is_O_with 1 _ _ _).is_O⟩

theorem is_o_zero_right_iff :
  is_o f' (λ x, (0 : F')) l ↔ ∀ᶠ x in l, f' x = 0 :=
⟨λ h, is_O_zero_right_iff.1 h.is_O,
  λ h c hc, is_O_with_zero_right_iff.2 h⟩

theorem is_O_with_const_const (c : E) {c' : F'} (hc' : c' ≠ 0) (l : filter α) :
  is_O_with (∥c∥ / ∥c'∥) (λ x : α, c) (λ x, c') l :=
begin
  apply univ_mem_sets',
  intro x,
  rw [mem_set_of_eq, div_mul_cancel],
  rwa [ne.def, norm_eq_zero]
end

theorem is_O_const_const (c : E) {c' : F'} (hc' : c' ≠ 0) (l : filter α) :
  is_O (λ x : α, c) (λ x, c') l :=
(is_O_with_const_const c hc' l).is_O

end zero_const

theorem is_O_with_const_one (c : E) (l : filter α) : is_O_with ∥c∥ (λ x : α, c) (λ x, (1 : 𝕜)) l :=
begin
  refine (is_O_with_const_const c _ l).congr_const _,
  { rw [normed_field.norm_one, div_one] },
  { exact one_ne_zero }
end

theorem is_O_const_one (c : E) (l : filter α) : is_O (λ x : α, c) (λ x, (1 : 𝕜)) l :=
(is_O_with_const_one c l).is_O

section

variable (𝕜)

theorem is_o_const_iff_is_o_one {c : F'} (hc : c ≠ 0) :
  is_o f (λ x, c) l ↔ is_o f (λ x, (1:𝕜)) l :=
⟨λ h, h.trans_is_O $ is_O_const_one c l, λ h, h.trans_is_O $ is_O_const_const _ hc _⟩

end

theorem is_o_const_iff {c : F'} (hc : c ≠ 0) :
  is_o f' (λ x, c) l ↔ tendsto f' l (𝓝 0) :=
(is_o_const_iff_is_o_one ℝ hc).trans
begin
  clear hc c,
  simp only [is_o, is_O_with, normed_field.norm_one, mul_one,
    metric.nhds_basis_closed_ball.tendsto_right_iff, metric.mem_closed_ball, dist_zero_right]
end

theorem is_O_const_of_tendsto {y : E'} (h : tendsto f' l (𝓝 y)) {c : F'} (hc : c ≠ 0) :
  is_O f' (λ x, c) l :=
begin
  refine is_O.trans _ (is_O_const_const (∥y∥ + 1) hc l),
  use 1,
  simp only [is_O_with, one_mul],
  have : tendsto (λx, ∥f' x∥) l (𝓝 ∥y∥), from (continuous_norm.tendsto _).comp h,
  have Iy : ∥y∥ < ∥∥y∥ + 1∥, from lt_of_lt_of_le (lt_add_one _) (le_abs_self _),
  exact this (ge_mem_nhds Iy)
end

section

variable (𝕜)

theorem is_o_one_iff : is_o f' (λ x, (1 : 𝕜)) l ↔ tendsto f' l (𝓝 0) :=
is_o_const_iff one_ne_zero

theorem is_O_one_of_tendsto {y : E'} (h : tendsto f' l (𝓝 y)) :
  is_O f' (λ x, (1:𝕜)) l :=
is_O_const_of_tendsto h one_ne_zero

theorem is_O.trans_tendsto_nhds (hfg : is_O f g' l) {y : F'} (hg : tendsto g' l (𝓝 y)) :
  is_O f (λ x, (1:𝕜)) l :=
hfg.trans $ is_O_one_of_tendsto 𝕜 hg

end

theorem is_O.trans_tendsto (hfg : is_O f' g' l) (hg : tendsto g' l (𝓝 0)) :
  tendsto f' l (𝓝 0) :=
(is_o_one_iff ℝ).1 $ hfg.trans_is_o $ (is_o_one_iff ℝ).2 hg

theorem is_o.trans_tendsto (hfg : is_o f' g' l) (hg : tendsto g' l (𝓝 0)) :
  tendsto f' l (𝓝 0) :=
hfg.is_O.trans_tendsto hg

/-! ### Multiplication by a constant -/

theorem is_O_with_const_mul_self (c : R) (f : α → R) (l : filter α) :
  is_O_with ∥c∥ (λ x, c * f x) f l :=
is_O_with_of_le' _ $ λ x, norm_mul_le _ _

theorem is_O_const_mul_self (c : R) (f : α → R) (l : filter α) :
  is_O (λ x, c * f x) f l :=
(is_O_with_const_mul_self c f l).is_O

theorem is_O_with.const_mul_left {f : α → R} (h : is_O_with c f g l) (c' : R) :
  is_O_with (∥c'∥ * c) (λ x, c' * f x) g l :=
(is_O_with_const_mul_self c' f l).trans h (norm_nonneg c')

theorem is_O.const_mul_left {f : α → R} (h : is_O f g l) (c' : R) :
  is_O (λ x, c' * f x) g l :=
let ⟨c, hc⟩ := h in (hc.const_mul_left c').is_O

theorem is_O_with_self_const_mul' (u : units R) (f : α → R) (l : filter α) :
  is_O_with ∥(↑u⁻¹:R)∥ f (λ x, ↑u * f x) l :=
(is_O_with_const_mul_self ↑u⁻¹ _ l).congr_left $ λ x, u.inv_mul_cancel_left (f x)

theorem is_O_with_self_const_mul (c : 𝕜) (hc : c ≠ 0) (f : α → 𝕜) (l : filter α) :
  is_O_with ∥c∥⁻¹ f (λ x, c * f x) l :=
(is_O_with_self_const_mul' (units.mk0 c hc) f l).congr_const $
  normed_field.norm_inv c

theorem is_O_self_const_mul' {c : R} (hc : is_unit c) (f : α → R) (l : filter α) :
  is_O f (λ x, c * f x) l :=
let ⟨u, hu⟩ := hc in hu ▸ (is_O_with_self_const_mul' u f l).is_O

theorem is_O_self_const_mul (c : 𝕜) (hc : c ≠ 0) (f : α → 𝕜) (l : filter α) :
  is_O f (λ x, c * f x) l :=
is_O_self_const_mul' (is_unit.mk0 c hc) f l

theorem is_O_const_mul_left_iff' {f : α → R} {c : R} (hc : is_unit c) :
  is_O (λ x, c * f x) g l ↔ is_O f g l :=
⟨(is_O_self_const_mul' hc f l).trans, λ h, h.const_mul_left c⟩

theorem is_O_const_mul_left_iff {f : α → 𝕜} {c : 𝕜} (hc : c ≠ 0) :
  is_O (λ x, c * f x) g l ↔ is_O f g l :=
is_O_const_mul_left_iff' $ is_unit.mk0 c hc

theorem is_o.const_mul_left {f : α → R} (h : is_o f g l) (c : R) :
  is_o (λ x, c * f x) g l :=
(is_O_const_mul_self c f l).trans_is_o h

theorem is_o_const_mul_left_iff' {f : α → R} {c : R} (hc : is_unit c) :
  is_o (λ x, c * f x) g l ↔ is_o f g l :=
⟨(is_O_self_const_mul' hc f l).trans_is_o, λ h, h.const_mul_left c⟩

theorem is_o_const_mul_left_iff {f : α → 𝕜} {c : 𝕜} (hc : c ≠ 0) :
  is_o (λ x, c * f x) g l ↔ is_o f g l :=
is_o_const_mul_left_iff' $ is_unit.mk0 c hc

theorem is_O_with.of_const_mul_right {g : α → R} {c : R} (hc' : 0 ≤ c')
  (h : is_O_with c' f (λ x, c * g x) l) :
  is_O_with (c' * ∥c∥) f g l :=
h.trans (is_O_with_const_mul_self c g l) hc'

theorem is_O.of_const_mul_right {g : α → R} {c : R}
  (h : is_O f (λ x, c * g x) l) :
  is_O f g l :=
let ⟨c, cnonneg, hc⟩ := h.exists_nonneg in (hc.of_const_mul_right cnonneg).is_O

theorem is_O_with.const_mul_right' {g : α → R} {u : units R} {c' : ℝ} (hc' : 0 ≤ c')
  (h : is_O_with c' f g l) :
  is_O_with (c' * ∥(↑u⁻¹:R)∥) f (λ x, ↑u * g x) l :=
h.trans (is_O_with_self_const_mul' _ _ _) hc'

theorem is_O_with.const_mul_right {g : α → 𝕜} {c : 𝕜} (hc : c ≠ 0)
  {c' : ℝ} (hc' : 0 ≤ c') (h : is_O_with c' f g l) :
  is_O_with (c' * ∥c∥⁻¹) f (λ x, c * g x) l :=
h.trans (is_O_with_self_const_mul c hc g l) hc'

theorem is_O.const_mul_right' {g : α → R} {c : R} (hc : is_unit c) (h : is_O f g l) :
  is_O f (λ x, c * g x) l :=
h.trans (is_O_self_const_mul' hc g l)

theorem is_O.const_mul_right {g : α → 𝕜} {c : 𝕜} (hc : c ≠ 0) (h : is_O f g l) :
  is_O f (λ x, c * g x) l :=
h.const_mul_right' $ is_unit.mk0 c hc

theorem is_O_const_mul_right_iff' {g : α → R} {c : R} (hc : is_unit c) :
  is_O f (λ x, c * g x) l ↔ is_O f g l :=
⟨λ h, h.of_const_mul_right, λ h, h.const_mul_right' hc⟩

theorem is_O_const_mul_right_iff {g : α → 𝕜} {c : 𝕜} (hc : c ≠ 0) :
  is_O f (λ x, c * g x) l ↔ is_O f g l :=
is_O_const_mul_right_iff' $ is_unit.mk0 c hc

theorem is_o.of_const_mul_right {g : α → R} {c : R} (h : is_o f (λ x, c * g x) l) :
  is_o f g l :=
h.trans_is_O (is_O_const_mul_self c g l)

theorem is_o.const_mul_right' {g : α → R} {c : R} (hc : is_unit c) (h : is_o f g l) :
  is_o f (λ x, c * g x) l :=
h.trans_is_O (is_O_self_const_mul' hc g l)

theorem is_o.const_mul_right {g : α → 𝕜} {c : 𝕜} (hc : c ≠ 0) (h : is_o f g l) :
  is_o f (λ x, c * g x) l :=
h.const_mul_right' $ is_unit.mk0 c hc

theorem is_o_const_mul_right_iff' {g : α → R} {c : R} (hc : is_unit c) :
  is_o f (λ x, c * g x) l ↔ is_o f g l :=
⟨λ h, h.of_const_mul_right, λ h, h.const_mul_right' hc⟩

theorem is_o_const_mul_right_iff {g : α → 𝕜} {c : 𝕜} (hc : c ≠ 0) :
  is_o f (λ x, c * g x) l ↔ is_o f g l :=
is_o_const_mul_right_iff' $ is_unit.mk0 c hc

/-! ### Multiplication -/

theorem is_O_with.mul {f₁ f₂ : α → R} {g₁ g₂ : α → 𝕜} {c₁ c₂ : ℝ}
  (h₁ : is_O_with c₁ f₁ g₁ l) (h₂ : is_O_with c₂ f₂ g₂ l) :
  is_O_with (c₁ * c₂) (λ x, f₁ x * f₂ x) (λ x, g₁ x * g₂ x) l :=
begin
  filter_upwards [h₁, h₂], simp only [mem_set_of_eq],
  intros x hx₁ hx₂,
  apply le_trans (norm_mul_le _ _),
  convert mul_le_mul hx₁ hx₂ (norm_nonneg _) (le_trans (norm_nonneg _) hx₁) using 1,
  rw normed_field.norm_mul,
  ac_refl
end

theorem is_O.mul {f₁ f₂ : α → R} {g₁ g₂ : α → 𝕜}
  (h₁ : is_O f₁ g₁ l) (h₂ : is_O f₂ g₂ l) :
  is_O (λ x, f₁ x * f₂ x) (λ x, g₁ x * g₂ x) l :=
let ⟨c, hc⟩ := h₁, ⟨c', hc'⟩ := h₂ in (hc.mul hc').is_O

theorem is_O.mul_is_o {f₁ f₂ : α → R} {g₁ g₂ : α → 𝕜}
  (h₁ : is_O f₁ g₁ l) (h₂ : is_o f₂ g₂ l) :
  is_o (λ x, f₁ x * f₂ x) (λ x, g₁ x * g₂ x) l :=
begin
  intros c cpos,
  rcases h₁.exists_pos with ⟨c', c'pos, hc'⟩,
  exact (hc'.mul (h₂ (div_pos cpos c'pos))).congr_const (mul_div_cancel' _ (ne_of_gt c'pos))
end

theorem is_o.mul_is_O {f₁ f₂ : α → R} {g₁ g₂ : α → 𝕜}
  (h₁ : is_o f₁ g₁ l) (h₂ : is_O f₂ g₂ l) :
  is_o (λ x, f₁ x * f₂ x) (λ x, g₁ x * g₂ x) l :=
begin
  intros c cpos,
  rcases h₂.exists_pos with ⟨c', c'pos, hc'⟩,
  exact ((h₁ (div_pos cpos c'pos)).mul hc').congr_const (div_mul_cancel _ (ne_of_gt c'pos))
end

theorem is_o.mul {f₁ f₂ : α → R} {g₁ g₂ : α → 𝕜} (h₁ : is_o f₁ g₁ l) (h₂ : is_o f₂ g₂ l) :
  is_o (λ x, f₁ x * f₂ x) (λ x, g₁ x * g₂ x) l :=
h₁.mul_is_O h₂.is_O

/-! ### Scalar multiplication -/

section smul_const
variables [normed_space 𝕜 E']

theorem is_O_with.const_smul_left (h : is_O_with c f' g l) (c' : 𝕜) :
  is_O_with (∥c'∥ * c) (λ x, c' • f' x) g l :=
by refine ((h.norm_left.const_mul_left (∥c'∥)).congr _ _ (λ _, rfl)).of_norm_left;
    intros; simp only [norm_norm, norm_smul]

theorem is_O_const_smul_left_iff {c : 𝕜} (hc : c ≠ 0) :
  is_O (λ x, c • f' x) g l ↔ is_O f' g l :=
begin
  have cne0 : ∥c∥ ≠ 0, from mt norm_eq_zero.mp hc,
  rw [←is_O_norm_left], simp only [norm_smul],
  rw [is_O_const_mul_left_iff cne0, is_O_norm_left],
end

theorem is_o_const_smul_left (h : is_o f' g l) (c : 𝕜) :
  is_o (λ x, c • f' x) g l :=
begin
  refine ((h.norm_left.const_mul_left (∥c∥)).congr_left _).of_norm_left,
  exact λ x, (norm_smul _ _).symm
end

theorem is_o_const_smul_left_iff {c : 𝕜} (hc : c ≠ 0) :
  is_o (λ x, c • f' x) g l ↔ is_o f' g l :=
begin
  have cne0 : ∥c∥ ≠ 0, from mt norm_eq_zero.mp hc,
  rw [←is_o_norm_left], simp only [norm_smul],
  rw [is_o_const_mul_left_iff cne0, is_o_norm_left]
end

theorem is_O_const_smul_right {c : 𝕜} (hc : c ≠ 0) :
  is_O f (λ x, c • f' x) l ↔ is_O f f' l :=
begin
  have cne0 : ∥c∥ ≠ 0, from mt norm_eq_zero.mp hc,
  rw [←is_O_norm_right], simp only [norm_smul],
  rw [is_O_const_mul_right_iff cne0, is_O_norm_right]
end

theorem is_o_const_smul_right {c : 𝕜} (hc : c ≠ 0) :
  is_o f (λ x, c • f' x) l ↔ is_o f f' l :=
begin
  have cne0 : ∥c∥ ≠ 0, from mt norm_eq_zero.mp hc,
  rw [←is_o_norm_right], simp only [norm_smul],
  rw [is_o_const_mul_right_iff cne0, is_o_norm_right]
end

end smul_const

section smul

variables [normed_space 𝕜 E'] [normed_space 𝕜 F']

theorem is_O_with.smul {k₁ k₂ : α → 𝕜} (h₁ : is_O_with c k₁ k₂ l) (h₂ : is_O_with c' f' g' l) :
  is_O_with (c * c') (λ x, k₁ x • f' x) (λ x, k₂ x • g' x) l :=
by refine ((h₁.norm_norm.mul h₂.norm_norm).congr rfl _ _).of_norm_norm;
  by intros; simp only [norm_smul]

theorem is_O.smul {k₁ k₂ : α → 𝕜} (h₁ : is_O k₁ k₂ l) (h₂ : is_O f' g' l) :
  is_O (λ x, k₁ x • f' x) (λ x, k₂ x • g' x) l :=
by refine ((h₁.norm_norm.mul h₂.norm_norm).congr _ _).of_norm_norm;
  by intros; simp only [norm_smul]

theorem is_O.smul_is_o {k₁ k₂ : α → 𝕜} (h₁ : is_O k₁ k₂ l) (h₂ : is_o f' g' l) :
  is_o (λ x, k₁ x • f' x) (λ x, k₂ x • g' x) l :=
by refine ((h₁.norm_norm.mul_is_o h₂.norm_norm).congr _ _).of_norm_norm;
  by intros; simp only [norm_smul]

theorem is_o.smul_is_O {k₁ k₂ : α → 𝕜} (h₁ : is_o k₁ k₂ l) (h₂ : is_O f' g' l) :
  is_o (λ x, k₁ x • f' x) (λ x, k₂ x • g' x) l :=
by refine ((h₁.norm_norm.mul_is_O h₂.norm_norm).congr _ _).of_norm_norm;
  by intros; simp only [norm_smul]

theorem is_o.smul {k₁ k₂ : α → 𝕜} (h₁ : is_o k₁ k₂ l) (h₂ : is_o f' g' l) :
  is_o (λ x, k₁ x • f' x) (λ x, k₂ x • g' x) l :=
by refine ((h₁.norm_norm.mul h₂.norm_norm).congr _ _).of_norm_norm;
  by intros; simp only [norm_smul]

end smul

/-! ### Sum -/

section sum

variables {ι : Type*} {A : ι → α → E'} {C : ι → ℝ} {s : finset ι}

theorem is_O_with.sum (h : ∀ i ∈ s, is_O_with (C i) (A i) g l) :
  is_O_with (∑ i in s, C i) (λ x, ∑ i in s, A i x) g l :=
begin
  induction s using finset.induction_on with i s is IH,
  { simp only [is_O_with_zero', finset.sum_empty, forall_true_iff] },
  { simp only [is, finset.sum_insert, not_false_iff],
    exact (h _ (finset.mem_insert_self i s)).add (IH (λ j hj, h _ (finset.mem_insert_of_mem hj))) }
end

theorem is_O.sum (h : ∀ i ∈ s, is_O (A i) g l) :
  is_O (λ x, ∑ i in s, A i x) g l :=
begin
  induction s using finset.induction_on with i s is IH,
  { simp only [is_O_zero, finset.sum_empty, forall_true_iff] },
  { simp only [is, finset.sum_insert, not_false_iff],
    exact (h _ (finset.mem_insert_self i s)).add (IH (λ j hj, h _ (finset.mem_insert_of_mem hj))) }
end

theorem is_o.sum (h : ∀ i ∈ s, is_o (A i) g' l) :
  is_o (λ x, ∑ i in s, A i x) g' l :=
begin
  induction s using finset.induction_on with i s is IH,
  { simp only [is_o_zero, finset.sum_empty, forall_true_iff] },
  { simp only [is, finset.sum_insert, not_false_iff],
    exact (h _ (finset.mem_insert_self i s)).add (IH (λ j hj, h _ (finset.mem_insert_of_mem hj))) }
end

end sum

/-! ### Relation between `f = o(g)` and `f / g → 0` -/

theorem is_o.tendsto_0 {f g : α → 𝕜} {l : filter α} (h : is_o f g l) :
  tendsto (λ x, f x / (g x)) l (𝓝 0) :=
have eq₁ : is_o (λ x, f x / g x) (λ x, g x / g x) l,
  from h.mul_is_O (is_O_refl _ _),
have eq₂ : is_O (λ x, g x / g x) (λ x, (1 : 𝕜)) l,
  from is_O_of_le _ (λ x, by by_cases h : ∥g x∥ = 0; simp [h, zero_le_one]),
(is_o_one_iff 𝕜).mp (eq₁.trans_is_O eq₂)

private theorem is_o_of_tendsto {f g : α → 𝕜} {l : filter α}
    (hgf : ∀ x, g x = 0 → f x = 0) (h : tendsto (λ x, f x / (g x)) l (𝓝 0)) :
  is_o f g l :=
have eq₁ : is_o (λ x, f x / (g x)) (λ x, (1 : 𝕜)) l,
  from (is_o_one_iff _).mpr h,
have eq₂ : is_o (λ x, f x / g x * g x) g l,
  by convert eq₁.mul_is_O (is_O_refl _ _); simp,
have eq₃ : is_O f (λ x, f x / g x * g x) l,
  begin
    refine is_O_of_le _ (λ x, _),
    by_cases H : g x = 0,
    { simp only [H, hgf _ H, mul_zero] },
    { simp only [div_mul_cancel _ H] }
  end,
eq₃.trans_is_o eq₂

theorem is_o_iff_tendsto {f g : α → 𝕜} {l : filter α}
    (hgf : ∀ x, g x = 0 → f x = 0) :
  is_o f g l ↔ tendsto (λ x, f x / (g x)) l (𝓝 0) :=
iff.intro is_o.tendsto_0 (is_o_of_tendsto hgf)

/-! ### Miscellanous lemmas -/

theorem is_o_pow_pow {m n : ℕ} (h : m < n) :
  is_o (λ(x : 𝕜), x^n) (λx, x^m) (𝓝 0) :=
begin
  let p := n - m,
  have nmp : n = m + p := (nat.add_sub_cancel' (le_of_lt h)).symm,
  have : (λ(x : 𝕜), x^m) = (λx, x^m * 1), by simp only [mul_one],
  simp only [this, pow_add, nmp],
  refine is_O.mul_is_o (is_O_refl _ _) ((is_o_one_iff _).2 _),
  convert (continuous_pow p).tendsto (0 : 𝕜),
  exact (zero_pow (nat.sub_pos_of_lt h)).symm
end

theorem is_o_pow_id {n : ℕ} (h : 1 < n) :
  is_o (λ(x : 𝕜), x^n) (λx, x) (𝓝 0) :=
by { convert is_o_pow_pow h, simp only [pow_one] }

theorem is_O_with.right_le_sub_of_lt_1 {f₁ f₂ : α → E'} (h : is_O_with c f₁ f₂ l) (hc : c < 1) :
  is_O_with (1 / (1 - c)) f₂ (λx, f₂ x - f₁ x) l :=
mem_sets_of_superset h $ λ x hx,
begin
  simp only [mem_set_of_eq] at hx ⊢,
  rw [mul_comm, one_div_eq_inv, ← div_eq_mul_inv, le_div_iff, mul_sub, mul_one, mul_comm],
  { exact le_trans (sub_le_sub_left hx _) (norm_sub_norm_le _ _) },
  { exact sub_pos.2 hc }
end

theorem is_O_with.right_le_add_of_lt_1 {f₁ f₂ : α → E'} (h : is_O_with c f₁ f₂ l) (hc : c < 1) :
  is_O_with (1 / (1 - c)) f₂ (λx, f₁ x + f₂ x) l :=
(h.neg_right.right_le_sub_of_lt_1 hc).neg_right.of_neg_left.congr rfl (λ x, rfl)
  (λ x, by rw [neg_sub, sub_neg_eq_add])

theorem is_o.right_is_O_sub {f₁ f₂ : α → E'} (h : is_o f₁ f₂ l) :
  is_O f₂ (λx, f₂ x - f₁ x) l :=
((h.def' one_half_pos).right_le_sub_of_lt_1 one_half_lt_one).is_O

theorem is_o.right_is_O_add {f₁ f₂ : α → E'} (h : is_o f₁ f₂ l) :
  is_O f₂ (λx, f₁ x + f₂ x) l :=
((h.def' one_half_pos).right_le_add_of_lt_1 one_half_lt_one).is_O

end asymptotics

namespace local_homeomorph

variables {α : Type*} {β : Type*} [topological_space α] [topological_space β]

variables {E : Type*} [has_norm E] {F : Type*} [has_norm F]

open asymptotics

/-- Transfer `is_O_with` over a `local_homeomorph`. -/
lemma is_O_with_congr (e : local_homeomorph α β) {b : β} (hb : b ∈ e.target)
  {f : β → E} {g : β → F} {C : ℝ} :
  is_O_with C f g (𝓝 b) ↔ is_O_with C (f ∘ e) (g ∘ e) (𝓝 (e.symm b)) :=
⟨λ h, h.comp_tendsto $
  by { convert e.continuous_at (e.map_target hb), exact (e.right_inv hb).symm },
  λ h, (h.comp_tendsto (e.continuous_at_symm hb)).congr' rfl
    ((e.eventually_right_inverse hb).mono $ λ x hx, congr_arg f hx)
    ((e.eventually_right_inverse hb).mono $ λ x hx, congr_arg g hx)⟩

/-- Transfer `is_O` over a `local_homeomorph`. -/
lemma is_O_congr (e : local_homeomorph α β) {b : β} (hb : b ∈ e.target) {f : β → E} {g : β → F} :
  is_O f g (𝓝 b) ↔ is_O (f ∘ e) (g ∘ e) (𝓝 (e.symm b)) :=
exists_congr $ λ C, e.is_O_with_congr hb

/-- Transfer `is_o` over a `local_homeomorph`. -/
lemma is_o_congr (e : local_homeomorph α β) {b : β} (hb : b ∈ e.target) {f : β → E} {g : β → F} :
  is_o f g (𝓝 b) ↔ is_o (f ∘ e) (g ∘ e) (𝓝 (e.symm b)) :=
forall_congr $ λ c, forall_congr $ λ hc, e.is_O_with_congr hb

end local_homeomorph

namespace homeomorph

variables {α : Type*} {β : Type*} [topological_space α] [topological_space β]

variables {E : Type*} [has_norm E] {F : Type*} [has_norm F]

open asymptotics

/-- Transfer `is_O_with` over a `homeomorph`. -/
lemma is_O_with_congr (e : α ≃ₜ β) {b : β} {f : β → E} {g : β → F} {C : ℝ} :
  is_O_with C f g (𝓝 b) ↔ is_O_with C (f ∘ e) (g ∘ e) (𝓝 (e.symm b)) :=
e.to_local_homeomorph.is_O_with_congr trivial

/-- Transfer `is_O` over a `homeomorph`. -/
lemma is_O_congr (e : α ≃ₜ β) {b : β} {f : β → E} {g : β → F} :
  is_O f g (𝓝 b) ↔ is_O (f ∘ e) (g ∘ e) (𝓝 (e.symm b)) :=
exists_congr $ λ C, e.is_O_with_congr

/-- Transfer `is_o` over a `homeomorph`. -/
lemma is_o_congr (e : α ≃ₜ β) {b : β} {f : β → E} {g : β → F} :
  is_o f g (𝓝 b) ↔ is_o (f ∘ e) (g ∘ e) (𝓝 (e.symm b)) :=
forall_congr $ λ c, forall_congr $ λ hc, e.is_O_with_congr

end homeomorph

attribute [irreducible] asymptotics.is_o asymptotics.is_O asymptotics.is_O_with
