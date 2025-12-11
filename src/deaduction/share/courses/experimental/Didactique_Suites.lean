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
title = "Suites"
author = "Frédéric Le Roux"
institution = "Université du monde"
description = """
Des exercices sur les limites des suites
et la continuité des fonctions
"""
[settings]
logic.usr_jokers_available = true
logic.use_color_for_applied_properties = true
functionality.allow_induction = false
functionality.calculator_available = true
others.Lean_request_method = "from_previous_proof_state"
logs.save_journal = true
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

lemma exercise.implication1
(u : ℕ → ℝ)  :
(∀ n, u n = u 0)  → (∃ c : ℝ, ∀ n: ℕ,  (u n = c))
:=
/- dEAduction
pretty_name = "Implication prop 3 vers prop 1"
-/
begin
  todo,
end

lemma exercise.implication2
(u : ℕ → ℝ)  :
 (∃ c : ℝ, ∀ n: ℕ,  (u n = c)) → (∀ n, u n = u 0) 
:=
/- dEAduction
pretty_name = "Implication prop 1 vers prop 3"
-/
begin
  todo,
end



lemma exercise.implication3
(u : ℕ → ℝ)  :
(∀ n, u n = u 0)  → (∀ n m, u n = u m)
:=
/- dEAduction
pretty_name = "Implication prop 3 vers prop 2"
-/
begin
  todo,
end

lemma exercise.implication4
(u : ℕ → ℝ)  :
 (∀ n m, u n = u m) → (∀ n, u n = u 0) 
:=
/- dEAduction
pretty_name = "Implication prop 2 vers prop 3"
-/
begin
  todo,
end





lemma exercise.implication5
(u : ℕ → ℝ)  :
(∀ n, u n = u 0)  → (∃ n: ℕ, ∀ m: ℕ, u n = u m)
:=
/- dEAduction
pretty_name = "Implication prop 3 vers prop 5"
-/
begin
  todo,
end

lemma exercise.implication6
(u : ℕ → ℝ)  :
 (∃ n: ℕ, ∀ m: ℕ, u n = u m) → (∀ n, u n = u 0) 
:=
/- dEAduction
pretty_name = "Implication prop 5 vers prop 3"
-/
begin
  todo,
end

lemma exercise.implication7
(u : ℕ → ℝ)  :
(∃ c : ℝ, ∀ n: ℕ,  (u n = c))  → (∀ n m, u n = u m)
:=
/- dEAduction
pretty_name = "Implication prop 1 vers prop 2"
-/
begin
  todo,
end

lemma exercise.implication8
(u : ℕ → ℝ)  :
 (∀ n m, u n = u m) → (∃ c : ℝ, ∀ n: ℕ,  (u n = c))
:=
/- dEAduction
pretty_name = "Implication prop 2 vers prop 1"
-/
begin
  todo,
end

lemma exercise.implication9
(u : ℕ → ℝ)  :
(∃ c : ℝ, ∀ n: ℕ,  (u n = c))  → (∃ n: ℕ, ∀ m: ℕ, u n = u m)
:=
/- dEAduction
pretty_name = "Implication prop 1 vers prop 5"
-/
begin
  todo,
end

lemma exercise.implication10
(u : ℕ → ℝ)  :
 (∃ n: ℕ, ∀ m: ℕ, u n = u m) → (∃ c : ℝ, ∀ n: ℕ,  (u n = c))
:=
/- dEAduction
pretty_name = "Implication prop 5 vers prop 1"
-/
begin
  todo,
end



end suites_constantes

namespace limite_positive
/- dEAduction
pretty_name = "Limites positives"
-/


lemma exercise.limite_positive
(u : ℕ → ℝ) (l : ℝ) (H : limit u l)
(H' : l >0) :
∃ N, ∀ n ≥ N, u n > 0
:=
/- dEAduction
pretty_name = "Suite dont la limite est strictement positive"
-/
begin
  todo,
end

end limite_positive



namespace limite_infinie_croissante
/- dEAduction
pretty_name = "Limite infinie"
-/


lemma exercise.infinie_pas_majoree
(u: ℕ → ℝ):
(limit_plus_infinity u → not (bounded_above u))
or
((not bounded_above u) → limit_plus_infinity u)
:=
/- dEAduction
pretty_name = "Tendre vers plus l'infini et ne pas être majorée"
-/
begin
  todo,
end

lemma exercise.croissante_non_majoree
(u: ℕ → ℝ) (H1: increasing_seq u) (H2: not (bounded_above u)) :
limit_plus_infinity u :=
/- dEAduction
pretty_name = "Une suite croissante non majorée tend vers plus l'infini"
-/
begin
  todo,
end

end limite_infinie_croissante



namespace limite_infinie_pas_finie
/- dEAduction
pretty_name = "Limite infinie et convergence"
-/

lemma exercise.limite_infinie_pas_finie
(u : ℕ → ℝ):
limit_plus_infinity u → not (converging_seq u)
:=
/- dEAduction
pretty_name = "Limite infinie et convergence"
-/
begin
--  `[ `[ rw definitions.suites.definition.converging_seq, trace "EFFECTIVE CODE n°1.0"] <|> `[ simp_rw definitions.suites.definition.converging_seq, trace "EFFECTIVE CODE n°1.1"] <|> `[ rw <- definitions.suites.definition.converging_seq, trace "EFFECTIVE CODE n°1.2"] <|> `[ simp_rw <- definitions.suites.definition.converging_seq, trace "EFFECTIVE CODE n°1.3"], `[ simp only [] , trace "EFFECTIVE CODE n°2.0"] <|> `[ skip, trace "EFFECTIVE CODE n°2.1"], all_goals_no_meta_vars, trace "EFFECTIVE CODE n°0.0"] <|> `[ apply_with definitions.suites.definition.converging_seq {md:=reducible}, all_goals_no_meta_vars, trace "EFFECTIVE CODE n°0.1"],
  todo,
end

end limite_infinie_pas_finie

end course