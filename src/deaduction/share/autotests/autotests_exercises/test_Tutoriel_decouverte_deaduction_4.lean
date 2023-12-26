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
    Tutoriel d'utilisation du logiciel dans un contexte de manipulations des entiers ou réels - Partie 4 : Méthodes de preuves
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
DefaultAvailableLogic
    ALL -mapsto
DefaultAvailableProof
    proof_methods 
DefaultAvailableMagic
    Assumption
AvailableCompute
    NONE
Display
   estquotiententier --> ( -2, " / ", -1, " est quotient entier ") 
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

lemma exercise.absurde1_2 
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
AllGoalsSolved
  True
AutoTest
    proof_methods 2 success=La_négation_du_but_est_ajoutée_au_contexte,
    @P4 not success=Négation_« poussée »_sur_la_propriété_H4,
    @P2 use_forall [ x__+__1 x__+__3 ] success=Propriété_H5_ajoutée_au_contexte,
    @P5 use_implies 0 success=Le_nouveau_but_sera_ajouté_au_contexte_quand_il_aura_été_démontré,
    target prove_and 1 success=On_décompose_le_but,
    @P1 target proof_methods 1 success=Preuve_par_contraposée_avec_l’hypothèse_H1,
    target not success=Négation_« poussée »_sur_le_but,
    @P5 not success=Négation_« poussée »_sur_la_propriété_H7,
    assumption success=But_en_cours_atteint,
    assumption success=But_en_cours_atteint,
    @P6 @P5 use_implies success=Propriété_H8_ajoutée_au_contexte,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.14h04
-/
begin
--   by_contradiction H4,
--   push_neg_once at H4,
--   have H5 := @H2 (x + 1) (x + 3),
--   have H6: ((((x + ((1): @real))/(x + ((3): @real))) = ((1): @real)) and ((x + ((3): @real)) ≠ ((0): @real))),
--   rw and.comm, split,
--   contrapose H1 with H7,
--   push_neg_once,
--   push_neg_once at H7,
--   solve1 {norm_num at *, compute_n 10 },
--   assumption,
--   have H8 := H5 H6,
--   solve1 {norm_num at * },
  todo
end


lemma exercise.absurde1_1 
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
AllGoalsSolved
  True
AutoTest
    proof_methods 2 success=La_négation_du_but_est_ajoutée_au_contexte,
    @P4 not success=Négation_« poussée »_sur_la_propriété_H4,
    @P1 @P3 use_implies success=Propriété_H5_ajoutée_au_contexte,
    @P4 @P5 prove_and success=Conjonction_H6_ajoutée_au_contexte,
    @P4 @P2 use_implies success=Propriété_H7_ajoutée_au_contexte,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.14h02
-/
begin
--   by_contradiction H4,
--   push_neg_once at H4,
--   have H5 := (H3 _).mpr H1,
--   have H6 := and.intro H4 H5, clear H4, clear H5,
--   have H7 := H2 _ _ H6,
--   solve1 {norm_num at * },
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

lemma exercise.absurde4_1 
{m n : ℕ}   (H1: pair m) (H2: impair n) :
not(estquotiententier n m )
:=
/- dEAduction
PrettyName
  Raisonnement par l'absurde (4) - Entiers
Description
  Raisonnement par l'absurde (4)  - Entiers -  Indication : Utiliser le nouveau théorème "condition pour être pair" (une implication de la définition), ou alors introduire un nouveau but.
AvailableProof
  proof_methods new_object
AvailableMagic
  assumption
AllGoalsSolved
  True
AutoTest
    proof_methods 2 success=La_négation_du_but_est_ajoutée_au_contexte,
    @P3 definition.estquotiententier success=Définition_appliquée_à_H3,
    @P3 use_exists success=Nouvel_objet_k_vérifiant_la_propriété_H5,
    @P1 definition.pair success=Définition_appliquée_à_H1,
    @P1 use_exists success=Nouvel_objet_j_vérifiant_la_propriété_H8,
    @P3 @P2 equal 0 success=m_remplacé_par_2_×_j_dans_H5,
    @P1 theorem.nonpair success=Théorème_appliqué_à_H2,
    definition.pair [ n ] success=Propriété_H11_ajoutée_au_contexte,
    @P4 iff success=Propriété_H11_séparée_en_H12_et_H13,
    @P6 use_implies 0 success=Le_nouveau_but_sera_ajouté_au_contexte_quand_il_aura_été_démontré,
    target prove_exists [ k__*__j ] success=Il_reste_à_démontrer_que_k_×_j_convient,
    @P2 equal success=n_remplacé_par_k_×_(2_×_j)_dans_le_but,
    assumption success=But_en_cours_atteint,
    @P7 @P6 use_implies success=Propriété_H15_ajoutée_au_contexte,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.14h24
-/
begin
--   by_contradiction H3,
--   rw decouverte_methodes_preuves.definition.estquotiententier at H3,
--   cases H3 with k H5,
--   rw decouverte_methodes_preuves.definition.pair at H1,
--   cases H1 with j H8,
--   rw H8 at H5,
--   rw <- decouverte_methodes_preuves.theorem.nonpair at H2,
--   have H11 := @decouverte_methodes_preuves.definition.pair (n),
--   cases (iff_def.mp H11) with H12 H13,
--   have H14: (∃i: @nat, (n = (((2): @nat) * i))),
--   use (k * j),
--   rw H5,
--   ac_reflexivity,
--   have H15 := H13 H14,
--   contradiction,
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
(not (A = ∅) ) ↔ ∃ x : X, x ∈ A
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

lemma exercise.absurde5_1 
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
AllGoalsSolved
  True
AutoTest
    proof_methods 2 success=La_négation_du_but_est_ajoutée_au_contexte,
    @P1 definition.ensemble_non_vide success=Définition_appliquée_à_H1,
    @P1 use_exists success=Nouvel_objet_x_vérifiant_la_propriété_H3,
    @P1 definition.intersection_deux_ensembles success=Définition_appliquée_à_H3,
    @P1 use_and success=Propriété_H3_découpée_en_H6_et_H7,
    @P2 definition.difference success=Définition_appliquée_à_H7,
    @P2 use_and success=Propriété_H7_découpée_en_H9_et_H10,
    assumption success=La_preuve_est_terminée_!,
Settings
  functionality.default_functionality_level --> "Free settings"
  functionality.allow_implicit_use_of_definitions --> True
  functionality.target_selected_by_default --> True
HistoryDate
  26déc.14h27
-/
begin
--   by_contradiction H1,
--   rw decouverte_methodes_preuves.definition.ensemble_non_vide at H1,
--   cases H1 with x H3,
--   rw decouverte_methodes_preuves.definition.intersection_deux_ensembles at H3,
--   cases H3 with H6 H7,
--   rw decouverte_methodes_preuves.definition.difference at H7,
--   cases H7 with H9 H10,
--   contradiction,
  todo
end



end decouverte_methodes_preuves

end course