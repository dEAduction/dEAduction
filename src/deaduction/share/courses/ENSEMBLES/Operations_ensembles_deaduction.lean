/-
Feuille d'exercice pour travailler les opérations et autres définitions sur les ensembles 
-/

import data.set
import tactic

-- dEAduction tactics
import structures2      -- hypo_analysis, targets_analysis
import utils            -- no_meta_vars
import user_notations   -- notations that can be used in deaduction UI for a new object
import push_neg_once


-- dEAduction definitions
import set_definitions

-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement or an equality
-- (since it will be called with 'rw' or 'symp_rw')

-------------------------
-- dEAduction METADATA --
-------------------------
-- logic names ['and', 'or', 'negate', 'implicate', 'iff', 'forall', 'exists']
-- proofs names ['use_proof_methods', 'new_object', 'apply', 'assumption']
-- magic names ['compute']
-- proof methods names ['cbr', 'contrapose', 'absurdum', 'sorry']

/- dEAduction
title = "Théorie des ensembles : opérations"
author = "Isabelle Dubois"
institution = "Université de Lorraine"
description = 'Ce cours correspond à un cours standard de théorie "élémentaire" des ensembles.'
[display]
set.prod = [ -2, " × ", -1]
[settings]
logic.usr_jokers_available = false
logic.use_color_for_applied_properties = false
functionality.allow_induction = false
functionality.calculator_available = true
others.Lean_request_method = "normal"

-/

local attribute [instance] classical.prop_decidable

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
variables {X Y Z: Type}


open set




namespace generalites
/- dEAduction
pretty_name = "Généralités"
-/

------------------------
-- COURSE DEFINITIONS --
------------------------
lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
/- dEAduction
implicit_use = true
-/
begin
    todo
end

