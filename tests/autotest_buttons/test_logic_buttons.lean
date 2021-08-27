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

---------------------------
--- TESTS LOGIC BUTTONS ---
---------------------------
namespace tests_logic_buttons

-----------
--- AND ---
-----------
namespace tests_and
lemma exercise.test_construct_and_left
(P Q : Prop) (H1: P) (H2 : Q) : P ∧ Q :=
/- dEAduction
AutoTest
    ∧ 0, CQFD, CQFD
-/
begin
  sorry
end

lemma exercise.test_construct_and_right
(P Q : Prop) (H1: P) (H2 : Q) :
P ∧ Q :=
/- dEAduction
AutoTest
    ∧ 1, CQFD, CQFD
-/
begin
  sorry
end

lemma exercise.test_apply_and
(P Q : Prop) (H1: P ∧ Q):
P :=
/- dEAduction
AutoTest
    H1 ∧,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_construct_and_hyp
(P Q : Prop)  (H1: P) (H2 : Q):
P ∧ Q :=
/- dEAduction
AutoTest
    @P1 @P2 ∧, CQFD
-/
begin
  sorry,
end
end tests_and

----------
--- OR ---
----------
namespace test_or

lemma exercise.test_construct_or_right
(P Q : Prop) (H1: P) : P ∨ Q :=
/- dEAduction
AutoTest
    ∨ 0,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_construct_or_left
(P Q : Prop) (H1: Q) : P ∨ Q :=
/- dEAduction
AutoTest
    ∨ 1,
    CQFD
-/
begin
  sorry
end


lemma exercise.test_apply_or_left
(P Q : Prop) (H1: P ∨ Q):
P ∨ Q :=
/- dEAduction
AutoTest
    H1 ∨ 0,
    ∨ 0,
    CQFD,
    ∨ 1,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_apply_or_right
(P Q : Prop) (H1: P ∨ Q) : P ∨ Q :=
/- dEAduction
AutoTest
    H1 ∨ 1,
    ∨ 1,
    CQFD,
    ∨ 0,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_construct_or_on_hyp_left
(P Q : Prop) (H1: P):
P ∨ Q :=
/- dEAduction
AutoTest
    H1 ∨ Q 0,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_construct_or_on_hyp_right
(P Q : Prop) (H1: Q):
P ∨ Q :=
/- dEAduction
AutoTest
    H1 ∨ P 1,
    CQFD
-/
begin
  sorry
end

end test_or

-----------
--- NOT ---
-----------
namespace test_not

lemma exercise.test_action_negate_hyp
(X: Type) (P Q : X × X → Prop)
(H1: ¬ (∀ x:X, ∃ y:X, P(x,y) ∨ Q(x,y)) ):
∃ x:X, ∀ y:X, ¬ P(x,y) ∧ ¬ Q(x,y) :=
/- dEAduction
AutoTest
    H1 ¬, 
    CQFD
-/
begin
  sorry
end

lemma exercise.test_action_negate_target
(X: Type) (P Q : X × X → Prop)
(H1: ∀ x:X, ∃ y:X, P(x,y) ∨ Q(x,y) ):
¬ (∃ x:X, ∀ y:X, ¬ P(x,y) ∧ ¬ Q(x,y))
 :=
/- dEAduction
AutoTest
    ¬,
    CQFD
-/
begin
  sorry
end

end test_not

-----------------
--- IMPLICATE ---
-----------------
namespace test_implicate

lemma exercise.test_construct_implicate
(P Q : Prop) (H1: Q) :
P → Q :=
/- dEAduction
AutoTest
    →,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_apply_implicate
(P Q : Prop) (H1: P) (H2: P → Q) :
Q :=
/- dEAduction
AutoTest
    H2 →,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_apply_implicate_to_hyp
(P Q : Prop) (H1: P) (H2: P → Q) :
Q :=
/- dEAduction
AutoTest
    H1 H2 →,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_apply_implicate_to_hyp_2
(X: Type) (P Q: X × X → Prop) (x y: X)
(H1: P(x,y)) (H2: ∀ x y:X, P(x,y) → Q(x,y)) :
Q(x,y) :=
/- dEAduction
AutoTest
    H1 H2 →,
    CQFD
-/
begin
  sorry
end
end test_implicate

-----------
--- IFF ---
-----------
namespace test_iff

lemma exercise.test_construct_iff_left
(P Q : Prop) (H1: P → Q) (H2: Q → P):
P ↔ Q
:=
/- dEAduction
AutoTest
    ↔ 0, CQFD, CQFD
-/
begin
  sorry
end

lemma exercise.test_construct_iff_right
(P Q : Prop) (H1: P → Q) (H2: Q → P):
P ↔ Q
:=
/- dEAduction
AutoTest
    ↔ 1, CQFD, CQFD
