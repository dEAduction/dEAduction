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
namespace test_magic_buttons

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

lemma definition.intersection_deux_ensembles {A B : set X} {x : X} :
x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B) :=
/- dEAduction
PrettyName
    Intersection de deux ensembles
ImplicitUse
    True
-/
begin
    exact iff.rfl
end

lemma definition.union_deux_ensembles  {A : set X} {B : set X} {x : X} :
x ∈ A ∪ B ↔ ( x ∈ A ∨ x ∈ B) :=
/- dEAduction
PrettyName
    Union de deux ensembles
ImplicitUse
    True
-/
begin
    exact iff.rfl
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

lemma exercise.test_assumption_cc2
(x y z: X) (B: set Y) (f: X → Y) (H: x=y) (H': y=z) (H'': f(z) ∈ B):
f(x) ∈ B
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

lemma exercise.test_assumption_or_left
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

lemma exercise.test_assumption_or_right
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

lemma exercise.test_assumption_or_rec1
(P Q R: Prop) (H: P):
((P or Q) or R)
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_or_rec2
(P Q R: Prop) (H: Q):
((P or Q) or R)
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_or_rec3
(P Q R: Prop) (H: R):
((P or Q) or R)
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

-- AND --

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

lemma exercise.test_assumption_rec_split_and
(P Q R: Prop) (H: P) (H': Q) (H'': R):
(P ∧ Q) ∧ R
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_split_context
(P Q R: Prop) (H: P ∧ R) (H': Q):
(P ∧ Q) ∧ R
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_implicit_or
(X: Type) (x : X) (A B C : set X)
(H: x ∈ B ) :
x ∈ A ∪ (B ∪ C)
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

lemma exercise.test_assumption_implicit_and
(X: Type) (x : X) (A B C : set X)
(H: x ∈ A ∩ B ) (H': x ∈ C ):
x ∈ A ∩ (B ∩ C)
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


lemma exercise.test_compute1
(x y z: ℝ)
(H0a: x ≠ 0)
(H0b: x ≥ 0) (H1: y > 0) (H2: z >0)
(H: x + y + z < 1):
x +  2*y + 3*z < 100
:=
/- dEAduction
AutoTest
    CQFD
-/
begin
  sorry
end

-- lemma exercise.compute2
-- (x y z: ℝ)
-- (H0: x > 0) (H1: y > 0) (H2: z >0)
-- (H: x + y + z < 1):
-- x +  2*y + 3*z < 1
-- :=
-- /- dEAduction
-- AutoTest
--     CQFD error=
-- -/
-- begin
--   sorry
-- end

-- lemma exercise.compute3
-- (x y z a b: ℝ)
-- (H0b: x ≠ 0)
-- (H0: x >= 0) (H1: y > 0) (H2: z >0)
-- (Ha: a=2*x) (Hb: b=5*y)
-- (H: x + y + z < 1):
-- x +  2*a + 3*b < 1
-- :=
-- /- dEAduction
-- AutoTest
--     CQFD error=
-- -/
-- begin
--   sorry
-- end





end tests_magic_buttons

end test_magic_buttons

end course
