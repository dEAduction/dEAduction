/-
Copyright (c) 2019 Scott Morrison. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Scott Morrison
-/
import data.list.range
import data.list.bag_inter

open nat

namespace list
/--
`Ico n m` is the list of natural numbers `n ≤ x < m`.
(Ico stands for "interval, closed-open".)

See also `data/set/intervals.lean` for `set.Ico`, modelling intervals in general preorders, and
`multiset.Ico` and `finset.Ico` for `n ≤ x < m` as a multiset or as a finset.

@TODO (anyone): Define `Ioo` and `Icc`, state basic lemmas about them.
@TODO (anyone): Prove that `finset.Ico` and `set.Ico` agree.
@TODO (anyone): Also do the versions for integers?
@TODO (anyone): One could generalise even further, defining
'locally finite partial orders', for which `set.Ico a b` is `[finite]`, and
'locally finite total orders', for which there is a list model.
 -/
def Ico (n m : ℕ) : list ℕ := range' n (m - n)

namespace Ico

theorem zero_bot (n : ℕ) : Ico 0 n = range n :=
by rw [Ico, nat.sub_zero, range_eq_range']

@[simp] theorem length (n m : ℕ) : length (Ico n m) = m - n :=
by dsimp [Ico]; simp only [length_range']

theorem pairwise_lt (n m : ℕ) : pairwise (<) (Ico n m) :=
by dsimp [Ico]; simp only [pairwise_lt_range']

theorem nodup (n m : ℕ) : nodup (Ico n m) :=
by dsimp [Ico]; simp only [nodup_range']

@[simp] theorem mem {n m l : ℕ} : l ∈ Ico n m ↔ n ≤ l ∧ l < m :=
suffices n ≤ l ∧ l < n + (m - n) ↔ n ≤ l ∧ l < m, by simp [Ico, this],
begin
  cases le_total n m with hnm hmn,
  { rw [nat.add_sub_of_le hnm] },
  { rw [nat.sub_eq_zero_of_le hmn, add_zero],
    exact and_congr_right (assume hnl, iff.intro
      (assume hln, (not_le_of_gt hln hnl).elim)
      (assume hlm, lt_of_lt_of_le hlm hmn)) }
end

theorem eq_nil_of_le {n m : ℕ} (h : m ≤ n) : Ico n m = [] :=
by simp [Ico, nat.sub_eq_zero_of_le h]

theorem map_add (n m k : ℕ) : (Ico n m).map ((+) k) = Ico (n + k) (m + k) :=
by rw [Ico, Ico, map_add_range', nat.add_sub_add_right, add_comm n k]

theorem map_sub (n m k : ℕ) (h₁ : k ≤ n) : (Ico n m).map (λ x, x - k) = Ico (n - k) (m - k) :=
begin
  by_cases h₂ : n < m,
  { rw [Ico, Ico],
    rw nat.sub_sub_sub_cancel_right h₁,
    rw [map_sub_range' _ _ _ h₁] },
  { simp at h₂,
    rw [eq_nil_of_le h₂],
    rw [eq_nil_of_le (nat.sub_le_sub_right h₂ _)],
    refl }
end

@[simp] theorem self_empty {n : ℕ} : Ico n n = [] :=
eq_nil_of_le (le_refl n)

@[simp] theorem eq_empty_iff {n m : ℕ} : Ico n m = [] ↔ m ≤ n :=
iff.intro (assume h, nat.le_of_sub_eq_zero $ by rw [← length, h]; refl) eq_nil_of_le

lemma append_consecutive {n m l : ℕ} (hnm : n ≤ m) (hml : m ≤ l) :
  Ico n m ++ Ico m l = Ico n l :=
begin
  dunfold Ico,
  convert range'_append _ _ _,
  { exact (nat.add_sub_of_le hnm).symm },
  { rwa [← nat.add_sub_assoc hnm, nat.sub_add_cancel] }
end

@[simp] lemma inter_consecutive (n m l : ℕ) : Ico n m ∩ Ico m l = [] :=
begin
  apply eq_nil_iff_forall_not_mem.2,
  intro a,
  simp only [and_imp, not_and, not_lt, list.mem_inter, list.Ico.mem],
  intros h₁ h₂ h₃,
  exfalso,
  exact not_lt_of_ge h₃ h₂
end

@[simp] lemma bag_inter_consecutive (n m l : ℕ) : list.bag_inter (Ico n m) (Ico m l) = [] :=
(bag_inter_nil_iff_inter_nil _ _).2 (inter_consecutive n m l)

@[simp] theorem succ_singleton {n : ℕ} : Ico n (n+1) = [n] :=
by dsimp [Ico]; simp [nat.add_sub_cancel_left]

theorem succ_top {n m : ℕ} (h : n ≤ m) : Ico n (m + 1) = Ico n m ++ [m] :=
by rwa [← succ_singleton, append_consecutive]; exact nat.le_succ _

theorem eq_cons {n m : ℕ} (h : n < m) : Ico n m = n :: Ico (n + 1) m :=
by rw [← append_consecutive (nat.le_succ n) h, succ_singleton]; refl

@[simp] theorem pred_singleton {m : ℕ} (h : 0 < m) : Ico (m - 1) m = [m - 1] :=
by dsimp [Ico]; rw nat.sub_sub_self h; simp

theorem chain'_succ (n m : ℕ) : chain' (λa b, b = succ a) (Ico n m) :=
begin
  by_cases n < m,
  { rw [eq_cons h], exact chain_succ_range' _ _ },
  { rw [eq_nil_of_le (le_of_not_gt h)], trivial }
end

@[simp] theorem not_mem_top {n m : ℕ} : m ∉ Ico n m :=
by simp; intros; refl

lemma filter_lt_of_top_le {n m l : ℕ} (hml : m ≤ l) : (Ico n m).filter (λ x, x < l) = Ico n m :=
filter_eq_self.2 $ assume k hk, lt_of_lt_of_le (mem.1 hk).2 hml

lemma filter_lt_of_le_bot {n m l : ℕ} (hln : l ≤ n) : (Ico n m).filter (λ x, x < l) = [] :=
filter_eq_nil.2 $ assume k hk, not_lt_of_le $ le_trans hln $ (mem.1 hk).1

lemma filter_lt_of_ge {n m l : ℕ} (hlm : l ≤ m) : (Ico n m).filter (λ x, x < l) = Ico n l :=
begin
  cases le_total n l with hnl hln,
  { rw [← append_consecutive hnl hlm, filter_append,
      filter_lt_of_top_le (le_refl l), filter_lt_of_le_bot (le_refl l), append_nil] },
  { rw [eq_nil_of_le hln, filter_lt_of_le_bot hln] }
end

@[simp] lemma filter_lt (n m l : ℕ) : (Ico n m).filter (λ x, x < l) = Ico n (min m l) :=
begin
  cases le_total m l with hml hlm,
  { rw [min_eq_left hml, filter_lt_of_top_le hml] },
  { rw [min_eq_right hlm, filter_lt_of_ge hlm] }
end

lemma filter_le_of_le_bot {n m l : ℕ} (hln : l ≤ n) : (Ico n m).filter (λ x, l ≤ x) = Ico n m :=
filter_eq_self.2 $ assume k hk, le_trans hln (mem.1 hk).1

lemma filter_le_of_top_le {n m l : ℕ} (hml : m ≤ l) : (Ico n m).filter (λ x, l ≤ x) = [] :=
filter_eq_nil.2 $ assume k hk, not_le_of_gt (lt_of_lt_of_le (mem.1 hk).2 hml)

lemma filter_le_of_le {n m l : ℕ} (hnl : n ≤ l) : (Ico n m).filter (λ x, l ≤ x) = Ico l m :=
begin
  cases le_total l m with hlm hml,
  { rw [← append_consecutive hnl hlm, filter_append,
      filter_le_of_top_le (le_refl l), filter_le_of_le_bot (le_refl l), nil_append] },
  { rw [eq_nil_of_le hml, filter_le_of_top_le hml] }
end

@[simp] lemma filter_le (n m l : ℕ) : (Ico n m).filter (λ x, l ≤ x) = Ico (_root_.max n l) m :=
begin
  cases le_total n l with hnl hln,
  { rw [max_eq_right hnl, filter_le_of_le hnl] },
  { rw [max_eq_left hln, filter_le_of_le_bot hln] }
end

/--
For any natural numbers n, a, and b, one of the following holds:
1. n < a
2. n ≥ b
3. n ∈ Ico a b
-/
lemma trichotomy (n a b : ℕ) : n < a ∨ b ≤ n ∨ n ∈ Ico a b :=
begin
  by_cases h₁ : n < a,
  { left, exact h₁ },
  { right,
    by_cases h₂ : n ∈ Ico a b,
    { right, exact h₂ },
    { left,  simp only [Ico.mem, not_and, not_lt] at *, exact h₂ h₁ }}
end

end Ico
end list
