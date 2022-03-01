-- import data.set
import tactic
import data.set
import data.real.basic

-- dEAduction imports
import structures2
import utils
import compute

-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement (since it will be called with 'rw' or 'symp_rw')

-- no Magic button ("compute")
/- dEAduction
Title
    Tautologies (tutoriel)
Author
    Frédéric Le Roux
Institution
    Université du Monde
Description
    Ce fichier contient exercices très simples qui peuvent servir à tester ou illustrer
    les effets des différents boutons logiques.
DefaultAvailableProof
    NONE
DefaultAvailableMagic
    Assumption
-/


-- logic names ['and', 'or', 'negate', 'implies', 'iff', 'forall', 'exists']
-- proofs names ['proof_methods', 'new_object', 'apply']
-- magic names ['compute', 'assumption']


local attribute [instance] classical.prop_decidable
---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
variables (P Q R: Prop) -- NOT global
notation [parsing_only] P ` \and ` Q := P ∧ Q
notation [parsing_only]  P ` \or ` Q := P ∨ Q
notation [parsing_only]  ` \not ` P := ¬ P
notation [parsing_only]  P ` \implies ` Q := P → Q
notation [parsing_only]  P ` \iff ` Q := P ↔ Q


------------------
-- COURSE TITLE --
------------------
-- namespace Tautologies

lemma exercise.implication (H: P → Q):
P → Q
:=
/- dEAduction
PrettyName
    Implication
Description
    Utilisation et démonstration d'une implication.
AvailableLogic
    implies
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.et (H: P ∧ Q):
P ∧ Q
:=
/- dEAduction
PrettyName
    Conjonction
Description
    Utilisation et démonstration d'une conjonction.
AvailableLogic
    and
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.ou_1 (H: P ∨ Q) (HP: P → R) (HQ: Q → R):
R
:=
/- dEAduction
PrettyName
    Disjonction I
Description
    Utilisation d'une disjonction.
AvailableLogic
    or implies
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.ou_2 (H: P):
P ∨ Q
:=
/- dEAduction
PrettyName
    Disjonction II
Description
    Démonstration d'une disjonction.
AvailableLogic
    or
AvailableMagic
    assumption
-/
begin
    sorry
end

variable S: Prop

lemma exercise.ou_3 (H: P ∨ Q) (HP: P → R) (HQ: Q → S):
R ∨ S
:=
/- dEAduction
PrettyName
    Disjonction III
Description
    Utilisation et démonstration d'une disjonction.
AvailableLogic
    or implies
AvailableMagic
    assumption
-/
begin
    sorry
end

variables (X: Type) 

lemma exercise.quel_que_soit (P Q: X → Prop) (H: ∀ x, P x) (H': ∀ x, (P x → Q x)):
∀ x, Q x
:=
/- dEAduction
PrettyName
    Quel que soit
Description
    Utilisation et démonstration d'une propriété universelle.
AvailableLogic
    forall implies
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.Existe_0 : (∃ x: ℝ, x >0) :=
/- dEAduction
PrettyName
    Existence (a)
Description
    Démonstration d'une propriété existentielle.
AvailableLogic
    exists
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.Existe_b : (∃ a b: ℝ, a < b) :=
/- dEAduction
PrettyName
    Existence (b)
Description
    Démonstration d'une propriété existentielle.
AvailableLogic
    exists
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.Existe_1 (P Q: X → Prop) (x: X) (H: P x) (H': (P x → Q x)):
∃ x, Q x
:=
/- dEAduction
PrettyName
    Existence I
Description
    Démonstration d'une propriété existentielle.
AvailableLogic
    forall exists implies
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.Existe_2 (P Q: X → Prop) (H: ∃ x, P x) (H': ∀ x, (P x → Q x)):
∃ x, Q x
:=
/- dEAduction
PrettyName
    Existence II
Description
    Utilisation et démonstration d'une propriété existentielle.
AvailableLogic
    forall exists implies
AvailableMagic
    assumption
-/
begin
    sorry
end

-- end Tautologies

end course

