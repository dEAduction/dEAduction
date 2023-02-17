/-
Copyright (c) 2020 Bhavik Mehta. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Bhavik Mehta
-/
import category_theory.reflect_isomorphisms

open category_theory category_theory.limits

namespace category_theory

universes v u₁ u₂ u₃

variables {C : Type u₁} [category.{v} C]

section creates
variables {D : Type u₂} [category.{v} D]

variables {J : Type v} [small_category J] {K : J ⥤ C}

/--
Define the lift of a cone: For a cone `c` for `K ⋙ F`, give a cone for `K`
which is a lift of `c`, i.e. the image of it under `F` is (iso) to `c`.

We will then use this as part of the definition of creation of limits:
every limit cone has a lift.

Note this definition is really only useful when `c` is a limit already.
-/
structure liftable_cone (K : J ⥤ C) (F : C ⥤ D) (c : cone (K ⋙ F)) :=
(lifted_cone : cone K)
(valid_lift : F.map_cone lifted_cone ≅ c)

/--
Define the lift of a cocone: For a cocone `c` for `K ⋙ F`, give a cocone for
`K` which is a lift of `c`, i.e. the image of it under `F` is (iso) to `c`.

We will then use this as part of the definition of creation of colimits:
every limit cocone has a lift.

Note this definition is really only useful when `c` is a colimit already.
-/
structure liftable_cocone (K : J ⥤ C) (F : C ⥤ D) (c : cocone (K ⋙ F)) :=
(lifted_cocone : cocone K)
(valid_lift : F.map_cocone lifted_cocone ≅ c)

set_option default_priority 100

/--
Definition 3.3.1 of [Riehl].
We say that `F` creates limits of `K` if, given any limit cone `c` for `K ⋙ F`
(i.e. below) we can lift it to a cone "above", and further that `F` reflects
limits for `K`.

If `F` reflects isomorphisms, it suffices to show only that the lifted cone is
a limit - see `creates_limit_of_reflects_iso`.
-/
class creates_limit (K : J ⥤ C) (F : C ⥤ D) extends reflects_limit K F :=
(lifts : Π c, is_limit c → liftable_cone K F c)

/--
`F` creates limits of shape `J` if `F` creates the limit of any diagram
`K : J ⥤ C`.
-/
class creates_limits_of_shape (J : Type v) [small_category J] (F : C ⥤ D) :=
(creates_limit : Π {K : J ⥤ C}, creates_limit K F)

/-- `F` creates limits if it creates limits of shape `J` for any small `J`. -/
class creates_limits (F : C ⥤ D) :=
(creates_limits_of_shape : Π {J : Type v} {𝒥 : small_category J},
  by exactI creates_limits_of_shape J F)

/--
Dual of definition 3.3.1 of [Riehl].
We say that `F` creates colimits of `K` if, given any limit cocone `c` for
`K ⋙ F` (i.e. below) we can lift it to a cocone "above", and further that `F`
reflects limits for `K`.

If `F` reflects isomorphisms, it suffices to show only that the lifted cocone is
a limit - see `creates_limit_of_reflects_iso`.
-/
class creates_colimit (K : J ⥤ C) (F : C ⥤ D) extends reflects_colimit K F :=
(lifts : Π c, is_colimit c → liftable_cocone K F c)

/--
`F` creates colimits of shape `J` if `F` creates the colimit of any diagram
`K : J ⥤ C`.
-/
class creates_colimits_of_shape (J : Type v) [small_category J] (F : C ⥤ D) :=
(creates_colimit : Π {K : J ⥤ C}, creates_colimit K F)

/-- `F` creates colimits if it creates colimits of shape `J` for any small `J`. -/
class creates_colimits (F : C ⥤ D) :=
(creates_colimits_of_shape : Π {J : Type v} {𝒥 : small_category J},
  by exactI creates_colimits_of_shape J F)

attribute [instance, priority 100] -- see Note [lower instance priority]
  creates_limits_of_shape.creates_limit creates_limits.creates_limits_of_shape
  creates_colimits_of_shape.creates_colimit creates_colimits.creates_colimits_of_shape

/- Interface to the `creates_limit` class. -/

/-- `lift_limit t` is the cone for `K` given by lifting the limit `t` for `K ⋙ F`. -/
def lift_limit {K : J ⥤ C} {F : C ⥤ D} [creates_limit K F] {c : cone (K ⋙ F)} (t : is_limit c) :
  cone K :=
(creates_limit.lifts c t).lifted_cone

