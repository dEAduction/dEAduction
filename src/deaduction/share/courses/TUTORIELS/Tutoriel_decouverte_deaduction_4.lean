/-
This is a d∃∀duction file providing a tutorial about proof methods.
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
title = "Tutoriel partie 4 : méthodes de preuves"
author = "Isabelle Dubois / inspiré du fichier tutoriel de Frédéric"
institution = "Université de Lorraine"
description = """
Tutoriel d'utilisation du logiciel dans un contexte de manipulations des entiers ou réels
- Partie 4 : méthodes de preuves
"""
available_exercises = "NONE"
default_available_logic = "ALL -mapsto"
default_available_proof = "proof_methods"
default_available_magic = "Assumption"
available_compute = "NONE"
[display]
estquotiententier = [ -2, " / ", -1, " est entier"]
[settings]
logic.usr_jokers_available = false
logic.use_color_for_applied_properties = false
functionality.allow_induction = false
functionality.calculator_available = true
others.Lean_request_method = "normal"
-/

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
open nat
open set
variables {X : Type}

variables (P Q R: Prop) -- NOT global
notation [parsing_only] P ` \and ` Q := P ∧ Q
notation [parsing_only]  P ` \or ` Q := P ∨ Q
notation [parsing_only]  ` \not ` P := ¬ P
notation [parsing_only]  P ` \implies ` Q := P → Q
notation [parsing_only]  P ` \iff ` Q := P ↔ Q

variables {m n k: ℕ}

namespace decouverte_methodes_preuves
/- dEAduction
pretty_name = "Découverte des méthodes de preuves"
-/

lemma theorem.simplifier (H: m ≠ 0):
 (m*m = n*m)  → (m=n)
:=
/- dEAduction
pretty_name = "Simplifier une égalité entre produits"
-/
begin
    todo
end

lemma exercise.cas1 (H1 : m*m = n*m) :
  (m=0) \or (m=n)
:=
/- dEAduction
pretty_name = "Raisonnement par cas (1) -  Entiers"
description = "Raisonnement par cas (1) : on choisira de discuter suivant la valeur de m"
available_magic = "assumption"
-/
begin
    todo
end

lemma theorem.valeur_absolue_de_positif :
∀ x : ℝ,
((0 ≤ x) → (abs x = x)) :=
/- dEAduction
pretty_name = "Valeur absolue d'un nombre positif"
-/
begin
  intro x, exact abs_of_nonneg,
end

lemma theorem.valeur_absolue_de_negatif :
∀ x : ℝ,
((x < 0) → (abs x = -x)) :=
/- dEAduction
pretty_name = "Valeur absolue d'un nombre négatif"
-/
begin
  todo
end


lemma exercise.cas2 {x : ℝ} 
(H1 : |x-1| +|2*x-3| =6)
(H4 : (x-1 <0)→ (2*x - 3<0) ) :
(x=10/3) \or (x = -2/3)
:=
/- dEAduction
pretty_name = "Raisonnement par cas (2) -  Réels"
description = "Raisonnement par cas (2) (et contradiction dans hypothèses) -  Réels - Défi : Se ramener à 3 cas seulement !"
available_proof = "proof_methods"
available_magic = "assumption"
-/
begin
    todo
end

-- ( not(x=-3)) → (not( (x+1)/(x+3) = 1)) 

lemma exercise.contraposee0 {x y : ℝ} :
 ( not(x=y)) → (not( (x-1)*(y+1) = (x+1)*(y-1)))
:=
/- dEAduction
pretty_name = "Raisonnement par contraposée (0) - Réels."
description = "Raisonnement par contraposée - Réels"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.contraposee0b
{x y : ℝ} (H1: ∀ a : ℝ, ∀ b : ℝ, (a+a*b =a*(1+b)))
(H2: ∀ a : ℝ, ∀ b : ℝ,  (a*b +b = (a+1)*b))
(H3:  ∀ a : ℝ, ∀ b : ℝ, ((a*b = 0)  → ( (a=0) \or (b=0) ))):
(not(x=-1) \and not(y=-1)) → (not( (x+ x*y)+ (1+ y) =0))
:=
/- dEAduction
pretty_name = "Raisonnement par contraposée (0 bis) - Réels."
description = "Raisonnement par contraposée (0 bis) - Réels"
available_magic = "assumption"
-/
begin
    todo
end


def pair (m: nat) := ∃ k, m = 2*k 

def impair (m: nat) := ∃ k, m = 2*k + 1 



lemma definition.pair {m:nat} : (pair m) ↔ ∃ k, m = 2*k :=
/- dEAduction
pretty_name = "Pair"
implicit_use = true
-/
begin
  todo
end

lemma definition.impair {m:nat} : (impair m) ↔ ∃ k, m = 2*k + 1 :=
/- dEAduction
pretty_name = "Impair"
implicit_use = true
-/
begin
  todo
end

lemma theorem.nonimpair {m:nat} : (not((impair m))) ↔ (pair m) :=
/- dEAduction
pretty_name = "Non (Impair )"
implicit_use = true
-/
begin
 todo
end

lemma theorem.nonpair {m:nat} : (not((pair m))) ↔ (impair m) :=
/- dEAduction
pretty_name = "Non (Pair )"
implicit_use = true
-/
begin
 todo
end


lemma exercise.contraposee1  {n : ℕ}:
 (impair (n*n) ) → (impair n)
:=
/- dEAduction
pretty_name = "Raisonnement par contraposée (1) - Entiers."
description = "Raisonnement par contraposée (1) - Entiers - Parité."
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.contraposee2 {n : ℕ}:
 (pair (n*n) ) → (pair n)
