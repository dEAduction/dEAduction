/-
This is a d∃∀duction file providing easy and progressive exercises for basic set theory.
It may be used as a tutorial for d∃∀duction.
French version.
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

-------------------------
-- dEAduction METADATA --
-------------------------

/- dEAduction
title = "Tutoriel"
author = "Camille Lichère"
institution = "Université de France"
description = """
Ce fichier contient quelques exercices faciles et progressifs de théorie élémentaire
des ensembles. Il peut être utilisé comme tutoriel pour d∃∀duction ; en particulier,
les boutons logiques sont introduits progressivement.
"""
default_available_logic = "ALL -not -exists -map -equal -iff"
available_proof = "ALL -new_object"
available_compute = "NONE"
[settings]
logic.usr_jokers_available = false
logic.use_color_for_applied_properties = false
functionality.allow_induction = false
functionality.calculator_available = false
others.Lean_request_method = "normal"
-/

/- Notes for exercise makers.

List of buttons
AvailableLogic
    forall exists implies and or
    map equal iff not
AvailableProof
    proof_methods new_object
AvailableCompute
    sum transitivity commute associativity
    triangular_inequality simplify
-/

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
variables {X Y Z: Type}

open set

------------------------
-- COURSE DEFINITIONS --
------------------------
namespace definitions
/- dEAduction
pretty_name = "Définitions"
-/

namespace inclusions_egalites
/- dEAduction
pretty_name = "Inclusions, égalités"
-/

lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
/- dEAduction
implicit_use = true
-/
begin
    exact iff.rfl,
end

-- lemma definition.egalite_deux_ensembles {A A' : set X} :
-- (A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
-- /- dEAduction
-- PrettyName
--     Egalité de deux ensembles
-- ImplicitUse
--     False
-- -/
-- begin
--      exact set.ext_iff,
-- end


lemma definition.double_inclusion (A A' : set X) :
A = A' ↔ (A ⊆ A' ∧ A' ⊆ A):=
/- dEAduction
pretty_name = "Double inclusion"
implicit_use = true
-/
begin
    exact subset.antisymm_iff,
end
end inclusions_egalites

namespace unions_intersections
/- dEAduction
pretty_name = "Unions, intersections"
-/
lemma definition.intersection_deux_ensembles {A B : set X} {x : X} :
x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B) :=
/- dEAduction
pretty_name = "Intersection de deux ensembles"
implicit_use = true
-/
begin
    exact iff.rfl,
end

lemma definition.union_deux_ensembles  {A : set X} {B : set X} {x : X} :
x ∈ A ∪ B ↔ ( x ∈ A ∨ x ∈ B) :=
/- dEAduction
pretty_name = "Union de deux ensembles"
implicit_use = true
-/
begin
    exact iff.rfl,
end

end unions_intersections

end definitions
---------------
-- SECTION 1 --
---------------
-- variables exercices --
-- variables {A B C : set X}


---------------
-- EXERCICES --
---------------
namespace exercices

-- description = "Voici un premier exercice !"
lemma exercise.intersection_inclus_ensemble
(A B : set X) :
A ∩ B ⊆ A
:=
/- dEAduction
pretty_name = "Un ensemble contient son intersection avec un autre"
-/
begin
    todo,
end


lemma exercise.inclus_dans_les_deux_implique_dans_lintersection
(A B C : set X) :
(C ⊆ A) ∧ (C ⊆ B) → C ⊆ A ∩ B
:=
/- dEAduction
pretty_name = "Inclus dans les deux implique inclus dans l'intersection"
-/
begin
    todo,
end

lemma exercise.inclusion_transitive
(A B C : set X) :
(A ⊆ B ∧ B ⊆ C) → A ⊆ C
:=
/- dEAduction
pretty_name = "Transitivité de l'inclusion"
-/
begin
    todo,
end

lemma exercise.ensemble_inclus_union
(A B : set X) :
B ⊆ A ∪ B
:=
/- dEAduction
pretty_name = "Ensemble inclus dans l'union"
description = 'Le bouton ∨ ("ou"), permet notamment de montrer un but de la forme "P ou Q" en choisissant si on veut montrer "P" ou "Q".'
-/
begin
    todo,
end

lemma exercise.ensemble_inclus_intersection
(A B : set X) :
A ⊆ A ∩ B  → (A ∪ B) = B
:=
/- dEAduction
pretty_name = "Ensemble inclus dans l'intersection"
description = """
Utilisez la double inclusion pour montrer une égalité entre ensembles.
Le bouton ∨ ("ou") permet également, appliqué à une hypothèse du type "P ou Q" de faire une disjonction de cas selon si on a "P" ou "Q".
"""
-/
begin
    todo,
end

lemma exercise.inter_distributive_union
(A B C : set X):
A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)
:=
/- dEAduction
pretty_name = "Union avec une intersection"
description = "Utilisez l'aperçu de preuve pour ne pas vous perdre dans les différents cas."
-/
begin
    todo,
end

lemma exercise.exercice_bilan
(A B : set X) :
A ⊆ B ↔ A ∩ B = A
:=
/- dEAduction
pretty_name = "Exercice bilan"
description = """
Dans cet exercice, deux nouveaux boutons apparaissent.
On peut utiliser une égalité pour remplacer l'un des termes par l'autre.
"""
available_logic = "ALL -not -exists -map"
-/
begin
    todo
end
end exercices

end course