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
    Tutoriel d'utilisation du logiciel dans un contexte de manipulations des entiers ou réels
    
    - Partie 1 - Découverte des icônes
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
    Le bouton "But !" et les tactiques de simplifications automatiques disponibles 
  
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

lemma exercise.nonbut_2 
{ a x y : ℝ} (Hypothese1 : a < 0 ) (Hypothese2 : x > y) :
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
AllGoalsSolved
  True
AutoTest
    target not success=Négation_« poussée »_sur_le_but,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  25déc.07h22
-/
begin
--   push_neg_once,
--   solve1 {norm_num at *, compute_n 10 },
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

lemma exercise.nonhyp_1 
{ a  x y : ℝ} (Hypothese1 : x > y) (Hypothese2 : not (a<=2)) :
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
AllGoalsSolved
  True
AutoTest
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  25déc.07h22
-/
begin
--   solve1 {norm_num at *, compute_n 10 },
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

lemma exercise.connecteur_etdansbut_1 
(H1 : (m>2) ) (H2 : n =4) :
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
AllGoalsSolved
  True
AutoTest
    target prove_and 0 success=On_décompose_le_but,
    assumption success=But_en_cours_atteint,
    target not success=Négation_« poussée »_sur_le_but,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  25déc.07h23
-/
begin
--   split,
--   solve1 {norm_num at *, compute_n 10 },
--   push_neg_once,
--   solve1 {norm_num at *, compute_n 10 },
  todo
end




lemma exercise.connecteur_etdanshyp (H : (2*m = 6) \and (m+n > 10*n^2)) :
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

lemma exercise.connecteur_etdanshyp_2 
(H : (2*m = 6) \and (m+n > 10*n^2)) :
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
AllGoalsSolved
  True
AutoTest
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  25déc.07h24
-/
begin
--   solve1 {norm_num at *, compute_n 10 },
  todo
end


lemma exercise.connecteur_etdanshyp_1 
(H : (2*m = 6) \and (m+n > 10*n^2)) :
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
AllGoalsSolved
  True
AutoTest
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  25déc.07h23
-/
begin
--   solve1 {norm_num at *, compute_n 10 },
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

lemma exercise.connecteur_oudansbut_2 
(H1 : (m>2) ) (H2 : n =4) :
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
AllGoalsSolved
  True
AutoTest
    target prove_or 0 success=But_remplacé_par_l’alternative_de_gauche,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  25déc.07h35
-/
begin
--   left,
--   solve1 {norm_num at *, compute_n 10 },
  todo
end


lemma exercise.connecteur_oudansbut_1 
(H1 : (m>2) ) (H2 : n =4) :
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
AllGoalsSolved
  True
AutoTest
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  25déc.07h35
-/
begin
--   left, solve1 {norm_num at *, compute_n 10 },
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

lemma exercise.connecteur_oudanshyp_1 
(H : (m=2) \or (n=3)) :
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
AllGoalsSolved
  True
AutoTest
    @P1 use_or 0 success=Preuve_par_cas,
    assumption success=But_en_cours_atteint,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  25déc.07h37
-/
begin
--   cases H with H1 H2,
--   solve1 {norm_num at *, compute_n 10 },
--   solve1 {norm_num at *, compute_n 10 },
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

lemma exercise.connecteur_etoudansbuthyp_2 
{a x y : ℝ} (H : (x <= y) \and ( (a<0) \or (a>0))) :
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
AllGoalsSolved
  True
AutoTest
    @P1 use_and success=Propriété_H_découpée_en_H1_et_H2,
    @P2 use_or 0 success=Preuve_par_cas,
    target prove_or 1 success=But_remplacé_par_l’alternative_de_droite,
    assumption success=But_en_cours_atteint,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  25déc.07h38
-/
begin
--   cases H with H1 H2,
--   cases H2 with H3 H4,
--   right,
--   solve1 {compute_n 10 },
--   left, solve1 {norm_num at *, compute_n 10 },
  todo
