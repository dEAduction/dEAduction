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
    Tutoriel d'utilisation du logiciel dans un contexte de manipulations des entiers ou réels  - Partie 3 - Découverte des Définitions et Théorèmes
Author
    Isabelle Dubois / inspiré du fichier tutoriel de Frédéric
Institution
    Université de Lorraine
Description
    Ce fichier, qui peut servir de tutoriel, contient quelques énoncés de logique  propositionnelle basés sur des exemples concrets.
    Le but n'est pas de les démontrer du point de vue de la logique propositionnelle,
    mais plutôt de voir comment l'interface fonctionne sur ces énoncés.
DefaultAvailableLogic
    ALL -map
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


lemma theorem.croissance1 
{ x y : ℝ} :
((0 <= x) \and (0<=y) \and (x <=y)) → x^2 <= y^2
:=
/- dEAduction
PrettyName
  Croissance de la fonction carré - Réels positifs
-/
begin
  todo
end

lemma exercise.utilisation_th { x y : ℝ} (H : 0 <=x)  :
(x <= y) → ((0<=y) \and (x^2 <= y^2))
:=
/- dEAduction
PrettyName
    Utilisation d'un théorème dans le but - Fonction carrée. 
Description
    Utilisation d'un théorème dans le but - Fonction carrée. 

AvailableLogic
     and  implies
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.utilisation_th_2 
{ x y : ℝ} (H : 0 <=x) :
(x <= y) → ((0<=y) \and (x^2 <= y^2))
:=
/- dEAduction
PrettyName
  Utilisation d'un théorème dans le but - Fonction carrée.
Description
  Utilisation d'un théorème dans le but - Fonction carrée.
AvailableLogic
  and  implies
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    target prove_implies success=Propriété_H1_ajoutée_au_contexte,
    target prove_and 0 success=On_décompose_le_but,
    assumption success=But_en_cours_atteint,
    target theorem.croissance1 success=Le_but_a_été_remplacé_en_appliquant_le_théorème,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.11h34
-/
begin
--   intro H1,
--   split,
--   solve1 {compute_n 10 },
--   apply_with theorem.croissance1 {md:=reducible},
--   split, split, assumption, solve1 {compute_n 10 }, assumption,
  todo
end


lemma exercise.utilisation_th_4 
{ x y : ℝ} (H : 0 <=x) :
(x <= y) → ((0<=y) \and (x^2 <= y^2))
:=
/- dEAduction
PrettyName
  Utilisation d'un théorème dans le but - Fonction carrée.
Description
  Utilisation d'un théorème dans le but - Fonction carrée.
AvailableLogic
  and  implies
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    target prove_implies success=Propriété_H1_ajoutée_au_contexte,
    theorem.croissance1 [ x y ] success=Propriété_H2_ajoutée_au_contexte,
    @P3 use_implies 0 success=Le_nouveau_but_sera_ajouté_au_contexte_quand_il_aura_été_démontré,
    assumption success=But_en_cours_atteint,
    @P4 @P3 use_implies success=Propriété_H4_ajoutée_au_contexte,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  20déc.22h28
-/
begin
--   intro H1,
--   have H2 := @theorem.croissance1 (x) (y),
--   have H3: (((((0): @real) ≤ x) and (((0): @real) ≤ y)) and (x ≤ y)),
--   split, split, assumption, solve1 {norm_num at *, compute_n 10 }, assumption,
--   have H4 := H2 H3,
--   cases H3 with H_aux_0 H_aux_1, split, solve1 {norm_num at *, compute_n 10 }, assumption,
  todo
end











lemma theorem.decroissance 
{ x y : ℝ} :
((x <= 0) \and (y<=0) \and (x <=y)) → y^2 <= x^2
:=
/- dEAduction
PrettyName
  Décroissance de la fonction carré - Réels négatifs
-/
begin
  todo
end

lemma exercise.utilisation_thd2 { x y : ℝ} (H : x <=0)  :
(x <= -2) → ((-2)^2 <= x^2)
:=
/- dEAduction
PrettyName
    Utilisation d'un théorème à choisir parmi deux dans le But - Fonction carrée.
Description
    Utilisation d'un théorème à choisir parmi deux dans le But - Fonction carrée.
AvailableLogic
      and implies
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.utilisation_thd2_2 
{ x y : ℝ} (H : x <=0) :
(x <= -2) → ((-2)^2 <= x^2)
:=
/- dEAduction
PrettyName
  Utilisation d'un théorème à choisir parmi deux dans le But - Fonction carrée.
Description
  Utilisation d'un théorème à choisir parmi deux dans le But - Fonction carrée.
