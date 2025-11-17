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
title = "Tutoriel partie 1 : découverte des icônes"
author = "Isabelle Dubois / inspiré du fichier tutoriel de Frédéric"
institution = "Université de Lorraine"
description = """
Tutoriel d'utilisation du logiciel dans un contexte de manipulations des entiers ou réels
- Partie 1 - Découverte des icônes
"""
available_exercises = "NONE"
available_proof = "NONE"
available_compute = "NONE"
logic.usr_jokers_available = false
logic.use_color_for_applied_properties = false
functionality.allow_induction = false
functionality.calculator_available = false
others.Lean_request_method = "normal"
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
pretty_name = "Bouton But - Enoncé directement vrai pour le logiciel -  Réels et inégalités"
description = 'Le bouton "But !" et les tactiques de simplifications automatiques disponibles.'
available_logic = "NONE"
available_magic = "assumption"
-/
begin
    todo
end



lemma exercise.nonbut { a x y : ℝ} (Hypothese1 : a < 0 ) (Hypothese2 : x > y):
 not( a*x >= a*y )
:=
/- dEAduction
pretty_name = "Transformation d'une proposition NON (P) dans le but - Réels et inégalités."
description = "Découverte du connecteur NON, pour transformer le But."
available_logic = "not"
available_magic = "assumption"
-/
begin
    todo
end



lemma exercise.nonhyp { a  x y : ℝ} (Hypothese1 : x > y) (Hypothese2 : not (a<=2)) :
 x*a > y*a
:=
/- dEAduction
pretty_name = "Transformation d'une proposition NON (P) dans l'hypothèse  - Réels et inégalités"
description = "Découverte du connecteur NON, pour transformer une hypothèse."
available_logic = "not"
available_magic = "assumption"
-/
begin
    todo
end


lemma exercise.connecteur_etdansbut (H1 : (m>2) ) (H2 : n =4) :
(m+n > 6) \and (not(m+n < 1))
:=
/- dEAduction
pretty_name = "Connecteur ET dans le but - Entiers et inégalités"
description = 'Le bouton "ET" permet de découper un but à atteindre contenant le connecteur ET en deux sous-buts.'
available_logic = "and not"
available_magic = "assumption"
-/
begin
    todo
end



lemma exercise.connecteur_etdanshyp (H : (2*m = 6) \and (m+n^2 > 10*n)) :
m*m <=10
:=
/- dEAduction
pretty_name = "Connecteur ET dans une hypothèse - Entiers"
description = 'Le bouton "ET" permet de découper une hypothèse contenant le connecteur ET en deux hypothèses.'
available_logic = "and"
available_magic = "assumption"
-/
begin
    todo
end


lemma exercise.connecteur_oudansbut (H1 : (m>2) ) (H2 : n =4) :
(m+n > 6) \or (m-n > 2)
:=
/- dEAduction
pretty_name = "Connecteur OU dans le but - Entiers et inégalités."
description = 'Le bouton "OU" permet de choisir quelle proposition peut/doit être démontrée dans le but.'
available_logic = "or"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.connecteur_oudanshyp (H : (m=2) \or (n=3)) :
m+n >= 1
:=
/- dEAduction
pretty_name = "Connecteur OU dans une hypothèse - Entiers"
description = 'Le bouton "OU" permet de découper une hypothèse contenant le connecteur OU en deux hypothèses successives.'
available_logic = "or"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.connecteur_etoudansbuthyp {a x y : ℝ} (H : (x <= y) \and ( (a<0) \or (a>0))) :
( a*x <= a*y) \or (a*y <= a*x)
:=
/- dEAduction
pretty_name = "Connecteurs ET et OU dans une hypothèse, et un OU dans un  but - Réels et inégalités"
description = 'Utilisation des boutons "ET" et "OU" combinés.'
available_logic = "or and"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.connecteur_impliquedansbut1 :
( m + n >=5) → (m+n >= 3)
:=
/- dEAduction
pretty_name = "Connecteur IMPLIQUE dans but (1) - Cas d'une proposition vraie en prémisse."
description = """
Le bouton "=>" permet de démontrer une implication : pour démontrer
"P => Q", on suppose P, et on montre Q.
"""
available_logic = "implies"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.connecteur_impliquedansbut2 :
( 1 = 5 ) → (m+n >= 3)
:=
/- dEAduction
pretty_name = "Connecteur IMPLIQUE dans but (2) - Cas d'une proposition fausse en prémisse"
description = """
Le bouton "=>" permet de démontrer une implication : pour démontrer
"P => Q", on suppose P, et on montre Q. Attention : Si P est fausse, alors l'implication "P => Q" est vraie, quelle que soit la proposition Q.
"""
available_logic = "implies"
available_magic = "assumption"
-/
begin
    todo
end




lemma exercise.connecteur_equal (H1:  (m+3*n =100) ) (H2 : m=10 ):
n = 30  -- utilisation de equal pour arriver au but
:=
/- dEAduction
pretty_name = "Bouton EGALITE - Substitution de valeurs de variables"
description = 'Le bouton "=" permet de remplacer une expression par une autre qui lui est égale.'
available_logic = "equal"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.connecteur_equal_ssi  { x  : ℝ} (H1:  5*x >= 23 )  (H2 : ( x >=1 )  ↔ ((1/x <=1)\and (x>0)) ) :
(1/x <=1) \and (x>0)
:=
/- dEAduction
pretty_name = "Bouton EGALITE - Substitution d'une proposition par une autre équivalente"
description = 'Le bouton "=" permet de remplacer une proposition par une autre qui lui est équivalente.'
available_logic = "equal"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.connecteur_impliquedanshyp (H1: ( m >=5) → (m+n =100) ) (H2 : m=10 ):
10 + n = 100  -- marche, mais par contre n=90 ne fonctionne pas
:=
/- dEAduction
pretty_name = "Connecteur IMPLIQUE dans une hypothèse - Première forme"
description = """Le bouton "=>" permet d'utiliser une implication dans une hypothèse :
à partir de  "P => Q" et de "P" on en déduit "Q"."""
available_logic = "implies"
available_magic = "assumption"
-/
begin
    todo
end



lemma exercise.connecteur_impliquedanshyp2 (H1: ( m >=5) → (m+n =100) ) (H2 : m=10 ):
n = 90  -- utilisation de equal pour arriver au but
:=
/- dEAduction
pretty_name = "Connecteur IMPLIQUE dans hypothèse et bouton EGALITE - Deuxième forme"
description = """
Le bouton "=>" permet d'utiliser une implication dans une hypothèse : à partir de  "P => Q" et de "P" on en déduit "Q".
Le bouton "=" permet de remplacer une expression par une autre qui lui est égale.
"""
available_logic = "implies equal"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.ssi1 { x  : ℝ}:
( (x >= 1) \and ( x>=0 \or x <= -1)) ↔ (x >= 1)
:=
/- dEAduction
pretty_name = "Connecteur EQUIVALENT dans But"
description = 'Le bouton "<=>" permet de découper le but en deux implications à démontrer.'
available_logic = "and or not implies iff"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.ssi2   (H1: m*n=0 ↔ ( m=0 \or n=0) ) 
 (H2: (m*n = 0) \or (m*n =1) \or (m*n >= 2) ) :
( not(m*n =1))→  ( (m=0) \or (n=0) \or (m*n >= 2) )
:=
/- dEAduction
pretty_name = "Connecteur EQUIVALENT dans une hypothèse"
description = """Le bouton "<=>" permet d'utiliser une des implications de l'hypothèse."""
available_logic = "and or not implies iff equal"
available_magic = "assumption"
-/
begin
    todo
end

end course
