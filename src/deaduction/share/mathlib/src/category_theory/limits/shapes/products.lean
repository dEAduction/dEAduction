/-
Copyright (c) 2018 Scott Morrison. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Scott Morrison
-/
import category_theory.limits.limits
import category_theory.discrete_category

universes v u

open category_theory

namespace category_theory.limits

variables {β : Type v}
variables {C : Type u} [category.{v} C]

-- We don't need an analogue of `pair` (for binary products), `parallel_pair` (for equalizers),
-- or `(co)span`, since we already have `discrete.functor`.

abbreviation fan (f : β → C) := cone (discrete.functor f)
abbreviation cofan (f : β → C) := cocone (discrete.functor f)

def fan.mk {f : β → C} {P : C} (p : Π b, P ⟶ f b) : fan f :=
{ X := P,
  π := { app := p } }

def cofan.mk {f : β → C} {P : C} (p : Π b, f b ⟶ P) : cofan f :=
{ X := P,
  ι := { app := p } }

@[simp] lemma fan.mk_π_app {f : β → C} {P : C} (p : Π b, P ⟶ f b) (b : β) : (fan.mk p).π.app b = p b := rfl
@[simp] lemma cofan.mk_π_app {f : β → C} {P : C} (p : Π b, f b ⟶ P) (b : β) : (cofan.mk p).ι.app b = p b := rfl

/-- `pi_obj f` computes the product of a family of elements `f`. (It is defined as an abbreviation
   for `limit (discrete.functor f)`, so for most facts about `pi_obj f`, you will just use general facts
   about limits.) -/
abbreviation pi_obj (f : β → C) [has_limit (discrete.functor f)] := limit (discrete.functor f)
/-- `sigma_obj f` computes the coproduct of a family of elements `f`. (It is defined as an abbreviation
   for `colimit (discrete.functor f)`, so for most facts about `sigma_obj f`, you will just use general facts
   about colimits.) -/
abbreviation sigma_obj (f : β → C) [has_colimit (discrete.functor f)] := colimit (discrete.functor f)

notation `∏ ` f:20 := pi_obj f
notation `∐ ` f:20 := sigma_obj f

abbreviation pi.π (f : β → C) [has_limit (discrete.functor f)] (b : β) : ∏ f ⟶ f b :=
limit.π (discrete.functor f) b
abbreviation sigma.ι (f : β → C) [has_colimit (discrete.functor f)] (b : β) : f b ⟶ ∐ f :=
colimit.ι (discrete.functor f) b

abbreviation pi.lift {f : β → C} [has_limit (discrete.functor f)] {P : C} (p : Π b, P ⟶ f b) : P ⟶ ∏ f :=
limit.lift _ (fan.mk p)
abbreviation sigma.desc {f : β → C} [has_colimit (discrete.functor f)] {P : C} (p : Π b, f b ⟶ P) : ∐ f ⟶ P :=
colimit.desc _ (cofan.mk p)

abbreviation pi.map {f g : β → C} [has_limits_of_shape.{v} (discrete β) C]
  (p : Π b, f b ⟶ g b) : ∏ f ⟶ ∏ g :=
lim.map (discrete.nat_trans p)
abbreviation sigma.map {f g : β → C} [has_colimits_of_shape.{v} (discrete β) C]
  (p : Π b, f b ⟶ g b) : ∐ f ⟶ ∐ g :=
colim.map (discrete.nat_trans p)

variables (C)

class has_products :=
(has_limits_of_shape : Π (J : Type v), has_limits_of_shape.{v} (discrete J) C)
class has_coproducts :=
(has_colimits_of_shape : Π (J : Type v), has_colimits_of_shape.{v} (discrete J) C)

attribute [instance] has_products.has_limits_of_shape has_coproducts.has_colimits_of_shape

end category_theory.limits