-/
begin
  sorry
end

lemma exercise.test_destruct_iff
(P Q : Prop)  (H1: P ↔ Q):
(P → Q) ∧ (Q → P)
:=
/- dEAduction
AutoTest
    ↔, CQFD
-/
begin
  sorry,
end

lemma exercise.test_destruct_iff_on_hyp
(P Q : Prop) (H1: P ↔ Q):
(P → Q) ∧ (Q → P)
:=
/- dEAduction
AutoTest
    H1 ↔, CQFD
-/
begin
  sorry
end

lemma exercise.test_construct_iff_on_hyp
(P Q : Prop) (H1: P → Q) (H2: Q → P):
P ↔ Q 
:=
/- dEAduction
AutoTest
    H1 H2 ↔, CQFD
-/
begin
  sorry
end

end test_iff

--------------
--- FORALL ---
--------------
namespace test_forall

lemma exercise.test_construct_and_apply_forall
(X: Type) (P: X → Prop)
(H1: ∀ x:X, P(x)) :
∀ x:X, P(x) :=
/- dEAduction
AutoTest
    ∀,
    @O3 @P1 ∀,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_apply_forall_to_hyp
(X: Type) (P Q: X × X → Prop) (x y: X)
(H1: P(x,y)) (H2: ∀ x y:X, P(x,y) → Q(x,y)) :
Q(x,y) :=
/- dEAduction
AutoTest
    @O4 @O5 H1 H2 ∀,
    CQFD
-/
begin
  sorry
end
end test_forall


--------------
--- EXISTS ---
--------------
namespace test_exists

lemma exercise.test_construct_exists
(X: Type) (P: X → Prop) (z: X)
(H1: P(z)) :
∃ x:X, P(x) :=
/- dEAduction
AutoTest
    @O3 ∃,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_construct_exists_2
(X: Type) (P: X → Prop) (z: X)
(H1: P(z)) :
∃ x:X, P(x) :=
/- dEAduction
AutoTest
    ∃ z,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_apply_exists_and_construct_exists_on_hyp
(X: Type) (P Q: X → Prop)
(H1: ∃ x:X, P(x))
(H2: ∀x:X, P(x) → Q(x)) :
(∃ x:X, Q(x))
:=
/- dEAduction
AutoTest
    H1 ∃,
    @P2 H2 →,
    @O4 @P3 ∃,
    CQFD
-/
begin
  sorry
end  
end test_exists

namespace test_equality
----------------
--- equality ---
----------------

lemma exercise.test_apply_equality1
(A B: set X) (x y : X) (f: X → Y) (H: x = y) (H': x ∈ A) (H'': A =B):
y ∈ B :=
/- dEAduction
AutoTest
    H' H =,
    H' H'' =,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_apply_equality_target1
(x y : X) (f: X → Y) (H: x = y):
f x= f y :=
/- dEAduction
AutoTest
    H = 0
-/
begin
  sorry
end

lemma exercise.test_apply_equality_target2
(x y : X) (f: X → Y) (H: x = y):
f x= f y :=
/- dEAduction
AutoTest
    H = 1
-/
begin
  sorry
end

lemma exercise.test_apply_equality_equality1
(x y z: X) (f: X → Y) (H: x = y) (H': y = z):
x = z :=
/- dEAduction
AutoTest
    H' H = 0,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_apply_equality_equality2
(x y z : X) (f: X → Y) (H: x = y) (H': y = z):
x = z :=
/- dEAduction
AutoTest
    H' H = 1,
    CQFD
-/
begin
  sorry
end

lemma exercise.test_apply_equality_equality_and_direction
(x y z : X) (f: X → Y) (H: x = y) (H': y = x):
x = z :=
/- dEAduction
AutoTest
    H' H = 0 0,
    proof_methods 3
-/
begin
  sorry
end




end test_equality

/- The following exo does not work. Pb= 
∃ x ∈ A, P(x)
as a target is actually 
∃ x:X, ∃ H:x ∈ A, P(x)
whereas in deaduction's hypo it is
∃ x:X, x ∈ A ∧ P(x).
Deaduction display all this the same way but assumption fails!
-/
-- lemma exercise.test_apply_exists_2
-- (X: Type) (A: set X) (P Q: X → Prop)
-- (H1: ∃ x ∈ A, P(x))
-- (H2: ∀x∈A, P(x) → Q(x)) :
-- (∃ x ∈ A, Q(x))
--  :=
/- deaduc
AutoTest
    H1 ∃,
    @P1 H2 →,
    @P3 @P4 ∧,
    @O5 @P5 ∃,
    CQFD
-/
end tests_logic_buttons
end theorie_des_ensembles
end course
