/-
Copyright (c) 2017 Robert Y. Lewis. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Robert Y. Lewis, Keeley Hoek
-/
import data.nat.cast
/-!
# The finite type with `n` elements

`fin n` is the type whose elements are natural numbers smaller than `n`.
This file expands on the development in the core library.

## Main definitions

### Induction principles

* `fin_zero.elim` : Elimination principle for the empty set `fin 0`, generalizes `fin.elim0`.
* `fin.succ_rec` : Define `C n i` by induction on  `i : fin n` interpreted
  as `(0 : fin (n - i)).succ.succ…`. This function has two arguments: `H0 n` defines
  `0`-th element `C (n+1) 0` of an `(n+1)`-tuple, and `Hs n i` defines `(i+1)`-st element
  of `(n+1)`-tuple based on `n`, `i`, and `i`-th element of `n`-tuple.
* `fin.succ_rec_on` : same as `fin.succ_rec` but `i : fin n` is the first argument;

### Casts

* `cast_lt i h` : embed `i` into a `fin` where `h` proves it belongs into;
* `cast_le h` : embed `fin n` into `fin m`, `h : n ≤ m`;
* `cast eq` : embed `fin n` into `fin m`, `eq : n = m`;
* `cast_add m` : embed `fin n` into `fin (n+m)`;
* `cast_succ` : embed `fin n` into `fin (n+1)`;
* `succ_above p` : embed `fin n` into `fin (n + 1)` with a hole around `p`;
* `pred_above p i h` : embed `i : fin (n+1)` into `fin n` by ignoring `p`;
* `sub_nat i h` : subtract `m` from `i ≥ m`, generalizes `fin.pred`;
* `add_nat i h` : add `m` on `i` on the right, generalizes `fin.succ`;
* `nat_add i h` adds `n` on `i` on the left;
* `clamp n m` : `min n m` as an element of `fin (m + 1)`;

### Operation on tuples

We interpret maps `Π i : fin n, α i` as tuples `(α 0, …, α (n-1))`.
If `α i` is a constant map, then tuples are isomorphic (but not definitionally equal)
to `vector`s.

We define the following operations:

* `tail` : the tail of an `n+1` tuple, i.e., its last `n` entries;
* `cons` : adding an element at the beginning of an `n`-tuple, to get an `n+1`-tuple;
* `init` : the beginning of an `n+1` tuple, i.e., its first `n` entries;
* `snoc` : adding an element at the end of an `n`-tuple, to get an `n+1`-tuple. The name `snoc`
  comes from `cons` (i.e., adding an element to the left of a tuple) read in reverse order.
* `find p` : returns the first index `n` where `p n` is satisfied, and `none` if it is never
  satisfied.

### Misc definitions

* `fin.last n` : The greatest value of `fin (n+1)`.

-/

universe u
open fin nat function

/-- Elimination principle for the empty set `fin 0`, dependent version. -/
def fin_zero_elim {α : fin 0 → Sort u} (x : fin 0) : α x := x.elim0

namespace fin
variables {n m : ℕ} {a b : fin n}

@[simp] protected lemma eta (a : fin n) (h : a.1 < n) : (⟨a.1, h⟩ : fin n) = a :=
by cases a; refl

attribute [ext] eq_of_veq

protected lemma ext_iff (a b : fin n) : a = b ↔ a.val = b.val :=
iff.intro (congr_arg _) fin.eq_of_veq

lemma val_injective {n : ℕ} : injective (val : fin n → ℕ) := λ _ _, fin.eq_of_veq

lemma eq_iff_veq (a b : fin n) : a = b ↔ a.1 = b.1 :=
⟨veq_of_eq, eq_of_veq⟩

@[simp] protected lemma mk.inj_iff {n a b : ℕ} {ha : a < n} {hb : b < n} :
  fin.mk a ha = fin.mk b hb ↔ a = b :=
⟨fin.mk.inj, λ h, by subst h⟩

instance fin_to_nat (n : ℕ) : has_coe (fin n) nat := ⟨fin.val⟩

lemma mk_val {m n : ℕ} (h : m < n) : (⟨m, h⟩ : fin n).val = m := rfl

@[simp, norm_cast] lemma coe_mk {m n : ℕ} (h : m < n) : ((⟨m, h⟩ : fin n) : ℕ) = m := rfl

lemma coe_eq_val (a : fin n) : (a : ℕ) = a.val := rfl

attribute [simp] val_zero
@[simp] lemma val_one  {n : ℕ} : (1 : fin (n+2)).val = 1 := rfl
@[simp] lemma val_two  {n : ℕ} : (2 : fin (n+3)).val = 2 := rfl
@[simp] lemma coe_zero {n : ℕ} : ((0 : fin (n+1)) : ℕ) = 0 := rfl
@[simp] lemma coe_one  {n : ℕ} : ((1 : fin (n+2)) : ℕ) = 1 := rfl
@[simp] lemma coe_two  {n : ℕ} : ((2 : fin (n+3)) : ℕ) = 2 := rfl

