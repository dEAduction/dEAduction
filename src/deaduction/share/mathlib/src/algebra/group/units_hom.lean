/-
Copyright (c) 2018 Johan Commelin All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Johan Commelin, Chris Hughes, Kevin Buzzard
-/
import algebra.group.units
import algebra.group.hom
/-!
# Lift monoid homomorphisms to group homomorphisms of their units subgroups.
-/

universes u v w

namespace units
variables {M : Type u} {N : Type v} {P : Type w} [monoid M] [monoid N] [monoid P]

/-- The group homomorphism on units induced by a `monoid_hom`. -/
@[to_additive "The `add_group` homomorphism on `add_unit`s induced by an `add_monoid_hom`."]
def map (f : M →* N) : units M →* units N :=
monoid_hom.mk'
  (λ u, ⟨f u.val, f u.inv,
                  by rw [← f.map_mul, u.val_inv, f.map_one],
                  by rw [← f.map_mul, u.inv_val, f.map_one]⟩)
  (λ x y, ext (f.map_mul x y))

@[simp, to_additive] lemma coe_map (f : M →* N) (x : units M) : ↑(map f x) = f x := rfl

@[simp, to_additive]
lemma map_comp (f : M →* N) (g : N →* P) : map (g.comp f) = (map g).comp (map f) := rfl

variables (M)
@[simp, to_additive] lemma map_id : map (monoid_hom.id M) = monoid_hom.id (units M) :=
by ext; refl

/-- Coercion `units M → M` as a monoid homomorphism. -/
@[to_additive "Coercion `add_units M → M` as an add_monoid homomorphism."]
def coe_hom : units M →* M := ⟨coe, coe_one, coe_mul⟩

variable {M}

@[simp, to_additive] lemma coe_hom_apply (x : units M) : coe_hom M x = ↑x := rfl

/-- If a map `g : M → units N` agrees with a homomorphism `f : M →* N`, then
this map is a monoid homomorphism too. -/
@[to_additive "If a map `g : M → add_units N` agrees with a homomorphism `f : M →+ N`, then this map
is an add_monoid homomorphism too."]
def lift_right (f : M →* N) (g : M → units N) (h : ∀ x, ↑(g x) = f x) :
  M →* units N :=
{ to_fun := g,
  map_one' := units.ext $ (h 1).symm ▸ f.map_one,
  map_mul' := λ x y, units.ext $ by simp only [h, coe_mul, f.map_mul] }

@[simp, to_additive] lemma coe_lift_right {f : M →* N} {g : M → units N}
  (h : ∀ x, ↑(g x) = f x) (x) : (lift_right f g h x : N) = f x := h x

@[simp, to_additive] lemma mul_lift_right_inv {f : M →* N} {g : M → units N}
  (h : ∀ x, ↑(g x) = f x) (x) : f x * ↑(lift_right f g h x)⁻¹ = 1 :=
by rw [units.mul_inv_eq_iff_eq_mul, one_mul, coe_lift_right]

@[simp, to_additive] lemma lift_right_inv_mul {f : M →* N} {g : M → units N}
  (h : ∀ x, ↑(g x) = f x) (x) : ↑(lift_right f g h x)⁻¹ * f x = 1 :=
by rw [units.inv_mul_eq_iff_eq_mul, mul_one, coe_lift_right]

end units

namespace monoid_hom

/-- If `f` is a homomorphism from a group `G` to a monoid `M`,
then its image lies in the units of `M`,
and `f.to_hom_units` is the corresponding monoid homomorphism from `G` to `units M`. -/
@[to_additive "If `f` is a homomorphism from an additive group `G` to an additive monoid `M`,
then its image lies in the `add_units` of `M`,
and `f.to_hom_units` is the corresponding homomorphism from `G` to `add_units M`."]
def to_hom_units {G M : Type*} [group G] [monoid M] (f : G →* M) : G →* units M :=
{ to_fun := λ g,
    ⟨f g, f (g⁻¹),
      by rw [← f.map_mul, mul_inv_self, f.map_one],
      by rw [← f.map_mul, inv_mul_self, f.map_one]⟩,
  map_one' := units.ext (f.map_one),
  map_mul' := λ _ _, units.ext (f.map_mul _ _) }

@[simp] lemma coe_to_hom_units {G M : Type*} [group G] [monoid M] (f : G →* M) (g : G):
  (f.to_hom_units g : M) = f g := rfl

end monoid_hom

section is_unit
variables {M : Type*} {N : Type*}

@[to_additive] lemma is_unit.map [monoid M] [monoid N]
  (f : M →* N) {x : M} (h : is_unit x) : is_unit (f x) :=
by rcases h with ⟨y, rfl⟩; exact is_unit_unit (units.map f y)

/-- If a homomorphism `f : M →* N` sends each element to an `is_unit`, then it can be lifted
to `f : M →* units N`. See also `units.lift_right` for a computable version. -/
@[to_additive "If a homomorphism `f : M →+ N` sends each element to an `is_add_unit`, then it can be
lifted to `f : M →+ add_units N`. See also `add_units.lift_right` for a computable version."]
noncomputable def is_unit.lift_right [monoid M] [monoid N] (f : M →* N)
  (hf : ∀ x, is_unit (f x)) : M →* units N :=
units.lift_right f (λ x, classical.some (hf x)) $ λ x, classical.some_spec (hf x)

@[to_additive] lemma is_unit.coe_lift_right [monoid M] [monoid N] (f : M →* N)
  (hf : ∀ x, is_unit (f x)) (x) :
  (is_unit.lift_right f hf x : N) = f x :=
units.coe_lift_right _ x

@[simp, to_additive] lemma is_unit.mul_lift_right_inv [monoid M] [monoid N] (f : M →* N)
  (h : ∀ x, is_unit (f x)) (x) : f x * ↑(is_unit.lift_right f h x)⁻¹ = 1 :=
units.mul_lift_right_inv (λ y, classical.some_spec $ h y) x

@[simp, to_additive] lemma is_unit.lift_right_inv_mul [monoid M] [monoid N] (f : M →* N)
  (h : ∀ x, is_unit (f x)) (x) : ↑(is_unit.lift_right f h x)⁻¹ * f x = 1 :=
units.lift_right_inv_mul (λ y, classical.some_spec $ h y) x

end is_unit
