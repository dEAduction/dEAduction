/-
Copyright (c) 2019 Yury Kudryashov. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Yury Kudryashov
-/
import algebra.group.type_tags
import algebra.group.units_hom
import algebra.ring

/-!
# Unbundled monoid and group homomorphisms (deprecated)

This file defines typeclasses for unbundled monoid and group homomorphisms. Though these classes are
deprecated, they are still widely used in mathlib, and probably will not go away before Lean 4
because Lean 3 often fails to coerce a bundled homomorphism to a function.

## main definitions

monoid_hom, is_monoid_hom (deprecated), is_group_hom (deprecated)

## implementation notes

There's a coercion from bundled homs to fun, and the canonical
notation is to use the bundled hom as a function via this coercion.

There is no `group_hom` -- the idea is that `monoid_hom` is used.
The constructor for `monoid_hom` needs a proof of `map_one` as well
as `map_mul`; a separate constructor `monoid_hom.mk'` will construct
group homs (i.e. monoid homs between groups) given only a proof
that multiplication is preserved,

Throughout the `monoid_hom` section implicit `{}` brackets are often used instead of type class `[]`
brackets.  This is done when the instances can be inferred because they are implicit arguments to
the type `monoid_hom`.  When they can be inferred from the type it is faster to use this method than
to use type class inference.

## Tags

is_group_hom, is_monoid_hom, monoid_hom

-/

/--
We have lemmas stating that the composition of two morphisms is again a morphism.
Since composition is reducible, type class inference will always succeed in applying these instances.
For example when the goal is just `⊢ is_mul_hom f` the instance `is_mul_hom.comp`
will still succeed, unifying `f` with `f ∘ (λ x, x)`.  This causes type class inference to loop.
To avoid this, we do not make these lemmas instances.
-/
library_note "no instance on morphisms"

universes u v
variables {α : Type u} {β : Type v}

/-- Predicate for maps which preserve an addition. -/
class is_add_hom {α β : Type*} [has_add α] [has_add β] (f : α → β) : Prop :=
(map_add [] : ∀ x y, f (x + y) = f x + f y)

/-- Predicate for maps which preserve a multiplication. -/
@[to_additive]
class is_mul_hom {α β : Type*} [has_mul α] [has_mul β] (f : α → β) : Prop :=
(map_mul [] : ∀ x y, f (x * y) = f x * f y)

namespace is_mul_hom
variables [has_mul α] [has_mul β] {γ : Type*} [has_mul γ]

/-- The identity map preserves multiplication. -/
@[to_additive "The identity map preserves addition"]
instance id : is_mul_hom (id : α → α) := {map_mul := λ _ _, rfl}

/-- The composition of maps which preserve multiplication, also preserves multiplication. -/
-- see Note [no instance on morphisms]
@[to_additive "The composition of addition preserving maps also preserves addition"]
lemma comp (f : α → β) (g : β → γ) [is_mul_hom f] [hg : is_mul_hom g] : is_mul_hom (g ∘ f) :=
{ map_mul := λ x y, by simp only [function.comp, map_mul f, map_mul g] }

/-- A product of maps which preserve multiplication,
preserves multiplication when the target is commutative. -/
@[instance, priority 10, to_additive]
lemma mul {α β} [semigroup α] [comm_semigroup β]
  (f g : α → β) [is_mul_hom f] [is_mul_hom g] :
  is_mul_hom (λa, f a * g a) :=
{ map_mul := assume a b, by simp only [map_mul f, map_mul g, mul_comm, mul_assoc, mul_left_comm] }

/-- The inverse of a map which preserves multiplication,
preserves multiplication when the target is commutative. -/
@[instance, to_additive]
lemma inv {α β} [has_mul α] [comm_group β] (f : α → β) [is_mul_hom f] :
  is_mul_hom (λa, (f a)⁻¹) :=
{ map_mul := assume a b, (map_mul f a b).symm ▸ mul_inv _ _ }

end is_mul_hom

section prio
set_option default_priority 100 -- see Note [default priority]
/-- Predicate for add_monoid homomorphisms (deprecated -- use the bundled `monoid_hom` version). -/
class is_add_monoid_hom [add_monoid α] [add_monoid β] (f : α → β) extends is_add_hom f : Prop :=
(map_zero [] : f 0 = 0)

/-- Predicate for monoid homomorphisms (deprecated -- use the bundled `monoid_hom` version). -/
@[to_additive is_add_monoid_hom]
class is_monoid_hom [monoid α] [monoid β] (f : α → β) extends is_mul_hom f : Prop :=
(map_one [] : f 1 = 1)
end prio

namespace monoid_hom
variables {M : Type*} {N : Type*} {P : Type*} [mM : monoid M] [mN : monoid N] {mP : monoid P}
variables {G : Type*} {H : Type*} [group G] [comm_group H]

