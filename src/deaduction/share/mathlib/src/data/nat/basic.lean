/-
Copyright (c) 2014 Floris van Doorn. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Floris van Doorn, Leonardo de Moura, Jeremy Avigad, Mario Carneiro
-/
import algebra.ordered_ring
import algebra.order_functions
import init_.data.nat.lemmas

/-!
# Basic operations on the natural numbers

This files has some basic lemmas about natural numbers, definition of the `choice` function,
and extra recursors:

* `le_rec_on`, `le_induction`: recursion and induction principles starting at non-zero numbers.
* `decreasing_induction` : recursion growing downwards.
* `strong_rec'` : recursion based on strong inequalities.
-/

universes u v

attribute [protected] nat.pow_zero nat.pow_succ

instance : canonically_ordered_comm_semiring ℕ :=
{ le_iff_exists_add := assume a b,
  ⟨assume h, let ⟨c, hc⟩ := nat.le.dest h in ⟨c, hc.symm⟩,
    assume ⟨c, hc⟩, hc.symm ▸ nat.le_add_right _ _⟩,
  zero_ne_one       := ne_of_lt zero_lt_one,
  eq_zero_or_eq_zero_of_mul_eq_zero   := assume a b, nat.eq_zero_of_mul_eq_zero,
  bot               := 0,
  bot_le            := nat.zero_le,
  .. (infer_instance : ordered_add_comm_monoid ℕ),
  .. (infer_instance : linear_ordered_semiring ℕ),
  .. (infer_instance : comm_semiring ℕ) }

namespace nat
variables {m n k : ℕ}

-- Sometimes a bare `nat.add` or similar appears as a consequence of unfolding
-- during pattern matching. These lemmas package them back up as typeclass
-- mediated operations.
@[simp] theorem add_def {a b : ℕ} : nat.add a b = a + b := rfl
@[simp] theorem mul_def {a b : ℕ} : nat.mul a b = a * b := rfl

attribute [simp] nat.add_sub_cancel nat.add_sub_cancel_left
attribute [simp] nat.sub_self

@[simp] lemma succ_pos' {n : ℕ} : 0 < succ n := succ_pos n

theorem succ_inj' {n m : ℕ} : succ n = succ m ↔ n = m :=
⟨succ.inj, congr_arg _⟩

theorem succ_injective : function.injective nat.succ := λ x y, succ.inj

theorem succ_le_succ_iff {m n : ℕ} : succ m ≤ succ n ↔ m ≤ n :=
⟨le_of_succ_le_succ, succ_le_succ⟩

lemma zero_max {m : nat} : max 0 m = m :=
max_eq_right (zero_le _)

theorem max_succ_succ {m n : ℕ} :
  max (succ m) (succ n) = succ (max m n) :=
begin
  by_cases h1 : m ≤ n,
  rw [max_eq_right h1, max_eq_right (succ_le_succ h1)],
  { rw not_le at h1, have h2 := le_of_lt h1,
    rw [max_eq_left h2, max_eq_left (succ_le_succ h2)] }
end

lemma not_succ_lt_self {n : ℕ} : ¬succ n < n :=
not_lt_of_ge (nat.le_succ _)

theorem lt_succ_iff {m n : ℕ} : m < succ n ↔ m ≤ n :=
succ_le_succ_iff

lemma succ_le_iff {m n : ℕ} : succ m ≤ n ↔ m < n :=
⟨lt_of_succ_le, succ_le_of_lt⟩

lemma lt_iff_add_one_le {m n : ℕ} : m < n ↔ m + 1 ≤ n :=
by rw succ_le_iff

-- Just a restatement of `nat.lt_succ_iff` using `+1`.
lemma lt_add_one_iff {a b : ℕ} : a < b + 1 ↔ a ≤ b :=
lt_succ_iff

-- A flipped version of `lt_add_one_iff`.
lemma lt_one_add_iff {a b : ℕ} : a < 1 + b ↔ a ≤ b :=
by simp only [add_comm, lt_succ_iff]

-- This is true reflexively, by the definition of `≤` on ℕ,
-- but it's still useful to have, to convince Lean to change the syntactic type.
lemma add_one_le_iff {a b : ℕ} : a + 1 ≤ b ↔ a < b :=
iff.refl _

lemma one_add_le_iff {a b : ℕ} : 1 + a ≤ b ↔ a < b :=
by simp only [add_comm, add_one_le_iff]

theorem of_le_succ {n m : ℕ} (H : n ≤ m.succ) : n ≤ m ∨ n = m.succ :=
(lt_or_eq_of_le H).imp le_of_lt_succ id

/-- Recursion starting at a non-zero number: given a map `C k → C (k+1)` for each `k`,
there is a map from `C n` to each `C m`, `n ≤ m`. -/
@[elab_as_eliminator]
def le_rec_on {C : ℕ → Sort u} {n : ℕ} : Π {m : ℕ}, n ≤ m → (Π {k}, C k → C (k+1)) → C n → C m
| 0     H next x := eq.rec_on (eq_zero_of_le_zero H) x
| (m+1) H next x := or.by_cases (of_le_succ H) (λ h : n ≤ m, next $ le_rec_on h @next x) (λ h : n = m + 1, eq.rec_on h x)

theorem le_rec_on_self {C : ℕ → Sort u} {n} {h : n ≤ n} {next} (x : C n) : (le_rec_on h next x : C n) = x :=
by cases n; unfold le_rec_on or.by_cases; rw [dif_neg n.not_succ_le_self, dif_pos rfl]

theorem le_rec_on_succ {C : ℕ → Sort u} {n m} (h1 : n ≤ m) {h2 : n ≤ m+1} {next} (x : C n) :
  (le_rec_on h2 @next x : C (m+1)) = next (le_rec_on h1 @next x : C m) :=
by conv { to_lhs, rw [le_rec_on, or.by_cases, dif_pos h1] }

theorem le_rec_on_succ' {C : ℕ → Sort u} {n} {h : n ≤ n+1} {next} (x : C n) :
  (le_rec_on h next x : C (n+1)) = next x :=
by rw [le_rec_on_succ (le_refl n), le_rec_on_self]

theorem le_rec_on_trans {C : ℕ → Sort u} {n m k} (hnm : n ≤ m) (hmk : m ≤ k) {next} (x : C n) :
  (le_rec_on (le_trans hnm hmk) @next x : C k) = le_rec_on hmk @next (le_rec_on hnm @next x) :=
begin
  induction hmk with k hmk ih, { rw le_rec_on_self },
  rw [le_rec_on_succ (le_trans hnm hmk), ih, le_rec_on_succ]
end

theorem le_rec_on_succ_left {C : ℕ → Sort u} {n m} (h1 : n ≤ m) (h2 : n+1 ≤ m)
  {next : Π{{k}}, C k → C (k+1)} (x : C n) :
  (le_rec_on h2 next (next x) : C m) = (le_rec_on h1 next x : C m) :=
