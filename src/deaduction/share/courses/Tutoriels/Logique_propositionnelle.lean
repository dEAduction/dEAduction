
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
title = "Logique propositionnelle (tutoriel)"
author = "Frédéric Le Roux"
institution = "Université du Monde"
description = """
Ce fichier, qui peut servir de tutoriel, contient quelques énoncés de logiques propositionnelle.
Le but n'est pas de les démontrer du point de vue de la logique propositionnelle,
mais plutôt de voir comment l'interface fonctionne sur ces énoncés.
"""
available_proof = "NONE"
available_compute = "NONE"
[settings]
logic.usr_jokers_available = false
logic.use_color_for_applied_properties = false
functionality.allow_induction = false
functionality.calculator_available = false
others.Lean_request_method = "normal"
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
pretty_name = "La tautologie"
description = """
Le bouton "=>" permet de démontrer une implication : pour montrer
"P => Q", on suppose P, et on montre Q.
"""
available_logic = "implies"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.et :
P ∧ Q → P
:=
/- dEAduction
pretty_name = "P et Q implique P"
description = 'Le bouton "ET" permet de découper une hypothèse'
available_logic = "and implies"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.et_commutatif_I :
P ∧ Q → Q ∧ P
:=
/- dEAduction
pretty_name = 'Le "ET" est commutatif (version faible)'
description = 'Le bouton "ET" permet aussi de découper le but en deux buts distincts'
available_logic = "and implies"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.et_commutatif_II :
P ∧ Q ↔ Q ∧ P
:=
/- dEAduction
pretty_name = 'Le "ET" est commutatif'
description = """
Le bouton "↔" permet de découper le but en deux implications.
On peut alors appliquer le résultat de l'exercice précédent en le
sélectionnant dans la liste...
"""
available_logic = "and iff implies"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.ou_commutatif :
P ∨ Q ↔ Q ∨ P
:=
/- dEAduction
pretty_name = 'Le "OU" est commutatif'
description = """
Pour utiliser l'hypothèse "P OU Q", on sépare les cas :
dans le premier cas on suppose P, dans le second cas on suppose Q.
Pour démontrer "Q OU P", on doit démontrer soit P, soit Q.
"""
available_logic = "and or implies iff"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.non_non :
¬ ¬ P ↔ P
:=
/- dEAduction
pretty_name = "Double négation"
description = """
Le bouton "NON" permet d'utiliser les règles logiques du "NON".
On peut l'utiliser uniquement sur les propriétés qui sont des négations,
c'est-à-dire de la forme "NON (...)".
"""
available_logic = "and or not implies iff"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.non_ET :
¬ (P ∧ Q) ↔ (¬ P) ∨ (¬ Q)
:=
/- dEAduction
pretty_name = Négation d'un "ET"
description = """
En général, le bouton "NON" tente de "pousser" la négation le long de la
propriété.
"""
available_logic = "and or not implies iff"
available_magic = "assumption"
-/
begin
    todo
end


lemma exercise.contradiction :
R ∨ ¬ R
:=
/- dEAduction
pretty_name = Le tiers exclu : l'une des deux propriétés "R" et "NON R" est vraie
description = "Le mécanisme de preuve inclus le tiers exclu, de façon un peu cachée..."
available_logic = "and or not implies iff"
available_proof = "proof_methods"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.negation_implication :
¬ (P → Q) ↔ (P ∧ ¬ Q)
:=
/- dEAduction
pretty_name = "Négation d'une implication"
description = "Blabla"
available_logic = "and or not implies iff"
available_proof = "proof_methods"
available_magic = "assumption"
 = """
"""
-/
begin
    todo
end


lemma exercise.contraposition :
(P → Q) ↔ (¬ Q → ¬ P)
:=
/- dEAduction
pretty_name = "Contraposition"
description = """
Le bouton "=>" permet également d'appliquer une implication "P => Q" à la
propriété "P" pour obtenir la propriété "Q". Attention, avant de
l'actionner il faut sélectionner toutes les propriétés requises !
On pourra raisonner par l'absurde en utilisant les "Méthodes de preuves".
"""
available_logic = "and or not implies iff"
available_proof = "proof_methods"
available_magic = "assumption"
 = """
"""
-/
begin
    todo
end

lemma exercise.ou_implication_I :
(P → Q) ↔ (¬ P ∨ Q)
:=
/- dEAduction
pretty_name = 'Implication sous forme de "OU"'
description = "Cette propriété permet de transformer une implication en une disjonction"
available_logic = "and or not implies iff"
available_proof = "proof_methods"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.ou_implication_II :
(P ∨ Q) ↔ (¬ P → Q)
:=
/- dEAduction
pretty_name = "OU" sous forme d'implication
description = """
Cette propriété est très proche de la précédente.
On peut la redémontrer entièrement, mais on peut aussi tenter d'appliquer
le résultat de l'exercice précédent. Pour cela, il faudra introduire
un nouvel objet, avant de lui appliquer le résultat précédent...
"""
available_logic = "and or not implies iff"
available_proof = "proof_methods new_object"
available_magic = "assumption"
-/
begin
    todo
end



end Logique_propositionnelle

end course
