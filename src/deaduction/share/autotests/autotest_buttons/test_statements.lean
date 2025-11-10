/-
This is a d∃∀duction file providing exercises about limits and continuity.
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
import set_definitions
import real_definitions

-- Use classical logic
local attribute [instance] classical.prop_decidable


/- dEAduction
title = "Théorie des ensembles"
author = "Frédéric Le Roux"
institution = "Université de France"
-/


local attribute [instance] classical.prop_decidable


---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
-- parameters {X Y Z: Type}

notation [parsing_only] P ` and ` Q := P ∧ Q
notation [parsing_only]  P ` or ` Q := P ∨ Q
notation [parsing_only]  ` not ` P := ¬ P
notation [parsing_only]  P ` implies ` Q := P → Q
notation [parsing_only]  P ` iff ` Q := P ↔ Q

notation [parsing_only]  x ` in ` A := x ∈ A
notation [parsing_only]  A ` cap ` B := A ∩ B
notation [parsing_only]  A ` cup ` B := A ∪ B
notation [parsing_only]  A ` subset ` B := A ⊆ B
notation [parsing_only]  `emptyset` := ∅
notation [parsing_only]  `vide` := ∅

notation [parsing_only] P ` et ` Q := P ∧ Q
notation [parsing_only]  P ` ou ` Q := P ∨ Q
notation [parsing_only]  ` non ` P := ¬ P
notation [parsing_only]  P ` implique ` Q := P → Q
notation [parsing_only]  P ` ssi ` Q := P ↔ Q

notation [parsing_only]  x ` dans ` A := x ∈ A
notation [parsing_only]  x ` appartient ` A := x ∈ A
notation [parsing_only]  A ` inter ` B := A ∩ B
notation [parsing_only]  A ` intersection ` B := A ∩ B
notation [parsing_only]  A ` union ` B := A ∪ B
notation [parsing_only]  A ` inclus ` B := A ⊆ B


notation f `⟮` A `⟯` := f '' A
notation f `⁻¹⟮` A `⟯` := f  ⁻¹' A
notation [parsing_only] f `inverse` A := f  ⁻¹' A
notation g `∘` f := set.composition g f
notation `∃!` P := exists_unique P

open set
parameters X Y Z: Type
------------------
-- COURSE TITLE --
------------------
namespace theorie_des_ensembles
/- dEAduction
pretty_name = "Théorie des ensembles"
-/

namespace generalites
/- dEAduction
pretty_name = "Généralités"
-/

------------------------
-- COURSE DEFINITIONS --
------------------------
lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
begin
    exact iff.rfl
end

lemma definition.egalite_deux_ensembles {A A' : set X} :
(A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
pretty_name = "Egalité de deux ensembles"
-/
begin
     exact set.ext_iff
end

lemma definition.ensemble_vide
(A: set X) :
(A = ∅) ↔ ∀ x : X, x ∉ A
:=
begin
    exact eq_empty_iff_forall_not_mem,
end

-- lemma definition.ensemble_non_vide
-- (A: set X) :
-- (A ≠ ∅) ↔ ∃ x : X, x ∈ A
-- :=
-- begin
--     sorry
-- end

-- set_option pp.all true
lemma definition.ensemble_extension {X: Type}  {P : X → Prop} {x:X} :
 x ∈ {x | P x} ↔ P x
:=
/- dEAduction
pretty_name = "Ensemble en extension"
-/
begin
    refl
end


lemma theorem.double_inclusion (A A' : set X) :
(A ⊆ A' ∧ A' ⊆ A) → A = A' :=
/- dEAduction
pretty_name = "Double inclusion"
-/
begin
    exact set.subset.antisymm_iff.mpr
end

variables (A: set X) (f: X → Y) (B: set Y)
lemma definition.image_directe (y: Y) : y ∈ f '' A ↔ ∃ x : X, x ∈ A ∧  f x = y :=
begin
    todo
end

lemma theorem.image_directe (x: X) : x ∈ A → f(x) ∈ f '' A :=
begin
    todo
end

lemma definition.image_reciproque (x: X) : x ∈ f ⁻¹' B ↔ f x ∈ B :=
begin
    todo
end
lemma exercise.inclusion_transitive
(A B C : set X) :
(A ⊆ B ∧ B ⊆ C) → A ⊆ C
:=
/- dEAduction
pretty_name = "Transitivité de l'inclusion"
-/
begin
    intro H1,
    rw definition.inclusion,
    intros x H2,
    cases H1 with H3 H4,
    rw definition.inclusion at H3 H4,
    have H5 := H3 H2,
    have H6 := H4 H5,
    assumption,
end

example (x y:X) (H : x ≠ y) : y ≠ x :=  
begin
    apply ne.symm, assumption,
end
 
end generalites


namespace tests_statements


lemma exercise.test_definition_context
(A B : set X)  (H1: A ⊆ B) :
A ⊆ B 
:=
/- dEAduction
[[auto_test]]
selection = [ "H1" ]
statement = "definition.inclusion"
success_msg = "H1"
[[auto_test]]
statement = "definition.inclusion"
target_selected = true
success_msg = "appliquée au but"
[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_definition_calculator
(A B : set X)  (H1: A ⊆ B) :
A ⊆ B 
:=
/- dEAduction
[[auto_test]]
statement = "definition.inclusion"
user_input = [
    [
        "_",
        "A",
        "B",
    ],
]
[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_theorem_target_1
(A A' : set X) (H1: (A ⊆ A' ∧ A' ⊆ A)): 
A = A' 
:=
/- dEAduction
[[auto_test]]
statement = "theorem.double_inclusion"
target_selected = true
success_msg = "but a été remplacé"
[[auto_test]]
button = "assumption"
-/
begin
  todo
end


lemma exercise.test_theorem_hypo
(A A' : set X) (H1: (A ⊆ A' ∧ A' ⊆ A)): 
A = A' 
:=
/- dEAduction
[[auto_test]]
selection = [ "H1" ]
statement = "theorem.double_inclusion"
success_msg = "Théorème appliqué"
[[auto_test]]
button = "assumption"
-/
begin
  todo
end

-- Here we test that deaduction is not too powerfull, i.e. theorem.image_directe should NOT solve the goal
-- (as the Lean `apply` tactic does, by unfolding the semi-reducible definition of inverse image)
-- deaduction does not send the code `apply`, but `apply_with ... {md:=reducible}`)
-- PB = il faut maintenant sélectionner le but
-- lemma exercise.test_theorem_target_2
-- (x: X) (A: set X) (f: X → Y) (H: x ∈ A): 
-- x ∈ f ⁻¹' (f '' A)
-- :=
-- /- dEAduction
-- AutoTest
--     theorem.image_directe success=Théorème_ajouté_au_contexte,
-- -/
-- begin
--   todo
-- end
 
-- lemma exercise.test_theorem_target_3
-- (x: X) (A: set X) (f: X → Y) (H: x ∈ A): 
-- x ∈ f ⁻¹' (f '' A)
-- :=
-- /- dEAduction
-- AutoTest
--     definition.image_reciproque,
--     theorem.image_directe success=Théorème_appliqué,
--     CQFD
-- -/
-- begin
--   todo
-- end


end tests_statements
end theorie_des_ensembles
end course
