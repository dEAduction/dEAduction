/-
Copyright (c) 2020 Yury Kudryashov. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Yury Kudryashov
-/
import order.conditionally_complete_lattice
import algebra.big_operators

/-!
# Support of a function

In this file we define `function.support f = {x | f x ≠ 0}` and prove its basic properties.
-/

universes u v w x y

open set
open_locale big_operators
namespace function

variables {α : Type u} {β : Type v} {ι : Sort w} {A : Type x} {B : Type y}

/-- `support` of a function is the set of points `x` such that `f x ≠ 0`. -/
def support [has_zero A] (f : α → A) : set α := {x | f x ≠ 0}

lemma nmem_support [has_zero A] {f : α → A} {x : α} :
  x ∉ support f ↔ f x = 0 :=
classical.not_not

lemma support_binop_subset [has_zero A] (op : A → A → A) (op0 : op 0 0 = 0) (f g : α → A) :
  support (λ x, op (f x) (g x)) ⊆ support f ∪ support g :=
λ x hx, classical.by_cases
  (λ hf : f x = 0, or.inr $ λ hg, hx $ by simp only [hf, hg, op0])
  or.inl

lemma support_add [add_monoid A] (f g : α → A) :
  support (λ x, f x + g x) ⊆ support f ∪ support g :=
support_binop_subset (+) (zero_add _) f g

@[simp] lemma support_neg [add_group A] (f : α → A) :
  support (λ x, -f x) = support f :=
set.ext $ λ x, not_congr neg_eq_zero

lemma support_sub [add_group A] (f g : α → A) :
  support (λ x, f x - g x) ⊆ support f ∪ support g :=
support_binop_subset (has_sub.sub) (sub_self _) f g

@[simp] lemma support_mul [mul_zero_class A] [no_zero_divisors A] (f g : α → A) :
  support (λ x, f x * g x) = support f ∩ support g :=
set.ext $ λ x, by simp only [support, ne.def, mul_eq_zero, mem_set_of_eq,
  mem_inter_iff, not_or_distrib]

@[simp] lemma support_inv [division_ring A] (f : α → A) :
  support (λ x, (f x)⁻¹) = support f :=
set.ext $ λ x, not_congr inv_eq_zero

@[simp] lemma support_div [division_ring A] (f g : α → A) :
  support (λ x, f x / g x) = support f ∩ support g :=
by simp [div_eq_mul_inv]

lemma support_sup [has_zero A] [semilattice_sup A] (f g : α → A) :
  support (λ x, (f x) ⊔ (g x)) ⊆ support f ∪ support g :=
support_binop_subset (⊔) sup_idem f g

lemma support_inf [has_zero A] [semilattice_inf A] (f g : α → A) :
  support (λ x, (f x) ⊓ (g x)) ⊆ support f ∪ support g :=
support_binop_subset (⊓) inf_idem f g

lemma support_max [has_zero A] [decidable_linear_order A] (f g : α → A) :
  support (λ x, max (f x) (g x)) ⊆ support f ∪ support g :=
support_sup f g

lemma support_min [has_zero A] [decidable_linear_order A] (f g : α → A) :
  support (λ x, min (f x) (g x)) ⊆ support f ∪ support g :=
support_inf f g

lemma support_supr [has_zero A] [conditionally_complete_lattice A] [nonempty ι] (f : ι → α → A) :
  support (λ x, ⨆ i, f i x) ⊆ ⋃ i, support (f i) :=
begin
  intros x hx,
  classical,
  contrapose hx,
  simp only [mem_Union, not_exists, nmem_support] at hx ⊢,
  simp only [hx, csupr_const]
end

lemma support_infi [has_zero A] [conditionally_complete_lattice A] [nonempty ι] (f : ι → α → A) :
  support (λ x, ⨅ i, f i x) ⊆ ⋃ i, support (f i) :=
@support_supr _ _ (order_dual A) ⟨(0:A)⟩ _ _ f

lemma support_sum [add_comm_monoid A] (s : finset α) (f : α → β → A) :
  support (λ x, ∑ i in s, f i x) ⊆ ⋃ i ∈ s, support (f i) :=
begin
  intros x hx,
  classical,
  contrapose hx,
  simp only [mem_Union, not_exists, nmem_support] at hx ⊢,
  exact finset.sum_eq_zero hx
end

-- TODO: Drop `classical` once #2332 is merged
lemma support_prod [integral_domain A] (s : finset α) (f : α → β → A) :
  support (λ x, ∏ i in s, f i x) = ⋂ i ∈ s, support (f i) :=
set.ext $ λ x, by classical;
  simp only [support, ne.def, finset.prod_eq_zero_iff, mem_set_of_eq, set.mem_Inter, not_exists]

lemma support_comp [has_zero A] [has_zero B] (g : A → B) (hg : g 0 = 0) (f : α → A) :
  support (g ∘ f) ⊆ support f :=
λ x, mt $ λ h, by simp [(∘), *]

lemma support_comp' [has_zero A] [has_zero B] (g : A → B) (hg : g 0 = 0) (f : α → A) :
  support (λ x, g (f x)) ⊆ support f :=
support_comp g hg f

lemma support_comp_eq [has_zero A] [has_zero B] (g : A → B) (hg : ∀ {x}, g x = 0 ↔ x = 0)
  (f : α → A) :
  support (g ∘ f) = support f :=
set.ext $ λ x, not_congr hg

lemma support_comp_eq' [has_zero A] [has_zero B] (g : A → B) (hg : ∀ {x}, g x = 0 ↔ x = 0)
  (f : α → A) :
  support (λ x, g (f x)) = support f :=
support_comp_eq g @hg f

end function
