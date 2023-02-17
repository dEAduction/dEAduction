/-
Copyright (c) 2018 Kenny Lau. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Kenny Lau, Chris Hughes, Mario Carneiro
-/
import algebra.associated
import linear_algebra.basic
import order.zorn

universes u v
variables {α : Type u} {β : Type v} {a b : α}
open set function

open_locale classical big_operators

namespace ideal
variables [comm_ring α] (I : ideal α)

@[ext] lemma ext {I J : ideal α} (h : ∀ x, x ∈ I ↔ x ∈ J) : I = J :=
submodule.ext h

theorem eq_top_of_unit_mem
  (x y : α) (hx : x ∈ I) (h : y * x = 1) : I = ⊤ :=
eq_top_iff.2 $ λ z _, calc
    z = z * (y * x) : by simp [h]
  ... = (z * y) * x : eq.symm $ mul_assoc z y x
  ... ∈ I : I.mul_mem_left hx

theorem eq_top_of_is_unit_mem {x} (hx : x ∈ I) (h : is_unit x) : I = ⊤ :=
let ⟨y, hy⟩ := is_unit_iff_exists_inv'.1 h in eq_top_of_unit_mem I x y hx hy

theorem eq_top_iff_one : I = ⊤ ↔ (1:α) ∈ I :=
⟨by rintro rfl; trivial,
 λ h, eq_top_of_unit_mem _ _ 1 h (by simp)⟩

theorem ne_top_iff_one : I ≠ ⊤ ↔ (1:α) ∉ I :=
not_congr I.eq_top_iff_one

def span (s : set α) : ideal α := submodule.span α s

lemma subset_span {s : set α} : s ⊆ span s := submodule.subset_span

lemma span_le {s : set α} {I} : span s ≤ I ↔ s ⊆ I := submodule.span_le

lemma span_mono {s t : set α} : s ⊆ t → span s ≤ span t := submodule.span_mono

@[simp] lemma span_eq : span (I : set α) = I := submodule.span_eq _

@[simp] lemma span_singleton_one : span ({1} : set α) = ⊤ :=
(eq_top_iff_one _).2 $ subset_span $ mem_singleton _

lemma mem_span_insert {s : set α} {x y} :
  x ∈ span (insert y s) ↔ ∃ a (z ∈ span s), x = a * y + z := submodule.mem_span_insert

lemma mem_span_insert' {s : set α} {x y} :
  x ∈ span (insert y s) ↔ ∃a, x + a * y ∈ span s := submodule.mem_span_insert'

lemma mem_span_singleton' {x y : α} :
  x ∈ span ({y} : set α) ↔ ∃ a, a * y = x := submodule.mem_span_singleton

lemma mem_span_singleton {x y : α} :
  x ∈ span ({y} : set α) ↔ y ∣ x :=
mem_span_singleton'.trans $ exists_congr $ λ _, by rw [eq_comm, mul_comm]

lemma span_singleton_le_span_singleton {x y : α} :
  span ({x} : set α) ≤ span ({y} : set α) ↔ y ∣ x :=
span_le.trans $ singleton_subset_iff.trans mem_span_singleton

lemma span_eq_bot {s : set α} : span s = ⊥ ↔ ∀ x ∈ s, (x:α) = 0 := submodule.span_eq_bot

lemma span_singleton_eq_bot {x} : span ({x} : set α) = ⊥ ↔ x = 0 := submodule.span_singleton_eq_bot

lemma span_singleton_eq_top {x} : span ({x} : set α) = ⊤ ↔ is_unit x :=
by rw [is_unit_iff_dvd_one, ← span_singleton_le_span_singleton, span_singleton_one, eq_top_iff]

@[class] def is_prime (I : ideal α) : Prop :=
I ≠ ⊤ ∧ ∀ {x y : α}, x * y ∈ I → x ∈ I ∨ y ∈ I