:=
/- dEAduction
pretty_name = "Raisonnement par contraposée (2) - Entiers"
description = "Raisonnement par contraposée (2) - Entiers - Parité."
available_magic = "assumption"
-/
begin
    todo
end



lemma exercise.contraposee3 {a : ℝ}:
 (∀ y > (0:ℝ), a <= y) → (a<=0)
:=
/- dEAduction
pretty_name = "Raisonnement par contraposée  - Réels."
description = "Raisonnement par contraposée  - Réels."
available_definitions = "NONE"
available_theorems = "NONE"
available_magic = "assumption"
-/
begin
    todo
end


lemma exercise.absurde1
{x : ℝ} (H1: not(x=-3) )
(H2: ∀ a : ℝ, ∀ b : ℝ,  ((a/b = 1) \and (not(b=0)) ) → (a =b))
(H3: ∀ a : ℝ, ( not( x+a =0)) ↔ not (x = -a) ) :
not( (x+1) / (x+3) =1 )
:=
/- dEAduction
pretty_name = "Raisonnement par l'absurde (1) - Réels"
description = "Raisonnement par l'absurde (1) - Réels"
available_definitions = "NONE"
available_theorems = "NONE"
available_magic = "assumption"
-/
begin
    todo
end



lemma theorem.produit_egal_un
{m n :ℤ} : (m*n = 1)  <-> (((m=1) \and (n=1)) \or ((m=-1) \and (n=-1)))
:=
/- dEAduction
pretty_name = "Produit d'entiers relatif égal à 1"
implicit_use = true
-/
begin
 todo
end

lemma exercise.absurde2 {m n : ℤ} :
not(18*m +6*n = 1)
:=
/- dEAduction
pretty_name = "Raisonnement par l'absurde (2) - Entiers relatifs"
description = "Raisonnement par l'absurde (2) - Entiers relatifs - Attention : Introduire un nouveau but si nécessaire !"
available_definitions = "NONE"
available_theorems = "produit_egal_un"
available_proof = "proof_methods new_object"
available_magic = "assumption"
-/
begin
    todo
end

lemma theorem.identite_remarquable {a b : ℤ} :
a^2 - b^2 = (a-b)*(a+b)
:=
/- dEAduction
pretty_name = "Identité Remarquable a^2 -b^2"
implicit_use = true
-/
begin
 todo
end

lemma exercise.absurde3
{n : ℤ}  (Hypothese: not(n=0)) :
not(∃ m, n^2 +1 = m^2)
:=
/- dEAduction
pretty_name = "Raisonnement par l'absurde (3) - Entiers"
description = "Raisonnement par l'absurde (3) - Entiers  - Attention : Introduire un nouveau but si nécessaire !"
available_definitions = "NONE"
available_theorems = "produit_egal_un, identite_remarquable"
available_proof = "proof_methods new_object"
available_magic = "assumption"
-/
begin
    todo
end


def estquotiententier (m: nat) (n: nat) :=
 ∃ k : ℕ, m = k*n

lemma definition.estquotiententier {m: nat} {n: nat} : 
(estquotiententier m n ) ↔ (∃ k : ℕ, m = k*n) 
:=
/- dEAduction
pretty_name = "Est Quotient entier"
implicit_use = true
-/
begin
 todo
end

lemma theorem.condition_etre_pair :
∀ m :ℕ, ( (∃ k, m = 2*k ) -> (pair m) ) :=
/- dEAduction
pretty_name = "Condition pour être pair"
implicit_use = true
-/
begin
  todo
end

lemma exercise.absurde4
{m n : ℕ}   (H1: pair m) (H2: impair n) :
not(estquotiententier n m )
:=
/- dEAduction
pretty_name = "Raisonnement par l'absurde (4) - Entiers"
description = """
Raisonnement par l'absurde (4)  - Entiers -
Indication : Utiliser le nouveau théorème "condition pour être pair" (une implication de la définition), ou alors introduire un nouveau but.
"""
available_proof = "proof_methods new_object"
available_magic = "assumption"
-/
begin
    todo
end


lemma definition.intersection_deux_ensembles
{A B : set X} {x : X} :
x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B)
:=
/- dEAduction
pretty_name = "Intersection de deux ensembles"
implicit_use = true
-/
begin
    todo
end

lemma auxiliary_definition.ensemble_non_vide
(A: set X) :
(not (A = ∅) ) ↔ ∃ x : X, x ∈ A
:=
begin
    todo
end

lemma definition.ensemble_non_vide
(A: set X) :
((A ≠ ∅) ) ↔ ∃ x : X, x ∈ A
:=
/- dEAduction
auxiliary_definitions = "auxiliary_definition.ensemble_non_vide"
implicit_use = true
-/
begin
    todo
end

lemma definition.difference
(A B : set X) (x : X) :
x ∈ (A \ B) ↔ x ∈ A ∧ x ∉ B
:=
/- dEAduction
pretty_name = "Différence de deux ensembles"
-/
begin
    todo
end

lemma exercise.absurde5
{A B : set X} :
A  ∩ ( B \ A)  = ∅ 
:=
/- dEAduction
pretty_name = "Raisonnement par l'absurde (5) - Ensembles"
description = "Raisonnement par l'absurde (5) - Ensembles"
available_theorems = "NONE"
available_definitions = "intersection_deux_ensembles, difference, ensemble_non_vide"
available_proof = "proof_methods"
available_magic = "assumption"
-/
begin
    todo
end


end decouverte_methodes_preuves

end course
