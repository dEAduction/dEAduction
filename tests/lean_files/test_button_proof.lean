import data.set
import tactic

-- dEAduction imports
import logics
import definitions
import structures2


local attribute [instance] classical.prop_decidable


------------------
-- COURSE TITLE --
------------------
namespace theorie_des_ensembles
-- global variable --
variable {X : Type}
variable {Y : Type}

lemma exercise.test_destruct_exist (A B : set X) (H : ∃ {{x : X}}, x ∈ A) : ∃ {{x : X}}, x ∈ A :=
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


lemma exercise.test_construct_exist (A B : set X) (x : X) (H : x ∈ A) : ∃ {{x : X}}, x ∈ A :=
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

lemma exercise.test_assumption (A : Prop) (H : A) : A :=
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


lemma exercise.test_use_or (P Q : Prop) (H : P ∨ Q) : P ∨ Q :=
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

lemma exercise.test_construct_or_left (P Q : Prop) (H : P): P ∨ Q :=
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


lemma exercise.test_construct_or_right (P Q : Prop) (H : Q): P ∨ Q :=
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

lemma exercise.test_use_and (P Q : Prop) (H : P ∧ Q) : P :=
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

lemma exercise.test_intro_and (P Q : Prop) (H1 : P) (h2 : Q) : P ∧ Q :=
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


lemma exercise.test_not_hyp (P : Prop) (H1 : ¬ ¬ P) : P :=
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


lemma exercise.test_not_target (P : Prop) (H1 : P) : ¬ ¬ P :=
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


lemma exercise.test_create_fun (H1 : ∀ {{x:X}}, ∃ {{y:X}}, x=y) : ∃ F: X → X, ∀ {{x:X}}, x = F x :=
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


lemma exercise.test_create_implication (P Q : Prop) (H1 : Q) : P → Q :=
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

lemma exercise.test_create_implication2 (P Q : Prop) (H1 : Q) : P → Q :=
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


lemma exercise.test_apply_fun (x y : X) (f : X → X) (H1 : x = y) : (f x = f y) :=
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

Tools->Theorems

ExpectedVarsNumber

-/
begin
    sorry
end



lemma exercise.test_apply_quant_forall (x : X) (P : X → Prop) (H1 : ∀ t:X, P t) : P x :=
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




lemma exercise.test_apply_imply (P Q : Prop) (h : P) (H1 : P → Q ) : Q :=
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


lemma exercise.test_apply_imply_with_quant (x : X) (P Q : X → Prop) (H1 : ∀ {t:X}, P t → Q t) (H2 : P x) : Q x :=
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



lemma exercise.test_apply_sub_with_quant (x : X) (u v : X → X) (H1 : ∀ {{t: X}}, u t = v t) (H2 : u x = x): v x = x :=
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



lemma exercise.test_apply_sub_iff_with_quant (x : X) (P Q : X → Prop) (H1 : ∀ {{t: X}}, P t ↔ Q t) (H2 : P x) : Q x :=
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




lemma exercise.test_apply_sub_eg_sans_ambiguite (x y : X) (H1 : x = y) (P : X → Prop) (H2 : P x) : P y :=
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


lemma exercise.test_apply_sub_iff_sans_ambiguite (A B : Prop) (H1 : A ↔  B) (P : Prop → Prop) (H2 : P A) : P B :=
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


lemma exercise.test_apply_sub_eg_avec_ambiguite (x y : X) (H1 : x = y) (P : X → X → Prop) (H2 : P x y) : P y x :=
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


lemma exercise.test_apply_sub_iff_avec_ambiguite (A B : Prop) (H : A ↔  B) (P : Prop → Prop → Prop) (H2 : P A B) : P B A :=
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

lemma exercise.test_proof_by_contradiction (A : Prop ) (H : ¬ A → false) : A :=
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


lemma exercise.test_proof_by_contraposee (A B : Prop ) (H : ¬ B → ¬ A) : A → B :=
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
