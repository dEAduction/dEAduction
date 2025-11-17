/-
Feuille d'exercice pour travailler les applications sur les ensembles - Exercices classiques
-/

-- Lean standard imports
import tactic
import data.real.basic
import data.set


-- dEAduction tactics
-- structures2 and utils are vital
import deaduction_all_tactics
-- import structures2      -- hypo_analysis, targets_analysis
-- import utils            -- no_meta_vars
-- import compute_all      -- Tactics for the compute buttons
-- import push_neg_once    -- Pushing negation just one step
-- import induction        -- Induction theorems

-- dEAduction definitions
import set_definitions
--import real_definitions

-- Use classical logic
local attribute [instance] classical.prop_decidable





-------------------------
-- dEAduction METADATA --
-------------------------


/- dEAduction
title = "Théorie des ensembles : applications"
author = "Isabelle Dubois"
institution = "Université de Lorraine"
description = 'Ce cours correspond à un cours standard de théorie "élémentaire" des ensembles. Partie Applications.'
available_exercises = "NONE"
-/

local attribute [instance] classical.prop_decidable

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
parameters {X Y Z: Type}


open set



namespace generalites
/- dEAduction
pretty_name = "Généralités"
-/

------------------------
-- COURSE DEFINITIONS --
------------------------

variables  {A A': set X}
variables {f: X → Y} {B B': set Y}
variables {I : index_set} {E : set_family I X} {F : set_family I Y}
variables (g : Y → Z) (h : X → Z)

namespace generalites_ensembles
/- dEAduction
pretty_name = "Généralités sur les ensembles"
-/

lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
/- dEAduction
implicit_use = true
-/
begin
    todo
end

lemma definition.egalite_deux_ensembles {A A' : set X} :
(A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
pretty_name = "Egalité de deux ensembles"
implicit_use = true
-/
begin
     todo
end
lemma definition.intersection_deux_ensembles {A B : set X} {x : X} :
x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B) :=
/- dEAduction
pretty_name = "Intersection de deux ensembles"
implicit_use = true
-/
begin
    exact iff.rfl
end



lemma definition.union_deux_ensembles  {A : set X} {B : set X} {x : X} :
x ∈ A ∪ B ↔ ( x ∈ A ∨ x ∈ B) :=
/- dEAduction
pretty_name = "Union de deux ensembles"
implicit_use = true
-/
begin
    exact iff.rfl
end

lemma definition.complement {A : set X} {x : X} : x ∈ set.compl A ↔ x ∉ A :=
/- dEAduction
pretty_name = "Complémentaire"
-/
begin
    finish
end

lemma definition.union_quelconque_ensembles {I : index_set} {E : I → set X}  {x : X} :
(x ∈ set.Union E) ↔ (∃ i:I, x ∈ E i) :=
/- dEAduction
pretty_name = "Union d'une famille quelconque d'ensembles"
-/
begin
    exact set.mem_Union
end

lemma definition.intersection_quelconque_ensembles {I : index_set} {E : I → set X}  {x : X} :
(x ∈ set.Inter E) ↔ (∀ i:I, x ∈ E i) :=
/- dEAduction
pretty_name = "Intersection d'une famille quelconque d'ensembles"
-/
begin
    exact set.mem_Inter
end

lemma definition.ensemble_vide
(A: set X) :
(A = ∅) ↔ ∀ x : X, x ∉ A
:=
begin
    todo
end


lemma definition.singleton {X : Type} {x y : X}: x ∈ ({y} : set X) ↔ x = y
:=
/- dEAduction
pretty_name = "Ensemble singleton"
-/
begin
    todo
end

end generalites_ensembles

namespace generalites_applications
/- dEAduction
pretty_name = "Généralités sur les applications"
-/


lemma definition.image_directe (y : Y) : y ∈ f '' A ↔ ∃ x : X, x ∈ A ∧  f x = y :=
begin
    todo
end

lemma definition.image_reciproque (x:X) : x ∈ f  ⁻¹' B ↔ f(x) ∈ B :=
begin
    todo
end



lemma definition.composition {x:X}:
 function.comp g f x = g (f x)
:=
begin
   refl,
end

lemma definition.egalite_fonctions (f' : X → Y) :
f = f' ↔ ∀ x, f x = f' x :=
/- dEAduction
pretty_name = "Egalité de deux fonctions"
-/
begin
    exact function.funext_iff,
end


lemma definition.Identite (f₀: X → X) :
f₀ = Identite ↔ ∀ x, f₀ x = x :=
/- dEAduction
pretty_name = "Application identité"
-/
begin
    apply definition.egalite_fonctions,
end

end generalites_applications

namespace injection_surjection

lemma definition.injectivite :
injective f ↔ ∀ x y : X, (f x = f y → x = y)
:=
/- dEAduction
pretty_name = "Application injective"
implicit_use = true
-/
begin
    refl,
end

lemma definition.surjectivite :
surjective f ↔ ∀ y : Y, ∃ x : X, y = f x
:=
/- dEAduction
pretty_name = "Application surjective"
implicit_use = true
-/
begin
    refl,
end

-- A bouger, mais à enlever de tous les exos où ça ne sert pas !
lemma definition.existe_un_unique
(P : X → Prop) :
(∃! (λx,  P x)) ↔  (∃ x : X, (P x ∧ (∀ x' : X, P x' → x' = x)))
:=
/- dEAduction
pretty_name = "∃! : existence et unicité"
-/
begin
    todo
end

lemma definition.bijectivite_1 :
bijective f ↔ (injective f ∧ surjective f)
:=
/- dEAduction
pretty_name = "Application bijective (première définition)"
-/
begin
    todo
end

lemma definition.bijectivite_2 :
bijective f ↔ ∀ y : Y, exists_unique (λ x, y = f x)
:=
/- dEAduction
pretty_name = "Application bijective (seconde définition)"
-/
begin
    refl,
end

end injection_surjection

end generalites

---------------
-- SECTION 1 --
---------------
namespace images_directes_et_reciproques
/- dEAduction
pretty_name = "Images directes et réciproques"
-/
open generalites


variables  {A A': set X}
variables {f: X → Y} {B B': set Y}
variables {I : index_set} {E : set_family I X} {F : set_family I Y}
variables (g : Y → Z) (h : X → Z)

---------------
-- EXERCICES --
---------------

lemma exercise.image_de_reciproque : f '' (f ⁻¹' B)  ⊆ B :=
/- dEAduction
pretty_name = "Image de l'image réciproque"
-/
begin
    todo
end

lemma exercise.image_de_reciproque_1 
 :
 f '' (f ⁻¹' B)  ⊆ B :=
/- dEAduction
all_goals_solved = "True"
history_date = "15nov.22h17"
[[auto_test]]
target_selected = true
statement = "definition.inclusion"
success_msg = "Définition appliquée au but"
[[auto_test]]
target_selected = true
button = "prove_forall"
success_msg = "Objet y ajouté au contexte"
[[auto_test]]
selection = [ "@P1" ]
statement = "definition.image_directe"
success_msg = "Définition appliquée à H_0"
[[auto_test]]
selection = [ "@P1" ]
button = "use_exists"
success_msg = "Nouvel objet x vérifiant la propriété H_1"
[[auto_test]]
selection = [ "@P1" ]
button = "use_and"
success_msg = "Propriété H_1 découpée en H_2 et H_3"
[[auto_test]]
selection = [ "@P1" ]
statement = "definition.image_reciproque"
success_msg = "Définition appliquée à H_2"
[[auto_test]]
selection = [ "@P1", "@P2" ]
button = "equal"
success_msg = "f(x) remplacé par y dans H_2"
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
--   rw generalites.generalites_ensembles.definition.inclusion, trace "EFFECTIVE CODE n°1.0", trace "EFFECTIVE CODE n°2.1", trace "EFFECTIVE CODE n°0.0",
--   intro y, intro H_0,
--   rw generalites.generalites_applications.definition.image_directe at H_0, trace "EFFECTIVE CODE n°4.0", trace "EFFECTIVE CODE n°5.1", trace "EFFECTIVE CODE n°3.0",
--   cases H_0 with x H_1,
--   cases H_1 with H_2 H_3,
--   rw generalites.generalites_applications.definition.image_reciproque at H_2, trace "EFFECTIVE CODE n°8.0", trace "EFFECTIVE CODE n°9.1", trace "EFFECTIVE CODE n°7.0",
--   rw H_3 at H_2, trace "EFFECTIVE CODE n°12.0", trace "EFFECTIVE CODE n°11.0",
--   assumption, trace "EFFECTIVE CODE n°14.0",
  todo
end


lemma exercise.reciproque_de_image : A ⊆ f ⁻¹' (f '' A) :=
/- dEAduction
pretty_name = "Image réciproque de l'image"
-/
begin
    todo
end

lemma exercise.reciproque_de_image_1 
 :
 A ⊆ f ⁻¹' (f '' A) :=
/- dEAduction
all_goals_solved = "True"
history_date = "15nov.22h19"
[[auto_test]]
target_selected = true
statement = "definition.inclusion"
success_msg = "Définition appliquée au but"
[[auto_test]]
target_selected = true
button = "prove_forall"
success_msg = "Objet x ajouté au contexte"
[[auto_test]]
target_selected = true
statement = "definition.image_reciproque"
success_msg = "Définition appliquée au but"
[[auto_test]]
target_selected = true
statement = "definition.image_directe"
success_msg = "Définition appliquée au but"
[[auto_test]]
selection = [ "@O5" ]
button = "prove_exists"
success_msg = "Il reste à démontrer que x convient"
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
--   rw generalites.generalites_ensembles.definition.inclusion, trace "EFFECTIVE CODE n°19.0", trace "EFFECTIVE CODE n°20.1", trace "EFFECTIVE CODE n°18.0",
--   intro x, intro H_0,
--   rw generalites.generalites_applications.definition.image_reciproque, trace "EFFECTIVE CODE n°22.0", trace "EFFECTIVE CODE n°23.1", trace "EFFECTIVE CODE n°21.0",
--   rw generalites.generalites_applications.definition.image_directe, trace "EFFECTIVE CODE n°25.0", trace "EFFECTIVE CODE n°26.1", trace "EFFECTIVE CODE n°24.0",
--   use (x),
--   split, assumption, trace "EFFECTIVE CODE n°30.0", refl, trace "EFFECTIVE CODE n°33.0", trace "EFFECTIVE CODE n°32.2", trace "EFFECTIVE CODE n°27.4",
  todo
end


lemma exercise.image_reciproque_inter :  f ⁻¹'  (B∩B') = f ⁻¹'  (B) ∩ f ⁻¹'  (B') :=
/- dEAduction
pretty_name = "Image réciproque d'une intersection de deux ensembles"
-/
begin
    todo
end

lemma  exercise.image_reciproque_union  : f ⁻¹' (B ∪ B') = f ⁻¹' B ∪ f ⁻¹' B'
:=
/- dEAduction
pretty_name = "Image réciproque d'une union de deux ensembles"
-/
begin
    todo
end


lemma exercise.image_reciproque_inter_quelconque :
(f ⁻¹'  (set.Inter (F))) = set.Inter (λ i, f ⁻¹' (F i): set_family I X)
-- (f ⁻¹'  (set.Inter (λ i, F i))) = set.Inter (λ i, f ⁻¹' (F i))
:=
/- dEAduction
pretty_name = "Image réciproque d'une intersection quelconque"
-/
begin
    todo
end

lemma exercise.image_reciproque_inter_quelconque_1 
 :
(f ⁻¹'  (set.Inter (F))) = set.Inter (λ i, f ⁻¹' (F i): set_family I X)
-- (f ⁻¹'  (set.Inter (λ i, F i))) = set.Inter (λ i, f ⁻¹' (F i))
:=
/- dEAduction
all_goals_solved = "True"
history_date = "15nov.22h20"
[[auto_test]]
target_selected = true
statement = "definition.egalite_deux_ensembles"
success_msg = "Définition appliquée au but"
[[auto_test]]
target_selected = true
button = "prove_forall"
success_msg = "Objet x ajouté au contexte"
[[auto_test]]
target_selected = true
statement = "definition.image_reciproque"
success_msg = "Définition appliquée au but"
[[auto_test]]
target_selected = true
statement = "definition.intersection_quelconque_ensembles"
success_msg = "Définition appliquée au but"
[[auto_test]]
target_selected = true
statement = "definition.image_reciproque"
success_msg = "Définition appliquée au but"
[[auto_test]]
target_selected = true
statement = "definition.intersection_quelconque_ensembles"
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
--   rw generalites.generalites_ensembles.definition.egalite_deux_ensembles, trace "EFFECTIVE CODE n°38.0", trace "EFFECTIVE CODE n°39.1", trace "EFFECTIVE CODE n°37.0",
--   intro x,
--   rw generalites.generalites_applications.definition.image_reciproque, trace "EFFECTIVE CODE n°41.0", trace "EFFECTIVE CODE n°42.1", trace "EFFECTIVE CODE n°40.0",
--   rw generalites.generalites_ensembles.definition.intersection_quelconque_ensembles, trace "EFFECTIVE CODE n°44.0", trace "EFFECTIVE CODE n°45.1", trace "EFFECTIVE CODE n°43.0",
--   simp_rw <- generalites.generalites_applications.definition.image_reciproque, trace "EFFECTIVE CODE n°47.3", trace "EFFECTIVE CODE n°48.1", trace "EFFECTIVE CODE n°46.0",
--   rw generalites.generalites_ensembles.definition.intersection_quelconque_ensembles, trace "EFFECTIVE CODE n°50.0", trace "EFFECTIVE CODE n°51.1", trace "EFFECTIVE CODE n°49.0",
  todo
end


lemma exercise.image_reciproque_union_quelconque :
(f ⁻¹'  (set.Union (λ i, F i))) = set.Union (λ i, f ⁻¹' (F i))
:=
/- dEAduction
pretty_name = "Image réciproque d'une union quelconque"
-/
begin
    todo
end

lemma exercise.inclusion_image_directe :
A ⊆ A' → f '' (A) ⊆ f '' (A')
:=
/- dEAduction
pretty_name = "L'image directe préserve l'inclusion"
-/
begin
    todo
end

lemma exercise.inclusion_image_directe_1 
 :
A ⊆ A' → f '' (A) ⊆ f '' (A')
:=
/- dEAduction
all_goals_solved = "True"
history_date = "15nov.22h22"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_0 ajoutée au contexte"
[[auto_test]]
target_selected = true
statement = "definition.inclusion"
success_msg = "Définition appliquée au but"
[[auto_test]]
target_selected = true
button = "prove_forall"
success_msg = "Objet y ajouté au contexte"
[[auto_test]]
selection = [ "@P2" ]
statement = "definition.image_directe"
success_msg = "Définition appliquée à H_1"
[[auto_test]]
selection = [ "@P2" ]
button = "use_exists"
success_msg = "Nouvel objet x vérifiant la propriété H_2"
[[auto_test]]
selection = [ "@P2" ]
button = "use_and"
success_msg = "Propriété H_2 découpée en H_3 et H_4"
[[auto_test]]
selection = [ "@P1" ]
statement = "definition.inclusion"
success_msg = "Définition appliquée à H_0"
[[auto_test]]
selection = [ "@P2", "@P1" ]
button = "use_forall"
success_msg = "Propriété H_5 ajoutée au contexte"
[[auto_test]]
target_selected = true
statement = "definition.image_directe"
success_msg = "Définition appliquée au but"
[[auto_test]]
selection = [ "@O7" ]
button = "prove_exists"
success_msg = "Il reste à démontrer que x convient"
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
--   rw generalites.generalites_ensembles.definition.inclusion, trace "EFFECTIVE CODE n°53.0", trace "EFFECTIVE CODE n°54.1", trace "EFFECTIVE CODE n°52.0",
--   intro y, intro H_1,
--   rw generalites.generalites_applications.definition.image_directe at H_1, trace "EFFECTIVE CODE n°56.0", trace "EFFECTIVE CODE n°57.1", trace "EFFECTIVE CODE n°55.0",
--   cases H_1 with x H_2,
--   cases H_2 with H_3 H_4,
--   rw generalites.generalites_ensembles.definition.inclusion at H_0, trace "EFFECTIVE CODE n°60.0", trace "EFFECTIVE CODE n°61.1", trace "EFFECTIVE CODE n°59.0",
--   have H_5 := H_0 H_3, trace "EFFECTIVE CODE n°63.0",
--   rw generalites.generalites_applications.definition.image_directe, trace "EFFECTIVE CODE n°65.0", trace "EFFECTIVE CODE n°66.1", trace "EFFECTIVE CODE n°64.0",
--   use (x),
--   cc, trace "EFFECTIVE CODE n°68.1", trace "EFFECTIVE CODE n°67.2",
  todo
end


lemma exercise.image_union :
f '' (A∪ A') = f '' (A) ∪ f '' (A')
:=
/- dEAduction
pretty_name = "Image directe d'une union"
-/
begin
    todo
end

lemma exercise.image_inter_inclus_inter_images :
f '' (A∩A') ⊆ f '' (A) ∩ f '' (A')
:=
/- dEAduction
pretty_name = "Image d'une intersection"
-/
begin
    todo
end

lemma exercise.reciproque_complementaire_I :
f ⁻¹' (set.compl B) ⊆ set.compl (f ⁻¹' B)
:=
/- dEAduction
pretty_name = "Image réciproque du complémentaire, inclusion"
-/
begin
    todo
end

lemma exercise.reciproque_complementaire_I_1 
 :
f ⁻¹' (set.compl B) ⊆ set.compl (f ⁻¹' B)
:=
/- dEAduction
all_goals_solved = "True"
history_date = "15nov.22h23"
[[auto_test]]
target_selected = true
button = "prove_forall"
success_msg = "Objet x ajouté au contexte"
[[auto_test]]
selection = [ "@P1" ]
statement = "definition.image_reciproque"
success_msg = "Définition appliquée à H_0"
[[auto_test]]
selection = [ "@P1" ]
statement = "definition.complement"
success_msg = "Définition appliquée à H_0"
[[auto_test]]
target_selected = true
statement = "definition.complement"
success_msg = "Définition appliquée au but"
[[auto_test]]
target_selected = true
statement = "definition.image_reciproque"
success_msg = "Définition appliquée au but"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
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
--   rw generalites.generalites_ensembles.definition.inclusion, intro x, intro H_0,
--   rw generalites.generalites_applications.definition.image_reciproque at H_0, trace "EFFECTIVE CODE n°84.0", trace "EFFECTIVE CODE n°85.1", trace "EFFECTIVE CODE n°83.0",
--   rw generalites.generalites_ensembles.definition.complement at H_0, trace "EFFECTIVE CODE n°88.0", trace "EFFECTIVE CODE n°89.1", trace "EFFECTIVE CODE n°87.0",
--   rw generalites.generalites_ensembles.definition.complement, trace "EFFECTIVE CODE n°92.0", trace "EFFECTIVE CODE n°93.1", trace "EFFECTIVE CODE n°91.0",
--   rw generalites.generalites_applications.definition.image_reciproque, trace "EFFECTIVE CODE n°95.0", trace "EFFECTIVE CODE n°96.1", trace "EFFECTIVE CODE n°94.0",
--   assumption, trace "EFFECTIVE CODE n°97.0",
  todo
end


lemma exercise.reciproque_complementaire_II :
f ⁻¹' (set.compl B) = set.compl (f ⁻¹' B)
:=
/- dEAduction
pretty_name = "Image réciproque du complémentaire, égalité"
-/
begin
    todo
end

lemma exercise.image_reciproque_composition
(C: set Z)
:
((function.comp g f) )⁻¹' C = f ⁻¹' (g ⁻¹' C)
:=
/- dEAduction
pretty_name = "Image réciproque et composition"
-/
begin
    todo
end

end images_directes_et_reciproques


---------------
-- SECTION 2 --
---------------

namespace inj_surj
/- dEAduction
pretty_name = "Applications injectives, surjectives, bijectives"
-/
open generalites
open generalites.generalites_ensembles
open generalites.injection_surjection
open generalites.generalites_applications

-- variables {A B C : set X}
variables  {A A': set X}
variables {f: X → Y} {B B': set Y}
variables {I : index_set} {E : set_family I X} {F : set_family I Y}
variables (g : Y → Z) (h : X → Z)

lemma exercise.composition_injections
(H1 : injective f) (H2 : injective g)
:
injective (function.comp g f)
:=
/- dEAduction
pretty_name = "Composition d'injections"
-/
begin
    todo
end

lemma exercise.composition_injections_1 
(H1 : injective f) (H2 : injective g) :
injective (function.comp g f)
:=
/- dEAduction
all_goals_solved = "True"
history_date = "15nov.22h25"
[[auto_test]]
target_selected = true
button = "prove_forall"
success_msg = "Objet x ajouté au contexte"
[[auto_test]]
target_selected = true
button = "prove_forall"
success_msg = "Objet y ajouté au contexte"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_3 ajoutée au contexte"
[[auto_test]]
selection = [ "@P3", "@P2" ]
button = "use_implies"
success_msg = "Propriété H_4 ajoutée au contexte"
[[auto_test]]
selection = [ "@P4", "@P1" ]
button = "use_implies"
success_msg = "Propriété H_5 ajoutée au contexte"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
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
--   rw generalites.injection_surjection.definition.injectivite, intro x,
--   intro y,
--   intro H_3,
--   have H_4 := H2 _ _ H_3, trace "EFFECTIVE CODE n°105.2",
--   have H_5 := H1 _ _ H_4, trace "EFFECTIVE CODE n°106.2",
--   assumption, trace "EFFECTIVE CODE n°107.0",
  todo
end


lemma exercise.composition_surjections
(H1 : surjective f) (H2 : surjective g) :
surjective (function.comp g f)
:=
/- dEAduction
pretty_name = "Composition de surjections"
-/
begin
    todo
end

lemma exercise.injective_si_compo_injective
(H1 : injective (function.comp g f)) :
injective f
:=
/- dEAduction
pretty_name = "Injective si composition injective"
-/
begin
    todo
end

lemma exercise.surjective_si_compo_surjective
(H1 : surjective (function.comp g f)) :
surjective g
:=
/- dEAduction
pretty_name = "Surjective si composition surjective"
-/
begin
    todo
end

lemma exercise.surjective_si_inj_et_compo_surjective
(H1 : surjective (function.comp g f)) (H2 : injective g) :
surjective f
:=
/- dEAduction
pretty_name = "f surjective si g injective et  g∘f surjective"
-/
begin
    todo
end

lemma exercise.injective_si_surj_et_compo_injective
(H1 : injective (function.comp g f)) (H2 : surjective f) :
injective g
:=
/- dEAduction
pretty_name = "g injective si f surjective et  g∘f injective"
-/
begin
    todo
end

lemma exercise.comp_comp_f {f : X → X}
(H : f= function.comp (function.comp f f) f )  :
injective f ↔  surjective f
:=
/- dEAduction
pretty_name = "Si f∘f∘f=f alors injectivité équivaut surjectivité"
-/
begin
    todo
end



lemma exercise.bij_comp {f: X → Y} :
bijective f ↔ ∀ A : set X, f '' ( set.compl A ) = ( set.compl (f '' A) )
:=
/- dEAduction
pretty_name = "Bijectivité et image du complémentaire"
-/
begin
    todo
end

lemma exercise.bij_comp_1 
{f: X → Y} :
bijective f ↔ ∀ A : set X, f '' ( set.compl A ) = ( set.compl (f '' A) )
:=
/- dEAduction
history_date = "15nov.22h39"
[[auto_test]]
target_selected = true
button = "prove_and"
user_input = [
    0,
]
success_msg = "Equivalence séparée en deux implications"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_0 ajoutée au contexte"
[[auto_test]]
target_selected = true
button = "prove_forall"
success_msg = "Objet A ajouté au contexte"
[[auto_test]]
target_selected = true
button = "prove_forall"
success_msg = "Objet y ajouté au contexte"
[[auto_test]]
target_selected = true
button = "prove_and"
user_input = [
    0,
]
success_msg = "Equivalence séparée en deux implications"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_1 ajoutée au contexte"
[[auto_test]]
selection = [ "@P2" ]
statement = "definition.image_directe"
success_msg = "Définition appliquée à H_1"
[[auto_test]]
selection = [ "@P2" ]
button = "use_exists"
success_msg = "Nouvel objet x vérifiant la propriété H_2"
[[auto_test]]
selection = [ "@P2" ]
button = "use_and"
success_msg = "Propriété H_2 découpée en H_3 et H_4"
[[auto_test]]
selection = [ "@P3" ]
button = "equal"
success_msg = "y remplacé par f(x) dans le but"
[[auto_test]]
target_selected = true
statement = "definition.complement"
success_msg = "Définition appliquée au but"
[[auto_test]]
target_selected = true
button = "proof_methods"
user_input = [
    2,
]
success_msg = "La négation du but est ajoutée au contexte"
[[auto_test]]
selection = [ "@P4" ]
statement = "definition.image_directe"
success_msg = "Définition appliquée à H_5"
[[auto_test]]
selection = [ "@P4" ]
button = "use_exists"
success_msg = "Nouvel objet z vérifiant la propriété H_6"
[[auto_test]]
selection = [ "@P4" ]
button = "use_and"
success_msg = "Propriété H_6 découpée en H_7 et H_8"
[[auto_test]]
selection = [ "@P1" ]
statement = "definition.bijectivite_1"
success_msg = "Définition appliquée à H_0"
[[auto_test]]
selection = [ "@P1" ]
button = "use_and"
success_msg = "Propriété H_0 découpée en H_9 et H_10"
[[auto_test]]
selection = [ "@P4", "@P5" ]
button = "use_implies"
success_msg = "Propriété H_11 ajoutée au contexte"
[[auto_test]]
selection = [ "@P3", "@P7" ]
button = "equal"
success_msg = "z remplacé par x dans H_7"
[[auto_test]]
button = "assumption"
success_msg = "But en cours atteint"
[[auto_test]]
button = "proof_methods"
user_input = [
    1,
]
success_msg = "Le but est remplacé par sa contraposée"
[[auto_test]]
target_selected = true
statement = "definition.complement"
success_msg = "Définition appliquée au but"
[[auto_test]]
target_selected = true
button = "not"
success_msg = "Négation « poussée » sur le but"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_1 ajoutée au contexte"
[[auto_test]]
selection = [ "@P2" ]
statement = "definition.image_directe"
success_msg = "Définition appliquée à H_1"
[[auto_test]]
selection = [ "@P2" ]
statement = "definition.complement"
success_msg = "Définition appliquée à H_1"
[[auto_test]]
selection = [ "@P2" ]
button = "not"
success_msg = "Négation « poussée » sur la propriété H_1"
[[auto_test]]
selection = [ "@P2" ]
button = "not"
success_msg = "Négation « poussée » sur la propriété H_1"
[[auto_test]]
selection = [ "@P2" ]
button = "not"
success_msg = "Négation « poussée » sur la propriété H_1"
[[auto_test]]
target_selected = true
statement = "definition.image_directe"
success_msg = "Définition appliquée au but"
[[auto_test]]
selection = [ "@P1" ]
statement = "definition.bijectivite_1"
success_msg = "Définition appliquée à H_0"
[[auto_test]]
selection = [ "@P1" ]
button = "use_and"
success_msg = "Propriété H_0 découpée en H_2 et H_3"
[[auto_test]]
selection = [ "@O5", "@P3" ]
button = "use_forall"
success_msg = "Propriété H_4 ajoutée au contexte"
[[auto_test]]
selection = [ "@P4" ]
button = "use_exists"
success_msg = "Nouvel objet x vérifiant la propriété H_5"
[[auto_test]]
selection = [ "@O6" ]
button = "prove_exists"
success_msg = "Il reste à démontrer que x convient"
[[auto_test]]
selection = [ "@O6", "@P1" ]
button = "use_forall"
success_msg = "Propriété H_6 ajoutée au contexte"
[[auto_test]]
selection = [ "@P5" ]
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
success_msg = "But en cours atteint"
[[auto_test]]
button = "proof_methods"
user_input = [
    1,
]
success_msg = "Le but est remplacé par sa contraposée"
[[auto_test]]
target_selected = true
button = "prove_implies"
success_msg = "Propriété H_0 ajoutée au contexte"
[[auto_test]]
selection = [ "@P1" ]
statement = "definition.bijectivite_1"
success_msg = "Définition appliquée à H_0"
[[auto_test]]
selection = [ "@P1" ]
button = "not"
success_msg = "Négation « poussée » sur la propriété H_0"
[[auto_test]]
target_selected = true
button = "not"
success_msg = "Négation « poussée » sur le but"
[[auto_test]]
selection = [ "@P1" ]
button = "use_or"
user_input = [
    0,
]
success_msg = "Preuve par cas"
[[auto_test]]
selection = [ "@P1" ]
statement = "definition.injectivite"
success_msg = "Définition appliquée à H_1"
[[auto_test]]
selection = [ "@P1" ]
button = "not"
success_msg = "Négation « poussée » sur la propriété H_1"
[[auto_test]]
selection = [ "@P1" ]
button = "use_exists"
success_msg = "Nouvel objet x vérifiant la propriété H_2"
[[auto_test]]
selection = [ "@P1" ]
button = "not"
success_msg = "Négation « poussée » sur la propriété H_2"
[[auto_test]]
selection = [ "@P1" ]
button = "use_exists"
success_msg = "Nouvel objet y vérifiant la propriété H_3"
[[auto_test]]
selection = [ "@P1" ]
button = "not"
success_msg = "Négation « poussée » sur la propriété H_3"
[[auto_test]]
selection = [ "@P1" ]
button = "use_and"
success_msg = "Propriété H_3 découpée en H_4 et H_5"
[[auto_test]]
target_selected = true
button = "prove_exists"
user_input = [
    [
        "((singleton x): (set X))",
    ],
]
success_msg = "Il reste à démontrer que {x} convient"
[[auto_test]]
target_selected = true
statement = "definition.egalite_deux_ensembles"
success_msg = "Définition appliquée au but"
[[auto_test]]
target_selected = true
button = "not"
success_msg = "Négation « poussée » sur le but"
[[auto_test]]
target_selected = true
button = "prove_exists"
user_input = [
    [
        "f x ",
    ],
]
success_msg = "Il reste à démontrer que f(x) convient"
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
--   split,
--   intro H_0,
--   intro A,
--   rw generalites.generalites_ensembles.definition.egalite_deux_ensembles, intro y,
--   split,
--   intro H_1,
--   rw generalites.generalites_applications.definition.image_directe at H_1, trace "EFFECTIVE CODE n°129.0", trace "EFFECTIVE CODE n°130.1", trace "EFFECTIVE CODE n°128.0",
--   cases H_1 with x H_2,
--   cases H_2 with H_3 H_4,
--   rw <- H_4, trace "EFFECTIVE CODE n°134.0", trace "EFFECTIVE CODE n°132.1",
--   rw generalites.generalites_ensembles.definition.complement, trace "EFFECTIVE CODE n°136.0", trace "EFFECTIVE CODE n°137.1", trace "EFFECTIVE CODE n°135.0",
--   by_contradiction H_5,
--   rw generalites.generalites_applications.definition.image_directe at H_5, trace "EFFECTIVE CODE n°139.0", trace "EFFECTIVE CODE n°140.1", trace "EFFECTIVE CODE n°138.0",
--   cases H_5 with z H_6,
--   cases H_6 with H_7 H_8,
--   rw generalites.injection_surjection.definition.bijectivite_1 at H_0, trace "EFFECTIVE CODE n°143.0", trace "EFFECTIVE CODE n°144.1", trace "EFFECTIVE CODE n°142.0",
--   cases H_0 with H_9 H_10,
--   have H_11 := H_9 _ _ H_8, trace "EFFECTIVE CODE n°146.2",
--   rw H_11 at H_7, trace "EFFECTIVE CODE n°148.0", trace "EFFECTIVE CODE n°147.0",
--   contradiction, trace "EFFECTIVE CODE n°150.1",
--   contrapose,
--   rw generalites.generalites_ensembles.definition.complement, trace "EFFECTIVE CODE n°165.0", trace "EFFECTIVE CODE n°166.1", trace "EFFECTIVE CODE n°164.0",
--   push_neg_once, trace "EFFECTIVE CODE n°167.1",
--   intro H_1,
--   rw generalites.generalites_applications.definition.image_directe at H_1, trace "EFFECTIVE CODE n°169.0", trace "EFFECTIVE CODE n°170.1", trace "EFFECTIVE CODE n°168.0",
--   simp_rw generalites.generalites_ensembles.definition.complement at H_1, trace "EFFECTIVE CODE n°177.1", trace "EFFECTIVE CODE n°178.1", trace "EFFECTIVE CODE n°176.0",
--   push_neg_once at H_1, trace "EFFECTIVE CODE n°180.1",
--   push_neg_once at H_1, simp only [ne.def] at H_1, trace "EFFECTIVE CODE n°181.0",
--   push_neg_once at H_1, simp only [ne.def] at H_1, trace "EFFECTIVE CODE n°182.0",
--   rw generalites.generalites_applications.definition.image_directe, trace "EFFECTIVE CODE n°184.0", trace "EFFECTIVE CODE n°185.1", trace "EFFECTIVE CODE n°183.0",
--   rw generalites.injection_surjection.definition.bijectivite_1 at H_0, trace "EFFECTIVE CODE n°187.0", trace "EFFECTIVE CODE n°188.1", trace "EFFECTIVE CODE n°186.0",
--   cases H_0 with H_2 H_3,
--   have H_4 := H_3 y, trace "EFFECTIVE CODE n°190.0",
--   cases H_4 with x H_5,
--   use (x),
--   have H_6 := H_1 x, trace "EFFECTIVE CODE n°191.0",
--   cases H_6 with H_7 H_8,
--   cc, trace "EFFECTIVE CODE n°193.1", trace "EFFECTIVE CODE n°192.2",
--   cc, trace "EFFECTIVE CODE n°209.1", trace "EFFECTIVE CODE n°208.2",
--   contrapose,
--   intro H_0,
--   rw generalites.injection_surjection.definition.bijectivite_1 at H_0, trace "EFFECTIVE CODE n°225.0", trace "EFFECTIVE CODE n°226.1", trace "EFFECTIVE CODE n°224.0",
--   push_neg_once at H_0, trace "EFFECTIVE CODE n°228.1",
--   push_neg_once, simp only [ne.def] , trace "EFFECTIVE CODE n°229.0",
--   cases H_0 with H_1 H_2,
--   rw generalites.injection_surjection.definition.injectivite at H_1, trace "EFFECTIVE CODE n°231.0", trace "EFFECTIVE CODE n°232.1", trace "EFFECTIVE CODE n°230.0",
--   push_neg_once at H_1, trace "EFFECTIVE CODE n°234.1",
--   cases H_1 with x H_2,
--   push_neg_once at H_2, trace "EFFECTIVE CODE n°235.1",
--   cases H_2 with y H_3,
--   push_neg_once at H_3, simp only [ne.def] at H_3, trace "EFFECTIVE CODE n°236.0",
--   cases H_3 with H_4 H_5,
--   use (((singleton x): (set X))),
  todo
end


lemma exercise.caracterisation_surj  :
surjective f ↔ ∀ B : set Y, f '' ( (f ⁻¹' B) ) = B
:=
/- dEAduction
pretty_name = "Caractérisation de la surjectivité par image de l'image réciproque"
-/
begin
    todo
end

lemma exercise.caracterisation_inj1  :
injective f ↔ ∀ A : set X, f ⁻¹' ( f '' A ) = A
:=
/- dEAduction
pretty_name = "Caractérisation de l'injectivité par image réciproque de l'image"
-/
begin
    todo
end

lemma exercise.caracterisation_inj2  :
injective f ↔ ∀ A  : set X, ∀ A' : set X,  f '' (A∩A') = (f '' A) ∩ (f ''  A')
:=
/- dEAduction
pretty_name = "Caractérisation de l'injectivité par image d'une intersection"
-/
begin
    todo
end



end inj_surj
end course
