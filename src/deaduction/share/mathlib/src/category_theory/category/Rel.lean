/-
Copyright (c) 2019 Scott Morrison. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Scott Morrison
-/
import category_theory.category

/-!
The category of types with binary relations as morphisms.
-/

namespace category_theory

universe u

/-- A type synonym for `Type`, which carries the category instance for which
    morphisms are binary relations. -/
def Rel := Type u

instance Rel.inhabited : inhabited Rel := by unfold Rel; apply_instance

/-- The category of types with binary relations as morphisms. -/
-- We must work in `Type u` rather than `Sort u`, because
-- `X → Y → Prop` is in `Sort (max u 1)`.
instance rel : large_category Rel.{u} :=
{ hom  := λ X Y, X → Y → Prop,
  id   := λ X, λ x y, x = y,
  comp := λ X Y Z f g x z, ∃ y, f x y ∧ g y z }

end category_theory
