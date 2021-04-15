-- import data.set
import tactic

-- dEAduction imports
import structures2
import notations_definitions
import utils

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

lemma exercise.inclusion_transitive
(A B C : set X) :
(A ⊆ B ∧ B ⊆ C) → A ⊆ C
:=
/- dEAduction
PrettyName
    Transitivité de l'inclusion
-/
begin
  sorry
end
 
end generalites


---------------------------
--- TESTS MAGIC BUTTONS ---
---------------------------
namespace tests_magic_buttons

lemma exercise.test_assumption
(P: Prop) (H: P):
P:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_contradiction
(P Q: Prop) (H: P) (H': ¬P): Q
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_rfl
(P: Prop):
P = P
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_eq_symm
(x y: X) (H: x=y):
y=x
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_cc
(x y z: X) (f: X → Y) (H: x=y) (H': y=z):
f(x) = f(z)
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_inequality
(x y: ℝ) (H: x < y):
y > x
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_or
(P Q: Prop) (H: P):
P or Q
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_or_2
(P Q: Prop) (H: Q):
P or Q
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_split_and
(P Q R: Prop) (H: P ∧ Q) (H': R):
P ∧ R
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_norm_num
:
1 + 1 = 2
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_empty_set
(P: Prop)
(x:X)
(H: x ∈ (∅:set X) ):
P
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end










end tests_magic_buttons


end theorie_des_ensembles
end course
