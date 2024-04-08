/-
This is a d∃∀duction file providing a tutorial.
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
    Tutoriel partie 1 : découverte des icônes
Author
    Isabelle Dubois / inspiré du fichier tutoriel de Frédéric
Institution
    Université de Lorraine
Description
    Tutoriel d'utilisation du logiciel dans un contexte de manipulations des entiers ou réels
    - Partie 1 - Découverte des icônes
AvailableExercises
    NONE
AvailableProof
    NONE
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




lemma exercise.but { a b x y : ℝ} (Hypothese1 : x <= a) (Hypothese2 : y < b):
 x + y < a+b
:=
/- dEAduction
PrettyName
    Bouton But - Enoncé directement vrai pour le logiciel -  Réels et inégalités
Description
    Le bouton "But !" et les tactiques de simplifications automatiques disponibles. 
  
AvailableLogic
    NONE
    
AvailableMagic
    assumption
-/
begin
    todo
end



lemma exercise.nonbut { a x y : ℝ} (Hypothese1 : a < 0 ) (Hypothese2 : x > y):
 not( a*x >= a*y )
:=
/- dEAduction
PrettyName
    Transformation d'une proposition NON (P) dans le but - Réels et inégalités.
Description
    Découverte du connecteur NON, pour transformer le But.
AvailableLogic
    not
    
AvailableMagic
    assumption
-/
begin
    todo
end



lemma exercise.nonhyp { a  x y : ℝ} (Hypothese1 : x > y) (Hypothese2 : not (a<=2)) :
 x*a > y*a
:=
/- dEAduction
PrettyName
    Transformation d'une proposition NON (P) dans l'hypothèse  - Réels et inégalités
Description
    Découverte du connecteur NON, pour transformer une hypothèse.
AvailableLogic
    not   
AvailableMagic
    assumption
-/
begin
    todo
end


lemma exercise.connecteur_etdansbut (H1 : (m>2) ) (H2 : n =4) :
(m+n > 6) \and (not(m+n < 1))
:=
/- dEAduction
PrettyName
    Connecteur ET dans le but - Entiers et inégalités
Description
    Le bouton "ET" permet de découper un but à atteindre contenant le connecteur ET en deux sous-buts.
AvailableLogic
    and not
AvailableMagic
    assumption
-/
begin
    todo
end



lemma exercise.connecteur_etdanshyp (H : (2*m = 6) \and (m+n^2 > 10*n)) :
m*m <=10
:=
/- dEAduction
PrettyName
    Connecteur ET dans une hypothèse - Entiers
Description
    Le bouton "ET" permet de découper une hypothèse contenant le connecteur ET en deux hypothèses.
AvailableLogic
    and 
AvailableMagic
    assumption
-/
begin
    todo
end


lemma exercise.connecteur_oudansbut (H1 : (m>2) ) (H2 : n =4) :
(m+n > 6) \or (m-n > 2)
:=
/- dEAduction
PrettyName
    Connecteur OU dans le but - Entiers et inégalités.
Description
    Le bouton "OU" permet de choisir quelle proposition peut/doit être démontrée dans le but.
AvailableLogic
      or
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.connecteur_oudanshyp (H : (m=2) \or (n=3)) :
m+n >= 1
:=
/- dEAduction
PrettyName
    Connecteur OU dans une hypothèse - Entiers
Description
    Le bouton "OU" permet de découper une hypothèse contenant le connecteur OU en deux hypothèses successives.
AvailableLogic
    or
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.connecteur_etoudansbuthyp {a x y : ℝ} (H : (x <= y) \and ( (a<0) \or (a>0))) :
( a*x <= a*y) \or (a*y <= a*x)
:=
/- dEAduction
PrettyName
    Connecteurs ET et OU dans une hypothèse, et un OU dans un  but - Réels et inégalités
Description
    Utilisation des boutons "ET" et "OU" combinés.
