/-
This is a d∃∀duction file providing a tutorial about using quantifiers.
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
title = "Tutoriel partie 2 : découverte des icônes Quantificateurs"
author = "Isabelle Dubois / inspiré du fichier tutoriel de Frédéric"
institution = "Université de Lorraine"
description = """
Tutoriel d'utilisation du logiciel dans un contexte de manipulations des entiers ou réels
- Partie 2 - Découverte des icônes Quantificateurs
"""
available_exercises = "NONE"
default_available_proof = "NONE"
default_available_magic = "Assumption"
available_compute = "NONE"
[settings]
logic.usr_jokers_available = false
logic.use_color_for_applied_properties = false
functionality.allow_induction = false
functionality.calculator_available = true
others.Lean_request_method = "normal"
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



lemma exercise.pourtout_hyp1 { x  : ℝ} (H: ∀ y : ℝ, y^2 = y*y ) : 
 ( (x+1)^2= 1 + 2*x +x*x)  
:=
/- dEAduction
pretty_name = "Utilisation du Pour tout dans une hypothèse (1)"
description = "Utilisation  du Pour tout dans une hypothèse (1)."
available_logic = "equal forall"
available_theorems = "NONE"
available_definitions = "NONE"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.pourtout_hyp2 { x  : ℝ} (H: ∀ y : ℝ, y^2 = y*y ) : 
 ( (x+1)^2= 1 + 2*x +x^2)  
:=
/- dEAduction
pretty_name = "Utilisation du Pour tout dans une hypothèse (2)"
description = "Utilisation  du Pour tout dans une hypothèse (2). Variante."
available_logic = "equal forall"
available_theorems = "NONE"
available_definitions = "NONE"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.pourtout_but  : 
 ( ∀ x : ℝ, ∀ y : ℝ, ∀ z : ℝ, x*(y+z) = x*y +x*z )  
:=
/- dEAduction
pretty_name = "Démontrer un Pour tout dans le but"
description = "Démontrer un Pour tout dans le but."
available_logic = "forall"
available_theorems = "NONE"
available_definitions = "NONE"
available_magic = "assumption"
-/
begin
    todo
end

lemma exercise.pourtout_hypbut (H1: ∀ x : ℝ, x^2 = x*x ) (H2: ∀ y : ℝ, y^3 = y*y*y ) : 
 ( ∀ z : ℝ, (z+1)^3= 1 + 3*z + 3*z^2 + z^3 )  
:=
/- dEAduction
pretty_name = "Pour Tout dans but et hypothèse"
description = "Démontrer/Utiliser un Pour Tout dans le but et une hypothèse."
available_logic = "equal forall"
available_theorems = "NONE"
available_definitions = "NONE"
available_magic = "assumption"
-/
begin
    todo
end


lemma exercise.ilexiste_but1 : 
 (  ∃ a  :  ℕ, a*a*a = 27  )
:=
/- dEAduction
pretty_name = "Démontrer un Il existe dans le but (1)"
description = "Démontrer un Il existe dans  le but (1)."
available_logic = "exists"
available_theorems = "NONE"
available_definitions = "NONE"
available_magic = "assumption"
-/
begin
   todo
end

lemma exercise.ilexiste_but2 : 
 (  ∃ a  :  ℕ, ∃ b  :  ℕ, (a*b=143) \and (a > b) )
:=
/- dEAduction
pretty_name = "Démontrer un Il existe dans le but (2)"
description = "Démontrer un Il existe dans le but (2)."
available_logic = "exists and"
available_theorems = "NONE"
available_definitions = "NONE"
available_magic = "assumption"
-/
begin
    todo
end


lemma exercise.ilexiste_hypbut { n  :  ℕ}  : 
 (  ∃ a  :  ℕ, n = 2*a ) → (  ∃ b  :  ℕ, n*n = 2*b )
:=
/- dEAduction
pretty_name = "Utilisation du bouton Il existe dans une hypothèse et but"
description = "Démontrer/Utiliser un Il existe dans une hypothèse et le but."
available_logic = "equal exists implies"
available_theorems = "NONE"
available_definitions = "NONE"
available_magic = "assumption"
-/
begin
    todo
end




end course
