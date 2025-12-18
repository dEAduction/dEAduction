/-
This is a d∃∀duction file providing exercises about limits and continuity.
-/

-- Lean standard imports
import tactic
import data.real.basic

-- dEAduction tactics
-- structures2 and utils are vital
import deaduction_all_tactics
-- import structures2      -- hypo_analysis, targets_analysis
-- import utils            -- no_meta_vars
-- import compute_all      -- Tactics for the compute buttons
-- import push_neg_once    -- Pushing negation just one step
-- import induction        -- Induction theorems

-- dEAduction definitions
import set_definitions
import real_definitions

-- Use classical logic
local attribute [instance] classical.prop_decidable

-------------------------
-- dEAduction METADATA --
-------------------------
/- dEAduction
title = "Suites constantes"
author = "Divers"
institution = "Université du monde"
description = """
Des exercices sur les expressions quantifiées,
autour de la notion de suite constante.
Merci à Renaud Chorlay !
"""
[settings]
logic.usr_jokers_available = false
logic.usr_name_new_vars = true
logic.use_color_for_applied_properties = true
functionality.allow_induction = true
functionality.calculator_available = true
others.Lean_request_method = "from_previous_proof_state"
logs.save_journal = true
[display]
constante_a_partir_certain_rang = [-1, " constante à partir d'un certain rang"]
-/


-- def push {source: Type} (target: Type) (object: source)
-- [has_coe: has_lift_t source target] :=
--  (@coe source target has_coe object)

-- def push_real (nb: Type)
-- [has_coe: has_lift_t _ ℝ] :=
--  (@coe _ _ has_coe nb)

  -- let v := λn: ℕ, push ℝ (2: ℕ),
  -- let w := λn:ℕ, 2,
  -- let wr := push (ℕ →ℝ) w,
  -- let wrr := push (ℕ →ℝ) wr,



variables {RealSubGroup : Type} [decidable_linear_ordered_comm_ring RealSubGroup] 

/-- Lots of definitions -/
definition limit (u : ℕ → RealSubGroup) (l : RealSubGroup) : Prop :=
∀ ε > 0, ∃ N, ∀ n ≥ N, | u n - l | < ε

definition converging_seq (u : ℕ → RealSubGroup) : Prop :=
∃ l, limit u l

definition limit_plus_infinity (u : ℕ → RealSubGroup) : Prop :=
∀ M:RealSubGroup, ∃ N:ℕ, ∀ n ≥ N, u n ≥ M

definition increasing_seq (u : ℕ → RealSubGroup) : Prop :=
∀ p q , p ≤ q → u p ≤ u q

definition bounded_above (u : ℕ → RealSubGroup) : Prop :=
∃ M:RealSubGroup, ∀ n, u n ≤ M

definition bounded_below (u : ℕ → RealSubGroup) : Prop :=
∃ m:RealSubGroup, ∀ n, u n ≥ m

definition constante_a_partir_certain_rang (u : ℕ → RealSubGroup) : Prop 
:= ∃ c: RealSubGroup, ∃ N:ℕ, ∀ n ≥ N, u n =c 

section course
open tactic.interactive
-- notation `|` x `|` := abs x

-----------------
-- definitions --
-----------------
namespace definitions
/- dEAduction
pretty_name = "Définitions"
-/


namespace generalites
/- dEAduction
pretty_name = "Généralités"
-/

lemma theorem.archimedien : ∀ x:ℝ, ∃ n:ℕ, x < n
:=
/- dEAduction
pretty_name = "ℝ est archimédien"
-/
begin
  todo
end

----------------------------------
namespace maximum
-- The name RealSubGroup will be replaced by ℝ in d∃∀duction, 
-- but allows to treat the cases of integers or rationals.

lemma definition.max (a b c : RealSubGroup) :
a = max b c ↔ (b ≤ a ∧ c ≤ a ∧ (a=b ∨ a=c))
:=
begin
  todo
end

lemma theorem.ppe_max_gauche :
∀ a b : RealSubGroup, a ≤ max a b :=
begin
  intros a b,
  -- hypo_analysis,
  -- norm_num, tautology,
  exact le_max_left a b,
  -- todo
end

lemma theorem.ppe_max_droite :
∀ a b : RealSubGroup,  b ≤ max a b :=
begin
  have H := @theorem.ppe_max_gauche,
  intros a b, norm_num, tautology,
  -- exact le_max_right a b,
end

lemma theorem.max_ppe
(a b c : RealSubGroup) (Ha: a ≤ c) (Hb: b ≤ c) :
max a b ≤ c :=
begin
  norm_num, tautology,
  -- exact max_le Ha Hb,
