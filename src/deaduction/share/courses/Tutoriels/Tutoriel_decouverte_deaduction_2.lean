/-
This is a d∃∀duction file providing a tutorial about using quantifiers.
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
    Tutoriel partie 2 : découverte des icônes Quantificateurs
Author
    Isabelle Dubois / inspiré du fichier tutoriel de Frédéric
Institution
    Université de Lorraine
Description
    Tutoriel d'utilisation du logiciel dans un contexte de manipulations des entiers ou réels
    - Partie 2 - Découverte des icônes Quantificateurs
AvailableExercises
    NONE
DefaultAvailableProof
    NONE
DefaultAvailableMagic
    Assumption
AvailableCompute
    NONE
-/

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
open nat

variables (P Q R: Prop) -- NOT global
notation [parsing_only] P ` \and ` Q := P ∧ Q
notation [parsing_only]  P ` \or ` Q := P ∨ Q
notation [parsing_only]  ` \not ` P := ¬ P
notation [parsing_only]  P ` \implies ` Q := P → Q
notation [parsing_only]  P ` \iff ` Q := P ↔ Q

variables {m n k: ℕ}



lemma exercise.pourtout_hyp1 { x  : ℝ} (H: ∀ y : ℝ, y^2 = y*y ) : 
 ( (x+1)^2= 1 + 2*x +x*x)  
:=
/- dEAduction
PrettyName
    Utilisation du Pour tout dans une hypothèse (1)
Description
     Utilisation  du Pour tout dans une hypothèse (1).
AvailableLogic
    equal forall
AvailableTheorems
  NONE
AvailableDefinitions
  NONE
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.pourtout_hyp2 { x  : ℝ} (H: ∀ y : ℝ, y^2 = y*y ) : 
 ( (x+1)^2= 1 + 2*x +x^2)  
:=
/- dEAduction
PrettyName
    Utilisation du Pour tout dans une hypothèse (2)
Description
     Utilisation  du Pour tout dans une hypothèse (2). Variante.
AvailableLogic
    equal forall
AvailableTheorems
  NONE
AvailableDefinitions
  NONE
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.pourtout_but  : 
 ( ∀ x : ℝ, ∀ y : ℝ, ∀ z : ℝ, x*(y+z) = x*y +x*z )  
:=
/- dEAduction
PrettyName
    Démontrer un Pour tout dans le but
Description
      Démontrer un Pour tout dans le but.
AvailableLogic
     forall
AvailableTheorems
  NONE
AvailableDefinitions
  NONE
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.pourtout_hypbut (H1: ∀ x : ℝ, x^2 = x*x ) (H2: ∀ y : ℝ, y^3 = y*y*y ) : 
 ( ∀ z : ℝ, (z+1)^3= 1 + 3*z + 3*z^2 + z^3 )  
:=
/- dEAduction
PrettyName
     Pour Tout dans but et hypothèse
Description
    Démontrer/Utiliser un Pour Tout dans le but et une hypothèse.
AvailableLogic
    equal forall
AvailableTheorems
  NONE
AvailableDefinitions
  NONE
AvailableMagic
    assumption
-/
begin
    todo
end


lemma exercise.ilexiste_but1 : 
 (  ∃ a  :  ℕ, a*a*a = 27  )
:=
/- dEAduction
PrettyName
    Démontrer un Il existe dans le but (1)
Description
     Démontrer un Il existe dans  le but (1).
AvailableLogic
    exists 
AvailableTheorems
  NONE
AvailableDefinitions
  NONE
AvailableMagic
    assumption
-/
begin
   todo
end

lemma exercise.ilexiste_but2 : 
 (  ∃ a  :  ℕ, ∃ b  :  ℕ, (a*b=143) \and (a > b) )
:=
/- dEAduction
PrettyName
   Démontrer un Il existe dans le but (2)
Description
    Démontrer un Il existe dans le but (2).
AvailableLogic
   exists and
AvailableTheorems
  NONE
AvailableDefinitions
  NONE
AvailableMagic
    assumption
-/
begin
    todo
end


lemma exercise.ilexiste_hypbut { n  :  ℕ}  : 
 (  ∃ a  :  ℕ, n = 2*a ) → (  ∃ b  :  ℕ, n*n = 2*b )
:=
/- dEAduction
PrettyName
    Utilisation du bouton Il existe dans une hypothèse et but 
Description
     Démontrer/Utiliser un Il existe dans une hypothèse et le but. 
AvailableLogic
    equal exists implies
AvailableTheorems
  NONE
AvailableDefinitions
  NONE
AvailableMagic
    assumption
-/
begin
    todo
end




end course