/-- The lifted cone has an image isomorphic to the original cone. -/
def lifted_limit_maps_to_original {K : J ⥤ C} {F : C ⥤ D}
  [creates_limit K F] {c : cone (K ⋙ F)} (t : is_limit c) :
  F.map_cone (lift_limit t) ≅ c :=
(creates_limit.lifts c t).valid_lift

/-- The lifted cone is a limit. -/
def lifted_limit_is_limit {K : J ⥤ C} {F : C ⥤ D}
  [creates_limit K F] {c : cone (K ⋙ F)} (t : is_limit c) :
  is_limit (lift_limit t) :=
reflects_limit.reflects (is_limit.of_iso_limit t (lifted_limit_maps_to_original t).symm)

/-- If `F` creates the limit of `K` and `K ⋙ F` has a limit, then `K` has a limit. -/
def has_limit_of_created (K : J ⥤ C) (F : C ⥤ D)
  [has_limit (K ⋙ F)] [creates_limit K F] : has_limit K :=
{ cone := lift_limit (limit.is_limit (K ⋙ F)),
  is_limit := lifted_limit_is_limit _ }

/- Interface to the `creates_colimit` class. -/

/-- `lift_colimit t` is the cocone for `K` given by lifting the colimit `t` for `K ⋙ F`. -/
def lift_colimit {K : J ⥤ C} {F : C ⥤ D} [creates_colimit K F] {c : cocone (K ⋙ F)} (t : is_colimit c) :
  cocone K :=
(creates_colimit.lifts c t).lifted_cocone

/-- The lifted cocone has an image isomorphic to the original cocone. -/
def lifted_colimit_maps_to_original {K : J ⥤ C} {F : C ⥤ D}
  [creates_colimit K F] {c : cocone (K ⋙ F)} (t : is_colimit c) :
  F.map_cocone (lift_colimit t) ≅ c :=
(creates_colimit.lifts c t).valid_lift

/-- The lifted cocone is a colimit. -/
def lifted_colimit_is_colimit {K : J ⥤ C} {F : C ⥤ D}
  [creates_colimit K F] {c : cocone (K ⋙ F)} (t : is_colimit c) :
  is_colimit (lift_colimit t) :=
reflects_colimit.reflects (is_colimit.of_iso_colimit t (lifted_colimit_maps_to_original t).symm)

/-- If `F` creates the limit of `K` and `K ⋙ F` has a limit, then `K` has a limit. -/
def has_colimit_of_created (K : J ⥤ C) (F : C ⥤ D)
  [has_colimit (K ⋙ F)] [creates_colimit K F] : has_colimit K :=
{ cocone := lift_colimit (colimit.is_colimit (K ⋙ F)),
  is_colimit := lifted_colimit_is_colimit _ }

/--
A helper to show a functor creates limits. In particular, if we can show
that for any limit cone `c` for `K ⋙ F`, there is a lift of it which is
a limit and `F` reflects isomorphisms, then `F` creates limits.
Usually, `F` creating limits says that _any_ lift of `c` is a limit, but
here we only need to show that our particular lift of `c` is a limit.
-/
structure lifts_to_limit (K : J ⥤ C) (F : C ⥤ D) (c : cone (K ⋙ F)) (t : is_limit c)
  extends liftable_cone K F c :=
(makes_limit : is_limit lifted_cone)

/--
A helper to show a functor creates colimits. In particular, if we can show
that for any limit cocone `c` for `K ⋙ F`, there is a lift of it which is
a limit and `F` reflects isomorphisms, then `F` creates colimits.
Usually, `F` creating colimits says that _any_ lift of `c` is a colimit, but
here we only need to show that our particular lift of `c` is a colimit.
-/
structure lifts_to_colimit (K : J ⥤ C) (F : C ⥤ D) (c : cocone (K ⋙ F)) (t : is_colimit c)
  extends liftable_cocone K F c :=
(makes_colimit : is_colimit lifted_cocone)

/--
If `F` reflects isomorphisms and we can lift any limit cone to a limit cone,
then `F` creates limits.
In particular here we don't need to assume that F reflects limits.
-/
def creates_limit_of_reflects_iso {K : J ⥤ C} {F : C ⥤ D} [reflects_isomorphisms F]
  (h : Π c t, lifts_to_limit K F c t) :
  creates_limit K F :=
{ lifts := λ c t, (h c t).to_liftable_cone,
  to_reflects_limit :=
  { reflects := λ (d : cone K) (hd : is_limit (F.map_cone d)),
    begin
      let d' : cone K := (h (F.map_cone d) hd).to_liftable_cone.lifted_cone,
      let i : F.map_cone d' ≅ F.map_cone d := (h (F.map_cone d) hd).to_liftable_cone.valid_lift,
      let hd' : is_limit d' := (h (F.map_cone d) hd).makes_limit,
      let f : d ⟶ d' := hd'.lift_cone_morphism d,
      have : (cones.functoriality K F).map f = i.inv := (hd.of_iso_limit i.symm).uniq_cone_morphism,
      haveI : is_iso ((cones.functoriality K F).map f) := (by { rw this, apply_instance }),
      haveI : is_iso f := is_iso_of_reflects_iso f (cones.functoriality K F),
      exact is_limit.of_iso_limit hd' (as_iso f).symm,
    end } }