AvailableLogic
  and implies
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    target prove_implies success=Propriété_H1_ajoutée_au_contexte,
    theorem.decroissance [ x -2 ] success=Propriété_H2_ajoutée_au_contexte,
    @P3 use_implies 0 success=Le_nouveau_but_sera_ajouté_au_contexte_quand_il_aura_été_démontré,
    assumption success=But_en_cours_atteint,
    @P4 @P3 use_implies success=Propriété_H4_ajoutée_au_contexte,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.11h58
-/
begin
--   intro H1,
--   have H2 := @theorem.decroissance (x) (-2),
--   have H3: (((x ≤ ((0): @real)) and ((-((2): @real)) ≤ ((0): @real))) and (x ≤ (-((2): @real)))),
--   split, split, assumption, solve1 {norm_num at * }, assumption,
--   have H4 := H2 H3,
--   assumption,
  todo
end


lemma exercise.utilisation_thd2_1 
{ x y : ℝ} (H : x <=0) :
(x <= -2) → ((-2)^2 <= x^2)
:=
/- dEAduction
PrettyName
  Utilisation d'un théorème à choisir parmi deux dans le But - Fonction carrée.
Description
  Utilisation d'un théorème à choisir parmi deux dans le But - Fonction carrée.
AvailableLogic
  and implies
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    target prove_implies success=Propriété_H1_ajoutée_au_contexte,
    theorem.decroissance [ x -2 ] success=Propriété_H2_ajoutée_au_contexte,
    @P3 use_implies 0 success=Le_nouveau_but_sera_ajouté_au_contexte_quand_il_aura_été_démontré,
    assumption success=But_en_cours_atteint,
    @P4 @P3 use_implies success=Propriété_H4_ajoutée_au_contexte,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  20déc.15h11
-/
begin
--   intro H1,
--   have H2 := @theorem.decroissance (x) (-2),
--   have H3: (((x ≤ ((0): @real)) and ((-((2): @real)) ≤ ((0): @real))) and (x ≤ (-((2): @real)))),
--   split, split, assumption, solve1 {norm_num at * }, assumption,
--   have H4 := H2 H3,
--   assumption,
  todo
end




lemma theorem.eqproduit 
{ x y : ℝ} :
(x*y=0) → ( (x=0) \or (y=0) )
:=
/- dEAduction
PrettyName
  Equation produit
-/
begin
  todo
end





lemma exercise.eq2 { x y : ℝ}  :
((x-1) * x)*y = 0 → ( (x=1) \or (x=0) \or (y=0) )
:=
/- dEAduction
PrettyName
    Utilisation d'un théorème dans une hypothèse  - Equation
Description
    Utilisation d'un théorème dans une hypothèse - Equation.
AvailableLogic
     or  implies
AvailableTheorems
  eqproduit
AvailableMagic
    assumption
-/
begin
    todo
end






lemma exercise.eq2_2 
{ x y : ℝ} :
((x-1) * x)*y = 0 → ( (x=1) \or (x=0) \or (y=0) )
:=
/- dEAduction
PrettyName
  Utilisation d'un théorème dans une hypothèse  - Equation
Description
  Utilisation d'un théorème dans une hypothèse - Equation.
AvailableLogic
  or  implies
AvailableTheorems
  eqproduit
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    target prove_implies success=Propriété_H1_ajoutée_au_contexte,
    theorem.eqproduit [ ((x__-__1)__*__x) y ] success=Propriété_H2_ajoutée_au_contexte,
    @P1 @P2 use_implies success=Propriété_H3_ajoutée_au_contexte,
    theorem.eqproduit [ x__-__1 x ] success=Propriété_H4_ajoutée_au_contexte,
    @P3 use_or 0 success=Preuve_par_cas,
    @P4 @P3 use_implies success=Propriété_H7_ajoutée_au_contexte,
    target prove_or 0 success=But_remplacé_par_l’alternative_de_gauche,
    @P5 use_or 0 success=Preuve_par_cas,
    target prove_or 0 success=But_remplacé_par_l’alternative_de_gauche,
    assumption success=But_en_cours_atteint,
    target prove_or 1 success=But_remplacé_par_l’alternative_de_droite,
    assumption success=But_en_cours_atteint,
    target prove_or 1 success=But_remplacé_par_l’alternative_de_droite,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  20déc.15h19
-/
begin
--   intro H1,
--   have H2 := @theorem.eqproduit ((x - 1) * x) (y),
--   have H3 := (H2 ).mp H1,
--   have H4 := @theorem.eqproduit (x - 1) (x),
--   cases H3 with H5 H6,
--   have H7 := (H4 ).mp H5,
--   left,
--   cases H7 with H8 H9,
--   left,
--   solve1 {norm_num at *, compute_n 10 },
--   right,
--   assumption,
--   right,
--   assumption,
  todo
end





end course
