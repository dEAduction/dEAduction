/-
Feuille d'exercice pour travailler les premières définitions d'ensembles dans le cadre des entiers
-/

import data.set
import tactic

-- dEAduction tactics
import structures2      -- hypo_analysis, targets_analysis
import utils            -- no_meta_vars
import user_notations   -- notations that can be used in deaduction UI for a new object
import push_neg_once
import compute

-- dEAduction definitions
import set_definitions



-------------------------
-- dEAduction METADATA --
-------------------------
-- logic names ['and', 'or', 'negate', 'implicate', 'iff', 'forall', 'exists']
-- proofs names ['use_proof_methods', 'new_object', 'apply', 'assumption']
-- magic names ['compute']
-- proof methods names ['cbr', 'contrapose', 'absurdum', 'sorry']

/- dEAduction
title = "Premières définitions - Théorie des ensembles"
author = "Isabelle Dubois"
institution = "Université de Lorraine"
description = Cette feuille d'exercices permet d'aborder les premières définitions de la théorie "élémentaire" des ensembles, dans un contexte concret.
logic.usr_jokers_available = false
logic.use_color_for_applied_properties = false
functionality.allow_induction = false
functionality.calculator_available = true
others.Lean_request_method = "normal"
-/

local attribute [instance] classical.prop_decidable

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
variables {X Y Z: Type}
variables {n p l m : ℕ}

open set
open nat  -- car on travaille dans l'ensemble ℕ


------------------------
-- COURSE DEFINITIONS --
------------------------
lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
/- dEAduction
pretty_name = "Inclusion d'un ensemble dans un autre"
implicit_use = true
-/
begin
    todo
end

lemma definition.egalite_deux_ensembles {A A' : set X} :
(A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
pretty_name = "Egalité de deux ensembles"
implicit_use = true
-/
begin
     todo
end

lemma definition.ensemble_vide
(A: set X) :
(A = ∅) ↔ ∀ x : X, x ∉ A
:=
/- dEAduction
pretty_name = "Ensemble vide"
implicit_use = true
-/
begin
    todo
end

lemma definition.ensemble_non_vide
(A: set X) :
(A ≠ ∅) ↔ ∃ x : X, x ∈ A
:=
/- dEAduction
pretty_name = "Ensemble non vide"
implicit_use = true
-/
begin
   todo
end

lemma definition.singleton {X : Type} {x y : X}: x ∈ ({y} : set X) ↔ x = y
:=
/- dEAduction
pretty_name = "Ensemble singleton"
-/
begin
    todo
end

lemma definition.ensemble_extension {X: Type}  {P : X → Prop} {x:X} :
 x ∈ {x | P x} ↔ P x
:=
/- dEAduction
pretty_name = "Ensemble défini en extension"
-/
begin
    todo
end



lemma exercise.singleton  :
 n ∈ ( { n } : set ℕ )
:=
/- dEAduction
pretty_name = "Appartenance à un ensemble singleton"
-/
begin
    todo
end

lemma exercise.singleton_nonvide (A : set ℕ) (n : ℕ) :
 A = { n } → A ≠ ∅
:=
/- dEAduction
pretty_name = "Un ensemble singleton est non vide"
-/
begin
    todo
end

lemma exercise.multiples_nonvide (Ea : set ℕ ) (a : ℕ) (H: Ea = {n | ∃ p  :  ℕ, n=a*p}) :
( Ea ≠  ∅ ) 
:=
/- dEAduction
pretty_name = "Ensemble des multiples de a est non vide"
-/
begin
    todo
end

lemma exercise.multiples_zero (E0 : set ℕ )  (H: E0 = {n | ∃ p  :  ℕ, n=0*p}) :
 E0 = ({ 0 }  : set ℕ )
:=
/- dEAduction
pretty_name = "Ensemble des multiples de zéro"
-/
begin
    todo
end



lemma exercise.multiples_a (Ea : set ℕ ) (a  : ℕ) (H: Ea = {n | ∃ p  :  ℕ, n=a*p}) :
a ∈ Ea
:=
/- dEAduction
pretty_name = "Ensemble des multiples de a contient a"
-/
begin
    todo
end

lemma exercise.zeroinclus (Ea : set ℕ )  (a: ℕ ) (H: Ea = {n | ∃ p  :  ℕ, n=a*p}) :
 ({ 0 }  : set ℕ ) ⊆  Ea
:=
/- dEAduction
pretty_name = "Ensemble des multiples de a contient {0}"
-/
begin
    todo
end

lemma exercise.inclusion_ensembles_multiples1  (Ea Ema : set ℕ ) (a m : ℕ) (H1: Ea = {n | ∃ p  :  ℕ, n=a*p}) (H2: Ema = {n | ∃ p  :  ℕ, n=(m*a)*p}):
 Ema ⊆ Ea 
:=
/- dEAduction
pretty_name = "Ensemble des multiples - Une inclusion"
-/
begin
    todo
end

lemma exercise.inclusion_ensembles_multiples2  (Ea Eb : set ℕ ) (a b : ℕ) (H1: Ea = {n | ∃ p  :  ℕ, n=a*p}) (H2: Eb = {n | ∃ p  :  ℕ, n=b*p}):
 Ea ⊆ Eb ↔ a ∈ Eb
:=
/- dEAduction
pretty_name = "Ensemble des multiples - Caractérisation Inclusion"
-/
begin
    todo
end


lemma exercise.inclusion_ensembles_multiples3 (Ea Eb : set ℕ ) (a b : ℕ) (H1: Ea = {n | ∃ p  :  ℕ, n=a*p}) (H2: Eb = {n | ∃ p  :  ℕ, n=b*p})
(H3: ∀ n : ℕ, ∀ p : ℕ, ∀ l : ℕ, ((n=n*p*l) → ((n = 0) ∨ ((p=1)∧ (l=1)) ) )):
 Ea = Eb ↔ a =b
:=
/- dEAduction
pretty_name = "Ensemble des multiples - Egalité"
-/
begin
    todo
end



end course