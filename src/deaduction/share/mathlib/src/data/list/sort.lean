/-
Copyright (c) 2016 Jeremy Avigad. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Jeremy Avigad

Insertion sort and merge sort.
-/
import data.list.perm
open list.perm

namespace list

section sorted
universe variable uu
variables {α : Type uu} {r : α → α → Prop}

/-- `sorted r l` is the same as `pairwise r l`, preferred in the case that `r`
  is a `<` or `≤`-like relation (transitive and antisymmetric or asymmetric) -/
def sorted := @pairwise

@[simp] theorem sorted_nil : sorted r [] := pairwise.nil

theorem sorted_of_sorted_cons {a : α} {l : list α} : sorted r (a :: l) → sorted r l :=
pairwise_of_pairwise_cons

theorem sorted.tail {r : α → α → Prop} : Π {l : list α}, sorted r l → sorted r l.tail
| [] h := h
| (hd :: tl) h := sorted_of_sorted_cons h

theorem rel_of_sorted_cons {a : α} {l : list α} : sorted r (a :: l) →
  ∀ b ∈ l, r a b :=
rel_of_pairwise_cons

@[simp] theorem sorted_cons {a : α} {l : list α} :
  sorted r (a :: l) ↔ (∀ b ∈ l, r a b) ∧ sorted r l :=
pairwise_cons

theorem eq_of_sorted_of_perm [is_antisymm α r]
  {l₁ l₂ : list α} (p : l₁ ~ l₂) (s₁ : sorted r l₁) (s₂ : sorted r l₂) : l₁ = l₂ :=
begin
  induction s₁ with a l₁ h₁ s₁ IH generalizing l₂,
  { exact p.nil_eq },
  { have : a ∈ l₂ := p.subset (mem_cons_self _ _),
    rcases mem_split this with ⟨u₂, v₂, rfl⟩,
    have p' := (perm_cons a).1 (p.trans perm_middle),
    have := IH p' (pairwise_of_sublist (by simp) s₂), subst l₁,
    change a::u₂ ++ v₂ = u₂ ++ ([a] ++ v₂), rw ← append_assoc, congr,
    have : ∀ (x : α) (h : x ∈ u₂), x = a := λ x m,
      antisymm ((pairwise_append.1 s₂).2.2 _ m a (mem_cons_self _ _))
        (h₁ _ (by simp [m])),
    rw [(@eq_repeat _ a (length u₂ + 1) (a::u₂)).2,
        (@eq_repeat _ a (length u₂ + 1) (u₂++[a])).2];
    split; simp [iff_true_intro this, or_comm] }
end

@[simp] theorem sorted_singleton (a : α) : sorted r [a] := pairwise_singleton _ _

lemma nth_le_of_sorted_of_le [is_refl α r] {l : list α}
  (h : l.sorted r) {a b : ℕ} {ha : a < l.length} {hb : b < l.length} (hab : a ≤ b) :
  r (l.nth_le a ha) (l.nth_le b hb) :=
begin
  cases eq_or_lt_of_le hab with H H,
  { induction H, exact refl _ },
  { exact list.pairwise_iff_nth_le.1 h a b hb H }
end

end sorted

/-
  sorting procedures
-/

section sort
universe variable uu
parameters {α : Type uu} (r : α → α → Prop) [decidable_rel r]
local infix ` ≼ ` : 50 := r

/- insertion sort -/

section insertion_sort

/-- `ordered_insert a l` inserts `a` into `l` at such that
  `ordered_insert a l` is sorted if `l` is. -/
@[simp] def ordered_insert (a : α) : list α → list α
| []       := [a]
| (b :: l) := if a ≼ b then a :: b :: l else b :: ordered_insert l

/-- `insertion_sort l` returns `l` sorted using the insertion sort algorithm. -/
@[simp] def insertion_sort : list α → list α
| []       := []
| (b :: l) := ordered_insert b (insertion_sort l)

@[simp] lemma ordered_insert_nil (a : α) : [].ordered_insert r a = [a] := rfl

theorem ordered_insert_length : Π (L : list α) (a : α), (L.ordered_insert r a).length = L.length + 1
| [] a := rfl
| (hd :: tl) a := by { dsimp [ordered_insert], split_ifs; simp [ordered_insert_length], }

section correctness
open perm

theorem perm_ordered_insert (a) : ∀ l : list α, ordered_insert a l ~ a :: l
| []       := perm.refl _
| (b :: l) := by by_cases a ≼ b; [simp [ordered_insert, h],
  simpa [ordered_insert, h] using
    ((perm_ordered_insert l).cons _).trans (perm.swap _ _ _)]

theorem ordered_insert_count [decidable_eq α] (L : list α) (a b : α) :
  count a (L.ordered_insert r b) = count a L + if (a = b) then 1 else 0 :=