/-- `a < b` as natural numbers if and only if `a < b` in `fin n`. -/
@[norm_cast, simp] lemma coe_fin_lt {n : ℕ} {a b : fin n} : (a : ℕ) < (b : ℕ) ↔ a < b :=
iff.rfl

/-- `a ≤ b` as natural numbers if and only if `a ≤ b` in `fin n`. -/
@[norm_cast, simp] lemma coe_fin_le {n : ℕ} {a b : fin n} : (a : ℕ) ≤ (b : ℕ) ↔ a ≤ b :=
iff.rfl

lemma val_add {n : ℕ} : ∀ a b : fin n, (a + b).val = (a.val + b.val) % n
| ⟨_, _⟩ ⟨_, _⟩ := rfl

lemma val_mul {n : ℕ} :  ∀ a b : fin n, (a * b).val = (a.val * b.val) % n
| ⟨_, _⟩ ⟨_, _⟩ := rfl

lemma one_val {n : ℕ} : (1 : fin (n+1)).val = 1 % (n+1) := rfl

@[simp] lemma zero_val (n : ℕ) : (0 : fin (n+1)).val = 0 := rfl

@[simp]
lemma of_nat_eq_coe (n : ℕ) (a : ℕ) : (of_nat a : fin (n+1)) = a :=
begin
  induction a with a ih, { refl },
  ext, show (a+1) % (n+1) = fin.val (a+1 : fin (n+1)),
  { rw [val_add, ← ih, of_nat],
    exact add_mod _ _ _ }
end

/-- Converting an in-range number to `fin (n + 1)` produces a result
whose value is the original number.  -/
lemma coe_val_of_lt {n : ℕ} {a : ℕ} (h : a < n + 1) :
  (a : fin (n + 1)).val = a :=
begin
  rw ←of_nat_eq_coe,
  exact nat.mod_eq_of_lt h
end

/-- Converting the value of a `fin (n + 1)` to `fin (n + 1)` results
in the same value.  -/
@[simp] lemma coe_val_eq_self {n : ℕ} (a : fin (n + 1)) : (a.val : fin (n + 1)) = a :=
begin
  rw fin.eq_iff_veq,
  exact coe_val_of_lt a.is_lt
end

/-- Coercing an in-range number to `fin (n + 1)`, and converting back
to `ℕ`, results in that number. -/
lemma coe_coe_of_lt {n : ℕ} {a : ℕ} (h : a < n + 1) :
  ((a : fin (n + 1)) : ℕ) = a :=
coe_val_of_lt h

/-- Converting a `fin (n + 1)` to `ℕ` and back results in the same
value. -/
@[simp] lemma coe_coe_eq_self {n : ℕ} (a : fin (n + 1)) : ((a : ℕ) : fin (n + 1)) = a :=
coe_val_eq_self a

/-- Assume `k = l`. If two functions defined on `fin k` and `fin l` are equal on each element,
then they coincide (in the heq sense). -/
protected lemma heq_fun_iff {α : Type*} {k l : ℕ} (h : k = l) {f : fin k → α} {g : fin l → α} :
  f == g ↔ (∀ (i : fin k), f i = g ⟨i.val, h ▸ i.2⟩) :=
by { induction h, simp [heq_iff_eq, function.funext_iff] }

protected lemma heq_ext_iff {k l : ℕ} (h : k = l) {i : fin k} {j : fin l} :
  i == j ↔ i.val = j.val :=
by { induction h, simp [fin.ext_iff] }

instance {n : ℕ} : decidable_linear_order (fin n) :=
decidable_linear_order.lift fin.val (@fin.eq_of_veq _)

lemma exists_iff {p : fin n → Prop} : (∃ i, p i) ↔ ∃ i h, p ⟨i, h⟩ :=
⟨λ h, exists.elim h (λ ⟨i, hi⟩ hpi, ⟨i, hi, hpi⟩),
  λ h, exists.elim h (λ i hi, ⟨⟨i, hi.fst⟩, hi.snd⟩)⟩

lemma forall_iff {p : fin n → Prop} : (∀ i, p i) ↔ ∀ i h, p ⟨i, h⟩ :=
⟨λ h i hi, h ⟨i, hi⟩, λ h ⟨i, hi⟩, h i hi⟩

lemma zero_le (a : fin (n + 1)) : 0 ≤ a := zero_le a.1

lemma lt_iff_val_lt_val : a < b ↔ a.val < b.val := iff.rfl

lemma le_iff_val_le_val : a ≤ b ↔ a.val ≤ b.val := iff.rfl

@[simp] lemma succ_val (j : fin n) : j.succ.val = j.val.succ :=
by cases j; simp [fin.succ]

protected theorem succ.inj (p : fin.succ a = fin.succ b) : a = b :=
by cases a; cases b; exact eq_of_veq (nat.succ.inj (veq_of_eq p))

@[simp] lemma succ_inj {a b : fin n} : a.succ = b.succ ↔ a = b :=
⟨λh, succ.inj h, λh, by rw h⟩

lemma succ_injective (n : ℕ) : injective (@fin.succ n) :=
λa b, succ.inj

