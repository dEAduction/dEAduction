/-
This is a d∃∀duction file providing easy and progressive exercises for basic set theory.
It may be used as a tutorial for d∃∀duction.
French version.
-/

import data.set
import tactic

-- dEAduction tactics
import structures2      -- hypo_analysis, targets_analysis
import utils            -- no_meta_vars
import user_notations   -- notations that can be used in deaduction UI for a new object

-- dEAduction definitions
import set_definitions


-------------------------
-- dEAduction METADATA --
-------------------------

/- dEAduction
Title
    Exercices TER L1
Author
    Camille Lichère
Institution
    Université de France
Description
    Ce fichier contient quelques exercices faciles et progressifs de théorie élémentaire
    des ensembles. Il peut être utilisé comme tutoriel pour d∃∀duction ; en particulier,
    les boutons logiques sont introduits progressivement.
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
ImplicitUse
    True
-/
begin
     exact set.ext_iff
end


lemma definition.double_inclusion (A A' : set X) :
A = A' ↔ (A ⊆ A' ∧ A' ⊆ A):=
/- dEAduction
PrettyName
    Double inclusion
ImplicitUse
    True
-/
begin
    exact subset.antisymm_iff,
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

namespace composition
/- dEAduction
PrettyName
    Exercices sur la composition
-/

open set
variables (f: X → Y) (g : Y → Z) (A: set X) (B: set Y)

namespace definitions
/- dEAduction
PrettyName
    Définitions
-/

lemma definition.composition {x:X}:
composition g f x = g (f x)
:=
begin
    todo,
end

lemma definition.image_directe (y : Y) : y ∈ f '' A ↔ ∃ x : X, x ∈ A ∧  f x = y :=
/- dEAduction
ImplicitUse
    True
-/
begin
    todo
end

lemma definition.image_reciproque (x:X) : x ∈ f  ⁻¹' B ↔ f(x) ∈ B :=
begin
    todo
end


lemma definition.injectivite :
injective f ↔ ∀ x y : X, (f x = f y → x = y)
:=
/- dEAduction
PrettyName
    Application injective
ImplicitUse
    True
-/
begin
    refl,
end

lemma definition.surjectivite :
surjective f ↔ ∀ y : Y, ∃ x : X, y = f x
:=
/- dEAduction
PrettyName
    Application surjective
ImplicitUse
    True
-/
begin
    refl,
end




end definitions

namespace exercices


lemma exercise.composition_injections
(H1 : injective f) (H2 : injective g)
:
injective (composition g f)
:=
/- dEAduction
PrettyName
    Composition d'injections
-/
begin
    todo
end

lemma exercise.composition_surjections
(H1 : surjective f) (H2 : surjective g) :
surjective (composition g f)
:=
/- dEAduction
PrettyName
    Composition de surjections
-/
begin
    todo
end


lemma exercise.composition_image_directe
(A: set X) : 
(composition g f) '' A = g '' (f '' A)
:=
/- dEAduction
PrettyName
    Image directe par une composition
-/
begin
    todo
end


lemma exercise.composition_image_reciproque
(C: set Z) : 
(composition g f) ⁻¹' C = f ⁻¹' (g ⁻¹' C)
:=
/- dEAduction
PrettyName
    Image réciproque par une composition
-/
begin
    todo
end


end exercices
end composition
end course
