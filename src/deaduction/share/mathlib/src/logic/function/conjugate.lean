/-
Copyright (c) 2020 Yury Kudryashov. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Yury Kudryashov
-/
import logic.function.basic

/-!
# Semiconjugate and commuting maps

We define the following predicates:

* `function.semiconj`: `f : α → β` semiconjugates `ga : α → α` to `gb : β → β` if `f ∘ ga = gb ∘ f`;
* `function.semiconj₂: `f : α → β` semiconjugates a binary operation `ga : α → α → α`
  to `gb : β → β → β` if `f (ga x y) = gb (f x) (f y)`;
* `f : α → α` commutes with `g : α → α` if `f ∘ g = g ∘ f`, or equivalently `semiconj f g g`.

-/

namespace function

variables {α : Type*} {β : Type*} {γ : Type*}

/-- We say that `f : α → β` semiconjugates `ga : α → α` to `gb : β → β` if `f ∘ ga = gb ∘ f`. -/
def semiconj (f : α → β) (ga : α → α) (gb : β → β) : Prop := ∀ x, f (ga x) = gb (f x)

namespace semiconj

variables {f fab : α → β} {fbc : β → γ} {ga ga' : α → α} {gb gb' : β → β} {gc gc' : γ → γ}

protected lemma comp_eq (h : semiconj f ga gb) : f ∘ ga = gb ∘ f := funext h

protected lemma eq (h : semiconj f ga gb) (x : α) : f (ga x) = gb (f x) := h x

lemma comp_right (h : semiconj f ga gb) (h' : semiconj f ga' gb') :
  semiconj f (ga ∘ ga') (gb ∘ gb') :=
λ x, by rw [comp_app, h.eq, h'.eq]

lemma comp_left (hab : semiconj fab ga gb) (hbc : semiconj fbc gb gc) :
  semiconj (fbc ∘ fab) ga gc :=
λ x, by simp only [comp_app, hab.eq, hbc.eq]

lemma id_right : semiconj f id id := λ _, rfl

lemma id_left : semiconj id ga ga := λ _, rfl

lemma inverses_right (h : semiconj f ga gb) (ha : right_inverse ga' ga)
  (hb : left_inverse gb' gb) :
  semiconj f ga' gb' :=
λ x, by rw [← hb (f (ga' x)), ← h.eq, ha x]

end semiconj

/-- Two maps `f g : α → α` commute if `f ∘ g = g ∘ f`. -/
def commute (f g : α → α) : Prop := semiconj f g g

lemma semiconj.commute {f g : α → α} (h : semiconj f g g) : commute f g := h

namespace commute

variables {f f' g g' : α → α}

@[refl] lemma refl (f : α → α) : commute f f := λ _, eq.refl _

@[symm] lemma symm (h : commute f g) : commute g f := λ x, (h x).symm

lemma comp_right (h : commute f g) (h' : commute f g') : commute f (g ∘ g') :=
h.comp_right h'

lemma comp_left (h : commute f g) (h' : commute f' g) : commute (f ∘ f') g :=
(h.symm.comp_right h'.symm).symm

lemma id_right : commute f id := semiconj.id_right

lemma id_left : commute id f := semiconj.id_left

end commute

/-- A map `f` semiconjugates a binary operation `ga` to a binary operation `gb` if
for all `x`, `y` we have `f (ga x y) = gb (f x) (f y)`. E.g., a `monoid_hom`
semiconjugates `(*)` to `(*)`. -/
def semiconj₂ (f : α → β) (ga : α → α → α) (gb : β → β → β) : Prop :=
∀ x y, f (ga x y) = gb (f x) (f y)

namespace semiconj₂

variables {f : α → β} {ga : α → α → α} {gb : β → β → β}

protected lemma eq (h : semiconj₂ f ga gb) (x y : α) : f (ga x y) = gb (f x) (f y) := h x y

protected lemma comp_eq (h : semiconj₂ f ga gb) :
  bicompr f ga = bicompl gb f f :=
funext $ λ x, funext $ h x

lemma id_left (op : α → α → α) : semiconj₂ id op op := λ _ _, rfl

lemma comp {f' : β → γ} {gc : γ → γ → γ} (hf' : semiconj₂ f' gb gc) (hf : semiconj₂ f ga gb) :
  semiconj₂ (f' ∘ f) ga gc :=
λ x y, by simp only [hf'.eq, hf.eq, comp_app]

end semiconj₂

end function