lemma definition.egalite_deux_ensembles {A A' : set X} :
(A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
pretty_name = "Egalité de deux ensembles"
implicit_use = true
-/
begin
     todo
end

lemma definition.ensemble_vide
(A: set X) :
(A = ∅) ↔ ∀ x : X, x ∉ A
:=
begin
    todo
end

lemma definition.ensemble_non_vide
(A: set X) :
(A ≠ ∅) ↔ ∃ x : X, x ∈ A
:=
begin
   todo
end

lemma definition.ensemble_extension {X: Type}  {P : X → Prop} {x:X} :
 x ∈ {x | P x} ↔ P x
:=
/- dEAduction
pretty_name = "Ensemble défini en extension"
-/
begin
    todo
end

lemma definition.singleton {X : Type} {x y : X}: x ∈ ({y} : set X) ↔ x = y
:=
/- dEAduction
pretty_name = "Ensemble singleton"
-/
begin
    todo
end

lemma exercise.double_inclusion (A A' : set X) :
A = A' ↔ (A ⊆ A' ∧ A' ⊆ A) 
:=
/- dEAduction
pretty_name = "Egalité de deux ensembles : double inclusion"
-/
begin
    todo
end

lemma exercise.nonvide (A : set X) (x_0 : X) :
 A = { x_0 } → A ≠ ∅
:=
/- dEAduction
pretty_name = "Un singleton est non vide"
-/
begin
    todo
end

lemma exercise.inclusion_transitive
(A B C : set X) :
(A ⊆ B ∧ B ⊆ C) → A ⊆ C
:=
/- dEAduction
pretty_name = "Transitivité de l'inclusion"
-/
begin
    todo
end




end generalites

---------------
-- SECTION 1 --
---------------
namespace unions_et_intersections
-- variables unions_et_intersections --
variables {A B C : set X}

-----------------
-- DEFINITIONS --
-----------------

lemma definition.intersection_deux_ensembles {A B : set X} {x : X} :
x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B) :=
/- dEAduction
pretty_name = "Intersection de deux ensembles"
implicit_use = true
-/
begin
    exact iff.rfl
end



lemma definition.union_deux_ensembles  {A : set X} {B : set X} {x : X} :
x ∈ A ∪ B ↔ ( x ∈ A ∨ x ∈ B) :=
/- dEAduction
pretty_name = "Union de deux ensembles"
implicit_use = true
-/
begin
    exact iff.rfl
end



---------------
-- EXERCICES --
---------------

lemma exercise.intersection_comm :
A ∩ B = B ∩ A
:=
/- dEAduction
pretty_name = "Commutativité de l'intersection"
-/
begin
    todo
end


lemma exercise.union_comm :
A ∪ B = B ∪ A
:=
/- dEAduction
pretty_name = "Commutativité de l'union"
-/
begin
    todo
end



lemma exercise.intersection_inclus_ensemble :
(A ∩ B ⊆ B ) 
:=
/- dEAduction
pretty_name = "Un ensemble contient son intersection avec un autre"
-/
begin
    todo
end

lemma exercise.ensemble_inclus_union :
A  ⊆ A ∪ B
:=
/- dEAduction
pretty_name = "Un ensemble est contenu dans son union avec un autre"
-/
begin
    todo
end

lemma exercise.union_distributive_inter : A ∩ (B ∪ C)  = (A ∩ B) ∪ (A ∩ C) :=
/- dEAduction
pretty_name = "Intersection avec une union"
description = "L'intersection est distributive par rapport à l'union"
available_logic = "$ALL"
available_proofs = "$ALL"
available_definitions = "$UNTIL_NOW"
available_theorems = "double_inclusion"
expected_vars_number = "X=3, A=1, B=1"
-/
begin
    todo
end

-- NB: 'ExpectedVarsNumber' is not implemented yet
-- planned to be used for naming variables


lemma exercise.inter_distributive_union : A ∪ (B ∩ C)  = (A ∪ B) ∩ (A ∪ C) :=
/- dEAduction
pretty_name = "Union avec une intersection"
description = "L'union est distributive par rapport à l'intersection"
available_definitions = "$UNTIL_NOW"
-/
begin
    todo
end

lemma exercise.inclus_eq_union : A  ⊆ B   ↔ (A ∪ B)=B
:=
/- dEAduction
pretty_name = "Caractérisation de l'inclusion par l'union"
description = "Caractérisation de l'inclusion par l'union"
available_definitions = "$UNTIL_NOW"
-/
begin
    todo
end

lemma exercise.inclus_eq_inter : (A  ⊆ B )  ↔ ( (A ∩ B)=A)
:=
/- dEAduction
pretty_name = "Caractérisation de l'inclusion par l'intersection"
description = "Caractérisation de l'inclusion par l'intersection"
available_definitions = "$UNTIL_NOW"
-/
begin
    todo
end


lemma exercise.cond_egalite : ((A ∩ B)=(A ∪ B) ) → (A=B)
:=
/- dEAduction
pretty_name = "Quand l'intersection égale l'union"
description = "Quand l'intersection égale l'union"
available_definitions = "$UNTIL_NOW"
-/
begin
    todo
end

lemma exercise.cond_egalite2 : ((A ∩ B)= (A ∩ C) ∧  (A ∪ B)= (A ∪ C)) → (B=C)
:=
/- dEAduction
pretty_name = "Même union et même intersection"
description = "Même union et même intersection"
available_definitions = "$UNTIL_NOW"
-/
begin
    todo
end

end unions_et_intersections


---------------
-- SECTION 2 --
---------------
namespace complementaire_difference
/- dEAduction
pretty_name = "Complémentaire et Différence"
-/


-- variables complementaire --
variables  {A B C : set X}

-- notation `∁`A := set.compl A

-----------------
-- DEFINITIONS --
-----------------
lemma definition.complement {A : set X} {x : X} : x ∈ set.compl A ↔ x ∉ A :=
/- dEAduction
pretty_name = "Complémentaire"
-/
begin
    todo
end

lemma definition.difference
(A B : set X) (x : X) :
x ∈ (A \ B) ↔ x ∈ A ∧ x ∉ B
:=
/- dEAduction
pretty_name = "Différence de deux ensembles"
-/
begin
    refl,
end

---------------
-- EXERCICES --
---------------



lemma exercise.complement_complement : (set.compl (set.compl A)) = A :=
/- dEAduction
pretty_name = "Complémentaire du complémentaire"
description = "Tout ensemble est égal au complémentaire de son complémentaire"
available_definitions = "$UNTIL_NOW"
-/
begin
    todo
end

lemma exercise.diff_diff : ((A \ B)\ C) = (A \ (B ∪ C)) :=
/- dEAduction
pretty_name = "Différence d'une différence"
description = "Différence d'une différence"
available_definitions = "$UNTIL_NOW"
-/
begin
    todo
end

lemma exercise.inter_compl :
(A ∩  ((set.compl A) ∪ B) ) = ( A ∩  B) :=
/- dEAduction
pretty_name = "Intersection et complémentaire"
description = "Intersection et complémentaire"
available_definitions = "$UNTIL_NOW"
-/
begin
    todo
end

lemma exercise.decomposition_union_inter :
A = ( A ∩  B) ∪ ( A ∩  (set.compl B)) :=
/- dEAduction
pretty_name = "Décomposition d'un ensemble avec une union"
description = "Décomposition d'un ensemble avec une union"
available_definitions = "$UNTIL_NOW"
-/
begin
    todo
end

lemma exercise.decomposition_inter_union :
A = ( A  ∪   B) ∩ ( A  ∪   (set.compl B)) :=
/- dEAduction
pretty_name = "Décomposition d'un ensemble avec une intersection"
description = "Décomposition d'un ensemble avec une intersection"
available_definitions = "$UNTIL_NOW"
-/
begin
    todo
end


lemma exercise.complement_union_deux :
set.compl (A ∪ B) = (set.compl A) ∩ (set.compl B) :=
/- dEAduction
pretty_name = "Complémentaire d'union"
description = "Le complémentaire de l'union de deux ensembles égale l'intersection des complémentaires"
available_definitions = "$UNTIL_NOW"
-/
begin
    todo
end

lemma exercise.complement_intersection_2
(A B : set X):
set.compl (A ∩  B) = (set.compl A) ∪ (set.compl B)
:=
/- dEAduction
pretty_name = "Complémentaire d'une intersection"
-/
begin
    todo
end


lemma exercise.inclusion_complement_I :
A ⊆ B → set.compl B ⊆ set.compl A
:=
/- dEAduction
pretty_name = "Le passage au complémentaire renverse les inclusions, implication"
description = "Si A est inclus dans B, alors le complémentaire de A contient le complémentaire de B"
-/
begin
    todo
end

lemma exercise.inclusion_complement_II :
A ⊆ B ↔ set.compl B ⊆ set.compl A
:=
/- dEAduction
pretty_name = "Le passage au complémentaire renverse les inclusions, équivalence"
description = "Si A est inclus dans B, alors le complémentaire de A contient le complémentaire de B"
-/
begin
    todo
end




end complementaire_difference




namespace produits_cartesiens
/- dEAduction
pretty_name = "Produits cartésiens"
-/


-- Peut-on en faire une définition ?
lemma theorem.type_produit :
∀ z:X × Y, ∃ x:X, ∃ y:Y, z = (x,y)
:=
/- dEAduction
pretty_name = "Element d'un produit cartésien de deux ensembles"
-/
begin
    todo
end


lemma definition.produit_de_parties {A : set X} {B : set Y}
{x:X} {y:Y} :
(x,y) ∈ set.prod A B ↔ x ∈ A ∧ y ∈ B
:=
/- dEAduction
pretty_name = "Produit cartésien de deux parties"
-/
begin
    todo
end

lemma exercise.produit_non_vide
(A : set X) ( B: set Y) :
(A ≠  ∅) ∧ (B ≠ ∅)  →  (set.prod A B ) ≠  ∅
:=
/- dEAduction
pretty_name = "Si les ensembles sont non vides, le produit est non vide"
-/
begin
    todo,
end

lemma exercise.produit_avec_vide
(A : set X) ( B: set Y) :
(B = ∅)  →  (set.prod A B ) = ∅
:=
/- dEAduction
pretty_name = "Le produit avec l'ensemble vide est vide"
-/
begin
    todo,
end

lemma exercise.produit_deux_singletons
(A : set X) ( B: set Y) (x: X) (y : Y):
(A = {x}) ∧ (B ={y})  →   ∃ z : X × Y , (set.prod A B ) = {z}
:=
/- dEAduction
pretty_name = "Le produit de deux singletons est un singleton"
-/
begin
    todo,
end


lemma exercise.produit_avec_intersection
(A : set X) (B C : set Y) :
set.prod A (B ∩ C) = (set.prod A B) ∩ (set.prod A C)
:=
begin
    todo,
end


end produits_cartesiens





-----------------------------------
-----------------------------------
namespace exercices_supplementaires







lemma exercise.exercice_ensembles_4a
(A B C : set X) :
A ∩ B = A ∩ C ∧ (set.compl A) ∩ B = (set.compl A) ∩ C → B ⊆ C
:=
/- dEAduction
pretty_name = "Caractérisation par intersection avec A et son complémentaire, I"
-/
begin
    todo
end

lemma exercise.exercice_ensembles_4b
(A B C : set X) :
A ∩ B = A ∩ C ∧ (set.compl A) ∩ B = (set.compl A) ∩ C → B = C
:=
/- dEAduction
pretty_name = "Caractérisaton par intersection avec A et son complémentaire, II"
-/
begin
    todo
end



--def diff {X : Type} (A B : set X) := {x ∈ A | ¬ x ∈ B}
--notation A `\\` B := diff A B

-- def symmetric_difference {X : Type} (A B : set X) := (A ∪ B) \ (A ∩ B)
-- notation A `Δ` B := symmetric_difference A B




lemma definition.difference_symetrique
(A B : set X) :
(A Δ B) =  (A ∪ B) \ (A ∩ B)
:=
/- dEAduction
pretty_name = "Différence symétrique de deux ensembles"
-/
begin
    refl,
end



lemma exercise.difference_symetrique_1
(A B : set X) :
(A Δ B) = (A \ B) ∪ (B \ A)
:=
/- dEAduction
pretty_name = "Différence symétrique - autre définition"
-/
begin
    todo
end

lemma exercise.difference_symetrique_inter
(A B C : set X) :
(A ∩ (B Δ C)) = ((A ∩ B) Δ (A ∩ C))
:=
/- dEAduction
pretty_name = "Différence symétrique et intersection"
-/
begin
    todo
end

lemma exercise.difference_symetrique_egalite
(A B C : set X) :
(A Δ C )= (B Δ C ) →  (A = B)
:=
/- dEAduction
pretty_name = "Egalité et Différence symétrique"
-/
begin
    todo
end


lemma exercise.difference_symetrique_comm
(A B : set X) :
(A Δ B) = (B Δ A)
:=
/- dEAduction
pretty_name = "Commutativité de la différence symétrique"
-/
begin
    todo
end



lemma exercise.difference_symetrique_vide
(A B : set X) :
(A Δ B) = ∅ ↔ A = B
:=
/- dEAduction
pretty_name = "Caractérisation d'une différence symétrique vide"
-/
begin
    todo
end


lemma exercise.difference_symetrique_3
(A B C : set X) :
((A Δ B) Δ C) = (A Δ (B Δ C))
:=
/- dEAduction
pretty_name = "Différence symétrique d'une différence symétrique"
-/
begin
    todo
end



end exercices_supplementaires


end course