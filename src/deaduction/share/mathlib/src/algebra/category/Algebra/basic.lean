/-
Copyright (c) 2020 Scott Morrison. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Scott Morrison
-/
import algebra.category.CommRing.basic
import algebra.category.Module.basic
import ring_theory.algebra

open category_theory
open category_theory.limits

universe u

variables (R : Type u) [comm_ring R]

/-- The category of R-modules and their morphisms. -/
structure Algebra :=
(carrier : Type u)
[is_ring : ring carrier]
[is_algebra : algebra R carrier]

attribute [instance] Algebra.is_ring Algebra.is_algebra

namespace Algebra

instance : has_coe_to_sort (Algebra R) :=
{ S := Type u, coe := Algebra.carrier }

instance : category (Algebra.{u} R) :=
{ hom   := λ A B, A →ₐ[R] B,
  id    := λ A, alg_hom.id R A,
  comp  := λ A B C f g, g.comp f }

instance : concrete_category (Algebra.{u} R) :=
{ forget := { obj := λ R, R, map := λ R S f, (f : R → S) },
  forget_faithful := { } }

instance has_forget_to_Ring : has_forget₂ (Algebra R) Ring :=
{ forget₂ :=
  { obj := λ A, Ring.of A,
    map := λ A₁ A₂ f, alg_hom.to_ring_hom f, } }

instance has_forget_to_Module : has_forget₂ (Algebra R) (Module R) :=
{ forget₂ :=
  { obj := λ M, Module.of R M,
    map := λ M₁ M₂ f, alg_hom.to_linear_map f, } }

/-- The object in the category of R-algebras associated to a type equipped with the appropriate typeclasses. -/
def of (X : Type u) [ring X] [algebra R X] : Algebra R := ⟨X⟩

instance : inhabited (Algebra R) := ⟨of R R⟩

@[simp]
lemma of_apply (X : Type u) [ring X] [algebra R X] :
  (of R X : Type u) = X := rfl

variables {R}

/-- Forgetting to the underlying type and then building the bundled object returns the original algebra. -/
@[simps]
def of_self_iso (M : Algebra R) : Algebra.of R M ≅ M :=
{ hom := 𝟙 M, inv := 𝟙 M }

variables {R} {M N U : Module R}

@[simp] lemma id_apply (m : M) : (𝟙 M : M → M) m = m := rfl

@[simp] lemma coe_comp (f : M ⟶ N) (g : N ⟶ U) :
  ((f ≫ g) : M → U) = g ∘ f := rfl

end Algebra

variables {R}
variables {X₁ X₂ : Type u}

/-- Build an isomorphism in the category `Algebra R` from a `alg_equiv` between `algebra`s. -/
@[simps]
def alg_equiv.to_Algebra_iso
  {g₁ : ring X₁} {g₂ : ring X₂} {m₁ : algebra R X₁} {m₂ : algebra R X₂} (e : X₁ ≃ₐ[R] X₂) :
  Algebra.of R X₁ ≅ Algebra.of R X₂ :=
{ hom := (e : X₁ →ₐ[R] X₂),
  inv := (e.symm : X₂ →ₐ[R] X₁),
  hom_inv_id' := begin ext, exact e.left_inv x, end,
  inv_hom_id' := begin ext, exact e.right_inv x, end, }

namespace category_theory.iso

/-- Build a `alg_equiv` from an isomorphism in the category `Algebra R`. -/
@[simps]
def to_alg_equiv {X Y : Algebra.{u} R} (i : X ≅ Y) : X ≃ₐ[R] Y :=
{ to_fun    := i.hom,
  inv_fun   := i.inv,
  left_inv  := by tidy,
  right_inv := by tidy,
  map_add'  := by tidy,
  map_mul'  := by tidy,
  commutes' := by tidy, }.

end category_theory.iso

/-- algebra equivalences between `algebras`s are the same as (isomorphic to) isomorphisms in `Algebra` -/
@[simps]
def alg_equiv_iso_Algebra_iso {X Y : Type u}
  [ring X] [ring Y] [algebra R X] [algebra R Y] :
  (X ≃ₐ[R] Y) ≅ (Algebra.of R X ≅ Algebra.of R Y) :=
{ hom := λ e, e.to_Algebra_iso,
  inv := λ i, i.to_alg_equiv, }

instance (X : Type u) [ring X] [algebra R X] : has_coe (subalgebra R X) (Algebra R) :=
⟨ λ N, Algebra.of R N ⟩
