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
Title
    Tutoriel partie 4 : méthodes de preuves
Author
    Isabelle Dubois / inspiré du fichier tutoriel de Frédéric
Institution
    Université de Lorraine
Description
    Tutoriel d'utilisation du logiciel dans un contexte de manipulations des entiers ou réels
    - Partie 4 : méthodes de preuves
AvailableExercises
    NONE
DefaultAvailableLogic
    ALL -mapsto
DefaultAvailableProof
    proof_methods 
DefaultAvailableMagic
    Assumption
AvailableCompute
    NONE
Display
   estquotiententier --> ( -2, " / ", -1, " est entier") 
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
PrettyName
 Découverte des méthodes de preuves
-/

lemma theorem.simplifier (H: m ≠ 0):
 (m*m = n*m)  → (m=n)
:=
/- dEAduction
PrettyName
    Simplifier une égalité entre produits
-/
begin
    todo
end

lemma exercise.cas1 (H1 : m*m = n*m) :
  (m=0) \or (m=n)
:=
/- dEAduction
PrettyName
    Raisonnement par cas (1) -  Entiers  
Description
    Raisonnement par cas (1) : on choisira de discuter suivant la valeur de m
  
AvailableMagic
    assumption
-/
begin
    todo
end

lemma theorem.valeur_absolue_de_positif :
∀ x : ℝ,
((0 ≤ x) → (abs x = x)) :=
/- dEAduction
PrettyName
  Valeur absolue d'un nombre positif
-/
begin
  intro x, exact abs_of_nonneg,
end

lemma theorem.valeur_absolue_de_negatif :
∀ x : ℝ,
((x < 0) → (abs x = -x)) :=
/- dEAduction
PrettyName
  Valeur absolue d'un nombre négatif
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
PrettyName
    Raisonnement par cas (2) -  Réels 
Description
    Raisonnement par cas (2) (et contradiction dans hypothèses) -  Réels - Défi : Se ramener à 3 cas seulement !
AvailableProof
   proof_methods

AvailableMagic
    assumption
-/
begin
    todo
end

-- ( not(x=-3)) → (not( (x+1)/(x+3) = 1)) 

lemma exercise.contraposee0 {x y : ℝ} :
 ( not(x=y)) → (not( (x-1)*(y+1) = (x+1)*(y-1)))
:=
/- dEAduction
PrettyName
    Raisonnement par contraposée (0) - Réels.
Description
    Raisonnement par contraposée - Réels

AvailableMagic
    assumption
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
PrettyName
    Raisonnement par contraposée (0 bis) - Réels.
Description
    Raisonnement par contraposée (0 bis) - Réels 

AvailableMagic
    assumption
-/
begin
    todo
end


def pair (m: nat) := ∃ k, m = 2*k 

def impair (m: nat) := ∃ k, m = 2*k + 1 



lemma definition.pair {m:nat} : (pair m) ↔ ∃ k, m = 2*k :=
/- dEAduction
PrettyName
  Pair
ImplicitUse
  True
-/
begin
  todo
end

lemma definition.impair {m:nat} : (impair m) ↔ ∃ k, m = 2*k + 1 :=
/- dEAduction
PrettyName
  Impair
ImplicitUse
  True
-/
begin
  todo
end

lemma theorem.nonimpair {m:nat} : (not((impair m))) ↔ (pair m) :=
/- dEAduction
PrettyName
  Non (Impair )
ImplicitUse
  True
-/
begin
 todo
end

lemma theorem.nonpair {m:nat} : (not((pair m))) ↔ (impair m) :=
/- dEAduction
PrettyName
  Non (Pair )
ImplicitUse
  True
-/
begin
 todo
end


lemma exercise.contraposee1  {n : ℕ}:
 (impair (n*n) ) → (impair n)
:=
/- dEAduction
PrettyName
    Raisonnement par contraposée (1) - Entiers.
Description
    Raisonnement par contraposée (1) - Entiers - Parité.

AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.contraposee2 {n : ℕ}:
 (pair (n*n) ) → (pair n)
:=
/- dEAduction
PrettyName
    Raisonnement par contraposée (2) - Entiers
Description
    Raisonnement par contraposée (2) - Entiers - Parité.

AvailableMagic
    assumption
-/
begin
    todo
end



lemma exercise.contraposee3 {a : ℝ}:
 (∀ y > (0:ℝ), a <= y) → (a<=0)
