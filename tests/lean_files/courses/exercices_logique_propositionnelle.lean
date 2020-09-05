-- import data.set
import tactic

-- dEAduction imports
import structures
import definitions

-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement (since it will be called with 'rw' or 'symp_rw')


-- logic names ['and', 'or', 'negate', 'implicate', 'iff', 'forall', 'exists', 'apply']
-- proofs names ['cbr', 'contrapose', 'absurdum', 'choice', 'new_object', 'assumption']



local attribute [instance] classical.prop_decidable
---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
variables (P Q R: Prop) -- NOT global


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
Tools->Logic
    implicate
Tools->ProofTechniques
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
Tools->Logic
    and implicate
Tools->ProofTechniques
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
Tools->Logic
    and implicate
Tools->ProofTechniques
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
    On peut alors appliquer le résultat de l'exercice précédent...
Tools->Logic
    and iff implicate
Tools->ProofTechniques
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
Tools->Logic
    or and implicate iff
Tools->ProofTechniques
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
Tools->Logic
    negate or and implicate iff
Tools->ProofTechniques
    assumption
-/
begin
    sorry
end

lemma exercise.non_ET :
not (P and Q) ↔ (not P) or (not Q)
:=
/- dEAduction
PrettyName
    Négation d'un "ET"
Description
    En général, le bouton "NON" tente de "pousser" la négation le long de la
    propriété.
Tools->Logic
    negate or and implicate iff
Tools->ProofTechniques
    assumption
-/
begin
    sorry
end

lemma exercise.tiers_exclus
(H : R ∧ ¬ R) :
 false
:=
/- dEAduction
PrettyName
    Le tiers exclu dit que l'une des deux propriétés "R" et "NON R" doit être
    vraie
Description
    Le bouton "0=1" permet de conclure la preuve lorsqu'on a obtenu deux
    propriétés contradictoires.
Tools->Logic
    negate or and implicate iff
Tools->ProofTechniques
    absurdum assumption
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
    Saurez-vous combiner les boutons pour démontrer cette règle ?
Tools->Logic
    negate or and implicate iff
Tools->ProofTechniques
    absurdum assumption
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
    Cette propriété de transformer une implication en une disjonction
Tools->Logic
    negate or and implicate iff
Tools->ProofTechniques
    absurdum assumption
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
Tools->Logic
    negate or and implicate iff apply
Tools->ProofTechniques
    absurdum assumption new_object
-/
begin
    sorry
end



end Logique_propositionnelle

end course

