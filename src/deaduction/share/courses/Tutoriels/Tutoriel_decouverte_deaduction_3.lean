/-
This is a d∃∀duction file providing a tutorial about using definitions and theorems.
-/

-- Lean standard imports
import tactic
import data.real.basic

-- dEAduction tactics
-- structures2 and utils are vital
import deaduction_all_tactics
-- import structures2      -- hypo_analysis, targets_analysis
-- import utils            -- no_meta_vars
-- import compute_all      -- Tactics for the compute buttons
-- import push_neg_once    -- Pushing negation just one step
-- import induction        -- Induction theorems

-- dEAduction definitions
-- import set_definitions
import real_definitions

-- Use classical logic
local attribute [instance] classical.prop_decidable


/- dEAduction
title = "Tutoriel partie 3 : découverte des Définitions et Théorèmes"
author = "Isabelle Dubois / inspiré du fichier tutoriel de Frédéric"
institution = "Université de Lorraine"
description = """
Tutoriel d'utilisation du logiciel dans un contexte de manipulations des entiers ou réels
- Partie 3 - Découverte des Définitions et Théorèmes
"""
default_available_logic = "ALL -map"
available_exercises = "NONE"
default_available_proof = "NONE"
default_available_magic = "Assumption"
available_compute = "NONE"
[settings]
functionality.calculator_available = true
-/

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
open nat

variables (P Q R: Prop) -- NOT global
notation [parsing_only] P ` \and ` Q := P ∧ Q
notation [parsing_only]  P ` \or ` Q := P ∨ Q
notation [parsing_only]  ` \not ` P := ¬ P
notation [parsing_only]  P ` \implies ` Q := P → Q
notation [parsing_only]  P ` \iff ` Q := P ↔ Q

variables {m n k: ℕ}


lemma theorem.croissance1 
{x y : ℝ} :
((0 <= x) \and (0<=y) \and (x <=y)) → x^2 <= y^2
:=
/- dEAduction
pretty_name = "Croissance de la fonction carré - Réels positifs"
-/
begin
  todo
end

lemma exercise.utilisation_th { x y : ℝ} (H : 0 <=x)  :
(x <= y) → ((0<=y) \and (x^2 <= y^2))
:=
/- dEAduction
pretty_name = "Utilisation d'un théorème dans le but - Fonction carrée."
description = "Utilisation d'un théorème dans le but - Fonction carrée."
available_logic = "and  implies"
available_magic = "assumption"
-/
begin
    todo
end


lemma theorem.decroissance 
{ x y : ℝ} :
((x <= 0) \and (y<=0) \and (x <=y)) → y^2 <= x^2
:=
/- dEAduction
pretty_name = "Décroissance de la fonction carré - Réels négatifs"
-/
begin
  todo
end

lemma exercise.utilisation_thd2 { x y : ℝ} (H : x <=0)  :
(x <= -2) → ((-2)^2 <= x^2)
:=
/- dEAduction
pretty_name = "Utilisation d'un théorème à choisir parmi deux dans le But - Fonction carrée."
description = "Utilisation d'un théorème à choisir parmi deux dans le But - Fonction carrée."
available_logic = "and implies"
available_magic = "assumption"
-/
begin
    todo
end

lemma theorem.eqproduit 
{ x y : ℝ} :
(x*y=0) ↔ ( (x=0) \or (y=0) )
:=
/- dEAduction
pretty_name = "Equation produit"
-/
begin
  todo
end





lemma exercise.eq2 { x y : ℝ}  :
((x-1) * x)*y = 0 → ( (x=1) \or (x=0) \or (y=0) )
:=
/- dEAduction
pretty_name = "Utilisation d'un théorème dans une hypothèse  - Equation"
description = "Utilisation d'un théorème dans une hypothèse - Equation."
available_logic = "or  implies"
available_theorems = "eqproduit"
available_magic = "assumption"
-/
begin
    todo
end



def F  (x  : ℝ) : ℝ := (x-1)*(x+2)

lemma definition.F   ( x : ℝ)  :
F (x) = (x-1)*(x+2)
:=
begin
    todo
end

lemma exercise.def  { x  : ℝ} (H: x=1) :
F (x) = 0
:=
/- dEAduction
pretty_name = "Utilisation d'une définition dans un but"
description = "Utilisation d'une définition dans un but"
available_logic = "equal  implies"
available_theorems = "eqproduit"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.defbilan  { x  : ℝ} :
( F (x) = 0 ) \iff ( (x=1) \or (x=-2) )
:=
/- dEAduction
pretty_name = "Utilisation d'une définition, d'un théorème"
description = "Utilisation d'une définition, d'un théorème"
available_logic = "or and equal  implies iff"
available_theorems = "eqproduit"
available_magic = "assumption"
-/
begin
    todo
end



end course
