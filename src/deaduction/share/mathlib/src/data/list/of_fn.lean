/-
Copyright (c) 2018 Mario Carneiro. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mario Carneiro
-/
import data.list.basic
import data.fin

universes u

variables {α : Type u}

open nat
namespace list

/- of_fn -/

theorem length_of_fn_aux {n} (f : fin n → α) :
  ∀ m h l, length (of_fn_aux f m h l) = length l + m
| 0        h l := rfl
| (succ m) h l := (length_of_fn_aux m _ _).trans (succ_add _ _)

@[simp] theorem length_of_fn {n} (f : fin n → α) : length (of_fn f) = n :=
(length_of_fn_aux f _ _ _).trans (zero_add _)

theorem nth_of_fn_aux {n} (f : fin n → α) (i) :
  ∀ m h l,
    (∀ i, nth l i = of_fn_nth_val f (i + m)) →
     nth (of_fn_aux f m h l) i = of_fn_nth_val f i
| 0        h l H := H i
| (succ m) h l H := nth_of_fn_aux m _ _ begin
  intro j, cases j with j,
  { simp only [nth, of_fn_nth_val, zero_add, dif_pos (show m < n, from h)] },
  { simp only [nth, H, succ_add] }
end

@[simp] theorem nth_of_fn {n} (f : fin n → α) (i) :
  nth (of_fn f) i = of_fn_nth_val f i :=
nth_of_fn_aux f _ _ _ _ $ λ i,
by simp only [of_fn_nth_val, dif_neg (not_lt.2 (le_add_left n i))]; refl

theorem nth_le_of_fn {n} (f : fin n → α) (i : fin n) :
  nth_le (of_fn f) i.1 ((length_of_fn f).symm ▸ i.2) = f i :=
option.some.inj $ by rw [← nth_le_nth];
  simp only [list.nth_of_fn, of_fn_nth_val, fin.eta, dif_pos i.2]

@[simp] theorem nth_le_of_fn' {n} (f : fin n → α) {i : ℕ} (h : i < (of_fn f).length) :
  nth_le (of_fn f) i h = f ⟨i, ((length_of_fn f) ▸ h)⟩ :=
nth_le_of_fn f ⟨i, ((length_of_fn f) ▸ h)⟩

@[simp] lemma map_of_fn {β : Type*} {n : ℕ} (f : fin n → α) (g : α → β) :
  map g (of_fn f) = of_fn (g ∘ f) :=
ext_le (by simp) (λ i h h', by simp)

theorem array_eq_of_fn {n} (a : array n α) : a.to_list = of_fn a.read :=
suffices ∀ {m h l}, d_array.rev_iterate_aux a
  (λ i, cons) m h l = of_fn_aux (d_array.read a) m h l, from this,
begin
  intros, induction m with m IH generalizing l, {refl},
  simp only [d_array.rev_iterate_aux, of_fn_aux, IH]
end

theorem of_fn_zero (f : fin 0 → α) : of_fn f = [] := rfl

theorem of_fn_succ {n} (f : fin (succ n) → α) :
  of_fn f = f 0 :: of_fn (λ i, f i.succ) :=
suffices ∀ {m h l}, of_fn_aux f (succ m) (succ_le_succ h) l =
  f 0 :: of_fn_aux (λ i, f i.succ) m h l, from this,
begin
  intros, induction m with m IH generalizing l, {refl},
  rw [of_fn_aux, IH], refl
end

theorem of_fn_nth_le : ∀ l : list α, of_fn (λ i, nth_le l i.1 i.2) = l
| [] := rfl
| (a::l) := by rw of_fn_succ; congr; simp only [fin.succ_val]; exact of_fn_nth_le l

-- not registered as a simp lemma, as otherwise it fires before `forall_mem_of_fn_iff` which
-- is much more useful
lemma mem_of_fn {n} (f : fin n → α) (a : α) :
  a ∈ of_fn f ↔ a ∈ set.range f :=
begin
  simp only [mem_iff_nth_le, set.mem_range, nth_le_of_fn'],
  exact ⟨λ ⟨i, hi, h⟩, ⟨_, h⟩, λ ⟨i, hi⟩, ⟨i.1, (length_of_fn f).symm ▸ i.2, by simpa using hi⟩⟩
end

@[simp] lemma forall_mem_of_fn_iff {n : ℕ} {f : fin n → α} {P : α → Prop} :
  (∀ i ∈ of_fn f, P i) ↔ ∀ j : fin n, P (f j) :=
by simp only [mem_of_fn, set.forall_range_iff]

end list
