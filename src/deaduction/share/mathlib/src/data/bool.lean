/-
Copyright (c) 2014 Microsoft Corporation. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Leonardo de Moura, Jeremy Avigad
-/

/-!
# booleans

This file proves various trivial lemmas about booleans and their
relation to decidable propositions.

## Notations

This file introduces the notation `!b` for `bnot b`, the boolean "not".

## Tags
bool, boolean, De Morgan
-/

prefix `!`:90 := bnot

namespace bool

@[simp] theorem coe_sort_tt : coe_sort.{1 1} tt = true := eq_true_intro rfl

@[simp] theorem coe_sort_ff : coe_sort.{1 1} ff = false := eq_false_intro ff_ne_tt

@[simp] theorem to_bool_true {h} : @to_bool true h = tt :=
show _ = to_bool true, by congr

@[simp] theorem to_bool_false {h} : @to_bool false h = ff :=
show _ = to_bool false, by congr

@[simp] theorem to_bool_coe (b:bool) {h} : @to_bool b h = b :=
(show _ = to_bool b, by congr).trans (by cases b; refl)

theorem coe_to_bool (p : Prop) [decidable p] : to_bool p ↔ p := to_bool_iff _

@[simp] lemma of_to_bool_iff {p : Prop} [decidable p] : to_bool p ↔ p :=
⟨of_to_bool_true, _root_.to_bool_true⟩

@[simp] lemma tt_eq_to_bool_iff {p : Prop} [decidable p] : tt = to_bool p ↔ p :=
eq_comm.trans of_to_bool_iff

@[simp] lemma ff_eq_to_bool_iff {p : Prop} [decidable p] : ff = to_bool p ↔ ¬ p :=
eq_comm.trans (to_bool_ff_iff _)

@[simp] theorem to_bool_not (p : Prop) [decidable p] : to_bool (¬ p) = bnot (to_bool p) :=
by by_cases p; simp *

@[simp] theorem to_bool_and (p q : Prop) [decidable p] [decidable q] :
  to_bool (p ∧ q) = p && q :=
by by_cases p; by_cases q; simp *

@[simp] theorem to_bool_or (p q : Prop) [decidable p] [decidable q] :
  to_bool (p ∨ q) = p || q :=
by by_cases p; by_cases q; simp *

@[simp] theorem to_bool_eq {p q : Prop} [decidable p] [decidable q] :
  to_bool p = to_bool q ↔ (p ↔ q) :=
⟨λ h, (coe_to_bool p).symm.trans $ by simp [h], to_bool_congr⟩

lemma not_ff : ¬ ff := by simp

@[simp] theorem default_bool : default bool = ff := rfl

theorem dichotomy (b : bool) : b = ff ∨ b = tt :=
by cases b; simp

theorem forall_bool {p : bool → Prop} : (∀ b, p b) ↔ p ff ∧ p tt :=
⟨λ h, by simp [h], λ ⟨h₁, h₂⟩ b, by cases b; assumption⟩

theorem exists_bool {p : bool → Prop} : (∃ b, p b) ↔ p ff ∨ p tt :=
⟨λ ⟨b, h⟩, by cases b; [exact or.inl h, exact or.inr h],
 λ h, by cases h; exact ⟨_, h⟩⟩

/-- If `p b` is decidable for all `b : bool`, then `∀ b, p b` is decidable -/
instance decidable_forall_bool {p : bool → Prop} [∀ b, decidable (p b)] : decidable (∀ b, p b) :=
decidable_of_decidable_of_iff and.decidable forall_bool.symm

/-- If `p b` is decidable for all `b : bool`, then `∃ b, p b` is decidable -/
instance decidable_exists_bool {p : bool → Prop} [∀ b, decidable (p b)] : decidable (∃ b, p b) :=
decidable_of_decidable_of_iff or.decidable exists_bool.symm

@[simp] theorem cond_ff {α} (t e : α) : cond ff t e = e := rfl

@[simp] theorem cond_tt {α} (t e : α) : cond tt t e = t := rfl

@[simp] theorem cond_to_bool {α} (p : Prop) [decidable p] (t e : α) :
  cond (to_bool p) t e = if p then t else e :=
by by_cases p; simp *

theorem coe_bool_iff : ∀ {a b : bool}, (a ↔ b) ↔ a = b := dec_trivial

theorem eq_tt_of_ne_ff : ∀ {a : bool}, a ≠ ff → a = tt := dec_trivial

theorem eq_ff_of_ne_tt : ∀ {a : bool}, a ≠ tt → a = ff := dec_trivial

theorem bor_comm : ∀ a b, a || b = b || a := dec_trivial

@[simp] theorem bor_assoc : ∀ a b c, (a || b) || c = a || (b || c) := dec_trivial

theorem bor_left_comm : ∀ a b c, a || (b || c) = b || (a || c) := dec_trivial

theorem bor_inl {a b : bool} (H : a) : a || b :=
by simp [H]

theorem bor_inr {a b : bool} (H : b) : a || b :=
by simp [H]

theorem band_comm : ∀ a b, a && b = b && a := dec_trivial

@[simp] theorem band_assoc : ∀ a b c, (a && b) && c = a && (b && c) := dec_trivial

theorem band_left_comm : ∀ a b c, a && (b && c) = b && (a && c) := dec_trivial

theorem band_elim_left : ∀ {a b : bool}, a && b → a := dec_trivial

theorem band_intro : ∀ {a b : bool}, a → b → a && b := dec_trivial

theorem band_elim_right : ∀ {a b : bool}, a && b → b := dec_trivial

@[simp] theorem bnot_false : bnot ff = tt := rfl

@[simp] theorem bnot_true : bnot tt = ff := rfl

theorem eq_tt_of_bnot_eq_ff : ∀ {a : bool}, bnot a = ff → a = tt := dec_trivial

theorem eq_ff_of_bnot_eq_tt : ∀ {a : bool}, bnot a = tt → a = ff := dec_trivial

theorem bxor_comm : ∀ a b, bxor a b = bxor b a := dec_trivial
@[simp] theorem bxor_assoc : ∀ a b c, bxor (bxor a b) c = bxor a (bxor b c) := dec_trivial
theorem bxor_left_comm : ∀ a b c, bxor a (bxor b c) = bxor b (bxor a c) := dec_trivial
@[simp] theorem bxor_bnot_left : ∀ a, bxor (!a) a = tt := dec_trivial
@[simp] theorem bxor_bnot_right : ∀ a, bxor a (!a) = tt := dec_trivial
@[simp] theorem bxor_bnot_bnot : ∀ a b, bxor (!a) (!b) = bxor a b := dec_trivial

lemma bxor_iff_ne : ∀ {x y : bool}, bxor x y = tt ↔ x ≠ y := dec_trivial

/-! ### De Morgan's laws for booleans-/
@[simp] lemma bnot_band : ∀ (a b : bool), !(a && b) = !a || !b := dec_trivial
@[simp] lemma bnot_bor : ∀ (a b : bool), !(a || b) = !a && !b := dec_trivial

lemma bnot_inj : ∀ {a b : bool}, !a = !b → a = b := dec_trivial

end bool

instance : decidable_linear_order bool :=
begin
  constructor,
  show bool → bool → Prop,
  { exact λ a b, a = ff ∨ b = tt },
  all_goals {apply_instance <|> exact dec_trivial}
end