theorem is_prime.mem_or_mem {I : ideal α} (hI : I.is_prime) :
  ∀ {x y : α}, x * y ∈ I → x ∈ I ∨ y ∈ I := hI.2

theorem is_prime.mem_or_mem_of_mul_eq_zero {I : ideal α} (hI : I.is_prime)
  {x y : α} (h : x * y = 0) : x ∈ I ∨ y ∈ I :=
hI.2 (h.symm ▸ I.zero_mem)

theorem is_prime.mem_of_pow_mem {I : ideal α} (hI : I.is_prime)
  {r : α} (n : ℕ) (H : r^n ∈ I) : r ∈ I :=
begin
  induction n with n ih,
  { exact (mt (eq_top_iff_one _).2 hI.1).elim H },
  exact or.cases_on (hI.mem_or_mem H) id ih
end

theorem zero_ne_one_of_proper {I : ideal α} (h : I ≠ ⊤) : (0:α) ≠ 1 :=
λ hz, I.ne_top_iff_one.1 h $ hz ▸ I.zero_mem

theorem span_singleton_prime {p : α} (hp : p ≠ 0) :
  is_prime (span ({p} : set α)) ↔ prime p :=
by simp [is_prime, prime, span_singleton_eq_top, hp, mem_span_singleton]

@[class] def is_maximal (I : ideal α) : Prop :=
I ≠ ⊤ ∧ ∀ J, I < J → J = ⊤

theorem is_maximal_iff {I : ideal α} : I.is_maximal ↔
  (1:α) ∉ I ∧ ∀ (J : ideal α) x, I ≤ J → x ∉ I → x ∈ J → (1:α) ∈ J :=
and_congr I.ne_top_iff_one $ forall_congr $ λ J,
by rw [lt_iff_le_not_le]; exact
 ⟨λ H x h hx₁ hx₂, J.eq_top_iff_one.1 $
    H ⟨h, not_subset.2 ⟨_, hx₂, hx₁⟩⟩,
  λ H ⟨h₁, h₂⟩, let ⟨x, xJ, xI⟩ := not_subset.1 h₂ in
   J.eq_top_iff_one.2 $ H x h₁ xI xJ⟩

theorem is_maximal.eq_of_le {I J : ideal α}
  (hI : I.is_maximal) (hJ : J ≠ ⊤) (IJ : I ≤ J) : I = J :=
eq_iff_le_not_lt.2 ⟨IJ, λ h, hJ (hI.2 _ h)⟩

theorem is_maximal.exists_inv {I : ideal α}
  (hI : I.is_maximal) {x} (hx : x ∉ I) : ∃ y, y * x - 1 ∈ I :=