begin
  rw [(L.perm_ordered_insert r b).count_eq, count_cons],
  split_ifs; simp only [nat.succ_eq_add_one, add_zero],
end

theorem perm_insertion_sort : ∀ l : list α, insertion_sort l ~ l
| []       := perm.nil
| (b :: l) := by simpa [insertion_sort] using
  (perm_ordered_insert _ _ _).trans ((perm_insertion_sort l).cons b)

section total_and_transitive
variables [is_total α r] [is_trans α r]

theorem sorted_ordered_insert (a : α) : ∀ l, sorted r l → sorted r (ordered_insert a l)
| []       h := sorted_singleton a
| (b :: l) h := begin
  by_cases h' : a ≼ b,
  { simpa [ordered_insert, h', h] using λ b' bm, trans h' (rel_of_sorted_cons h _ bm) },
  { suffices : ∀ (b' : α), b' ∈ ordered_insert r a l → r b b',
    { simpa [ordered_insert, h', sorted_ordered_insert l (sorted_of_sorted_cons h)] },
    intros b' bm,
    cases (show b' = a ∨ b' ∈ l, by simpa using
      (perm_ordered_insert _ _ _).subset bm) with be bm,
    { subst b', exact (total_of r _ _).resolve_left h' },
    { exact rel_of_sorted_cons h _ bm } }
end

theorem sorted_insertion_sort : ∀ l, sorted r (insertion_sort l)
| []       := sorted_nil
| (a :: l) := sorted_ordered_insert a _ (sorted_insertion_sort l)

end total_and_transitive
end correctness
end insertion_sort

/- merge sort -/

section merge_sort

-- TODO(Jeremy): observation: if instead we write (a :: (split l).1, b :: (split l).2), the
-- equation compiler can't prove the third equation

/-- Split `l` into two lists of approximately equal length.

     split [1, 2, 3, 4, 5] = ([1, 3, 5], [2, 4]) -/
@[simp] def split : list α → list α × list α
| []       := ([], [])
| (a :: l) := let (l₁, l₂) := split l in (a :: l₂, l₁)

theorem split_cons_of_eq (a : α) {l l₁ l₂ : list α} (h : split l = (l₁, l₂)) :
  split (a :: l) = (a :: l₂, l₁) :=
by rw [split, h]; refl

theorem length_split_le : ∀ {l l₁ l₂ : list α},
  split l = (l₁, l₂) → length l₁ ≤ length l ∧ length l₂ ≤ length l
| []     ._  ._  rfl := ⟨nat.le_refl 0, nat.le_refl 0⟩
| (a::l) l₁' l₂' h   := begin
  cases e : split l with l₁ l₂,
  injection (split_cons_of_eq _ e).symm.trans h, substs l₁' l₂',
  cases length_split_le e with h₁ h₂,
  exact ⟨nat.succ_le_succ h₂, nat.le_succ_of_le h₁⟩
end

theorem length_split_lt {a b} {l l₁ l₂ : list α} (h : split (a::b::l) = (l₁, l₂)) :
  length l₁ < length (a::b::l) ∧ length l₂ < length (a::b::l) :=
begin
  cases e : split l with l₁' l₂',
  injection (split_cons_of_eq _ (split_cons_of_eq _ e)).symm.trans h, substs l₁ l₂,
  cases length_split_le e with h₁ h₂,
  exact ⟨nat.succ_le_succ (nat.succ_le_succ h₁), nat.succ_le_succ (nat.succ_le_succ h₂)⟩
end

theorem perm_split : ∀ {l l₁ l₂ : list α}, split l = (l₁, l₂) → l ~ l₁ ++ l₂
| []     ._  ._  rfl := perm.refl _
| (a::l) l₁' l₂' h   := begin
  cases e : split l with l₁ l₂,
  injection (split_cons_of_eq _ e).symm.trans h, substs l₁' l₂',
  exact ((perm_split e).trans perm_append_comm).cons a,
end

/-- Merge two sorted lists into one in linear time.

     merge [1, 2, 4, 5] [0, 1, 3, 4] = [0, 1, 1, 2, 3, 4, 4, 5] -/
def merge : list α → list α → list α
| []       l'        := l'
| l        []        := l
| (a :: l) (b :: l') := if a ≼ b then a :: merge l (b :: l') else b :: merge (a :: l) l'

include r
/-- Implementation of a merge sort algorithm to sort a list. -/
def merge_sort : list α → list α
| []        := []
| [a]       := [a]
| (a::b::l) := begin
  cases e : split (a::b::l) with l₁ l₂,
  cases length_split_lt e with h₁ h₂,
  exact merge r (merge_sort l₁) (merge_sort l₂)
end
using_well_founded {
  rel_tac := λ_ _, `[exact ⟨_, inv_image.wf length nat.lt_wf⟩],
  dec_tac := tactic.assumption }

theorem merge_sort_cons_cons {a b} {l l₁ l₂ : list α}
  (h : split (a::b::l) = (l₁, l₂)) :
  merge_sort (a::b::l) = merge (merge_sort l₁) (merge_sort l₂) :=
begin
  suffices : ∀ (L : list α) h1, @@and.rec
    (λ a a (_ : length l₁ < length l + 1 + 1 ∧
      length l₂ < length l + 1 + 1), L) h1 h1 = L,
  { simp [merge_sort, h], apply this },
  intros, cases h1, refl
end

section correctness

theorem perm_merge : ∀ (l l' : list α), merge l l' ~ l ++ l'
| []       []        := perm.nil
| []       (b :: l') := by simp [merge]
| (a :: l) []        := by simp [merge]
| (a :: l) (b :: l') := begin
  by_cases a ≼ b,
  { simpa [merge, h] using perm_merge _ _ },
  { suffices : b :: merge r (a :: l) l' ~ a :: (l ++ b :: l'), {simpa [merge, h]},
    exact ((perm_merge _ _).cons _).trans ((swap _ _ _).trans (perm_middle.symm.cons _)) }
end

theorem perm_merge_sort : ∀ l : list α, merge_sort l ~ l
| []        := perm.refl _
| [a]       := perm.refl _
| (a::b::l) := begin
  cases e : split (a::b::l) with l₁ l₂,
  cases length_split_lt e with h₁ h₂,
  rw [merge_sort_cons_cons r e],
  apply (perm_merge r _ _).trans,
  exact ((perm_merge_sort l₁).append (perm_merge_sort l₂)).trans (perm_split e).symm
end
using_well_founded {
  rel_tac := λ_ _, `[exact ⟨_, inv_image.wf length nat.lt_wf⟩],
  dec_tac := tactic.assumption }

@[simp] lemma length_merge_sort (l : list α) : (merge_sort l).length = l.length :=
(perm_merge_sort _).length_eq

section total_and_transitive
variables [is_total α r] [is_trans α r]

theorem sorted_merge : ∀ {l l' : list α}, sorted r l → sorted r l' → sorted r (merge l l')
| []       []        h₁ h₂ := sorted_nil
| []       (b :: l') h₁ h₂ := by simpa [merge] using h₂
| (a :: l) []        h₁ h₂ := by simpa [merge] using h₁
| (a :: l) (b :: l') h₁ h₂ := begin
  by_cases a ≼ b,
  { suffices : ∀ (b' : α) (_ : b' ∈ merge r l (b :: l')), r a b',
    { simpa [merge, h, sorted_merge (sorted_of_sorted_cons h₁) h₂] },
    intros b' bm,
    rcases (show b' = b ∨ b' ∈ l ∨ b' ∈ l', by simpa [or.left_comm] using
      (perm_merge _ _ _).subset bm) with be | bl | bl',
    { subst b', assumption },
    { exact rel_of_sorted_cons h₁ _ bl },
    { exact trans h (rel_of_sorted_cons h₂ _ bl') } },
  { suffices : ∀ (b' : α) (_ : b' ∈ merge r (a :: l) l'), r b b',
    { simpa [merge, h, sorted_merge h₁ (sorted_of_sorted_cons h₂)] },
    intros b' bm,
    have ba : b ≼ a := (total_of r _ _).resolve_left h,
    rcases (show b' = a ∨ b' ∈ l ∨ b' ∈ l', by simpa using
      (perm_merge _ _ _).subset bm) with be | bl | bl',
    { subst b', assumption },
    { exact trans ba (rel_of_sorted_cons h₁ _ bl) },
    { exact rel_of_sorted_cons h₂ _ bl' } }
end

theorem sorted_merge_sort : ∀ l : list α, sorted r (merge_sort l)
| []        := sorted_nil
| [a]       := sorted_singleton _
| (a::b::l) := begin
  cases e : split (a::b::l) with l₁ l₂,
  cases length_split_lt e with h₁ h₂,
  rw [merge_sort_cons_cons r e],
  exact sorted_merge r (sorted_merge_sort l₁) (sorted_merge_sort l₂)
end
using_well_founded {
  rel_tac := λ_ _, `[exact ⟨_, inv_image.wf length nat.lt_wf⟩],
  dec_tac := tactic.assumption }

theorem merge_sort_eq_self [is_antisymm α r] {l : list α} : sorted r l → merge_sort l = l :=
eq_of_sorted_of_perm (perm_merge_sort _) (sorted_merge_sort _)

end total_and_transitive
end correctness
end merge_sort
end sort

/- try them out! -/

--#eval insertion_sort (λ m n : ℕ, m ≤ n) [5, 27, 221, 95, 17, 43, 7, 2, 98, 567, 23, 12]

--#eval merge_sort     (λ m n : ℕ, m ≤ n) [5, 27, 221, 95, 17, 43, 7, 2, 98, 567, 23, 12]

end list
