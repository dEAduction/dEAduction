import data.set
import tactic

-- dEAduction imports
import structures2
import utils          
import push_neg_once
import compute          -- tactics for computation, used by the Goal! button

import data.real.basic
import real_definitions

-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement (since it will be called with 'rw' or 'symp_rw')


/- dEAduction
Title
    Tutoriel d'utilisation du logiciel dans un contexte de manipulations des entiers ou réels
    
    - Partie 2 - Découverte des icônes Quantificateurs
Author
    Isabelle Dubois / inspiré du fichier tutoriel de Frédéric
Institution
    Université de Lorraine
Description
    Ce fichier, qui peut servir de tutoriel, contient quelques énoncés de logique  propositionnelle basés sur des exemples concrets.
    Le but n'est pas de les démontrer du point de vue de la logique propositionnelle,
    mais plutôt de voir comment l'interface fonctionne sur ces énoncés.
AvailableExercises
    NONE
DefaultAvailableProof
    NONE
DefaultAvailableMagic
    Assumption
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
Settings
    logic.button_use_or_prove_mode --> "display_switch"
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

lemma exercise.pourtout_hyp1_4 
{ x  : ℝ} (H: ∀ y : ℝ, y^2 = y*y ) :
 
 ( (x+1)^2= 1 + 2*x +x*x)  
:=
/- dEAduction
PrettyName
  Utilisation du Pour tout dans une hypothèse (1)
Description
  Utilisation  du Pour tout dans une hypothèse (1).
Settings
  logic.button_use_or_prove_mode --> "display_switch"
AvailableLogic
  equal forall
AvailableTheorems
  NONE
AvailableDefinitions
  NONE
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    @P1 use_forall [ x__+__1 ] success=Propriété_H1_ajoutée_au_contexte,
    @P2 equal success=(x_+_1)^2_remplacé_par_(x_+_1)_×_(x_+_1)_dans_le_but,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.11h23
-/
begin
--   have H1 := @H (x + 1),
--   rw H1,
--   solve1 {ring },
  todo
end


lemma exercise.pourtout_hyp1_3 
{ x  : ℝ} (H: ∀ y : ℝ, y^2 = y*y ) :
 
 ( (x+1)^2= 1 + 2*x +x*x)  
:=
/- dEAduction
PrettyName
  Utilisation du Pour tout dans une hypothèse (1)
Description
  Utilisation  du Pour tout dans une hypothèse (1).
Settings
  logic.button_use_or_prove_mode --> "display_switch"
AvailableLogic
  equal forall
AvailableTheorems
  NONE
AvailableDefinitions
  NONE
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.11h13
-/
begin
--   solve1 {ring },
  todo
end


lemma exercise.pourtout_hyp1_2 
{ x  : ℝ} (H: ∀ y : ℝ, y^2 = y*y ) :
 
 ( (x+1)^2= 1 + 2*x +x*x)  
:=
/- dEAduction
PrettyName
  Utilisation du Pour tout dans une hypothèse (1)
Description
  Utilisation  du Pour tout dans une hypothèse (1).
Settings
  logic.button_use_or_prove_mode --> "display_switch"
AvailableLogic
  equal forall
AvailableTheorems
  NONE
AvailableDefinitions
  NONE
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  21déc.23h59
-/
begin
--   solve1 {ring },
  todo
end


lemma exercise.pourtout_hyp1_1 
{ x  : ℝ} (H: ∀ y : ℝ, y^2 = y*y ) :
 
 ( (x+1)^2= 1 + 2*x +x*x)  
:=
/- dEAduction
PrettyName
  Utilisation du Pour tout dans une hypothèse (1)
Description
  Utilisation  du Pour tout dans une hypothèse (1).
Settings
  logic.button_use_or_prove_mode --> "display_switch"
AvailableLogic
  equal forall
AvailableTheorems
  NONE
AvailableDefinitions
  NONE
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    @P1 use_forall [ x__+__1 ] success=Propriété_H1_ajoutée_au_contexte,
    @P2 equal success=(x_+_1)^2_remplacé_par_(x_+_1)_×_(x_+_1)_dans_le_but,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  21déc.23h58
-/
begin
--   have H1 := @H (x + 1),
--   rw H1,
--   solve1 {ring },
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

lemma exercise.pourtout_hyp2_1 
{ x  : ℝ} (H: ∀ y : ℝ, y^2 = y*y ) :
 
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
AllGoalsSolved
  True
AutoTest
    @P1 use_forall [ x__+__1 ] success=Propriété_H1_ajoutée_au_contexte,
    @P2 equal success=(x_+_1)^2_remplacé_par_(x_+_1)_×_(x_+_1)_dans_le_but,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.11h23
