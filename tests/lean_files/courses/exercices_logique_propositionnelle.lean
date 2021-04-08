-- import data.set
import tactic

-- dEAduction imports
import structures2
import utils

-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement (since it will be called with 'rw' or 'symp_rw')

-- no Magic button ("compute")
/- dEAduction
Title
    Logique propositionnelle (tutorial)
DefaultAvailableProof
    NONE
DefaultAvailableMagic
    Assumption
-/


-- logic names ['and', 'or', 'negate', 'implicate', 'iff', 'forall', 'exists']
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
namespace Logique_propositionnelle

lemma exercise.tautologie :
P → P
:=
/- dEAduction
PrettyName
    La tautologie
Description
    Le bouton "=>" permet de démontrer une implication : pour montrer
    "P => Q", on suppose P, et on montre Q.
AvailableLogic
    implicate
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.et :
P ∧ Q → P
:=
/- dEAduction
PrettyName
    P et Q implique P
Description
    Le bouton "ET" permet de découper une hypothèse
AvailableLogic
    and implicate
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.et_commutatif_I :
P ∧ Q → Q ∧ P
:=
/- dEAduction
PrettyName
    Le "ET" est commutatif (version faible)
Description
    Le bouton "ET" permet aussi de découper le but en deux buts distincts
AvailableLogic
    and implicate
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.et_commutatif_II :
P ∧ Q ↔ Q ∧ P
:=
/- dEAduction
PrettyName
    Le "ET" est commutatif
Description
    Le bouton "↔" permet de découper le but en deux implications.
    On peut alors appliquer le résultat de l'exercice précédent en le
    sélectionnant dans la liste...
AvailableLogic
    and iff implicate
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.ou_commutatif :
P ∨ Q ↔ Q ∨ P
:=
/- dEAduction
PrettyName
    Le "OU" est commutatif
Description
    Pour utiliser l'hypothèse "P OU Q", on sépare les cas :
    dans le premier cas on suppose P, dans le second cas on suppose Q.
    Pour démontrer "Q OU P", on doit démontrer soit P, soit Q.
AvailableLogic
    and or implicate iff
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.non_non :
¬ ¬ P ↔ P
:=
/- dEAduction
PrettyName
    Double négation
Description
    Le bouton "NON" permet d'utiliser les règles logiques du "NON".
    On peut l'utiliser uniquement sur les propriétés qui sont des négations,
    c'est-à-dire de la forme "NON (...)".
AvailableLogic
    and or negate implicate iff
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.non_ET :
¬ (P ∧ Q) ↔ (¬ P) ∨ (¬ Q)
:=
/- dEAduction
PrettyName
    Négation d'un "ET"
Description
    En général, le bouton "NON" tente de "pousser" la négation le long de la
    propriété.
AvailableLogic
    and or negate implicate iff
AvailableMagic
    assumption
-/
begin
    sorry
end


lemma exercise.contradiction :
R ∨ ¬ R
:=
/- dEAduction
PrettyName
    Le tiers exclu : l'une des deux propriétés "R" et "NON R" est vraie
Description
    Le mécanisme de preuve inclus le tiers exclu, de façon un peu cachée...
AvailableLogic
    and or negate implicate iff
AvailableProof
    use_proof_methods
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.contraposition :
(P → Q) ↔ (¬ Q → ¬ P)
:=
/- dEAduction
PrettyName
    Contraposition
Description
    Le bouton "=>" permet également d'appliquer une implication "P => Q" à la
    propriété "P" pour obtenir la propriété "Q". Attention, avant de
    l'actionner il faut sélectionner toutes les propriétés requises !
AvailableLogic
    and or negate implicate iff
AvailableProof
    use_proof_methods apply
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.ou_implication_I :
(P → Q) ↔ (¬ P ∨ Q)
:=
/- dEAduction
PrettyName
    Implication sous forme de "OU"
Description
    Cette propriété permet de transformer une implication en une disjonction
AvailableLogic
    and or negate implicate iff
AvailableProof
    use_proof_methods apply
AvailableMagic
    assumption
-/
begin
    sorry
end

lemma exercise.ou_implication_II :
(P ∨ Q) ↔ (¬ P → Q)
:=
/- dEAduction
PrettyName
    "OU" sous forme d'implication
Description
    Cette propriété est très proche de la précédente.
    On peut la redémontrer entièrement, mais on peut aussi tenter d'appliquer
    le résultat de l'exercice précédent. Pour cela, il faudra introduire
    un nouvel objet, avant de lui appliquer le résultat précédent...
AvailableLogic
    and or negate implicate iff
AvailableProof
    use_proof_methods new_object apply
AvailableMagic
    assumption
-/
begin
    sorry
end



end Logique_propositionnelle

end course

