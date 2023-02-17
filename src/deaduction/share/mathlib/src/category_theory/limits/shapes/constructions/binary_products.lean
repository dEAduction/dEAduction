/-
Copyright (c) 2020 Bhavik Mehta. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Bhavik Mehta
-/
import category_theory.limits.shapes.pullbacks
import category_theory.limits.shapes.binary_products

universes v u

/-!
# Constructing binary product from pullbacks and terminal object.

If a category has pullbacks and a terminal object, then it has binary products.

TODO: provide the dual result.
-/

open category_theory category_theory.category category_theory.limits

/-- Any category with pullbacks and terminal object has binary products. -/
-- This is not an instance, as it is not always how one wants to construct binary products!
def has_binary_products_of_terminal_and_pullbacks
  (C : Type u) [𝒞 : category.{v} C] [has_terminal.{v} C] [has_pullbacks.{v} C] :
  has_binary_products.{v} C :=
{ has_limits_of_shape :=
  { has_limit := λ F,
    { cone :=
      { X := pullback (terminal.from (F.obj walking_pair.left))
                      (terminal.from (F.obj walking_pair.right)),
        π := discrete.nat_trans (λ x, walking_pair.cases_on x pullback.fst pullback.snd)},
      is_limit :=
      { lift := λ c, pullback.lift ((c.π).app walking_pair.left)
                                   ((c.π).app walking_pair.right)
                                   (subsingleton.elim _ _),
        fac' := λ s c, walking_pair.cases_on c (limit.lift_π _ _) (limit.lift_π _ _),
        uniq' := λ s m J,
                 begin
                   rw [←J, ←J],
                   ext;
                   rw limit.lift_π;
                   refl
                 end } } } }
