
-- Lean standard imports
import tactic
import data.real.basic

-- dEAduction tactics
-- structures2 and utils are vital
-- import deaduction_all_tactics
import structures2      -- hypo_analysis, targets_analysis
import utils            -- no_meta_vars
-- import compute_all      -- Tactics for the compute buttons
import push_neg_once    -- Pushing negation just one step
-- import induction        -- Induction theorems

-- dEAduction definitions
import set_definitions
-- import real_definitions

-- Use classical logic
local attribute [instance] classical.prop_decidable


/- dEAduction
Title
    Logique propositionnelle (tutoriel)
Author
    Frédéric Le Roux
Institution
    Université du Monde
Description
    Ce fichier, qui peut servir de tutoriel, contient quelques énoncés de logiques propositionnelle.
    Le but n'est pas de les démontrer du point de vue de la logique propositionnelle,
    mais plutôt de voir comment l'interface fonctionne sur ces énoncés.
AvailableProof
    NONE
AvailableCompute
    NONE
-/

-- Use classical logic
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
AvailableLogic
    implies
AvailableMagic
    assumption
-/
begin
    todo
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
    and implies
AvailableMagic
    assumption
-/
begin
    todo
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
    and implies
AvailableMagic
    assumption
-/
begin
    todo
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
    and iff implies
AvailableMagic
    assumption
-/
begin
    todo
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
    and or implies iff
AvailableMagic
    assumption
-/
begin
    todo
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
    and or not implies iff
AvailableMagic
    assumption
-/
begin
    todo
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
    and or not implies iff
AvailableMagic
    assumption
-/
begin
    todo
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
    and or not implies iff
AvailableProof
    proof_methods
AvailableMagic
    assumption
-/
begin
    todo
end

lemma exercise.negation_implication :
¬ (P → Q) ↔ (P ∧ ¬ Q)
:=
/- dEAduction
PrettyName
    Négation d'une implication
Description
    Blabla
AvailableLogic
    and or not implies iff
AvailableProof
    proof_methods
AvailableMagic
    assumption

-/
begin
    todo
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
    On pourra raisonner par l'absurde en utilisant les "Méthodes de preuves".
AvailableLogic
    and or not implies iff
AvailableProof
    proof_methods
AvailableMagic
    assumption

-/
begin
    todo
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
    and or not implies iff
AvailableProof
    proof_methods
AvailableMagic
    assumption
-/
begin
    todo
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
    and or not implies iff
AvailableProof
    proof_methods new_object
AvailableMagic
    assumption
-/
begin
    todo
end



end Logique_propositionnelle

end course

