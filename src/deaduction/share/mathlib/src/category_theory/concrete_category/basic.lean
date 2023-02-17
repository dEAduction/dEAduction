/-
Copyright (c) 2018 Scott Morrison. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Scott Morrison, Johannes Hölzl, Reid Barton, Sean Leather, Yury Kudryashov
-/
import category_theory.types
import category_theory.full_subcategory

/-!
# Concrete categories

A concrete category is a category `C` with a fixed faithful functor
`forget : C ⥤ Type*`.  We define concrete categories using `class
concrete_category`.  In particular, we impose no restrictions on the
carrier type `C`, so `Type` is a concrete category with the identity
forgetful functor.

Each concrete category `C` comes with a canonical faithful functor
`forget C : C ⥤ Type*`.  We say that a concrete category `C` admits a
*forgetful functor* to a concrete category `D`, if it has a functor
`forget₂ C D : C ⥤ D` such that `(forget₂ C D) ⋙ (forget D) = forget
C`, see `class has_forget₂`.  Due to `faithful.div_comp`, it suffices
to verify that `forget₂.obj` and `forget₂.map` agree with the equality
above; then `forget₂` will satisfy the functor laws automatically, see
`has_forget₂.mk'`.

Two classes helping construct concrete categories in the two most
common cases are provided in the files `bundled_hom` and
`unbundled_hom`, see their documentation for details.

## References

See [Ahrens and Lumsdaine, *Displayed Categories*][ahrens2017] for
related work.
-/

universe u

namespace category_theory

section prio
set_option default_priority 100 -- see Note [default priority]
/-- A concrete category is a category `C` with a fixed faithful functor `forget : C ⥤ Type`. -/
class concrete_category (C : Type (u+1)) [large_category C] :=
(forget [] : C ⥤ Type u)
[forget_faithful : faithful forget]
end prio

attribute [instance] concrete_category.forget_faithful

/-- The forgetful functor from a concrete category to `Type u`. -/
@[reducible] def forget (C : Type (u+1)) [large_category C] [concrete_category C] : C ⥤ Type u :=
concrete_category.forget C

/--
Provide a coercion to `Type u` for a concrete category. This is not marked as an instance
as it could potentially apply to every type, and so is too expensive in typeclass search.

You can use it on particular examples as:
```
instance : has_coe_to_sort X := concrete_category.has_coe_to_sort X
```
-/
def concrete_category.has_coe_to_sort (C : Type (u+1)) [large_category C] [concrete_category C] : has_coe_to_sort C :=
{ S := Type u, coe := (concrete_category.forget C).obj }

section
local attribute [instance] concrete_category.has_coe_to_sort

variables {C : Type (u+1)} [large_category C] [concrete_category C]

@[simp] lemma forget_obj_eq_coe {X : C} : (forget C).obj X = X := rfl

/-- Usually a bundled hom structure already has a coercion to function
that works with different universes. So we don't use this as a global instance. -/
def concrete_category.has_coe_to_fun {X Y : C} : has_coe_to_fun (X ⟶ Y) :=
{ F   := λ f, X → Y,
  coe := λ f, (forget _).map f }

local attribute [instance] concrete_category.has_coe_to_fun

/-- In any concrete category, we can test equality of morphisms by pointwise evaluations.-/
lemma concrete_category.hom_ext {X Y : C} (f g : X ⟶ Y) (w : ∀ x : X, f x  = g x) : f = g :=
begin
  apply faithful.map_injective (forget C),
  ext,
  exact w x,
end

@[simp] lemma forget_map_eq_coe {X Y : C} (f : X ⟶ Y) : (forget C).map f = f := rfl

@[simp] lemma coe_id {X : C} (x : X) : ((𝟙 X) : X → X) x = x :=
congr_fun ((forget _).map_id X) x

@[simp] lemma coe_comp {X Y Z : C} (f : X ⟶ Y) (g : Y ⟶ Z) (x : X) :
  (f ≫ g) x = g (f x) :=
congr_fun ((forget _).map_comp _ _) x

@[simp] lemma coe_hom_inv_id {X Y : C} (f : X ≅ Y) (x : X) :
  f.inv (f.hom x) = x :=
congr_fun ((forget C).map_iso f).hom_inv_id x
@[simp] lemma coe_inv_hom_id {X Y : C} (f : X ≅ Y) (y : Y) :
  f.hom (f.inv y) = y :=
congr_fun ((forget C).map_iso f).inv_hom_id y

local attribute [ext] concrete_category.hom_ext

/--
In any concrete category, injective morphisms are monomorphisms,
by extensionality.
-/
lemma concrete_category.mono_of_injective {X Y : C} (f : X ⟶ Y) (i : function.injective f) : mono f :=
⟨λ Z g h w,
  begin
    ext z,
    apply i,
    convert congr_arg (λ k : Z ⟶ Y, (k : Z → Y) z) w; simp only [coe_comp],
  end⟩

end

instance concrete_category.types : concrete_category (Type u) :=
{ forget := 𝟭 _ }

/--
`has_forget₂ C D`, where `C` and `D` are both concrete categories, provides a functor
`forget₂ C D : C ⥤ D` and a proof that `forget₂ ⋙ (forget D) = forget C`.
-/
class has_forget₂ (C D : Type (u+1)) [large_category C] [concrete_category C] [large_category D] [concrete_category D] :=
(forget₂ : C ⥤ D)
(forget_comp : forget₂ ⋙ (forget D) = forget C . obviously)

/-- The forgetful functor `C ⥤ D` between concrete categories for which we have an instance
`has_forget₂ C `. -/
@[reducible] def forget₂ (C D : Type (u+1)) [large_category C] [concrete_category C] [large_category D] [concrete_category D]
  [has_forget₂ C D] : C ⥤ D :=
has_forget₂.forget₂

instance forget_faithful (C D : Type (u+1)) [large_category C] [concrete_category C] [large_category D] [concrete_category D]
  [has_forget₂ C D] : faithful (forget₂ C D) :=
has_forget₂.forget_comp.faithful_of_comp

instance induced_category.concrete_category {C D : Type (u+1)} [large_category D] [concrete_category D] (f : C → D) :
  concrete_category (induced_category D f) :=
{ forget := induced_functor f ⋙ forget D }

instance induced_category.has_forget₂ {C D : Type (u+1)} [large_category D] [concrete_category D] (f : C → D) :
  has_forget₂ (induced_category D f) D :=
{ forget₂ := induced_functor f,
  forget_comp := rfl }

/--
In order to construct a “partially forgetting” functor, we do not need to verify functor laws;
it suffices to ensure that compositions agree with `forget₂ C D ⋙ forget D = forget C`.
-/
def has_forget₂.mk' {C D : Type (u+1)} [large_category C] [concrete_category C] [large_category D] [concrete_category D]
  (obj : C → D) (h_obj : ∀ X, (forget D).obj (obj X) = (forget C).obj X)
  (map : Π {X Y}, (X ⟶ Y) → (obj X ⟶ obj Y))
  (h_map : ∀ {X Y} {f : X ⟶ Y}, (forget D).map (map f) == (forget C).map f) :
has_forget₂ C D :=
{ forget₂ := faithful.div _ _ _ @h_obj _ @h_map,
  forget_comp := by apply faithful.div_comp }

instance has_forget_to_Type (C : Type (u+1)) [large_category C] [concrete_category C] : has_forget₂ C (Type u) :=
{ forget₂ := forget C,
  forget_comp := functor.comp_id _ }

end category_theory
