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

lemma exercise.but_1 
{ a b x y : ℝ} (Hypothese1 : x <= a) (Hypothese2 : y < b) :
 x + y < a+b
:=
/- dEAduction
all_goals_solved = "True"
auto_test = [
    { button = "assumption", success_msg = "La preuve est terminée !" },
]
history_date = "17nov.11h10"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = true
functionality.allow_implicit_use_of_definitions = true
functionality.auto_solve_inequalities_in_bounded_quantification = true
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   solve1 {trace "EFFECTIVE CODE n°5.1", compute_n 10 }, trace "EFFECTIVE CODE n°1.3", trace "EFFECTIVE CODE n°0.2",
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

lemma exercise.nonbut_2 
{ a x y : ℝ} (Hypothese1 : a < 0 ) (Hypothese2 : x > y) :
 not( a*x >= a*y )
:=
/- dEAduction
all_goals_solved = "True"
auto_test = [
    { target_selected = true, button = "not", success_msg = "Négation « poussée » sur le but" },
    { button = "assumption", success_msg = "La preuve est terminée !" },
]
history_date = "17nov.11h10"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   push_neg_once, trace "EFFECTIVE CODE n°30.1",
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°36.0", compute_n 10 }, trace "EFFECTIVE CODE n°32.3", trace "EFFECTIVE CODE n°31.2",
  todo
end


lemma exercise.nonbut_1 
{ a x y : ℝ} (Hypothese1 : a < 0 ) (Hypothese2 : x > y) :
 not( a*x >= a*y )
:=
/- dEAduction
all_goals_solved = "True"
auto_test = [
    { target_selected = true, button = "not", success_msg = "Négation « poussée » sur le but" },
    { button = "assumption", success_msg = "La preuve est terminée !" },
]
history_date = "17nov.11h10"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   push_neg_once, trace "EFFECTIVE CODE n°12.1",
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°18.0", compute_n 10 }, trace "EFFECTIVE CODE n°14.3", trace "EFFECTIVE CODE n°13.2",
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

lemma exercise.nonhyp_2 
{ a  x y : ℝ} (Hypothese1 : x > y) (Hypothese2 : not (a<=2)) :
 x*a > y*a
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h11"
[[auto_test]]
selection = [ "@P2" ]
button = "not"
success_msg = "Négation « poussée » sur la propriété Hypothese2"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   push_neg_once at Hypothese2, trace "EFFECTIVE CODE n°55.1",
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°61.0", compute_n 10 }, trace "EFFECTIVE CODE n°57.3", trace "EFFECTIVE CODE n°56.2",
  todo
end


lemma exercise.nonhyp_1 
{ a  x y : ℝ} (Hypothese1 : x > y) (Hypothese2 : not (a<=2)) :
 x*a > y*a
:=
/- dEAduction
all_goals_solved = "True"
auto_test = [
    { button = "assumption", success_msg = "La preuve est terminée !" },
]
history_date = "17nov.11h10"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°48.0", compute_n 10 }, trace "EFFECTIVE CODE n°44.3", trace "EFFECTIVE CODE n°43.2",
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

lemma exercise.connecteur_etdansbut_1 
(H1 : (m>2) ) (H2 : n =4) :
(m+n > 6) \and (not(m+n < 1))
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h11"
[[auto_test]]
target_selected = true
button = "prove_and"
user_input = [
    0,
]
success_msg = "On décompose le but"
[[auto_test]]
button = "assumption"
success_msg = "But en cours atteint"
[[auto_test]]
target_selected = true
button = "not"
success_msg = "Négation « poussée » sur le but"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   split,
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°74.0", compute_n 10 }, trace "EFFECTIVE CODE n°70.3", trace "EFFECTIVE CODE n°68.3",
--   push_neg_once, trace "EFFECTIVE CODE n°82.1",
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°87.0", compute_n 10 }, trace "EFFECTIVE CODE n°85.2", trace "EFFECTIVE CODE n°83.3",
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

