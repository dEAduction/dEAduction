import tactic
import data.real.basic
import utils

mk_simp_attribute simp_arith "Simplifier lemmas for basic arithmetic operations"
mk_simp_attribute simp_min_max "Simplifier lemmas for min, max, abs"


/-
----------------------------------------------------
Simplifier lemmas for basic arithmetic operations
----------------------------------------------------
-/
-- substraction
-- TODO: tactic.ring.add_neg_eq_sub
-- TODO: how to add existing lemmas?? simp only <list>

variables {u: Type} [add_comm_group u]

@[simp_arith]
lemma sub0 (a: u) : -(-a) = a :=
begin
  exact neg_neg a,
end

@[simp_arith]
lemma sub1 (a: u) : a-a = 0 :=
begin
  exact sub_self a
end

@[simp_arith]
lemma sub1b (a: u) : a + (-a) = 0 :=
begin
  exact add_right_neg a
end

@[simp_arith]
lemma sub2 (a b: u) : a + b - b = a :=
begin
  exact add_sub_cancel a b
end

@[simp_arith]
lemma sub3 (a b: u) : (b + a) - b = a :=
begin
  simp only [add_sub_cancel']
end

@[simp_arith]
lemma sub4 (a b c: u) : a + b + c - a = b + c :=
begin
  todo,
end

-- Addition
@[simp_arith]
lemma zero_add1 (a: u) : 0+a = a :=
begin
  simp only [zero_add],
end

@[simp_arith]
lemma add_zero1 (a: u) : a+0 = a :=
begin
  simp only [add_zero],
end

@[simp_arith]
lemma add_right_inj1 (a b c: u) : a+b = a+c ↔ b = c:=
begin
  simp only [add_right_inj]
end

@[simp_arith]
lemma add_right_inj2 (a c: u) : a = a+c ↔ 0 = c:=
begin
  todo
end

@[simp_arith]
lemma add_right_inj3 (a b: u) : a + b = a ↔ b = 0:=
begin
  simp only [add_right_eq_self]
end


-- left
@[simp_arith]
lemma add_left_inj1 (a b c: u) : a+b = c+b ↔ a = c:=
begin
  simp only [add_left_inj]
end

@[simp_arith]
lemma add_left_inj2 (a c: u) : a = c+a ↔ 0 = c:=
begin
  todo
end

@[simp_arith]
lemma add_left_inj3 (a b: u) : a+b = b ↔ a = 0:=
begin
  simp only [add_left_eq_self]
end


-- Multiplication
variables {v w: Type} [monoid v] [group w]

@[simp_arith]
lemma one_mul1 (a: v) : 1*a = a :=
begin
  simp only [one_mul],
end

@[simp_arith]
lemma mul_one1 (a: v) : a*1 = a :=
begin
  simp only [mul_one],
end

@[simp_arith]
lemma mul_right_inj1 (a b c: w) : a*b = a*c ↔ b = c:=
begin
  have H2 :=(@mul_right_inj w _ a b c),
  exact H2,
end

@[simp_arith]
lemma mul_right_inj2 (a b: w) : a = a*b ↔ 1 = b:=
begin
  todo
end

@[simp_arith]
lemma mul_right_inj3 (a b: w) : a*b = a ↔ b = 1:=
begin
  todo
end


-- left
@[simp_arith]
lemma mul_left_inj1 (a b c: w) : a*b = c*b ↔ a = c:=
begin
  todo
end

@[simp_arith]
lemma mul_left_inj2 (a b: w) : a = b*a ↔ 1 = b:=
begin
  todo
end

@[simp_arith]
lemma mul_left_inj3 (a b: w) : a*b = b ↔ a = 1:=
begin
  todo
end


-- Powers
@[simp_arith]
lemma square {Z:Type} [has_mul Z] [has_pow Z ℕ] {a:Z}: a^2 = a * a :=
begin
  todo
end

/-
----------------------------------------------------
Simplifier lemmas for min, max, abs
----------------------------------------------------
-/
variables [decidable_linear_ordered_comm_ring u]
@[simp_arith]
lemma abs_neg2 :
∀ x :u, abs (-x) =  abs x
:= 
/- dEAduction
pretty_name = "Valeur absolue de l'opposé"
-/
begin
  todo,
end










open lean.parser tactic interactive
-- open interactive (loc.ns)
-- open interactive.types
-- open expr

-- open tactic.interactive
open lean.parser (tk)
-- open interactive (loc.ns)
open interactive.types

-- TODO: smart_comm on target

--  try eq_comm but only at end
-- names ←  get_all_theorems_whose_name_ends_with "comm",tactic.trace "Got thms",
--    e1 ← get_local h1, tactic.trace "Got h1",
--     rw_with_thm names e1


/-
Tests and examples
-/

example (a b c: ℝ) (H: c=0) (H2: a-a + b + 1 = c +b + 0 + 2): (1:real)=2 :=
begin
  -- simp only [zero_add, sub_self],
  simp only [*] with simp_arith at H2 H,
  exact H2,
end

example (a b c: ℝ) (H: c=0): 1 + a-a + b = c +b + 0 + 1:=
begin
  -- simp only [zero_add, sub_self],
  norm_num,
  simp only [*],
  try {simp with simp_arith},
  try {simp only [*]},
  -- simp only [] with simp_arith
  todo,
end
