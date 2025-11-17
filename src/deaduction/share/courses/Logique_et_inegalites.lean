/-
This is a d∃∀duction file providing first exercises about quantifiers and numbers.
French version.
-/

-- Lean standard import
import data.real.basic
import tactic

-- dEAduction tactics
-- structures2 and utils are vital
import deaduction_all_tactics
-- import structures2      -- hypo_analysis, targets_analysis
-- import utils            -- no_meta_vars
-- import compute_all      -- Tactics for the compute buttons
-- import push_neg_once    -- Pushing negation just one step
-- import induction        -- Induction theorems

-- dEAduction definitions
-- import set_definitions
-- import real_definitions

-- Use classical logic
local attribute [instance] classical.prop_decidable


-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement (since it will be called with 'rw' or 'symp_rw')



---------------------
-- Course metadata --
---------------------
/- dEAduction
author = "Frédéric Le Roux"
institution = "Université de France"
title = "VRAI/FAUX : Logique et inégalités"
description = """
Ce fichier contient quelques exercices de base
impliquant des quantificateurs et des inégalités.
Certains buts sont vrais et d'autres faux :
avant de commencer l'exercice,
vous choisirez ce que vous voulez prouver,
le but ou sa négation.
"""
open_question = true
available_exercises = "NONE"
available_logic = "ALL -not"
[settings]
logic.usr_jokers_available = true
logic.use_color_for_applied_properties = false
functionality.allow_induction = false
functionality.calculator_available = true
others.Lean_request_method = "normal"
-/

-- If OpenQuestion is True, DEAduction will ask the user if she wants to
-- prove the statement or its negation, and set the variable
-- NegateStatement accordingly
-- If NegateStatement is True, then the statement will be replaced by its
-- negation
-- AvailableExercises is set to None so that no exercise statement can be applied
-- by the user. Recommended with OpenQuestions set to True!


local attribute [instance] classical.prop_decidable

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course

namespace Logique_et_nombres_reels
/- dEAduction
pretty_name = "Logique et nombres réels"
-/

namespace negation
/- dEAduction
pretty_name = "Enoncés de négation"
-/

lemma theorem.negation_et {P Q : Prop} :
( not (P and Q) ) ↔ ( (not P) or (not Q) )
:=
/- dEAduction
pretty_name = "Négation du 'et'"
-/
begin
    exact not_and_distrib
end

lemma theorem.negation_ou {P Q : Prop} :
( not (P or Q) ) ↔ ( (not P) and (not Q) )
:=
/- dEAduction
pretty_name = "Négation du 'ou'"
-/
begin
    exact not_or_distrib
end

lemma theorem.negation_non {P : Prop} :
( not not P ) ↔  P
:=
/- dEAduction
pretty_name = "Négation du 'non'"
-/
begin
    exact not_not
end


lemma theorem.negation_implique {P Q : Prop} :
( not (P → Q) ) ↔  ( P and (not Q) )
:=
/- dEAduction
pretty_name = "Négation d'une implication"
-/
begin
    exact not_imp,
end


lemma theorem.negation_existe  {X : Type} {P : X → Prop} :
( ( not ∃ (x:X), P x  ) ↔ ∀ x:X, not P x )
:=
/- dEAduction
pretty_name = "Négation de '∃X, P(x)'"
-/
begin
    exact not_exists,
end



lemma theorem.negation_pour_tout {X : Type} {P : X → Prop} :
( not (∀x, P x ) ) ↔ ∃x, not P x
:=
/- dEAduction
pretty_name = "Négation de '∀x, P(x)'"
-/
begin
    exact not_forall
end


lemma theorem.negation_inegalite_stricte {X : Type} (x y : X) [linear_order X]:
( not (x < y) ) ↔ y ≤ x
:=
/- dEAduction
pretty_name = "Négation de 'x < y'"
-/
begin
    exact not_lt
end


lemma theorem.negation_inegalite_large {X : Type} (x y : X) [linear_order X]:
( not (x ≤ y) ) ↔ y < x
:=
/- dEAduction
pretty_name = "Négation de 'x ≤ y'"
-/
begin
    exact not_le
end

lemma theorem.double_negation (P: Prop) :
(not not P) ↔ P :=
/- dEAduction
pretty_name = "Double négation"
-/
begin
    todo
end


end negation

namespace exercices
/- dEAduction
pretty_name = "Exercices"
-/



lemma exercise.zero_ou_un : ∀ n:ℕ, (n ≠ 0 or n ≠ 1)
:=
/- dEAduction
pretty_name = "Pas zéro ou pas un"
-/
begin
    todo
end

lemma exercise.zero_ou_un_2 : ∀ n:ℕ, (n = 0 or n = 1)
:=
/- dEAduction
pretty_name = "Zéro ou un ou ?..."
-/
begin
    todo
end


lemma exercise.plus_petit : ∃ m:ℕ, ∀ n:ℕ, m ≤ n
:=
/- dEAduction
pretty_name = "Plus petit que tous"
-/
begin
    todo
end


lemma exercise.vraiment_plus_petit : ∃ m:ℤ, ∀ n:ℤ, m ≤ n
:=
/- dEAduction
pretty_name = "Plus petit que tous..."
-/
begin
    todo
end


lemma exercise.positif :
(∀x:ℝ, ∃y:ℝ, x+y >0)
:=
/- dEAduction
pretty_name = "Positif"
-/
begin
    todo
end



lemma exercise.egalite : ∀ n:ℕ, ∃ m:ℕ, m=n
:=
/- dEAduction
pretty_name = "Tous égaux"
-/
begin
    todo
end


lemma exercise.egalite_2 :
∃ m:ℕ, ∀ n:ℕ, m=n
:=
/- dEAduction
pretty_name = "Egaux à tous !"
-/
begin
    todo
end

-- Marche bien par l'absurde, ou directement
lemma exercise.tres_petit :
∀ a ≥ (0:ℝ), ∀ ε ≥ (0:ℝ), (a ≤ ε → a = 0)
:=
/- dEAduction
pretty_name = "Très petit"
-/
begin
    todo
end


lemma exercise.tres_petit_2 :
∀ a ≥ (0:ℝ), ((∀ ε ≥ (0:ℝ), a ≤ ε) → a = 0)
:=
/- dEAduction
pretty_name = "Ca se complique"
simplification_compute = "$ALL"
-/
begin
    todo
end


-- Utiliser la preuve par contrapposée
lemma exercise.tres_petit_3 :
∀ a ≥ (0:ℝ), ((∀ ε > (0:ℝ), a ≤ ε) → a = 0)
:=
/- dEAduction
pretty_name = "Trop compliqué !"
-/
begin
    todo
end


lemma exercise.entre_deux_entiers :
∀x:ℤ, ∀y:ℤ, (x<y → (∃z:ℤ, x < z and z < y))
:=
/- dEAduction
pretty_name = "Entre deux entiers"
-/
begin
    todo
end


lemma exercise.entre_deux_reels :
∀x:ℝ, ∀y:ℝ, (x<y → (∃z:ℝ, x < z and z < y))
:=
/- dEAduction
pretty_name = "Entre deux réels"
-/
begin
    todo
end

end exercices

end Logique_et_nombres_reels

end course