lemma succ_ne_zero {n} : ∀ k : fin n, fin.succ k ≠ 0
| ⟨k, hk⟩ heq := nat.succ_ne_zero k $ (fin.ext_iff _ _).1 heq

@[simp] lemma pred_val (j : fin (n+1)) (h : j ≠ 0) : (j.pred h).val = j.val.pred :=
by cases j; simp [fin.pred]

@[simp] lemma succ_pred : ∀(i : fin (n+1)) (h : i ≠ 0), (i.pred h).succ = i
| ⟨0,     h⟩ hi := by contradiction
| ⟨n + 1, h⟩ hi := rfl

@[simp] lemma pred_succ (i : fin n) {h : i.succ ≠ 0} : i.succ.pred h = i :=
by cases i; refl

@[simp] lemma pred_inj :
  ∀ {a b : fin (n + 1)} {ha : a ≠ 0} {hb : b ≠ 0}, a.pred ha = b.pred hb ↔ a = b
| ⟨0,   _⟩  b         ha hb := by contradiction
| ⟨i+1, _⟩  ⟨0,   _⟩  ha hb := by contradiction
| ⟨i+1, hi⟩ ⟨j+1, hj⟩ ha hb := by simp [fin.eq_iff_veq]

/-- The greatest value of `fin (n+1)` -/
def last (n : ℕ) : fin (n+1) := ⟨_, n.lt_succ_self⟩

/-- `cast_lt i h` embeds `i` into a `fin` where `h` proves it belongs into.  -/
def cast_lt (i : fin m) (h : i.1 < n) : fin n := ⟨i.1, h⟩

/-- `cast_le h i` embeds `i` into a larger `fin` type.  -/
def cast_le (h : n ≤ m) (a : fin n) : fin m := cast_lt a (lt_of_lt_of_le a.2 h)

/-- `cast eq i` embeds `i` into a equal `fin` type. -/
def cast (eq : n = m) : fin n → fin m := cast_le $ le_of_eq eq

/-- `cast_add m i` embeds `i : fin n` in `fin (n+m)`. -/
def cast_add (m) : fin n → fin (n + m) := cast_le $ le_add_right n m

/-- `cast_succ i` embeds `i : fin n` in `fin (n+1)`. -/
def cast_succ : fin n → fin (n + 1) := cast_add 1

/-- `succ_above p i` embeds `fin n` into `fin (n + 1)` with a hole around `p`. -/
def succ_above (p : fin (n+1)) (i : fin n) : fin (n+1) :=
if i.1 < p.1 then i.cast_succ else i.succ

/-- `pred_above p i h` embeds `i : fin (n+1)` into `fin n` by ignoring `p`. -/
def pred_above (p : fin (n+1)) (i : fin (n+1)) (hi : i ≠ p) : fin n :=
if h : i < p
then i.cast_lt (lt_of_lt_of_le h $ nat.le_of_lt_succ p.2)
else i.pred $
  have p < i, from lt_of_le_of_ne (le_of_not_gt h) hi.symm,
  ne_of_gt (lt_of_le_of_lt (zero_le p) this)

/-- `sub_nat i h` subtracts `m` from `i`, generalizes `fin.pred`. -/
def sub_nat (m) (i : fin (n + m)) (h : m ≤ i.val) : fin n :=
⟨i.val - m, by simp [nat.sub_lt_right_iff_lt_add h, i.is_lt]⟩

/-- `add_nat i h` adds `m` on `i`, generalizes `fin.succ`. -/
def add_nat (m) (i : fin n) : fin (n + m) :=
⟨i.1 + m, add_lt_add_right i.2 _⟩

/-- `nat_add i h` adds `n` on `i` -/
def nat_add (n) {m} (i : fin m) : fin (n + m) :=
⟨n + i.1, add_lt_add_left i.2 _⟩

theorem le_last (i : fin (n+1)) : i ≤ last n :=
le_of_lt_succ i.is_lt

@[simp] lemma cast_val (k : fin n) (h : n = m) : (fin.cast h k).val = k.val := rfl

@[simp] lemma cast_succ_val (k : fin n) : k.cast_succ.val = k.val := rfl

@[simp] lemma cast_lt_val (k : fin m) (h : k.1 < n) : (k.cast_lt h).val = k.val := rfl

@[simp] lemma cast_le_val (k : fin m) (h : m ≤ n) : (k.cast_le h).val = k.val := rfl

@[simp] lemma cast_add_val (k : fin m) : (k.cast_add n).val = k.val := rfl

@[simp] lemma last_val (n : ℕ) : (last n).val = n := rfl

@[simp, norm_cast] lemma coe_last {n : ℕ} : (last n : ℕ) = n := rfl

@[simp] lemma succ_last (n : ℕ) : (last n).succ = last (n.succ) := rfl

@[simp] lemma cast_succ_cast_lt (i : fin (n + 1)) (h : i.val < n) : cast_succ (cast_lt i h) = i :=
fin.eq_of_veq rfl

@[simp] lemma cast_lt_cast_succ {n : ℕ} (a : fin n) (h : a.1 < n) : cast_lt (cast_succ a) h = a :=
by cases a; refl

