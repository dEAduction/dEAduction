

-- import data.set
import tactic

-- dEAduction imports
import structures2
import user_notations
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
PrettyName
    Transitivité de l'inclusion
AutoTest
    →, definition.inclusion, ∀, →,
    @P1 ∧,
    @P2 @P3 definition.inclusion,
    @P1 @P2 →,
    @P4 @P3 →,
    CQFD
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


lemma exercise.test_definition
(A B : set X)  (H1: A ⊆ B) :
A ⊆ B 
:=
/- dEAduction
AutoTest
    H1 definition.inclusion success=H1,
    definition.inclusion success=appliquée_au_but,
    CQFD
-/
begin
  todo
end

lemma exercise.test_theorem_target_1
(A A' : set X) (H1: (A ⊆ A' ∧ A' ⊆ A)): 
A = A' 
:=
/- dEAduction
AutoTest
    target theorem.double_inclusion success=but_a_été_remplacé,
    CQFD
-/
begin
  todo
end


lemma exercise.test_theorem_hypo
(A A' : set X) (H1: (A ⊆ A' ∧ A' ⊆ A)): 
A = A' 
:=
/- dEAduction
AutoTest
    H1 theorem.double_inclusion success=Théorème_appliqué,
    CQFD
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

