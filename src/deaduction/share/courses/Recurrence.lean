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
Title
    Démonstration par récurrence
    -
Author
    Isabelle Dubois 
Institution
    Université de Lorraine
Description
    Exercices sur la récurrence
AvailableExercises
    NONE
Settings
    functionality.calculator_available --> true
    others.Lean_request_method --> "normal"  
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
PrettyName
  Pair
ImplicitUse
  True
-/
begin
  refl,
end

lemma definition.impair {m:nat} : (impair m) ↔ ∃ k, m = 2*k + 1 :=
/- dEAduction
PrettyName
  Impair
ImplicitUse
  True
-/
begin
  refl,
end



lemma exercise.pair_ou_impair : ∀n: nat, (pair n ∨ impair n) :=
/- dEAduction
PrettyName
  Pair ou impair
Description
   Tout entier est pair ou impair, à démontrer par récurrence
-/
begin
    todo
end

lemma theorem.puissance1  : ∀ a: ℤ , ∀ n: nat, a^(n+1) = (a^n)*a :=
/- dEAduction
PrettyName
  Propriété Puissance (Entiers relatifs)
ImplicitUse
  True
-/
begin
  todo
end

lemma theorem.puissance2  : ∀ x: ℝ , ∀ n: nat, x^(n+1) = (x^n)*x :=
/- dEAduction
PrettyName
  Propriété Puissance (Réels)
ImplicitUse
  True
-/
begin
  todo
end

lemma exercise.suite_arithmetico_geometrique {u : ℕ → ℤ} (H1 : u 0 = 3 ) (H2 :  ∀n: nat, u (n+1) = 3*(u n) - 2 ) : ∀n: nat, ( u n = 2 *( (3^n))+1 ):=
/- dEAduction
PrettyName
  Suite définie par récurrence arithmético-géométrique
Description
   Suite définie par récurrence de type arithmético-géométrique - Formule explicite à démontrer par récurrence
AvailableDefinitions
	NONE
AvailableTheorems
   puissance1
-/
begin
    todo
end




lemma exercise.suite_geometrique {p q : ℝ } {u : ℕ →  ℝ } (H1 : u 0 = p) (H2 :  ∀n: nat, u (n+1) = q*(u n) ) : ∀n: nat, ( u n = p *( q^n) ):=
/- dEAduction
PrettyName
  Suite définie par récurrence géométrique
Description
   Suite définie par récurrence de type géométrique - Formule explicite à démontrer par récurrence
AvailableDefinitions
	NONE
AvailableTheorems
   puissance2
-/
begin
    todo
end

def divides (a b:ℤ) := ∃ c, b = a * c

lemma definition.divise {a b : ℤ} : (divides a b) ↔ (∃ c, b = a * c) :=
/- dEAduction
PrettyName
  Divise
ImplicitUse
  True
-/
begin
  todo
end

lemma exercise.quatre_divise : ∀n: nat, divides (4) (3^n -(-1)^n) :=
/- dEAduction
PrettyName
  Divisibilité par 4
Description
    Divisibilité par 4 d'une expression dépendant de n,  à démontrer par récurrence
AvailableDefinitions
	divise
AvailableTheorems
   puissance1 

-/
begin
  todo
end

lemma theorem.puissance3  : ∀ m: nat , ∀ n: nat, m^(n+1) = (m^n)*m :=
/- dEAduction
PrettyName
  Propriété Puissance (Entiers naturels)
ImplicitUse
  True
-/
begin
  todo
end

lemma exercise.heredite_seule :  ( ∀n: nat, ( pair (3^n)  → pair (3^(n+1) ) ) ) and (∀n: nat, ( impair (3^n) )) :=
/- dEAduction
PrettyName
  Propriété héréditaire mais fausse
Description
   Propriété héréditaire mais qui est toujours fausse.
AvailableDefinitions
	pair, impair
AvailableTheorems
   puissance3
   
-/
begin
    todo
end


end recurrence

end course

