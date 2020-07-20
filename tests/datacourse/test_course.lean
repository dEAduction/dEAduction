import data.set
import tactic

-- dEAduction imports
import logics
import structures
import definitions

-- import definitions_test


----------------------------------------------
namespace set_theory -- Course title
/- dEAduction
Section
    Set Theory
-/


variables {X : Type} {Y : Type}



lemma definition.inclusion (A B : set X) : A ⊆ B ↔ ∀ {{x:X}}, x ∈ A → x ∈ B := 
iff.rfl



lemma definition.egalite_ensembles {A A' : set X} : (A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
PrettyName
    Egalité d'ensembles    
-/
by exact set.ext_iff

lemma theorem.double_inclusion {A A' : set X} : (A = A') ↔ (A ⊆ A' ∧ A' ⊆ A) :=
begin
    exact le_antisymm_iff
end


----------------------------------------------
namespace unions_and_intersections -- section 1
-- pretty name for dEAduction will be computed from lean name


lemma definition.intersection_deux  (A B : set X) (x : X) :  x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B) := 
iff.rfl
/- dEAduction
PrettyName
    Intersection de deux ensembles
-/

lemma theorem.intersection_ensemble  (A B C : set X) : C ⊆ A ∩ B ↔ C ⊆ A ∧ C ⊆ B := 
begin
    exact ball_and_distrib
end

lemma definition.intersection_quelconque (I : Type) (O : I → set X)  (x : X) : (x ∈ set.Inter O) ↔ (∀ i:I, x ∈ O i) :=
set.mem_Inter
/- dEAduction
PrettyName
    Intersection quelconque    
-/

-- Les deux lemmes suivants seront à regroupé au sein d'une même tactique : essayer le premier, 
-- en cas d'échec essayer le second. Un seul bouton dans l'interface graphique
lemma definition.union  (A : set X) (B : set X) (x : X) :  x ∈ A ∪ B ↔ ( x ∈ A ∨ x ∈ B) := 
iff.rfl
/- dEAduction
PrettyName
    Union de deux ensembles
-/

lemma definition.union_quelconque (I : Type) (O : I → set X)  (x : X) : (x ∈ set.Union O) ↔ (∃ i:I, x ∈ O i) :=
set.mem_Union
/- dEAduction
PrettyName
    Union quelconque
-/





lemma exercise.union_distributive_inter (X : Type) (A B C : set X) : A ∩ (B ∪ C)  = (A ∩ B) ∪ (A ∩ C) := 
/- dEAduction
PrettyName  
    Intersection d'unions
Description 
    L'intersection est distributive par rapport à l'union
    et ça continue sur la ligne suivante
Tools->Logic
    $ALL -implicate -negate
Tools->ProofTechniques
    $ALL -contradiction
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    double_inclusion, Riemann_hypothesis
ExpectedVarsNumber 
    X=3, A=1, B=1
-/
begin
    sorry
end    


variables {A B C : set X}

lemma exercise.inter_distributive_union : A ∪ (B ∩ C)  = (A ∪ B) ∩ (A ∪ C) := 
/- dEAduction
PrettyName 
    Union d'intersections
Description 
    L'union est distributive par rapport à l'intersection 
Tools->Logic 
    $ALL
Tools->ProofTechniques
    $ALL -choice
Tools->Statements
    $UNTIL_NOW
-/
begin
    sorry
end

end unions_and_intersections

-----------------------------------------
namespace complements -- section 2
/- dEAduction
Section
    Complementaires
-/



lemma definition.complement {A : set X} {x : X} : x ∈ set.univ \ A ↔ x ∉ A := 
by finish

lemma definition.complement_1 {A : set X} {x : X} : x ∈ set.compl A ↔ x ∉ A := 
by finish

lemma definition.complement_2 {A B : set X} {x : X} : x ∈ B \ A ↔ (x ∈ B ∧ x ∉ A) :=
iff.rfl

lemma exercise.complement_complement {A : set X} : - - A = A :=
/- dEAduction
PrettyName 
    Complémentaire du complémentaire
Description 
    Tout ensemble est égal au complémentaire de son complémentaire 
    et réciproquement.
-/
begin
    sorry
end

end complements

end set_theory