lemma exercise.connecteur_etdanshyp_1 
(H : (2*m = 6) \and (m+n^2 > 10*n)) :
m*m <=10
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h12"
[[auto_test]]
selection = [ "@P1" ]
button = "use_and"
success_msg = "Propriété H découpée en H_0 et H_1"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   cases H with H_0 H_1,
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°97.0", compute_n 10 }, trace "EFFECTIVE CODE n°95.2", trace "EFFECTIVE CODE n°93.3",
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

lemma exercise.connecteur_oudansbut_1 
(H1 : (m>2) ) (H2 : n =4) :
(m+n > 6) \or (m-n > 2)
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h12"
[[auto_test]]
target_selected = true
button = "prove_or"
user_input = [
    0,
]
success_msg = "But remplacé par l’alternative de gauche"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   left,
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°109.0", compute_n 10 }, trace "EFFECTIVE CODE n°105.3", trace "EFFECTIVE CODE n°103.3",
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

lemma exercise.connecteur_oudanshyp_1 
(H : (m=2) \or (n=3)) :
m+n >= 1
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h12"
[[auto_test]]
selection = [ "@P1" ]
button = "use_or"
user_input = [
    0,
]
success_msg = "Preuve par cas"
[[auto_test]]
button = "assumption"
success_msg = "But en cours atteint"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   cases H with H_0 H_1,
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°121.0", compute_n 10 }, trace "EFFECTIVE CODE n°119.2", trace "EFFECTIVE CODE n°117.3",
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°131.0", compute_n 10 }, trace "EFFECTIVE CODE n°129.2", trace "EFFECTIVE CODE n°127.3",
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

lemma exercise.connecteur_etoudansbuthyp_1 
{a x y : ℝ} (H : (x <= y) \and ( (a<0) \or (a>0))) :
( a*x <= a*y) \or (a*y <= a*x)
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h13"
[[auto_test]]
selection = [ "@P1" ]
button = "use_and"
success_msg = "Propriété H découpée en H_0 et H_1"
[[auto_test]]
selection = [ "@P2" ]
button = "use_or"
user_input = [
    0,
]
success_msg = "Preuve par cas"
[[auto_test]]
target_selected = true
button = "prove_or"
user_input = [
    1,
]
success_msg = "But remplacé par l’alternative de droite"
[[auto_test]]
button = "assumption"
success_msg = "But en cours atteint"
[[auto_test]]
target_selected = true
button = "prove_or"
user_input = [
    0,
]
success_msg = "But remplacé par l’alternative de gauche"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   cases H with H_0 H_1,
--   cases H_1 with H_2 H_3,
--   right,
--   solve1 {trace "EFFECTIVE CODE n°142.1", compute_n 10 }, trace "EFFECTIVE CODE n°138.3", trace "EFFECTIVE CODE n°137.2",
--   left,
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°154.0", compute_n 10 }, trace "EFFECTIVE CODE n°150.3", trace "EFFECTIVE CODE n°149.2",
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

lemma exercise.connecteur_impliquedansbut1_1 
 :
( m + n >=5) → (m+n >= 3)
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h13"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_0 ajoutée au contexte"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   intro H_0,
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°165.0", compute_n 10 }, trace "EFFECTIVE CODE n°162.3", trace "EFFECTIVE CODE n°161.2",
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

lemma exercise.connecteur_impliquedansbut2_1 
 :
( 1 = 5 ) → (m+n >= 3)
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h14"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_0 ajoutée au contexte"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   intro H_0,
--   cc, trace "EFFECTIVE CODE n°174.1", trace "EFFECTIVE CODE n°173.2",
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

lemma exercise.connecteur_equal_1 
(H1:  (m+3*n =100) ) (H2 : m=10 ) :
n = 30  -- utilisation de equal pour arriver au but
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h15"
[[auto_test]]
selection = [ "@P2", "@P1" ]
button = "equal"
user_input = [
    0,
]
success_msg = "m remplacé par 10 dans H1"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   rw H2 at H1, trace "EFFECTIVE CODE n°211.0", trace "EFFECTIVE CODE n°210.0",
--   solve1 {trace "EFFECTIVE CODE n°221.1", compute_n 10 }, trace "EFFECTIVE CODE n°215.4", trace "EFFECTIVE CODE n°213.3",
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