/-- `F` preserves the limit of `K` if it creates the limit and `K ⋙ F` has the limit. -/
instance preserves_limit_of_creates_limit_and_has_limit (K : J ⥤ C) (F : C ⥤ D)
  [creates_limit K F] [has_limit (K ⋙ F)] :
preserves_limit K F :=
{ preserves := λ c t, is_limit.of_iso_limit (limit.is_limit _)
    ((lifted_limit_maps_to_original (limit.is_limit _)).symm ≪≫
      ((cones.functoriality K F).map_iso ((lifted_limit_is_limit (limit.is_limit _)).unique_up_to_iso t))) }

/-- `F` preserves the limit of shape `J` if it creates these limits and `D` has them. -/
instance preserves_limit_of_shape_of_creates_limits_of_shape_and_has_limits_of_shape (F : C ⥤ D)
  [creates_limits_of_shape J F] [has_limits_of_shape J D] :
preserves_limits_of_shape J F :=
{ preserves_limit := λ K, category_theory.preserves_limit_of_creates_limit_and_has_limit K F }

/-- `F` preserves limits if it creates limits and `D` has limits. -/
instance preserves_limits_of_creates_limits_and_has_limits (F : C ⥤ D) [creates_limits F] [has_limits.{v} D] :
  preserves_limits F :=
{ preserves_limits_of_shape := λ J 𝒥,
  by exactI category_theory.preserves_limit_of_shape_of_creates_limits_of_shape_and_has_limits_of_shape F }

/--
If `F` reflects isomorphisms and we can lift any limit cocone to a limit cocone,
then `F` creates colimits.
In particular here we don't need to assume that F reflects colimits.
-/
def creates_colimit_of_reflects_iso {K : J ⥤ C} {F : C ⥤ D} [reflects_isomorphisms F]
  (h : Π c t, lifts_to_colimit K F c t) :
  creates_colimit K F :=
{ lifts := λ c t, (h c t).to_liftable_cocone,
  to_reflects_colimit :=
  { reflects := λ (d : cocone K) (hd : is_colimit (F.map_cocone d)),
    begin
      let d' : cocone K := (h (F.map_cocone d) hd).to_liftable_cocone.lifted_cocone,
      let i : F.map_cocone d' ≅ F.map_cocone d := (h (F.map_cocone d) hd).to_liftable_cocone.valid_lift,
      let hd' : is_colimit d' := (h (F.map_cocone d) hd).makes_colimit,
      let f : d' ⟶ d := hd'.desc_cocone_morphism d,
      have : (cocones.functoriality K F).map f = i.hom := (hd.of_iso_colimit i.symm).uniq_cocone_morphism,
      haveI : is_iso ((cocones.functoriality K F).map f) := (by { rw this, apply_instance }),
      haveI := is_iso_of_reflects_iso f (cocones.functoriality K F),
      exact is_colimit.of_iso_colimit hd' (as_iso f),
    end } }

/-- `F` preserves the colimit of `K` if it creates the colimit and `K ⋙ F` has the colimit. -/
instance preserves_colimit_of_creates_colimit_and_has_colimit (K : J ⥤ C) (F : C ⥤ D)
  [creates_colimit K F] [has_colimit (K ⋙ F)] :
preserves_colimit K F :=
{ preserves := λ c t, is_colimit.of_iso_colimit (colimit.is_colimit _)
    ((lifted_colimit_maps_to_original (colimit.is_colimit _)).symm ≪≫
      ((cocones.functoriality K F).map_iso ((lifted_colimit_is_colimit (colimit.is_colimit _)).unique_up_to_iso t))) }

/-- `F` preserves the colimit of shape `J` if it creates these colimits and `D` has them. -/
instance preserves_colimit_of_shape_of_creates_colimits_of_shape_and_has_colimits_of_shape (F : C ⥤ D)
  [creates_colimits_of_shape J F] [has_colimits_of_shape J D] :