end


lemma exercise.connecteur_etoudansbuthyp_1 
{a x y : ℝ} (H : (x <= y) \and ( (a<0) \or (a>0))) :
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
AllGoalsSolved
  True
AutoTest
    @P1 use_and success=Propriété_H_découpée_en_H1_et_H2,
    @P2 use_or 0 success=Preuve_par_cas,
    target prove_or 1 success=But_remplacé_par_l’alternative_de_droite,
    assumption success=But_en_cours_atteint,
    target prove_or 0 success=But_remplacé_par_l’alternative_de_gauche,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  25déc.07h38
-/
begin
--   cases H with H1 H2,
--   cases H2 with H3 H4,
--   right,
--   solve1 {compute_n 10 },
--   left,
--   solve1 {norm_num at *, compute_n 10 },
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

lemma exercise.connecteur_impliquedansbut1_1 
 :
( m + n >=5) → (m+n >= 3)
:=
/- dEAduction
PrettyName
  Connecteur IMPLIQUE dans but (1) - Cas d'une proposition vraie en prémisse.
Description
  Le bouton "=>" permet de démontrer une implication : pour démontrer "P => Q", on suppose P, et on montre Q.
AvailableLogic
  implies
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    target prove_implies success=Propriété_H1_ajoutée_au_contexte,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  25déc.07h39
-/
begin
--   intro H1,
--   solve1 {norm_num at *, compute_n 10 },
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

lemma exercise.connecteur_impliquedansbut2_1 
 :
( 1 = 5 ) → (m+n >= 3)
:=
/- dEAduction
PrettyName
  Connecteur IMPLIQUE dans but (2) - Cas d'une proposition fausse en prémisse
Description
  Le bouton "=>" permet de démontrer une implication : pour démontrer "P => Q", on suppose P, et on montre Q. Attention : Si P est fausse, alors l'implication "P => Q" est vraie, quelle que soit la proposition Q.
AvailableLogic
  implies
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    target prove_implies success=Propriété_H1_ajoutée_au_contexte,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.08h49
-/
begin
--   intro H1,
--   cc,
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

lemma exercise.connecteur_equal_1 
(H1:  (m+3*n =100) ) (H2 : m=10 ) :
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
AllGoalsSolved
  True
AutoTest
    @P1 @P2 equal 1 success=m_remplacé_par_10_dans_H1,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.08h49
-/
begin
--   rw H2 at H1,
--   solve1 {compute_n 10 },
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

lemma exercise.connecteur_impliquedanshyp_1 
(H1: ( m >=5) → (m+n =100) ) (H2 : m=10 ) :
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
AllGoalsSolved
  True
AutoTest
    @P1 use_implies 0 success=Le_nouveau_but_sera_ajouté_au_contexte_quand_il_aura_été_démontré,
    assumption success=But_en_cours_atteint,
    @P3 @P1 use_implies success=Propriété_H4_ajoutée_au_contexte,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.08h50
-/
begin
--   have H3: (m ≥ ((5): @nat)),
--   solve1 {norm_num at *, compute_n 10 },
--   have H4 := H1 H3,
--   cc,
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

lemma exercise.connecteur_impliquedanshyp2_1 
(H1: ( m >=5) → (m+n =100) ) (H2 : m=10 ) :
n = 90  -- utilisation de equal pour arriver au but
:=
/- dEAduction
PrettyName
  Connecteur IMPLIQUE dans hypothèse et bouton EGALITE - Deuxième forme
Description
  Le bouton "=>" permet d'utiliser une implication dans une hypothèse : à partir de  "P => Q" et de "P" on en déduit "Q".  Le bouton "=" permet de remplacer une expression par une autre qui lui est égale.