lemma exercise.connecteur_equal_ssi_2 
{ x  : ℝ} (H1:  5*x >= 23 )  (H2 : ( x >=1 )  ↔ ((1/x <=1)\and (x>0)) ) :
(1/x <=1) \and (x>0)
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h15"
[[auto_test]]
selection = [ "@P2" ]
button = "equal"
success_msg = "1/x ≤ 1 et x > 0 remplacé par x ≥ 1 dans le but"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   rw <- H2, trace "EFFECTIVE CODE n°279.0", trace "EFFECTIVE CODE n°277.1",
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°285.0", compute_n 10 }, trace "EFFECTIVE CODE n°281.3", trace "EFFECTIVE CODE n°280.2",
  todo
end


lemma exercise.connecteur_equal_ssi_1 
{ x  : ℝ} (H1:  5*x >= 23 )  (H2 : ( x >=1 )  ↔ ((1/x <=1)\and (x>0)) ) :
(1/x <=1) \and (x>0)
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h15"
[[auto_test]]
selection = [ "@P2" ]
button = "equal"
success_msg = "1/x ≤ 1 et x > 0 remplacé par x ≥ 1 dans le but"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   rw <- H2, trace "EFFECTIVE CODE n°242.0", trace "EFFECTIVE CODE n°240.1",
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°248.0", compute_n 10 }, trace "EFFECTIVE CODE n°244.3", trace "EFFECTIVE CODE n°243.2",
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

lemma exercise.connecteur_impliquedanshyp_1 
(H1: ( m >=5) → (m+n =100) ) (H2 : m=10 ) :
10 + n = 100  -- marche, mais par contre n=90 ne fonctionne pas
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h17"
[[auto_test]]
selection = [ "@P1" ]
button = "use_implies"
user_input = [
    0,
]
success_msg = "Le nouveau but sera ajouté au contexte quand il aura été démontré"
[[auto_test]]
button = "assumption"
success_msg = "But en cours atteint"
[[auto_test]]
selection = [ "@P3", "@P1" ]
button = "use_implies"
success_msg = "Propriété H_4 ajoutée au contexte"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   have H_3: (m ≥ (5: @nat)),
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°296.0", compute_n 10 }, trace "EFFECTIVE CODE n°294.2", trace "EFFECTIVE CODE n°292.3",
--   have H_4 := H1 H_3, trace "EFFECTIVE CODE n°303.0",
--   cc, trace "EFFECTIVE CODE n°305.1", trace "EFFECTIVE CODE n°304.2",
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

lemma exercise.connecteur_impliquedanshyp2_1 
(H1: ( m >=5) → (m+n =100) ) (H2 : m=10 ) :
n = 90  -- utilisation de equal pour arriver au but
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h18"
[[auto_test]]
selection = [ "@P1" ]
button = "use_implies"
user_input = [
    0,
]
success_msg = "Le nouveau but sera ajouté au contexte quand il aura été démontré"
[[auto_test]]
selection = [ "@P2" ]
button = "equal"
success_msg = "m remplacé par 10 dans le but"
[[auto_test]]
button = "assumption"
success_msg = "But en cours atteint"
[[auto_test]]
selection = [ "@P3", "@P1" ]
button = "use_implies"
success_msg = "Propriété H_4 ajoutée au contexte"
[[auto_test]]
selection = [ "@P2", "@P4" ]
button = "equal"
user_input = [
    0,
]
success_msg = "m remplacé par 10 dans H_4"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   have H_3: (m ≥ (5: @nat)),
--   rw H2, trace "EFFECTIVE CODE n°329.0", trace "EFFECTIVE CODE n°328.0",
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°334.0" }, trace "EFFECTIVE CODE n°333.1", trace "EFFECTIVE CODE n°331.3",
--   have H_4 := H1 H_3, trace "EFFECTIVE CODE n°341.0",
--   rw H2 at H_4, trace "EFFECTIVE CODE n°370.0", trace "EFFECTIVE CODE n°369.0",
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°380.0", compute_n 10 }, trace "EFFECTIVE CODE n°374.4", trace "EFFECTIVE CODE n°372.3",
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

