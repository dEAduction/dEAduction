/-
Copyright (c) 2020 David Wärn. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: David Wärn
-/
import category_theory.natural_isomorphism

/-!
# Quotient category

Constructs the quotient of a category by an arbitrary family of relations on its hom-sets,
by introducing a type synonym for the objects, and identifying homs as necessary.

This is analogous to 'the quotient of a group by the normal closure of a subset', rather
than 'the quotient of a group by a normal subgroup'.
-/

universes v v₁ u u₁

namespace category_theory

variables {C : Type u} [category.{v} C]
          (r : Π ⦃a b : C⦄, (a ⟶ b) → (a ⟶ b) → Prop)
include r

/-- A type synonom for `C`, thought of as the objects of the quotient category. -/
structure quotient := (as : C)

instance [inhabited C] : inhabited (quotient r) := ⟨ { as := default C } ⟩

namespace quotient

/-- Generates the closure of a family of relations w.r.t. composition from left and right. -/
inductive comp_closure ⦃s t : C⦄ : (s ⟶ t) → (s ⟶ t) → Prop
| intro {a b} (f : s ⟶ a) (m₁ m₂ : a ⟶ b) (g : b ⟶ t) (h : r m₁ m₂) :
  comp_closure (f ≫ m₁ ≫ g) (f ≫ m₂ ≫ g)

lemma comp_left {a b c : C} (f : a ⟶ b) : Π (g₁ g₂ : b ⟶ c) (h : comp_closure r g₁ g₂),
  comp_closure r (f ≫ g₁) (f ≫ g₂)
| _ _ ⟨x, m₁, m₂, y, h⟩ := by simpa using comp_closure.intro (f ≫ x) m₁ m₂ y h

lemma comp_right {a b c : C} (g : b ⟶ c) : Π (f₁ f₂ : a ⟶ b) (h : comp_closure r f₁ f₂),
  comp_closure r (f₁ ≫ g) (f₂ ≫ g)
| _ _ ⟨x, m₁, m₂, y, h⟩ := by simpa using comp_closure.intro x m₁ m₂ (y ≫ g) h

/-- Hom-sets of the quotient category. -/
def hom (s t : quotient r) := quot $ @comp_closure C _ r s.as t.as

instance (a : quotient r) : inhabited (hom r a a) := ⟨quot.mk _ (𝟙 a.as)⟩

/-- Composition in the quotient category. -/
def comp ⦃a b c : quotient r⦄ : hom r a b → hom r b c → hom r a c :=
λ hf hg, quot.lift_on hf ( λ f, quot.lift_on hg (λ g, quot.mk _ (f ≫ g))
  (λ g₁ g₂ h, quot.sound $ comp_left r f g₁ g₂ h) )
  (λ f₁ f₂ h, quot.induction_on hg $ λ g, quot.sound $ comp_right r g f₁ f₂ h)

@[simp]
lemma comp_mk {a b c : quotient r} (f : a.as ⟶ b.as) (g : b.as ⟶ c.as) :
  comp r (quot.mk _ f) (quot.mk _ g) = quot.mk _ (f ≫ g) := rfl

instance category : category (quotient r) :=
{ hom := hom r,
  id := λ a, quot.mk _ (𝟙 a.as),
  comp := comp r }

/-- The functor from a category to its quotient. -/
@[simps]
def functor : C ⥤ quotient r :=
{ obj := λ a, { as := a },
  map := λ _ _ f, quot.mk _ f }

protected lemma induction {P : Π {a b : quotient r}, (a ⟶ b) → Prop}
  (h : ∀ {x y : C} (f : x ⟶ y), P ((functor r).map f)) :
  ∀ {a b : quotient r} (f : a ⟶ b), P f :=
by { rintros ⟨x⟩ ⟨y⟩ ⟨f⟩, exact h f, }

protected lemma sound {a b : C} {f₁ f₂ : a ⟶ b} (h : r f₁ f₂) :
  (functor r).map f₁ = (functor r).map f₂ :=
by simpa using quot.sound (comp_closure.intro (𝟙 a) f₁ f₂ (𝟙 b) h)

variables {D : Type*} [category D]
  (F : C ⥤ D)
  (H : ∀ (x y : C) (f₁ f₂ : x ⟶ y), r f₁ f₂ → F.map f₁ = F.map f₂)
include H

/-- The induced functor on the quotient category. -/
@[simps]
def lift : quotient r ⥤ D :=
{ obj := λ a, F.obj a.as,
  map := λ a b hf, quot.lift_on hf (λ f, F.map f)
    (by { rintros _ _ ⟨_, _, _, _, _, _, h⟩, simp [H _ _ _ _ h], }),
  map_id' := λ a, F.map_id a.as,
  map_comp' := by { rintros a b c ⟨f⟩ ⟨g⟩, exact F.map_comp f g, } }

/-- The original functor factors through the induced functor. -/
def lift.is_lift : (functor r) ⋙ lift r F H ≅ F :=
nat_iso.of_components (λ X, iso.refl _) (by tidy)

@[simp]
lemma lift.is_lift_hom (X : C) : (lift.is_lift r F H).hom.app X = 𝟙 (F.obj X) :=
rfl
@[simp]
lemma lift.is_lift_inv (X : C) : (lift.is_lift r F H).inv.app X = 𝟙 (F.obj X) :=
rfl

end quotient

end category_theory