AvailableLogic
  implies equal
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    @P1 @P2 equal success=m_remplacé_par_10_dans_H1,
    @P1 use_implies 0 success=Le_nouveau_but_sera_ajouté_au_contexte_quand_il_aura_été_démontré,
    assumption success=But_en_cours_atteint,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.08h51
-/
begin
--   rw H2 at H1,
--   have H3: (((10): @nat) ≥ ((5): @nat)),
--   solve1 {norm_num at * },
--   solve1 {norm_num at *, compute_n 10 },
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

lemma exercise.ssi1_1 
{ x  : ℝ} :
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
AllGoalsSolved
  True
AutoTest
    target iff 0 success=Equivalence_séparée_en_deux_implications,
    target prove_implies success=Propriété_H1_ajoutée_au_contexte,
    @P1 use_and success=Propriété_H1_découpée_en_H2_et_H3,
    assumption success=But_en_cours_atteint,
    target prove_implies success=Propriété_H4_ajoutée_au_contexte,
    target prove_and 0 success=On_décompose_le_but,
    assumption success=But_en_cours_atteint,
    target prove_or 0 success=But_remplacé_par_l’alternative_de_gauche,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.08h52
-/
begin
--   split,
--   intro H1,
--   cases H1 with H2 H3,
--   assumption,
--   intro H4,
--   split,
--   assumption,
--   left,
--   solve1 {norm_num at *, compute_n 10 },
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
    and or not implies iff
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.ssi2_2 
(H1: m*n=0 ↔ ( m=0 \or n=0) ) 
 (H2: (m*n = 0) \or (m*n =1) \or (m*n >= 2) ) :
( not(m*n =1))→  ( (m=0) \or (n=0) \or (m*n >= 2) )
:=
/- dEAduction
PrettyName
  Connecteur EQUIVALENT dans une hypothèse
Description
  Le bouton "<=>" permet d'utiliser une des implications de l'hypothèse.
AvailableLogic
  and or not implies iff
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    target prove_implies success=Propriété_H3_ajoutée_au_contexte,
    @P2 use_or 0 success=Preuve_par_cas,
    @P3 use_or 0 success=Preuve_par_cas,
    @P3 @P1 use_implies success=Propriété_H8_ajoutée_au_contexte,
    assumption success=But_en_cours_atteint,
    assumption success=But_en_cours_atteint,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.08h57
-/
begin
--   intro H3,
--   cases H2 with H4 H5,
--   cases H4 with H6 H7,
--   have H8 := (H1 ).mp H6,
--   cc,
--   contradiction,
--   right, assumption,
  todo
end


lemma exercise.ssi2_1 
(H1: m*n=0 ↔ ( m=0 \or n=0) ) 
 (H2: (m*n = 0) \or (m*n =1) \or (m*n >= 2) ) :
( not(m*n =1))→  ( (m=0) \or (n=0) \or (m*n >= 2) )
:=
/- dEAduction
PrettyName
  Connecteur EQUIVALENT dans une hypothèse
Description
  Le bouton "<=>" permet d'utiliser une des implications de l'hypothèse.
AvailableLogic
  and or not implies iff
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    @P1 iff success=Propriété_H1_séparée_en_H3_et_H4,
    target prove_implies success=Propriété_H5_ajoutée_au_contexte,
    @P2 use_or 1 success=Preuve_par_cas,
    assumption success=But_en_cours_atteint,
    @P5 use_or 0 success=Preuve_par_cas,
    @P5 @P2 use_implies success=Propriété_H10_ajoutée_au_contexte,
    target prove_or 0 success=But_remplacé_par_l’alternative_de_gauche,
    assumption success=But_en_cours_atteint,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.08h55
-/
begin
--   cases (iff_def.mp H1) with H3 H4,
--   intro H5,
--   rw or.comm at H2, cases H2 with H6 H7,
--   right, assumption,
--   cases H7 with H8 H9,
--   have H10 := H3 H8,
--   left,
--   assumption,
--   contradiction,
  todo
end


end course