/-
Feuille d'exercice pour travailler le raisonnement par récurrence sur N 
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
-- import real_definitions

-- Use classical logic
local attribute [instance] classical.prop_decidable


/- dEAduction
title = "Démonstration par récurrence"
author = "Isabelle Dubois"
institution = "Université de Lorraine"
description = "Exercices sur la récurrence"
available_exercises = "NONE"
[settings]
functionality.calculator_available = true
others.Lean_request_method = "normal"
-/


-- logic names ['and', 'or', 'not', 'implies', 'iff', 'forall', 'exists']
-- proofs names ['proof_methods', 'new_object', 'apply']
-- magic names ['compute', 'assumption']


local attribute [instance] classical.prop_decidable
---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
open nat


namespace recurrence



def pair (m: nat) := ∃ k, m = 2*k 

def impair (m: nat) := ∃ k, m = 2*k + 1 



lemma definition.pair {m:nat} : (pair m) ↔ ∃ k, m = 2*k :=
/- dEAduction
pretty_name = "Pair"
implicit_use = true
-/
begin
  refl,
end

lemma definition.impair {m:nat} : (impair m) ↔ ∃ k, m = 2*k + 1 :=
/- dEAduction
pretty_name = "Impair"
implicit_use = true
-/
begin
  refl,
end



lemma exercise.pair_ou_impair : ∀n: nat, (pair n ∨ impair n) :=
/- dEAduction
pretty_name = "Pair ou impair"
description = "Tout entier est pair ou impair, à démontrer par récurrence"
-/
begin
    todo
end

lemma theorem.puissance1  : ∀ a: ℤ , ∀ n: nat, a^(n+1) = (a^n)*a :=
/- dEAduction
pretty_name = "Propriété Puissance (Entiers relatifs)"
implicit_use = true
-/
begin
  todo
end

lemma theorem.puissance2  : ∀ x: ℝ , ∀ n: nat, x^(n+1) = (x^n)*x :=
/- dEAduction
pretty_name = "Propriété Puissance (Réels)"
implicit_use = true
-/
begin
  todo
end

lemma exercise.suite_arithmetico_geometrique {u : ℕ → ℤ} (H1 : u 0 = 3 ) (H2 :  ∀n: nat, u (n+1) = 3*(u n) - 2 ) : ∀n: nat, ( u n = 2 *( (3^n))+1 ):=
/- dEAduction
pretty_name = "Suite définie par récurrence arithmético-géométrique"
description = "Suite définie par récurrence de type arithmético-géométrique - Formule explicite à démontrer par récurrence"
available_definitions = "NONE"
available_theorems = "puissance1"
-/
begin
    todo
end




lemma exercise.suite_geometrique {p q : ℝ } {u : ℕ →  ℝ } (H1 : u 0 = p) (H2 :  ∀n: nat, u (n+1) = q*(u n) ) : ∀n: nat, ( u n = p *( q^n) ):=
/- dEAduction
pretty_name = "Suite définie par récurrence géométrique"
description = "Suite définie par récurrence de type géométrique - Formule explicite à démontrer par récurrence"
available_definitions = "NONE"
available_theorems = "puissance2"
-/
begin
    todo
end

def divides (a b:ℤ) := ∃ c, b = a * c

lemma definition.divise {a b : ℤ} : (divides a b) ↔ (∃ c, b = a * c) :=
/- dEAduction
pretty_name = "Divise"
implicit_use = true
-/
begin
  todo
end

lemma exercise.quatre_divise : ∀n: nat, divides (4) (3^n -(-1)^n) :=
/- dEAduction
pretty_name = "Divisibilité par 4"
description = "Divisibilité par 4 d'une expression dépendant de n,  à démontrer par récurrence"
available_definitions = "divise"
available_theorems = "puissance1"
-/
begin
  todo
end

lemma theorem.puissance3  : ∀ m: nat , ∀ n: nat, m^(n+1) = (m^n)*m :=
/- dEAduction
pretty_name = "Propriété Puissance (Entiers naturels)"
implicit_use = true
-/
begin
  todo
end

lemma exercise.heredite_seule :  ( ∀n: nat, ( pair (3^n)  → pair (3^(n+1) ) ) ) and (∀n: nat, ( impair (3^n) )) :=
/- dEAduction
pretty_name = "Propriété héréditaire mais fausse"
description = "Propriété héréditaire mais qui est toujours fausse."
available_definitions = "pair, impair"
available_theorems = "puissance3"
-/
begin
    todo
end


end recurrence

end course