end

lemma theorem.max_pp
(a b c : RealSubGroup) (Ha: a < c) (Hb: b < c) :
max a b < c :=
begin
  norm_num, tautology,
  -- exact max_lt Ha Hb,
end

end maximum

namespace valeur_absolue

lemma definition.valeur_absolue
(a b : RealSubGroup) :
a = abs b ↔ (a ≥ 0 ∧ (a=b ∨ a=-b))
:=
begin
  todo
end

lemma theorem.valeur_absolue_de_positif
(x : RealSubGroup) :
((0 ≤ x) → (abs x = x)) :=
/- dEAduction
pretty_name = "Valeur absolue d'un nombre positif"
-/
begin
  exact abs_of_nonneg,
end

lemma theorem.valeur_absolue_de_negatif
(x : RealSubGroup) :
((x ≤ 0) → (abs x = -x)) :=
/- dEAduction
pretty_name = "Valeur absolue d'un nombre négatif"
-/
begin
  exact abs_of_nonpos,
end

lemma theorem.majoration_valeur_absolue
(x r : RealSubGroup):
(abs x < r) ↔ ((-r < x) ∧ (x < r))
:= 
/- dEAduction
pretty_name = "Majoration d'une valeur absolue"
-/
begin
  exact abs_lt
end

lemma theorem.minoration_valeur_absolue
(x : RealSubGroup):
(x ≤ abs x)
:= 
/- dEAduction
pretty_name = "Minoration d'une valeur absolue"
-/
begin
  -- by_cases (x≥0),
  -- rewrite theorem.valeur_absolue_de_positif, assumption,
  -- rewrite theorem.valeur_absolue_de_negatif,
  -- push_neg at h, 
  todo,
end


lemma theorem.inegalite_triangulaire
(x y : RealSubGroup):
|x + y| ≤ |x| + |y|
:= 
/- dEAduction
pretty_name = "Inégalité triangulaire"
-/
begin
  exact abs_add x y 
end

lemma theorem.valeur_absolue_produit :
∀ x y : RealSubGroup,  |x * y| = |x| * |y|
:= 
/- dEAduction
pretty_name = "Valeur absolue d'un produit"
-/
begin
  intros x y, exact abs_mul x y 
end

end valeur_absolue

end generalites


namespace suites
------------------------------
-- Définitions de la limite --
------------------------------

lemma definition.limit 
{u : ℕ → ℝ} {l : ℝ} :
(limit u l) ↔ 
∀ ε > 0, ∃ N, ∀ n ≥ N, | u n - l | < ε
:= 
/- dEAduction
pretty_name = "Limite d'une suite"
implicit_use = true
-/
begin
  refl
end

lemma definition.converging_seq
{u : ℕ → ℝ} :
(converging_seq u) ↔ 
∃ l, limit u l
:= 
/- dEAduction
pretty_name = "Suite convergente"
implicit_use = true
-/
begin
  refl
end

lemma definition.limit_plus_infinity
{u : ℕ → ℝ} :
(limit_plus_infinity u) ↔ ∀ M:ℝ, ∃ N:ℕ, ∀ n ≥ N, u n ≥ M := 
/- dEAduction
pretty_name = "Limite infinie d'une suite"
implicit_use = true
-/
begin
  refl
end

lemma definition.increasing_seq
{u : ℕ → ℝ} :
(increasing_seq u) ↔ 
∀ p q, p ≤ q → u p ≤ u q
:= 
/- dEAduction
pretty_name = "Suite croissante"
implicit_use = true
-/
begin
  refl
end

lemma definition.bounded_above 
{u : ℕ → ℝ} :
(bounded_above u) ↔ 
∃ M:ℝ, ∀ n,  u n ≤ M
:= 
/- dEAduction
pretty_name = "Suite majorée"
implicit_use = true
-/
begin
  refl
end

-- lemma definition.bounded_below 
-- {u : ℕ → ℝ} :
-- (bounded_below_sequence u) ↔ 
-- ∃ M:ℝ, ∀ n,  u n ≥ M
-- := 
-- /- dEAduction
-- PrettyName
--   Suite minorée
-- ImplicitUse
--   True
-- -/
-- begin
--   refl
-- end

-- lemma definition.bounded 
-- {u : ℕ → RealSubGroup} :
-- (bounded_sequence u) ↔ 
-- ∃ M>0, ∀ n, | u n | ≤ M
-- := 
-- /- dEAduction
-- pretty_name = "Suite bornée"
-- implicit_use = true
-- -/
-- begin
--   refl
-- end