begin
  rw [subsingleton.elim h1 (le_trans (le_succ n) h2),
      le_rec_on_trans (le_succ n) h2, le_rec_on_succ']
end

theorem le_rec_on_injective {C : ℕ → Sort u} {n m} (hnm : n ≤ m)
  (next : Π n, C n → C (n+1)) (Hnext : ∀ n, function.injective (next n)) :
  function.injective (le_rec_on hnm next) :=
begin
  induction hnm with m hnm ih, { intros x y H, rwa [le_rec_on_self, le_rec_on_self] at H },
  intros x y H, rw [le_rec_on_succ hnm, le_rec_on_succ hnm] at H, exact ih (Hnext _ H)
end

theorem le_rec_on_surjective {C : ℕ → Sort u} {n m} (hnm : n ≤ m)
  (next : Π n, C n → C (n+1)) (Hnext : ∀ n, function.surjective (next n)) :
  function.surjective (le_rec_on hnm next) :=
begin
  induction hnm with m hnm ih, { intros x, use x, rw le_rec_on_self },
  intros x, rcases Hnext _ x with ⟨w, rfl⟩, rcases ih w with ⟨x, rfl⟩, use x, rw le_rec_on_succ
end

theorem pred_eq_of_eq_succ {m n : ℕ} (H : m = n.succ) : m.pred = n := by simp [H]

@[simp] lemma pred_eq_succ_iff {n m : ℕ} : pred n = succ m ↔ n = m + 2 :=
by cases n; split; rintro ⟨⟩; refl

theorem pred_sub (n m : ℕ) : pred n - m = pred (n - m) :=
by rw [← sub_one, nat.sub_sub, one_add]; refl

@[simp]
lemma add_succ_sub_one (n m : ℕ) : (n + succ m) - 1 = n + m :=
by rw [add_succ, succ_sub_one]

@[simp]
lemma succ_add_sub_one (n m : ℕ) : (succ n + m) - 1 = n + m :=
by rw [succ_add, succ_sub_one]

lemma pred_eq_sub_one (n : ℕ) : pred n = n - 1 := rfl

lemma one_le_of_lt {n m : ℕ} (h : n < m) : 1 ≤ m :=
lt_of_le_of_lt (nat.zero_le _) h

lemma le_pred_of_lt {n m : ℕ} (h : m < n) : m ≤ n - 1 :=
nat.sub_le_sub_right h 1

lemma le_of_pred_lt {m n : ℕ} : pred m < n → m ≤ n :=
match m with
| 0 := le_of_lt
| m+1 := id
end

/-- This ensures that `simp` succeeds on `pred (n + 1) = n`. -/
@[simp] lemma pred_one_add (n : ℕ) : pred (1 + n) = n :=
by rw [add_comm, add_one, pred_succ]

theorem pos_iff_ne_zero : 0 < n ↔ n ≠ 0 :=
⟨ne_of_gt, nat.pos_of_ne_zero⟩

lemma one_lt_iff_ne_zero_and_ne_one : ∀ {n : ℕ}, 1 < n ↔ n ≠ 0 ∧ n ≠ 1
| 0     := dec_trivial
| 1     := dec_trivial
| (n+2) := dec_trivial

theorem eq_of_lt_succ_of_not_lt {a b : ℕ} (h1 : a < b + 1) (h2 : ¬ a < b) : a = b :=
have h3 : a ≤ b, from le_of_lt_succ h1,
or.elim (eq_or_lt_of_not_lt h2) (λ h, h) (λ h, absurd h (not_lt_of_ge h3))

protected theorem le_sub_add (n m : ℕ) : n ≤ n - m + m :=
or.elim (le_total n m)
  (assume : n ≤ m, begin rw [sub_eq_zero_of_le this, zero_add], exact this end)
  (assume : m ≤ n, begin rw (nat.sub_add_cancel this) end)

theorem sub_add_eq_max (n m : ℕ) : n - m + m = max n m :=
eq_max (nat.le_sub_add _ _) (le_add_left _ _) $ λ k h₁ h₂,
by rw ← nat.sub_add_cancel h₂; exact
add_le_add_right (nat.sub_le_sub_right h₁ _) _

theorem add_sub_eq_max (n m : ℕ) : n + (m - n) = max n m :=
by rw [add_comm, max_comm, sub_add_eq_max]

theorem sub_add_min (n m : ℕ) : n - m + min n m = n :=
(le_total n m).elim
  (λ h, by rw [min_eq_left h, sub_eq_zero_of_le h, zero_add])
  (λ h, by rw [min_eq_right h, nat.sub_add_cancel h])

protected theorem add_sub_cancel' {n m : ℕ} (h : m ≤ n) : m + (n - m) = n :=
by rw [add_comm, nat.sub_add_cancel h]

protected theorem sub_eq_of_eq_add (h : k = m + n) : k - m = n :=
begin rw [h, nat.add_sub_cancel_left] end

theorem sub_cancel {a b c : ℕ} (h₁ : a ≤ b) (h₂ : a ≤ c) (w : b - a = c - a) : b = c :=
by rw [←nat.sub_add_cancel h₁, ←nat.sub_add_cancel h₂, w]

lemma sub_sub_sub_cancel_right {a b c : ℕ} (h₂ : c ≤ b) : (a - c) - (b - c) = a - b :=
by rw [nat.sub_sub, ←nat.add_sub_assoc h₂, nat.add_sub_cancel_left]

lemma add_sub_cancel_right (n m k : ℕ) : n + (m + k) - k = n + m :=
by { rw [nat.add_sub_assoc, nat.add_sub_cancel], apply k.le_add_left }

protected lemma sub_add_eq_add_sub {a b c : ℕ} (h : b ≤ a) : (a - b) + c = (a + c) - b :=
by rw [add_comm a, nat.add_sub_assoc h, add_comm]

theorem sub_min (n m : ℕ) : n - min n m = n - m :=
nat.sub_eq_of_eq_add $ by rw [add_comm, sub_add_min]

theorem sub_sub_assoc {a b c : ℕ} (h₁ : b ≤ a) (h₂ : c ≤ b) : a - (b - c) = a - b + c :=
(nat.sub_eq_iff_eq_add (le_trans (nat.sub_le _ _) h₁)).2 $
by rw [add_right_comm, add_assoc, nat.sub_add_cancel h₂, nat.sub_add_cancel h₁]

protected theorem lt_of_sub_pos (h : 0 < n - m) : m < n :=
lt_of_not_ge
  (assume : n ≤ m,
    have n - m = 0, from sub_eq_zero_of_le this,
    begin rw this at h, exact lt_irrefl _ h end)

protected theorem lt_of_sub_lt_sub_right : m - k < n - k → m < n :=
lt_imp_lt_of_le_imp_le (λ h, nat.sub_le_sub_right h _)

protected theorem lt_of_sub_lt_sub_left : m - n < m - k → k < n :=
lt_imp_lt_of_le_imp_le (nat.sub_le_sub_left _)

protected theorem sub_lt_self (h₁ : 0 < m) (h₂ : 0 < n) : m - n < m :=
calc
  m - n = succ (pred m) - succ (pred n) : by rw [succ_pred_eq_of_pos h₁, succ_pred_eq_of_pos h₂]
    ... = pred m - pred n               : by rw succ_sub_succ
    ... ≤ pred m                        : sub_le _ _
    ... < succ (pred m)                 : lt_succ_self _
    ... = m                             : succ_pred_eq_of_pos h₁

protected theorem le_sub_right_of_add_le (h : m + k ≤ n) : m ≤ n - k :=
by rw ← nat.add_sub_cancel m k; exact nat.sub_le_sub_right h k

protected theorem le_sub_left_of_add_le (h : k + m ≤ n) : m ≤ n - k :=
nat.le_sub_right_of_add_le (by rwa add_comm at h)

protected theorem lt_sub_right_of_add_lt (h : m + k < n) : m < n - k :=
lt_of_succ_le $ nat.le_sub_right_of_add_le $
by rw succ_add; exact succ_le_of_lt h

protected theorem lt_sub_left_of_add_lt (h : k + m < n) : m < n - k :=
nat.lt_sub_right_of_add_lt (by rwa add_comm at h)

protected theorem add_lt_of_lt_sub_right (h : m < n - k) : m + k < n :=
@nat.lt_of_sub_lt_sub_right _ _ k (by rwa nat.add_sub_cancel)

protected theorem add_lt_of_lt_sub_left (h : m < n - k) : k + m < n :=
by rw add_comm; exact nat.add_lt_of_lt_sub_right h

protected theorem le_add_of_sub_le_right : n - k ≤ m → n ≤ m + k :=
le_imp_le_of_lt_imp_lt nat.lt_sub_right_of_add_lt

protected theorem le_add_of_sub_le_left : n - k ≤ m → n ≤ k + m :=
le_imp_le_of_lt_imp_lt nat.lt_sub_left_of_add_lt

protected theorem lt_add_of_sub_lt_right : n - k < m → n < m + k :=
lt_imp_lt_of_le_imp_le nat.le_sub_right_of_add_le

protected theorem lt_add_of_sub_lt_left : n - k < m → n < k + m :=
lt_imp_lt_of_le_imp_le nat.le_sub_left_of_add_le

protected theorem sub_le_left_of_le_add : n ≤ k + m → n - k ≤ m :=
le_imp_le_of_lt_imp_lt nat.add_lt_of_lt_sub_left

protected theorem sub_le_right_of_le_add : n ≤ m + k → n - k ≤ m :=
le_imp_le_of_lt_imp_lt nat.add_lt_of_lt_sub_right

protected theorem sub_lt_left_iff_lt_add (H : n ≤ k) : k - n < m ↔ k < n + m :=
⟨nat.lt_add_of_sub_lt_left,
 λ h₁,
  have succ k ≤ n + m,   from succ_le_of_lt h₁,
  have succ (k - n) ≤ m, from
    calc succ (k - n) = succ k - n : by rw (succ_sub H)
          ...     ≤ n + m - n      : nat.sub_le_sub_right this n
          ...     = m              : by rw nat.add_sub_cancel_left,
  lt_of_succ_le this⟩

protected theorem le_sub_left_iff_add_le (H : m ≤ k) : n ≤ k - m ↔ m + n ≤ k :=
le_iff_le_iff_lt_iff_lt.2 (nat.sub_lt_left_iff_lt_add H)

protected theorem le_sub_right_iff_add_le (H : n ≤ k) : m ≤ k - n ↔ m + n ≤ k :=
by rw [nat.le_sub_left_iff_add_le H, add_comm]

protected theorem lt_sub_left_iff_add_lt : n < k - m ↔ m + n < k :=
⟨nat.add_lt_of_lt_sub_left, nat.lt_sub_left_of_add_lt⟩

protected theorem lt_sub_right_iff_add_lt : m < k - n ↔ m + n < k :=
by rw [nat.lt_sub_left_iff_add_lt, add_comm]

theorem sub_le_left_iff_le_add : m - n ≤ k ↔ m ≤ n + k :=
le_iff_le_iff_lt_iff_lt.2 nat.lt_sub_left_iff_add_lt

theorem sub_le_right_iff_le_add : m - k ≤ n ↔ m ≤ n + k :=
by rw [nat.sub_le_left_iff_le_add, add_comm]

protected theorem sub_lt_right_iff_lt_add (H : k ≤ m) : m - k < n ↔ m < n + k :=
by rw [nat.sub_lt_left_iff_lt_add H, add_comm]

protected theorem sub_le_sub_left_iff (H : k ≤ m) : m - n ≤ m - k ↔ k ≤ n :=
⟨λ h,
  have k + (m - k) - n ≤ m - k, by rwa nat.add_sub_cancel' H,
  nat.le_of_add_le_add_right (nat.le_add_of_sub_le_left this),
nat.sub_le_sub_left _⟩

protected theorem sub_lt_sub_right_iff (H : k ≤ m) : m - k < n - k ↔ m < n :=
lt_iff_lt_of_le_iff_le (nat.sub_le_sub_right_iff _ _ _ H)

protected theorem sub_lt_sub_left_iff (H : n ≤ m) : m - n < m - k ↔ k < n :=
lt_iff_lt_of_le_iff_le (nat.sub_le_sub_left_iff H)

protected theorem sub_le_iff : m - n ≤ k ↔ m - k ≤ n :=
nat.sub_le_left_iff_le_add.trans nat.sub_le_right_iff_le_add.symm

protected lemma sub_le_self (n m : ℕ) : n - m ≤ n :=
nat.sub_le_left_of_le_add (nat.le_add_left _ _)

protected theorem sub_lt_iff (h₁ : n ≤ m) (h₂ : k ≤ m) : m - n < k ↔ m - k < n :=
(nat.sub_lt_left_iff_lt_add h₁).trans (nat.sub_lt_right_iff_lt_add h₂).symm

lemma pred_le_iff {n m : ℕ} : pred n ≤ m ↔ n ≤ succ m :=
@nat.sub_le_right_iff_le_add n m 1

lemma lt_pred_iff {n m : ℕ} : n < pred m ↔ succ n < m :=
@nat.lt_sub_right_iff_add_lt n 1 m

lemma lt_of_lt_pred {a b : ℕ} (h : a < b - 1) : a < b :=
lt_of_succ_lt (lt_pred_iff.1 h)

protected theorem mul_ne_zero {n m : ℕ} (n0 : n ≠ 0) (m0 : m ≠ 0) : n * m ≠ 0
| nm := (eq_zero_of_mul_eq_zero nm).elim n0 m0

@[simp] protected theorem mul_eq_zero {a b : ℕ} : a * b = 0 ↔ a = 0 ∨ b = 0 :=
iff.intro eq_zero_of_mul_eq_zero (by simp [or_imp_distrib] {contextual := tt})

@[simp] protected theorem zero_eq_mul {a b : ℕ} : 0 = a * b ↔ a = 0 ∨ b = 0 :=
by rw [eq_comm, nat.mul_eq_zero]

lemma eq_zero_of_double_le {a : ℕ} (h : 2 * a ≤ a) : a = 0 :=
nat.eq_zero_of_le_zero $
  by rwa [two_mul, nat.add_le_to_le_sub, nat.sub_self] at h; refl

lemma eq_zero_of_mul_le {a b : ℕ} (hb : 2 ≤ b) (h : b * a ≤ a) : a = 0 :=
eq_zero_of_double_le $ le_trans (nat.mul_le_mul_right _ hb) h

lemma le_mul_of_pos_left {m n : ℕ} (h : 0 < n) : m ≤ n * m :=
begin
  conv {to_lhs, rw [← one_mul(m)]},
  exact mul_le_mul_of_nonneg_right (nat.succ_le_of_lt h) dec_trivial,
end

lemma le_mul_of_pos_right {m n : ℕ} (h : 0 < n) : m ≤ m * n :=
begin
  conv {to_lhs, rw [← mul_one(m)]},
  exact mul_le_mul_of_nonneg_left (nat.succ_le_of_lt h) dec_trivial,
end

theorem two_mul_ne_two_mul_add_one {n m} : 2 * n ≠ 2 * m + 1 :=
mt (congr_arg (%2)) (by rw [add_comm, add_mul_mod_self_left, mul_mod_right]; exact dec_trivial)

/-- Recursion principle based on `<`. -/
@[elab_as_eliminator]
protected def strong_rec' {p : ℕ → Sort u} (H : ∀ n, (∀ m, m < n → p m) → p n) : ∀ (n : ℕ), p n
| n := H n (λ m hm, strong_rec' m)

/-- Recursion principle based on `<` applied to some natural number. -/
@[elab_as_eliminator]
def strong_rec_on' {P : ℕ → Sort*} (n : ℕ) (h : ∀ n, (∀ m, m < n → P m) → P n) : P n :=
nat.strong_rec' h n

theorem strong_rec_on_beta' {P : ℕ → Sort*} {h} {n : ℕ} :
  (strong_rec_on' n h : P n) = h n (λ m hmn, (strong_rec_on' m h : P m)) :=
by { simp only [strong_rec_on'], rw nat.strong_rec' }

attribute [simp] nat.div_self

protected lemma div_le_of_le_mul' {m n : ℕ} {k} (h : m ≤ k * n) : m / k ≤ n :=
(eq_zero_or_pos k).elim
  (λ k0, by rw [k0, nat.div_zero]; apply zero_le)
  (λ k0, (decidable.mul_le_mul_left k0).1 $
    calc k * (m / k)
        ≤ m % k + k * (m / k) : le_add_left _ _
    ... = m                   : mod_add_div _ _
    ... ≤ k * n               : h)

protected lemma div_le_self' (m n : ℕ) : m / n ≤ m :=
(eq_zero_or_pos n).elim
  (λ n0, by rw [n0, nat.div_zero]; apply zero_le)
  (λ n0, nat.div_le_of_le_mul' $ calc
      m = 1 * m : (one_mul _).symm
    ... ≤ n * m : mul_le_mul_right _ n0)

/-- A version of `nat.div_lt_self` using successors, rather than additional hypotheses. -/
lemma div_lt_self' (n b : ℕ) : (n+1)/(b+2) < n+1 :=
nat.div_lt_self (nat.succ_pos n) (nat.succ_lt_succ (nat.succ_pos _))

theorem le_div_iff_mul_le' {x y : ℕ} {k : ℕ} (k0 : 0 < k) : x ≤ y / k ↔ x * k ≤ y :=
begin
  revert x, refine nat.strong_rec' _ y,
  clear y, intros y IH x,
  cases decidable.lt_or_le y k with h h,
  { rw [div_eq_of_lt h],
    cases x with x,
    { simp [zero_mul, zero_le] },
    { rw succ_mul,
      exact iff_of_false (not_succ_le_zero _)
        (not_le_of_lt $ lt_of_lt_of_le h (le_add_left _ _)) } },
  { rw [div_eq_sub_div k0 h],
    cases x with x,
    { simp [zero_mul, zero_le] },
    { rw [← add_one, nat.add_le_add_iff_le_right, succ_mul,
        IH _ (sub_lt_of_pos_le _ _ k0 h), add_le_to_le_sub _ h] } }
end

theorem div_mul_le_self' (m n : ℕ) : m / n * n ≤ m :=
(nat.eq_zero_or_pos n).elim (λ n0, by simp [n0, zero_le]) $ λ n0,
(le_div_iff_mul_le' n0).1 (le_refl _)

theorem div_lt_iff_lt_mul' {x y : ℕ} {k : ℕ} (k0 : 0 < k) : x / k < y ↔ x < y * k :=
lt_iff_lt_of_le_iff_le $ le_div_iff_mul_le' k0

protected theorem div_le_div_right {n m : ℕ} (h : n ≤ m) {k : ℕ} : n / k ≤ m / k :=
(nat.eq_zero_or_pos k).elim (λ k0, by simp [k0]) $ λ hk,
(le_div_iff_mul_le' hk).2 $ le_trans (nat.div_mul_le_self' _ _) h

lemma lt_of_div_lt_div {m n k : ℕ} (h : m / k < n / k) : m < n :=
by_contradiction $ λ h₁, absurd h (not_lt_of_ge (nat.div_le_div_right (not_lt.1 h₁)))

protected theorem eq_mul_of_div_eq_right {a b c : ℕ} (H1 : b ∣ a) (H2 : a / b = c) :
  a = b * c :=
by rw [← H2, nat.mul_div_cancel' H1]

protected theorem div_eq_iff_eq_mul_right {a b c : ℕ} (H : 0 < b) (H' : b ∣ a) :
  a / b = c ↔ a = b * c :=
⟨nat.eq_mul_of_div_eq_right H', nat.div_eq_of_eq_mul_right H⟩

protected theorem div_eq_iff_eq_mul_left {a b c : ℕ} (H : 0 < b) (H' : b ∣ a) :
  a / b = c ↔ a = c * b :=
by rw mul_comm; exact nat.div_eq_iff_eq_mul_right H H'

protected theorem eq_mul_of_div_eq_left {a b c : ℕ} (H1 : b ∣ a) (H2 : a / b = c) :
  a = c * b :=
by rw [mul_comm, nat.eq_mul_of_div_eq_right H1 H2]

protected theorem mul_div_cancel_left' {a b : ℕ} (Hd :  a ∣ b) : a * (b / a) = b :=
by rw [mul_comm,nat.div_mul_cancel Hd]

protected theorem div_mod_unique {n k m d : ℕ} (h : 0 < k) :
  n / k = d ∧ n % k = m ↔ m + k * d = n ∧ m < k :=
⟨λ ⟨e₁, e₂⟩, e₁ ▸ e₂ ▸ ⟨mod_add_div _ _, mod_lt _ h⟩,
 λ ⟨h₁, h₂⟩, h₁ ▸ by rw [add_mul_div_left _ _ h, add_mul_mod_self_left];
   simp [div_eq_of_lt, mod_eq_of_lt, h₂]⟩

lemma two_mul_odd_div_two {n : ℕ} (hn : n % 2 = 1) : 2 * (n / 2) = n - 1 :=
by conv {to_rhs, rw [← nat.mod_add_div n 2, hn, nat.add_sub_cancel_left]}

lemma div_dvd_of_dvd {a b : ℕ} (h : b ∣ a) : (a / b) ∣ a :=
⟨b, (nat.div_mul_cancel h).symm⟩

protected lemma div_pos {a b : ℕ} (hba : b ≤ a) (hb : 0 < b) : 0 < a / b :=
nat.pos_of_ne_zero (λ h, lt_irrefl a
  (calc a = a % b : by simpa [h] using (mod_add_div a b).symm
      ... < b : nat.mod_lt a hb
      ... ≤ a : hba))

protected theorem mul_left_inj {a b c : ℕ} (ha : 0 < a) : b * a = c * a ↔ b = c :=
⟨nat.eq_of_mul_eq_mul_right ha, λ e, e ▸ rfl⟩

protected theorem mul_right_inj {a b c : ℕ} (ha : 0 < a) : a * b = a * c ↔ b = c :=
⟨nat.eq_of_mul_eq_mul_left ha, λ e, e ▸ rfl⟩

protected lemma div_div_self : ∀ {a b : ℕ}, b ∣ a → 0 < a → a / (a / b) = b
| a     0     h₁ h₂ := by rw eq_zero_of_zero_dvd h₁; refl
| 0     b     h₁ h₂ := absurd h₂ dec_trivial
| (a+1) (b+1) h₁ h₂ :=
(nat.mul_left_inj (nat.div_pos (le_of_dvd (succ_pos a) h₁) (succ_pos b))).1 $
  by rw [nat.div_mul_cancel (div_dvd_of_dvd h₁), nat.mul_div_cancel' h₁]

protected lemma div_lt_of_lt_mul {m n k : ℕ} (h : m < n * k) : m / n < k :=
lt_of_mul_lt_mul_left
  (calc n * (m / n) ≤ m % n + n * (m / n) : nat.le_add_left _ _
    ... = m : mod_add_div _ _
    ... < n * k : h)
  (nat.zero_le n)

lemma lt_mul_of_div_lt {a b c : ℕ} (h : a / c < b) (w : 0 < c) : a < b * c :=
lt_of_not_ge $ not_le_of_gt h ∘ (nat.le_div_iff_mul_le _ _ w).2

protected lemma div_eq_zero_iff {a b : ℕ} (hb : 0 < b) : a / b = 0 ↔ a < b :=
⟨λ h, by rw [← mod_add_div a b, h, mul_zero, add_zero]; exact mod_lt _ hb,
  λ h, by rw [← nat.mul_right_inj hb, ← @add_left_cancel_iff _ _ (a % b), mod_add_div,
    mod_eq_of_lt h, mul_zero, add_zero]⟩

lemma eq_zero_of_le_div {a b : ℕ} (hb : 2 ≤ b) (h : a ≤ a / b) : a = 0 :=
eq_zero_of_mul_le hb $
  by rw mul_comm; exact (nat.le_div_iff_mul_le' (lt_of_lt_of_le dec_trivial hb)).1 h

lemma mul_div_le_mul_div_assoc (a b c : ℕ) : a * (b / c) ≤ (a * b) / c :=
if hc0 : c = 0 then by simp [hc0]
else (nat.le_div_iff_mul_le _ _ (nat.pos_of_ne_zero hc0)).2
  (by rw [mul_assoc]; exact mul_le_mul_left _ (nat.div_mul_le_self _ _))

lemma div_mul_div_le_div (a b c : ℕ) : ((a / c) * b) / a ≤ b / c :=
if ha0 : a = 0 then by simp [ha0]
else calc a / c * b / a ≤ b * a / c / a :
    nat.div_le_div_right (by rw [mul_comm];
        exact mul_div_le_mul_div_assoc _ _ _)
  ... = b / c : by rw [nat.div_div_eq_div_mul, mul_comm b, mul_comm c,
      nat.mul_div_mul _ _ (nat.pos_of_ne_zero ha0)]

lemma eq_zero_of_le_half {a : ℕ} (h : a ≤ a / 2) : a = 0 :=
eq_zero_of_le_div (le_refl _) h

lemma mod_mul_right_div_self (a b c : ℕ) : a % (b * c) / b = (a / b) % c :=
if hb : b = 0 then by simp [hb] else if hc : c = 0 then by simp [hc]
else by conv {to_rhs, rw ← mod_add_div a (b * c)};
rw [mul_assoc, nat.add_mul_div_left _ _ (nat.pos_of_ne_zero hb), add_mul_mod_self_left,
  mod_eq_of_lt (nat.div_lt_of_lt_mul (mod_lt _ (mul_pos (nat.pos_of_ne_zero hb) (nat.pos_of_ne_zero hc))))]

lemma mod_mul_left_div_self (a b c : ℕ) : a % (c * b) / b = (a / b) % c :=
by rw [mul_comm c, mod_mul_right_div_self]

/- The `n+1`-st triangle number is `n` more than the `n`-th triangle number -/
lemma triangle_succ (n : ℕ) : (n + 1) * ((n + 1) - 1) / 2 = n * (n - 1) / 2 + n :=
begin
  rw [← add_mul_div_left, mul_comm 2 n, ← mul_add, nat.add_sub_cancel, mul_comm],
  cases n; refl, apply zero_lt_succ
end

@[simp] protected theorem dvd_one {n : ℕ} : n ∣ 1 ↔ n = 1 :=
⟨eq_one_of_dvd_one, λ e, e.symm ▸ dvd_refl _⟩

protected theorem dvd_add_left {k m n : ℕ} (h : k ∣ n) : k ∣ m + n ↔ k ∣ m :=
(nat.dvd_add_iff_left h).symm

protected theorem dvd_add_right {k m n : ℕ} (h : k ∣ m) : k ∣ m + n ↔ k ∣ n :=
(nat.dvd_add_iff_right h).symm

/-- A natural number m divides the sum m + n if and only if m divides b.-/
@[simp] protected lemma dvd_add_self_left {m n : ℕ} :
  m ∣ m + n ↔ m ∣ n :=
nat.dvd_add_right (dvd_refl m)

/-- A natural number m divides the sum n + m if and only if m divides b.-/
@[simp] protected lemma dvd_add_self_right {m n : ℕ} :
  m ∣ n + m ↔ m ∣ n :=
nat.dvd_add_left (dvd_refl m)

protected theorem mul_dvd_mul_iff_left {a b c : ℕ} (ha : 0 < a) : a * b ∣ a * c ↔ b ∣ c :=
exists_congr $ λ d, by rw [mul_assoc, nat.mul_right_inj ha]

protected theorem mul_dvd_mul_iff_right {a b c : ℕ} (hc : 0 < c) : a * c ∣ b * c ↔ a ∣ b :=
exists_congr $ λ d, by rw [mul_right_comm, nat.mul_left_inj hc]

lemma succ_div : ∀ (a b : ℕ), (a + 1) / b =
  a / b + if b ∣ a + 1 then 1 else 0
| a     0     := by simp
| 0     1     := rfl
| 0     (b+2) := have hb2 : b + 2 > 1, from dec_trivial,
  by simp [ne_of_gt hb2, div_eq_of_lt hb2]
| (a+1) (b+1) := begin
  rw [nat.div_def], conv_rhs { rw nat.div_def },
  by_cases hb_eq_a : b = a + 1,
  { simp [hb_eq_a, le_refl] },
  by_cases hb_le_a1 : b ≤ a + 1,
  { have hb_le_a : b ≤ a, from le_of_lt_succ (lt_of_le_of_ne hb_le_a1 hb_eq_a),
    have h₁ : (0 < b + 1 ∧ b + 1 ≤ a + 1 + 1),
      from ⟨succ_pos _, (add_le_add_iff_right _).2 hb_le_a1⟩,
    have h₂ : (0 < b + 1 ∧ b + 1 ≤ a + 1),
      from ⟨succ_pos _, (add_le_add_iff_right _).2 hb_le_a⟩,
    have dvd_iff : b + 1 ∣ a - b + 1 ↔  b + 1 ∣ a + 1 + 1,
    { rw [nat.dvd_add_iff_left (dvd_refl (b + 1)),
        ← nat.add_sub_add_right a 1 b, add_comm (_ - _), add_assoc,
        nat.sub_add_cancel (succ_le_succ hb_le_a), add_comm 1] },
    have wf : a - b < a + 1, from lt_succ_of_le (nat.sub_le_self _ _),
    rw [if_pos h₁, if_pos h₂, nat.add_sub_add_right, nat.sub_add_comm hb_le_a,
      by exact have _ := wf, succ_div (a - b),
      nat.add_sub_add_right],
    simp [dvd_iff, succ_eq_add_one, add_comm 1, add_assoc] },
  { have hba : ¬ b ≤ a,
      from not_le_of_gt (lt_trans (lt_succ_self a) (lt_of_not_ge hb_le_a1)),
    have hb_dvd_a : ¬ b + 1 ∣ a + 2,
      from λ h, hb_le_a1 (le_of_succ_le_succ (le_of_dvd (succ_pos _) h)),
    simp [hba, hb_le_a1, hb_dvd_a], }
end

lemma succ_div_of_dvd {a b : ℕ} (hba : b ∣ a + 1) :
  (a + 1) / b = a / b + 1 :=
by rw [succ_div, if_pos hba]

lemma succ_div_of_not_dvd {a b : ℕ} (hba : ¬ b ∣ a + 1) :
  (a + 1) / b = a / b :=
by rw [succ_div, if_neg hba, add_zero]

@[simp] theorem mod_mod_of_dvd (n : nat) {m k : nat} (h : m ∣ k) : n % k % m = n % m :=
begin
  conv { to_rhs, rw ←mod_add_div n k },
  rcases h with ⟨t, rfl⟩, rw [mul_assoc, add_mul_mod_self_left]
end

@[simp] theorem mod_mod (a n : ℕ) : (a % n) % n = a % n :=
(eq_zero_or_pos n).elim
  (λ n0, by simp [n0])
  (λ npos, mod_eq_of_lt (mod_lt _ npos))

/--  If `a` and `b` are equal mod `c`, `a - b` is zero mod `c`. -/
lemma sub_mod_eq_zero_of_mod_eq {a b c : ℕ} (h : a % c = b % c) : (a - b) % c = 0 :=
by rw [←nat.mod_add_div a c, ←nat.mod_add_div b c, ←h, ←nat.sub_sub, nat.add_sub_cancel_left,
       ←nat.mul_sub_left_distrib, nat.mul_mod_right]

lemma dvd_sub_mod (k : ℕ) : n ∣ (k - (k % n)) :=
⟨k / n, nat.sub_eq_of_eq_add (nat.mod_add_div k n).symm⟩

@[simp] theorem mod_add_mod (m n k : ℕ) : (m % n + k) % n = (m + k) % n :=
by have := (add_mul_mod_self_left (m % n + k) n (m / n)).symm;
   rwa [add_right_comm, mod_add_div] at this

@[simp] theorem add_mod_mod (m n k : ℕ) : (m + n % k) % k = (m + n) % k :=
by rw [add_comm, mod_add_mod, add_comm]

lemma add_mod (a b n : ℕ) : (a + b) % n = ((a % n) + (b % n)) % n :=
by rw [add_mod_mod, mod_add_mod]

theorem add_mod_eq_add_mod_right {m n k : ℕ} (i : ℕ) (H : m % n = k % n) :
  (m + i) % n = (k + i) % n :=
by rw [← mod_add_mod, ← mod_add_mod k, H]

theorem add_mod_eq_add_mod_left {m n k : ℕ} (i : ℕ) (H : m % n = k % n) :
  (i + m) % n = (i + k) % n :=
by rw [add_comm, add_mod_eq_add_mod_right _ H, add_comm]

lemma mul_mod (a b n : ℕ) : (a * b) % n = ((a % n) * (b % n)) % n :=
begin
  conv_lhs {
    rw [←mod_add_div a n, ←mod_add_div b n, right_distrib, left_distrib, left_distrib,
        mul_assoc, mul_assoc, ←left_distrib n _ _, add_mul_mod_self_left,
        mul_comm _ (n * (b / n)), mul_assoc, add_mul_mod_self_left] }
end

theorem add_pos_left {m : ℕ} (h : 0 < m) (n : ℕ) : 0 < m + n :=
calc
  m + n > 0 + n : nat.add_lt_add_right h n
    ... = n     : nat.zero_add n
    ... ≥ 0     : zero_le n

theorem add_pos_right (m : ℕ) {n : ℕ} (h : 0 < n) : 0 < m + n :=
begin rw add_comm, exact add_pos_left h m end

theorem add_pos_iff_pos_or_pos (m n : ℕ) : 0 < m + n ↔ 0 < m ∨ 0 < n :=
iff.intro
  begin
    intro h,
    cases m with m,
    {simp [zero_add] at h, exact or.inr h},
    exact or.inl (succ_pos _)
  end
  begin
    intro h, cases h with mpos npos,
    { apply add_pos_left mpos },
    apply add_pos_right _ npos
  end

lemma add_eq_one_iff : ∀ {a b : ℕ}, a + b = 1 ↔ (a = 0 ∧ b = 1) ∨ (a = 1 ∧ b = 0)
| 0     0     := dec_trivial
| 0     1     := dec_trivial
| 1     0     := dec_trivial
| 1     1     := dec_trivial
| (a+2) _     := by rw add_right_comm; exact dec_trivial
| _     (b+2) := by rw [← add_assoc]; simp only [nat.succ_inj', nat.succ_ne_zero]; simp

lemma mul_eq_one_iff : ∀ {a b : ℕ}, a * b = 1 ↔ a = 1 ∧ b = 1
| 0     0     := dec_trivial
| 0     1     := dec_trivial
| 1     0     := dec_trivial
| (a+2) 0     := by simp
| 0     (b+2) := by simp
| (a+1) (b+1) := ⟨λ h, by simp only [add_mul, mul_add, mul_add, one_mul, mul_one,
    (add_assoc _ _ _).symm, nat.succ_inj', add_eq_zero_iff] at h; simp [h.1.2, h.2],
  by clear_aux_decl; finish⟩

lemma mul_right_eq_self_iff {a b : ℕ} (ha : 0 < a) : a * b = a ↔ b = 1 :=
suffices a * b = a * 1 ↔ b = 1, by rwa mul_one at this,
nat.mul_right_inj ha

lemma mul_left_eq_self_iff {a b : ℕ} (hb : 0 < b) : a * b = b ↔ a = 1 :=
by rw [mul_comm, nat.mul_right_eq_self_iff hb]

lemma lt_succ_iff_lt_or_eq {n i : ℕ} : n < i.succ ↔ (n < i ∨ n = i) :=
lt_succ_iff.trans le_iff_lt_or_eq

theorem le_zero_iff {i : ℕ} : i ≤ 0 ↔ i = 0 :=
⟨nat.eq_zero_of_le_zero, assume h, h ▸ le_refl i⟩

theorem le_add_one_iff {i j : ℕ} : i ≤ j + 1 ↔ (i ≤ j ∨ i = j + 1) :=
⟨assume h,
  match nat.eq_or_lt_of_le h with
  | or.inl h := or.inr h
  | or.inr h := or.inl $ nat.le_of_succ_le_succ h
  end,
  or.rec (assume h, le_trans h $ nat.le_add_right _ _) le_of_eq⟩

theorem mul_self_inj {n m : ℕ} : n * n = m * m ↔ n = m :=
le_antisymm_iff.trans (le_antisymm_iff.trans
  (and_congr mul_self_le_mul_self_iff mul_self_le_mul_self_iff)).symm

section facts
-- Inject some simple facts into the typeclass system.
-- This `fact` should not be confused with the factorial function `nat.fact`!

instance succ_pos'' (n : ℕ) : _root_.fact (0 < n.succ) := n.succ_pos

instance pos_of_one_lt (n : ℕ) [h : fact (1 < n)] : fact (0 < n) :=
lt_trans zero_lt_one h

end facts

instance decidable_ball_lt (n : nat) (P : Π k < n, Prop) :
  ∀ [H : ∀ n h, decidable (P n h)], decidable (∀ n h, P n h) :=
begin
  induction n with n IH; intro; resetI,
  { exact is_true (λ n, dec_trivial) },
  cases IH (λ k h, P k (lt_succ_of_lt h)) with h,
  { refine is_false (mt _ h), intros hn k h, apply hn },
  by_cases p : P n (lt_succ_self n),
  { exact is_true (λ k h',
     (lt_or_eq_of_le $ le_of_lt_succ h').elim (h _)
       (λ e, match k, e, h' with _, rfl, h := p end)) },
  { exact is_false (mt (λ hn, hn _ _) p) }
end

instance decidable_forall_fin {n : ℕ} (P : fin n → Prop)
  [H : decidable_pred P] : decidable (∀ i, P i) :=
decidable_of_iff (∀ k h, P ⟨k, h⟩) ⟨λ a ⟨k, h⟩, a k h, λ a k h, a ⟨k, h⟩⟩

instance decidable_ball_le (n : ℕ) (P : Π k ≤ n, Prop)
  [H : ∀ n h, decidable (P n h)] : decidable (∀ n h, P n h) :=
decidable_of_iff (∀ k (h : k < succ n), P k (le_of_lt_succ h))
⟨λ a k h, a k (lt_succ_of_le h), λ a k h, a k _⟩

instance decidable_lo_hi (lo hi : ℕ) (P : ℕ → Prop) [H : decidable_pred P] : decidable (∀x, lo ≤ x → x < hi → P x) :=
decidable_of_iff (∀ x < hi - lo, P (lo + x))
⟨λal x hl hh, by have := al (x - lo) (lt_of_not_ge $
  (not_congr (nat.sub_le_sub_right_iff _ _ _ hl)).2 $ not_le_of_gt hh);
  rwa [nat.add_sub_of_le hl] at this,
λal x h, al _ (nat.le_add_right _ _) (nat.add_lt_of_lt_sub_left h)⟩

instance decidable_lo_hi_le (lo hi : ℕ) (P : ℕ → Prop) [H : decidable_pred P] : decidable (∀x, lo ≤ x → x ≤ hi → P x) :=
decidable_of_iff (∀x, lo ≤ x → x < hi + 1 → P x) $
ball_congr $ λ x hl, imp_congr lt_succ_iff iff.rfl

protected theorem bit0_le {n m : ℕ} (h : n ≤ m) : bit0 n ≤ bit0 m :=
add_le_add h h

protected theorem bit1_le {n m : ℕ} (h : n ≤ m) : bit1 n ≤ bit1 m :=
succ_le_succ (add_le_add h h)

theorem bit_le : ∀ (b : bool) {n m : ℕ}, n ≤ m → bit b n ≤ bit b m
| tt n m h := nat.bit1_le h
| ff n m h := nat.bit0_le h

theorem bit_ne_zero (b) {n} (h : n ≠ 0) : bit b n ≠ 0 :=
by cases b; [exact nat.bit0_ne_zero h, exact nat.bit1_ne_zero _]

theorem bit0_le_bit : ∀ (b) {m n : ℕ}, m ≤ n → bit0 m ≤ bit b n
| tt m n h := le_of_lt $ nat.bit0_lt_bit1 h
| ff m n h := nat.bit0_le h

theorem bit_le_bit1 : ∀ (b) {m n : ℕ}, m ≤ n → bit b m ≤ bit1 n
| ff m n h := le_of_lt $ nat.bit0_lt_bit1 h
| tt m n h := nat.bit1_le h

theorem bit_lt_bit0 : ∀ (b) {n m : ℕ}, n < m → bit b n < bit0 m
| tt n m h := nat.bit1_lt_bit0 h
| ff n m h := nat.bit0_lt h

theorem bit_lt_bit (a b) {n m : ℕ} (h : n < m) : bit a n < bit b m :=
lt_of_lt_of_le (bit_lt_bit0 _ h) (bit0_le_bit _ (le_refl _))

@[simp] lemma bit0_le_bit1_iff : bit0 k ≤ bit1 n ↔ k ≤ n :=
⟨λ h, by rwa [← nat.lt_succ_iff, n.bit1_eq_succ_bit0, ← n.bit0_succ_eq,
  bit0_lt_bit0, nat.lt_succ_iff] at h, λ h, le_of_lt (nat.bit0_lt_bit1 h)⟩

@[simp] lemma bit0_lt_bit1_iff : bit0 k < bit1 n ↔ k ≤ n :=
⟨λ h, bit0_le_bit1_iff.1 (le_of_lt h), nat.bit0_lt_bit1⟩

@[simp] lemma bit1_le_bit0_iff : bit1 k ≤ bit0 n ↔ k < n :=
⟨λ h, by rwa [k.bit1_eq_succ_bit0, succ_le_iff, bit0_lt_bit0] at h,
  λ h, le_of_lt (nat.bit1_lt_bit0 h)⟩

@[simp] lemma bit1_lt_bit0_iff : bit1 k < bit0 n ↔ k < n :=
⟨λ h, bit1_le_bit0_iff.1 (le_of_lt h), nat.bit1_lt_bit0⟩

@[simp] lemma one_le_bit0_iff : 1 ≤ bit0 n ↔ 0 < n :=
by { convert bit1_le_bit0_iff, refl, }

@[simp] lemma one_lt_bit0_iff : 1 < bit0 n ↔ 1 ≤ n :=
by { convert bit1_lt_bit0_iff, refl, }

@[simp] lemma bit_le_bit_iff : ∀ {b : bool}, bit b k ≤ bit b n ↔ k ≤ n
| ff := bit0_le_bit0
| tt := bit1_le_bit1

@[simp] lemma bit_lt_bit_iff : ∀ {b : bool}, bit b k < bit b n ↔ k < n
| ff := bit0_lt_bit0
| tt := bit1_lt_bit1

@[simp] lemma bit_le_bit1_iff : ∀ {b : bool}, bit b k ≤ bit1 n ↔ k ≤ n
| ff := bit0_le_bit1_iff
| tt := bit1_le_bit1

lemma pos_of_bit0_pos {n : ℕ} (h : 0 < bit0 n) : 0 < n :=
by { cases n, cases h, apply succ_pos, }

/-- Define a function on `ℕ` depending on parity of the argument. -/
@[elab_as_eliminator]
def bit_cases {C : ℕ → Sort u} (H : Π b n, C (bit b n)) (n : ℕ) : C n :=
eq.rec_on n.bit_decomp (H (bodd n) (div2 n))

/- partial subtraction -/

/-- Partial predecessor operation. Returns `ppred n = some m`
  if `n = m + 1`, otherwise `none`. -/
@[simp] def ppred : ℕ → option ℕ
| 0     := none
| (n+1) := some n

/-- Partial subtraction operation. Returns `psub m n = some k`
  if `m = n + k`, otherwise `none`. -/
@[simp] def psub (m : ℕ) : ℕ → option ℕ
| 0     := some m
| (n+1) := psub n >>= ppred

theorem pred_eq_ppred (n : ℕ) : pred n = (ppred n).get_or_else 0 :=
by cases n; refl

theorem sub_eq_psub (m : ℕ) : ∀ n, m - n = (psub m n).get_or_else 0
| 0     := rfl
| (n+1) := (pred_eq_ppred (m-n)).trans $
  by rw [sub_eq_psub, psub]; cases psub m n; refl

@[simp] theorem ppred_eq_some {m : ℕ} : ∀ {n}, ppred n = some m ↔ succ m = n
| 0     := by split; intro h; contradiction
| (n+1) := by dsimp; split; intro h; injection h; subst n

@[simp] theorem ppred_eq_none : ∀ {n : ℕ}, ppred n = none ↔ n = 0
| 0     := by simp
| (n+1) := by dsimp; split; contradiction

theorem psub_eq_some {m : ℕ} : ∀ {n k}, psub m n = some k ↔ k + n = m
| 0     k := by simp [eq_comm]
| (n+1) k :=
  begin
    dsimp,
    apply option.bind_eq_some.trans,
    simp [psub_eq_some, add_comm, add_left_comm, nat.succ_eq_add_one]
  end

theorem psub_eq_none (m n : ℕ) : psub m n = none ↔ m < n :=
begin
  cases s : psub m n; simp [eq_comm],
  { show m < n, refine lt_of_not_ge (λ h, _),
    cases le.dest h with k e,
    injection s.symm.trans (psub_eq_some.2 $ (add_comm _ _).trans e) },
  { show n ≤ m, rw ← psub_eq_some.1 s, apply le_add_left }
end

theorem ppred_eq_pred {n} (h : 0 < n) : ppred n = some (pred n) :=
ppred_eq_some.2 $ succ_pred_eq_of_pos h

theorem psub_eq_sub {m n} (h : n ≤ m) : psub m n = some (m - n) :=
psub_eq_some.2 $ nat.sub_add_cancel h

theorem psub_add (m n k) : psub m (n + k) = do x ← psub m n, psub x k :=
by induction k; simp [*, add_succ, bind_assoc]

/- pow -/

attribute [simp] nat.pow_zero nat.pow_one

@[simp] lemma one_pow : ∀ n : ℕ, 1 ^ n = 1
| 0 := rfl
| (k+1) := show 1^k * 1 = 1, by rw [mul_one, one_pow]

theorem pow_add (a m n : ℕ) : a^(m + n) = a^m * a^n :=
by induction n; simp [*, nat.pow_succ, mul_assoc]

theorem pow_two (a : ℕ) : a ^ 2 = a * a := show (1 * a) * a = _, by rw one_mul

theorem pow_dvd_pow (a : ℕ) {m n : ℕ} (h : m ≤ n) : a^m ∣ a^n :=
by rw [← nat.add_sub_cancel' h, pow_add]; apply dvd_mul_right

theorem pow_dvd_pow_of_dvd {a b : ℕ} (h : a ∣ b) : ∀ n:ℕ, a^n ∣ b^n
| 0     := dvd_refl _
| (n+1) := mul_dvd_mul (pow_dvd_pow_of_dvd n) h

theorem mul_pow (a b n : ℕ) : (a * b) ^ n = a ^ n * b ^ n :=
by induction n; simp [*, nat.pow_succ, mul_comm, mul_assoc, mul_left_comm]

protected theorem pow_mul (a b n : ℕ) : n ^ (a * b) = (n ^ a) ^ b :=
by induction b; simp [*, nat.succ_eq_add_one, nat.pow_add, mul_add, mul_comm]

theorem pow_pos {p : ℕ} (hp : 0 < p) : ∀ n : ℕ, 0 < p ^ n
| 0 := by simp
| (k+1) := mul_pos (pow_pos _) hp

lemma pow_eq_mul_pow_sub (p : ℕ) {m n : ℕ} (h : m ≤ n) : p ^ m * p ^ (n - m)  = p ^ n :=
by rw [←nat.pow_add, nat.add_sub_cancel' h]

lemma pow_lt_pow_succ {p : ℕ} (h : 1 < p) (n : ℕ) : p^n < p^(n+1) :=
suffices p^n*1 < p^n*p, by simpa,
nat.mul_lt_mul_of_pos_left h (nat.pow_pos (lt_of_succ_lt h) n)

lemma lt_pow_self {p : ℕ} (h : 1 < p) : ∀ n : ℕ, n < p ^ n
| 0 := by simp [zero_lt_one]
| (n+1) := calc
  n + 1 < p^n + 1 : nat.add_lt_add_right (lt_pow_self _) _
    ... ≤ p ^ (n+1) : pow_lt_pow_succ h _

lemma lt_two_pow (n : ℕ) : n < 2^n :=
lt_pow_self dec_trivial n

lemma one_le_pow (n m : ℕ) (h : 0 < m) : 1 ≤ m^n :=
one_pow n ▸ pow_le_pow_of_le_left h n
lemma one_le_pow' (n m : ℕ) : 1 ≤ (m+1)^n := one_le_pow n (m+1) (succ_pos m)

lemma one_le_two_pow (n : ℕ) : 1 ≤ 2^n := one_le_pow n 2 dec_trivial

lemma one_lt_pow (n m : ℕ) (h₀ : 0 < n) (h₁ : 1 < m) : 1 < m^n :=
one_pow n ▸ pow_lt_pow_of_lt_left h₁ h₀
lemma one_lt_pow' (n m : ℕ) : 1 < (m+2)^(n+1) :=
one_lt_pow (n+1) (m+2) (succ_pos n) (nat.lt_of_sub_eq_succ rfl)

lemma one_lt_two_pow (n : ℕ) (h₀ : 0 < n) : 1 < 2^n := one_lt_pow n 2 h₀ dec_trivial
lemma one_lt_two_pow' (n : ℕ) : 1 < 2^(n+1) := one_lt_pow (n+1) 2 (succ_pos n) dec_trivial

lemma pow_right_strict_mono {x : ℕ} (k : 2 ≤ x) : strict_mono (nat.pow x) :=
λ _ _, pow_lt_pow_of_lt_right k

lemma pow_le_iff_le_right {x m n : ℕ} (k : 2 ≤ x) : x^m ≤ x^n ↔ m ≤ n :=
strict_mono.le_iff_le (pow_right_strict_mono k)

lemma pow_lt_iff_lt_right {x m n : ℕ} (k : 2 ≤ x) : x^m < x^n ↔ m < n :=
strict_mono.lt_iff_lt (pow_right_strict_mono k)

lemma pow_right_injective {x : ℕ} (k : 2 ≤ x) : function.injective (nat.pow x) :=
strict_mono.injective (pow_right_strict_mono k)

lemma pow_dvd_pow_iff_pow_le_pow {k l : ℕ} : Π {x : ℕ} (w : 0 < x), x^k ∣ x^l ↔ x^k ≤ x^l
| (x+1) w :=
begin
  split,
  { intro a, exact le_of_dvd (pow_pos (succ_pos x) l) a, },
  { intro a, cases x with x,
    { simp only [one_pow], },
    { have le := (pow_le_iff_le_right (le_add_left _ _)).mp a,
      use (x+2)^(l-k),
      rw [←nat.pow_add, add_comm k, nat.sub_add_cancel le], } }
end

/-- If `1 < x`, then `x^k` divides `x^l` if and only if `k` is at most `l`. -/
lemma pow_dvd_pow_iff_le_right {x k l : ℕ} (w : 1 < x) : x^k ∣ x^l ↔ k ≤ l :=
by rw [pow_dvd_pow_iff_pow_le_pow (lt_of_succ_lt w), pow_le_iff_le_right w]

lemma pow_dvd_pow_iff_le_right' {b k l : ℕ} : (b+2)^k ∣ (b+2)^l ↔ k ≤ l :=
pow_dvd_pow_iff_le_right (nat.lt_of_sub_eq_succ rfl)

lemma pow_left_strict_mono {m : ℕ} (k : 1 ≤ m) : strict_mono (λ (x : ℕ), x^m) :=
λ _ _ h, pow_lt_pow_of_lt_left h k

lemma pow_le_iff_le_left {m x y : ℕ} (k : 1 ≤ m) : x^m ≤ y^m ↔ x ≤ y :=
strict_mono.le_iff_le (pow_left_strict_mono k)

lemma pow_lt_iff_lt_left {m x y : ℕ} (k : 1 ≤ m) : x^m < y^m ↔ x < y :=
strict_mono.lt_iff_lt (pow_left_strict_mono k)

lemma pow_left_injective {m : ℕ} (k : 1 ≤ m) : function.injective (λ (x : ℕ), x^m) :=
strict_mono.injective (pow_left_strict_mono k)

lemma not_pos_pow_dvd : ∀ {p k : ℕ} (hp : 1 < p) (hk : 1 < k), ¬ p^k ∣ p
| (succ p) (succ k) hp hk h :=
  have (succ p)^k * succ p ∣ 1 * succ p, by simpa,
  have (succ p) ^ k ∣ 1, from dvd_of_mul_dvd_mul_right (succ_pos _) this,
  have he : (succ p) ^ k = 1, from eq_one_of_dvd_one this,
  have k < (succ p) ^ k, from lt_pow_self hp k,
  have k < 1, by rwa [he] at this,
  have k = 0, from eq_zero_of_le_zero $ le_of_lt_succ this,
  have 1 < 1, by rwa [this] at hk,
  absurd this dec_trivial

@[simp] theorem bodd_div2_eq (n : ℕ) : bodd_div2 n = (bodd n, div2 n) :=
by unfold bodd div2; cases bodd_div2 n; refl

@[simp] lemma bodd_bit0 (n) : bodd (bit0 n) = ff := bodd_bit ff n
@[simp] lemma bodd_bit1 (n) : bodd (bit1 n) = tt := bodd_bit tt n

@[simp] lemma div2_bit0 (n) : div2 (bit0 n) = n := div2_bit ff n
@[simp] lemma div2_bit1 (n) : div2 (bit1 n) = n := div2_bit tt n

/- size and shift -/

theorem shiftl'_ne_zero_left (b) {m} (h : m ≠ 0) (n) : shiftl' b m n ≠ 0 :=
by induction n; simp [shiftl', bit_ne_zero, *]

theorem shiftl'_tt_ne_zero (m) : ∀ {n} (h : n ≠ 0), shiftl' tt m n ≠ 0
| 0        h := absurd rfl h
| (succ n) _ := nat.bit1_ne_zero _

@[simp] theorem size_zero : size 0 = 0 := rfl

@[simp] theorem size_bit {b n} (h : bit b n ≠ 0) : size (bit b n) = succ (size n) :=
begin
  rw size,
  conv { to_lhs, rw [binary_rec], simp [h] },
  rw div2_bit,
end

@[simp] theorem size_bit0 {n} (h : n ≠ 0) : size (bit0 n) = succ (size n) :=
@size_bit ff n (nat.bit0_ne_zero h)

@[simp] theorem size_bit1 (n) : size (bit1 n) = succ (size n) :=
@size_bit tt n (nat.bit1_ne_zero n)

@[simp] theorem size_one : size 1 = 1 := by apply size_bit1 0

@[simp] theorem size_shiftl' {b m n} (h : shiftl' b m n ≠ 0) :
  size (shiftl' b m n) = size m + n :=
begin
  induction n with n IH; simp [shiftl'] at h ⊢,
  rw [size_bit h, nat.add_succ],
  by_cases s0 : shiftl' b m n = 0; [skip, rw [IH s0]],
  rw s0 at h ⊢,
  cases b, {exact absurd rfl h},
  have : shiftl' tt m n + 1 = 1 := congr_arg (+1) s0,
  rw [shiftl'_tt_eq_mul_pow] at this,
  have m0 := succ.inj (eq_one_of_dvd_one ⟨_, this.symm⟩),
  subst m0,
  simp at this,
  have : n = 0 := eq_zero_of_le_zero (le_of_not_gt $ λ hn,
    ne_of_gt (pow_lt_pow_of_lt_right dec_trivial hn) this),
  subst n, refl
end

@[simp] theorem size_shiftl {m} (h : m ≠ 0) (n) :
  size (shiftl m n) = size m + n :=
size_shiftl' (shiftl'_ne_zero_left _ h _)

theorem lt_size_self (n : ℕ) : n < 2^size n :=
begin
  rw [← one_shiftl],
  have : ∀ {n}, n = 0 → n < shiftl 1 (size n) :=
    λ n e, by subst e; exact dec_trivial,
  apply binary_rec _ _ n, {apply this rfl},
  intros b n IH,
  by_cases bit b n = 0, {apply this h},
  rw [size_bit h, shiftl_succ],
  exact bit_lt_bit0 _ IH
end

theorem size_le {m n : ℕ} : size m ≤ n ↔ m < 2^n :=
⟨λ h, lt_of_lt_of_le (lt_size_self _) (pow_le_pow_of_le_right dec_trivial h),
begin
  rw [← one_shiftl], revert n,
  apply binary_rec _ _ m,
  { intros n h, apply zero_le },
  { intros b m IH n h,
    by_cases e : bit b m = 0, { rw e, apply zero_le },
    rw [size_bit e],
    cases n with n,
    { exact e.elim (eq_zero_of_le_zero (le_of_lt_succ h)) },
    { apply succ_le_succ (IH _),
      apply lt_imp_lt_of_le_imp_le (λ h', bit0_le_bit _ h') h } }
end⟩

theorem lt_size {m n : ℕ} : m < size n ↔ 2^m ≤ n :=
by rw [← not_lt, iff_not_comm, not_lt, size_le]

theorem size_pos {n : ℕ} : 0 < size n ↔ 0 < n :=
by rw lt_size; refl

theorem size_eq_zero {n : ℕ} : size n = 0 ↔ n = 0 :=
by have := @size_pos n; simp [pos_iff_ne_zero] at this;
   exact not_iff_not.1 this

theorem size_pow {n : ℕ} : size (2^n) = n+1 :=
le_antisymm
  (size_le.2 $ pow_lt_pow_of_lt_right dec_trivial (lt_succ_self _))
  (lt_size.2 $ le_refl _)

theorem size_le_size {m n : ℕ} (h : m ≤ n) : size m ≤ size n :=
size_le.2 $ lt_of_le_of_lt h (lt_size_self _)

/- factorial -/

/-- `fact n` is the factorial of `n`. -/
@[simp] def fact : nat → nat
| 0        := 1
| (succ n) := succ n * fact n

@[simp] theorem fact_zero : fact 0 = 1 := rfl

@[simp] theorem fact_succ (n) : fact (succ n) = succ n * fact n := rfl

@[simp] theorem fact_one : fact 1 = 1 := rfl

theorem fact_pos : ∀ n, 0 < fact n
| 0        := zero_lt_one
| (succ n) := mul_pos (succ_pos _) (fact_pos n)

theorem fact_ne_zero (n : ℕ) : fact n ≠ 0 := ne_of_gt (fact_pos _)

theorem fact_dvd_fact {m n} (h : m ≤ n) : fact m ∣ fact n :=
begin
  induction n with n IH; simp,
  { have := eq_zero_of_le_zero h, subst m, simp },
  { cases eq_or_lt_of_le h with he hl,
    { subst m, simp },
    { apply dvd_mul_of_dvd_right (IH (le_of_lt_succ hl)) } }
end

theorem dvd_fact : ∀ {m n}, 0 < m → m ≤ n → m ∣ fact n
| (succ m) n _ h := dvd_of_mul_right_dvd (fact_dvd_fact h)

theorem fact_le {m n} (h : m ≤ n) : fact m ≤ fact n :=
le_of_dvd (fact_pos _) (fact_dvd_fact h)

lemma fact_mul_pow_le_fact : ∀ {m n : ℕ}, m.fact * m.succ ^ n ≤ (m + n).fact
| m 0     := by simp
| m (n+1) :=
by  rw [← add_assoc, nat.fact_succ, mul_comm (nat.succ _), nat.pow_succ, ← mul_assoc];
  exact mul_le_mul fact_mul_pow_le_fact
    (nat.succ_le_succ (nat.le_add_right _ _)) (nat.zero_le _) (nat.zero_le _)

lemma monotone_fact : monotone fact := λ n m, fact_le

lemma fact_lt (h0 : 0 < n) : n.fact < m.fact ↔ n < m :=
begin
  split; intro h,
  { rw [← not_le], intro hmn, apply not_le_of_lt h (fact_le hmn) },
  { have : ∀(n : ℕ), 0 < n → n.fact < n.succ.fact,
    { intros k hk, rw [fact_succ, succ_mul, lt_add_iff_pos_left],
      apply mul_pos hk (fact_pos k) },
    induction h generalizing h0,
    { exact this _ h0, },
    { refine lt_trans (h_ih h0) (this _ _), exact lt_trans h0 (lt_of_succ_le h_a) }}
end

lemma one_lt_fact : 1 < n.fact ↔ 1 < n :=
by { convert fact_lt _, refl, exact one_pos }

lemma fact_eq_one : n.fact = 1 ↔ n ≤ 1 :=
begin
  split; intro h,
  { rw [← not_lt, ← one_lt_fact, h], apply lt_irrefl },
  { cases h with h h, refl, cases h, refl }
end

lemma fact_inj (h0 : 1 < n.fact) : n.fact = m.fact ↔ n = m :=
begin
  split; intro h,
  { rcases lt_trichotomy n m with hnm|hnm|hnm,
    { exfalso, rw [← fact_lt, h] at hnm, exact lt_irrefl _ hnm,
      rw [one_lt_fact] at h0, exact lt_trans one_pos h0 },
    { exact hnm },
    { exfalso, rw [← fact_lt, h] at hnm, exact lt_irrefl _ hnm,
      rw [h, one_lt_fact] at h0, exact lt_trans one_pos h0 }},
  { rw h }
end

/- choose -/

/-- `choose n k` is the number of `k`-element subsets in an `n`-element set. Also known as binomial
coefficients. -/
def choose : ℕ → ℕ → ℕ
| _             0 := 1
| 0       (k + 1) := 0
| (n + 1) (k + 1) := choose n k + choose n (k + 1)

@[simp] lemma choose_zero_right (n : ℕ) : choose n 0 = 1 := by cases n; refl

@[simp] lemma choose_zero_succ (k : ℕ) : choose 0 (succ k) = 0 := rfl

lemma choose_succ_succ (n k : ℕ) : choose (succ n) (succ k) = choose n k + choose n (succ k) := rfl

lemma choose_eq_zero_of_lt : ∀ {n k}, n < k → choose n k = 0
| _             0 hk := absurd hk dec_trivial
| 0       (k + 1) hk := choose_zero_succ _
| (n + 1) (k + 1) hk :=
  have hnk : n < k, from lt_of_succ_lt_succ hk,
  have hnk1 : n < k + 1, from lt_of_succ_lt hk,
  by rw [choose_succ_succ, choose_eq_zero_of_lt hnk, choose_eq_zero_of_lt hnk1]

@[simp] lemma choose_self (n : ℕ) : choose n n = 1 :=
by induction n; simp [*, choose, choose_eq_zero_of_lt (lt_succ_self _)]

@[simp] lemma choose_succ_self (n : ℕ) : choose n (succ n) = 0 :=
choose_eq_zero_of_lt (lt_succ_self _)

@[simp] lemma choose_one_right (n : ℕ) : choose n 1 = n :=
by induction n; simp [*, choose, add_comm]

/-- `choose n 2` is the `n`-th triangle number. -/
lemma choose_two_right (n : ℕ) : choose n 2 = n * (n - 1) / 2 :=
begin
  induction n with n ih,
  simp,
  {rw triangle_succ n, simp [choose, ih], rw add_comm},
end

lemma choose_pos : ∀ {n k}, k ≤ n → 0 < choose n k
| 0             _ hk := by rw [eq_zero_of_le_zero hk]; exact dec_trivial
| (n + 1)       0 hk := by simp; exact dec_trivial
| (n + 1) (k + 1) hk := by rw choose_succ_succ;
    exact add_pos_of_pos_of_nonneg (choose_pos (le_of_succ_le_succ hk)) (nat.zero_le _)

lemma succ_mul_choose_eq : ∀ n k, succ n * choose n k = choose (succ n) (succ k) * succ k
| 0             0 := dec_trivial
| 0       (k + 1) := by simp [choose]
| (n + 1)       0 := by simp
| (n + 1) (k + 1) :=
  by rw [choose_succ_succ (succ n) (succ k), add_mul, ←succ_mul_choose_eq, mul_succ,
  ←succ_mul_choose_eq, add_right_comm, ←mul_add, ←choose_succ_succ, ←succ_mul]

lemma choose_mul_fact_mul_fact : ∀ {n k}, k ≤ n → choose n k * fact k * fact (n - k) = fact n
| 0              _ hk := by simp [eq_zero_of_le_zero hk]
| (n + 1)        0 hk := by simp
| (n + 1) (succ k) hk :=
begin
  cases lt_or_eq_of_le hk with hk₁ hk₁,
  { have h : choose n k * fact (succ k) * fact (n - k) = succ k * fact n :=
      by rw ← choose_mul_fact_mul_fact (le_of_succ_le_succ hk);
      simp [fact_succ, mul_comm, mul_left_comm],
    have h₁ : fact (n - k) = (n - k) * fact (n - succ k) :=
      by rw [← succ_sub_succ, succ_sub (le_of_lt_succ hk₁), fact_succ],
    have h₂ : choose n (succ k) * fact (succ k) * ((n - k) * fact (n - succ k)) = (n - k) * fact n :=
      by rw ← choose_mul_fact_mul_fact (le_of_lt_succ hk₁);
      simp [fact_succ, mul_comm, mul_left_comm, mul_assoc],
    have h₃ : k * fact n ≤ n * fact n := mul_le_mul_right _ (le_of_succ_le_succ hk),
  rw [choose_succ_succ, add_mul, add_mul, succ_sub_succ, h, h₁, h₂, ← add_one, add_mul, nat.mul_sub_right_distrib,
      fact_succ, ← nat.add_sub_assoc h₃, add_assoc, ← add_mul, nat.add_sub_cancel_left, add_comm] },
  { simp [hk₁, mul_comm, choose, nat.sub_self] }
end

theorem choose_eq_fact_div_fact {n k : ℕ} (hk : k ≤ n) : choose n k = fact n / (fact k * fact (n - k)) :=
begin
  have : fact n = choose n k * (fact k * fact (n - k)) :=
    by rw ← mul_assoc; exact (choose_mul_fact_mul_fact hk).symm,
  exact (nat.div_eq_of_eq_mul_left (mul_pos (fact_pos _) (fact_pos _)) this).symm
end

theorem fact_mul_fact_dvd_fact {n k : ℕ} (hk : k ≤ n) : fact k * fact (n - k) ∣ fact n :=
by rw [←choose_mul_fact_mul_fact hk, mul_assoc]; exact dvd_mul_left _ _

@[simp] lemma choose_symm {n k : ℕ} (hk : k ≤ n) : choose n (n-k) = choose n k :=
by rw [choose_eq_fact_div_fact hk, choose_eq_fact_div_fact (sub_le _ _), nat.sub_sub_self hk, mul_comm]

lemma choose_symm_of_eq_add {n a b : ℕ} (h : n = a + b) : nat.choose n a = nat.choose n b :=
by { convert nat.choose_symm (nat.le_add_left _ _), rw nat.add_sub_cancel}

lemma choose_symm_add {a b : ℕ} : choose (a+b) a = choose (a+b) b :=
choose_symm_of_eq_add rfl

lemma choose_symm_half (m : ℕ) : choose (2 * m + 1) (m + 1) = choose (2 * m + 1) m :=
by { apply choose_symm_of_eq_add, rw [add_comm m 1, add_assoc 1 m m, add_comm (2 * m) 1, two_mul m] }

lemma choose_succ_right_eq (n k : ℕ) : choose n (k + 1) * (k + 1) = choose n k * (n - k) :=
begin
  have e : (n+1) * choose n k = choose n k * (k+1) + choose n (k+1) * (k+1),
    rw [← right_distrib, ← choose_succ_succ, succ_mul_choose_eq],
  rw [← nat.sub_eq_of_eq_add e, mul_comm, ← nat.mul_sub_left_distrib, nat.add_sub_add_right]
end

@[simp] lemma choose_succ_self_right : ∀ (n:ℕ), (n+1).choose n = n+1
| 0     := rfl
| (n+1) := by rw [choose_succ_succ, choose_succ_self_right, choose_self]

lemma choose_mul_succ_eq (n k : ℕ) :
  (n.choose k) * (n + 1) = ((n+1).choose k) * (n + 1 - k) :=
begin
  induction k with k ih, { simp },
  by_cases hk : n < k + 1,
  { rw [choose_eq_zero_of_lt hk, sub_eq_zero_of_le hk, zero_mul, mul_zero] },
  push_neg at hk,
  replace hk : k + 1 ≤ n + 1 := _root_.le_add_right hk,
  rw [choose_succ_succ],
  rw [add_mul, succ_sub_succ],
  rw [← choose_succ_right_eq],
  rw [← succ_sub_succ, nat.mul_sub_left_distrib],
  symmetry,
  apply nat.add_sub_cancel',
  exact mul_le_mul_left _ hk,
end

theorem units_eq_one (u : units ℕ) : u = 1 :=
units.ext $ nat.eq_one_of_dvd_one ⟨u.inv, u.val_inv.symm⟩

theorem add_units_eq_zero (u : add_units ℕ) : u = 0 :=
add_units.ext $ (nat.eq_zero_of_add_eq_zero u.val_neg).1

@[simp] protected theorem is_unit_iff {n : ℕ} : is_unit n ↔ n = 1 :=
iff.intro
  (assume ⟨u, hu⟩, match n, u, hu, nat.units_eq_one u with _, _, rfl, rfl := rfl end)
  (assume h, h.symm ▸ ⟨1, rfl⟩)

section find_greatest

/-- `find_greatest P b` is the largest `i ≤ bound` such that `P i` holds, or `0` if no such `i`
exists -/
protected def find_greatest (P : ℕ → Prop) [decidable_pred P] : ℕ → ℕ
| 0       := 0
| (n + 1) := if P (n + 1) then n + 1 else find_greatest n

variables {P : ℕ → Prop} [decidable_pred P]

@[simp] lemma find_greatest_zero : nat.find_greatest P 0 = 0 := rfl

@[simp] lemma find_greatest_eq : ∀{b}, P b → nat.find_greatest P b = b
| 0       h := rfl
| (n + 1) h := by simp [nat.find_greatest, h]

@[simp] lemma find_greatest_of_not {b} (h : ¬ P (b + 1)) :
  nat.find_greatest P (b + 1) = nat.find_greatest P b :=
by simp [nat.find_greatest, h]

lemma find_greatest_spec_and_le :
  ∀{b m}, m ≤ b → P m → P (nat.find_greatest P b) ∧ m ≤ nat.find_greatest P b
| 0       m hm hP :=
  have m = 0, from le_antisymm hm (nat.zero_le _),
  show P 0 ∧ m ≤ 0, from this ▸ ⟨hP, le_refl _⟩
| (b + 1) m hm hP :=
  begin
    by_cases h : P (b + 1),
    { simp [h, hm] },
    { have : m ≠ b + 1 := assume this, h $ this ▸ hP,
      have : m ≤ b := (le_of_not_gt $ assume h : b + 1 ≤ m, this $ le_antisymm hm h),
      have : P (nat.find_greatest P b) ∧ m ≤ nat.find_greatest P b :=
        find_greatest_spec_and_le this hP,
      simp [h, this] }
  end

lemma find_greatest_spec {b} : (∃m, m ≤ b ∧ P m) → P (nat.find_greatest P b)
| ⟨m, hmb, hm⟩ := (find_greatest_spec_and_le hmb hm).1

lemma find_greatest_le : ∀ {b}, nat.find_greatest P b ≤ b
| 0       := le_refl _
| (b + 1) :=
  have nat.find_greatest P b ≤ b + 1, from le_trans find_greatest_le (nat.le_succ b),
  by by_cases P (b + 1); simp [h, this]

lemma le_find_greatest {b m} (hmb : m ≤ b) (hm : P m) : m ≤ nat.find_greatest P b :=
(find_greatest_spec_and_le hmb hm).2

lemma find_greatest_is_greatest {P : ℕ → Prop} [decidable_pred P] {b} :
  (∃ m, m ≤ b ∧ P m) → ∀ k, nat.find_greatest P b < k ∧ k ≤ b → ¬ P k
| ⟨m, hmb, hP⟩ k ⟨hk, hkb⟩ hPk := lt_irrefl k $ lt_of_le_of_lt (le_find_greatest hkb hPk) hk

lemma find_greatest_eq_zero {P : ℕ → Prop} [decidable_pred P] :
  ∀ {b}, (∀ n ≤ b, ¬ P n) → nat.find_greatest P b = 0
| 0       h := find_greatest_zero
| (n + 1) h :=
begin
  have := nat.find_greatest_of_not (h (n + 1) (le_refl _)),
  rw this, exact find_greatest_eq_zero (assume k hk, h k (le_trans hk $ nat.le_succ _))
end

lemma find_greatest_of_ne_zero {P : ℕ → Prop} [decidable_pred P] :
  ∀ {b m}, nat.find_greatest P b = m → m ≠ 0 → P m
| 0       m rfl h := by { have := @find_greatest_zero P _, contradiction }
| (b + 1) m rfl h :=
decidable.by_cases
  (assume hb : P (b + 1), by { have := find_greatest_eq hb, rw this, exact hb })
  (assume hb : ¬ P (b + 1), find_greatest_of_ne_zero (find_greatest_of_not hb).symm h)

end find_greatest

section div
lemma dvd_div_of_mul_dvd {a b c : ℕ} (h : a * b ∣ c) : b ∣ c / a :=
if ha : a = 0 then
  by simp [ha]
else
  have ha : 0 < a, from nat.pos_of_ne_zero ha,
  have h1 : ∃ d, c = a * b * d, from h,
  let ⟨d, hd⟩ := h1 in
  have hac : a ∣ c, from dvd_of_mul_right_dvd h,
  have h2 : c / a = b * d, from nat.div_eq_of_eq_mul_right ha (by simpa [mul_assoc] using hd),
  show ∃ d, c / a = b * d, from ⟨d, h2⟩

lemma mul_dvd_of_dvd_div {a b c : ℕ} (hab : c ∣ b) (h : a ∣ b / c) : c * a ∣ b :=
have h1 : ∃ d, b / c = a * d, from h,
have h2 : ∃ e, b = c * e, from hab,
let ⟨d, hd⟩ := h1, ⟨e, he⟩ := h2 in
have h3 : b = a * d * c, from
  nat.eq_mul_of_div_eq_left hab hd,
show ∃ d, b = c * a * d, from ⟨d, by cc⟩

lemma div_mul_div {a b c d : ℕ} (hab : b ∣ a) (hcd : d ∣ c) :
      (a / b) * (c / d) = (a * c) / (b * d) :=
have exi1 : ∃ x, a = b * x, from hab,
have exi2 : ∃ y, c = d * y, from hcd,
if hb : b = 0 then by simp [hb]
else have 0 < b, from nat.pos_of_ne_zero hb,
if hd : d = 0 then by simp [hd]
else have 0 < d, from nat.pos_of_ne_zero hd,
begin
  cases exi1 with x hx, cases exi2 with y hy,
  rw [hx, hy, nat.mul_div_cancel_left, nat.mul_div_cancel_left],
  symmetry,
  apply nat.div_eq_of_eq_mul_left,
  apply mul_pos,
  repeat {assumption},
  cc
end

lemma pow_dvd_of_le_of_pow_dvd {p m n k : ℕ} (hmn : m ≤ n) (hdiv : p ^ n ∣ k) : p ^ m ∣ k :=
have p ^ m ∣ p ^ n, from pow_dvd_pow _ hmn,
dvd_trans this hdiv

lemma dvd_of_pow_dvd {p k m : ℕ} (hk : 1 ≤ k) (hpk : p^k ∣ m) : p ∣ m :=
by rw ←nat.pow_one p; exact pow_dvd_of_le_of_pow_dvd hk hpk

lemma eq_of_dvd_of_div_eq_one {a b : ℕ} (w : a ∣ b) (h : b / a = 1) : a = b :=
by rw [←nat.div_mul_cancel w, h, one_mul]

lemma eq_zero_of_dvd_of_div_eq_zero {a b : ℕ} (w : a ∣ b)  (h : b / a = 0) : b = 0 :=
by rw [←nat.div_mul_cancel w, h, zero_mul]

/-- If a small natural number is divisible by a larger natural number,
the small number is zero. -/
lemma eq_zero_of_dvd_of_lt {a b : ℕ} (w : a ∣ b) (h : b < a) : b = 0 :=
nat.eq_zero_of_dvd_of_div_eq_zero w
  ((nat.div_eq_zero_iff (lt_of_le_of_lt (zero_le b) h)).elim_right h)

lemma div_le_div_left {a b c : ℕ} (h₁ : c ≤ b) (h₂ : 0 < c) : a / b ≤ a / c :=
(nat.le_div_iff_mul_le _ _ h₂).2 $
  le_trans (mul_le_mul_left _ h₁) (div_mul_le_self _ _)

lemma div_eq_self {a b : ℕ} : a / b = a ↔ a = 0 ∨ b = 1 :=
begin
  split,
  { intro,
    cases b,
    { simp * at * },
    { cases b,
      { right, refl },
      { left,
        have : a / (b + 2) ≤ a / 2 := div_le_div_left (by simp) dec_trivial,
        refine eq_zero_of_le_half _,
        simp * at * } } },
  { rintros (rfl|rfl); simp }
end

end div

lemma exists_eq_add_of_le : ∀ {m n : ℕ}, m ≤ n → ∃ k : ℕ, n = m + k
| 0 0 h := ⟨0, by simp⟩
| 0 (n+1) h := ⟨n+1, by simp⟩
| (m+1) (n+1) h :=
  let ⟨k, hk⟩ := exists_eq_add_of_le (nat.le_of_succ_le_succ h) in
  ⟨k, by simp [hk, add_comm, add_left_comm]⟩

lemma exists_eq_add_of_lt : ∀ {m n : ℕ}, m < n → ∃ k : ℕ, n = m + k + 1
| 0 0 h := false.elim $ lt_irrefl _ h
| 0 (n+1) h := ⟨n, by simp⟩
| (m+1) (n+1) h := let ⟨k, hk⟩ := exists_eq_add_of_le (nat.le_of_succ_le_succ h) in ⟨k, by simp [hk]⟩

lemma with_bot.add_eq_zero_iff : ∀ {n m : with_bot ℕ}, n + m = 0 ↔ n = 0 ∧ m = 0
| none     m        := iff_of_false dec_trivial (λ h, absurd h.1 dec_trivial)
| n        none     := iff_of_false (by cases n; exact dec_trivial)
  (λ h, absurd h.2 dec_trivial)
| (some n) (some m) := show (n + m : with_bot ℕ) = (0 : ℕ) ↔ (n : with_bot ℕ) = (0 : ℕ) ∧
    (m : with_bot ℕ) = (0 : ℕ),
  by rw [← with_bot.coe_add, with_bot.coe_eq_coe, with_bot.coe_eq_coe,
    with_bot.coe_eq_coe, add_eq_zero_iff' (nat.zero_le _) (nat.zero_le _)]

lemma with_bot.add_eq_one_iff : ∀ {n m : with_bot ℕ}, n + m = 1 ↔ (n = 0 ∧ m = 1) ∨ (n = 1 ∧ m = 0)
| none     none     := dec_trivial
| none     (some m) := dec_trivial
| (some n) none     := iff_of_false dec_trivial (λ h, h.elim (λ h, absurd h.2 dec_trivial)
  (λ h, absurd h.2 dec_trivial))
| (some n) (some 0) := by erw [with_bot.coe_eq_coe, with_bot.coe_eq_coe, with_bot.coe_eq_coe,
    with_bot.coe_eq_coe]; simp
| (some n) (some (m + 1)) := by erw [with_bot.coe_eq_coe, with_bot.coe_eq_coe, with_bot.coe_eq_coe,
    with_bot.coe_eq_coe, with_bot.coe_eq_coe]; simp [nat.add_succ, nat.succ_inj', nat.succ_ne_zero]

@[simp] lemma with_bot.coe_nonneg {n : ℕ} : 0 ≤ (n : with_bot ℕ) :=
by rw [← with_bot.coe_zero, with_bot.coe_le_coe]; exact nat.zero_le _

@[simp] lemma with_bot.lt_zero_iff (n : with_bot ℕ) : n < 0 ↔ n = ⊥ :=
option.cases_on n dec_trivial (λ n, iff_of_false
  (by simp [with_bot.some_eq_coe]) (λ h, option.no_confusion h))

-- induction

/-- Induction principle starting at a non-zero number. For maps to a `Sort*` see `le_rec_on`. -/
@[elab_as_eliminator] lemma le_induction {P : nat → Prop} {m} (h0 : P m) (h1 : ∀ n, m ≤ n → P n → P (n + 1)) :
  ∀ n, m ≤ n → P n :=
by apply nat.less_than_or_equal.rec h0; exact h1

/-- Decreasing induction: if `P (k+1)` implies `P k`, then `P n` implies `P m` for all `m ≤ n`.
Also works for functions to `Sort*`. -/
@[elab_as_eliminator]
def decreasing_induction {P : ℕ → Sort*} (h : ∀n, P (n+1) → P n) {m n : ℕ} (mn : m ≤ n)
  (hP : P n) : P m :=
le_rec_on mn (λ k ih hsk, ih $ h k hsk) (λ h, h) hP

@[simp] lemma decreasing_induction_self {P : ℕ → Sort*} (h : ∀n, P (n+1) → P n) {n : ℕ}
  (nn : n ≤ n) (hP : P n) : (decreasing_induction h nn hP : P n) = hP :=
by { dunfold decreasing_induction, rw [le_rec_on_self] }

lemma decreasing_induction_succ {P : ℕ → Sort*} (h : ∀n, P (n+1) → P n) {m n : ℕ} (mn : m ≤ n)
  (msn : m ≤ n + 1) (hP : P (n+1)) :
  (decreasing_induction h msn hP : P m) = decreasing_induction h mn (h n hP) :=
by { dunfold decreasing_induction, rw [le_rec_on_succ] }

@[simp] lemma decreasing_induction_succ' {P : ℕ → Sort*} (h : ∀n, P (n+1) → P n) {m : ℕ}
  (msm : m ≤ m + 1) (hP : P (m+1)) : (decreasing_induction h msm hP : P m) = h m hP :=
by { dunfold decreasing_induction, rw [le_rec_on_succ'] }

lemma decreasing_induction_trans {P : ℕ → Sort*} (h : ∀n, P (n+1) → P n) {m n k : ℕ}
  (mn : m ≤ n) (nk : n ≤ k) (hP : P k) :
  (decreasing_induction h (le_trans mn nk) hP : P m) =
  decreasing_induction h mn (decreasing_induction h nk hP) :=
by { induction nk with k nk ih, rw [decreasing_induction_self],
     rw [decreasing_induction_succ h (le_trans mn nk), ih, decreasing_induction_succ] }

lemma decreasing_induction_succ_left {P : ℕ → Sort*} (h : ∀n, P (n+1) → P n) {m n : ℕ}
  (smn : m + 1 ≤ n) (mn : m ≤ n) (hP : P n) :
  (decreasing_induction h mn hP : P m) = h m (decreasing_induction h smn hP) :=
by { rw [subsingleton.elim mn (le_trans (le_succ m) smn), decreasing_induction_trans,
         decreasing_induction_succ'] }

end nat
