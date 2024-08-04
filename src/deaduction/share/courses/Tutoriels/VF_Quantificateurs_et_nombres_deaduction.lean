/-
This is a d∃∀duction file providing first exercises about quantifiers and numbers.
French version.
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
-- import set_definitions
import real_definitions

-- Use classical logic
local attribute [instance] classical.prop_decidable

/- dEAduction
Author
    Isabelle Dubois
Institution
    Université de Lorraine
Title
    Logique avec prédicat, nombres, égalités et inégalités
Description
    Ce fichier contient quelques exercices de base
    impliquant des quantificateurs et relations algébriques entre nombres.
    Certains buts sont vrais et d'autres faux :
    avant de commencer l'exercice,
    vous choisirez ce que vous voulez prouver,
    le but ou sa négation.
OpenQuestion
    True
AvailableExercises
    NONE
AvailableLogic
    ALL -not
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



lemma theorem.negation_et {P Q : Prop} :
( not (P and Q) ) ↔ ( (not P) or (not Q) )
:=
/- dEAduction
PrettyName
    Négation du 'et'
-/
begin
    exact not_and_distrib
end

lemma theorem.negation_ou {P Q : Prop} :
( not (P or Q) ) ↔ ( (not P) and (not Q) )
:=
/- dEAduction
PrettyName
    Négation du 'ou'
-/
begin
    exact not_or_distrib
end

lemma theorem.double_negation (P: Prop) :
(not not P) ↔ P :=
/- dEAduction
PrettyName
    Double négation
-/
begin
    todo
end




lemma theorem.negation_implique {P Q : Prop} :
( not (P → Q) ) ↔  ( P and (not Q) )
:=
/- dEAduction
PrettyName
    Négation d'une implication
-/
begin
    exact not_imp,
end


lemma theorem.negation_existe  {X : Type} {P : X → Prop} :
( ( not ∃ (x:X), P x  ) ↔ ∀ x:X, not P x )
:=
/- dEAduction
PrettyName
    Négation de '∃X, P(x)'
-/
begin
    exact not_exists,
end



lemma theorem.negation_pour_tout {X : Type} {P : X → Prop} :
( not (∀x, P x ) ) ↔ ∃x, not P x
:=
/- dEAduction
PrettyName
    Négation de '∀x, P(x)'
-/
begin
    exact not_forall
end

lemma theorem.negation_nonegalite {X : Type} (x y : X) [linear_order X]:
( not (x ≠ y) ) ↔ x = y
:=
/- dEAduction
PrettyName
    Négation de 'x ≠ y'
-/
begin
    todo 
end

lemma theorem.negation_inegalite_stricte {X : Type} (x y : X) [linear_order X]:
( not (x < y) ) ↔ y ≤ x
:=
/- dEAduction
PrettyName
    Négation de 'x < y'
-/
begin
    exact not_lt
end


lemma theorem.negation_inegalite_large {X : Type} (x y : X) [linear_order X]:
( not (x ≤ y) ) ↔ y < x
:=
/- dEAduction
PrettyName
    Négation de 'x ≤ y'
-/
begin
    exact not_le
end





lemma exercise.existence1 : ∃ x:ℝ, x^2=1
:=
/- dEAduction
PrettyName
    Existence - premier exercice
-/
begin
    todo
end

lemma exercise.existence2 : ∃ x:ℤ, x^2+1=0
:=
/- dEAduction
PrettyName
    Existence - deuxième exercice
-/
begin
    todo
end

lemma exercise.pourtout1 : ∀ m:ℤ, 2*m+1=3
:=
/- dEAduction
PrettyName
    Pour tout - premier exercice
-/
begin
    todo
end

lemma exercise.pourtout2 : ∀  n:ℕ, 3*n+2 ≠ 7
:=
/- dEAduction
PrettyName
    Pour tout - deuxième exercice
-/
begin
    todo
end

lemma exercise.pourtoutexiste1 : ∀ x:ℝ, ∃ y:ℝ, y=x^2
:=
/- dEAduction
PrettyName
    Pour tout - Il existe - premier exercice
-/
begin
    todo
end

lemma exercise.pourtoutexiste2 : ∀ y:ℝ, ∃ x:ℝ, y=x^2
:=
/- dEAduction
PrettyName
    Pour tout - Il existe - Deuxième exercice
-/
begin
    todo
end

lemma exercise.existepourtout1 : ∃  x:ℝ, ∀ y:ℝ, y=x^2
:=
/- dEAduction
PrettyName
     Il existe - Pour tout -premier exercice
-/
begin
    todo
end

lemma exercise.existepourtout2 : ∃  y:ℝ, ∀ x:ℝ, y=x^2
:=
/- dEAduction
PrettyName
     Il existe - Pour tout - Deuxième exercice
-/
begin
    todo
end


lemma exercise.pourtoutpourtout : ∀ x:ℤ, ∀ y:ℤ, 1 ≤ |x-y| 
:=
/- dEAduction
PrettyName
     Pour tout - Pour tout - Valeur absolue
-/
begin
    todo
end



end course