begin
  cases is_maximal_iff.1 hI with H₁ H₂,
  rcases mem_span_insert'.1 (H₂ (span (insert x I)) x
    (set.subset.trans (subset_insert _ _) subset_span)
    hx (subset_span (mem_insert _ _))) with ⟨y, hy⟩,
  rw [span_eq, ← neg_mem_iff, add_comm, neg_add', neg_mul_eq_neg_mul] at hy,
  exact ⟨-y, hy⟩
end

theorem is_maximal.is_prime {I : ideal α} (H : I.is_maximal) : I.is_prime :=
⟨H.1, λ x y hxy, or_iff_not_imp_left.2 $ λ hx, begin
  cases H.exists_inv hx with z hz,
  have := I.mul_mem_left hz,
  rw [mul_sub, mul_one, mul_comm, mul_assoc] at this,
  exact I.neg_mem_iff.1 ((I.add_mem_iff_right $ I.mul_mem_left hxy).1 this)
end⟩

@[priority 100] -- see Note [lower instance priority]
instance is_maximal.is_prime' (I : ideal α) : ∀ [H : I.is_maximal], I.is_prime := is_maximal.is_prime

theorem exists_le_maximal (I : ideal α) (hI : I ≠ ⊤) :
  ∃ M : ideal α, M.is_maximal ∧ I ≤ M :=
begin
  rcases zorn.zorn_partial_order₀ { J : ideal α | J ≠ ⊤ } _ I hI with ⟨M, M0, IM, h⟩,
  { refine ⟨M, ⟨M0, λ J hJ, by_contradiction $ λ J0, _⟩, IM⟩,
    cases h J J0 (le_of_lt hJ), exact lt_irrefl _ hJ },
  { intros S SC cC I IS,
    refine ⟨Sup S, λ H, _, λ _, le_Sup⟩,
    obtain ⟨J, JS, J0⟩ : ∃ J ∈ S, (1 : α) ∈ J,
      from (submodule.mem_Sup_of_directed ⟨I, IS⟩ cC.directed_on).1 ((eq_top_iff_one _).1 H),
    exact SC JS ((eq_top_iff_one _).2 J0) }
end

theorem mem_span_pair {x y z : α} :
  z ∈ span ({x, y} : set α) ↔ ∃ a b, a * x + b * y = z :=
by simp [mem_span_insert, mem_span_singleton', @eq_comm _ _ z]

lemma span_singleton_lt_span_singleton [integral_domain β] {x y : β} :
  span ({x} : set β) < span ({y} : set β) ↔ y ≠ 0 ∧ ∃ d : β, ¬ is_unit d ∧ x = y * d :=
by rw [lt_iff_le_not_le, span_singleton_le_span_singleton, span_singleton_le_span_singleton,
  dvd_and_not_dvd_iff]

lemma factors_decreasing [integral_domain β] (b₁ b₂ : β) (h₁ : b₁ ≠ 0) (h₂ : ¬ is_unit b₂) :
  span ({b₁ * b₂} : set β) < span {b₁} :=
lt_of_le_not_le (ideal.span_le.2 $ singleton_subset_iff.2 $
  ideal.mem_span_singleton.2 ⟨b₂, rfl⟩) $ λ h,
h₂ $ is_unit_of_dvd_one _ $ (mul_dvd_mul_iff_left h₁).1 $
by rwa [mul_one, ← ideal.span_singleton_le_span_singleton]

def quotient (I : ideal α) := I.quotient

namespace quotient
variables {I} {x y : α}
def mk (I : ideal α) (a : α) : I.quotient := submodule.quotient.mk a

protected theorem eq : mk I x = mk I y ↔ x - y ∈ I := submodule.quotient.eq I

instance (I : ideal α) : has_one I.quotient := ⟨mk I 1⟩

@[simp] lemma mk_one (I : ideal α) : mk I 1 = 1 := rfl

instance (I : ideal α) : has_mul I.quotient :=
⟨λ a b, quotient.lift_on₂' a b (λ a b, mk I (a * b)) $
 λ a₁ a₂ b₁ b₂ h₁ h₂, quot.sound $ begin
  refine calc a₁ * a₂ - b₁ * b₂ = a₂ * (a₁ - b₁) + (a₂ - b₂) * b₁ : _
  ... ∈ I : I.add_mem (I.mul_mem_left h₁) (I.mul_mem_right h₂),
  rw [mul_sub, sub_mul, sub_add_sub_cancel, mul_comm, mul_comm b₁]
 end⟩

@[simp] theorem mk_mul : mk I (x * y) = mk I x * mk I y := rfl

instance (I : ideal α) : comm_ring I.quotient :=
{ mul := (*),
  one := 1,
  mul_assoc := λ a b c, quotient.induction_on₃' a b c $
    λ a b c, congr_arg (mk _) (mul_assoc a b c),
  mul_comm := λ a b, quotient.induction_on₂' a b $
    λ a b, congr_arg (mk _) (mul_comm a b),
  one_mul := λ a, quotient.induction_on' a $
    λ a, congr_arg (mk _) (one_mul a),
  mul_one := λ a, quotient.induction_on' a $
    λ a, congr_arg (mk _) (mul_one a),
  left_distrib := λ a b c, quotient.induction_on₃' a b c $
    λ a b c, congr_arg (mk _) (left_distrib a b c),
  right_distrib := λ a b c, quotient.induction_on₃' a b c $
    λ a b c, congr_arg (mk _) (right_distrib a b c),
  ..submodule.quotient.add_comm_group I }

/-- `ideal.quotient.mk` as a `ring_hom` -/
def mk_hom (I : ideal α) : α →+* I.quotient := ⟨mk I, rfl, λ _ _, rfl, rfl, λ _ _, rfl⟩

lemma mk_eq_mk_hom (I : ideal α) (x : α) : ideal.quotient.mk I x = ideal.quotient.mk_hom I x := rfl

def map_mk (I J : ideal α) : ideal I.quotient :=
{ carrier := mk I '' J,
  zero_mem' := ⟨0, J.zero_mem, rfl⟩,
  add_mem' := by rintro _ _ ⟨x, hx, rfl⟩ ⟨y, hy, rfl⟩;
    exact ⟨x + y, J.add_mem hx hy, rfl⟩,
  smul_mem' := by rintro ⟨c⟩ _ ⟨x, hx, rfl⟩;
    exact ⟨c * x, J.mul_mem_left hx, rfl⟩ }

@[simp] lemma mk_zero (I : ideal α) : mk I 0 = 0 := rfl
@[simp] lemma mk_add (I : ideal α) (a b : α) : mk I (a + b) = mk I a + mk I b := rfl
@[simp] lemma mk_neg (I : ideal α) (a : α) : mk I (-a : α) = -mk I a := rfl
@[simp] lemma mk_sub (I : ideal α) (a b : α) : mk I (a - b : α) = mk I a - mk I b := rfl
@[simp] lemma mk_pow (I : ideal α) (a : α) (n : ℕ) : mk I (a ^ n : α) = mk I a ^ n :=
(mk_hom I).map_pow a n

lemma mk_prod {ι} (I : ideal α) (s : finset ι) (f : ι → α) :
  mk I (∏ i in s, f i) = ∏ i in s, mk I (f i) :=
(mk_hom I).map_prod f s

lemma mk_sum {ι} (I : ideal α) (s : finset ι) (f : ι → α) :
  mk I (∑ i in s, f i) = ∑ i in s, mk I (f i) :=
(mk_hom I).map_sum f s

lemma eq_zero_iff_mem {I : ideal α} : mk I a = 0 ↔ a ∈ I :=
by conv {to_rhs, rw ← sub_zero a }; exact quotient.eq'

theorem zero_eq_one_iff {I : ideal α} : (0 : I.quotient) = 1 ↔ I = ⊤ :=
eq_comm.trans $ eq_zero_iff_mem.trans (eq_top_iff_one _).symm

theorem zero_ne_one_iff {I : ideal α} : (0 : I.quotient) ≠ 1 ↔ I ≠ ⊤ :=
not_congr zero_eq_one_iff

protected theorem nonzero {I : ideal α} (hI : I ≠ ⊤) : nonzero I.quotient :=
{ zero_ne_one := zero_ne_one_iff.2 hI }

instance (I : ideal α) [hI : I.is_prime] : integral_domain I.quotient :=
{ eq_zero_or_eq_zero_of_mul_eq_zero := λ a b,
    quotient.induction_on₂' a b $ λ a b hab,
      (hI.mem_or_mem (eq_zero_iff_mem.1 hab)).elim
        (or.inl ∘ eq_zero_iff_mem.2)
        (or.inr ∘ eq_zero_iff_mem.2),
  ..quotient.nonzero hI.1,
  ..quotient.comm_ring I }

lemma exists_inv {I : ideal α} [hI : I.is_maximal] :
 ∀ {a : I.quotient}, a ≠ 0 → ∃ b : I.quotient, a * b = 1 :=
begin
  rintro ⟨a⟩ h,
  cases hI.exists_inv (mt eq_zero_iff_mem.2 h) with b hb,
  rw [mul_comm] at hb,
  exact ⟨mk _ b, quot.sound hb⟩
end

/-- quotient by maximal ideal is a field. def rather than instance, since users will have
computable inverses in some applications -/
protected noncomputable def field (I : ideal α) [hI : I.is_maximal] : field I.quotient :=
{ inv := λ a, if ha : a = 0 then 0 else classical.some (exists_inv ha),
  mul_inv_cancel := λ a (ha : a ≠ 0), show a * dite _ _ _ = _,
    by rw dif_neg ha;
    exact classical.some_spec (exists_inv ha),
  inv_zero := dif_pos rfl,
  ..quotient.integral_domain I }

variable [comm_ring β]

/-- Given a ring homomorphism `f : α →+* β` sending all elements of an ideal to zero,
lift it to the quotient by this ideal. -/
def lift (S : ideal α) (f : α →+* β) (H : ∀ (a : α), a ∈ S → f a = 0) :
  quotient S →+* β :=
{ to_fun := λ x, quotient.lift_on' x f $ λ (a b) (h : _ ∈ _),
    eq_of_sub_eq_zero $ by rw [← f.map_sub, H _ h],
  map_one' := f.map_one,
  map_zero' := f.map_zero,
  map_add' := λ a₁ a₂, quotient.induction_on₂' a₁ a₂ f.map_add,
  map_mul' := λ a₁ a₂, quotient.induction_on₂' a₁ a₂ f.map_mul }

@[simp] lemma lift_mk (S : ideal α) (f : α →+* β) (H : ∀ (a : α), a ∈ S → f a = 0) :
  lift S f H (mk S a) = f a := rfl

end quotient

section lattice
variables {R : Type u} [comm_ring R]

theorem mem_Inf {s : set (ideal R)} {x : R} :
  x ∈ Inf s ↔ ∀ ⦃I⦄, I ∈ s → x ∈ I :=
⟨λ hx I his, hx I ⟨I, infi_pos his⟩, λ H I ⟨J, hij⟩, hij ▸ λ S ⟨hj, hS⟩, hS ▸ H hj⟩

end lattice

/-- All ideals in a field are trivial. -/
lemma eq_bot_or_top {K : Type u} [field K] (I : ideal K) :
  I = ⊥ ∨ I = ⊤ :=
begin
  rw classical.or_iff_not_imp_right,
  change _ ≠ _ → _,
  rw ideal.ne_top_iff_one,
  intro h1,
  rw eq_bot_iff,
  intros r hr,
  by_cases H : r = 0, {simpa},
  simpa [H, h1] using submodule.smul_mem I r⁻¹ hr,
end

lemma eq_bot_of_prime {K : Type u} [field K] (I : ideal K) [h : I.is_prime] :
  I = ⊥ :=
classical.or_iff_not_imp_right.mp I.eq_bot_or_top h.1

end ideal

/-- The set of non-invertible elements of a monoid. -/
def nonunits (α : Type u) [monoid α] : set α := { a | ¬is_unit a }

@[simp] theorem mem_nonunits_iff [comm_monoid α] : a ∈ nonunits α ↔ ¬ is_unit a := iff.rfl

theorem mul_mem_nonunits_right [comm_monoid α] :
  b ∈ nonunits α → a * b ∈ nonunits α :=
mt is_unit_of_mul_is_unit_right

theorem mul_mem_nonunits_left [comm_monoid α] :
  a ∈ nonunits α → a * b ∈ nonunits α :=
mt is_unit_of_mul_is_unit_left

theorem zero_mem_nonunits [semiring α] : 0 ∈ nonunits α ↔ (0:α) ≠ 1 :=
not_congr is_unit_zero_iff

@[simp] theorem one_not_mem_nonunits [monoid α] : (1:α) ∉ nonunits α :=
not_not_intro is_unit_one

theorem coe_subset_nonunits [comm_ring α] {I : ideal α} (h : I ≠ ⊤) :
  (I : set α) ⊆ nonunits α :=
λ x hx hu, h $ I.eq_top_of_is_unit_mem hx hu

lemma exists_max_ideal_of_mem_nonunits [comm_ring α] (h : a ∈ nonunits α) :
  ∃ I : ideal α, I.is_maximal ∧ a ∈ I :=
begin
  have : ideal.span ({a} : set α) ≠ ⊤,
  { intro H, rw ideal.span_singleton_eq_top at H, contradiction },
  rcases ideal.exists_le_maximal _ this with ⟨I, Imax, H⟩,
  use [I, Imax], apply H, apply ideal.subset_span, exact set.mem_singleton a
end

section prio
set_option default_priority 100 -- see Note [default priority]
class local_ring (α : Type u) extends comm_ring α, nonzero α :=
(is_local : ∀ (a : α), (is_unit a) ∨ (is_unit (1 - a)))
end prio

namespace local_ring
variable [local_ring α]

lemma is_unit_or_is_unit_one_sub_self (a : α) :
  (is_unit a) ∨ (is_unit (1 - a)) :=
is_local a

lemma is_unit_of_mem_nonunits_one_sub_self (a : α) (h : (1 - a) ∈ nonunits α) :
  is_unit a :=
or_iff_not_imp_right.1 (is_local a) h

lemma is_unit_one_sub_self_of_mem_nonunits (a : α) (h : a ∈ nonunits α) :
  is_unit (1 - a) :=
or_iff_not_imp_left.1 (is_local a) h

lemma nonunits_add {x y} (hx : x ∈ nonunits α) (hy : y ∈ nonunits α) :
  x + y ∈ nonunits α :=
begin
  rintros ⟨u, hu⟩,
  apply hy,
  suffices : is_unit ((↑u⁻¹ : α) * y),
  { rcases this with ⟨s, hs⟩,
    use u * s,
    convert congr_arg (λ z, (u : α) * z) hs,
    rw ← mul_assoc, simp },
  rw show (↑u⁻¹ * y) = (1 - ↑u⁻¹ * x),
  { rw eq_sub_iff_add_eq,
    replace hu := congr_arg (λ z, (↑u⁻¹ : α) * z) hu.symm,
    simpa [mul_add, add_comm] using hu },
  apply is_unit_one_sub_self_of_mem_nonunits,
  exact mul_mem_nonunits_right hx
end

variable (α)

/-- The ideal of elements that are not units. -/
def nonunits_ideal : ideal α :=
{ carrier := nonunits α,
  zero_mem' := zero_mem_nonunits.2 $ zero_ne_one,
  add_mem' := λ x y hx hy, nonunits_add hx hy,
  smul_mem' := λ a x, mul_mem_nonunits_right }

instance nonunits_ideal.is_maximal : (nonunits_ideal α).is_maximal :=
begin
  rw ideal.is_maximal_iff,
  split,
  { intro h, apply h, exact is_unit_one },
  { intros I x hI hx H,
    erw not_not at hx,
    rcases hx with ⟨u,rfl⟩,
    simpa using I.smul_mem ↑u⁻¹ H }
end

lemma max_ideal_unique :
  ∃! I : ideal α, I.is_maximal :=
⟨nonunits_ideal α, nonunits_ideal.is_maximal α,
  λ I hI, hI.eq_of_le (nonunits_ideal.is_maximal α).1 $
  λ x hx, hI.1 ∘ I.eq_top_of_is_unit_mem hx⟩

variable {α}

@[simp] lemma mem_nonunits_ideal (x) :
  x ∈ nonunits_ideal α ↔ x ∈ nonunits α := iff.rfl

end local_ring

def is_local_ring (α : Type u) [comm_ring α] : Prop :=
((0:α) ≠ 1) ∧ ∀ (a : α), (is_unit a) ∨ (is_unit (1 - a))

def local_of_is_local_ring [comm_ring α] (h : is_local_ring α) : local_ring α :=
{ zero_ne_one := h.1,
  is_local := h.2,
  .. ‹comm_ring α› }

def local_of_unit_or_unit_one_sub [comm_ring α] (hnze : (0:α) ≠ 1)
  (h : ∀ x : α, is_unit x ∨ is_unit (1 - x)) : local_ring α :=
local_of_is_local_ring ⟨hnze, h⟩

def local_of_nonunits_ideal [comm_ring α] (hnze : (0:α) ≠ 1)
  (h : ∀ x y ∈ nonunits α, x + y ∈ nonunits α) : local_ring α :=
local_of_is_local_ring ⟨hnze,
λ x, or_iff_not_imp_left.mpr $ λ hx,
begin
  by_contra H,
  apply h _ _ hx H,
  simp [-sub_eq_add_neg, add_sub_cancel'_right]
end⟩

def local_of_unique_max_ideal [comm_ring α] (h : ∃! I : ideal α, I.is_maximal) :
  local_ring α :=
local_of_nonunits_ideal
(let ⟨I, Imax, _⟩ := h in (λ (H : 0 = 1), Imax.1 $ I.eq_top_iff_one.2 $ H ▸ I.zero_mem))
$ λ x y hx hy H,
let ⟨I, Imax, Iuniq⟩ := h in
let ⟨Ix, Ixmax, Hx⟩ := exists_max_ideal_of_mem_nonunits hx in
let ⟨Iy, Iymax, Hy⟩ := exists_max_ideal_of_mem_nonunits hy in
have xmemI : x ∈ I, from ((Iuniq Ix Ixmax) ▸ Hx),
have ymemI : y ∈ I, from ((Iuniq Iy Iymax) ▸ Hy),
Imax.1 $ I.eq_top_of_is_unit_mem (I.add_mem xmemI ymemI) H

section prio
set_option default_priority 100 -- see Note [default priority]
class is_local_ring_hom [semiring α] [semiring β] (f : α →+* β) : Prop :=
(map_nonunit : ∀ a, is_unit (f a) → is_unit a)
end prio

@[simp] lemma is_unit_of_map_unit [semiring α] [semiring β] (f : α →+* β) [is_local_ring_hom f]
  (a) (h : is_unit (f a)) : is_unit a :=
is_local_ring_hom.map_nonunit a h

section
open local_ring
variables [local_ring α] [local_ring β]
variables (f : α →+* β) [is_local_ring_hom f]

lemma map_nonunit (a) (h : a ∈ nonunits_ideal α) : f a ∈ nonunits_ideal β :=
λ H, h $ is_unit_of_map_unit f a H

end

namespace local_ring
variables [local_ring α] [local_ring β]

variable (α)
def residue_field := (nonunits_ideal α).quotient

noncomputable instance residue_field.field : field (residue_field α) :=
ideal.quotient.field (nonunits_ideal α)

/-- The quotient map from a local ring to it's residue field. -/
def residue : α →+* (residue_field α) :=
ideal.quotient.mk_hom _

namespace residue_field

variables {α β}
noncomputable def map (f : α →+* β) [is_local_ring_hom f] :
  residue_field α →+* residue_field β :=
ideal.quotient.lift (nonunits_ideal α) ((ideal.quotient.mk_hom _).comp f) $
λ a ha,
begin
  erw ideal.quotient.eq_zero_iff_mem,
  exact map_nonunit f a ha
end

end residue_field

end local_ring

namespace field
variables [field α]

@[priority 100] -- see Note [lower instance priority]
instance : local_ring α :=
{ is_local := λ a,
  if h : a = 0
  then or.inr (by rw [h, sub_zero]; exact is_unit_one)
  else or.inl $ is_unit_of_mul_eq_one a a⁻¹ $ div_self h }

end field
