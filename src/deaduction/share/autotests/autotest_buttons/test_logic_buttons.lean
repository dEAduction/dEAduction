/-
This is a d∃∀duction file providing exercises about limits and continuity.-/

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
title = "Tests logic buttons"
author = "Frédéric Le Roux"
institution = "Université de France"-/


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
pretty_name = "Théorie des ensembles"-/

namespace generalites
/- dEAduction
pretty_name = "Généralités"-/

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
pretty_name = "Egalité de deux ensembles"-/
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
--     todo
-- end

-- set_option pp.all true
lemma definition.ensemble_extension {X: Type}  {P : X → Prop} {x:X} :
 x ∈ {x | P x} ↔ P x
:=
/- dEAduction
pretty_name = "Ensemble en extension"-/
begin
    refl
end


lemma theorem.double_inclusion (A A' : set X) :
(A ⊆ A' ∧ A' ⊆ A) → A = A' :=
/- dEAduction
pretty_name = "Double inclusion"-/
begin
    exact set.subset.antisymm_iff.mpr
end

lemma exercise.inclusion_transitive
(A B C : set X) :
(A ⊆ B ∧ B ⊆ C) → A ⊆ C
:=
/- dEAduction
pretty_name = "Transitivité de l'inclusion"-/
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
[[auto_test]]
button = "and"
user_input = [
    0,
]

[[auto_test]]
button = "assumption"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_construct_and_right
(P Q : Prop) (H1: P) (H2 : Q) :
P ∧ Q :=
/- dEAduction
[[auto_test]]
button = "and"
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

lemma exercise.test_apply_and
(P Q : Prop) (H1: P ∧ Q):
P :=
/- dEAduction
[[auto_test]]
selection = [
    "H1",
]
button = "and"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_construct_and_hyp
(P Q : Prop)  (H1: P) (H2 : Q):
P ∧ Q :=
/- dEAduction
[[auto_test]]
selection = [
    "@P1",
    "@P2",
]
button = "prove_and"

[[auto_test]]
button = "assumption"
-/
begin
  todo,
end
end tests_and

----------
--- OR ---
----------
namespace test_or

lemma exercise.test_construct_or_right
(P Q : Prop) (H1: P) : P ∨ Q :=
/- dEAduction
[[auto_test]]
button = "or"
user_input = [
    0,
]

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_construct_or_left
(P Q : Prop) (H1: Q) : P ∨ Q :=
/- dEAduction
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


lemma exercise.test_apply_or_left
(P Q : Prop) (H1: P ∨ Q):
P ∨ Q :=
/- dEAduction
[[auto_test]]
selection = [
    "H1",
]
button = "or"
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

lemma exercise.test_apply_or_right
(P Q : Prop) (H1: P ∨ Q) : P ∨ Q :=
/- dEAduction
[[auto_test]]
selection = [
    "H1",
]
button = "or"
user_input = [
    1,
]

[[auto_test]]
button = "or"
user_input = [
    1,
]

[[auto_test]]
button = "assumption"

[[auto_test]]
button = "or"
user_input = [
    0,
]

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_construct_or_on_hyp_left
(P Q : Prop) (H1: P):
P ∨ Q :=
/- dEAduction
[[auto_test]]
selection = [
    "H1",
]
button = "prove_or"
user_input = [
    0,
    [
        "Q",
    ],
]

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_construct_or_on_hyp_right
(P Q : Prop) (H1: Q):
P ∨ Q :=
/- dEAduction
[[auto_test]]
selection = [
    "H1",
]
button = "prove_or"
user_input = [
    1,
    [
        "P",
    ],
]

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_use_or_as_impliesI
(P Q : Prop) (H1: not P) (H2: P ∨ Q):
Q :=
/- dEAduction
[[auto_test]]
selection = [
    "@P1",
    "@P2",
]
button = "use_or"
success_msg = "Propriété H3 ajoutée au contexte"

[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
-/
begin
  todo
end

lemma exercise.test_use_or_as_impliesII
(P Q : Prop) (H1: not Q) (H2: P ∨ Q):
P :=
/- dEAduction
[[auto_test]]
selection = [
    "@P1",
    "@P2",
]
button = "use_or"
success_msg = "Propriété H3 ajoutée au contexte"

[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
-/
begin
  todo
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
[[auto_test]]
selection = [
    "H1",
]
button = "not"

[[auto_test]]
selection = [
    "H1",
]
button = "not"

[[auto_test]]
selection = [
    "H1",
]
button = "not"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_action_negate_target
(X: Type) (P Q : X × X → Prop)
(H1: ∀ x:X, ∃ y:X, P(x,y) ∨ Q(x,y) ):
¬ (∃ x:X, ∀ y:X, ¬ P(x,y) ∧ ¬ Q(x,y))
 :=
/- dEAduction
auto_test = [
    { button = "not" },
    { button = "not" },
    { button = "not" },
    { button = "not" },
    { button = "not" },
    { button = "assumption" },
]
-/
begin
  -- push_neg_once,
  -- push_neg_once,
  -- push_neg_once,
  -- push_neg_once,
  -- push_neg_once,
  -- exact H1,
  todo
end

end test_not

-----------------
--- IMPLICATE ---
-----------------
namespace test_implicate

lemma exercise.test_construct_implies
(P Q : Prop) (H1: Q) :
P → Q :=
/- dEAduction
auto_test = [
    { button = "implies" },
    { button = "assumption" },
]
-/
begin
  todo
end

lemma exercise.test_apply_implies
(P Q : Prop) (H1: P) (H2: P → Q) :
Q :=
/- dEAduction
[[auto_test]]
selection = [
    "H2",
]
button = "implies"
target_selected = true

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_apply_implies_to_hyp
(P Q : Prop) (H1: P) (H2: P → Q) :
Q :=
/- dEAduction
[[auto_test]]
selection = [
    "H1",
    "H2",
]
button = "implies"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_apply_implies_to_hyp3
(P Q : Prop) 
(H1: (P → Q) ↔ (¬ P ∨ Q))
(H2: P → Q) :
(¬ P ∨ Q) :=
/- dEAduction
[[auto_test]]
selection = [
    "H1",
    "H2",
]
button = "implies"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end
 

lemma exercise.test_apply_implies_to_hyp_2
(X: Type) (P Q: X × X → Prop) (x y: X)
(H1: P(x,y)) (H2: ∀ x y:X, P(x,y) → Q(x,y)) :
Q(x,y) :=
/- dEAduction
[[auto_test]]
selection = [
    "H1",
    "H2",
]
button = "implies"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end
 


lemma exercise.test_apply_iff_mp_to_hyp
(P Q : Prop) (H1: P) (H2: P ↔ Q) :
Q :=
/- dEAduction
[[auto_test]]
selection = [
    "H1",
    "H2",
]
button = "implies"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_apply_iff_mpr_to_hyp
(P Q : Prop) (H1: P) (H2: Q ↔ P) :
Q :=
/- dEAduction
[[auto_test]]
selection = [
    "H2",
    "H1",
]
button = "implies"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_apply_iff_mp_to_hyp_2
(X: Type) (P Q: X × X → Prop) (x y: X)
(H1: P(x,y)) (H2: ∀ x y:X, P(x,y) ↔ Q(x,y)) :
Q(x,y) :=
/- dEAduction
[[auto_test]]
selection = [
    "H2",
    "H1",
]
button = "implies"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_apply_iff_mpr_to_hyp_2
(X: Type) (P Q: X × X → Prop) (x y: X)
(H1: P(x,y)) (H2: ∀ x y:X, Q(x,y) ↔ P(x,y)) :
Q(x,y) :=
/- dEAduction
[[auto_test]]
selection = [
    "H1",
    "H2",
]
button = "implies"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_prove_premise
(P Q : Prop) (H2: Q → P) :
Q ∧ P :=
/- dEAduction
[[auto_test]]
selection = [
    "@P1",
]
button = "use_implies"
user_input = [
    0,
]
success_msg = "Le nouveau but sera ajouté au contexte quand il aura été démontré"

[[auto_test]]
button = "proof_methods"
user_input = [
    3,
]
success_msg = "But en cours atteint"

[[auto_test]]
selection = [
    "@P2",
    "@P1",
]
button = "use_implies"
success_msg = "Propriété H3 ajoutée au contexte"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_prove_premise_iff
(P Q : Prop) (H2: Q ↔ P) :
Q ∧ P :=
/- dEAduction
[[auto_test]]
selection = [
    "@P1",
]
button = "use_implies"
user_input = [
    1,
]
success_msg = "Le nouveau but sera ajouté au contexte quand il aura été démontré"

[[auto_test]]
button = "proof_methods"
user_input = [
    3,
]
success_msg = "But en cours atteint"

[[auto_test]]
selection = [
    "@P2",
    "@P1",
]
button = "use_implies"
success_msg = "Propriété H3 ajoutée au contexte"

[[auto_test]]
button = "assumption"
-/
begin
  todo
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
[[auto_test]]
button = "iff"
user_input = [
    0,
]

[[auto_test]]
button = "assumption"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_construct_iff_right
(P Q : Prop) (H1: P → Q) (H2: Q → P):
P ↔ Q
:=
/- dEAduction
[[auto_test]]
button = "iff"
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

lemma exercise.test_construct_iff_with_and
(P Q : Prop) (H1: P → Q) (H2: Q → P):
P ↔ Q
:=
/- dEAduction
[[auto_test]]
button = "and"
user_input = [
    0,
]

[[auto_test]]
button = "assumption"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_destruct_iff
(P Q : Prop)  (H1: P ↔ Q):
(P → Q) ∧ (Q → P)
:=
/- dEAduction
auto_test = [
    { button = "iff" },
    { button = "assumption" },
]
-/
begin
  todo,
end

-- lemma exercise.test_destruct_iff_on_hyp
-- (P Q : Prop) (H1: P ↔ Q):
-- (P → Q) ∧ (Q → P)
-- :=
-- /- dEAduction
-- AutoTest
--     H1 ↔, CQFD
-- -/
-- begin
--   cases H1 with H1a H1b, split,
--   assumption, assumption,
-- end

lemma exercise.test_construct_iff_on_hyp
(P Q : Prop) (H1: P → Q) (H2: Q → P):
P ↔ Q 
:=
/- dEAduction
[[auto_test]]
selection = [
    "H1",
    "H2",
]
button = "iff"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end


lemma exercise.test_iff_as_implies_target
(X: Type) (P Q : X → Prop)
(H: ∀ x, (P x ↔ Q x))  (x:X) (H': P x) :
Q x
:=
/- dEAduction
[[auto_test]]
selection = [
    "H",
]
button = "iff"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end


lemma exercise.test_iff_as_implies_hyp
(X: Type) (P Q : X → Prop)
(H: ∀ x, (P x ↔ Q x))  (x:X) (H': P x) :
Q x
:=
/- dEAduction
[[auto_test]]
selection = [
    "H",
    "H'",
]
button = "iff"

[[auto_test]]
button = "assumption"
-/
begin
  todo
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
[[auto_test]]
button = "forall"

[[auto_test]]
selection = [
    "@O3",
    "@P1",
]
button = "forall"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_apply_forall_to_hyp
(X: Type) (P Q: X × X → Prop) (x y: X)
(H1: P(x,y)) (H2: ∀ x y:X, P(x,y) → Q(x,y)) :
Q(x,y) :=
/- dEAduction
[[auto_test]]
selection = [
    "@O4",
    "@O5",
    "H1",
    "H2",
]
button = "forall"

[[auto_test]]
button = "assumption"
-/
begin
  todo
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
[[auto_test]]
selection = [
    "@O3",
]
button = "prove_exists"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_construct_exists_2
(X: Type) (P: X → Prop) (z: X)
(H1: P(z)) :
∃ x:X, P(x) :=
/- dEAduction
[[auto_test]]
button = "exists"
user_input = [
    [
        "z",
    ],
]

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_construct_exists_3
(X: Type) (P: X → Prop) (z z': X)
(H1: P(z))  (Def1: z=z'):
∃ x:X, P(x) :=
/- dEAduction
[[auto_test]]
selection = [
    "@P2",
]
button = "prove_exists"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end


lemma exercise.test_apply_exists_and_construct_exists_on_hyp
(X: Type) (P Q: X → Prop)
(H1: ∃ x:X, P(x))
(H2: ∀x:X, P(x) → Q(x)) :
(∃ x:X, Q(x))
:=
/- dEAduction
[[auto_test]]
selection = [
    "H1",
]
button = "use_exists"

[[auto_test]]
selection = [
    "@P2",
    "H2",
]
button = "implies"

[[auto_test]]
selection = [
    "@O4",
    "@P3",
]
button = "prove_exists"

[[auto_test]]
button = "assumption"
-/
begin
  todo
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
[[auto_test]]
selection = [
    "H'",
    "H",
]
button = "equal"

[[auto_test]]
selection = [
    "H'",
    "H''",
]
button = "equal"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_apply_equality_target1
(x y : X) (f: X → Y) (H: x = y):
f x= f y :=
/- dEAduction
[[auto_test]]
selection = [
    "H",
]
button = "equal"
user_input = [
    0,
]
-/
begin
  todo
end

lemma exercise.test_apply_equality_target2
(x y : X) (f: X → Y) (H: x = y):
f x= f y :=
/- dEAduction
[[auto_test]]
selection = [
    "H",
]
button = "equal"
user_input = [
    1,
]
-/
begin
  todo
end

lemma exercise.test_apply_equality_equality1
(x y z: X) (f: X → Y) (H: x = y) (H': y = z):
x = z :=
/- dEAduction
[[auto_test]]
selection = [
    "H'",
    "H",
]
button = "equal"
user_input = [
    0,
]

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_apply_equality_equality2
(x y z : X) (f: X → Y) (H: x = y) (H': y = z):
x = z :=
/- dEAduction
[[auto_test]]
selection = [
    "H'",
    "H",
]
button = "equal"
user_input = [
    1,
]

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_apply_equality_equality_and_direction1
(x y z : X) (f: X → Y) (H: x = y) (H': y = x) (H2: x = z):
x = z :=
/- dEAduction
[[auto_test]]
selection = [
    "H'",
    "H",
]
button = "equal"
user_input = [
    0,
    0,
]
[[auto_test]]
button = "assumption"-/
begin
  todo
end

lemma exercise.test_apply_equality_equality_and_direction2
(x y z : X) (f: X → Y) (H: x = y) (H': y = x):
x = z :=
/- dEAduction
[[auto_test]]
selection = [
    "H'",
    "H",
]
button = "equal"
user_input = [
    0,
    1,
]

[[auto_test]]
button = "STOP"-/
begin
  todo
end
lemma exercise.test_apply_equality_equality_and_direction3
(x y z : X) (f: X → Y) (H: x = y) (H': y = x):
x = z :=
/- dEAduction
[[auto_test]]
selection = [
    "H'",
    "H",
]
button = "equal"
user_input = [
    1,
    0,
]

[[auto_test]]
button = "STOP"-/
begin
  todo
end
lemma exercise.test_apply_equality_equality_and_direction4
(x y z : X) (f: X → Y) (H: x = y) (H': y = x):
x = z :=
/- dEAduction
[[auto_test]]
selection = [
    "H'",
    "H",
]
button = "equal"
user_input = [
    1,
    1,
]

[[auto_test]]
button = "STOP"-/
begin
  todo
end

end test_equality

namespace test_map
--------------
--- map ---
--------------

lemma exercise.test_map_equality1
(x y : X) (f: X → Y) (H: x = y):
f(x) = f(y) :=
/- dEAduction
[[auto_test]]
selection = [
    "H",
    "f",
]
button = "map"

[[auto_test]]
button = "assumption"
-/
begin
  todo
end

lemma exercise.test_map_equality2
(x y z w : X) (f: X → Y) (H: x = y) (H': x = z) (H'': z = w):
f(x) = f(y) :=
/- dEAduction
[[auto_test]]
selection = [
    "H",
    "f",
    "H'",
    "H''",
]
button = "map"
[[auto_test]]
button = "assumption"-/
begin
  todo
end

lemma exercise.test_map_element_1
(x x' : X) (f: X → Y) :
∃ y:Y, y= f(x') :=
/- dEAduction
[[auto_test]]
selection = [
    "x'",
    "f",
]
button = "map"
[[auto_test]]
selection = [
    "y",
]
button = "prove_exists"-/
begin
  todo
end

lemma exercise.test_map_element_2
(x x' : X) (f: X → Y) :
∃ y:Y, y= f(x') :=
/- dEAduction
[[auto_test]]
selection = [
    "f",
]
button = "map"
user_input = [
    [
        "x'",
    ],
]
[[auto_test]]
selection = [
    "y",
]
button = "prove_exists"-/
begin
  todo
end


lemma exercise.test_apply_error_1
(A B: set X) (x y : X) (f: X → Y) (H: x = y) (H': x ∈ A) (H'': A =B):
y ∈ B :=
/- dEAduction
[[auto_test]]
selection = [
    "H'",
]
button = "map"
error_type = 1
error_msg = "Sélectionner une application"
-/
begin
  todo
end



end test_map
end tests_logic_buttons
end theorie_des_ensembles
end course