-/
begin
--   have H1 := @H (x + 1),
--   rw H1,
--   solve1 {ring },
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

lemma exercise.pourtout_but_1 
 :
 
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
AllGoalsSolved
  True
AutoTest
    target prove_forall success=Objet_x_ajouté_au_contexte,
    target prove_forall success=Objet_y_ajouté_au_contexte,
    target prove_forall success=Objet_z_ajouté_au_contexte,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.11h26
-/
begin
--   intro x,
--   intro y,
--   intro z,
--   solve1 {ring },
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

lemma exercise.pourtout_hypbut_2 
(H1: ∀ x : ℝ, x^2 = x*x ) (H2: ∀ y : ℝ, y^3 = y*y*y ) :
 
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
AllGoalsSolved
  True
AutoTest
    target prove_forall success=Objet_x_ajouté_au_contexte,
    @O1 @P1 use_forall success=Propriété_H3_ajoutée_au_contexte,
    @O1 @P2 use_forall success=Propriété_H4_ajoutée_au_contexte,
    @P3 equal success=x^2_remplacé_par_x_×_x_dans_le_but,
    @P4 equal success=x^3_remplacé_par_x_×_x_×_x_dans_le_but,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.11h26
-/
begin
--   intro x,
--   have H3 := H1 x,
--   have H4 := H2 x,
--   rw H3,
--   rw H4,
--   solve1 {ring },
  todo
end


lemma exercise.pourtout_hypbut_1 
(H1: ∀ x : ℝ, x^2 = x*x ) (H2: ∀ y : ℝ, y^3 = y*y*y ) :
 
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
AllGoalsSolved
  True
AutoTest
    target prove_forall success=Objet_x_ajouté_au_contexte,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  16déc.21h56
-/
begin
--   intro x,
--   solve1 {ring },
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

lemma exercise.ilexiste_but1_1 
 :
 
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
AllGoalsSolved
  True
AutoTest
    target prove_exists [ ((3):__@nat) ] success=Il_reste_à_démontrer_que_3_convient,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.11h27
-/
begin
--   use (((3): @nat)),
--   solve1 {ring },
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

lemma exercise.ilexiste_but2_2 
 :
 
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
AllGoalsSolved
  True
AutoTest
    target prove_exists [ ((13):__@nat) ] success=Il_reste_à_démontrer_que_13_convient,
    target prove_exists [ ((11):__@nat) ] success=Il_reste_à_démontrer_que_11_convient,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.11h29
-/
begin
--   use (((13): @nat)),
--   use (((11): @nat)),
--   split, solve1 {ring }, solve1 {norm_num at * },
  todo
end


lemma exercise.ilexiste_but2_1 
 :
 
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
AllGoalsSolved
  True
AutoTest
    target prove_exists [ ((13):__@nat) ] success=Il_reste_à_démontrer_que_13_convient,
    target prove_exists [ ((11):__@nat) ] success=Il_reste_à_démontrer_que_11_convient,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.11h27
-/
begin
--   use (((13): @nat)),
--   use (((11): @nat)),
--   split, solve1 {ring }, solve1 {norm_num at * },
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

lemma exercise.ilexiste_hypbut_2 
{ n  :  ℕ} :
 
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
AllGoalsSolved
  True
AutoTest
    target prove_implies success=Propriété_H1_ajoutée_au_contexte,
    @P1 use_exists success=Nouvel_objet_a_vérifiant_la_propriété_H2,
    @P1 equal success=n_remplacé_par_2_×_a_dans_le_but,
    target prove_exists [ ((2):__@nat)__*__(a__^__2) ] success=Il_reste_à_démontrer_que_2_×_a^2_convient,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.11h30
-/
begin
--   intro H1,
--   cases H1 with a H2,
--   rw H2,
--   use (((2): @nat) * (a ^ 2)),
--   solve1 {ring },
  todo
end


lemma exercise.ilexiste_hypbut_1 
{ n  :  ℕ} :
 
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
AllGoalsSolved
  True
AutoTest
    target prove_implies success=Propriété_H1_ajoutée_au_contexte,
    @P1 use_exists success=Nouvel_objet_a_vérifiant_la_propriété_H2,
    @P1 equal success=n_remplacé_par_2_×_a_dans_le_but,
    target prove_exists [ a__*__(2__*__a) ] success=Il_reste_à_démontrer_que_a_×_(2_×_a)_convient,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  16déc.22h01
-/
begin
--   intro H1,
--   cases H1 with a H2,
--   rw H2,
--   use (a * (2 * a)),
--   ac_reflexivity,
  todo
end





end course