include mM mN
/-- Interpret a map `f : M → N` as a homomorphism `M →* N`. -/
@[to_additive "Interpret a map `f : M → N` as a homomorphism `M →+ N`."]
def of (f : M → N) [h : is_monoid_hom f] : M →* N :=
{ to_fun := f,
  map_one' := h.2,
  map_mul' := h.1.1 }

variables {mM mN mP}
@[simp, to_additive]
lemma coe_of (f : M → N) [is_monoid_hom f] : ⇑ (monoid_hom.of f) = f :=
rfl

@[to_additive is_add_monoid_hom]
instance (f : M →* N) : is_monoid_hom (f : M → N) :=
{ map_mul := f.map_mul,
  map_one := f.map_one }

end monoid_hom

namespace is_monoid_hom
variables [monoid α] [monoid β] (f : α → β) [is_monoid_hom f]

/-- A monoid homomorphism preserves multiplication. -/
@[to_additive]
lemma map_mul (x y) : f (x * y) = f x * f y :=
is_mul_hom.map_mul f x y

end is_monoid_hom

/-- A map to a group preserving multiplication is a monoid homomorphism. -/
@[to_additive]
theorem is_monoid_hom.of_mul [monoid α] [group β] (f : α → β) [is_mul_hom f] :
  is_monoid_hom f :=
{ map_one := mul_self_iff_eq_one.1 $ by rw [← is_mul_hom.map_mul f, one_mul] }

namespace is_monoid_hom
variables [monoid α] [monoid β] (f : α → β) [is_monoid_hom f]

/-- The identity map is a monoid homomorphism. -/
@[to_additive]
instance id : is_monoid_hom (@id α) := { map_one := rfl }

/-- The composite of two monoid homomorphisms is a monoid homomorphism. -/
@[to_additive] -- see Note [no instance on morphisms]
lemma comp {γ} [monoid γ] (g : β → γ) [is_monoid_hom g] :
  is_monoid_hom (g ∘ f) :=
{ map_one := show g _ = 1, by rw [map_one f, map_one g], ..is_mul_hom.comp _ _ }

end is_monoid_hom

namespace is_add_monoid_hom

/-- Left multiplication in a ring is an additive monoid morphism. -/
instance is_add_monoid_hom_mul_left {γ : Type*} [semiring γ] (x : γ) :
  is_add_monoid_hom (λ y : γ, x * y) :=
{ map_zero := mul_zero x, map_add := λ y z, mul_add x y z }

/-- Right multiplication in a ring is an additive monoid morphism. -/
instance is_add_monoid_hom_mul_right {γ : Type*} [semiring γ] (x : γ) :
  is_add_monoid_hom (λ y : γ, y * x) :=
{ map_zero := zero_mul x, map_add := λ y z, add_mul y z x }

end is_add_monoid_hom

section prio
set_option default_priority 100 -- see Note [default priority]
/-- Predicate for additive group homomorphism (deprecated -- use bundled `monoid_hom`). -/
class is_add_group_hom [add_group α] [add_group β] (f : α → β) extends is_add_hom f : Prop

/-- Predicate for group homomorphisms (deprecated -- use bundled `monoid_hom`). -/
@[to_additive is_add_group_hom]
class is_group_hom [group α] [group β] (f : α → β) extends is_mul_hom f : Prop
end prio

@[to_additive is_add_group_hom]
instance monoid_hom.is_group_hom {G H : Type*} {_ : group G} {_ : group H} (f : G →* H) :
  is_group_hom (f : G → H) :=
{ map_mul := f.map_mul }

/-- Construct `is_group_hom` from its only hypothesis. The default constructor tries to get
`is_mul_hom` from class instances, and this makes some proofs fail. -/
@[to_additive]
lemma is_group_hom.mk' [group α] [group β] {f : α → β} (hf : ∀ x y, f (x * y) = f x * f y) :
  is_group_hom f :=
{ map_mul := hf }

namespace is_group_hom
variables [group α] [group β] (f : α → β) [is_group_hom f]
open is_mul_hom (map_mul)

/-- A group homomorphism is a monoid homomorphism. -/
@[priority 100, to_additive to_is_add_monoid_hom] -- see Note [lower instance priority]
instance to_is_monoid_hom : is_monoid_hom f :=
is_monoid_hom.of_mul f

/-- A group homomorphism sends 1 to 1. -/
@[to_additive]
lemma map_one : f 1 = 1 := is_monoid_hom.map_one f

/-- A group homomorphism sends inverses to inverses. -/
@[to_additive]
theorem map_inv (a : α) : f a⁻¹ = (f a)⁻¹ :=
eq_inv_of_mul_eq_one $ by rw [← map_mul f, inv_mul_self, map_one f]

/-- The identity is a group homomorphism. -/
@[to_additive]
instance id : is_group_hom (@id α) := { }

/-- The composition of two group homomomorphisms is a group homomorphism. -/
@[to_additive] -- see Note [no instance on morphisms]
lemma comp {γ} [group γ] (g : β → γ) [is_group_hom g] : is_group_hom (g ∘ f) :=
{ ..is_mul_hom.comp _ _ }

/-- A group homomorphism is injective iff its kernel is trivial. -/
@[to_additive]
lemma injective_iff (f : α → β) [is_group_hom f] :
  function.injective f ↔ (∀ a, f a = 1 → a = 1) :=
⟨λ h _, by rw ← is_group_hom.map_one f; exact @h _ _,
  λ h x y hxy, by rw [← inv_inv (f x), inv_eq_iff_mul_eq_one, ← map_inv f,
      ← map_mul f] at hxy;
    simpa using inv_eq_of_mul_eq_one (h _ hxy)⟩

/-- The product of group homomorphisms is a group homomorphism if the target is commutative. -/
@[instance, priority 10, to_additive]
lemma mul {α β} [group α] [comm_group β]
  (f g : α → β) [is_group_hom f] [is_group_hom g] :
  is_group_hom (λa, f a * g a) :=
{ }

/-- The inverse of a group homomorphism is a group homomorphism if the target is commutative. -/
@[instance, to_additive]
lemma inv {α β} [group α] [comm_group β] (f : α → β) [is_group_hom f] :
  is_group_hom (λa, (f a)⁻¹) :=
{ }

end is_group_hom

/-- Inversion is a group homomorphism if the group is commutative. -/
@[instance, to_additive is_add_group_hom]
lemma inv.is_group_hom [comm_group α] : is_group_hom (has_inv.inv : α → α) :=
{ map_mul := mul_inv }

namespace is_add_group_hom
variables [add_group α] [add_group β] (f : α → β) [is_add_group_hom f]

/-- Additive group homomorphisms commute with subtraction. -/
lemma map_sub (a b) : f (a - b) = f a - f b :=
calc f (a + -b) = f a + f (-b) : is_add_hom.map_add f _ _
            ... = f a + -f b   : by rw [map_neg f]

end is_add_group_hom

/-- The difference of two additive group homomorphisms is an additive group
homomorphism if the target is commutative. -/
@[instance]
lemma is_add_group_hom.sub {α β} [add_group α] [add_comm_group β]
  (f g : α → β) [is_add_group_hom f] [is_add_group_hom g] :
  is_add_group_hom (λa, f a - g a) :=
is_add_group_hom.add f (λa, - g a)

namespace units

variables {M : Type*} {N : Type*} [monoid M] [monoid N]

/-- The group homomorphism on units induced by a multiplicative morphism. -/
@[reducible] def map' (f : M → N) [is_monoid_hom f] : units M →* units N :=
  map (monoid_hom.of f)

@[simp] lemma coe_map' (f : M → N) [is_monoid_hom f] (x : units M) :
  ↑((map' f : units M → units N) x) = f x :=
rfl

instance coe_is_monoid_hom : is_monoid_hom (coe : units M → M) := (coe_hom M).is_monoid_hom

end units

namespace is_unit

variables {M : Type*} {N : Type*} [monoid M] [monoid N] {x : M}

lemma map' (f : M → N) {x : M} (h : is_unit x) [is_monoid_hom f] :
  is_unit (f x) :=
h.map (monoid_hom.of f)

end is_unit

lemma additive.is_add_hom [has_mul α] [has_mul β] (f : α → β) [is_mul_hom f] :
  @is_add_hom (additive α) (additive β) _ _ f :=
{ map_add := @is_mul_hom.map_mul α β _ _ f _ }

lemma multiplicative.is_mul_hom [has_add α] [has_add β] (f : α → β) [is_add_hom f] :
  @is_mul_hom (multiplicative α) (multiplicative β) _ _ f :=
{ map_mul := @is_add_hom.map_add α β _ _ f _ }

lemma additive.is_add_monoid_hom [monoid α] [monoid β] (f : α → β) [is_monoid_hom f] :
  @is_add_monoid_hom (additive α) (additive β) _ _ f :=
{ map_zero := @is_monoid_hom.map_one α β _ _ f _,
  ..additive.is_add_hom f }

lemma multiplicative.is_monoid_hom [add_monoid α] [add_monoid β] (f : α → β) [is_add_monoid_hom f] :
  @is_monoid_hom (multiplicative α) (multiplicative β) _ _ f :=
{ map_one := @is_add_monoid_hom.map_zero α β _ _ f _,
  ..multiplicative.is_mul_hom f }

lemma additive.is_add_group_hom [group α] [group β] (f : α → β) [is_group_hom f] :
  @is_add_group_hom (additive α) (additive β) _ _ f :=
{ map_add := @is_mul_hom.map_mul α β _ _ f _ }

lemma multiplicative.is_group_hom [add_group α] [add_group β] (f : α → β) [is_add_group_hom f] :
  @is_group_hom (multiplicative α) (multiplicative β) _ _ f :=
{ map_mul := @is_add_hom.map_add α β _ _ f _ }
