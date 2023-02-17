/-
Copyright (c) 2018 Johannes Hölzl. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Johannes Hölzl, Callum Sutton, Yury Kudryashov
-/
import data.equiv.basic
import deprecated.group

/-!
# Multiplicative and additive equivs

In this file we define two extensions of `equiv` called `add_equiv` and `mul_equiv`, which are
datatypes representing isomorphisms of `add_monoid`s/`add_group`s and `monoid`s/`group`s. We also
introduce the corresponding groups of automorphisms `add_aut` and `mul_aut`.

## Notations

The extended equivs all have coercions to functions, and the coercions are the canonical
notation when treating the isomorphisms as maps.

## Implementation notes

The fields for `mul_equiv`, `add_equiv` now avoid the unbundled `is_mul_hom` and `is_add_hom`, as
these are deprecated.

Definition of multiplication in the groups of automorphisms agrees with function composition,
multiplication in `equiv.perm`, and multiplication in `category_theory.End`, not with
`category_theory.comp`.

## Tags

equiv, mul_equiv, add_equiv, mul_aut, add_aut
-/

variables {A : Type*} {B : Type*} {M : Type*} {N : Type*} {P : Type*} {G : Type*} {H : Type*}

set_option old_structure_cmd true

/-- add_equiv α β is the type of an equiv α ≃ β which preserves addition. -/
structure add_equiv (A B : Type*) [has_add A] [has_add B] extends A ≃ B :=
(map_add' : ∀ x y : A, to_fun (x + y) = to_fun x + to_fun y)

/-- `mul_equiv α β` is the type of an equiv `α ≃ β` which preserves multiplication. -/
@[to_additive]
structure mul_equiv (M N : Type*) [has_mul M] [has_mul N] extends M ≃ N :=
(map_mul' : ∀ x y : M, to_fun (x * y) = to_fun x * to_fun y)

infix ` ≃* `:25 := mul_equiv
infix ` ≃+ `:25 := add_equiv

namespace mul_equiv

@[to_additive]
instance [has_mul M] [has_mul N] : has_coe_to_fun (M ≃* N) := ⟨_, mul_equiv.to_fun⟩

variables [has_mul M] [has_mul N] [has_mul P]

@[simp, to_additive]
lemma to_fun_apply {f : M ≃* N} {m : M} : f.to_fun m = f m := rfl

/-- A multiplicative isomorphism preserves multiplication (canonical form). -/
@[to_additive]
lemma map_mul (f : M ≃* N) : ∀ x y, f (x * y) = f x * f y := f.map_mul'

/-- A multiplicative isomorphism preserves multiplication (deprecated). -/
@[to_additive]
instance (h : M ≃* N) : is_mul_hom h := ⟨h.map_mul⟩

/-- Makes a multiplicative isomorphism from a bijection which preserves multiplication. -/
@[to_additive]
def mk' (f : M ≃ N) (h : ∀ x y, f (x * y) = f x * f y) : M ≃* N :=
⟨f.1, f.2, f.3, f.4, h⟩

/-- The identity map is a multiplicative isomorphism. -/
@[refl, to_additive]
def refl (M : Type*) [has_mul M] : M ≃* M :=
{ map_mul' := λ _ _, rfl,
..equiv.refl _}

/-- The inverse of an isomorphism is an isomorphism. -/
@[symm, to_additive]
def symm (h : M ≃* N) : N ≃* M :=
{ map_mul' := λ n₁ n₂, h.left_inv.injective begin
    show h.to_equiv (h.to_equiv.symm (n₁ * n₂)) =
      h ((h.to_equiv.symm n₁) * (h.to_equiv.symm n₂)),
   rw h.map_mul,
   show _ = h.to_equiv (_) * h.to_equiv (_),
   rw [h.to_equiv.apply_symm_apply, h.to_equiv.apply_symm_apply, h.to_equiv.apply_symm_apply], end,
  ..h.to_equiv.symm}

@[simp, to_additive]
theorem to_equiv_symm (f : M ≃* N) : f.symm.to_equiv = f.to_equiv.symm := rfl

@[simp, to_additive]
theorem coe_mk (f : M → N) (g h₁ h₂ h₃) : ⇑(mul_equiv.mk f g h₁ h₂ h₃) = f := rfl

@[simp, to_additive]
theorem coe_symm_mk (f : M → N) (g h₁ h₂ h₃) : ⇑(mul_equiv.mk f g h₁ h₂ h₃).symm = g := rfl

/-- Transitivity of multiplication-preserving isomorphisms -/
@[trans, to_additive]
def trans (h1 : M ≃* N) (h2 : N ≃* P) : (M ≃* P) :=
{ map_mul' := λ x y, show h2 (h1 (x * y)) = h2 (h1 x) * h2 (h1 y),
    by rw [h1.map_mul, h2.map_mul],
  ..h1.to_equiv.trans h2.to_equiv }

/-- e.right_inv in canonical form -/
@[simp, to_additive]
lemma apply_symm_apply (e : M ≃* N) : ∀ y, e (e.symm y) = y :=
e.to_equiv.apply_symm_apply

/-- e.left_inv in canonical form -/
@[simp, to_additive]
lemma symm_apply_apply (e : M ≃* N) : ∀ x, e.symm (e x) = x :=
e.to_equiv.symm_apply_apply

/-- a multiplicative equiv of monoids sends 1 to 1 (and is hence a monoid isomorphism) -/
@[simp, to_additive]
lemma map_one {M N} [monoid M] [monoid N] (h : M ≃* N) : h 1 = 1 :=
by rw [←mul_one (h 1), ←h.apply_symm_apply 1, ←h.map_mul, one_mul]

@[simp, to_additive]
lemma map_eq_one_iff {M N} [monoid M] [monoid N] (h : M ≃* N) {x : M} :
  h x = 1 ↔ x = 1 :=
h.map_one ▸ h.to_equiv.apply_eq_iff_eq x 1

@[to_additive]
lemma map_ne_one_iff {M N} [monoid M] [monoid N] (h : M ≃* N) {x : M} :
  h x ≠ 1 ↔ x ≠ 1 :=
⟨mt h.map_eq_one_iff.2, mt h.map_eq_one_iff.1⟩

/--
Extract the forward direction of a multiplicative equivalence
as a multiplication preserving function.
-/
@[to_additive to_add_monoid_hom]
def to_monoid_hom {M N} [monoid M] [monoid N] (h : M ≃* N) : (M →* N) :=
{ map_one' := h.map_one, .. h }

@[simp, to_additive]
lemma to_monoid_hom_apply {M N} [monoid M] [monoid N] (e : M ≃* N) (x : M) :
  e.to_monoid_hom x = e x :=
rfl

/-- A multiplicative equivalence of groups preserves inversion. -/
@[to_additive]
lemma map_inv [group G] [group H] (h : G ≃* H) (x : G) : h x⁻¹ = (h x)⁻¹ :=
h.to_monoid_hom.map_inv x

/-- A multiplicative bijection between two monoids is a monoid hom
  (deprecated -- use to_monoid_hom). -/
@[to_additive is_add_monoid_hom]
instance is_monoid_hom {M N} [monoid M] [monoid N] (h : M ≃* N) : is_monoid_hom h :=
⟨h.map_one⟩

/-- A multiplicative bijection between two groups is a group hom
  (deprecated -- use to_monoid_hom). -/
@[to_additive is_add_group_hom]
instance is_group_hom {G H} [group G] [group H] (h : G ≃* H) :
  is_group_hom h := { map_mul := h.map_mul }

/-- Two multiplicative isomorphisms agree if they are defined by the
    same underlying function. -/
@[ext, to_additive
  "Two additive isomorphisms agree if they are defined by the same underlying function."]
lemma ext {f g : mul_equiv M N} (h : ∀ x, f x = g x) : f = g :=
begin
  have h₁ : f.to_equiv = g.to_equiv := equiv.ext h,
  cases f, cases g, congr,
  { exact (funext h) },
  { exact congr_arg equiv.inv_fun h₁ }
end

attribute [ext] add_equiv.ext

end mul_equiv

/-- An additive equivalence of additive groups preserves subtraction. -/
lemma add_equiv.map_sub [add_group A] [add_group B] (h : A ≃+ B) (x y : A) :
  h (x - y) = h x - h y :=
h.to_add_monoid_hom.map_sub x y


/-- The group of multiplicative automorphisms. -/
@[to_additive "The group of additive automorphisms."]
def mul_aut (M : Type*) [has_mul M] := M ≃* M

attribute [reducible] mul_aut add_aut

namespace mul_aut

variables (M) [has_mul M]

/--
The group operation on multiplicative automorphisms is defined by
`λ g h, mul_equiv.trans h g`.
This means that multiplication agrees with composition, `(g*h)(x) = g (h x)`.
-/
instance : group (mul_aut M) :=
by refine_struct
{ mul := λ g h, mul_equiv.trans h g,
  one := mul_equiv.refl M,
  inv := mul_equiv.symm };
intros; ext; try { refl }; apply equiv.left_inv

instance : inhabited (mul_aut M) := ⟨1⟩

@[simp] lemma coe_mul (e₁ e₂ : mul_aut M) : ⇑(e₁ * e₂) = e₁ ∘ e₂ := rfl
@[simp] lemma coe_one : ⇑(1 : mul_aut M) = id := rfl

/-- Monoid hom from the group of multiplicative automorphisms to the group of permutations. -/
def to_perm : mul_aut M →* equiv.perm M :=
by refine_struct { to_fun := mul_equiv.to_equiv }; intros; refl

end mul_aut

namespace add_aut

variables (A) [has_add A]

/--
The group operation on additive automorphisms is defined by
`λ g h, mul_equiv.trans h g`.
This means that multiplication agrees with composition, `(g*h)(x) = g (h x)`.
-/
instance group : group (add_aut A) :=
by refine_struct
{ mul := λ g h, add_equiv.trans h g,
  one := add_equiv.refl A,
  inv := add_equiv.symm };
intros; ext; try { refl }; apply equiv.left_inv

instance : inhabited (add_aut A) := ⟨1⟩

@[simp] lemma coe_mul (e₁ e₂ : add_aut A) : ⇑(e₁ * e₂) = e₁ ∘ e₂ := rfl
@[simp] lemma coe_one : ⇑(1 : add_aut A) = id := rfl

/-- Monoid hom from the group of multiplicative automorphisms to the group of permutations. -/
def to_perm : add_aut A →* equiv.perm A :=
by refine_struct { to_fun := add_equiv.to_equiv }; intros; refl

end add_aut

/-- A group is isomorphic to its group of units. -/
def to_units (G) [group G] : G ≃* units G :=
{ to_fun := λ x, ⟨x, x⁻¹, mul_inv_self _, inv_mul_self _⟩,
  inv_fun := coe,
  left_inv := λ x, rfl,
  right_inv := λ u, units.ext rfl,
  map_mul' := λ x y, units.ext rfl }

namespace units

variables [monoid M] [monoid N] [monoid P]

/-- A multiplicative equivalence of monoids defines a multiplicative equivalence
of their groups of units. -/
def map_equiv (h : M ≃* N) : units M ≃* units N :=
{ inv_fun := map h.symm.to_monoid_hom,
  left_inv := λ u, ext $ h.left_inv u,
  right_inv := λ u, ext $ h.right_inv u,
  .. map h.to_monoid_hom }

end units


namespace equiv

section group
variables [group G]

@[to_additive]
protected def mul_left (a : G) : perm G :=
{ to_fun    := λx, a * x,
  inv_fun   := λx, a⁻¹ * x,
  left_inv  := assume x, show a⁻¹ * (a * x) = x, from inv_mul_cancel_left a x,
  right_inv := assume x, show a * (a⁻¹ * x) = x, from mul_inv_cancel_left a x }

@[simp, to_additive]
lemma coe_mul_left (a : G) : ⇑(equiv.mul_left a) = (*) a := rfl

@[simp, to_additive]
lemma mul_left_symm (a : G) : (equiv.mul_left a).symm = equiv.mul_left a⁻¹ :=
ext $ λ x, rfl

@[to_additive]
protected def mul_right (a : G) : perm G :=
{ to_fun    := λx, x * a,
  inv_fun   := λx, x * a⁻¹,
  left_inv  := assume x, show (x * a) * a⁻¹ = x, from mul_inv_cancel_right x a,
  right_inv := assume x, show (x * a⁻¹) * a = x, from inv_mul_cancel_right x a }

@[simp, to_additive]
lemma coe_mul_right (a : G) : ⇑(equiv.mul_right a) = λ x, x * a := rfl

@[simp, to_additive]
lemma mul_right_symm (a : G) : (equiv.mul_right a).symm = equiv.mul_right a⁻¹ :=
ext $ λ x, rfl

variable (G)

@[to_additive]
protected def inv : perm G :=
{ to_fun    := λa, a⁻¹,
  inv_fun   := λa, a⁻¹,
  left_inv  := assume a, inv_inv a,
  right_inv := assume a, inv_inv a }

variable {G}

@[simp, to_additive]
lemma coe_inv : ⇑(equiv.inv G) = has_inv.inv := rfl

@[simp, to_additive]
lemma inv_symm : (equiv.inv G).symm = equiv.inv G := rfl

end group

section point_reflection

variables [add_comm_group A] (x y : A)

/-- Point reflection in `x` as a permutation. -/
def point_reflection (x : A) : perm A :=
(equiv.neg A).trans (equiv.add_left (x + x))

lemma point_reflection_apply : point_reflection x y = x + x - y := rfl

@[simp] lemma point_reflection_self : point_reflection x x = x := add_sub_cancel _ _

lemma point_reflection_involutive : function.involutive (point_reflection x : A → A) :=
λ y, by simp only [point_reflection_apply, sub_sub_cancel]

@[simp] lemma point_reflection_symm : (point_reflection x).symm = point_reflection x :=
by { ext y, rw [symm_apply_eq, point_reflection_involutive x y] }

/-- `x` is the only fixed point of `point_reflection x`. This lemma requires
`x + x = y + y ↔ x = y`. There is no typeclass to use here, so we add it as an explicit argument. -/
lemma point_reflection_fixed_iff_of_bit0_injective {x y : A} (h : function.injective (bit0 : A → A)) :
  point_reflection x y = y ↔ y = x :=
sub_eq_iff_eq_add.trans $ h.eq_iff.trans eq_comm

end point_reflection

end equiv

section type_tags

/-- Reinterpret `f : G ≃+ H` as `multiplicative G ≃* multiplicative H`. -/
def add_equiv.to_multiplicative [add_monoid G] [add_monoid H] (f : G ≃+ H) :
  multiplicative G ≃* multiplicative H :=
⟨f.to_add_monoid_hom.to_multiplicative, f.symm.to_add_monoid_hom.to_multiplicative, f.3, f.4, f.5⟩

/-- Reinterpret `f : G ≃* H` as `additive G ≃+ additive H`. -/
def mul_equiv.to_additive [monoid G] [monoid H] (f : G ≃* H) : additive G ≃+ additive H :=
⟨f.to_monoid_hom.to_additive, f.symm.to_monoid_hom.to_additive, f.3, f.4, f.5⟩

end type_tags
