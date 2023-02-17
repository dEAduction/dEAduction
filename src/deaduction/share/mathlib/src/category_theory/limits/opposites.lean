/-
Copyright (c) 2019 Scott Morrison. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Scott Morrison, Floris van Doorn
-/
import category_theory.limits.limits
import category_theory.discrete_category

universes v u

open category_theory
open category_theory.functor
open opposite

namespace category_theory.limits

variables {C : Type u} [category.{v} C]
variables {J : Type v} [small_category J]
variable (F : J ⥤ Cᵒᵖ)

instance has_limit_of_has_colimit_left_op [has_colimit.{v} F.left_op] : has_limit.{v} F :=
{ cone := cone_of_cocone_left_op (colimit.cocone F.left_op),
  is_limit :=
  { lift := λ s, (colimit.desc F.left_op (cocone_left_op_of_cone s)).op,
    fac' := λ s j,
    begin
      rw [cone_of_cocone_left_op_π_app, colimit.cocone_ι, ←op_comp,
          colimit.ι_desc, cocone_left_op_of_cone_ι_app, has_hom.hom.op_unop],
      refl, end,
    uniq' := λ s m w,
    begin
      -- It's a pity we can't do this automatically.
      -- Usually something like this would work by limit.hom_ext,
      -- but the opposites get in the way of this firing.
      have u := (colimit.is_colimit F.left_op).uniq (cocone_left_op_of_cone s) (m.unop),
      convert congr_arg (λ f : _ ⟶ _, f.op) (u _), clear u,
      intro j,
      rw [cocone_left_op_of_cone_ι_app, colimit.cocone_ι],
      convert congr_arg (λ f : _ ⟶ _, f.unop) (w (unop j)), clear w,
      rw [cone_of_cocone_left_op_π_app, colimit.cocone_ι, has_hom.hom.unop_op],
      refl,
    end } }

instance has_limits_of_shape_op_of_has_colimits_of_shape [has_colimits_of_shape.{v} Jᵒᵖ C] :
  has_limits_of_shape.{v} J Cᵒᵖ :=
{ has_limit := λ F, by apply_instance }

instance has_limits_op_of_has_colimits [has_colimits.{v} C] : has_limits.{v} Cᵒᵖ :=
{ has_limits_of_shape := λ J 𝒥, by { resetI, apply_instance } }

instance has_colimit_of_has_limit_left_op [has_limit.{v} F.left_op] : has_colimit.{v} F :=
{ cocone := cocone_of_cone_left_op (limit.cone F.left_op),
  is_colimit :=
  { desc := λ s, (limit.lift F.left_op (cone_left_op_of_cocone s)).op,
    fac' := λ s j,
    begin
      rw [cocone_of_cone_left_op_ι_app, limit.cone_π, ←op_comp,
          limit.lift_π, cone_left_op_of_cocone_π_app, has_hom.hom.op_unop],
      refl, end,
    uniq' := λ s m w,
    begin
      have u := (limit.is_limit F.left_op).uniq (cone_left_op_of_cocone s) (m.unop),
      convert congr_arg (λ f : _ ⟶ _, f.op) (u _), clear u,
      intro j,
      rw [cone_left_op_of_cocone_π_app, limit.cone_π],
      convert congr_arg (λ f : _ ⟶ _, f.unop) (w (unop j)), clear w,
      rw [cocone_of_cone_left_op_ι_app, limit.cone_π, has_hom.hom.unop_op],
      refl,
    end } }

instance has_colimits_of_shape_op_of_has_limits_of_shape [has_limits_of_shape.{v} Jᵒᵖ C] :
  has_colimits_of_shape.{v} J Cᵒᵖ :=
{ has_colimit := λ F, by apply_instance }

instance has_colimits_op_of_has_limits [has_limits.{v} C] : has_colimits.{v} Cᵒᵖ :=
{ has_colimits_of_shape := λ J 𝒥, by { resetI, apply_instance } }

variables (X : Type v)
instance has_coproducts_opposite [has_limits_of_shape (discrete X) C] :
  has_colimits_of_shape (discrete X) Cᵒᵖ :=
begin
  haveI : has_limits_of_shape (discrete X)ᵒᵖ C :=
    has_limits_of_shape_of_equivalence (discrete.opposite X).symm, apply_instance
end

instance has_products_opposite [has_colimits_of_shape (discrete X) C] :
  has_limits_of_shape (discrete X) Cᵒᵖ :=
begin
  haveI : has_colimits_of_shape (discrete X)ᵒᵖ C :=
    has_colimits_of_shape_of_equivalence (discrete.opposite X).symm, apply_instance
end


end category_theory.limits
