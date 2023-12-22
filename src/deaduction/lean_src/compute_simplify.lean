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

@[simp_arith]
lemma sub1 (a: ℝ) : a-a = 0 :=
begin
  simp only [sub_self],
end

@[simp_arith]
lemma sub2 (a b: ℝ) : a + b - b = a :=
begin
  simp only [add_sub_cancel]
end

@[simp_arith]
lemma sub3 (a b: ℝ) : (b + a) - b = a :=
begin
  simp only [add_sub_cancel']
end


-- addition
@[simp_arith]
lemma zero_add1 (a: ℝ) : 0+a = a :=
begin
  simp only [zero_add],
end

@[simp_arith]
lemma add_zero1 (a: ℝ) : a+0 = a :=
begin
  simp only [add_zero],
end

@[simp_arith]
lemma add_right_inj1 (a b c: ℝ) : a+b = a+c ↔ b = c:=
begin
  simp only [add_right_inj]
end

@[simp_arith]
lemma add_right_inj2 (a c: ℝ) : a = a+c ↔ 0 = c:=
begin
  todo
end

@[simp_arith]
lemma add_right_inj3 (a b: ℝ) : a + b = a ↔ b = 0:=
begin
  simp only [add_right_eq_self]
end


-- left
@[simp_arith]
lemma add_left_inj1 (a b c: ℝ) : a+b = c+b ↔ a = c:=
begin
  simp only [add_left_inj]
end

@[simp_arith]
lemma add_left_inj2 (a c: ℝ) : a = c+a ↔ 0 = c:=
begin
  todo
end

@[simp_arith]
lemma add_left_inj3 (a b: ℝ) : a+b = b ↔ a = 0:=
begin
  simp only [add_left_eq_self]
end

/-
----------------------------------------------------
Simplifier lemmas for min, max, abs
----------------------------------------------------
-/

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