AvailableLogic
    or and
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.connecteur_impliquedansbut1 :
( m + n >=5) → (m+n >= 3)
:=
/- dEAduction
PrettyName
    Connecteur IMPLIQUE dans but (1) - Cas d'une proposition vraie en prémisse.
Description
    Le bouton "=>" permet de démontrer une implication : pour démontrer
    "P => Q", on suppose P, et on montre Q.
AvailableLogic
    implies
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.connecteur_impliquedansbut2 :
( 1 = 5 ) → (m+n >= 3)
:=
/- dEAduction
PrettyName
    Connecteur IMPLIQUE dans but (2) - Cas d'une proposition fausse en prémisse
Description
    Le bouton "=>" permet de démontrer une implication : pour démontrer
    "P => Q", on suppose P, et on montre Q. Attention : Si P est fausse, alors l'implication "P => Q" est vraie, quelle que soit la proposition Q.
AvailableLogic
    implies
AvailableMagic
    assumption
-/
begin
    todo
end




lemma exercise.connecteur_equal (H1:  (m+3*n =100) ) (H2 : m=10 ):
n = 30  -- utilisation de equal pour arriver au but
:=
/- dEAduction
PrettyName
   Bouton EGALITE - Substitution de valeurs de variables
Description
   
    Le bouton "=" permet de remplacer une expression par une autre qui lui est égale.
AvailableLogic
     equal
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.connecteur_equal_ssi  { x  : ℝ} (H1:  5*x >= 23 )  (H2 : ( x >=1 )  ↔ ((1/x <=1)\and (x>0)) ) :
(1/x <=1) \and (x>0)
:=
/- dEAduction
PrettyName
   Bouton EGALITE - Substitution d'une proposition par une autre équivalente
Description
   
    Le bouton "=" permet de remplacer une proposition par une autre qui lui est équivalente.
AvailableLogic
     equal
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.connecteur_impliquedanshyp (H1: ( m >=5) → (m+n =100) ) (H2 : m=10 ):
10 + n = 100  -- marche, mais par contre n=90 ne fonctionne pas
:=
/- dEAduction
PrettyName
    Connecteur IMPLIQUE dans une hypothèse - Première forme
Description
    Le bouton "=>" permet d'utiliser une implication dans une hypothèse : à partir de  "P => Q" et de "P" on en déduit "Q".
AvailableLogic
    implies
AvailableMagic
    assumption
-/
begin
    todo
end



lemma exercise.connecteur_impliquedanshyp2 (H1: ( m >=5) → (m+n =100) ) (H2 : m=10 ):
n = 90  -- utilisation de equal pour arriver au but
:=
/- dEAduction
PrettyName
    Connecteur IMPLIQUE dans hypothèse et bouton EGALITE - Deuxième forme
Description
   Le bouton "=>" permet d'utiliser une implication dans une hypothèse : à partir de  "P => Q" et de "P" on en déduit "Q".
    
    Le bouton "=" permet de remplacer une expression par une autre qui lui est égale.
AvailableLogic
    implies equal
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.ssi1 { x  : ℝ}:
( (x >= 1) \and ( x>=0 \or x <= -1)) ↔ (x >= 1)
:=
/- dEAduction
PrettyName
    Connecteur EQUIVALENT dans But
Description
    Le bouton "<=>" permet de découper le but en deux implications à démontrer.
AvailableLogic
    and or not implies iff
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.ssi2   (H1: m*n=0 ↔ ( m=0 \or n=0) ) 
 (H2: (m*n = 0) \or (m*n =1) \or (m*n >= 2) ) :
( not(m*n =1))→  ( (m=0) \or (n=0) \or (m*n >= 2) )
:=
/- dEAduction
PrettyName
    Connecteur EQUIVALENT dans une hypothèse
Description
    Le bouton "<=>" permet d'utiliser une des implications de l'hypothèse.
AvailableLogic
    and or not implies iff equal
AvailableMagic
    assumption
-/
begin
    todo
end

end course

