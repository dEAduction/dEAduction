import data.set
import tactic

-- dEAduction imports
import logics
import structures
import definitions

namespace elementary_logic
/- dEAduction
Section
    Elementary logic
-/

lemma definition.iff {P Q : Prop} : ( P ↔ Q ) ↔ (P → Q) ∧ (Q → P) :=
iff_def
/- dEAduction
PrettyName
    If and only if defition
-/

end elementary_logic


namespace set_theory -- Course title
/- dEAduction
Section
    Set theory
-/

variables {X : Type} {Y : Type}

lemma definition.inclusion (A B : set X) : A ⊆ B ↔ ∀ {{x:X}}, x ∈ A → x ∈ B := 
iff.rfl
/- dEAduction
PrettyName
    Inclusion of two sets
-/

lemma definition.equality_two_sets {A A' : set X} : (A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
PrettyName
    Equality of two sets
-/
by exact set.ext_iff

lemma theorem.double_inclusion {A A' : set X} : (A = A') ↔ (A ⊆ A' ∧ A' ⊆ A) :=
/- dEAduction
PrettyName
    Double inclusion
-/
begin
    exact le_antisymm_iff
end


namespace unions_and_intersections -- Section 1


lemma definition.intersection_two_sets (A B : set X) (x : X) :  x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B) := 
iff.rfl
/- dEAduction
PrettyName
    Intersection of two sets
-/

lemma theorem.included_in_intersection_iff  (A B C : set X) : C ⊆ A ∩ B ↔ C ⊆ A ∧ C ⊆ B := 
/- dEAduction
PrettyName
    Included in intersection iff
-/
begin
    exact ball_and_distrib
end

lemma definition.intersection_arbitrary_sets (I : Type) (O : I → set X)  (x : X) : (x ∈ set.Inter O) ↔ (∀ i:I, x ∈ O i) :=
set.mem_Inter
/- dEAduction
PrettyName
    Intersection of an arbitrary family of sets
-/

lemma definition.union_two_sets  (A : set X) (B : set X) (x : X) :  x ∈ A ∪ B ↔ ( x ∈ A ∨ x ∈ B) := 
iff.rfl
/- dEAduction
PrettyName
    Union of two sets
-/

lemma definition.union_arbitrary_sets (I : Type) (O : I → set X)  (x : X) : (x ∈ set.Union O) ↔ (∃ i:I, x ∈ O i) :=
set.mem_Union
/- dEAduction
PrettyName
    Union of an arbitrary family of sets
-/

lemma exercise.intersection_dist_over_union (X : Type) (A B C : set X) : A ∩ (B ∪ C)  = (A ∩ B) ∪ (A ∩ C) := 
/- dEAduction
PrettyName
    Intersection distributes over union
Description 
    The intersection of sets distributes over the union of sets.
Tools->Logic
    $ALL -implicate -negate
Tools->ProofTechniques
    $ALL -contradiction
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    double_inclusion
ExpectedVarsNumber
    X=3, A=1, B=1
-/
begin
    sorry
end    

variables {A B C : set X}

lemma exercise.union_dist_over_union : A ∪ (B ∩ C)  = (A ∪ B) ∩ (A ∪ C) := 
/- dEAduction
PrettyName
    Union distributes over intersection
Description 
    The union of sets distributes over the intersection of sets.
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


namespace complements -- section 2
/- dEAduction
Section
    Complements
-/


lemma definition.complement {A : set X} {x : X} : x ∈ set.univ \ A ↔ x ∉ A := 
by finish
/- dEAduction
PrettyName
    Complement
-/

lemma definition.complement_1 {A : set X} {x : X} : x ∈ set.compl A ↔ x ∉ A := 
by finish
/- dEAduction
PrettyName
    Complement 1
-/

lemma definition.complement_2 {A B : set X} {x : X} : x ∈ B \ A ↔ (x ∈ B ∧ x ∉ A) :=
iff.rfl
/- dEAduction
PrettyName
    Complement 2
-/

lemma exercise.complement_of_complement {A : set X} : - - A = A :=
/- dEAduction
PrettyName 
    Complement of complement
Description 
    Every set equals the complement of its complement.
-/
begin
    sorry
end

end complements
end set_theory