@[simp] lemma sub_nat_val (i : fin (n + m)) (h : m ≤ i.val) : (i.sub_nat m h).val = i.val - m :=
rfl

@[simp] lemma add_nat_val (i : fin (n + m)) (h : m ≤ i.val) : (i.add_nat m).val = i.val + m :=
rfl

@[simp] lemma cast_succ_inj {a b : fin n} : a.cast_succ = b.cast_succ ↔ a = b :=
by simp [eq_iff_veq]

lemma cast_succ_ne_last (a : fin n) : cast_succ a ≠ last n :=
by simp [eq_iff_veq, ne_of_lt a.2]

lemma eq_last_of_not_lt {i : fin (n+1)} (h : ¬ i.val < n) : i = last n :=
le_antisymm (le_last i) (not_lt.1 h)

lemma cast_succ_fin_succ (n : ℕ) (j : fin n) :
  cast_succ (fin.succ j) = fin.succ (cast_succ j) :=
by simp [fin.ext_iff]

/-- `min n m` as an element of `fin (m + 1)` -/
def clamp (n m : ℕ) : fin (m + 1) := fin.of_nat $ min n m

@[simp] lemma clamp_val (n m : ℕ) : (clamp n m).val = min n m :=
nat.mod_eq_of_lt $ nat.lt_succ_iff.mpr $ min_le_right _ _

lemma cast_le_injective {n₁ n₂ : ℕ} (h : n₁ ≤ n₂) : injective (fin.cast_le h)
| ⟨i₁, h₁⟩ ⟨i₂, h₂⟩ eq := fin.eq_of_veq $ show i₁ = i₂, from fin.veq_of_eq eq

lemma cast_succ_injective (n : ℕ) : injective (@fin.cast_succ n) :=
cast_le_injective (le_add_right n 1)

theorem succ_above_ne (p : fin (n+1)) (i : fin n) : p.succ_above i ≠ p :=
begin
  assume eq,
  unfold fin.succ_above at eq,
  split_ifs at eq with h;
    simpa [lt_irrefl, nat.lt_succ_self, eq.symm] using h
end

@[simp] lemma succ_above_descend :
  ∀(p i : fin (n+1)) (h : i ≠ p), p.succ_above (p.pred_above i h) = i
| ⟨p, hp⟩ ⟨0,   hi⟩ h := fin.eq_of_veq $ by simp [succ_above, pred_above]; split_ifs; simp * at *
| ⟨p, hp⟩ ⟨i+1, hi⟩ h := fin.eq_of_veq
  begin
    have : i + 1 ≠ p, by rwa [(≠), fin.ext_iff] at h,
    unfold succ_above pred_above,
    split_ifs with h1 h2;
      simp only [fin.cast_succ_cast_lt, add_right_inj, pred_val, ne.def, cast_succ_val,
                 nat.pred_succ, fin.succ_pred, add_right_inj] at *,
    exact (this (le_antisymm h2 (le_of_not_gt h1))).elim
  end

@[simp] lemma pred_above_succ_above (p : fin (n+1)) (i : fin n) (h : p.succ_above i ≠ p) :
  p.pred_above (p.succ_above i) h = i :=
begin
  unfold fin.succ_above,
  apply eq_of_veq,
  split_ifs with h₀,
  { simp [pred_above, h₀, lt_iff_val_lt_val], },
  { unfold pred_above,
    split_ifs with h₁,
    { exfalso,
      rw [lt_iff_val_lt_val, succ_val] at h₁,
      exact h₀ (lt_trans (nat.lt_succ_self _) h₁) },
    { rw [pred_succ] } }
end

/-- A function `f` on `fin n` is strictly monotone if and only if `f i < f (i+1)` for all `i`. -/
lemma strict_mono_iff_lt_succ {α : Type*} [preorder α] {f : fin n → α} :
  strict_mono f ↔ ∀ i (h : i + 1 < n), f ⟨i, lt_of_le_of_lt (nat.le_succ i) h⟩ < f ⟨i+1, h⟩ :=
