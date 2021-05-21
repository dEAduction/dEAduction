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
-- proof methods names ['cbr', 'contrapose', 'absurdum', 'todo']



/- dEAduction
Title
    Exercices TER L1
Author
    Camille Lichère
Institution
    Université de France
AvailableProof
    ALL -new_object
AvailableMagic
    assumption
-/


local attribute [instance] classical.prop_decidable


---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
parameters {X Y Z: Type}

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
notation [parsing_only]  `vide` := ∅

notation f `⟮` A `⟯` := f '' A
notation f `⁻¹⟮` A `⟯` := f  ⁻¹' A
notation [parsing_only] f `inverse` A := f  ⁻¹' A
notation g `∘` f := set.composition g f
notation `∃!` P := exists_unique P

open set


------------------------
-- COURSE DEFINITIONS --
------------------------
namespace definitions
/- dEAduction
PrettyName
    Définitions
-/

namespace inclusions_egalites
/- dEAduction
PrettyName
    Inclusions, égalités
-/

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


lemma theorem.double_inclusion (A A' : set X) :
(A ⊆ A' ∧ A' ⊆ A) → A = A' :=
/- dEAduction
PrettyName
    Double inclusion
-/
begin
    exact set.subset.antisymm_iff.mpr
end
end inclusions_egalites

namespace unions_intersections
/- dEAduction
PrettyName
    Unions, intersections
-/
lemma definition.intersection_deux_ensembles {A B : set X} {x : X} :
x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B) :=
/- dEAduction
PrettyName
    Intersection de deux ensembles
-/
begin
    exact iff.rfl
end

lemma definition.union_deux_ensembles  {A : set X} {B : set X} {x : X} :
x ∈ A ∪ B ↔ ( x ∈ A ∨ x ∈ B) :=
/- dEAduction
PrettyName
    Union de deux ensembles
-/
begin
    exact iff.rfl
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

lemma exercise.intersection_inclus_ensemble
(A B : set X) :
A ∩ B ⊆ A
:=
/- dEAduction
PrettyName
    Un ensemble contient son intersection avec un autre
Description
    Voici un premier exercice !
-/
begin
    todo
end


lemma exercise.inclus_dans_les_deux_implique_dans_lintersection
(A B C : set X) :
(C ⊆ A) ∧ (C ⊆ B) → C ⊆ A ∩ B
:=
/- dEAduction
PrettyName
    Inclus dans les deux implique inclus dans l'intersection
Description
    Voici un deuxième exercice !
-/
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
Description
    Voici un troisième exercice !
-/
begin
    todo
end

lemma exercise.ensemble_inclus_union
(A B : set X) :
B ⊆ A ∪ B
:=
/- dEAduction
PrettyName
    Ensemble inclus dans l'union
Description
    Le bouton ∨ ("ou"), permet notamment de montrer un but de la forme "P ou Q" en choisissant si on veut montrer "P" ou "Q".
-/
begin
    todo
end

lemma exercise.ensemble_inclus_intersection
(A B : set X) :
A ⊆ A ∩ B  → (A ∪ B) = B
:=
/- dEAduction
PrettyName
    Ensemble inclus dans l'intersection
Description
    Le bouton ∨ ("ou") permet également, appliqué à une hypothèse du type "P ou Q" de faire une disjonction de cas selon si on a "P" ou "Q".
-/
begin
    todo
end

lemma exercise.inter_distributive_union
(A B C : set X):
A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)
:=
/- dEAduction
PrettyName
    Union avec une intersection
Description
    Le bouton ↔ (équivalence), permet notamment de scinder "P ↔ Q" en deux implications "P → Q" et "Q → P".
-/
begin
    todo
end

lemma exercise.exercice_bilan
(A B : set X) :
A ⊆ B ↔ A ∩ B = A
:=
/- dEAduction
PrettyName
    Exercice bilan
-/
begin
    todo
end
end exercices

end course
