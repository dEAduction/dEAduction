import tactic
import structures2
import utils

/- dEAduction
Title
    Naive set theory
Institution
    World University
AvailableMagic
    ALL -compute
-/

local attribute [instance] classical.prop_decidable
-- NB: this is a technical line (allow the use of classical logic).

section course
parameters {X : Type}

open set -- Open the `set`spacename to allow easy access to the instructions.
------------------
-- COURSE TITLE --
------------------
namespace set_theory

namespace definitions

------------------------
-- COURSE DEFINITIONS --
------------------------
lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
begin
    exact iff.rfl
end

end definitions
namespace exercises

lemma exercise.inclusion_transitive
(A B C : set X) :
(A ⊆ B ∧ B ⊆ C) → A ⊆ C
:=
/- dEAduction
PrettyName
    Transitivity of inclusion
Description
    The inclusion is a transitive relation.
-/
begin
    sorry
end

end exercises

end set_theory
end course