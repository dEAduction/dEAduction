import data.set
import tactic

-- dEAduction imports
import logics
import definitions
import structures


local attribute [instance] classical.prop_decidable


------------------
-- COURSE TITLE --
------------------
namespace theorie_des_ensembles
-- global variable --
variable {X : Type}


lemma exercise.test_destruct_exist (A B : set X) (h : ∃ {{x : X}}, x ∈ A) : ∃ {{x : X}}, x ∈ A :=
/- dEAduction
PrettyName
    test_exist
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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


lemma exercise.test_construct_exist (A B : set X) (x : X) (h : x ∈ A) : ∃ {{x : X}}, x ∈ A :=
/- dEAduction
PrettyName
    test_exist
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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

lemma exercise.test_assumption (A : Prop) : A :=
/- dEAduction
PrettyName
    test_apply_aa
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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


lemma exercise.test_use_or (P Q : Prop) (h : P ∨ Q) : P ∨ Q :=
/- dEAduction
PrettyName
    test_apply_or
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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

lemma exercise.test_construct_or_left (P Q : Prop) (h : P): P ∨ Q :=
/- dEAduction
PrettyName
    test_apply_or
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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


lemma exercise.test_construct_or_right (P Q : Prop) (h : Q): P ∨ Q :=
/- dEAduction
PrettyName
    test_apply_or
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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

lemma exercise.test_use_and (P Q : Prop) (h : P ∧ Q) : P :=
/- dEAduction
PrettyName
    test_apply_and
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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

lemma exercise.test_intro_and (P Q : Prop) (h : P) (h2 : Q) : P ∧ Q :=
/- dEAduction
PrettyName
    test_apply_and2
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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


lemma exercise.test_not_hyp (P : Prop) (h : ¬ ¬ P) : P :=
/- dEAduction
PrettyName
    test_apply_not
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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


lemma exercise.test_not_target (P : Prop) (h : P) : ¬ ¬ P :=
/- dEAduction
PrettyName
    test_apply_not
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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


lemma exercise.test_create_fun (h : ∀ {{x:X}}, ∃ {{y:X}}, x=y) : ∃ F: X → X, ∀ {{x:X}}, x = F x :=
/- dEAduction
PrettyName
    test_apply_not
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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


lemma exercise.test_create_implication (P Q : Prop) (h : Q) : P → Q :=
/- dEAduction
PrettyName
    test_apply_not
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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

lemma exercise.test_create_implication2 (P Q : Prop) (h : Q) : P → Q :=
/- dEAduction
PrettyName
    test_apply_not
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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


lemma exercise.test_apply_target {A B : Prop} (h : A ↔ B) : A → B :=
/- dEAduction
PrettyName
    test_apply_target
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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

lemma exercise.test_apply_sub_eg_sans_ambiguite (x y : X) (h : x = y) (P : X → Prop) (h2 : P x) : P y :=
/- dEAduction
PrettyName
    test_apply_target
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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


lemma exercise.test_apply_sub_iff_sans_ambiguite (A B : Prop) (h : A ↔  B) (P : Prop → Prop) (h2 : P A) : P B :=
/- dEAduction
PrettyName
    test_apply_target
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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


lemma exercise.test_apply_sub_eg_avec_ambiguite (x y : X) (h : x = y) (P : X → X → Prop) (h2 : P x y) : P y x :=
/- dEAduction
PrettyName
    test_apply_target
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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


lemma exercise.test_apply_sub_iff_avec_ambiguite (A B : Prop) (h : A ↔  B) (P : Prop → Prop → Prop) (h2 : P A B) : P B A :=
/- dEAduction
PrettyName
    test_apply_target
Description
    test_exist
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
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






end theorie_des_ensembles