:=
/- dEAduction
PrettyName
    Raisonnement par contraposée  - Réels.
Description
    Raisonnement par contraposée  - Réels.
AvailableDefinitions
	NONE
AvailableTheorems
	NONE
AvailableMagic
    assumption
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
PrettyName
    Raisonnement par l'absurde (1) - Réels
Description
    Raisonnement par l'absurde (1) - Réels
AvailableDefinitions
	NONE
AvailableTheorems
	NONE
AvailableMagic
    assumption
-/
begin
    todo
end



lemma theorem.produit_egal_un
{m n :ℤ} : (m*n = 1)  <-> (((m=1) \and (n=1)) \or ((m=-1) \and (n=-1)))
:=
/- dEAduction
PrettyName
  Produit d'entiers relatif égal à 1
ImplicitUse
  True
-/
begin
 todo
end

lemma exercise.absurde2 {m n : ℤ} :
not(18*m +6*n = 1)
:=
/- dEAduction
PrettyName
     Raisonnement par l'absurde (2) - Entiers relatifs
Description
     Raisonnement par l'absurde (2) - Entiers relatifs - Attention : Introduire un nouveau but si nécessaire !
AvailableDefinitions
	NONE
AvailableTheorems
	produit_egal_un

AvailableProof
    proof_methods new_object
AvailableMagic
    assumption
-/
begin
    todo
end

lemma theorem.identite_remarquable {a b : ℤ} :
a^2 - b^2 = (a-b)*(a+b)
:=
/- dEAduction
PrettyName
  Identité Remarquable a^2 -b^2
ImplicitUse
  True
-/
begin
 todo
end

lemma exercise.absurde3
{n : ℤ}  (Hypothese: not(n=0)) :
not(∃ m, n^2 +1 = m^2)
:=
/- dEAduction
PrettyName
     Raisonnement par l'absurde (3) - Entiers 
Description
     Raisonnement par l'absurde (3) - Entiers  - Attention : Introduire un nouveau but si nécessaire !
AvailableDefinitions
	NONE
AvailableTheorems
	produit_egal_un, identite_remarquable
AvailableProof
    proof_methods new_object
AvailableMagic
    assumption
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
PrettyName
  Est Quotient entier
ImplicitUse
  True
-/
begin
 todo
end

lemma theorem.condition_etre_pair :
∀ m :ℕ, ( (∃ k, m = 2*k ) -> (pair m) ) :=
/- dEAduction
PrettyName
  Condition pour être pair
ImplicitUse
  True
-/
begin
  todo
end

lemma exercise.absurde4
{m n : ℕ}   (H1: pair m) (H2: impair n) :
not(estquotiententier n m )
:=
/- dEAduction
PrettyName
     Raisonnement par l'absurde (4) - Entiers
Description
     Raisonnement par l'absurde (4)  - Entiers - 
     
     Indication : Utiliser le nouveau théorème "condition pour être pair" (une implication de la définition), ou alors introduire un nouveau but.
AvailableProof
    proof_methods new_object
AvailableMagic
    assumption
-/
begin
    todo
end


lemma definition.intersection_deux_ensembles
{A B : set X} {x : X} :
x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B)
:=
/- dEAduction
PrettyName
    Intersection de deux ensembles
ImplicitUse
    True
-/
begin
    todo
end

lemma definition.ensemble_non_vide
(A: set X) :
((A ≠ ∅) ) ↔ ∃ x : X, x ∈ A
:=
/- dEAduction
ImplicitUse
  True
-/
begin
    todo
end

lemma definition.difference
(A B : set X) (x : X) :
x ∈ (A \ B) ↔ x ∈ A ∧ x ∉ B
:=
/- dEAduction
PrettyName
    Différence de deux ensembles
-/
begin
    todo
end

lemma exercise.absurde5
{A B : set X} :
A  ∩ ( B \ A)  = ∅ 
:=
/- dEAduction
PrettyName
     Raisonnement par l'absurde (5) - Ensembles  
Description
     Raisonnement par l'absurde (5) - Ensembles  
AvailableTheorems
	NONE
AvailableDefinitions
	intersection_deux_ensembles, difference, ensemble_non_vide	
AvailableProof
    proof_methods
AvailableMagic
    assumption
-/
begin
    todo
end


end decouverte_methodes_preuves

end course

