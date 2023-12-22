-- import data.set
import tactic

-- dEAduction imports
import structures2
import user_notations
import utils
import push_neg_once


-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement (since it will be called with 'rw' or 'symp_rw')

---------------------
-- Course metadata --
---------------------
-- logic names ['and', 'or', 'negate', 'implicate', 'iff', 'forall', 'exists']
-- proofs names ['use_proof_methods', 'new_object', 'apply', 'assumption']
-- magic names ['compute']
-- proof methods names ['cbr', 'contrapose', 'absurdum', 'sorry']



/- dEAduction
Title
    Théorie des ensembles
Author
    Frédéric Le Roux
Institution
    Université de France
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
PrettyName
    Théorie des ensembles
-/

namespace generalites
/- dEAduction
PrettyName
    Généralités
-/

------------------------
-- COURSE DEFINITIONS --
------------------------
lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
/- dEAduction
ImplicitUse
    True
-/
begin
    exact iff.rfl
end

lemma definition.egalite_deux_ensembles {A A' : set X} :
(A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
PrettyName
    Egalité de deux ensembles
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
PrettyName
    Ensemble en extension
-/
begin
    refl
end


lemma theorem.double_inclusion (A A' : set X) :
(A ⊆ A' ∧ A' ⊆ A) → A = A' :=
/- dEAduction
PrettyName
    Double inclusion
-/
begin
    exact set.subset.antisymm_iff.mpr  
end

lemma exercise.test_implicit_inclusion
(A B C : set X) :
(A ⊆ B ∧ B ⊆ C) → A ⊆ C
:=
/- dEAduction
PrettyName
    Transitivité de l'inclusion
AutoTest
    →, @P1 ∧, ∀, →,
    @P3 @P1 →, @P4 @P2 →,
    CQFD 
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
AutoTest
    proof_methods 0 P,
    ∨ 0, CQFD,
    ∨ 1, CQFD
-/
begin
    todo
end

lemma exercise.test_case_base_reasoning_2
(P Q : Prop) (H1: P ∨ Q):
P ∨ Q :=
/- dEAduction
AutoTest
    H1 proof_methods 0,
    ∨ 0,
    CQFD,
    ∨ 1,
    CQFD
-/
begin
  todo
end

lemma exercise.test_contrapose
(P Q : Prop) (H1: ¬ Q → ¬ P):
P → Q :=
/- dEAduction
AutoTest
    proof_methods 1,
    CQFD
-/
begin
  todo
end

lemma exercise.test_absurdum
(P: Prop) (H1: P):
P :=
/- dEAduction
AutoTest
    proof_methods 2,
    CQFD
-/
begin
  todo
end

lemma exercise.test_sorry
(P: Prop):
P :=
/- dEAduction
AutoTest
    proof_methods 3
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
AutoTest
    new_object 0 z [ x ],
    ∃ [ z ]
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
AutoTest
    new_object 1 [ P__∨__Q ],
    ∨ 1, CQFD, CQFD
-/
begin
  todo
end

lemma exercise.test_introduce_new_function
(P: X × Y → Prop) (H: ∀ x:X, ∃ y:Y, P(x,y)):
∃ g: (X → Y), ∀ x:X, P(x,g(x)) :=
/- dEAduction
AutoTest
    H new_object [ 2 ],
    @O4 ∃,
    CQFD
-/
begin
  todo
end
end tests_proof_buttons
end theorie_des_ensembles
end course

