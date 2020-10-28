-- import data.set
import tactic

-- dEAduction imports
import structures2
import definitions
import notations_definitions

-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement (since it will be called with 'rw' or 'symp_rw')



local attribute [instance] classical.prop_decidable

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
parameters {X Y Z: Type}

notation [parsing_only] P ` \and ` Q := P ∧ Q
notation [parsing_only]  P ` \or ` Q := P ∨ Q
notation [parsing_only]  ` \not ` P := ¬ P
notation [parsing_only]  P ` \implies ` Q := P → Q
notation [parsing_only]  P ` \iff ` Q := P ↔ Q

notation [parsing_only]  x ` \in ` A := x ∈ A
notation [parsing_only]  A ` \cap ` B := A ∩ B
notation [parsing_only]  A ` \cup ` B := A ∪ B
notation [parsing_only]  A ` \subset ` B := A ⊆ B
notation [parsing_only]  `\emptyset` := ∅


open set


/- dEAduction
Title
    Systèmes dynamiques hamiltoniens
School
    Sorbonne Université
Teacher
    Professeur Le Roux
Year
    2020-2021
Description
    Blaaablabla bllaa blaa blaaa.
-/

namespace theorie_des_ensembles


------------------------
-- COURSE DEFINITIONS --
------------------------
lemma definition.ssi {P Q : Prop} : (P ↔ Q) ↔ (P → Q) ∧ (Q → P) :=
begin
    exact iff_def
end
lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
begin
    exact iff.rfl
end

lemma definition.egalite_deux_ensembles {A A' : set X} :
(A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
PrettyName
    egalité de deux ensembles
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
PrettyName
    Intersection de deux ensembles
-/
begin
    exact iff.rfl
end

lemma definition.intersection_quelconque_ensembles {I : Type} {E : I → set X}  {x : X} :
(x ∈ set.Inter (λ i, E i)) ↔ (∀ i:I, x ∈ E i) :=
/- dEAduction
PrettyName
    Intersection d'une famille d'ensembles quelconque
-/
begin
    exact set.mem_Inter
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

lemma definition.union_quelconque_ensembles {I : Type} {E : I → set X}  {x : X} :
(x ∈ set.Union (λ i, E i)) ↔ (∃ i:I, x ∈ E i) :=
/- dEAduction
PrettyName
    Union d'une famille d'ensembles quelconque
-/
begin
    exact set.mem_Union
end


---------------
-- EXERCICES --
---------------
lemma exercise.union_distributive_inter : A ∩ (B ∪ C)  = (A ∩ B) ∪ (A ∩ C) :=
/- dEAduction
PrettyName
    Intersection avec une union
Description
    L'intersection est distributive par rapport à l'union
Tools->Logic
    $ALL -negate
Tools->ProofTechniques
    $ALL -contradiction
Tools->Definitions
    $UNTIL_NOW -union_quelconque_ensembles -intersection_quelconque_ensembles
Tools->Theorems
    double_inclusion
ExpectedVarsNumber
    X=3, A=1, B=1
-/
begin
    sorry,
end


lemma exercise.inter_distributive_union : A ∪ (B ∩ C)  = (A ∪ B) ∩ (A ∪ C) :=
/- dEAduction
PrettyName
    Union avec une intersection
Description
    L'union est distributive par rapport à l'intersection
-/
begin
    sorry
end

end unions_et_intersections




end exercices_supplementaires

end theorie_des_ensembles

end course