begin
  split,
  { assume H i hi,
    apply H,
    exact nat.lt_succ_self _ },
  { assume H,
    have A : ∀ i j (h : i < j) (h' : j < n), f ⟨i, lt_trans h h'⟩ < f ⟨j, h'⟩,
    { assume i j h h',
      induction h with k h IH,
      { exact H _ _ },
      { exact lt_trans (IH (nat.lt_of_succ_lt h')) (H _ _) } },
    assume i j hij,
    convert A (i : ℕ) (j : ℕ) hij j.2;
    simp [fin.ext_iff, fin.coe_eq_val] }
end

section rec

/-- Define `C n i` by induction on  `i : fin n` interpreted as `(0 : fin (n - i)).succ.succ…`.
This function has two arguments: `H0 n` defines `0`-th element `C (n+1) 0` of an `(n+1)`-tuple,
and `Hs n i` defines `(i+1)`-st element of `(n+1)`-tuple based on `n`, `i`, and `i`-th element
of `n`-tuple. -/
@[elab_as_eliminator] def succ_rec
  {C : Π n, fin n → Sort*}
  (H0 : Π n, C (succ n) 0)
  (Hs : Π n i, C n i → C (succ n) i.succ) : Π {n : ℕ} (i : fin n), C n i
| 0        i           := i.elim0
| (succ n) ⟨0, _⟩      := H0 _
| (succ n) ⟨succ i, h⟩ := Hs _ _ (succ_rec ⟨i, lt_of_succ_lt_succ h⟩)

/-- Define `C n i` by induction on  `i : fin n` interpreted as `(0 : fin (n - i)).succ.succ…`.
This function has two arguments: `H0 n` defines `0`-th element `C (n+1) 0` of an `(n+1)`-tuple,
and `Hs n i` defines `(i+1)`-st element of `(n+1)`-tuple based on `n`, `i`, and `i`-th element
of `n`-tuple.

A version of `fin.succ_rec` taking `i : fin n` as the first argument. -/
@[elab_as_eliminator] def succ_rec_on {n : ℕ} (i : fin n)
  {C : Π n, fin n → Sort*}
  (H0 : Π n, C (succ n) 0)
  (Hs : Π n i, C n i → C (succ n) i.succ) : C n i :=
i.succ_rec H0 Hs

@[simp] theorem succ_rec_on_zero {C : ∀ n, fin n → Sort*} {H0 Hs} (n) :
  @fin.succ_rec_on (succ n) 0 C H0 Hs = H0 n :=
rfl

@[simp] theorem succ_rec_on_succ {C : ∀ n, fin n → Sort*} {H0 Hs} {n} (i : fin n) :
  @fin.succ_rec_on (succ n) i.succ C H0 Hs = Hs n i (fin.succ_rec_on i H0 Hs) :=
by cases i; refl

/-- Define `f : Π i : fin n.succ, C i` by separately handling the cases `i = 0` and
`i = j.succ`, `j : fin n`. -/
@[elab_as_eliminator] def cases
  {C : fin (succ n) → Sort*} (H0 : C 0) (Hs : Π i : fin n, C (i.succ)) :
  Π (i : fin (succ n)), C i
| ⟨0, h⟩ := H0
| ⟨succ i, h⟩ := Hs ⟨i, lt_of_succ_lt_succ h⟩

@[simp] theorem cases_zero {n} {C : fin (succ n) → Sort*} {H0 Hs} : @fin.cases n C H0 Hs 0 = H0 :=
rfl

@[simp] theorem cases_succ {n} {C : fin (succ n) → Sort*} {H0 Hs} (i : fin n) :
  @fin.cases n C H0 Hs i.succ = Hs i :=
by cases i; refl

lemma forall_fin_succ {P : fin (n+1) → Prop} :
  (∀ i, P i) ↔ P 0 ∧ (∀ i:fin n, P i.succ) :=
⟨λ H, ⟨H 0, λ i, H _⟩, λ ⟨H0, H1⟩ i, fin.cases H0 H1 i⟩

lemma exists_fin_succ {P : fin (n+1) → Prop} :
  (∃ i, P i) ↔ P 0 ∨ (∃i:fin n, P i.succ) :=
⟨λ ⟨i, h⟩, fin.cases or.inl (λ i hi, or.inr ⟨i, hi⟩) i h,
  λ h, or.elim h (λ h, ⟨0, h⟩) $ λ⟨i, hi⟩, ⟨i.succ, hi⟩⟩

end rec

section tuple
/-!
### Tuples

We can think of the type `Π(i : fin n), α i` as `n`-tuples of elements of possibly varying type
`α i`. A particular case is `fin n → α` of elements with all the same type. Here are some relevant
operations, first about adding or removing elements at the beginning of a tuple.
-/

/-- There is exactly one tuple of size zero. -/
instance tuple0_unique (α : fin 0 → Type u) : unique (Π i : fin 0, α i) :=
{ default := fin_zero_elim, uniq := λ x, funext fin_zero_elim }

variables {α : fin (n+1) → Type u} (x : α 0) (q : Πi, α i) (p : Π(i : fin n), α (i.succ))
(i : fin n) (y : α i.succ) (z : α 0)

/-- The tail of an `n+1` tuple, i.e., its last `n` entries -/
def tail (q : Πi, α i) : (Π(i : fin n), α (i.succ)) := λ i, q i.succ

/-- Adding an element at the beginning of an `n`-tuple, to get an `n+1`-tuple -/
def cons (x : α 0) (p : Π(i : fin n), α (i.succ)) : Πi, α i :=
λ j, fin.cases x p j

@[simp] lemma tail_cons : tail (cons x p) = p :=
by simp [tail, cons]

@[simp] lemma cons_succ : cons x p i.succ = p i :=
by simp [cons]

@[simp] lemma cons_zero : cons x p 0 = x :=
by simp [cons]

/-- Updating a tuple and adding an element at the beginning commute. -/
@[simp] lemma cons_update : cons x (update p i y) = update (cons x p) i.succ y :=
begin
  ext j,
  by_cases h : j = 0,
  { rw h, simp [ne.symm (succ_ne_zero i)] },
  { let j' := pred j h,
    have : j'.succ = j := succ_pred j h,
    rw [← this, cons_succ],
    by_cases h' : j' = i,
    { rw h', simp },
    { have : j'.succ ≠ i.succ, by rwa [ne.def, succ_inj],
      rw [update_noteq h', update_noteq this, cons_succ] } }
end

/-- Adding an element at the beginning of a tuple and then updating it amounts to adding it
directly. -/
lemma update_cons_zero : update (cons x p) 0 z = cons z p :=
begin
  ext j,
  by_cases h : j = 0,
  { rw h, simp },
  { simp only [h, update_noteq, ne.def, not_false_iff],
    let j' := pred j h,
    have : j'.succ = j := succ_pred j h,
    rw [← this, cons_succ, cons_succ] }
end

/-- Concatenating the first element of a tuple with its tail gives back the original tuple -/
@[simp] lemma cons_self_tail : cons (q 0) (tail q) = q :=
begin
  ext j,
  by_cases h : j = 0,
  { rw h, simp },
  { let j' := pred j h,
    have : j'.succ = j := succ_pred j h,
    rw [← this, tail, cons_succ] }
end

/-- Updating the first element of a tuple does not change the tail. -/
@[simp] lemma tail_update_zero : tail (update q 0 z) = tail q :=
by { ext j, simp [tail, fin.succ_ne_zero] }

/-- Updating a nonzero element and taking the tail commute. -/
@[simp] lemma tail_update_succ :
  tail (update q i.succ y) = update (tail q) i y :=
begin
  ext j,
  by_cases h : j = i,
  { rw h, simp [tail] },
  { simp [tail, (fin.succ_injective n).ne h, h] }
end

lemma comp_cons {α : Type*} {β : Type*} (g : α → β) (y : α) (q : fin n → α) :
  g ∘ (cons y q) = cons (g y) (g ∘ q) :=
begin
  ext j,
  by_cases h : j = 0,
  { rw h, refl },
  { let j' := pred j h,
    have : j'.succ = j := succ_pred j h,
    rw [← this, cons_succ, comp_app, cons_succ] }
end

lemma comp_tail {α : Type*} {β : Type*} (g : α → β) (q : fin n.succ → α) :
  g ∘ (tail q) = tail (g ∘ q) :=
by { ext j, simp [tail] }

end tuple

section tuple_right
/-! In the previous section, we have discussed inserting or removing elements on the left of a
tuple. In this section, we do the same on the right. A difference is that `fin (n+1)` is constructed
inductively from `fin n` starting from the left, not from the right. This implies that Lean needs
more help to realize that elements belong to the right types, i.e., we need to insert casts at
several places. -/

variables {α : fin (n+1) → Type u} (x : α (last n)) (q : Πi, α i) (p : Π(i : fin n), α i.cast_succ)
(i : fin n) (y : α i.cast_succ) (z : α (last n))

/-- The beginning of an `n+1` tuple, i.e., its first `n` entries -/
def init (q : Πi, α i) (i : fin n) : α i.cast_succ :=
q i.cast_succ

/-- Adding an element at the end of an `n`-tuple, to get an `n+1`-tuple. The name `snoc` comes from
`cons` (i.e., adding an element to the left of a tuple) read in reverse order. -/
def snoc (p : Π(i : fin n), α i.cast_succ) (x : α (last n)) (i : fin (n+1)) : α i :=
if h : i.val < n
then _root_.cast (by rw fin.cast_succ_cast_lt i h) (p (cast_lt i h))
else _root_.cast (by rw eq_last_of_not_lt h) x

@[simp] lemma init_snoc : init (snoc p x) = p :=
begin
  ext i,
  have h' := fin.cast_lt_cast_succ i i.is_lt,
  simp [init, snoc, i.is_lt, h'],
  convert cast_eq rfl (p i)
end

@[simp] lemma snoc_cast_succ : snoc p x i.cast_succ = p i :=
begin
  have : i.cast_succ.val < n := i.is_lt,
  have h' := fin.cast_lt_cast_succ i i.is_lt,
  simp [snoc, this, h'],
  convert cast_eq rfl (p i)
end

@[simp] lemma snoc_last : snoc p x (last n) = x :=
by { simp [snoc], refl }

/-- Updating a tuple and adding an element at the end commute. -/
@[simp] lemma snoc_update : snoc (update p i y) x = update (snoc p x) i.cast_succ y :=
begin
  ext j,
  by_cases h : j.val < n,
  { simp only [snoc, h, dif_pos],
    by_cases h' : j = cast_succ i,
    { have C1 : α i.cast_succ = α j, by rw h',
      have E1 : update (snoc p x) i.cast_succ y j = _root_.cast C1 y,
      { have : update (snoc p x) j (_root_.cast C1 y) j = _root_.cast C1 y, by simp,
        convert this,
        { exact h'.symm },
        { exact heq_of_eq_mp (congr_arg α (eq.symm h')) rfl } },
      have C2 : α i.cast_succ = α (cast_succ (cast_lt j h)),
        by rw [cast_succ_cast_lt, h'],
      have E2 : update p i y (cast_lt j h) = _root_.cast C2 y,
      { have : update p (cast_lt j h) (_root_.cast C2 y) (cast_lt j h) = _root_.cast C2 y,
          by simp,
        convert this,
        { simp [h, h'] },
        { exact heq_of_eq_mp C2 rfl } },
      rw [E1, E2],
      exact eq_rec_compose _ _ _ },
    { have : ¬(cast_lt j h = i),
        by { assume E, apply h', rw [← E, cast_succ_cast_lt] },
      simp [h', this, snoc, h] } },
  { rw eq_last_of_not_lt h,
    simp [ne.symm (cast_succ_ne_last i)] }
end

/-- Adding an element at the beginning of a tuple and then updating it amounts to adding it
directly. -/
lemma update_snoc_last : update (snoc p x) (last n) z = snoc p z :=
begin
  ext j,
  by_cases h : j.val < n,
  { have : j ≠ last n := ne_of_lt h,
    simp [h, update_noteq, this, snoc] },
  { rw eq_last_of_not_lt h,
    simp }
end

/-- Concatenating the first element of a tuple with its tail gives back the original tuple -/
@[simp] lemma snoc_init_self : snoc (init q) (q (last n)) = q :=
begin
  ext j,
  by_cases h : j.val < n,
  { have : j ≠ last n := ne_of_lt h,
    simp [h, update_noteq, this, snoc, init, cast_succ_cast_lt],
    have A : cast_succ (cast_lt j h) = j := cast_succ_cast_lt _ _,
    rw ← cast_eq rfl (q j),
    congr' 1; rw A },
  { rw eq_last_of_not_lt h,
    simp }
end

/-- Updating the last element of a tuple does not change the beginning. -/
@[simp] lemma init_update_last : init (update q (last n) z) = init q :=
by { ext j, simp [init, cast_succ_ne_last] }

/-- Updating an element and taking the beginning commute. -/
@[simp] lemma init_update_cast_succ :
  init (update q i.cast_succ y) = update (init q) i y :=
begin
  ext j,
  by_cases h : j = i,
  { rw h, simp [init] },
  { simp [init, h] }
end

/-- `tail` and `init` commute. We state this lemma in a non-dependent setting, as otherwise it
would involve a cast to convince Lean that the two types are equal, making it harder to use. -/
lemma tail_init_eq_init_tail {β : Type*} (q : fin (n+2) → β) :
  tail (init q) = init (tail q) :=
by { ext i, simp [tail, init, cast_succ_fin_succ] }

/-- `cons` and `snoc` commute. We state this lemma in a non-dependent setting, as otherwise it
would involve a cast to convince Lean that the two types are equal, making it harder to use. -/
lemma cons_snoc_eq_snoc_cons {β : Type*} (a : β) (q : fin n → β) (b : β) :
  @cons n.succ (λ i, β) a (snoc q b) = snoc (cons a q) b :=
begin
  ext i,
  by_cases h : i = 0,
  { rw h, refl },
  set j := pred i h with ji,
  have : i = j.succ, by rw [ji, succ_pred],
  rw [this, cons_succ],
  by_cases h' : j.val < n,
  { set k := cast_lt j h' with jk,
    have : j = k.cast_succ, by rw [jk, cast_succ_cast_lt],
    rw [this, ← cast_succ_fin_succ],
    simp },
  rw [eq_last_of_not_lt h', succ_last],
  simp
end


lemma comp_snoc {α : Type*} {β : Type*} (g : α → β) (q : fin n → α) (y : α) :
  g ∘ (snoc q y) = snoc (g ∘ q) (g y) :=
begin
  ext j,
  by_cases h : j.val < n,
  { have : j ≠ last n := ne_of_lt h,
    simp [h, this, snoc, cast_succ_cast_lt],
    refl },
  { rw eq_last_of_not_lt h,
    simp }
end

lemma comp_init {α : Type*} {β : Type*} (g : α → β) (q : fin n.succ → α) :
  g ∘ (init q) = init (g ∘ q) :=
by { ext j, simp [init] }

end tuple_right

section find

/-- `find p` returns the first index `n` where `p n` is satisfied, and `none` if it is never
satisfied. -/
def find : Π {n : ℕ} (p : fin n → Prop) [decidable_pred p], option (fin n)
| 0     p _ := none
| (n+1) p _ := by resetI; exact option.cases_on
  (@find n (λ i, p (i.cast_lt (nat.lt_succ_of_lt i.2))) _)
  (if h : p (fin.last n) then some (fin.last n) else none)
  (λ i, some (i.cast_lt (nat.lt_succ_of_lt i.2)))

/-- If `find p = some i`, then `p i` holds -/
lemma find_spec : Π {n : ℕ} (p : fin n → Prop) [decidable_pred p] {i : fin n}
  (hi : i ∈ by exactI fin.find p), p i
| 0     p I i hi := option.no_confusion hi
| (n+1) p I i hi := begin
  dsimp [find] at hi,
  resetI,
  cases h : find (λ i : fin n, (p (i.cast_lt (nat.lt_succ_of_lt i.2)))) with j,
  { rw h at hi,
    dsimp at hi,
    split_ifs at hi with hl hl,
    { exact option.some_inj.1 hi ▸ hl },
    { exact option.no_confusion hi } },
  { rw h at hi,
    rw [← option.some_inj.1 hi],
    exact find_spec _ h }
end

/-- `find p` does not return `none` if and only if `p i` holds at some index `i`. -/
lemma is_some_find_iff : Π {n : ℕ} {p : fin n → Prop} [decidable_pred p],
  by exactI (find p).is_some ↔ ∃ i, p i
| 0     p _ := iff_of_false (λ h, bool.no_confusion h) (λ ⟨i, _⟩, fin.elim0 i)
| (n+1) p _ := ⟨λ h, begin
  rw [option.is_some_iff_exists] at h,
  cases h with i hi,
  exactI ⟨i, find_spec _ hi⟩
end, λ ⟨⟨i, hin⟩, hi⟩,
begin
  resetI,
  dsimp [find],
  cases h : find (λ i : fin n, (p (i.cast_lt (nat.lt_succ_of_lt i.2)))) with j,
  { split_ifs with hl hl,
    { exact option.is_some_some },
    { have := (@is_some_find_iff n (λ x, p (x.cast_lt (nat.lt_succ_of_lt x.2))) _).2
        ⟨⟨i, lt_of_le_of_ne (nat.le_of_lt_succ hin)
        (λ h, by clear_aux_decl; cases h; exact hl hi)⟩, hi⟩,
      rw h at this,
      exact this } },
  { simp }
end⟩

/-- `find p` returns `none` if and only if `p i` never holds. -/
lemma find_eq_none_iff {n : ℕ} {p : fin n → Prop} [decidable_pred p] :
  find p = none ↔ ∀ i, ¬ p i :=
by rw [← not_exists, ← is_some_find_iff]; cases (find p); simp

/-- If `find p` returns `some i`, then `p j` does not hold for `j < i`, i.e., `i` is minimal among
the indices where `p` holds. -/
lemma find_min : Π {n : ℕ} {p : fin n → Prop} [decidable_pred p] {i : fin n}
  (hi : i ∈ by exactI fin.find p) {j : fin n} (hj : j < i), ¬ p j
| 0     p _ i hi j hj hpj := option.no_confusion hi
| (n+1) p _ i hi ⟨j, hjn⟩ hj hpj := begin
  resetI,
  dsimp [find] at hi,
  cases h : find (λ i : fin n, (p (i.cast_lt (nat.lt_succ_of_lt i.2)))) with k,
  { rw [h] at hi,
    split_ifs at hi with hl hl,
    { have := option.some_inj.1 hi,
      subst this,
      rw [find_eq_none_iff] at h,
      exact h ⟨j, hj⟩ hpj },
    { exact option.no_confusion hi } },
  { rw h at hi,
    dsimp at hi,
    have := option.some_inj.1 hi,
    subst this,
    exact find_min h (show (⟨j, lt_trans hj k.2⟩ : fin n) < k, from hj) hpj }
end

lemma find_min' {p : fin n → Prop} [decidable_pred p] {i : fin n}
  (h : i ∈ fin.find p) {j : fin n} (hj : p j) : i ≤ j :=
le_of_not_gt (λ hij, find_min h hij hj)

lemma nat_find_mem_find {p : fin n → Prop} [decidable_pred p]
  (h : ∃ i, ∃ hin : i < n, p ⟨i, hin⟩) :
  (⟨nat.find h, (nat.find_spec h).fst⟩ : fin n) ∈ find p :=
let ⟨i, hin, hi⟩ := h in
begin
  cases hf : find p with f,
  { rw [find_eq_none_iff] at hf,
    exact (hf ⟨i, hin⟩ hi).elim },
  { refine option.some_inj.2 (le_antisymm _ _),
    { exact find_min' hf (nat.find_spec h).snd },
    { exact nat.find_min' _ ⟨f.2, by convert find_spec p hf;
        exact fin.eta _ _⟩ } }
end

lemma mem_find_iff {p : fin n → Prop} [decidable_pred p] {i : fin n} :
  i ∈ fin.find p ↔ p i ∧ ∀ j, p j → i ≤ j :=
⟨λ hi, ⟨find_spec _ hi, λ _, find_min' hi⟩,
  begin
    rintros ⟨hpi, hj⟩,
    cases hfp : fin.find p,
    { rw [find_eq_none_iff] at hfp,
      exact (hfp _ hpi).elim },
    { exact option.some_inj.2 (le_antisymm (find_min' hfp hpi) (hj _ (find_spec _ hfp))) }
  end⟩

lemma find_eq_some_iff {p : fin n → Prop} [decidable_pred p] {i : fin n} :
  fin.find p = some i ↔ p i ∧ ∀ j, p j → i ≤ j :=
 mem_find_iff

lemma mem_find_of_unique {p : fin n → Prop} [decidable_pred p]
  (h : ∀ i j, p i → p j → i = j) {i : fin n} (hi : p i) : i ∈ fin.find p :=
mem_find_iff.2 ⟨hi, λ j hj, le_of_eq $ h i j hi hj⟩

end find

end fin