lemma exercise.ssi1_1 
{ x  : ℝ} :
( (x >= 1) \and ( x>=0 \or x <= -1)) ↔ (x >= 1)
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h19"
[[auto_test]]
target_selected = true
button = "iff"
user_input = [
    1,
]
success_msg = "Equivalence séparée en deux implications"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_0 ajoutée au contexte"
[[auto_test]]
target_selected = true
button = "prove_and"
user_input = [
    0,
]
success_msg = "On décompose le but"
[[auto_test]]
button = "assumption"
success_msg = "But en cours atteint"
[[auto_test]]
target_selected = true
button = "prove_or"
user_input = [
    0,
]
success_msg = "But remplacé par l’alternative de gauche"
[[auto_test]]
button = "assumption"
success_msg = "But en cours atteint"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_0 ajoutée au contexte"
[[auto_test]]
selection = [ "@P1" ]
button = "use_and"
success_msg = "Propriété H_0 découpée en H_1 et H_2"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   rw iff.comm, split,
--   intro H_0,
--   split,
--   assumption, trace "EFFECTIVE CODE n°419.0",
--   left,
--   solve1 {norm_num at *, trace "EFFECTIVE CODE n°431.0", compute_n 10 }, trace "EFFECTIVE CODE n°428.3", trace "EFFECTIVE CODE n°427.2",
--   intro H_0,
--   cases H_0 with H_1 H_2,
--   assumption, trace "EFFECTIVE CODE n°437.0",
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

lemma exercise.ssi2_1 
(H1: m*n=0 ↔ ( m=0 \or n=0) ) 
 (H2: (m*n = 0) \or (m*n =1) \or (m*n >= 2) ) :
( not(m*n =1))→  ( (m=0) \or (n=0) \or (m*n >= 2) )
:=
/- dEAduction
all_goals_solved = "True"
history_date = "17nov.11h20"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_3 ajoutée au contexte"
[[auto_test]]
selection = [ "@P2" ]
button = "use_or"
user_input = [
    0,
]
success_msg = "Preuve par cas"
[[auto_test]]
selection = [ "@P3" ]
button = "use_or"
user_input = [
    0,
]
success_msg = "Preuve par cas"
[[auto_test]]
selection = [ "@P3", "@P1" ]
button = "use_implies"
success_msg = "Propriété H_6 ajoutée au contexte"
[[auto_test]]
button = "assumption"
success_msg = "But en cours atteint"
[[auto_test]]
button = "assumption"
success_msg = "But en cours atteint"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
[settings]
functionality.default_functionality_level = "Free settings"
functionality.automatic_use_of_exists = true
functionality.automatic_use_of_and = true
functionality.target_selected_by_default = false
functionality.allow_implicit_use_of_definitions = false
functionality.auto_solve_inequalities_in_bounded_quantification = false
functionality.automatic_intro_of_variables_and_hypotheses = false
functionality.choose_order_to_prove_conjunction = false
functionality.choose_order_to_use_disjunction = false
-/
begin
--   intro H_3,
--   cases H2 with H_4 H_5,
--   cases H_4 with H_5 H_6,
--   have H_6 := (H1 ).mp H_5, trace "EFFECTIVE CODE n°446.0", trace "EFFECTIVE CODE n°445.0",
--   cc, trace "EFFECTIVE CODE n°449.1", trace "EFFECTIVE CODE n°448.2",
--   contradiction, trace "EFFECTIVE CODE n°499.1",
--   right, assumption, trace "EFFECTIVE CODE n°586.0", trace "EFFECTIVE CODE n°556.1", trace "EFFECTIVE CODE n°550.4",
  todo
end


end course