end suites

end definitions

-----------------
--  exercices  --
-----------------

namespace suites_constantes
/- dEAduction
pretty_name = "Suites constantes"
-/

namespace definitions_equivalentes
/- dEAduction
pretty_name = "Définitions équivalentes"
-/

lemma exercise.implication1
(u : ℕ → ℝ)  :
(∀ n, u n = u 0)  → (∃ c : ℝ, ∀ n: ℕ,  (u n = c))
:=
/- dEAduction
pretty_name = "C implique A"
-/
begin
  todo,
end

lemma exercise.implication2
(u : ℕ → ℝ)  :
 (∃ c : ℝ, ∀ n: ℕ,  (u n = c)) → (∀ n, u n = u 0) 
:=
/- dEAduction
pretty_name = "A implique C"
-/
begin
  todo,
end



lemma exercise.implication3
(u : ℕ → ℝ)  :
(∀ n, u n = u 0)  → (∀ m n, u m = u n)
:=
/- dEAduction
pretty_name = "C implique B"
-/
begin
  todo,
end

lemma exercise.implication4
(u : ℕ → ℝ)  :
 (∀ m n, u m = u n) → (∀ n, u n = u 0) 
:=
/- dEAduction
pretty_name = "B implique C"
-/
begin
  todo,
end





lemma exercise.implication5
(u : ℕ → ℝ)  :
(∀ n, u n = u 0)  → (∃ m: ℕ, ∀ n: ℕ, u m = u n)
:=
/- dEAduction
pretty_name = "C implique D"
-/
begin
  todo,
end

lemma exercise.implication6
(u : ℕ → ℝ)  :
 (∃ m: ℕ, ∀ n: ℕ, u m = u n) → (∀ n, u n = u 0) 
:=
/- dEAduction
pretty_name = "D implique C"
-/
begin
  todo,
end

lemma exercise.implication7
(u : ℕ → ℝ)  :
(∃ c : ℝ, ∀ n: ℕ,  (u n = c))  → (∀ m n, u m = u n)
:=
/- dEAduction
pretty_name = "A implique B"
-/
begin
  todo,
end

lemma exercise.implication8
(u : ℕ → ℝ)  :
 (∀ m n, u m = u n) → (∃ c : ℝ, ∀ n: ℕ,  (u n = c))
:=
/- dEAduction
pretty_name = "B implique A"
-/
begin
  todo,
end

lemma exercise.implication9
(u : ℕ → ℝ)  :
(∃ c : ℝ, ∀ n: ℕ,  (u n = c))  → (∃ n: ℕ, ∀ m: ℕ, u n = u m)
:=
/- dEAduction
pretty_name = "A implique D"
-/
begin
  todo,
end

lemma exercise.implication10
(u : ℕ → ℝ)  :
 (∃ m: ℕ, ∀ n: ℕ, u m = u n) → (∃ c : ℝ, ∀ n: ℕ,  (u n = c))
:=
/- dEAduction
pretty_name = "D implique A"
-/
begin
  todo,
end

lemma exercise_equivalence
(u : ℕ → ℝ)  :
(∃ c, ∀ n: ℕ, u n = c) ↔ (∀ n: ℕ,  (u n = u (n+1)))
:=
begin
  todo,
end

end definitions_equivalentes

namespace non_definitions
/- dEAduction
pretty_name = """
"Définitions" incorrectes"""
-/

lemma exercise.incorrecte1  (u : ℕ → ℝ)  :
(∀ m: ℕ, ∃ n: ℕ, u m = u n) 
:=
/- dEAduction
pretty_name = "Suite constante ?"
-/
begin
  todo
end

end non_definitions

end suites_constantes

namespace a_partir_dun_certain_rang
/- dEAduction
pretty_name = "Propriétés vraies à partir d'un certain rang"
-/

lemma definition.suite_constante_rang (u : ℕ → RealSubGroup)  :
constante_a_partir_certain_rang u ↔
(∃ c: RealSubGroup, ∃ N:ℕ, ∀ n ≥ N, u n = c) :=
/- dEAduction
pretty_name = "Suite constante à partir d'un certain rang"
-/
begin
  refl,
end


lemma exercise.somme
(u v : ℕ → ℝ) (H: constante_a_partir_certain_rang u)
(H': constante_a_partir_certain_rang v) : 
constante_a_partir_certain_rang (λn, u n + v n) :=
/- dEAduction
pretty_name = "Somme de suites constantes"
-/
begin
  todo
end






end a_partir_dun_certain_rang

end course