preserves_colimits_of_shape J F :=
{ preserves_colimit := λ K, category_theory.preserves_colimit_of_creates_colimit_and_has_colimit K F }

/-- `F` preserves limits if it creates limits and `D` has limits. -/
instance preserves_colimits_of_creates_colimits_and_has_colimits (F : C ⥤ D) [creates_colimits F] [has_colimits.{v} D] :
  preserves_colimits F :=
{ preserves_colimits_of_shape := λ J 𝒥,
  by exactI category_theory.preserves_colimit_of_shape_of_creates_colimits_of_shape_and_has_colimits_of_shape F }

-- For the inhabited linter later.
/-- If F creates the limit of K, any cone lifts to a limit. -/
def lifts_to_limit_of_creates (K : J ⥤ C) (F : C ⥤ D)
  [creates_limit K F] (c : cone (K ⋙ F)) (t : is_limit c) :
  lifts_to_limit K F c t :=
{ lifted_cone := lift_limit t,
  valid_lift := lifted_limit_maps_to_original t,
  makes_limit := lifted_limit_is_limit t }

-- For the inhabited linter later.
/-- If F creates the colimit of K, any cocone lifts to a colimit. -/
def lifts_to_colimit_of_creates (K : J ⥤ C) (F : C ⥤ D)
  [creates_colimit K F] (c : cocone (K ⋙ F)) (t : is_colimit c) :
  lifts_to_colimit K F c t :=
{ lifted_cocone := lift_colimit t,
  valid_lift := lifted_colimit_maps_to_original t,
  makes_colimit := lifted_colimit_is_colimit t }

/-- Any cone lifts through the identity functor. -/
def id_lifts_cone (c : cone (K ⋙ 𝟭 C)) : liftable_cone K (𝟭 C) c :=
{ lifted_cone :=
  { X := c.X,
    π := c.π ≫ K.right_unitor.hom },
  valid_lift := cones.ext (iso.refl _) (by tidy) }

/-- The identity functor creates all limits. -/
instance id_creates_limits : creates_limits (𝟭 C) :=
{ creates_limits_of_shape := λ J 𝒥, by exactI
  { creates_limit := λ F, { lifts := λ c t, id_lifts_cone c } } }

/-- Any cocone lifts through the identity functor. -/
def id_lifts_cocone (c : cocone (K ⋙ 𝟭 C)) : liftable_cocone K (𝟭 C) c :=
{ lifted_cocone :=
  { X := c.X,
    ι := K.right_unitor.inv ≫ c.ι },
  valid_lift := cocones.ext (iso.refl _) (by tidy) }

/-- The identity functor creates all colimits. -/
instance id_creates_colimits : creates_colimits (𝟭 C) :=
{ creates_colimits_of_shape := λ J 𝒥, by exactI
  { creates_colimit := λ F, { lifts := λ c t, id_lifts_cocone c } } }

/-- Satisfy the inhabited linter -/
instance inhabited_liftable_cone (c : cone (K ⋙ 𝟭 C)) : inhabited (liftable_cone K (𝟭 C) c) :=
⟨id_lifts_cone c⟩
instance inhabited_liftable_cocone (c : cocone (K ⋙ 𝟭 C)) : inhabited (liftable_cocone K (𝟭 C) c) :=
⟨id_lifts_cocone c⟩

/-- Satisfy the inhabited linter -/
instance inhabited_lifts_to_limit (K : J ⥤ C) (F : C ⥤ D)
  [creates_limit K F] (c : cone (K ⋙ F)) (t : is_limit c) :
  inhabited (lifts_to_limit _ _ _ t) :=
⟨lifts_to_limit_of_creates K F c t⟩
instance inhabited_lifts_to_colimit (K : J ⥤ C) (F : C ⥤ D)
  [creates_colimit K F] (c : cocone (K ⋙ F)) (t : is_colimit c) :
  inhabited (lifts_to_colimit _ _ _ t) :=
⟨lifts_to_colimit_of_creates K F c t⟩

section comp

variables {E : Type u₃} [ℰ : category.{v} E]
variables (F : C ⥤ D) (G : D ⥤ E)

instance comp_creates_limit [i₁ : creates_limit K F] [i₂ : creates_limit (K ⋙ F) G] :
  creates_limit K (F ⋙ G) :=
{ lifts := λ c t,
  { lifted_cone := lift_limit (lifted_limit_is_limit t),
    valid_lift := (cones.functoriality (K ⋙ F) G).map_iso
      (lifted_limit_maps_to_original (lifted_limit_is_limit t)) ≪≫
      (lifted_limit_maps_to_original t),
  } }

end comp

end creates

end category_theory
