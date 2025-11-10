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
/- dEAduction
implicit_use = true
-/
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

lemma exercise.test_implicit_inclusion
(A B C : set X) :
(A ⊆ B ∧ B ⊆ C) → A ⊆ C
:=
/- dEAduction
pretty_name = "Transitivité de l'inclusion"
[[auto_test]]
button = "implies"
[[auto_test]]
selection = [ "@P1" ]
button = "and"
[[auto_test]]
button = "forall"
[[auto_test]]
selection = [ "@P3", "@P1" ]
button = "implies"
[[auto_test]]
selection = [ "@P4", "@P2" ]
button = "implies"
[[auto_test]]
button = "assumption"
-/
begin
    todo
end

example (x y:X) (H : x ≠ y) : y ≠ x :=  
begin
    apply ne.symm,
    assumption,
end
 
end generalites



---------------------------
--- TESTS PROOF BUTTONS ---
---------------------------
namespace tests_proof_buttons

-------------------
-- Proof methods --
-------------------

-- Case base reasoning --
lemma exercise.test_case_base_reasoning
(P: Prop):
P ∨ ¬ P :=
/- dEAduction
[[auto_test]]
button = "proof_methods"
user_input = [
    0,
    "P",
]
[[auto_test]]
button = "or"
user_input = [
    0,
]
[[auto_test]]
button = "assumption"
[[auto_test]]
button = "or"
user_input = [
    1,
]
[[auto_test]]
button = "assumption"
-/
begin
    todo
end

lemma exercise.test_case_base_reasoning_2
(P Q : Prop) (H1: P ∨ Q):
P ∨ Q :=
/- dEAduction
[[auto_test]]
selection = [ "H1" ]
button = "proof_methods"
user_input = [
    0,
]
[[auto_test]]
button = "or"
user_input = [
    0,
]
[[auto_test]]
button = "assumption"
[[auto_test]]
button = "or"
user_input = [
    1,
]
[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_contrapose
(P Q : Prop) (H1: ¬ Q → ¬ P):
P → Q :=
/- dEAduction
[[auto_test]]
button = "proof_methods"
user_input = [
    1,
]
[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_absurdum
(P: Prop) (H1: P):
P :=
/- dEAduction
[[auto_test]]
button = "proof_methods"
user_input = [
    2,
]
[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_sorry
(P: Prop):
P :=
/- dEAduction
[[auto_test]]
button = "proof_methods"
user_input = [
    3,
]
error_msg = "Cette méthode est utile seulement lorsqu'il y a plusieurs buts"
error_type = 1
-/
begin
  todo
end

-----------------
-- Now objects --
-----------------

lemma exercise.test_introduce_new_object
(x: X):
∃ y: X, y=x
:=
/- dEAduction
[[auto_test]]
button = "new_object"
user_input = [
    0,
    "z",
    [
        "x",
    ],
]
[[auto_test]]
button = "exists"
user_input = [
    [
        "z",
    ],
]
-/
begin
  todo
end

-- Don't know how to test this one!!
lemma exercise.test_introduce_new_subgoal
(P Q R: Prop) (H1: Q) :
(P ∨ Q) ∨ R
:=
/- dEAduction
[[auto_test]]
button = "new_object"
user_input = [
    1,
    [
        "P ∨ Q",
    ],
]
[[auto_test]]
button = "or"
user_input = [
    1,
]
[[auto_test]]
button = "assumption"
[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_introduce_new_function
(P: X × Y → Prop) (H: ∀ x:X, ∃ y:Y, P(x,y)):
∃ g: (X → Y), ∀ x:X, P(x,g(x)) :=
/- dEAduction
[[auto_test]]
selection = [ "H" ]
button = "new_object"
user_input = [
    2,
]
[[auto_test]]
selection = [ "@O4" ]
button = "exists"
[[auto_test]]
button = "assumption"
-/
begin
  todo
end
end tests_proof_buttons
end theorie_des_ensembles
end course
